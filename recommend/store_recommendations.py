#!/usr/bin/env python3
"""
Generate and store recommendations for all users in the database.
This script should be run after persona assignment in the data pipeline.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from recommend.engine import generate_recommendations

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "users.sqlite"


def store_recommendations_for_all_users():
    """Generate and store recommendations for all users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all users with consent
    cursor.execute("SELECT user_id FROM users WHERE consent_granted = 1 ORDER BY user_id")
    users = cursor.fetchall()

    if not users:
        print("⚠️  No users with consent found")
        conn.close()
        return

    print(f"Generating recommendations for {len(users)} users...")

    stored_count = 0
    skipped_count = 0

    for (user_id,) in users:
        try:
            # Generate recommendations
            result = generate_recommendations(user_id)

            # Get persona from result
            persona = result.get("persona", "general")

            # Convert entire result to JSON for storage
            recommendations_json = json.dumps(result)
            generated_at = datetime.now().isoformat()

            # Store in database
            cursor.execute(
                """
                INSERT OR REPLACE INTO recommendations
                (user_id, persona, recommendations_json, generated_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, persona, recommendations_json, generated_at)
            )

            stored_count += 1

            # Print progress every 10 users
            if stored_count % 10 == 0:
                print(f"  Stored recommendations for {stored_count}/{len(users)} users...")

        except Exception as e:
            print(f"  ⚠️  Failed to generate recommendations for {user_id}: {e}")
            skipped_count += 1

    conn.commit()
    conn.close()

    print(f"\n✅ Stored recommendations for {stored_count} users")
    if skipped_count > 0:
        print(f"⚠️  Skipped {skipped_count} users due to errors")


if __name__ == "__main__":
    print("📊 Generating and storing recommendations...")
    print(f"   Database: {DB_PATH}\n")

    store_recommendations_for_all_users()

    print("\n✨ Done!")

#!/usr/bin/env python3
"""
Migration script to add operator recommendation tables.
Run once to update existing database.
"""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "users.sqlite"


def migrate():
    """Apply migration to add operator recommendation tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Creating operator_recommendations table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operator_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            recommendation_id TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            topic TEXT,
            rationale TEXT NOT NULL,
            disclaimer TEXT,
            content_json TEXT,
            source TEXT NOT NULL DEFAULT 'operator_created',
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            overridden_at TEXT,
            overridden_by TEXT,
            overrides_original_id TEXT,
            metadata_json TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            UNIQUE (user_id, recommendation_id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_operator_recs_user_status
        ON operator_recommendations(user_id, status)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_operator_recs_created_by
        ON operator_recommendations(created_by)
    """)

    print("Creating recommendation_audit_log table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendation_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            recommendation_id TEXT NOT NULL,
            action TEXT NOT NULL,
            operator_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            previous_value_json TEXT,
            new_value_json TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_user_timestamp
        ON recommendation_audit_log(user_id, timestamp DESC)
    """)

    print("Adding columns to recommendations table...")

    # Check existing columns
    cursor.execute("PRAGMA table_info(recommendations)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "has_operator_overrides" not in existing_columns:
        cursor.execute("""
            ALTER TABLE recommendations
            ADD COLUMN has_operator_overrides BOOLEAN DEFAULT 0
        """)
        print("  Added has_operator_overrides column")
    else:
        print("  Column has_operator_overrides already exists")

    if "last_modified_at" not in existing_columns:
        cursor.execute("""
            ALTER TABLE recommendations
            ADD COLUMN last_modified_at TEXT
        """)
        print("  Added last_modified_at column")
    else:
        print("  Column last_modified_at already exists")

    if "last_modified_by" not in existing_columns:
        cursor.execute("""
            ALTER TABLE recommendations
            ADD COLUMN last_modified_by TEXT
        """)
        print("  Added last_modified_by column")
    else:
        print("  Column last_modified_by already exists")

    conn.commit()
    conn.close()

    print("✅ Migration complete!")


if __name__ == "__main__":
    migrate()

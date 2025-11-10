"""
Service layer for operator-managed recommendations.
Handles CRUD operations, override logic, and merging with auto-generated recs.
"""

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).parent.parent.parent / "data" / "users.sqlite"


def get_merged_recommendations(user_id: str) -> List[Dict[str, Any]]:
    """
    Merge auto-generated and operator recommendations for a user.

    Logic:
    1. Get all auto-generated recs from recommendations table
    2. Get active operator recs
    3. Remove auto recs that have been overridden
    4. Merge and return
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get auto-generated recs
    cursor.execute(
        "SELECT recommendations_json FROM recommendations WHERE user_id = ?",
        (user_id,)
    )
    auto_row = cursor.fetchone()
    auto_recs = []
    overridden_ids = set()

    if auto_row:
        auto_payload = json.loads(auto_row['recommendations_json'])
        auto_recs = auto_payload.get('recommendations', [])

    # Get active operator recs
    cursor.execute(
        """
        SELECT * FROM operator_recommendations
        WHERE user_id = ? AND status = 'active'
        ORDER BY created_at DESC
        """,
        (user_id,)
    )
    operator_rows = cursor.fetchall()

    operator_recs = []
    for row in operator_rows:
        rec = {
            'recommendation_id': row['recommendation_id'],
            'type': row['type'],
            'title': row['title'],
            'description': row['description'],
            'category': row['category'],
            'topic': row['topic'],
            'rationale': row['rationale'],
            'disclaimer': row['disclaimer'] or "This is educational content, not financial advice.",
            'content': json.loads(row['content_json']) if row['content_json'] else None,
            'source': row['source'],
            'created_by': row['created_by'],
        }
        operator_recs.append(rec)

        # If this overrides an auto-rec, mark it for exclusion
        if row['overrides_original_id']:
            overridden_ids.add(row['overrides_original_id'])

    conn.close()

    # Filter out overridden auto recs
    filtered_auto_recs = []
    for rec in auto_recs:
        rec_id = rec.get('recommendation_id', '')
        if rec_id not in overridden_ids:
            rec['source'] = 'auto_generated'  # Mark source
            filtered_auto_recs.append(rec)

    # Merge: operator recs first (higher priority), then auto recs
    merged = operator_recs + filtered_auto_recs

    return merged


def get_operator_recs(user_id: str) -> Dict[str, Any]:
    """Get all operator-managed recommendations for a user (including overridden for audit)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM operator_recommendations
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    recs = []
    for row in rows:
        rec = {
            'id': row['id'],
            'recommendation_id': row['recommendation_id'],
            'user_id': row['user_id'],
            'type': row['type'],
            'title': row['title'],
            'description': row['description'],
            'category': row['category'],
            'topic': row['topic'],
            'rationale': row['rationale'],
            'disclaimer': row['disclaimer'],
            'content': json.loads(row['content_json']) if row['content_json'] else None,
            'source': row['source'],
            'created_by': row['created_by'],
            'created_at': row['created_at'],
            'status': row['status'],
            'overridden_at': row['overridden_at'],
            'overridden_by': row['overridden_by'],
            'overrides_original_id': row['overrides_original_id'],
        }
        recs.append(rec)

    return {'user_id': user_id, 'recommendations': recs}


def create_operator_rec(
    user_id: str,
    rec_type: str,
    title: str,
    description: str,
    category: str,
    topic: str,
    rationale: str,
    operator_name: str,
    disclaimer: Optional[str] = None,
    content: Optional[dict] = None,
) -> Dict[str, Any]:
    """Create new operator recommendation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Generate unique recommendation_id
    timestamp = datetime.now().timestamp()
    rec_id = f"op-{user_id}-{int(timestamp)}"

    # Insert into operator_recommendations
    cursor.execute(
        """
        INSERT INTO operator_recommendations
        (user_id, recommendation_id, type, title, description, category, topic,
         rationale, disclaimer, content_json, source, created_by, created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            rec_id,
            rec_type,
            title,
            description,
            category,
            topic,
            rationale,
            disclaimer or "This is educational content, not financial advice.",
            json.dumps(content) if content else None,
            'operator_created',
            operator_name,
            datetime.now().isoformat(),
            'active'
        )
    )

    # Log audit trail
    _log_audit(
        cursor,
        user_id=user_id,
        recommendation_id=rec_id,
        action='created',
        operator_name=operator_name,
        new_value_json=json.dumps({
            'title': title,
            'description': description,
            'type': rec_type,
            'category': category,
            'topic': topic,
        })
    )

    # Mark user as having operator overrides
    cursor.execute(
        """
        UPDATE recommendations
        SET has_operator_overrides = 1, last_modified_at = ?, last_modified_by = ?
        WHERE user_id = ?
        """,
        (datetime.now().isoformat(), operator_name, user_id)
    )

    conn.commit()
    conn.close()

    return {"success": True, "recommendation_id": rec_id}


def update_operator_rec(
    recommendation_id: str,
    title: str,
    description: str,
    category: str,
    topic: str,
    rationale: str,
    operator_name: str,
    disclaimer: Optional[str] = None,
    content: Optional[dict] = None,
) -> Dict[str, Any]:
    """Update existing operator recommendation."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get current rec for audit
    cursor.execute(
        "SELECT * FROM operator_recommendations WHERE recommendation_id = ?",
        (recommendation_id,)
    )
    current = cursor.fetchone()

    if not current:
        conn.close()
        raise ValueError(f"Recommendation {recommendation_id} not found")

    previous_value = dict(current)

    # Update rec
    cursor.execute(
        """
        UPDATE operator_recommendations
        SET title = ?, description = ?, category = ?, topic = ?,
            rationale = ?, disclaimer = ?, content_json = ?
        WHERE recommendation_id = ?
        """,
        (
            title,
            description,
            category,
            topic,
            rationale,
            disclaimer or current['disclaimer'],
            json.dumps(content) if content else current['content_json'],
            recommendation_id
        )
    )

    # Log audit
    _log_audit(
        cursor,
        user_id=current['user_id'],
        recommendation_id=recommendation_id,
        action='edited',
        operator_name=operator_name,
        previous_value_json=json.dumps({k: previous_value[k] for k in ['title', 'description', 'category', 'topic']}),
        new_value_json=json.dumps({'title': title, 'description': description, 'category': category, 'topic': topic})
    )

    conn.commit()
    conn.close()

    return {"success": True}


def delete_operator_rec(recommendation_id: str, operator_name: str) -> Dict[str, Any]:
    """Soft-delete operator recommendation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Mark as deleted
    cursor.execute(
        """
        UPDATE operator_recommendations
        SET status = 'deleted'
        WHERE recommendation_id = ?
        """,
        (recommendation_id,)
    )

    # Log audit
    cursor.execute(
        "SELECT user_id FROM operator_recommendations WHERE recommendation_id = ?",
        (recommendation_id,)
    )
    row = cursor.fetchone()
    if row:
        user_id = row[0]
        _log_audit(
            cursor,
            user_id=user_id,
            recommendation_id=recommendation_id,
            action='deleted',
            operator_name=operator_name
        )

    conn.commit()
    conn.close()

    return {"success": True}


def override_auto_rec(
    user_id: str,
    original_rec_id: str,
    rec_type: str,
    title: str,
    description: str,
    category: str,
    topic: str,
    rationale: str,
    operator_name: str,
    disclaimer: Optional[str] = None,
    content: Optional[dict] = None,
) -> Dict[str, Any]:
    """
    Override an auto-generated recommendation.
    Marks original as 'overridden', creates new operator rec.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create new operator rec with override flag
    timestamp = datetime.now().timestamp()
    new_rec_id = f"op-override-{user_id}-{int(timestamp)}"

    cursor.execute(
        """
        INSERT INTO operator_recommendations
        (user_id, recommendation_id, type, title, description, category, topic,
         rationale, disclaimer, content_json, source, created_by, created_at,
         status, overrides_original_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            new_rec_id,
            rec_type,
            title,
            description,
            category,
            topic,
            rationale,
            disclaimer or "This is educational content, not financial advice.",
            json.dumps(content) if content else None,
            'operator_override',
            operator_name,
            datetime.now().isoformat(),
            'active',
            original_rec_id  # Original rec ID being overridden
        )
    )

    # Log audit
    _log_audit(
        cursor,
        user_id=user_id,
        recommendation_id=new_rec_id,
        action='overridden',
        operator_name=operator_name,
        notes=f"Overrides auto-rec {original_rec_id}",
        new_value_json=json.dumps({'title': title, 'description': description})
    )

    conn.commit()
    conn.close()

    return {"success": True, "new_recommendation_id": new_rec_id}


def bulk_get_recs(user_ids: List[str]) -> Dict[str, Any]:
    """Get recommendations for multiple users."""
    results = {}
    for user_id in user_ids:
        results[user_id] = get_operator_recs(user_id)
    return results


def bulk_edit_recs(recommendation_ids: List[str], updates: dict, operator_name: str) -> Dict[str, Any]:
    """Bulk edit multiple recommendations."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updated_count = 0
    for rec_id in recommendation_ids:
        # Build UPDATE query dynamically based on updates dict
        set_clauses = []
        values = []
        for key, value in updates.items():
            if key in ['title', 'description', 'category', 'topic', 'rationale', 'disclaimer']:
                set_clauses.append(f"{key} = ?")
                values.append(value)

        if set_clauses:
            query = f"""
                UPDATE operator_recommendations
                SET {', '.join(set_clauses)}
                WHERE recommendation_id = ?
            """
            values.append(rec_id)
            cursor.execute(query, values)

            # Log audit
            cursor.execute(
                "SELECT user_id FROM operator_recommendations WHERE recommendation_id = ?",
                (rec_id,)
            )
            row = cursor.fetchone()
            if row:
                _log_audit(
                    cursor,
                    user_id=row[0],
                    recommendation_id=rec_id,
                    action='bulk_edited',
                    operator_name=operator_name,
                    new_value_json=json.dumps(updates)
                )
                updated_count += 1

    conn.commit()
    conn.close()

    return {"success": True, "updated_count": updated_count}


def _log_audit(
    cursor,
    user_id: str,
    recommendation_id: str,
    action: str,
    operator_name: str,
    previous_value_json: Optional[str] = None,
    new_value_json: Optional[str] = None,
    notes: Optional[str] = None
):
    """Helper to log audit trail."""
    cursor.execute(
        """
        INSERT INTO recommendation_audit_log
        (user_id, recommendation_id, action, operator_name, timestamp,
         previous_value_json, new_value_json, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            recommendation_id,
            action,
            operator_name,
            datetime.now().isoformat(),
            previous_value_json,
            new_value_json,
            notes
        )
    )


def _slugify(text: str) -> str:
    """Basic slug for stable recommendation ids."""
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:64] if text else "item"

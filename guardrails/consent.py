"""
Consent Management for SpendSense MVP V2

This module provides functions for managing user consent for data processing.
All processing is blocked unless explicit consent is granted.

Core Functions:
- grant_consent(user_id): Opt user into data processing
- revoke_consent(user_id): Opt user out and archive data
- check_consent(user_id): Check current consent status
- get_consent_history(user_id): Get consent audit trail

Design Principles:
- Explicit opt-in required before any processing
- Users can revoke consent at any time
- All consent changes tracked with timestamps
- Consent status stored in SQLite users table

Compliance:
- Implements PRD Part 1, Section 4.3: Consent Tracking
- Implements PRD Part 2, Section 8: Guardrails
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


# Database path - use absolute path to project root
DB_PATH = Path(__file__).parent.parent / "data" / "users.sqlite"


def grant_consent(user_id: str) -> Dict[str, Any]:
    """
    Grant consent for a user to process their financial data.

    Args:
        user_id: User identifier

    Returns:
        Dictionary with:
        - success: boolean
        - user_id: user identifier
        - consent_granted: True
        - consent_timestamp: ISO 8601 timestamp
        - message: status message

    Raises:
        ValueError: If user_id not found in database
        sqlite3.Error: If database operation fails
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    timestamp = datetime.now().isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            raise ValueError(f"User {user_id} not found in database")

        # Update consent status
        cursor.execute(
            """
            UPDATE users
            SET consent_granted = 1,
                consent_timestamp = ?,
                revoked_timestamp = NULL
            WHERE user_id = ?
            """,
            (timestamp, user_id),
        )
        conn.commit()

    return {
        "success": True,
        "user_id": user_id,
        "consent_granted": True,
        "consent_timestamp": timestamp,
        "message": f"Consent granted for user {user_id}",
    }


def revoke_consent(user_id: str) -> Dict[str, Any]:
    """
    Revoke consent for a user, blocking all future processing.

    Args:
        user_id: User identifier

    Returns:
        Dictionary with:
        - success: boolean
        - user_id: user identifier
        - consent_granted: False
        - revoked_timestamp: ISO 8601 timestamp
        - message: status message

    Raises:
        ValueError: If user_id not found in database
        sqlite3.Error: If database operation fails

    Note:
        This function sets consent_granted to 0 and records revoked_timestamp.
        It does NOT delete user data (for audit purposes).
        Data archival/deletion should be handled separately per data retention policy.
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    timestamp = datetime.now().isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            raise ValueError(f"User {user_id} not found in database")

        # Update consent status
        cursor.execute(
            """
            UPDATE users
            SET consent_granted = 0,
                revoked_timestamp = ?
            WHERE user_id = ?
            """,
            (timestamp, user_id),
        )
        conn.commit()

    return {
        "success": True,
        "user_id": user_id,
        "consent_granted": False,
        "revoked_timestamp": timestamp,
        "message": f"Consent revoked for user {user_id}",
    }


def check_consent(user_id: str) -> bool:
    """
    Check if a user has granted consent for data processing.

    Args:
        user_id: User identifier

    Returns:
        True if consent granted, False otherwise

    Raises:
        ValueError: If user_id not found in database
        sqlite3.Error: If database operation fails
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT consent_granted FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if row is None:
            raise ValueError(f"User {user_id} not found in database")

        # SQLite stores booleans as integers (0 or 1)
        return bool(row[0])


def get_consent_history(user_id: str) -> Dict[str, Any]:
    """
    Get consent audit trail for a user.

    Args:
        user_id: User identifier

    Returns:
        Dictionary with:
        - user_id: user identifier
        - consent_granted: current status (boolean)
        - consent_timestamp: when consent was last granted (or None)
        - revoked_timestamp: when consent was last revoked (or None)
        - current_status: "granted", "revoked", or "never_granted"

    Raises:
        ValueError: If user_id not found in database
        sqlite3.Error: If database operation fails
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT consent_granted, consent_timestamp, revoked_timestamp
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = cursor.fetchone()

        if row is None:
            raise ValueError(f"User {user_id} not found in database")

        consent_granted, consent_timestamp, revoked_timestamp = row

        # Determine current status
        if bool(consent_granted):
            current_status = "granted"
        elif revoked_timestamp:
            current_status = "revoked"
        else:
            current_status = "never_granted"

        return {
            "user_id": user_id,
            "consent_granted": bool(consent_granted),
            "consent_timestamp": consent_timestamp,
            "revoked_timestamp": revoked_timestamp,
            "current_status": current_status,
        }


def batch_grant_consent(user_ids: list) -> Dict[str, Any]:
    """
    Grant consent for multiple users at once (useful for testing/setup).

    Args:
        user_ids: List of user identifiers

    Returns:
        Dictionary with:
        - success_count: number of successful grants
        - failed_count: number of failures
        - failures: list of (user_id, error_message) tuples
    """
    timestamp = datetime.now().isoformat()
    success_count = 0
    failed_count = 0
    failures = []

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for user_id in user_ids:
            try:
                # Check if user exists
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                if not cursor.fetchone():
                    failures.append((user_id, "User not found"))
                    failed_count += 1
                    continue

                # Update consent
                cursor.execute(
                    """
                    UPDATE users
                    SET consent_granted = 1,
                        consent_timestamp = ?,
                        revoked_timestamp = NULL
                    WHERE user_id = ?
                    """,
                    (timestamp, user_id),
                )
                success_count += 1

            except Exception as e:
                failures.append((user_id, str(e)))
                failed_count += 1

        conn.commit()

    return {
        "success_count": success_count,
        "failed_count": failed_count,
        "failures": failures,
        "timestamp": timestamp,
    }

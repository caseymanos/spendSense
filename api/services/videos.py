"""
Video service for fetching educational YouTube videos by topic.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "spendsense.db"


def get_videos_by_topic(topic: str) -> List[Dict[str, Any]]:
    """
    Fetch educational videos for a given topic from the database.

    Args:
        topic: Topic identifier (e.g., 'credit_utilization', 'debt_paydown_strategy')

    Returns:
        List of video dictionaries containing:
        - video_id
        - youtube_id
        - title
        - channel_name
        - duration_seconds
        - thumbnail_url
        - description
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            video_id,
            topic,
            youtube_id,
            title,
            channel_name,
            duration_seconds,
            thumbnail_url,
            description
        FROM educational_videos
        WHERE topic = ?
        ORDER BY added_at DESC
        """,
        (topic,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_all_videos() -> List[Dict[str, Any]]:
    """
    Fetch all educational videos from the database.

    Returns:
        List of all video dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            video_id,
            topic,
            youtube_id,
            title,
            channel_name,
            duration_seconds,
            thumbnail_url,
            description
        FROM educational_videos
        ORDER BY topic, added_at DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_topics_with_videos() -> List[str]:
    """
    Get list of all topics that have videos.

    Returns:
        List of topic identifiers
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT DISTINCT topic
        FROM educational_videos
        ORDER BY topic
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to MM:SS or HH:MM:SS.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"

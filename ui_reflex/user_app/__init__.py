"""Package export for Reflex app.

Expose the themed user app as the package-level `app` so
`reflex run` (using `app_name='user_app'`) picks up the updated UI.

This avoids touching `user_app.py` when it's reserved by another agent.
"""

from .user_app_themed import app  # noqa: F401

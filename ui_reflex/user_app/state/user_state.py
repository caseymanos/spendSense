"""
User application state management.

Manages the state for the user-facing dashboard including:
- Selected user
- Current page/view
- Loaded data (user info, persona, signals, recommendations)
- UI state (loading indicators, error messages)
"""

import reflex as rx
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loaders import (
    load_all_users,
    load_user_data,
    load_persona_assignment,
    load_behavioral_signals,
    get_recommendations,
    grant_user_consent,
    revoke_user_consent,
    get_persona_description,
    get_database_stats,
)


class UserAppState(rx.State):
    """State management for the SpendSense user application."""

    # ==========================================================================
    # NAVIGATION STATE
    # ==========================================================================

    current_page: str = "dashboard"
    """Current page: 'dashboard', 'learning_feed', or 'privacy'"""

    # ==========================================================================
    # USER SELECTION
    # ==========================================================================

    selected_user_id: str = ""
    """Currently selected user ID"""

    all_users: List[Dict[str, Any]] = []
    """List of all available users"""

    # ==========================================================================
    # USER DATA
    # ==========================================================================

    user_data: Dict[str, Any] = {}
    """Current user's demographic and consent data"""

    persona_data: Optional[Dict[str, Any]] = None
    """Current user's persona assignment"""

    signals: Dict[str, Any] = {}
    """Current user's behavioral signals"""

    recommendations_data: Dict[str, Any] = {}
    """Current user's recommendations"""

    # ==========================================================================
    # UI STATE
    # ==========================================================================

    is_loading: bool = False
    """Whether data is currently being loaded"""

    error_message: str = ""
    """Current error message to display"""

    show_consent_modal: bool = False
    """Whether to show the consent confirmation modal"""

    show_revoke_modal: bool = False
    """Whether to show the revoke consent confirmation modal"""

    # ==========================================================================
    # COMPUTED PROPERTIES
    # ==========================================================================

    @rx.var
    def user_ids(self) -> List[str]:
        """Get list of user IDs for the selector."""
        return [user["user_id"] for user in self.all_users]

    @rx.var
    def consent_granted_at(self) -> str:
        """Get formatted timestamp of when consent was granted."""
        if not self.consent_granted:
            return "Never granted"

        # Prefer DB column name; fall back to any legacy key if present
        consent_at = self.user_data.get("consent_timestamp") or self.user_data.get("consent_granted_at")
        if not consent_at:
            return "Unknown date"

        try:
            from datetime import datetime
            dt = datetime.fromisoformat(consent_at.replace('Z', '+00:00'))
            return dt.strftime("%b %d, %Y at %I:%M %p")
        except:
            return str(consent_at)

    @rx.var
    def consent_status_text(self) -> str:
        """Get descriptive text for consent status."""
        if not self.consent_granted:
            return "Consent has never been granted for this user"

        # Prefer DB column name; fall back to any legacy key if present
        consent_at = self.user_data.get("consent_timestamp") or self.user_data.get("consent_granted_at")
        if not consent_at:
            return "Consent granted (date unknown)"

        try:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(consent_at.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            delta = now - dt

            if delta.days == 0:
                return "Granted today"
            elif delta.days == 1:
                return "Granted yesterday"
            elif delta.days < 7:
                return f"Granted {delta.days} days ago"
            else:
                return f"Granted on {dt.strftime('%b %d, %Y')}"
        except:
            return "Consent granted"

    @rx.var
    def users_with_consent_status(self) -> List[Dict[str, Any]]:
        """Get list of users with consent status indicators for dropdown."""
        return [
            {
                "user_id": user["user_id"],
                "display": f"{'✓' if user.get('consent_granted') else '✗'} {user['user_id']}",
                "has_consent": bool(user.get("consent_granted"))
            }
            for user in self.all_users
        ]

    # ==========================================================================
    # INITIALIZATION
    # ==========================================================================

    @rx.event
    def on_load(self):
        """Initialize the application state on first load."""
        # Load all users for the selector
        self.all_users = load_all_users()

        # Select first user if available
        if self.all_users and not self.selected_user_id:
            self.selected_user_id = self.all_users[0]["user_id"]
            self.load_user_data_event()

    # ==========================================================================
    # USER SELECTION EVENTS
    # ==========================================================================

    @rx.event
    def select_user(self, user_id: str):
        """Select a different user and load their data.

        Args:
            user_id: The user ID to select
        """
        self.selected_user_id = user_id
        self.load_user_data_event()

    @rx.event
    def load_user_data_event(self):
        """Load all data for the currently selected user."""
        if not self.selected_user_id:
            return

        self.is_loading = True
        self.error_message = ""

        try:
            # Load user demographics and consent
            self.user_data = load_user_data(self.selected_user_id)

            # Load persona assignment
            self.persona_data = load_persona_assignment(self.selected_user_id)

            # Load behavioral signals
            self.signals = load_behavioral_signals(self.selected_user_id)

            # Load recommendations (only if consent granted)
            if self.user_data.get("consent_granted", False):
                self.recommendations_data = get_recommendations(self.selected_user_id)
            else:
                self.recommendations_data = {
                    "recommendations": [],
                    "metadata": {"reason": "consent_not_granted"}
                }

        except Exception as e:
            self.error_message = f"Error loading user data: {str(e)}"
            print(f"Error in load_user_data_event: {e}")

        finally:
            self.is_loading = False

    # ==========================================================================
    # NAVIGATION EVENTS
    # ==========================================================================

    @rx.event
    def navigate_to_dashboard(self):
        """Navigate to the dashboard page."""
        self.current_page = "dashboard"

    @rx.event
    def navigate_to_learning_feed(self):
        """Navigate to the learning feed page."""
        self.current_page = "learning_feed"

    @rx.event
    def navigate_to_privacy(self):
        """Navigate to the privacy settings page."""
        self.current_page = "privacy"

    # ==========================================================================
    # CONSENT MANAGEMENT EVENTS
    # ==========================================================================

    @rx.event
    def show_consent_confirmation(self):
        """Show the consent grant confirmation modal."""
        self.show_consent_modal = True

    @rx.event
    def hide_consent_confirmation(self):
        """Hide the consent grant confirmation modal."""
        self.show_consent_modal = False

    @rx.event
    def grant_consent_confirmed(self):
        """Grant consent for the current user after confirmation."""
        if not self.selected_user_id:
            return

        self.is_loading = True
        self.error_message = ""

        try:
            success = grant_user_consent(self.selected_user_id)

            if success:
                # Reload user data to reflect consent change
                self.load_user_data_event()
                self.show_consent_modal = False
            else:
                self.error_message = "Failed to grant consent. Please try again."

        except Exception as e:
            self.error_message = f"Error granting consent: {str(e)}"
            print(f"Error in grant_consent_confirmed: {e}")

        finally:
            self.is_loading = False

    @rx.event
    def show_revoke_confirmation(self):
        """Show the revoke consent confirmation modal."""
        self.show_revoke_modal = True

    @rx.event
    def hide_revoke_confirmation(self):
        """Hide the revoke consent confirmation modal."""
        self.show_revoke_modal = False

    @rx.event
    def revoke_consent_confirmed(self):
        """Revoke consent for the current user after confirmation."""
        if not self.selected_user_id:
            return

        self.is_loading = True
        self.error_message = ""

        try:
            success = revoke_user_consent(self.selected_user_id)

            if success:
                # Reload user data to reflect consent change
                self.load_user_data_event()
                self.show_revoke_modal = False
            else:
                self.error_message = "Failed to revoke consent. Please try again."

        except Exception as e:
            self.error_message = f"Error revoking consent: {str(e)}"
            print(f"Error in revoke_consent_confirmed: {e}")

        finally:
            self.is_loading = False

    # ==========================================================================
    # COMPUTED PROPERTIES
    # ==========================================================================

    @rx.var
    def consent_granted(self) -> bool:
        """Whether the current user has granted consent."""
        return self.user_data.get("consent_granted", False)

    @rx.var
    def user_name(self) -> str:
        """Current user's name."""
        return self.user_data.get("name", "Unknown User")

    @rx.var
    def persona(self) -> str:
        """Current user's persona identifier."""
        if self.persona_data:
            return self.persona_data.get("persona", "general")
        return "general"

    @rx.var
    def persona_info(self) -> Dict[str, str]:
        """Current user's persona description."""
        return get_persona_description(self.persona)

    @rx.var
    def has_recommendations(self) -> bool:
        """Whether the current user has any recommendations."""
        if not self.recommendations_data:
            return False
        return len(self.recommendations_data.get("recommendations", [])) > 0

    @rx.var
    def education_recommendations(self) -> List[Dict[str, Any]]:
        """Get only education recommendations."""
        if not self.recommendations_data:
            return []
        return [
            rec for rec in self.recommendations_data.get("recommendations", [])
            if rec.get("type") == "education"
        ]

    @rx.var
    def partner_offers(self) -> List[Dict[str, Any]]:
        """Get only partner offer recommendations."""
        if not self.recommendations_data:
            return []
        return [
            rec for rec in self.recommendations_data.get("recommendations", [])
            if rec.get("type") == "partner_offer"
        ]

    @rx.var
    def top_recommendations(self) -> List[Dict[str, Any]]:
        """Get top 3 recommendations for dashboard preview."""
        if not self.recommendations_data:
            return []
        return self.recommendations_data.get("recommendations", [])[:3]

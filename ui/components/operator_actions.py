"""Operator action components (approve, override, flag)."""

from nicegui import ui, app
from typing import Callable
from ui.utils.data_loaders import log_operator_override
from ui.utils.data_loaders import DB_PATH as _DB_PATH, SIGNALS_PATH as _SIGNALS_PATH, TRACES_DIR as _TRACES_DIR


def _get_data_mtime() -> float:
    """Return latest mtime among core data files/dirs."""
    mtimes = []
    try:
        if _DB_PATH.exists():
            mtimes.append(_DB_PATH.stat().st_mtime)
    except Exception:
        pass
    try:
        if _SIGNALS_PATH.exists():
            mtimes.append(_SIGNALS_PATH.stat().st_mtime)
    except Exception:
        pass
    try:
        if _TRACES_DIR.exists():
            latest = max((p.stat().st_mtime for p in _TRACES_DIR.glob('*.json')), default=0)
            mtimes.append(latest)
    except Exception:
        pass
    return max(mtimes) if mtimes else 0.0


def _notify_if_stale():
    """Warn operator if data changed since last refresh."""
    try:
        last_seen = app.storage.user.get('last_data_mtime', 0)
        if _get_data_mtime() > last_seen:
            ui.notify('New data available since your last refresh. Consider refreshing before acting.', type='warning')
    except Exception:
        pass


def create_operator_actions(
    user_id: str,
    recommendation_title: str,
    on_action_complete: Callable = None,
    theme_classes: str = "",
):
    """
    Create operator action buttons (approve, override, flag).

    Args:
        user_id: User ID
        recommendation_title: Title of recommendation
        Handlers read the current operator name from `app.storage.user` to avoid stale values
        on_action_complete: Callback after action is logged
        theme_classes: CSS classes from theme manager
    """

    def handle_approve():
        """Handle approve action."""
        _notify_if_stale()
        operator_name = app.storage.user.get("operator_name", "").strip()
        if not operator_name:
            ui.notify("Please enter operator name", type="warning")
            return

        success, message = log_operator_override(
            user_id=user_id,
            operator_name=operator_name,
            action="approve",
            reason="Approved by operator",
            recommendation_title=recommendation_title,
        )

        if success:
            ui.notify("Recommendation approved", type="positive")
            if on_action_complete:
                on_action_complete()
        else:
            ui.notify(f"Error: {message}", type="negative")

    def handle_override():
        """Open override dialog."""
        create_override_dialog(
            user_id=user_id,
            recommendation_title=recommendation_title,
            on_action_complete=on_action_complete,
        )

    def handle_flag():
        """Open flag dialog."""
        create_flag_dialog(
            user_id=user_id,
            recommendation_title=recommendation_title,
            on_action_complete=on_action_complete,
        )

    with ui.row().classes("gap-2"):
        ui.button("Approve", icon="check_circle", on_click=handle_approve).props(
            "color=positive"
        ).classes(theme_classes)

        ui.button("Override", icon="edit", on_click=handle_override).props("color=warning").classes(
            theme_classes
        )

        ui.button("Flag", icon="flag", on_click=handle_flag).props("color=negative").classes(
            theme_classes
        )


def create_override_dialog(
    user_id: str, recommendation_title: str, on_action_complete: Callable = None
):
    """
    Create dialog for override action.

    Args:
        user_id: User ID
        recommendation_title: Title of recommendation
        on_action_complete: Callback after action is logged
    """
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Override Recommendation").classes("text-lg font-bold mb-4")

        ui.label(f"User: {user_id}").classes("text-sm text-gray-600")
        ui.label(f"Recommendation: {recommendation_title}").classes("text-sm text-gray-600 mb-4")

        reason_input = ui.textarea(
            label="Reason for override",
            placeholder="Explain why you are overriding this recommendation...",
        ).classes("w-full")

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")

            def submit_override():
                _notify_if_stale()
                operator_name = app.storage.user.get("operator_name", "").strip()
                if not operator_name:
                    ui.notify("Please enter operator name first", type="warning")
                    return

                if not reason_input.value:
                    ui.notify("Please provide a reason", type="warning")
                    return

                success, message = log_operator_override(
                    user_id=user_id,
                    operator_name=operator_name,
                    action="override",
                    reason=reason_input.value,
                    recommendation_title=recommendation_title,
                )

                if success:
                    ui.notify("Override logged successfully", type="positive")
                    dialog.close()
                    if on_action_complete:
                        on_action_complete()
                else:
                    ui.notify(f"Error: {message}", type="negative")

            ui.button("Submit Override", icon="send", on_click=submit_override).props(
                "color=warning"
            )

    dialog.open()


def create_flag_dialog(
    user_id: str, recommendation_title: str, on_action_complete: Callable = None
):
    """
    Create dialog for flag action.

    Args:
        user_id: User ID
        recommendation_title: Title of recommendation
        on_action_complete: Callback after action is logged
    """
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Flag Recommendation").classes("text-lg font-bold mb-4")

        ui.label(f"User: {user_id}").classes("text-sm text-gray-600")
        ui.label(f"Recommendation: {recommendation_title}").classes("text-sm text-gray-600 mb-4")

        reason_input = ui.textarea(
            label="Reason for flagging",
            placeholder="Explain why you are flagging this recommendation...",
        ).classes("w-full")

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")

            def submit_flag():
                _notify_if_stale()
                operator_name = app.storage.user.get("operator_name", "").strip()
                if not operator_name:
                    ui.notify("Please enter operator name first", type="warning")
                    return

                if not reason_input.value:
                    ui.notify("Please provide a reason", type="warning")
                    return

                success, message = log_operator_override(
                    user_id=user_id,
                    operator_name=operator_name,
                    action="flag",
                    reason=reason_input.value,
                    recommendation_title=recommendation_title,
                )

                if success:
                    ui.notify("Recommendation flagged", type="positive")
                    dialog.close()
                    if on_action_complete:
                        on_action_complete()
                else:
                    ui.notify(f"Error: {message}", type="negative")

            ui.button("Submit Flag", icon="flag", on_click=submit_flag).props("color=negative")

    dialog.open()

"""Operator action components (approve, override, flag)."""

from nicegui import ui
from typing import Callable, Optional
from ui.utils.data_loaders import log_operator_override


def create_operator_actions(
    user_id: str,
    recommendation_title: str,
    operator_name_ref: dict,  # Dictionary reference to get operator name
    on_action_complete: Callable = None,
    theme_classes: str = ''
):
    """
    Create operator action buttons (approve, override, flag).

    Args:
        user_id: User ID
        recommendation_title: Title of recommendation
        operator_name_ref: Dict with 'value' key containing operator name
        on_action_complete: Callback after action is logged
        theme_classes: CSS classes from theme manager
    """

    def handle_approve():
        """Handle approve action."""
        if not operator_name_ref.get('value'):
            ui.notify('Please enter operator name', type='warning')
            return

        success, message = log_operator_override(
            user_id=user_id,
            operator_name=operator_name_ref['value'],
            action='approve',
            reason='Approved by operator',
            recommendation_title=recommendation_title
        )

        if success:
            ui.notify('Recommendation approved', type='positive')
            if on_action_complete:
                on_action_complete()
        else:
            ui.notify(f'Error: {message}', type='negative')

    def handle_override():
        """Open override dialog."""
        create_override_dialog(
            user_id=user_id,
            recommendation_title=recommendation_title,
            operator_name_ref=operator_name_ref,
            on_action_complete=on_action_complete
        )

    def handle_flag():
        """Open flag dialog."""
        create_flag_dialog(
            user_id=user_id,
            recommendation_title=recommendation_title,
            operator_name_ref=operator_name_ref,
            on_action_complete=on_action_complete
        )

    with ui.row().classes('gap-2'):
        ui.button('Approve', icon='check_circle', on_click=handle_approve) \
            .props('color=positive').classes(theme_classes)

        ui.button('Override', icon='edit', on_click=handle_override) \
            .props('color=warning').classes(theme_classes)

        ui.button('Flag', icon='flag', on_click=handle_flag) \
            .props('color=negative').classes(theme_classes)


def create_override_dialog(
    user_id: str,
    recommendation_title: str,
    operator_name_ref: dict,
    on_action_complete: Callable = None
):
    """
    Create dialog for override action.

    Args:
        user_id: User ID
        recommendation_title: Title of recommendation
        operator_name_ref: Dict with 'value' key containing operator name
        on_action_complete: Callback after action is logged
    """
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('Override Recommendation').classes('text-lg font-bold mb-4')

        ui.label(f'User: {user_id}').classes('text-sm text-gray-600')
        ui.label(f'Recommendation: {recommendation_title}').classes('text-sm text-gray-600 mb-4')

        reason_input = ui.textarea(
            label='Reason for override',
            placeholder='Explain why you are overriding this recommendation...'
        ).classes('w-full')

        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('Cancel', on_click=dialog.close).props('flat')

            def submit_override():
                if not operator_name_ref.get('value'):
                    ui.notify('Please enter operator name first', type='warning')
                    return

                if not reason_input.value:
                    ui.notify('Please provide a reason', type='warning')
                    return

                success, message = log_operator_override(
                    user_id=user_id,
                    operator_name=operator_name_ref['value'],
                    action='override',
                    reason=reason_input.value,
                    recommendation_title=recommendation_title
                )

                if success:
                    ui.notify('Override logged successfully', type='positive')
                    dialog.close()
                    if on_action_complete:
                        on_action_complete()
                else:
                    ui.notify(f'Error: {message}', type='negative')

            ui.button('Submit Override', icon='send', on_click=submit_override) \
                .props('color=warning')

    dialog.open()


def create_flag_dialog(
    user_id: str,
    recommendation_title: str,
    operator_name_ref: dict,
    on_action_complete: Callable = None
):
    """
    Create dialog for flag action.

    Args:
        user_id: User ID
        recommendation_title: Title of recommendation
        operator_name_ref: Dict with 'value' key containing operator name
        on_action_complete: Callback after action is logged
    """
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('Flag Recommendation').classes('text-lg font-bold mb-4')

        ui.label(f'User: {user_id}').classes('text-sm text-gray-600')
        ui.label(f'Recommendation: {recommendation_title}').classes('text-sm text-gray-600 mb-4')

        reason_input = ui.textarea(
            label='Reason for flagging',
            placeholder='Explain why you are flagging this recommendation...'
        ).classes('w-full')

        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('Cancel', on_click=dialog.close).props('flat')

            def submit_flag():
                if not operator_name_ref.get('value'):
                    ui.notify('Please enter operator name first', type='warning')
                    return

                if not reason_input.value:
                    ui.notify('Please provide a reason', type='warning')
                    return

                success, message = log_operator_override(
                    user_id=user_id,
                    operator_name=operator_name_ref['value'],
                    action='flag',
                    reason=reason_input.value,
                    recommendation_title=recommendation_title
                )

                if success:
                    ui.notify('Recommendation flagged', type='positive')
                    dialog.close()
                    if on_action_complete:
                        on_action_complete()
                else:
                    ui.notify(f'Error: {message}', type='negative')

            ui.button('Submit Flag', icon='flag', on_click=submit_flag) \
                .props('color=negative')

    dialog.open()

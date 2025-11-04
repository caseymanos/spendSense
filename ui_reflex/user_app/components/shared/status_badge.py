"""
Status Badge Component

Displays status indicators like consent granted/not granted,
active/inactive, etc. with appropriate colors and icons.
"""

import reflex as rx
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils import theme


def status_badge(
    is_active: bool,
    active_text: str = "Active",
    inactive_text: str = "Inactive",
    show_icon: bool = True,
) -> rx.Component:
    """Display a status badge with color coding.

    Args:
        is_active: Whether the status is active
        active_text: Text to display when active
        inactive_text: Text to display when inactive
        show_icon: Whether to show checkmark/x icon

    Returns:
        Reflex component
    """
    return rx.hstack(
        rx.cond(
            show_icon,
            rx.cond(
                is_active,
                rx.icon("check", size=16, color=theme.SUCCESS),
                rx.icon("x", size=16, color=theme.GRAY_400),
            ),
            rx.box(),
        ),
        rx.text(
            rx.cond(is_active, active_text, inactive_text),
            font_size=theme.FONT_SIZE_SM,
            font_weight=theme.FONT_WEIGHT_MEDIUM,
            color=rx.cond(is_active, theme.SUCCESS, theme.GRAY_600),
        ),
        padding=f"{theme.SPACE_1} {theme.SPACE_3}",
        border_radius=theme.BORDER_RADIUS_FULL,
        background=rx.cond(is_active, theme.SUCCESS_LIGHT, theme.GRAY_100),
        border=f"{theme.BORDER_WIDTH_1} solid {rx.cond(is_active, theme.SUCCESS, theme.GRAY_300)}",
        spacing="2",
        align_items="center",
    )


def consent_badge(consent_granted: bool, timestamp: str = None) -> rx.Component:
    """Display consent status badge with optional timestamp.

    Args:
        consent_granted: Whether consent is granted
        timestamp: Optional timestamp text to display

    Returns:
        Reflex component
    """
    # Always show badge with optional timestamp
    return rx.hstack(
        status_badge(
            is_active=consent_granted,
            active_text="Consent Granted",
            inactive_text="No Consent",
            show_icon=True,
        ),
        rx.cond(
            timestamp,
            rx.text(
                timestamp,
                font_size=theme.FONT_SIZE_SM,
                color=theme.GRAY_500,
                font_style="italic",
            ),
            rx.box(),  # Empty box when no timestamp
        ),
        spacing="2",
        align_items="center",
    )


def category_badge(category: str, color: str = None) -> rx.Component:
    """Display a category badge (for recommendations).

    Args:
        category: The category name
        color: Optional color override

    Returns:
        Reflex component
    """
    # Default category colors
    category_colors = {
        "credit": theme.PERSONA_COLORS["high_utilization"],
        "savings": theme.PERSONA_COLORS["savings_builder"],
        "subscriptions": theme.PERSONA_COLORS["subscription_heavy"],
        "income": theme.PERSONA_COLORS["variable_income"],
        "budgeting": theme.PRIMARY,
        "general": theme.GRAY_500,
    }

    badge_color = color or category_colors.get(category.lower(), theme.PRIMARY)

    return rx.box(
        rx.text(
            category.replace("_", " ").title(),
            font_size=theme.FONT_SIZE_XS,
            font_weight=theme.FONT_WEIGHT_MEDIUM,
            color=theme.WHITE,
        ),
        padding=f"{theme.SPACE_1} {theme.SPACE_3}",
        border_radius=theme.BORDER_RADIUS_FULL,
        background=badge_color,
    )


def alert_badge(text: str, alert_type: str = "info") -> rx.Component:
    """Display an alert-style badge.

    Args:
        text: The alert text
        alert_type: Type of alert - 'success', 'warning', 'danger', 'info'

    Returns:
        Reflex component
    """
    bg_color, text_color = theme.get_alert_colors(alert_type)

    icons = {
        "success": "check",
        "warning": "alert-triangle",
        "danger": "x",
        "info": "info",
    }

    return rx.hstack(
        rx.icon(icons.get(alert_type, "info"), size=16, color=text_color),
        rx.text(
            text,
            font_size=theme.FONT_SIZE_SM,
            font_weight=theme.FONT_WEIGHT_MEDIUM,
            color=text_color,
        ),
        padding=f"{theme.SPACE_2} {theme.SPACE_4}",
        border_radius=theme.BORDER_RADIUS_BASE,
        background=bg_color,
        border=f"{theme.BORDER_WIDTH_1} solid {text_color}",
        spacing="2",
        align_items="center",
    )

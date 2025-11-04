"""
Metric Card Component

Displays a single metric with label, value, and optional help text.
Used throughout the dashboard to show financial data points.
"""

import reflex as rx
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils import theme


def metric_card(
    label: str,
    value: str,
    help_text: str = None,
    color: str = theme.PRIMARY,
    icon: str = None,
) -> rx.Component:
    """Display a metric in a card format.

    Args:
        label: The metric label (e.g., "Credit Cards")
        value: The metric value (e.g., "3")
        help_text: Optional tooltip/help text
        color: Color for the value text
        icon: Optional emoji or icon to display

    Returns:
        Reflex component
    """
    return rx.box(
        rx.vstack(
            # Icon (if provided)
            rx.cond(
                icon is not None,
                rx.text(icon, font_size=theme.FONT_SIZE_2XL),
                rx.box(),
            ),
            # Label
            rx.text(
                label,
                font_size=theme.FONT_SIZE_SM,
                color=theme.GRAY_600,
                font_weight=theme.FONT_WEIGHT_MEDIUM,
            ),
            # Value
            rx.text(
                value,
                font_size=theme.FONT_SIZE_2XL,
                font_weight=theme.FONT_WEIGHT_BOLD,
                color=color,
            ),
            # Help text (if provided)
            rx.cond(
                help_text is not None,
                rx.text(
                    help_text,
                    font_size=theme.FONT_SIZE_XS,
                    color=theme.GRAY_500,
                    text_align="center",
                ),
                rx.box(),
            ),
            spacing="2",
            align_items="center",
            justify_content="center",
        ),
        padding=theme.SPACE_5,
        border_radius=theme.BORDER_RADIUS_MD,
        border=f"{theme.BORDER_WIDTH_1} solid {theme.GRAY_200}",
        background=theme.WHITE,
        box_shadow=theme.SHADOW_BASE,
        min_height="140px",
        _hover={
            "box_shadow": theme.SHADOW_MD,
            "transform": "translateY(-2px)",
            "transition": "all 0.2s ease-in-out",
        },
    )


def metric_card_skeleton() -> rx.Component:
    """Loading skeleton for metric card.

    Returns:
        Reflex component showing loading state
    """
    return rx.box(
        rx.vstack(
            rx.skeleton(height="24px", width="60%"),
            rx.skeleton(height="32px", width="80%"),
            rx.skeleton(height="14px", width="100%"),
            spacing="2",
            align_items="center",
        ),
        padding=theme.SPACE_5,
        border_radius=theme.BORDER_RADIUS_MD,
        border=f"{theme.BORDER_WIDTH_1} solid {theme.GRAY_200}",
        background=theme.WHITE,
        min_height="140px",
    )

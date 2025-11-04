"""
Persona Badge Component

Displays a user's persona with icon, title, and color coding.
Includes expandable section to show why the persona was assigned.
"""

import reflex as rx
from typing import Dict, List
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils import theme


def persona_badge(
    persona_info: Dict[str, str],
    show_description: bool = True,
    size: str = "lg",
) -> rx.Component:
    """Display a persona badge with icon and title.

    Args:
        persona_info: Dictionary with 'icon', 'title', 'description', 'color'
        show_description: Whether to show the description text
        size: Size variant - 'sm', 'md', or 'lg'

    Returns:
        Reflex component
    """
    # Size-specific styling
    size_config = {
        "sm": {
            "icon_size": theme.FONT_SIZE_2XL,
            "title_size": theme.FONT_SIZE_BASE,
            "desc_size": theme.FONT_SIZE_SM,
            "padding": theme.SPACE_3,
        },
        "md": {
            "icon_size": theme.FONT_SIZE_3XL,
            "title_size": theme.FONT_SIZE_LG,
            "desc_size": theme.FONT_SIZE_BASE,
            "padding": theme.SPACE_4,
        },
        "lg": {
            "icon_size": theme.FONT_SIZE_4XL,
            "title_size": theme.FONT_SIZE_2XL,
            "desc_size": theme.FONT_SIZE_LG,
            "padding": theme.SPACE_6,
        },
    }

    config = size_config.get(size, size_config["md"])

    return rx.box(
        rx.hstack(
            # Icon
            rx.text(
                persona_info.get("icon", "🌱"),
                font_size=config["icon_size"],
            ),
            # Text content
            rx.vstack(
                # Title
                rx.text(
                    persona_info.get("title", "Unknown Persona"),
                    font_size=config["title_size"],
                    font_weight=theme.FONT_WEIGHT_BOLD,
                    color=theme.GRAY_900,
                ),
                # Description (if enabled)
                rx.cond(
                    show_description,
                    rx.text(
                        persona_info.get("description", ""),
                        font_size=config["desc_size"],
                        color=theme.GRAY_600,
                        line_height=theme.LINE_HEIGHT_RELAXED,
                    ),
                    rx.box(),
                ),
                spacing="2",
                align_items="flex-start",
                flex="1",
            ),
            spacing="4",
            align_items="center",
            width="100%",
        ),
        padding=config["padding"],
        border_radius=theme.BORDER_RADIUS_MD,
        background=theme.WHITE,
        border=f"{theme.BORDER_WIDTH_2} solid {persona_info.get('color', theme.PRIMARY)}",
        box_shadow=theme.SHADOW_BASE,
    )


def persona_section_with_criteria(
    persona_info: Dict[str, str],
    criteria_met: List[str] = None,
) -> rx.Component:
    """Display persona with expandable criteria section.

    Args:
        persona_info: Dictionary with 'icon', 'title', 'description', 'color'
        criteria_met: List of criteria strings that were met

    Returns:
        Reflex component
    """
    return rx.vstack(
        # Main persona badge
        persona_badge(persona_info, show_description=True, size="lg"),
        # Criteria section (if provided)
        rx.cond(
            criteria_met is not None and len(criteria_met) > 0,
            rx.box(
                rx.details(
                    rx.summary(
                        rx.hstack(
                            rx.text(
                                "Why this profile?",
                                font_size=theme.FONT_SIZE_SM,
                                font_weight=theme.FONT_WEIGHT_SEMIBOLD,
                                color=theme.GRAY_700,
                            ),
                            rx.icon("chevron-down", size=16),
                            spacing="2",
                        ),
                    ),
                    rx.vstack(
                        rx.text(
                            "Key patterns detected:",
                            font_size=theme.FONT_SIZE_SM,
                            font_weight=theme.FONT_WEIGHT_MEDIUM,
                            color=theme.GRAY_600,
                            margin_top=theme.SPACE_3,
                        ),
                        rx.foreach(
                            criteria_met,
                            lambda criterion: rx.hstack(
                                rx.text("•", color=persona_info.get("color", theme.PRIMARY)),
                                rx.text(
                                    criterion,
                                    font_size=theme.FONT_SIZE_SM,
                                    color=theme.GRAY_600,
                                ),
                                spacing="2",
                                align_items="flex-start",
                            ),
                        ),
                        spacing="2",
                        align_items="flex-start",
                        width="100%",
                    ),
                ),
                padding=theme.SPACE_4,
                border_radius=theme.BORDER_RADIUS_BASE,
                background=theme.GRAY_50,
                margin_top=theme.SPACE_3,
            ),
            rx.box(),
        ),
        spacing="3",
        width="100%",
    )


def persona_badge_inline(persona_info: Dict[str, str]) -> rx.Component:
    """Display a compact inline persona badge.

    Args:
        persona_info: Dictionary with 'icon', 'title', 'color'

    Returns:
        Reflex component
    """
    return rx.hstack(
        rx.text(persona_info.get("icon", "🌱"), font_size=theme.FONT_SIZE_BASE),
        rx.text(
            persona_info.get("title", "Unknown"),
            font_size=theme.FONT_SIZE_SM,
            font_weight=theme.FONT_WEIGHT_MEDIUM,
            color=theme.GRAY_700,
        ),
        padding=f"{theme.SPACE_1} {theme.SPACE_3}",
        border_radius=theme.BORDER_RADIUS_FULL,
        background=theme.GRAY_100,
        border=f"{theme.BORDER_WIDTH_1} solid {persona_info.get('color', theme.GRAY_300)}",
        spacing="2",
    )

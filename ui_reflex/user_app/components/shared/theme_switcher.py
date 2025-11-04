"""
Theme Switcher Component

Beautiful theme selector with live preview colors for each theme.
"""

import reflex as rx


def theme_preview_card(theme_name: str, display_name: str, preview_colors: list[str], is_active: bool, on_click) -> rx.Component:
    """
    Preview card for a single theme.

    Args:
        theme_name: Internal theme identifier
        display_name: Display name for the theme
        preview_colors: List of 3-4 colors representing the theme
        is_active: Whether this theme is currently active
        on_click: Click handler
    """
    return rx.box(
        rx.vstack(
            # Color preview circles
            rx.hstack(
                *[
                    rx.box(
                        width="2rem",
                        height="2rem",
                        border_radius="50%",
                        background=color,
                        box_shadow="0 2px 4px rgba(0, 0, 0, 0.1)",
                    )
                    for color in preview_colors
                ],
                spacing="2",
                justify="center",
                margin_bottom="3",
            ),
            # Theme name
            rx.text(
                display_name,
                font_weight=rx.cond(is_active, "600", "500"),
                font_size="0.875rem",
                color=rx.cond(is_active, "#3B82F6", "#4B5563"),
            ),
            # Active indicator
            rx.cond(
                is_active,
                rx.box(
                    rx.text("✓ Active", font_size="0.75rem", color="#10B981"),
                    padding="0.25rem 0.5rem",
                    background="#D1FAE5",
                    border_radius="0.25rem",
                ),
                rx.box(height="1.5rem"),  # Spacer when not active
            ),
            spacing="2",
            align_items="center",
        ),
        padding="1rem",
        background=rx.cond(is_active, "#F0F9FF", "#FFFFFF"),
        border=rx.cond(
            is_active,
            "2px solid #3B82F6",
            "1px solid #E5E7EB",
        ),
        border_radius="0.75rem",
        cursor="pointer",
        transition="all 0.2s ease",
        _hover={
            "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            "transform": "translateY(-2px)",
        },
        on_click=on_click,
    )


def theme_switcher(current_theme: str, on_default, on_dark, on_glass, on_minimal, on_vibrant) -> rx.Component:
    """
    Theme switcher component with preview cards for all themes.

    Args:
        current_theme: Current active theme name
        on_default: Event handler for default theme
        on_dark: Event handler for dark theme
        on_glass: Event handler for glass theme
        on_minimal: Event handler for minimal theme
        on_vibrant: Event handler for vibrant theme
    """
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading(
                    "🎨 Choose Your Theme",
                    size="6",
                    color="#111827",
                ),
                width="100%",
                align_items="center",
                margin_bottom="4",
            ),
            # Description
            rx.text(
                "Select a theme to customize your SpendSense experience. Changes apply instantly.",
                font_size="0.875rem",
                color="#6B7280",
                margin_bottom="6",
            ),
            # Theme grid
            rx.grid(
                # Default Light
                theme_preview_card(
                    theme_name="default",
                    display_name="Default Light",
                    preview_colors=["#3B82F6", "#10B981", "#F59E0B"],
                    is_active=current_theme == "default",
                    on_click=on_default,
                ),
                # Dark Mode
                theme_preview_card(
                    theme_name="dark",
                    display_name="Dark Mode",
                    preview_colors=["#0F172A", "#60A5FA", "#34D399"],
                    is_active=current_theme == "dark",
                    on_click=on_dark,
                ),
                # Glassmorphism
                theme_preview_card(
                    theme_name="glass",
                    display_name="Glassmorphism",
                    preview_colors=["#667eea", "#764ba2", "#A78BFA"],
                    is_active=current_theme == "glass",
                    on_click=on_glass,
                ),
                # Minimal
                theme_preview_card(
                    theme_name="minimal",
                    display_name="Minimal",
                    preview_colors=["#1A1A1A", "#666666", "#00C853"],
                    is_active=current_theme == "minimal",
                    on_click=on_minimal,
                ),
                # Vibrant
                theme_preview_card(
                    theme_name="vibrant",
                    display_name="Vibrant",
                    preview_colors=["#EC4899", "#8B5CF6", "#22C55E"],
                    is_active=current_theme == "vibrant",
                    on_click=on_vibrant,
                ),
                columns="5",
                spacing="4",
                width="100%",
            ),
            spacing="0",
            width="100%",
        ),
        padding="6",
        background="#FFFFFF",
        border="1px solid #E5E7EB",
        border_radius="1rem",
        box_shadow="0 10px 15px -3px rgba(0, 0, 0, 0.1)",
        margin_bottom="6",
    )


def theme_switcher_button(on_click) -> rx.Component:
    """
    Floating theme switcher button that opens the theme selector.

    Args:
        on_click: Click handler to open theme selector
    """
    return rx.button(
        "🎨",
        on_click=on_click,
        position="fixed",
        bottom="2rem",
        right="2rem",
        width="3.5rem",
        height="3.5rem",
        border_radius="50%",
        background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        color="#FFFFFF",
        font_size="1.5rem",
        box_shadow="0 10px 25px rgba(102, 126, 234, 0.3)",
        border="none",
        cursor="pointer",
        z_index="1000",
        transition="all 0.3s ease",
        _hover={
            "transform": "scale(1.1) rotate(15deg)",
            "box_shadow": "0 15px 30px rgba(102, 126, 234, 0.4)",
        },
    )

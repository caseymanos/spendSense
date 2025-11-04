"""SpendSense User Dashboard - Multi-Theme Version

Features 5 stunning themes:
- Default Light: Clean, modern, professional
- Dark Mode: Sleek dark with excellent contrast
- Glassmorphism: Modern frosted glass aesthetic
- Minimal: Ultra-clean, content-first design
- Vibrant: Bold, colorful, energetic
"""

import reflex as rx
from .state.user_state import UserAppState
from .components.shared.theme_switcher import theme_switcher, theme_switcher_button
from .utils.formatters import format_currency


def navbar() -> rx.Component:
    """Top navigation bar with dynamic theming."""
    return rx.box(
        rx.hstack(
            # Logo and title
            rx.heading("💰 SpendSense", size="7", color=UserAppState.theme_text_primary),
            rx.spacer(),
            # Navigation buttons
            rx.button(
                "Dashboard",
                on_click=UserAppState.navigate_to_dashboard,
                variant="ghost",
                color=UserAppState.theme_text_primary,
            ),
            rx.button(
                "Learning Feed",
                on_click=UserAppState.navigate_to_learning_feed,
                variant="ghost",
                color=UserAppState.theme_text_primary,
            ),
            rx.button(
                "Privacy",
                on_click=UserAppState.navigate_to_privacy,
                variant="ghost",
                color=UserAppState.theme_text_primary,
            ),
            # User info
            rx.hstack(
                rx.text(UserAppState.user_name, font_weight="500", color=UserAppState.theme_text_primary),
                rx.badge(
                    rx.cond(UserAppState.consent_granted, "✓ Active", "✗ Inactive"),
                    color_scheme=rx.cond(UserAppState.consent_granted, "green", "gray"),
                ),
                spacing="3",
            ),
            spacing="4",
            width="100%",
        ),
        padding="4",
        background=UserAppState.theme_surface,
        border_bottom=f"1px solid",
        border_color=UserAppState.theme_border,
        position="sticky",
        top="0",
        z_index="100",
    )


def user_selector() -> rx.Component:
    """User selection dropdown with consent status info."""
    return rx.vstack(
        rx.select(
            UserAppState.user_ids,
            value=UserAppState.selected_user_id,
            on_change=UserAppState.select_user,
            placeholder="Select a user...",
            width="100%",
        ),
        rx.text(
            "Tip: Users 0-9 have consent granted for testing. Try user_0010+ to test consent flow.",
            font_size="0.875rem",
            color=UserAppState.theme_text_muted,
            font_style="italic",
        ),
        spacing="1",
        align_items="flex_start",
        width="100%",
    )


def metric_card_themed(label: str, value, help_text: str, color) -> rx.Component:
    """Themed metric card."""
    return rx.box(
        rx.vstack(
            rx.text(
                label,
                font_size="0.875rem",
                font_weight="500",
                color=UserAppState.theme_text_secondary,
                margin_bottom="2",
            ),
            rx.text(
                value,
                font_size="2rem",
                font_weight="700",
                color=color,
                line_height="1",
                margin_bottom="1",
            ),
            rx.text(
                help_text,
                font_size="0.75rem",
                color=UserAppState.theme_text_muted,
            ),
            spacing="1",
            align_items="center",
        ),
        padding="5",
        background=UserAppState.theme_surface,
        border="1px solid",
        border_color=UserAppState.theme_border,
        border_radius=UserAppState.theme_border_radius,
        box_shadow=UserAppState.theme_shadow,
        transition="all 0.2s ease",
        _hover={"box_shadow": UserAppState.theme_shadow_lg, "transform": "translateY(-2px)"},
    )


def persona_badge_themed() -> rx.Component:
    """Themed persona badge."""
    return rx.box(
        rx.vstack(
            rx.heading(
                f"🎯 Your Persona: {UserAppState.persona_info.get('name', 'Unknown')}",
                size="6",
                color=UserAppState.theme_text_primary,
                margin_bottom="3",
            ),
            rx.box(
                rx.text(
                    UserAppState.persona_info.get("description", "No description available"),
                    color=UserAppState.theme_text_secondary,
                    line_height="1.6",
                ),
                padding="4",
                background=UserAppState.theme_surface,
                border_left="4px solid",
                border_color=UserAppState.theme_primary,
                border_radius=UserAppState.theme_border_radius,
            ),
            spacing="2",
            align_items="flex_start",
            width="100%",
        ),
        padding="6",
        background=UserAppState.theme_surface,
        border="1px solid",
        border_color=UserAppState.theme_border,
        border_radius=UserAppState.theme_border_radius,
        box_shadow=UserAppState.theme_shadow,
        margin_bottom="6",
    )


def recommendation_card_themed(rec) -> rx.Component:
    """Themed recommendation card."""
    return rx.box(
        rx.vstack(
            rx.heading(rec["title"], size="5", color=UserAppState.theme_text_primary),
            rx.text(rec["description"], color=UserAppState.theme_text_secondary, margin_bottom="2"),
            rx.box(
                rx.text(
                    f"💡 {rec['rationale']}",
                    font_style="italic",
                    color=UserAppState.theme_text_secondary,
                ),
                padding="3",
                background=UserAppState.theme_info_light,
                border_radius=UserAppState.theme_border_radius,
            ),
            spacing="2",
            align_items="flex_start",
        ),
        padding="5",
        background=UserAppState.theme_surface,
        border="1px solid",
        border_color=UserAppState.theme_border,
        border_radius=UserAppState.theme_border_radius,
        box_shadow=UserAppState.theme_shadow,
        margin_bottom="3",
        transition="all 0.2s ease",
        _hover={"box_shadow": UserAppState.theme_shadow_lg, "transform": "translateY(-2px)"},
    )


def index() -> rx.Component:
    """Main app entry point with dynamic theming."""
    return rx.box(
        navbar(),
        rx.container(
            # Theme switcher panel (conditionally shown)
            rx.cond(
                UserAppState.show_theme_switcher,
                theme_switcher(
                    UserAppState.current_theme,
                    UserAppState.change_theme,
                ),
                rx.box(),  # Empty placeholder when hidden
            ),
            # User selector
            rx.vstack(
                rx.heading("Select User", size="5", color=UserAppState.theme_text_primary),
                user_selector(),
                spacing="2",
                align_items="flex_start",
                margin_bottom="8",
            ),
            # Loading state
            rx.cond(
                UserAppState.is_loading,
                rx.spinner(size="3"),
                # Content (when not loading)
                rx.cond(
                    UserAppState.consent_granted,
                    # Dashboard content (consent granted)
                    rx.vstack(
                        # Consent info banner
                        rx.box(
                            rx.hstack(
                                rx.vstack(
                                    rx.heading(
                                        "✓ Data Analysis Active",
                                        size="4",
                                        color=UserAppState.theme_success,
                                        margin_bottom="1",
                                    ),
                                    rx.text(
                                        UserAppState.consent_status_text,
                                        font_size="0.875rem",
                                        color=UserAppState.theme_text_secondary,
                                    ),
                                    spacing="0",
                                    align_items="flex_start",
                                ),
                                rx.spacer(),
                                rx.button(
                                    "Revoke Consent",
                                    on_click=UserAppState.revoke_consent_confirmed,
                                    variant="outline",
                                    color_scheme="red",
                                    size="2",
                                ),
                                spacing="4",
                                width="100%",
                                align_items="center",
                            ),
                            padding="4",
                            background=UserAppState.theme_success_light,
                            border="1px solid",
                            border_color=UserAppState.theme_success,
                            border_radius=UserAppState.theme_border_radius,
                            margin_bottom="6",
                        ),
                        # Persona section
                        persona_badge_themed(),
                        # Metrics grid
                        rx.heading(
                            "Your Financial Snapshot",
                            size="7",
                            margin_bottom="4",
                            color=UserAppState.theme_text_primary,
                        ),
                        rx.grid(
                            metric_card_themed(
                                label="Credit Cards",
                                value=rx.cond(
                                    UserAppState.signals.get("credit_num_cards"),
                                    rx.text(str(UserAppState.signals["credit_num_cards"])),
                                    rx.text("0"),
                                ),
                                help_text="Active accounts",
                                color=UserAppState.theme_persona_high_util,
                            ),
                            metric_card_themed(
                                label="Subscriptions",
                                value=rx.cond(
                                    UserAppState.signals.get("sub_180d_recurring_count"),
                                    rx.text(str(UserAppState.signals["sub_180d_recurring_count"])),
                                    rx.text("0"),
                                ),
                                help_text="Recurring services",
                                color=UserAppState.theme_persona_subscription,
                            ),
                            metric_card_themed(
                                label="Savings (6mo)",
                                value=rx.text("$0"),  # Simplified for now
                                help_text="Net inflow",
                                color=UserAppState.theme_persona_savings,
                            ),
                            columns="3",
                            spacing="4",
                        ),
                        # Recommendations preview
                        rx.heading(
                            "Your Recommendations",
                            size="7",
                            margin_top="8",
                            margin_bottom="4",
                            color=UserAppState.theme_text_primary,
                        ),
                        rx.cond(
                            UserAppState.has_recommendations,
                            rx.vstack(
                                rx.foreach(
                                    UserAppState.top_recommendations,
                                    recommendation_card_themed,
                                ),
                                spacing="3",
                            ),
                            rx.text("No recommendations available", color=UserAppState.theme_text_muted),
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    # Consent banner (no consent)
                    rx.box(
                        rx.heading(
                            "Consent Not Yet Granted",
                            size="7",
                            margin_bottom="3",
                            color=UserAppState.theme_text_primary,
                        ),
                        rx.text(
                            UserAppState.consent_status_text,
                            margin_bottom="4",
                            color=UserAppState.theme_text_secondary,
                            font_style="italic",
                        ),
                        rx.text(
                            "To provide personalized financial insights and recommendations, we need your consent to analyze your transaction data.",
                            margin_bottom="4",
                            color=UserAppState.theme_text_secondary,
                        ),
                        rx.button(
                            "Grant Consent",
                            on_click=UserAppState.grant_consent_confirmed,
                            background=UserAppState.theme_primary,
                            color="#FFFFFF",
                            size="3",
                        ),
                        padding="8",
                        background=UserAppState.theme_warning_light,
                        border="2px solid",
                        border_color=UserAppState.theme_warning,
                        border_radius=UserAppState.theme_border_radius,
                    ),
                ),
            ),
            padding="8",
            max_width="1200px",
        ),
        # Floating theme switcher button
        theme_switcher_button(UserAppState.toggle_theme_switcher),
        background=UserAppState.theme_background,
        min_height="100vh",
    )


# Create app
app = rx.App()

# Add main page with data loading on mount
app.add_page(
    index,
    route="/",
    title="SpendSense - Your Themed Financial Dashboard",
    on_load=UserAppState.on_load,
)

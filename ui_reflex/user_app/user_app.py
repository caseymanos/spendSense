"""SpendSense User Dashboard - Themed Reflex Implementation"""

import reflex as rx
from .state.user_state import UserAppState
from .components.shared.theme_switcher import theme_switcher, theme_switcher_button
from .utils.themes import get_theme, get_persona_color
from .utils.formatters import format_currency


def navbar(theme_config) -> rx.Component:
    """Top navigation bar with theme colors."""
    theme = theme_config.colors

    return rx.box(
        rx.hstack(
            # Logo and title
            rx.heading("💰 SpendSense", size="7", color=theme.text_primary),
            rx.spacer(),
            # Navigation buttons
            rx.button(
                "Dashboard",
                on_click=UserAppState.navigate_to_dashboard,
                variant="ghost",
                color=theme.text_primary,
            ),
            rx.button(
                "Learning Feed",
                on_click=UserAppState.navigate_to_learning_feed,
                variant="ghost",
                color=theme.text_primary,
            ),
            rx.button(
                "Privacy",
                on_click=UserAppState.navigate_to_privacy,
                variant="ghost",
                color=theme.text_primary,
            ),
            # User info
            rx.hstack(
                rx.text(UserAppState.user_name, as_="div", font_weight="500", color=theme.text_primary),
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
        background=theme.surface,
        border_bottom=f"1px solid {theme.border}",
        position="sticky",
        top="0",
        z_index="100",
        backdrop_filter=rx.cond(
            UserAppState.current_theme == "glass",
            "blur(10px)",
            "none",
        ),
    )


def user_selector(theme_config) -> rx.Component:
    """User selection dropdown with consent status info."""
    theme = theme_config.colors

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
            as_="div",
            font_size="0.875rem",
            color=theme.text_muted,
            font_style="italic",
        ),
        spacing="1",
        align_items="flex-start",
        width="100%",
    )


def metric_card_themed(label: str, value: str, help_text: str, color: str, theme_config) -> rx.Component:
    """Themed metric card."""
    theme = theme_config.colors

    return rx.box(
        rx.vstack(
            rx.text(
                label,
                as_="div",
                font_size="0.875rem",
                font_weight="500",
                color=theme.text_secondary,
                margin_bottom="2",
            ),
            rx.text(
                value,
                as_="div",
                font_size="2rem",
                font_weight="700",
                color=color,
                line_height="1",
                margin_bottom="1",
            ),
            rx.text(
                help_text,
                as_="div",
                font_size="0.75rem",
                color=theme.text_muted,
            ),
            spacing="1",
            align_items="center",
        ),
        padding="5",
        background=theme.surface,
        border=f"1px solid {theme.border}",
        border_radius=theme_config.border_radius,
        box_shadow=theme.shadow,
        transition="all 0.2s ease",
        _hover={"box_shadow": theme.shadow_lg, "transform": "translateY(-2px)"},
    )


def persona_badge_themed(persona_info: dict, persona_id: str, theme_config) -> rx.Component:
    """Themed persona badge."""
    theme = theme_config.colors
    persona_color = get_persona_color(theme_config, persona_id)

    return rx.box(
        rx.vstack(
            rx.heading(
                f"{persona_info.get('icon', '🎯')} Your Persona: {persona_info.get('title', 'Unknown')}",
                size="6",
                color=theme.text_primary,
                margin_bottom="3",
            ),
            rx.box(
                rx.text(
                    persona_info.get("description", "No description available"),
                    as_="div",
                    color=theme.text_secondary,
                    line_height="1.6",
                ),
                padding="4",
                background=theme.surface,
                border_left=f"4px solid {persona_color}",
                border_radius=theme_config.border_radius,
            ),
            spacing="2",
            align_items="flex-start",
            width="100%",
        ),
        padding="6",
        background=theme.surface,
        border=f"1px solid {theme.border}",
        border_radius=theme_config.border_radius,
        box_shadow=theme.shadow,
        margin_bottom="6",
    )


def recommendation_card_themed(rec: dict, theme_config) -> rx.Component:
    """Themed recommendation card."""
    theme = theme_config.colors

    return rx.box(
        rx.vstack(
            rx.heading(rec["title"], size="5", color=theme.text_primary),
            rx.text(rec["description"], as_="div", color=theme.text_secondary, margin_bottom="2"),
            rx.box(
                rx.text(
                    f"💡 {rec['rationale']}",
                    as_="div",
                    font_style="italic",
                    color=theme.text_secondary,
                ),
                padding="3",
                background=theme.info_light,
                border_radius=theme_config.border_radius,
            ),
            spacing="2",
            align_items="flex-start",
        ),
        padding="5",
        background=theme.surface,
        border=f"1px solid {theme.border}",
        border_radius=theme_config.border_radius,
        box_shadow=theme.shadow,
        margin_bottom="3",
        transition="all 0.2s ease",
        _hover={"box_shadow": theme.shadow_lg, "transform": "translateY(-2px)"},
    )


def dashboard_view(theme_config) -> rx.Component:
    """Dashboard view - shows persona, metrics, and recommendations."""
    theme = theme_config.colors

    return rx.cond(
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
                            color=theme.success,
                            margin_bottom="1",
                        ),
                        rx.text(
                            UserAppState.consent_status_text,
                            as_="div",
                            font_size="0.875rem",
                            color=theme.text_secondary,
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
                background=theme.success_light,
                border=f"1px solid {theme.success}",
                border_radius=theme_config.border_radius,
                margin_bottom="6",
            ),
            # Persona section
            persona_badge_themed(UserAppState.persona_info, UserAppState.persona, theme_config),
            # Metrics grid
            rx.heading(
                "Your Financial Snapshot",
                size="7",
                margin_bottom="4",
                color=theme.text_primary,
            ),
            rx.grid(
                metric_card_themed(
                    label="Credit Cards",
                    value=UserAppState.safe_credit_num_cards,
                    help_text="Active accounts",
                    color=theme.persona_high_util,
                    theme_config=theme_config,
                ),
                metric_card_themed(
                    label="Subscriptions",
                    value=UserAppState.safe_sub_count,
                    help_text="Recurring services",
                    color=theme.persona_subscription,
                    theme_config=theme_config,
                ),
                metric_card_themed(
                    label="Savings (6mo)",
                    value=UserAppState.safe_sav_net_inflow,
                    help_text="Net inflow",
                    color=theme.persona_savings,
                    theme_config=theme_config,
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
                color=theme.text_primary,
            ),
            rx.cond(
                UserAppState.has_recommendations,
                rx.vstack(
                    rx.foreach(
                        UserAppState.top_recommendations,
                        lambda rec: recommendation_card_themed(rec, theme_config),
                    ),
                    spacing="3",
                ),
                rx.text("No recommendations available", as_="div", color=theme.text_muted),
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
                color=theme.text_primary,
            ),
            rx.text(
                UserAppState.consent_status_text,
                as_="div",
                margin_bottom="4",
                color=theme.text_secondary,
                font_style="italic",
            ),
            rx.text(
                "To provide personalized financial insights and recommendations, we need your consent to analyze your transaction data.",
                as_="div",
                margin_bottom="4",
                color=theme.text_secondary,
            ),
            rx.button(
                "Grant Consent",
                on_click=UserAppState.grant_consent_confirmed,
                background=theme.primary,
                color="#FFFFFF",
                size="3",
                _hover={"background": theme.primary_hover},
            ),
            padding="8",
            background=theme.warning_light,
            border=f"2px solid {theme.warning}",
            border_radius=theme_config.border_radius,
        ),
    )


def learning_feed_view(theme_config) -> rx.Component:
    """Learning feed view - educational content and insights."""
    theme = theme_config.colors

    return rx.vstack(
        rx.heading(
            "📚 Learning Feed",
            size="8",
            margin_bottom="4",
            color=theme.text_primary,
        ),
        rx.text(
            "Explore educational content and insights about your financial behaviors.",
            as_="div",
            font_size="1.1rem",
            margin_bottom="6",
            color=theme.text_secondary,
        ),
        rx.cond(
            UserAppState.consent_granted,
            rx.vstack(
                rx.foreach(
                    UserAppState.recommendations,
                    lambda rec: recommendation_card_themed(rec, theme_config),
                ),
                spacing="4",
                width="100%",
            ),
            rx.box(
                rx.heading(
                    "Grant Consent to View Learning Feed",
                    size="6",
                    margin_bottom="3",
                    color=theme.text_primary,
                ),
                rx.text(
                    "To see personalized educational content, please grant consent to analyze your transaction data.",
                    as_="div",
                    margin_bottom="4",
                    color=theme.text_secondary,
                ),
                rx.button(
                    "Grant Consent",
                    on_click=UserAppState.grant_consent_confirmed,
                    background=theme.primary,
                    color="#FFFFFF",
                    size="3",
                    _hover={"background": theme.primary_hover},
                ),
                padding="8",
                background=theme.warning_light,
                border=f"2px solid {theme.warning}",
                border_radius=theme_config.border_radius,
            ),
        ),
        spacing="4",
        width="100%",
    )


def privacy_view(theme_config) -> rx.Component:
    """Privacy view - consent management and data controls."""
    theme = theme_config.colors

    return rx.vstack(
        rx.heading(
            "🔒 Privacy & Consent",
            size="8",
            margin_bottom="4",
            color=theme.text_primary,
        ),
        rx.text(
            "Manage your data consent and privacy settings.",
            as_="div",
            font_size="1.1rem",
            margin_bottom="6",
            color=theme.text_secondary,
        ),
        # Consent status card
        rx.box(
            rx.heading(
                rx.cond(
                    UserAppState.consent_granted,
                    "✓ Consent Active",
                    "✗ Consent Not Granted",
                ),
                size="6",
                margin_bottom="3",
                color=rx.cond(UserAppState.consent_granted, theme.success, theme.warning),
            ),
            rx.text(
                UserAppState.consent_status_text,
                as_="div",
                margin_bottom="4",
                color=theme.text_secondary,
            ),
            rx.cond(
                UserAppState.consent_granted,
                rx.button(
                    "Revoke Consent",
                    on_click=UserAppState.revoke_consent_confirmed,
                    variant="outline",
                    color_scheme="red",
                    size="3",
                ),
                rx.button(
                    "Grant Consent",
                    on_click=UserAppState.grant_consent_confirmed,
                    background=theme.primary,
                    color="#FFFFFF",
                    size="3",
                    _hover={"background": theme.primary_hover},
                ),
            ),
            padding="6",
            background=rx.cond(
                UserAppState.consent_granted,
                theme.success_light,
                theme.warning_light,
            ),
            border=rx.cond(
                UserAppState.consent_granted,
                f"2px solid {theme.success}",
                f"2px solid {theme.warning}",
            ),
            border_radius=theme_config.border_radius,
            margin_bottom="6",
        ),
        # Privacy information
        rx.box(
            rx.heading(
                "How We Use Your Data",
                size="5",
                margin_bottom="3",
                color=theme.text_primary,
            ),
            rx.vstack(
                rx.text("• We analyze your transaction data to detect behavioral patterns", color=theme.text_secondary),
                rx.text("• We assign you a persona based on your spending habits", color=theme.text_secondary),
                rx.text("• We provide educational recommendations (not financial advice)", color=theme.text_secondary),
                rx.text("• All data is processed locally - no external sharing", color=theme.text_secondary),
                rx.text("• You can revoke consent at any time", color=theme.text_secondary),
                spacing="2",
                align_items="flex_start",
            ),
            padding="6",
            background=theme.surface,
            border=f"1px solid {theme.border}",
            border_radius=theme_config.border_radius,
        ),
        spacing="4",
        width="100%",
    )


def themed_dashboard(theme_config) -> rx.Component:
    """Main themed dashboard."""
    theme = theme_config.colors

    return rx.box(
        navbar(theme_config),
        rx.container(
            # Theme switcher panel (conditionally shown)
            rx.cond(
                UserAppState.show_theme_switcher,
                theme_switcher(
                    UserAppState.current_theme,
                    UserAppState.change_theme_default,
                    UserAppState.change_theme_dark,
                    UserAppState.change_theme_glass,
                    UserAppState.change_theme_minimal,
                    UserAppState.change_theme_vibrant,
                ),
                rx.box(),  # Empty placeholder when hidden
            ),
            # User selector
            rx.vstack(
                rx.heading("Select User", size="5", color=theme.text_primary),
                user_selector(theme_config),
                spacing="2",
                align_items="flex-start",
                margin_bottom="8",
            ),
            # Loading state
            rx.cond(
                UserAppState.is_loading,
                rx.spinner(size="3"),
                # Content (when not loading) - conditional based on current_page
                rx.cond(
                    UserAppState.current_page == "dashboard",
                    dashboard_view(theme_config),
                    rx.cond(
                        UserAppState.current_page == "learning_feed",
                        learning_feed_view(theme_config),
                        rx.cond(
                            UserAppState.current_page == "privacy",
                            privacy_view(theme_config),
                            dashboard_view(theme_config),  # Default fallback
                        ),
                    ),
                ),
            ),
            padding="8",
            max_width="1200px",
        ),
        # Floating theme switcher button
        theme_switcher_button(UserAppState.toggle_theme_switcher),
        background=theme.background,
        min_height="100vh",
    )


def index() -> rx.Component:
    """Main app entry point with dynamic theming.

    Uses the computed theme_config property from state to ensure consistent
    theme resolution between server-side rendering and client-side hydration.
    This prevents hydration errors from nested conditionals.
    """
    return themed_dashboard(UserAppState.theme_config)


# Create app
app = rx.App()

# Add main page with data loading on mount
app.add_page(
    index,
    route="/",
    title="SpendSense - Your Financial Dashboard",
    on_load=UserAppState.on_load,
)

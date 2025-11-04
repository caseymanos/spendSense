"""SpendSense User Dashboard - Reflex Implementation"""

import reflex as rx
from .state.user_state import UserAppState
from .components.shared.metric_card import metric_card
from .components.shared.persona_badge import persona_badge
from .components.shared.status_badge import consent_badge
from .utils.formatters import format_currency, format_percentage
from .utils import theme


def navbar() -> rx.Component:
    """Top navigation bar."""
    return rx.box(
        rx.hstack(
            # Logo and title
            rx.heading("💰 SpendSense", size="7", color=theme.PRIMARY),

            rx.spacer(),

            # Navigation buttons
            rx.button(
                "Dashboard",
                on_click=UserAppState.navigate_to_dashboard,
                variant="ghost",
                color_scheme="blue",
            ),
            rx.button(
                "Learning Feed",
                on_click=UserAppState.navigate_to_learning_feed,
                variant="ghost",
                color_scheme="blue",
            ),
            rx.button(
                "Privacy",
                on_click=UserAppState.navigate_to_privacy,
                variant="ghost",
                color_scheme="blue",
            ),

            # User info
            rx.hstack(
                rx.text(UserAppState.user_name, font_weight="500", color=theme.GRAY_900),
                consent_badge(UserAppState.consent_granted, UserAppState.consent_status_text),
                spacing="3",
            ),

            spacing="4",
            width="100%",
        ),
        padding="4",
        background=theme.WHITE,
        border_bottom=f"1px solid {theme.GRAY_200}",
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
            font_size=theme.FONT_SIZE_SM,
            color=theme.GRAY_500,
            font_style="italic",
        ),
        spacing="1",
        align_items="flex-start",
        width="100%",
    )


def simple_dashboard() -> rx.Component:
    """Simplified dashboard page to get started."""
    return rx.box(
        navbar(),

        rx.container(
            # User selector
            rx.vstack(
                rx.heading("Select User", size="5", color=theme.GRAY_900),
                user_selector(),
                spacing="2",
                align_items="flex-start",
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
                                    rx.heading("Data Analysis Active", size="4", color=theme.SUCCESS, margin_bottom="1"),
                                    rx.text(
                                        UserAppState.consent_status_text,
                                        font_size=theme.FONT_SIZE_SM,
                                        color=theme.GRAY_600,
                                    ),
                                    spacing="0",
                                    align_items="flex-start",
                                ),
                                rx.spacer(),
                                rx.button(
                                    "Revoke Consent",
                                    on_click=UserAppState.show_revoke_confirmation,
                                    variant="outline",
                                    color_scheme="red",
                                    size="2",
                                ),
                                spacing="4",
                                width="100%",
                                align_items="center",
                            ),
                            padding="4",
                            background=theme.SUCCESS_LIGHT,
                            border=f"1px solid {theme.SUCCESS}",
                            border_radius="md",
                            margin_bottom="6",
                        ),

                        # Persona section
                        rx.box(
                            persona_badge(
                                UserAppState.persona_info,
                                show_description=True,
                                size="7",
                            ),
                            margin_bottom="6",
                        ),

                        # Metrics grid (simple example)
                        rx.heading("Your Financial Snapshot", size="7", margin_bottom="4", color=theme.GRAY_900),
                        rx.grid(
                            metric_card(
                                label="Credit Cards",
                                value=rx.cond(
                                    UserAppState.signals.get("credit_num_cards"),
                                    str(UserAppState.signals["credit_num_cards"]),
                                    "0",
                                ),
                                help_text="Active accounts",
                                color=theme.PERSONA_COLORS["high_utilization"],
                            ),
                            metric_card(
                                label="Subscriptions",
                                value=rx.cond(
                                    UserAppState.signals.get("sub_180d_recurring_count"),
                                    str(UserAppState.signals["sub_180d_recurring_count"]),
                                    "0",
                                ),
                                help_text="Recurring services",
                                color=theme.PERSONA_COLORS["subscription_heavy"],
                            ),
                            metric_card(
                                label="Savings (6mo)",
                                value=rx.cond(
                                    UserAppState.signals.get("sav_180d_net_inflow"),
                                    format_currency(UserAppState.signals["sav_180d_net_inflow"]),
                                    "$0.00",
                                ),
                                help_text="Net inflow",
                                color=theme.PERSONA_COLORS["savings_builder"],
                            ),
                            columns="3",
                            spacing="4",
                        ),

                        # Recommendations preview
                        rx.heading("Your Recommendations", size="7", margin_top="8", margin_bottom="4", color=theme.GRAY_900),
                        rx.cond(
                            UserAppState.has_recommendations,
                            rx.vstack(
                                rx.foreach(
                                    UserAppState.top_recommendations,
                                    lambda rec: rx.box(
                                        rx.heading(rec["title"], size="5", color=theme.GRAY_900),
                                        rx.text(rec["description"], color=theme.GRAY_700),
                                        rx.box(
                                            rx.text(rec["rationale"], font_style="italic", color=theme.GRAY_600),
                                            padding="3",
                                            background=theme.INFO_LIGHT,
                                            border_radius="md",
                                            margin_top="2",
                                        ),
                                        padding="5",
                                        background=theme.WHITE,
                                        border=f"1px solid {theme.GRAY_200}",
                                        border_radius="lg",
                                        margin_bottom="3",
                                    ),
                                ),
                                spacing="3",
                            ),
                            rx.text("No recommendations available", color=theme.GRAY_500),
                        ),

                        spacing="4",
                        width="100%",
                    ),

                    # Consent banner (no consent)
                    rx.box(
                        rx.heading("Consent Not Yet Granted", size="7", margin_bottom="3", color=theme.GRAY_900),
                        rx.text(
                            UserAppState.consent_status_text,
                            margin_bottom="4",
                            color=theme.GRAY_600,
                            font_style="italic",
                        ),
                        rx.text(
                            "To provide personalized financial insights and recommendations, we need your consent to analyze your transaction data.",
                            margin_bottom="4",
                            color=theme.GRAY_700,
                        ),
                        rx.button(
                            "Grant Consent",
                            on_click=UserAppState.grant_consent_confirmed,
                            color_scheme="blue",
                            size="3",
                        ),
                        padding="8",
                        background=theme.WARNING_LIGHT,
                        border=f"2px solid {theme.WARNING}",
                        border_radius="lg",
                    ),
                ),
            ),

            padding="8",
            max_width="1200px",
        ),
        background=theme.GRAY_50,
        min_height="100vh",
    )


def index() -> rx.Component:
    """Main app entry point."""
    return simple_dashboard()


# Create app
app = rx.App()

# Add main page with data loading on mount
app.add_page(
    index,
    route="/",
    title="SpendSense - Your Financial Dashboard",
    on_load=UserAppState.on_load,
)

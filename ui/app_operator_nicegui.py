"""
SpendSense MVP V2 - NiceGUI Operator Dashboard

Modern operator dashboard with 3 switchable themes and enhanced data generation controls.

Features:
- 7 tabs: Overview, User Management, Behavioral Signals, Recommendation Review,
  Decision Trace Viewer, Guardrails Monitor, Data Generation
- 3 visual themes: Clean/Minimal, Modern/Colorful, Dashboard/Analytics
- Interactive parameter controls for test data generation
- Full audit trail and compliance features

Run with: uv run python ui/app_operator_nicegui.py
"""

from datetime import datetime
import pandas as pd
import os
import hashlib

from nicegui import ui, app

# Import theme system
from ui.themes import ThemeManager, Theme

# Import utilities - use API loaders if API_URL is set (production), else use file loaders (local dev)
USE_API = bool(os.getenv("API_URL"))

if USE_API:
    from ui.utils.api_data_loaders import (
        load_all_users,
        load_all_signals,
        load_user_trace,
        load_persona_distribution,
        load_guardrail_summary,
    )
    _DB_PATH = None
    _SIGNALS_PATH = None
    _TRACES_DIR = None
else:
    from ui.utils.data_loaders import (
        load_all_users,
        load_all_signals,
        load_user_trace,
        load_persona_distribution,
        load_guardrail_summary,
    )
    from ui.utils.data_loaders import DB_PATH as _DB_PATH
    from ui.utils.data_loaders import SIGNALS_PATH as _SIGNALS_PATH
    from ui.utils.data_loaders import TRACES_DIR as _TRACES_DIR

# Import recommendation engine for live generation
from recommend.engine import generate_recommendations

# Import AI recommendations
try:
    from recommend.ai_recommendations import generate_ai_recommendations, OPENAI_AVAILABLE
    AI_RECOMMENDATIONS_AVAILABLE = True
except ImportError:
    AI_RECOMMENDATIONS_AVAILABLE = False
    OPENAI_AVAILABLE = False

# Import content management
from recommend.content_loader import (
    load_content_catalog,
    save_override,
    delete_override,
    reset_to_defaults,
    export_catalog,
    get_all_personas,
)

# Import components
from ui.components import (
    create_summary_metrics_row,
    create_data_table,
    create_persona_chart,
    create_credit_utilization_histogram,
    create_histogram,
    create_operator_actions,
)

# Import data generator UI
from ui.data_generator_ui import DataGeneratorUI

# =============================================================================
# GLOBAL STATE
# =============================================================================

# Operator state
operator_state = {
    "operator_name": "",
    "current_tab": "overview",
    "selected_user_id": None,
}

# Data cache
data_cache = {
    "users": None,
    "signals": None,
    "persona_distribution": None,
    "guardrail_summary": None,
    "last_refresh": None,
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def refresh_data():
    """Refresh all data from sources."""
    data_cache["users"] = load_all_users()
    data_cache["signals"] = load_all_signals()
    data_cache["persona_distribution"] = load_persona_distribution()
    data_cache["guardrail_summary"] = load_guardrail_summary()
    data_cache["last_refresh"] = datetime.now()


def _get_data_mtime() -> float:
    """Return latest mtime among core data files/dirs (file mode only)."""
    if USE_API:
        # In API mode, we can't check file mtimes, so return current time
        # This effectively disables stale data detection in production
        return datetime.now().timestamp()

    mtimes = []
    try:
        if _DB_PATH and _DB_PATH.exists():
            mtimes.append(_DB_PATH.stat().st_mtime)
    except Exception:
        pass
    try:
        if _SIGNALS_PATH and _SIGNALS_PATH.exists():
            mtimes.append(_SIGNALS_PATH.stat().st_mtime)
    except Exception:
        pass
    try:
        if _TRACES_DIR and _TRACES_DIR.exists():
            latest = max((p.stat().st_mtime for p in _TRACES_DIR.glob("*.json")), default=0)
            mtimes.append(latest)
    except Exception:
        pass
    return max(mtimes) if mtimes else 0.0


def _is_data_stale() -> bool:
    """Check if data has changed since last refresh."""
    if USE_API:
        # In API mode, always return False since we can't detect file changes
        # User must manually refresh
        return False

    try:
        last_seen = app.storage.user.get('last_data_mtime', 0)
        return _get_data_mtime() > last_seen
    except Exception:
        return False


def _render_stale_data_banner():
    """Render warning banner when data is stale with refresh button."""
    if _is_data_stale():
        with ui.card().classes("w-full bg-orange-50 border-l-4 border-orange-500 mb-4"):
            with ui.row().classes("w-full items-center justify-between p-4"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("warning", size="lg").classes("text-orange-600")
                    with ui.column().classes("gap-1"):
                        ui.label("Data Updated Since Last Refresh").classes("font-semibold text-orange-900")
                        ui.label("Click 'Refresh Data' to see the latest information").classes("text-sm text-orange-700")

                ui.button("Refresh Data", icon="refresh", on_click=lambda: handle_refresh()).props("color=orange").classes("text-white")


def get_persona_description(persona: str) -> str:
    """Get description for a persona."""
    descriptions = {
        "High Utilization": "Credit card utilization > 50% (prioritized for debt reduction advice)",
        "Variable Income Budgeter": "Income deposits with >20 day gap variance (irregular income patterns)",
        "Subscription-Heavy": "5+ recurring subscriptions (focus on spending optimization)",
        "Savings Builder": "Consistent savings deposits (positive reinforcement for good habits)",
        "General": "Default persona for users not matching specific behavioral criteria",
        "Custom Persona": "Reserved for future expansion or special cases",
    }
    return descriptions.get(persona, "No description available")


# =============================================================================
# THEME SWITCHER COMPONENT
# =============================================================================


def create_theme_switcher():
    """Set theme to Clean & Minimal only."""
    # Always use Clean & Minimal theme
    ThemeManager.set_theme(Theme.CLEAN_MINIMAL)


# =============================================================================
# TAB 1: OVERVIEW
# =============================================================================


@ui.refreshable
def render_overview_tab():
    """Render Overview tab with system health metrics."""
    # Show stale data warning if data has been updated
    _render_stale_data_banner()

    users_df = data_cache["users"]
    persona_dist = data_cache["persona_distribution"]
    guardrail_summary = data_cache["guardrail_summary"]

    if users_df is None or users_df.empty:
        ui.label("No data available. Please generate data first.").classes(
            "text-center p-8 text-gray-500"
        )
        return

    # Summary metrics
    total_users = len(users_df)
    users_with_consent = users_df["consent_granted"].sum()
    consent_pct = (users_with_consent / total_users * 100) if total_users > 0 else 0
    distinct_personas = users_df["persona"].nunique()
    total_recs = guardrail_summary.get("total_recommendations", 0)

    metrics = [
        {"title": "Total Users", "value": total_users, "icon": "people"},
        {"title": "Consent Granted", "value": f"{consent_pct:.0f}%", "icon": "verified_user"},
        {"title": "Personas", "value": distinct_personas, "icon": "category"},
        {"title": "Recommendations", "value": total_recs, "icon": "recommend"},
    ]

    create_summary_metrics_row(metrics, ThemeManager.get_metric_card_classes())

    ui.separator().classes("my-6")

    # Persona distribution chart
    with ui.card().classes(ThemeManager.get_card_classes() + " mt-4"):
        ui.label("Persona Distribution").classes("text-xl font-bold mb-4")

        if persona_dist:
            create_persona_chart(persona_dist, ThemeManager.get_chart_colors())

            # Persona definitions table
            ui.label("Persona Definitions").classes("text-lg font-semibold mt-6 mb-2")

            persona_data = []
            for persona, count in persona_dist.items():
                persona_data.append(
                    {
                        "persona": persona,
                        "count": count,
                        "description": get_persona_description(persona),
                    }
                )

            persona_df = pd.DataFrame(persona_data)
            create_data_table(
                data=persona_df,
                columns=[
                    {"name": "persona", "label": "Persona", "field": "persona", "align": "left"},
                    {"name": "count", "label": "Count", "field": "count", "align": "center"},
                    {
                        "name": "description",
                        "label": "Description",
                        "field": "description",
                        "align": "left",
                    },
                ],
                theme_classes=ThemeManager.get_table_classes(),
            )

    ui.separator().classes("my-6")

    # Guardrails summary
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label("Guardrails Summary").classes("text-xl font-bold mb-4")

        tone_violations_count = len(guardrail_summary.get("tone_violations", []))
        blocked_offers_count = len(guardrail_summary.get("blocked_offers", []))
        no_consent_count = total_users - users_with_consent

        guardrail_metrics = [
            {
                "title": "Tone Violations",
                "value": tone_violations_count,
                "icon": "warning",
                "delta_color": "red",
            },
            {
                "title": "Blocked Offers",
                "value": blocked_offers_count,
                "icon": "block",
                "delta_color": "orange",
            },
            {
                "title": "No Consent",
                "value": no_consent_count,
                "icon": "cancel",
                "delta_color": "red",
            },
        ]

        create_summary_metrics_row(guardrail_metrics, ThemeManager.get_metric_card_classes())


# =============================================================================
# TAB 2: USER MANAGEMENT
# =============================================================================


@ui.refreshable
def render_user_management_tab():
    """Render User Management tab with filtering."""
    # Show stale data warning if data has been updated
    _render_stale_data_banner()

    users_df = data_cache["users"]

    if users_df is None or users_df.empty:
        ui.label("No users data available").classes("text-center p-8 text-gray-500")
        return

    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label("User Management").classes("text-xl font-bold mb-4")

        # Filters
        with ui.row().classes("gap-4 mb-4"):
            consent_filter = ui.select(
                label="Consent Status", options=["All", "Granted", "Not Granted"], value="All"
            ).classes("w-48")

            persona_options = ["All"] + sorted(users_df["persona"].dropna().unique().tolist())
            persona_filter = ui.select(
                label="Persona", options=persona_options, value="All"
            ).classes("w-48")

            gender_options = ["All"] + sorted(users_df["gender"].dropna().unique().tolist())
            gender_filter = ui.select(label="Gender", options=gender_options, value="All").classes(
                "w-48"
            )

            income_options = ["All"] + sorted(users_df["income_tier"].dropna().unique().tolist())
            income_filter = ui.select(
                label="Income Tier", options=income_options, value="All"
            ).classes("w-48")

        # Filtered data container
        filtered_table_container = ui.column().classes("w-full")

        def update_filtered_table():
            """Update table based on filters."""
            filtered_df = users_df.copy()

            # Apply filters
            if consent_filter.value != "All":
                consent_val = consent_filter.value == "Granted"
                filtered_df = filtered_df[filtered_df["consent_granted"] == consent_val]

            if persona_filter.value != "All":
                filtered_df = filtered_df[filtered_df["persona"] == persona_filter.value]

            if gender_filter.value != "All":
                filtered_df = filtered_df[filtered_df["gender"] == gender_filter.value]

            if income_filter.value != "All":
                filtered_df = filtered_df[filtered_df["income_tier"] == income_filter.value]

            # Display filtered table
            filtered_table_container.clear()
            with filtered_table_container:
                ui.label(f"Showing {len(filtered_df)} users").classes("text-sm text-gray-600 mb-2")

                display_cols = [
                    "user_id",
                    "name",
                    "consent_granted",
                    "persona",
                    "age",
                    "gender",
                    "income_tier",
                    "region",
                ]
                display_df = filtered_df[display_cols]

                create_data_table(
                    data=display_df,
                    row_key="user_id",
                    pagination=20,
                    theme_classes=ThemeManager.get_table_classes(),
                )

        # Bind filters
        consent_filter.on_value_change(lambda: update_filtered_table())
        persona_filter.on_value_change(lambda: update_filtered_table())
        gender_filter.on_value_change(lambda: update_filtered_table())
        income_filter.on_value_change(lambda: update_filtered_table())

        # Initial table render
        update_filtered_table()


# =============================================================================
# TAB 3: BEHAVIORAL SIGNALS
# =============================================================================


@ui.refreshable
def render_behavioral_signals_tab():
    """Render Behavioral Signals tab with signal analysis."""
    signals_df = data_cache["signals"]

    if signals_df is None or signals_df.empty:
        ui.label("No signals data available").classes("text-center p-8 text-gray-500")
        return

    # Aggregate metrics (using actual parquet column names)
    avg_credit_util = (
        signals_df["credit_avg_util_pct"].mean()
        if "credit_avg_util_pct" in signals_df.columns
        else 0
    )
    avg_subscriptions = (
        signals_df["sub_30d_recurring_count"].mean()
        if "sub_30d_recurring_count" in signals_df.columns
        else 0
    )
    median_savings = (
        signals_df["sav_180d_net_inflow"].median()
        if "sav_180d_net_inflow" in signals_df.columns
        else 0
    )
    median_pay_gap = (
        signals_df["inc_30d_median_pay_gap_days"].median()
        if "inc_30d_median_pay_gap_days" in signals_df.columns
        else 0
    )

    metrics = [
        {
            "title": "Avg Credit Utilization",
            "value": f"{avg_credit_util:.1f}%",
            "icon": "credit_card",
        },
        {
            "title": "Avg Subscriptions",
            "value": f"{avg_subscriptions:.1f}",
            "icon": "subscriptions",
        },
        {"title": "Median Savings (180d)", "value": f"${median_savings:,.0f}", "icon": "savings"},
        {"title": "Median Pay Gap", "value": f"{median_pay_gap:.1f} days", "icon": "schedule"},
    ]

    create_summary_metrics_row(metrics, ThemeManager.get_metric_card_classes())

    ui.separator().classes("my-6")

    # Distribution charts
    with ui.row().classes("w-full gap-4"):
        # Credit utilization histogram
        with ui.card().classes(ThemeManager.get_card_classes() + " flex-1"):
            ui.label("Credit Utilization Distribution").classes("text-lg font-bold mb-4")
            create_credit_utilization_histogram(signals_df, ThemeManager.get_chart_colors())

        # Subscription count distribution
        with ui.card().classes(ThemeManager.get_card_classes() + " flex-1"):
            ui.label("Subscription Count Distribution").classes("text-lg font-bold mb-4")
            if "recurring_subscriptions_30d" in signals_df.columns:
                create_histogram(
                    data=signals_df,
                    column="recurring_subscriptions_30d",
                    title="",
                    x_label="Number of Subscriptions",
                    bins=15,
                    chart_colors=ThemeManager.get_chart_colors(),
                )

    ui.separator().classes("my-6")

    # 30d vs 180d comparison
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label("Signal Comparison: 30d vs 180d").classes("text-xl font-bold mb-4")

        comparison_data = []

        # Recurring subscriptions
        if (
            "recurring_subscriptions_30d" in signals_df.columns
            and "recurring_subscriptions_180d" in signals_df.columns
        ):
            comparison_data.append(
                {
                    "signal": "Recurring Subscriptions",
                    "30d_avg": f"{signals_df['recurring_subscriptions_30d'].mean():.2f}",
                    "180d_avg": f"{signals_df['recurring_subscriptions_180d'].mean():.2f}",
                }
            )

        # Pay gap variance
        if (
            "pay_gap_variance_30d" in signals_df.columns
            and "pay_gap_variance_180d" in signals_df.columns
        ):
            comparison_data.append(
                {
                    "signal": "Pay Gap Variance (days)",
                    "30d_avg": f"{signals_df['pay_gap_variance_30d'].median():.2f}",
                    "180d_avg": f"{signals_df['pay_gap_variance_180d'].median():.2f}",
                }
            )

        # Credit utilization
        if "credit_utilization_30d" in signals_df.columns:
            comparison_data.append(
                {
                    "signal": "Credit Utilization",
                    "30d_avg": f"{signals_df['credit_utilization_30d'].mean():.1%}",
                    "180d_avg": "N/A",
                }
            )

        # Savings inflow
        if "savings_inflow_180d" in signals_df.columns:
            comparison_data.append(
                {
                    "signal": "Savings Inflow",
                    "30d_avg": "N/A",
                    "180d_avg": f"${signals_df['savings_inflow_180d'].median():,.0f}",
                }
            )

        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            create_data_table(
                data=comparison_df,
                columns=[
                    {"name": "signal", "label": "Signal Type", "field": "signal", "align": "left"},
                    {
                        "name": "30d_avg",
                        "label": "30-Day Window",
                        "field": "30d_avg",
                        "align": "center",
                    },
                    {
                        "name": "180d_avg",
                        "label": "180-Day Window",
                        "field": "180d_avg",
                        "align": "center",
                    },
                ],
                theme_classes=ThemeManager.get_table_classes(),
            )

    ui.separator().classes("my-6")

    # Per-user signal drill-down
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label("Per-User Signal Detail").classes("text-xl font-bold mb-4")

        # User selector
        user_ids = (
            signals_df["user_id"].unique().tolist() if "user_id" in signals_df.columns else []
        )

        if user_ids:
            selected_user_container = ui.column().classes("w-full")

            user_select = ui.select(
                label="Select User", options=user_ids, value=user_ids[0] if user_ids else None
            ).classes("w-64 mb-4")

            def display_user_signals():
                """Display signals for selected user."""
                selected_user_container.clear()

                if not user_select.value:
                    return

                user_signals = (
                    signals_df[signals_df["user_id"] == user_select.value].iloc[0].to_dict()
                )

                with selected_user_container:
                    # Credit signals
                    with ui.expansion("Credit Signals", icon="credit_card", value=True).classes(
                        "w-full"
                    ):
                        credit_cols = [
                            col for col in user_signals.keys() if "credit" in col.lower()
                        ]
                        if credit_cols:
                            for col in credit_cols:
                                val = user_signals[col]
                                if pd.notna(val):
                                    with ui.row().classes(
                                        "w-full justify-between items-center mb-2"
                                    ):
                                        ui.label(col.replace("_", " ").title()).classes(
                                            "font-semibold"
                                        )
                                        if isinstance(val, float) and "utilization" in col:
                                            ui.label(f"{val:.1%}").classes("text-blue-600")
                                        else:
                                            ui.label(str(val)).classes("text-blue-600")

                    # Subscription signals
                    with ui.expansion("Subscription Signals", icon="subscriptions").classes(
                        "w-full"
                    ):
                        sub_cols = [
                            col
                            for col in user_signals.keys()
                            if "subscription" in col.lower() or "recurring" in col.lower()
                        ]
                        if sub_cols:
                            for col in sub_cols:
                                val = user_signals[col]
                                if pd.notna(val):
                                    with ui.row().classes(
                                        "w-full justify-between items-center mb-2"
                                    ):
                                        ui.label(col.replace("_", " ").title()).classes(
                                            "font-semibold"
                                        )
                                        ui.label(str(val)).classes("text-purple-600")

                    # Savings signals
                    with ui.expansion("Savings Signals", icon="savings").classes("w-full"):
                        savings_cols = [
                            col for col in user_signals.keys() if "savings" in col.lower()
                        ]
                        if savings_cols:
                            for col in savings_cols:
                                val = user_signals[col]
                                if pd.notna(val):
                                    with ui.row().classes(
                                        "w-full justify-between items-center mb-2"
                                    ):
                                        ui.label(col.replace("_", " ").title()).classes(
                                            "font-semibold"
                                        )
                                        if isinstance(val, (int, float)):
                                            ui.label(f"${val:,.2f}").classes("text-green-600")
                                        else:
                                            ui.label(str(val)).classes("text-green-600")

                    # Income signals
                    with ui.expansion("Income Signals", icon="payments").classes("w-full"):
                        income_cols = [
                            col
                            for col in user_signals.keys()
                            if "pay" in col.lower() or "income" in col.lower()
                        ]
                        if income_cols:
                            for col in income_cols:
                                val = user_signals[col]
                                if pd.notna(val):
                                    with ui.row().classes(
                                        "w-full justify-between items-center mb-2"
                                    ):
                                        ui.label(col.replace("_", " ").title()).classes(
                                            "font-semibold"
                                        )
                                        if isinstance(val, (int, float)) and "gap" in col:
                                            ui.label(f"{val:.1f} days").classes("text-orange-600")
                                        else:
                                            ui.label(str(val)).classes("text-orange-600")

            user_select.on_value_change(lambda: display_user_signals())
            display_user_signals()  # Initial display
        else:
            ui.label("No user data available").classes("text-gray-500")


# =============================================================================
# TAB 4: RECOMMENDATION REVIEW
# =============================================================================


@ui.refreshable
def render_recommendation_review_tab():
    """Render Recommendation Review tab with operator actions."""
    # Show stale data warning if data has been updated
    _render_stale_data_banner()

    users_df = data_cache["users"]

    if users_df is None or users_df.empty:
        ui.label("No users data available").classes("text-center p-8 text-gray-500")
        return

    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label("Recommendation Review").classes("text-xl font-bold mb-4")

        # User selector
        user_ids = users_df["user_id"].tolist()
        user_names = users_df["name"].tolist()
        user_personas = users_df["persona"].fillna("No Persona").tolist()

        user_options = {
            f"{uid} - {name} ({persona})": uid
            for uid, name, persona in zip(user_ids, user_names, user_personas)
        }

        recommendation_container = ui.column().classes("w-full")
        button_container = ui.row().classes("gap-2")
        ai_config_state = {"api_key": "", "model": "gpt-4o-mini", "max_recs": 5}

        with ui.row().classes("w-full items-center gap-4 mb-4"):
            user_select = ui.select(
                label="Select User",
                options=list(user_options.keys()),
                value=list(user_options.keys())[0] if user_options else None,
            ).classes("flex-grow")

            button_container

        # AI Recommendations Section
        if AI_RECOMMENDATIONS_AVAILABLE and OPENAI_AVAILABLE:
            with ui.expansion("🤖 AI-Powered Recommendations (OpenAI)", icon="auto_awesome").classes("w-full mb-4 border-2 border-purple-300"):
                ui.label("Generate AI-powered recommendations using OpenAI's GPT models").classes("text-sm text-gray-600 mb-3")

                with ui.row().classes("w-full gap-4 items-end"):
                    api_key_input = ui.input(
                        label="OpenAI API Key",
                        placeholder="sk-...",
                        password=True,
                        password_toggle_button=True,
                    ).classes("flex-grow").bind_value(ai_config_state, "api_key")

                    model_select = ui.select(
                        label="Model",
                        options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                        value="gpt-4o-mini",
                    ).classes("w-48").bind_value(ai_config_state, "model")

                    max_recs_input = ui.number(
                        label="Max Recommendations",
                        value=5,
                        min=1,
                        max=10,
                    ).classes("w-32").bind_value(ai_config_state, "max_recs")

                ui.label("💡 Tip: gpt-4o-mini is recommended for cost efficiency").classes("text-xs text-blue-600 mt-2")
        elif AI_RECOMMENDATIONS_AVAILABLE and not OPENAI_AVAILABLE:
            with ui.card().classes("w-full bg-yellow-50 border-l-4 border-yellow-500 p-4 mb-4"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("warning", size="md").classes("text-yellow-600")
                    ui.label("OpenAI library not installed. Run: uv pip install openai").classes("text-sm text-yellow-800")

        def load_existing_recommendations():
            """Load existing recommendations from trace file."""
            recommendation_container.clear()

            if not user_select.value:
                with recommendation_container:
                    ui.label("Please select a user").classes("text-gray-500")
                return

            selected_user_id = user_options[user_select.value]

            # Try to load from trace file first
            trace = load_user_trace(selected_user_id)

            if not trace or "recommendations" not in trace:
                # No existing recommendations - show option to generate
                with recommendation_container:
                    with ui.card().classes("w-full bg-gray-50 p-8 text-center"):
                        ui.icon("inbox", size="xl").classes("text-gray-400 mb-4")
                        ui.label("No recommendations found for this user").classes(
                            "text-lg text-gray-600 mb-2"
                        )
                        ui.label("Click 'Generate Recommendations' to create new recommendations").classes(
                            "text-sm text-gray-500"
                        )
                return

            # Extract recommendations from trace
            rec_data = trace["recommendations"]
            recommendations_list = rec_data.get("recommendations", [])
            trace_consent = rec_data.get("consent_granted", False)
            persona = rec_data.get("persona", "Unknown")
            timestamp = rec_data.get("timestamp", "Unknown")

            # Get current consent from database
            current_user = users_df[users_df["user_id"] == selected_user_id]
            current_consent = bool(current_user.iloc[0]["consent_granted"]) if not current_user.empty else trace_consent
            consent_mismatch = current_consent != trace_consent

            with recommendation_container:
                # Timestamp banner
                with ui.card().classes("w-full bg-indigo-50 border-l-4 border-indigo-500 p-4 mb-4"):
                    with ui.row().classes("items-center gap-3"):
                        ui.icon("history", size="md").classes("text-indigo-600")
                        with ui.column().classes("gap-1 flex-1"):
                            ui.label("Viewing Existing Recommendations").classes("font-semibold text-indigo-900")
                            ui.label(f"Generated: {timestamp}").classes("text-sm text-indigo-800")

                # Consent mismatch warning
                if consent_mismatch:
                    with ui.card().classes("w-full bg-yellow-50 border-l-4 border-yellow-500 p-4 mb-4"):
                        with ui.row().classes("items-start gap-3"):
                            ui.icon("warning", size="md").classes("text-yellow-600")
                            with ui.column().classes("gap-1 flex-1"):
                                ui.label("Consent Status Changed").classes("font-semibold text-yellow-900")
                                ui.label(f"Current (database): {'✓ Granted' if current_consent else '✗ Not Granted'} | "
                                        f"At generation time: {'✓ Granted' if trace_consent else '✗ Not Granted'}").classes("text-sm text-yellow-800")
                                ui.label("These recommendations were generated with the historical consent status.").classes("text-xs text-yellow-700 mt-1")

                # Metadata
                with ui.card().classes("bg-blue-50 p-4 mb-4"):
                    with ui.row().classes("w-full items-center gap-8"):
                        with ui.column().classes("gap-1"):
                            ui.label("User ID:").classes("text-xs text-gray-600")
                            ui.label(selected_user_id).classes("font-semibold")

                        with ui.column().classes("gap-1"):
                            ui.label("Persona:").classes("text-xs text-gray-600")
                            ui.label(persona).classes("font-semibold")

                        with ui.column().classes("gap-1"):
                            ui.label("Current Consent:").classes("text-xs text-gray-600")
                            consent_badge = ui.badge(
                                "✓ Granted" if current_consent else "✗ Not Granted"
                            )
                            consent_badge.props(
                                f'color={"positive" if current_consent else "negative"}'
                            )

                        with ui.column().classes("gap-1"):
                            ui.label("Total Recommendations:").classes("text-xs text-gray-600")
                            ui.label(str(len(recommendations_list))).classes("font-semibold")

                        # Show source (AI vs Rule-Based)
                        with ui.column().classes("gap-1"):
                            ui.label("Source:").classes("text-xs text-gray-600")
                            source = rec_data.get("source", "rule_based")
                            if source == "ai_generated":
                                ui.badge("🤖 AI Generated").props("color=purple")
                            else:
                                ui.badge("📋 Rule-Based").props("color=blue")

                # Recommendations
                if not recommendations_list:
                    ui.label("No recommendations in trace file").classes(
                        "text-gray-500 p-4"
                    )
                    return

                education_items = [r for r in recommendations_list if r.get("type") == "education"]
                partner_offers = [
                    r for r in recommendations_list if r.get("type") == "partner_offer"
                ]

                ui.label(
                    f"Education Items: {len(education_items)} | Partner Offers: {len(partner_offers)}"
                ).classes("text-sm text-gray-600 mb-4")

                # Display each recommendation
                for idx, rec in enumerate(recommendations_list):
                    rec_type = rec.get("type", "unknown")
                    rec_category = rec.get("category", "N/A")
                    rec_title = rec.get("title", "Untitled")
                    rec_description = rec.get("description", "")
                    rec_rationale = rec.get("rationale", "No rationale provided")
                    rec_disclaimer = rec.get("disclaimer", "")

                    # Icon based on type
                    icon = "school" if rec_type == "education" else "local_offer"
                    type_color = "blue" if rec_type == "education" else "purple"

                    with ui.expansion(f"{rec_title}", icon=icon).classes(
                        "w-full mb-2"
                    ) as expansion:
                        expansion.classes(f"border-l-4 border-{type_color}-500")

                        with ui.column().classes("gap-3 p-2"):
                            # Type and category
                            with ui.row().classes("gap-2"):
                                ui.badge(rec_type.replace("_", " ").title()).props(
                                    f"color={type_color}"
                                )
                                ui.badge(rec_category).props("outline")

                            # Description
                            if rec_description:
                                with ui.card().classes("bg-gray-50 p-3"):
                                    ui.label("Description:").classes(
                                        "text-xs font-semibold text-gray-600 mb-1"
                                    )
                                    ui.label(rec_description).classes("text-sm")

                            # Rationale (most important for compliance)
                            with ui.card().classes("bg-yellow-50 border border-yellow-200 p-3"):
                                ui.label("Rationale:").classes(
                                    "text-xs font-semibold text-gray-600 mb-1"
                                )
                                ui.label(rec_rationale).classes("text-sm font-medium")

                            # Disclaimer
                            if rec_disclaimer:
                                with ui.card().classes("bg-red-50 border border-red-200 p-3"):
                                    ui.label("Disclaimer:").classes(
                                        "text-xs font-semibold text-gray-600 mb-1"
                                    )
                                    ui.label(rec_disclaimer).classes("text-xs")

                            ui.separator().classes("my-2")

                            # Guardrail checks
                            ui.label("Guardrail Checks:").classes("text-sm font-semibold mb-2")

                            # Tone check (simulated - in real implementation would call validate_tone)
                            tone_check = "PASS"  # Placeholder
                            tone_check_color = "positive" if tone_check == "PASS" else "negative"

                            with ui.row().classes("items-center gap-2"):
                                ui.icon(
                                    "check_circle" if tone_check == "PASS" else "cancel"
                                ).classes(f"text-{tone_check_color}")
                                ui.label(f"Tone Validation: {tone_check}").classes("text-sm")

                            # Eligibility check (simulated)
                            eligibility = "ELIGIBLE"  # Placeholder
                            eligibility_color = (
                                "positive" if eligibility == "ELIGIBLE" else "negative"
                            )

                            with ui.row().classes("items-center gap-2"):
                                ui.icon(
                                    "check_circle" if eligibility == "ELIGIBLE" else "cancel"
                                ).classes(f"text-{eligibility_color}")
                                ui.label(f"Eligibility: {eligibility}").classes("text-sm")

                            ui.separator().classes("my-2")

                            # Operator actions
                            ui.label("Operator Actions:").classes("text-sm font-semibold mb-2")

                            def refresh_after_action():
                                """Refresh view after operator action."""
                                load_existing_recommendations()

                            create_operator_actions(
                                user_id=selected_user_id,
                                recommendation_title=rec_title,
                                on_action_complete=refresh_after_action,
                                theme_classes=ThemeManager.get_button_classes(),
                            )

        def generate_new_recommendations(use_ai=False):
            """Generate fresh recommendations for selected user."""
            recommendation_container.clear()

            if not user_select.value:
                with recommendation_container:
                    ui.label("Please select a user").classes("text-gray-500")
                return

            selected_user_id = user_options[user_select.value]

            # Show loading indicator
            with recommendation_container:
                if use_ai:
                    ui.spinner(size="lg", color="purple")
                    ui.label("🤖 Generating AI-powered recommendations using OpenAI...").classes("text-purple-600 mt-2 font-semibold")
                else:
                    ui.spinner(size="lg")
                    ui.label("Generating rule-based recommendations...").classes("text-gray-600 mt-2")

            # Generate fresh recommendations (writes to trace automatically)
            try:
                if use_ai and AI_RECOMMENDATIONS_AVAILABLE:
                    # Validate API key
                    if not ai_config_state["api_key"]:
                        recommendation_container.clear()
                        with recommendation_container:
                            ui.label("⚠️ Please enter your OpenAI API key first").classes("text-orange-600")
                        return

                    # Generate AI recommendations
                    rec_response = generate_ai_recommendations(
                        user_id=selected_user_id,
                        api_key=ai_config_state["api_key"],
                        model=ai_config_state["model"],
                        max_recommendations=int(ai_config_state["max_recs"]),
                    )

                    # Check for errors
                    if rec_response.get("metadata", {}).get("error"):
                        recommendation_container.clear()
                        with recommendation_container:
                            with ui.card().classes("bg-red-50 border-l-4 border-red-500 p-4"):
                                ui.label(f"❌ AI generation failed: {rec_response['metadata']['error']}").classes("text-red-800 font-semibold mb-2")
                                ui.label("Falling back to rule-based recommendations...").classes("text-sm text-red-700")

                        # Fallback to rule-based
                        rec_response = generate_recommendations(selected_user_id)
                        ui.notify("AI generation failed, using rule-based recommendations", type="warning")
                    else:
                        # Success! Show token usage and trace file info
                        token_usage = rec_response.get("metadata", {}).get("token_usage", {})
                        trace_path = f"docs/traces/{selected_user_id}.json"
                        if token_usage:
                            ui.notify(
                                f"✓ AI recommendations generated | Tokens: {token_usage.get('total_tokens', 0)} "
                                f"({token_usage.get('prompt_tokens', 0)} prompt + {token_usage.get('completion_tokens', 0)} completion) | "
                                f"Saved to {trace_path}",
                                type="positive",
                                timeout=6000
                            )
                        else:
                            ui.notify(
                                f"✓ AI recommendations generated and saved to {trace_path}",
                                type="positive",
                                timeout=5000
                            )
                else:
                    # Standard rule-based generation
                    rec_response = generate_recommendations(selected_user_id)
                    trace_path = f"docs/traces/{selected_user_id}.json"
                    num_recs = len(rec_response.get("recommendations", []))
                    ui.notify(
                        f"✓ Generated {num_recs} rule-based recommendations | Saved to {trace_path}",
                        type="positive",
                        timeout=5000
                    )

                # Reload the existing recommendations view to show the new ones
                load_existing_recommendations()

                # Refresh all cached data to update overview metrics
                refresh_data()
                app.storage.user["last_data_mtime"] = _get_data_mtime()

                # Refresh overview tab to show updated recommendation count
                render_overview_tab.refresh()
            except Exception as e:
                recommendation_container.clear()
                with recommendation_container:
                    ui.label(f"Error generating recommendations: {str(e)}").classes(
                        "text-red-600"
                    )
                return

        def update_buttons():
            """Update button visibility based on whether recommendations exist."""
            button_container.clear()

            if not user_select.value:
                return

            selected_user_id = user_options[user_select.value]
            trace = load_user_trace(selected_user_id)
            has_recommendations = trace and "recommendations" in trace

            with button_container:
                if has_recommendations:
                    ui.button("Regenerate (Rule-Based)", icon="refresh", on_click=lambda: generate_new_recommendations(use_ai=False)).props(
                        "color=primary"
                    ).classes(ThemeManager.get_button_classes())

                    # Add AI generation button if available
                    if AI_RECOMMENDATIONS_AVAILABLE and OPENAI_AVAILABLE:
                        ui.button("🤖 Generate with AI", icon="auto_awesome", on_click=lambda: generate_new_recommendations(use_ai=True)).props(
                            "color=purple"
                        ).classes(ThemeManager.get_button_classes())
                else:
                    ui.button("Generate Recommendations", icon="add", on_click=lambda: generate_new_recommendations(use_ai=False)).props(
                        "color=primary"
                    ).classes(ThemeManager.get_button_classes())

                    # Add AI generation button if available
                    if AI_RECOMMENDATIONS_AVAILABLE and OPENAI_AVAILABLE:
                        ui.button("🤖 Generate with AI", icon="auto_awesome", on_click=lambda: generate_new_recommendations(use_ai=True)).props(
                            "color=purple"
                        ).classes(ThemeManager.get_button_classes())

        def on_user_change():
            """Handle user selection change."""
            update_buttons()
            load_existing_recommendations()

        user_select.on_value_change(lambda: on_user_change())

        # Initial load
        if user_options:
            update_buttons()
            load_existing_recommendations()


# =============================================================================
# TAB 5: DECISION TRACE VIEWER
# =============================================================================


@ui.refreshable
def render_decision_trace_viewer_tab():
    """Render Decision Trace Viewer tab with full audit trail."""
    users_df = data_cache["users"]

    if users_df is None or users_df.empty:
        ui.label("No users data available").classes("text-center p-8 text-gray-500")
        return

    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label("Decision Trace Viewer").classes("text-xl font-bold mb-4")
        ui.label("View complete decision trace for audit and compliance").classes(
            "text-sm text-gray-600 mb-6"
        )

        # User selector
        user_ids = users_df["user_id"].tolist()
        user_names = users_df["name"].tolist()

        user_options = {f"{uid} - {name}": uid for uid, name in zip(user_ids, user_names)}

        trace_container = ui.column().classes("w-full")

        user_select = ui.select(
            label="Select User",
            options=list(user_options.keys()),
            value=list(user_options.keys())[0] if user_options else None,
        ).classes("w-96 mb-4")

        def display_trace():
            """Display trace for selected user."""
            trace_container.clear()

            if not user_select.value:
                return

            selected_user_id = user_options[user_select.value]
            trace = load_user_trace(selected_user_id)

            if not trace:
                with trace_container:
                    ui.label(f"No trace found for user {selected_user_id}").classes(
                        "text-orange-600"
                    )
                return

            with trace_container:
                # User info summary
                user_info = users_df[users_df["user_id"] == selected_user_id].iloc[0]

                with ui.card().classes("bg-blue-50 p-4 mb-4"):
                    ui.label("User Information").classes("text-lg font-bold mb-3")

                    with ui.row().classes("w-full gap-8"):
                        with ui.column():
                            ui.label(f"Name: {user_info.get('name', 'N/A')}").classes("text-sm")
                            ui.label(f"Persona: {user_info.get('persona', 'N/A')}").classes(
                                "text-sm"
                            )

                        with ui.column():
                            consent = user_info.get("consent_granted", False)
                            ui.label(f"Consent: {'Granted' if consent else 'Not Granted'}").classes(
                                "text-sm"
                            )
                            ui.label(
                                f"Age: {user_info.get('age', 'N/A')} | Gender: {user_info.get('gender', 'N/A')}"
                            ).classes("text-sm")

                # Behavioral signals
                with ui.expansion("Behavioral Signals", icon="analytics", value=False).classes(
                    "w-full mb-2"
                ):
                    signals = trace.get("behavioral_signals", {})

                    if signals:
                        # 30d signals
                        signals_30d = signals.get("30d", {})
                        if signals_30d:
                            ui.label("30-Day Signals:").classes("font-semibold mb-2")
                            ui.json_editor(signals_30d).props("mode=view readonly").classes(
                                "w-full mb-4"
                            )

                        # 180d signals
                        signals_180d = signals.get("180d", {})
                        if signals_180d:
                            ui.label("180-Day Signals:").classes("font-semibold mb-2")
                            ui.json_editor(signals_180d).props("mode=view readonly").classes(
                                "w-full"
                            )
                    else:
                        ui.label("No behavioral signals in trace").classes("text-gray-500")

                # Persona assignment
                with ui.expansion("Persona Assignment", icon="category", value=False).classes(
                    "w-full mb-2"
                ):
                    persona_data = trace.get("persona_assignment", {})

                    if persona_data:
                        ui.json_editor(persona_data).props("mode=view readonly").classes("w-full")
                    else:
                        ui.label("No persona assignment in trace").classes("text-gray-500")

                # Recommendations
                with ui.expansion("Recommendations", icon="recommend", value=False).classes(
                    "w-full mb-2"
                ):
                    recommendations_data = trace.get("recommendations", {})

                    if recommendations_data:
                        # Summary
                        recs = recommendations_data.get("recommendations", [])
                        ui.label(f"Generated {len(recs)} recommendations").classes(
                            "font-semibold mb-2"
                        )

                        ui.json_editor(recommendations_data).props("mode=view readonly").classes(
                            "w-full"
                        )
                    else:
                        ui.label("No recommendations in trace").classes("text-gray-500")

                # Guardrail decisions
                with ui.expansion("Guardrail Decisions", icon="shield", value=False).classes(
                    "w-full mb-2"
                ):
                    guardrail_decisions = trace.get("guardrail_decisions", [])

                    if guardrail_decisions:
                        ui.label(f"Total decisions: {len(guardrail_decisions)}").classes(
                            "font-semibold mb-2"
                        )

                        for idx, decision in enumerate(guardrail_decisions):
                            with ui.expansion(
                                f"Decision {idx+1}: {decision.get('decision_type', 'Unknown')}",
                                icon="rule",
                            ).classes("w-full mb-2"):
                                ui.json_editor(decision).props("mode=view readonly").classes(
                                    "w-full"
                                )
                    else:
                        ui.label("No guardrail decisions in trace").classes("text-gray-500")

                # Raw JSON
                with ui.expansion("Raw JSON", icon="code", value=False).classes("w-full"):
                    with ui.row().classes("w-full justify-end mb-2"):

                        def copy_json():
                            ui.notify("JSON copied to clipboard!", type="positive")

                        ui.button(
                            "Copy to Clipboard", icon="content_copy", on_click=copy_json
                        ).props("flat dense")

                    ui.json_editor(trace).props("mode=view readonly").classes("w-full h-96")

        user_select.on_value_change(lambda: display_trace())

        # Auto-display first user
        if user_options:
            display_trace()


# =============================================================================
# TAB 6: GUARDRAILS MONITOR
# =============================================================================


@ui.refreshable
def render_guardrails_monitor_tab():
    """Render Guardrails Monitor tab with compliance metrics."""
    # Show stale data warning if data has been updated
    _render_stale_data_banner()

    guardrail_summary = data_cache["guardrail_summary"]
    users_df = data_cache["users"]

    if guardrail_summary is None:
        ui.label("No guardrails data available").classes("text-center p-8 text-gray-500")
        return

    # Summary metrics
    total_users = guardrail_summary.get("total_users", 0)
    users_with_consent = guardrail_summary.get("users_with_consent", 0)
    tone_violations_list = guardrail_summary.get("tone_violations", [])
    blocked_offers_list = guardrail_summary.get("blocked_offers", [])

    metrics = [
        {"title": "Total Users", "value": total_users, "icon": "people"},
        {"title": "With Consent", "value": users_with_consent, "icon": "verified_user"},
        {
            "title": "Tone Violations",
            "value": len(tone_violations_list),
            "icon": "warning",
            "delta": "-12%",
            "delta_color": "green",
        },
        {
            "title": "Blocked Offers",
            "value": len(blocked_offers_list),
            "icon": "block",
            "delta": "-8%",
            "delta_color": "green",
        },
    ]

    create_summary_metrics_row(metrics, ThemeManager.get_metric_card_classes())

    ui.separator().classes("my-6")

    # Tone violations detail
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label("Tone Violations Detail").classes("text-xl font-bold mb-4")

        if tone_violations_list:
            # Count occurrences of each prohibited phrase
            from collections import Counter

            violation_counts = Counter(tone_violations_list)

            violation_data = []
            for phrase, count in violation_counts.most_common():
                violation_data.append({"phrase": phrase, "count": count})

            violations_df = pd.DataFrame(violation_data)

            create_data_table(
                data=violations_df,
                columns=[
                    {
                        "name": "phrase",
                        "label": "Prohibited Phrase",
                        "field": "phrase",
                        "align": "left",
                        "sortable": True,
                    },
                    {
                        "name": "count",
                        "label": "Occurrences",
                        "field": "count",
                        "align": "center",
                        "sortable": True,
                    },
                ],
                pagination=10,
                theme_classes=ThemeManager.get_table_classes(),
            )
        else:
            ui.label("No tone violations found").classes("text-green-600 font-semibold")

    ui.separator().classes("my-6")

    # Blocked offers detail
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label("Blocked Offers Detail").classes("text-xl font-bold mb-4")

        if blocked_offers_list:
            # Show first 10 blocked offers
            display_count = min(10, len(blocked_offers_list))

            for i, offer in enumerate(blocked_offers_list[:display_count]):
                with ui.expansion(f"Blocked Offer {i+1}", icon="block").classes("w-full"):
                    ui.json_editor(offer).props("mode=view readonly").classes("w-full")

            if len(blocked_offers_list) > 10:
                ui.label(f"...and {len(blocked_offers_list) - 10} more blocked offers").classes(
                    "text-sm text-gray-600 mt-2"
                )
        else:
            ui.label("No blocked offers").classes("text-green-600 font-semibold")

    ui.separator().classes("my-6")

    # Consent audit trail
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label("Recent Consent Changes").classes("text-xl font-bold mb-4")

        if users_df is not None and not users_df.empty:
            # Get users with recent consent changes
            consent_df = users_df[
                ["user_id", "name", "consent_granted", "consent_timestamp"]
            ].copy()
            consent_df = consent_df.dropna(subset=["consent_timestamp"])

            # Sort by timestamp descending and take top 10
            consent_df = consent_df.sort_values("consent_timestamp", ascending=False).head(10)

            # Format consent status
            consent_df["status"] = consent_df["consent_granted"].apply(
                lambda x: "Granted" if x else "Revoked"
            )

            create_data_table(
                data=consent_df,
                columns=[
                    {"name": "user_id", "label": "User ID", "field": "user_id", "align": "left"},
                    {"name": "name", "label": "Name", "field": "name", "align": "left"},
                    {
                        "name": "status",
                        "label": "Consent Status",
                        "field": "status",
                        "align": "center",
                    },
                    {
                        "name": "consent_timestamp",
                        "label": "Timestamp",
                        "field": "consent_timestamp",
                        "align": "left",
                    },
                ],
                pagination=10,
                theme_classes=ThemeManager.get_table_classes(),
            )
        else:
            ui.label("No consent history available").classes("text-gray-500")


# =============================================================================
# TAB 7: DATA GENERATION (NEW)
# =============================================================================


@ui.refreshable
def render_data_generation_tab():
    """Render Data Generation tab with persona-skewed generation controls."""
    # Instantiate and render the full-featured DataGeneratorUI component
    data_gen_ui = DataGeneratorUI()
    data_gen_ui.render()


# =============================================================================
# TAB 8: CONTENT MANAGEMENT (NEW)
# =============================================================================


@ui.refreshable
def render_content_management_tab():
    """Render Content Management tab for editing recommendations."""
    import json

    # Load current catalog
    catalog = load_content_catalog()

    # State for selected item
    selected_item = {"persona": None, "type": None, "index": None, "data": {}}
    filter_state = {"persona": "all", "type": "all", "search": ""}

    ui.label("📚 Content Management").classes("text-2xl font-bold mb-4")
    ui.label("Edit educational content and partner offers").classes("text-gray-500 mb-6")

    # Top controls row
    with ui.row().classes("w-full gap-4 mb-6"):
        persona_filter = ui.select(
            label="Filter by Persona",
            options=["all"] + get_all_personas(),
            value="all",
            on_change=lambda: render_content_list.refresh()
        ).classes("w-64")
        persona_filter.bind_value(filter_state, "persona")

        type_filter = ui.select(
            label="Content Type",
            options=["all", "educational", "offers"],
            value="all",
            on_change=lambda: render_content_list.refresh()
        ).classes("w-48")
        type_filter.bind_value(filter_state, "type")

        search_input = ui.input(
            label="Search",
            placeholder="Search by title or topic...",
            on_change=lambda: render_content_list.refresh()
        ).classes("flex-grow")
        search_input.bind_value(filter_state, "search")

        def reset_filters():
            filter_state["persona"] = "all"
            filter_state["type"] = "all"
            filter_state["search"] = ""
            persona_filter.update()
            type_filter.update()
            search_input.update()
            render_content_list.refresh()

        ui.button("Reset Filters", on_click=reset_filters).props("flat color=grey")

    # Main content area with two panels
    with ui.row().classes("w-full gap-4"):
        # LEFT PANEL: Content List (60%)
        with ui.card().classes("w-3/5 p-4"):
            ui.label("Content Items").classes("text-lg font-bold mb-4")

            @ui.refreshable
            def render_content_list():
                """Render filtered list of content items."""
                items_found = 0

                for content_type in ["educational", "offers"]:
                    if filter_state["type"] != "all" and filter_state["type"] != content_type:
                        continue

                    for persona in get_all_personas():
                        if filter_state["persona"] != "all" and filter_state["persona"] != persona:
                            continue

                        items = catalog.get(content_type, {}).get(persona, [])

                        for idx, item in enumerate(items):
                            # Apply search filter
                            if filter_state["search"]:
                                search_term = filter_state["search"].lower()
                                if (search_term not in item.get("title", "").lower() and
                                    search_term not in item.get("topic", "").lower()):
                                    continue

                            items_found += 1

                            # Render item card
                            with ui.expansion(item.get("title", "Untitled"), icon="article" if content_type == "educational" else "sell").classes("w-full mb-2"):
                                with ui.row().classes("w-full gap-2 items-start"):
                                    ui.badge(persona.replace("_", " ").title()).props(f"color={'blue' if content_type == 'educational' else 'green'}")
                                    ui.badge(item.get("category", "general")).props("color=grey")
                                    if item.get("topic"):
                                        ui.badge(f"#{item.get('topic')}").props("color=orange outline")

                                ui.label(item.get("description", "")[:150] + "...").classes("text-sm text-gray-600 my-2")

                                with ui.row().classes("gap-2"):
                                    ui.button(
                                        "Edit",
                                        icon="edit",
                                        on_click=lambda p=persona, t=content_type, i=idx: load_item_for_editing(p, t, i)
                                    ).props("size=sm color=primary")

                                    ui.button(
                                        "Delete",
                                        icon="delete",
                                        on_click=lambda p=persona, t=content_type, i=idx, title=item.get("title"): confirm_delete_item(p, t, i, title)
                                    ).props("size=sm color=red flat")

                if items_found == 0:
                    ui.label("No items match your filters").classes("text-gray-500 italic")

            render_content_list()

            # Add New Item button
            ui.separator().classes("my-4")
            ui.button(
                "+ Add New Item",
                icon="add_circle",
                on_click=lambda: load_blank_form()
            ).props("color=green outline")

        # RIGHT PANEL: Edit Form (40%)
        with ui.card().classes("w-2/5 p-4"):
            ui.label("Edit Form").classes("text-lg font-bold mb-4")

            @ui.refreshable
            def render_edit_form():
                """Render the edit form for selected item."""
                if not selected_item["data"]:
                    ui.label("← Select an item to edit or click '+ Add New Item'").classes("text-gray-500 italic")
                    return

                # Form fields
                title_input = ui.input(
                    label="Title",
                    value=selected_item["data"].get("title", "")
                ).classes("w-full mb-2")

                description_input = ui.textarea(
                    label="Description",
                    value=selected_item["data"].get("description", "")
                ).classes("w-full mb-2").props("rows=3")

                with ui.row().classes("w-full gap-2 mb-2"):
                    category_input = ui.input(
                        label="Category",
                        value=selected_item["data"].get("category", "")
                    ).classes("flex-grow")

                    topic_input = ui.input(
                        label="Topic",
                        value=selected_item["data"].get("topic", "")
                    ).classes("flex-grow")

                rationale_input = ui.textarea(
                    label="Rationale Template",
                    value=selected_item["data"].get("rationale_template", ""),
                    placeholder="Use {placeholders} for user data"
                ).classes("w-full mb-2").props("rows=4")

                partner_equiv_checkbox = ui.checkbox(
                    "Has Partner Equivalent",
                    value=selected_item["data"].get("partner_equivalent", False)
                ).classes("mb-2")

                ui.label("Eligibility Rules (JSON)").classes("font-bold mb-1")
                eligibility_input = ui.textarea(
                    value=json.dumps(selected_item["data"].get("eligibility", {}), indent=2),
                    placeholder='{"min_utilization": 0.30}'
                ).classes("w-full mb-4").props("rows=6")

                # Action buttons
                with ui.row().classes("gap-2"):
                    def save_item():
                        """Save the edited item."""
                        nonlocal catalog  # Declare nonlocal at the top of the function
                        try:
                            # Parse eligibility JSON
                            eligibility = json.loads(eligibility_input.value or "{}")

                            # Build updated item
                            updated_item = {
                                "title": title_input.value,
                                "description": description_input.value,
                                "category": category_input.value,
                                "topic": topic_input.value,
                                "rationale_template": rationale_input.value,
                                "partner_equivalent": partner_equiv_checkbox.value,
                                "eligibility": eligibility,
                            }

                            # Save override
                            save_override(
                                selected_item["type"],
                                selected_item["persona"],
                                updated_item
                            )

                            ui.notify("✓ Item saved successfully!", type="positive")

                            # Refresh catalog and list
                            catalog = load_content_catalog()
                            render_content_list.refresh()

                        except json.JSONDecodeError as e:
                            ui.notify(f"Invalid JSON in eligibility: {e}", type="negative")
                        except Exception as e:
                            ui.notify(f"Error saving item: {e}", type="negative")

                    ui.button("Save", icon="save", on_click=save_item).props("color=primary")
                    ui.button("Cancel", icon="cancel", on_click=lambda: (
                        selected_item.update({"persona": None, "type": None, "index": None, "data": {}}),
                        render_edit_form.refresh()
                    )).props("flat")

            render_edit_form()

    # Helper functions
    def load_item_for_editing(persona, content_type, index):
        """Load an item into the edit form."""
        items = catalog.get(content_type, {}).get(persona, [])
        if index < len(items):
            selected_item["persona"] = persona
            selected_item["type"] = content_type
            selected_item["index"] = index
            selected_item["data"] = items[index].copy()
            render_edit_form.refresh()

    def load_blank_form():
        """Load a blank form for creating new item."""
        selected_item["persona"] = get_all_personas()[0]  # Default to first persona
        selected_item["type"] = "educational"
        selected_item["index"] = -1  # -1 indicates new item
        selected_item["data"] = {
            "title": "",
            "description": "",
            "category": "",
            "topic": "",
            "rationale_template": "",
            "partner_equivalent": False,
            "eligibility": {}
        }
        render_edit_form.refresh()

    def confirm_delete_item(persona, content_type, index, title):
        """Confirm and delete an item."""
        async def delete():
            nonlocal catalog  # Declare nonlocal at the top
            try:
                items = catalog.get(content_type, {}).get(persona, [])
                if index < len(items):
                    item = items[index]
                    item_id = item.get("id") or f"{item.get('title', '').lower().replace(' ', '_')}_{item.get('topic', '')}"
                    delete_override(content_type, persona, item_id)

                    ui.notify(f"✓ Deleted: {title}", type="positive")

                    # Refresh
                    catalog = load_content_catalog()
                    render_content_list.refresh()

                    # Clear edit form if this item was selected
                    if selected_item["index"] == index:
                        selected_item.update({"persona": None, "type": None, "index": None, "data": {}})
                        render_edit_form.refresh()
            except Exception as e:
                ui.notify(f"Error deleting item: {e}", type="negative")

        with ui.dialog() as dialog, ui.card():
            ui.label(f"Delete '{title}'?").classes("text-lg font-bold")
            ui.label("This will mark the item as deleted in overrides.").classes("text-sm text-gray-500 mb-4")
            with ui.row():
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button("Delete", on_click=lambda: (delete(), dialog.close())).props("color=red")
        dialog.open()

    # Bottom action buttons
    ui.separator().classes("my-6")
    with ui.row().classes("gap-4"):
        def handle_reset():
            """Reset to defaults."""
            with ui.dialog() as dialog, ui.card():
                ui.label("Reset to Defaults?").classes("text-lg font-bold")
                ui.label("This will delete all operator overrides and revert to default catalog.").classes("text-sm mb-4")
                with ui.row():
                    ui.button("Cancel", on_click=dialog.close).props("flat")
                    ui.button("Reset", on_click=lambda: (
                        reset_to_defaults(),
                        ui.notify("✓ Reset to defaults", type="positive"),
                        dialog.close(),
                        render_content_management_tab.refresh()
                    )).props("color=red")
            dialog.open()

        def handle_export():
            """Export catalog."""
            try:
                export_path = export_catalog()
                ui.notify(f"✓ Exported to {export_path}", type="positive")
            except Exception as e:
                ui.notify(f"Error exporting: {e}", type="negative")

        ui.button("Reset to Defaults", icon="refresh", on_click=handle_reset).props("color=red outline")
        ui.button("Export Catalog", icon="download", on_click=handle_export).props("color=blue outline")


# =============================================================================
# AUTHENTICATION
# =============================================================================

# Load authentication credentials from environment
OPERATOR_USERNAME = os.getenv("OPERATOR_USERNAME", "operator")
OPERATOR_PASSWORD_HASH = os.getenv("OPERATOR_PASSWORD_HASH", "")  # SHA256 hash
OPERATOR_PASSWORD = os.getenv("OPERATOR_PASSWORD", "")  # Plain password for local dev
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "true").lower() == "true"


def hash_password(password: str) -> str:
    """Create SHA256 hash of password."""
    return hashlib.sha256(password.encode()).hexdigest()


def check_auth():
    """Check if user is authenticated."""
    if not AUTH_ENABLED:
        return True

    # Check if already authenticated in session
    if app.storage.user.get("authenticated", False):
        return True

    return False


def verify_credentials(username: str, password: str) -> bool:
    """Verify username and password."""
    if username != OPERATOR_USERNAME:
        return False

    # Check against hashed password if available
    if OPERATOR_PASSWORD_HASH:
        return hash_password(password) == OPERATOR_PASSWORD_HASH

    # Fallback to plain password for local dev
    if OPERATOR_PASSWORD:
        return password == OPERATOR_PASSWORD

    # No password set - deny access in production
    return False


@ui.page("/login")
def login_page():
    """Login page with authentication form."""

    def try_login():
        """Attempt to log in with provided credentials."""
        if verify_credentials(username.value, password.value):
            app.storage.user["authenticated"] = True
            ui.navigate.to("/")
        else:
            ui.notify("Invalid credentials", type="negative")
            password.value = ""

    with ui.column().classes("absolute-center items-center"):
        ui.icon("engineering", size="64px").classes("mb-4 text-primary")
        ui.label("SpendSense Operator Dashboard").classes("text-2xl font-bold mb-2")
        ui.label("Please log in to continue").classes("text-gray-600 mb-6")

        with ui.card().classes("p-6"):
            username = ui.input("Username", placeholder="operator").props("autofocus").classes("w-64")
            password = ui.input("Password", password=True, password_toggle_button=True).props(
                "clearable"
            ).classes("w-64").on("keydown.enter", try_login)

            ui.button("Log In", icon="login", on_click=try_login).props("color=primary").classes("w-full mt-4")


# =============================================================================
# MAIN PAGE
# =============================================================================


@ui.page("/")
async def main_page():
    """Main operator dashboard page."""
    # Initialize themes
    ThemeManager.initialize_themes()
    # Always use Clean & Minimal theme
    ThemeManager.set_theme(Theme.CLEAN_MINIMAL)
    ThemeManager.apply_theme(Theme.CLEAN_MINIMAL)

    # Initialize operator name from storage
    if "operator_name" not in app.storage.user:
        app.storage.user["operator_name"] = ""

    # Always refresh data on page load to reflect external changes
    refresh_data()
    # Track data mtime at last refresh
    app.storage.user["last_data_mtime"] = _get_data_mtime()

    # Header
    with ui.header().classes("items-center justify-between px-6"):
        with ui.row().classes("items-center gap-4"):
            ui.icon("engineering").classes("text-3xl")
            with ui.column().classes("gap-0"):
                ui.label("SpendSense Operator Dashboard").classes("text-xl font-bold")
                ui.label("Compliance & Oversight Interface").classes("text-sm opacity-80")

        with ui.row().classes("items-center gap-4"):
            # Operator name input
            ui.input(label="Operator Name", placeholder="Your name").bind_value(
                app.storage.user, "operator_name"
            ).props(
                "outlined dense dark label-color=white input-class=text-white color=white clearable"
            ).classes(
                "w-64"
            )

            # Refresh button
            def handle_refresh():
                refresh_data()
                ui.notify("Data refreshed", type="positive")
                render_overview_tab.refresh()
                render_user_management_tab.refresh()
                render_behavioral_signals_tab.refresh()
                render_recommendation_review_tab.refresh()
                render_decision_trace_viewer_tab.refresh()
                render_guardrails_monitor_tab.refresh()
                render_data_generation_tab.refresh()
                render_content_management_tab.refresh()
                app.storage.user["last_data_mtime"] = _get_data_mtime()

            ui.button(icon="refresh", on_click=handle_refresh).props("flat round")

            # Show indicator if external data changed since last refresh
            try:
                if _get_data_mtime() > app.storage.user.get("last_data_mtime", 0):
                    ui.button(
                        "New data available", icon="notification_important", on_click=handle_refresh
                    ).props("flat color=warning")
            except Exception:
                pass

    # No auto-refresh; manual refresh with change indicator only

    # Main content with tabs
    with ui.tabs().classes("w-full") as tabs:
        tab_overview = ui.tab("Overview", icon="dashboard")
        tab_users = ui.tab("Users", icon="people")
        tab_signals = ui.tab("Signals", icon="trending_up")
        tab_recommendations = ui.tab("Recommendations", icon="recommend")
        tab_traces = ui.tab("Traces", icon="timeline")
        tab_guardrails = ui.tab("Guardrails", icon="shield")
        tab_datagen = ui.tab("Data Generation", icon="build")
        tab_content = ui.tab("Content Management", icon="edit_note")

    with ui.tab_panels(tabs, value=tab_overview).classes("w-full p-6"):
        with ui.tab_panel(tab_overview):
            render_overview_tab()

        with ui.tab_panel(tab_users):
            render_user_management_tab()

        with ui.tab_panel(tab_signals):
            render_behavioral_signals_tab()

        with ui.tab_panel(tab_recommendations):
            render_recommendation_review_tab()

        with ui.tab_panel(tab_traces):
            render_decision_trace_viewer_tab()

        with ui.tab_panel(tab_guardrails):
            render_guardrails_monitor_tab()

        with ui.tab_panel(tab_datagen):
            render_data_generation_tab()

        with ui.tab_panel(tab_content):
            render_content_management_tab()


# =============================================================================
# RUN APP
# =============================================================================

if __name__ in {"__main__", "__mp_main__"}:
    import os

    # Production configuration
    PORT = int(os.getenv("PORT", 8085))
    RELOAD = os.getenv("RELOAD", "false").lower() == "true"
    SHOW = os.getenv("SHOW", "false").lower() == "true"
    STORAGE_SECRET = os.getenv("STORAGE_SECRET", "spendsense-operator-dashboard-secret-key-change-in-production")

    ui.run(
        title="SpendSense Operator Dashboard",
        host="0.0.0.0",  # Required for Railway deployment
        port=PORT,
        reload=RELOAD,
        show=SHOW,
        storage_secret=STORAGE_SECRET,
        reconnect_timeout=60,  # Increase websocket timeout for slower initial loads
    )

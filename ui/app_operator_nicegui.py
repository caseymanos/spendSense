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

import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import json

from nicegui import ui, app

# Import theme system
from ui.themes import ThemeManager, Theme

# Import utilities
from ui.utils.data_loaders import (
    load_all_users,
    load_all_signals,
    load_user_trace,
    load_persona_distribution,
    load_guardrail_summary,
    load_config,
    save_config,
    log_operator_override,
)

# Import components
from ui.components import (
    create_metric_card,
    create_summary_metrics_row,
    create_data_table,
    create_persona_chart,
    create_credit_utilization_histogram,
    create_histogram,
    create_operator_actions,
)

# =============================================================================
# GLOBAL STATE
# =============================================================================

# Operator state
operator_state = {
    'operator_name': '',
    'current_tab': 'overview',
    'selected_user_id': None,
}

# Data cache
data_cache = {
    'users': None,
    'signals': None,
    'persona_distribution': None,
    'guardrail_summary': None,
    'last_refresh': None,
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def refresh_data():
    """Refresh all data from sources."""
    data_cache['users'] = load_all_users()
    data_cache['signals'] = load_all_signals()
    data_cache['persona_distribution'] = load_persona_distribution()
    data_cache['guardrail_summary'] = load_guardrail_summary()
    data_cache['last_refresh'] = datetime.now()


def get_persona_description(persona: str) -> str:
    """Get description for a persona."""
    descriptions = {
        "High Utilization": "Credit card utilization > 50% (prioritized for debt reduction advice)",
        "Variable Income Budgeter": "Income deposits with >20 day gap variance (irregular income patterns)",
        "Subscription Heavy": "5+ recurring subscriptions (focus on spending optimization)",
        "Savings Builder": "Consistent savings deposits (positive reinforcement for good habits)",
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
    users_df = data_cache['users']
    persona_dist = data_cache['persona_distribution']
    guardrail_summary = data_cache['guardrail_summary']

    if users_df is None or users_df.empty:
        ui.label('No data available. Please generate data first.').classes('text-center p-8 text-gray-500')
        return

    # Summary metrics
    total_users = len(users_df)
    users_with_consent = users_df['consent_granted'].sum()
    consent_pct = (users_with_consent / total_users * 100) if total_users > 0 else 0
    distinct_personas = users_df['persona'].nunique()
    total_recs = guardrail_summary.get('total_recommendations', 0)

    metrics = [
        {'title': 'Total Users', 'value': total_users, 'icon': 'people'},
        {'title': 'Consent Granted', 'value': f'{consent_pct:.0f}%', 'icon': 'verified_user'},
        {'title': 'Personas', 'value': distinct_personas, 'icon': 'category'},
        {'title': 'Recommendations', 'value': total_recs, 'icon': 'recommend'},
    ]

    create_summary_metrics_row(metrics, ThemeManager.get_metric_card_classes())

    ui.separator().classes('my-6')

    # Persona distribution chart
    with ui.card().classes(ThemeManager.get_card_classes() + ' mt-4'):
        ui.label('Persona Distribution').classes('text-xl font-bold mb-4')

        if persona_dist:
            create_persona_chart(persona_dist, ThemeManager.get_chart_colors())

            # Persona definitions table
            ui.label('Persona Definitions').classes('text-lg font-semibold mt-6 mb-2')

            persona_data = []
            for persona, count in persona_dist.items():
                persona_data.append({
                    'persona': persona,
                    'count': count,
                    'description': get_persona_description(persona)
                })

            persona_df = pd.DataFrame(persona_data)
            create_data_table(
                data=persona_df,
                columns=[
                    {'name': 'persona', 'label': 'Persona', 'field': 'persona', 'align': 'left'},
                    {'name': 'count', 'label': 'Count', 'field': 'count', 'align': 'center'},
                    {'name': 'description', 'label': 'Description', 'field': 'description', 'align': 'left'},
                ],
                theme_classes=ThemeManager.get_table_classes()
            )

    ui.separator().classes('my-6')

    # Guardrails summary
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label('Guardrails Summary').classes('text-xl font-bold mb-4')

        tone_violations_count = len(guardrail_summary.get('tone_violations', []))
        blocked_offers_count = len(guardrail_summary.get('blocked_offers', []))
        no_consent_count = total_users - users_with_consent

        guardrail_metrics = [
            {'title': 'Tone Violations', 'value': tone_violations_count, 'icon': 'warning', 'delta_color': 'red'},
            {'title': 'Blocked Offers', 'value': blocked_offers_count, 'icon': 'block', 'delta_color': 'orange'},
            {'title': 'No Consent', 'value': no_consent_count, 'icon': 'cancel', 'delta_color': 'red'},
        ]

        create_summary_metrics_row(guardrail_metrics, ThemeManager.get_metric_card_classes())


# =============================================================================
# TAB 2: USER MANAGEMENT
# =============================================================================

@ui.refreshable
def render_user_management_tab():
    """Render User Management tab with filtering."""
    users_df = data_cache['users']

    if users_df is None or users_df.empty:
        ui.label('No users data available').classes('text-center p-8 text-gray-500')
        return

    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label('User Management').classes('text-xl font-bold mb-4')

        # Filters
        with ui.row().classes('gap-4 mb-4'):
            consent_filter = ui.select(
                label='Consent Status',
                options=['All', 'Granted', 'Not Granted'],
                value='All'
            ).classes('w-48')

            persona_options = ['All'] + sorted(users_df['persona'].dropna().unique().tolist())
            persona_filter = ui.select(
                label='Persona',
                options=persona_options,
                value='All'
            ).classes('w-48')

            gender_options = ['All'] + sorted(users_df['gender'].dropna().unique().tolist())
            gender_filter = ui.select(
                label='Gender',
                options=gender_options,
                value='All'
            ).classes('w-48')

            income_options = ['All'] + sorted(users_df['income_tier'].dropna().unique().tolist())
            income_filter = ui.select(
                label='Income Tier',
                options=income_options,
                value='All'
            ).classes('w-48')

        # Filtered data container
        filtered_table_container = ui.column().classes('w-full')

        def update_filtered_table():
            """Update table based on filters."""
            filtered_df = users_df.copy()

            # Apply filters
            if consent_filter.value != 'All':
                consent_val = consent_filter.value == 'Granted'
                filtered_df = filtered_df[filtered_df['consent_granted'] == consent_val]

            if persona_filter.value != 'All':
                filtered_df = filtered_df[filtered_df['persona'] == persona_filter.value]

            if gender_filter.value != 'All':
                filtered_df = filtered_df[filtered_df['gender'] == gender_filter.value]

            if income_filter.value != 'All':
                filtered_df = filtered_df[filtered_df['income_tier'] == income_filter.value]

            # Display filtered table
            filtered_table_container.clear()
            with filtered_table_container:
                ui.label(f'Showing {len(filtered_df)} users').classes('text-sm text-gray-600 mb-2')

                display_cols = ['user_id', 'name', 'consent_granted', 'persona', 'age', 'gender', 'income_tier', 'region']
                display_df = filtered_df[display_cols]

                create_data_table(
                    data=display_df,
                    row_key='user_id',
                    pagination=20,
                    theme_classes=ThemeManager.get_table_classes()
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
    signals_df = data_cache['signals']

    if signals_df is None or signals_df.empty:
        ui.label('No signals data available').classes('text-center p-8 text-gray-500')
        return

    # Aggregate metrics
    avg_credit_util = signals_df['credit_utilization_30d'].mean() if 'credit_utilization_30d' in signals_df.columns else 0
    avg_subscriptions = signals_df['recurring_subscriptions_30d'].mean() if 'recurring_subscriptions_30d' in signals_df.columns else 0
    median_savings = signals_df['savings_inflow_180d'].median() if 'savings_inflow_180d' in signals_df.columns else 0
    median_pay_gap = signals_df['pay_gap_variance_30d'].median() if 'pay_gap_variance_30d' in signals_df.columns else 0

    metrics = [
        {'title': 'Avg Credit Utilization', 'value': f'{avg_credit_util:.1%}', 'icon': 'credit_card'},
        {'title': 'Avg Subscriptions', 'value': f'{avg_subscriptions:.1f}', 'icon': 'subscriptions'},
        {'title': 'Median Savings (180d)', 'value': f'${median_savings:,.0f}', 'icon': 'savings'},
        {'title': 'Median Pay Gap', 'value': f'{median_pay_gap:.1f} days', 'icon': 'schedule'},
    ]

    create_summary_metrics_row(metrics, ThemeManager.get_metric_card_classes())

    ui.separator().classes('my-6')

    # Distribution charts
    with ui.row().classes('w-full gap-4'):
        # Credit utilization histogram
        with ui.card().classes(ThemeManager.get_card_classes() + ' flex-1'):
            ui.label('Credit Utilization Distribution').classes('text-lg font-bold mb-4')
            create_credit_utilization_histogram(signals_df, ThemeManager.get_chart_colors())

        # Subscription count distribution
        with ui.card().classes(ThemeManager.get_card_classes() + ' flex-1'):
            ui.label('Subscription Count Distribution').classes('text-lg font-bold mb-4')
            if 'recurring_subscriptions_30d' in signals_df.columns:
                create_histogram(
                    data=signals_df,
                    column='recurring_subscriptions_30d',
                    title='',
                    x_label='Number of Subscriptions',
                    bins=15,
                    chart_colors=ThemeManager.get_chart_colors()
                )

    ui.separator().classes('my-6')

    # 30d vs 180d comparison
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label('Signal Comparison: 30d vs 180d').classes('text-xl font-bold mb-4')

        comparison_data = []

        # Recurring subscriptions
        if 'recurring_subscriptions_30d' in signals_df.columns and 'recurring_subscriptions_180d' in signals_df.columns:
            comparison_data.append({
                'signal': 'Recurring Subscriptions',
                '30d_avg': f"{signals_df['recurring_subscriptions_30d'].mean():.2f}",
                '180d_avg': f"{signals_df['recurring_subscriptions_180d'].mean():.2f}",
            })

        # Pay gap variance
        if 'pay_gap_variance_30d' in signals_df.columns and 'pay_gap_variance_180d' in signals_df.columns:
            comparison_data.append({
                'signal': 'Pay Gap Variance (days)',
                '30d_avg': f"{signals_df['pay_gap_variance_30d'].median():.2f}",
                '180d_avg': f"{signals_df['pay_gap_variance_180d'].median():.2f}",
            })

        # Credit utilization
        if 'credit_utilization_30d' in signals_df.columns:
            comparison_data.append({
                'signal': 'Credit Utilization',
                '30d_avg': f"{signals_df['credit_utilization_30d'].mean():.1%}",
                '180d_avg': 'N/A',
            })

        # Savings inflow
        if 'savings_inflow_180d' in signals_df.columns:
            comparison_data.append({
                'signal': 'Savings Inflow',
                '30d_avg': 'N/A',
                '180d_avg': f"${signals_df['savings_inflow_180d'].median():,.0f}",
            })

        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            create_data_table(
                data=comparison_df,
                columns=[
                    {'name': 'signal', 'label': 'Signal Type', 'field': 'signal', 'align': 'left'},
                    {'name': '30d_avg', 'label': '30-Day Window', 'field': '30d_avg', 'align': 'center'},
                    {'name': '180d_avg', 'label': '180-Day Window', 'field': '180d_avg', 'align': 'center'},
                ],
                theme_classes=ThemeManager.get_table_classes()
            )

    ui.separator().classes('my-6')

    # Per-user signal drill-down
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label('Per-User Signal Detail').classes('text-xl font-bold mb-4')

        # User selector
        user_ids = signals_df['user_id'].unique().tolist() if 'user_id' in signals_df.columns else []

        if user_ids:
            selected_user_container = ui.column().classes('w-full')

            user_select = ui.select(
                label='Select User',
                options=user_ids,
                value=user_ids[0] if user_ids else None
            ).classes('w-64 mb-4')

            def display_user_signals():
                """Display signals for selected user."""
                selected_user_container.clear()

                if not user_select.value:
                    return

                user_signals = signals_df[signals_df['user_id'] == user_select.value].iloc[0].to_dict()

                with selected_user_container:
                    # Credit signals
                    with ui.expansion('Credit Signals', icon='credit_card', value=True).classes('w-full'):
                        credit_cols = [col for col in user_signals.keys() if 'credit' in col.lower()]
                        if credit_cols:
                            for col in credit_cols:
                                val = user_signals[col]
                                if pd.notna(val):
                                    with ui.row().classes('w-full justify-between items-center mb-2'):
                                        ui.label(col.replace('_', ' ').title()).classes('font-semibold')
                                        if isinstance(val, float) and 'utilization' in col:
                                            ui.label(f'{val:.1%}').classes('text-blue-600')
                                        else:
                                            ui.label(str(val)).classes('text-blue-600')

                    # Subscription signals
                    with ui.expansion('Subscription Signals', icon='subscriptions').classes('w-full'):
                        sub_cols = [col for col in user_signals.keys() if 'subscription' in col.lower() or 'recurring' in col.lower()]
                        if sub_cols:
                            for col in sub_cols:
                                val = user_signals[col]
                                if pd.notna(val):
                                    with ui.row().classes('w-full justify-between items-center mb-2'):
                                        ui.label(col.replace('_', ' ').title()).classes('font-semibold')
                                        ui.label(str(val)).classes('text-purple-600')

                    # Savings signals
                    with ui.expansion('Savings Signals', icon='savings').classes('w-full'):
                        savings_cols = [col for col in user_signals.keys() if 'savings' in col.lower()]
                        if savings_cols:
                            for col in savings_cols:
                                val = user_signals[col]
                                if pd.notna(val):
                                    with ui.row().classes('w-full justify-between items-center mb-2'):
                                        ui.label(col.replace('_', ' ').title()).classes('font-semibold')
                                        if isinstance(val, (int, float)):
                                            ui.label(f'${val:,.2f}').classes('text-green-600')
                                        else:
                                            ui.label(str(val)).classes('text-green-600')

                    # Income signals
                    with ui.expansion('Income Signals', icon='payments').classes('w-full'):
                        income_cols = [col for col in user_signals.keys() if 'pay' in col.lower() or 'income' in col.lower()]
                        if income_cols:
                            for col in income_cols:
                                val = user_signals[col]
                                if pd.notna(val):
                                    with ui.row().classes('w-full justify-between items-center mb-2'):
                                        ui.label(col.replace('_', ' ').title()).classes('font-semibold')
                                        if isinstance(val, (int, float)) and 'gap' in col:
                                            ui.label(f'{val:.1f} days').classes('text-orange-600')
                                        else:
                                            ui.label(str(val)).classes('text-orange-600')

            user_select.on_value_change(lambda: display_user_signals())
            display_user_signals()  # Initial display
        else:
            ui.label('No user data available').classes('text-gray-500')


# =============================================================================
# TAB 4: RECOMMENDATION REVIEW
# =============================================================================

@ui.refreshable
def render_recommendation_review_tab():
    """Render Recommendation Review tab with operator actions."""
    users_df = data_cache['users']

    if users_df is None or users_df.empty:
        ui.label('No users data available').classes('text-center p-8 text-gray-500')
        return

    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label('Recommendation Review').classes('text-xl font-bold mb-4')

        # User selector
        user_ids = users_df['user_id'].tolist()
        user_names = users_df['name'].tolist()
        user_personas = users_df['persona'].fillna('No Persona').tolist()

        user_options = {
            f"{uid} - {name} ({persona})": uid
            for uid, name, persona in zip(user_ids, user_names, user_personas)
        }

        recommendation_container = ui.column().classes('w-full')

        with ui.row().classes('w-full items-center gap-4 mb-4'):
            user_select = ui.select(
                label='Select User',
                options=list(user_options.keys()),
                value=list(user_options.keys())[0] if user_options else None
            ).classes('flex-grow')

            load_button = ui.button('Load Recommendations', icon='download') \
                .props('color=primary').classes(ThemeManager.get_button_classes())

        def load_recommendations():
            """Load and display recommendations for selected user."""
            recommendation_container.clear()

            if not user_select.value:
                with recommendation_container:
                    ui.label('Please select a user').classes('text-gray-500')
                return

            selected_user_id = user_options[user_select.value]
            trace = load_user_trace(selected_user_id)

            if not trace:
                with recommendation_container:
                    ui.label(f'No trace found for user {selected_user_id}').classes('text-orange-600')
                return

            recommendations_data = trace.get('recommendations', {})
            consent_granted = recommendations_data.get('consent_granted', False)
            persona = recommendations_data.get('persona', 'Unknown')
            recommendations_list = recommendations_data.get('recommendations', [])

            with recommendation_container:
                # Metadata
                with ui.card().classes('bg-blue-50 p-4 mb-4'):
                    with ui.row().classes('w-full items-center gap-8'):
                        with ui.column().classes('gap-1'):
                            ui.label('User ID:').classes('text-xs text-gray-600')
                            ui.label(selected_user_id).classes('font-semibold')

                        with ui.column().classes('gap-1'):
                            ui.label('Persona:').classes('text-xs text-gray-600')
                            ui.label(persona).classes('font-semibold')

                        with ui.column().classes('gap-1'):
                            ui.label('Consent:').classes('text-xs text-gray-600')
                            consent_badge = ui.badge('Granted' if consent_granted else 'Not Granted')
                            consent_badge.props(f'color={"positive" if consent_granted else "negative"}')

                        with ui.column().classes('gap-1'):
                            ui.label('Total Recommendations:').classes('text-xs text-gray-600')
                            ui.label(str(len(recommendations_list))).classes('font-semibold')

                # Recommendations
                if not recommendations_list:
                    ui.label('No recommendations generated for this user').classes('text-gray-500 p-4')
                    return

                education_items = [r for r in recommendations_list if r.get('type') == 'education']
                partner_offers = [r for r in recommendations_list if r.get('type') == 'partner_offer']

                ui.label(f'Education Items: {len(education_items)} | Partner Offers: {len(partner_offers)}') \
                    .classes('text-sm text-gray-600 mb-4')

                # Display each recommendation
                for idx, rec in enumerate(recommendations_list):
                    rec_type = rec.get('type', 'unknown')
                    rec_category = rec.get('category', 'N/A')
                    rec_title = rec.get('title', 'Untitled')
                    rec_description = rec.get('description', '')
                    rec_rationale = rec.get('rationale', 'No rationale provided')
                    rec_disclaimer = rec.get('disclaimer', '')

                    # Icon based on type
                    icon = 'school' if rec_type == 'education' else 'local_offer'
                    type_color = 'blue' if rec_type == 'education' else 'purple'

                    with ui.expansion(f"{rec_title}", icon=icon).classes('w-full mb-2') as expansion:
                        expansion.classes(f'border-l-4 border-{type_color}-500')

                        with ui.column().classes('gap-3 p-2'):
                            # Type and category
                            with ui.row().classes('gap-2'):
                                ui.badge(rec_type.replace('_', ' ').title()).props(f'color={type_color}')
                                ui.badge(rec_category).props('outline')

                            # Description
                            if rec_description:
                                with ui.card().classes('bg-gray-50 p-3'):
                                    ui.label('Description:').classes('text-xs font-semibold text-gray-600 mb-1')
                                    ui.label(rec_description).classes('text-sm')

                            # Rationale (most important for compliance)
                            with ui.card().classes('bg-yellow-50 border border-yellow-200 p-3'):
                                ui.label('Rationale:').classes('text-xs font-semibold text-gray-600 mb-1')
                                ui.label(rec_rationale).classes('text-sm font-medium')

                            # Disclaimer
                            if rec_disclaimer:
                                with ui.card().classes('bg-red-50 border border-red-200 p-3'):
                                    ui.label('Disclaimer:').classes('text-xs font-semibold text-gray-600 mb-1')
                                    ui.label(rec_disclaimer).classes('text-xs')

                            ui.separator().classes('my-2')

                            # Guardrail checks
                            ui.label('Guardrail Checks:').classes('text-sm font-semibold mb-2')

                            # Tone check (simulated - in real implementation would call validate_tone)
                            tone_check = 'PASS'  # Placeholder
                            tone_check_color = 'positive' if tone_check == 'PASS' else 'negative'

                            with ui.row().classes('items-center gap-2'):
                                ui.icon('check_circle' if tone_check == 'PASS' else 'cancel') \
                                    .classes(f'text-{tone_check_color}')
                                ui.label(f'Tone Validation: {tone_check}').classes('text-sm')

                            # Eligibility check (simulated)
                            eligibility = 'ELIGIBLE'  # Placeholder
                            eligibility_color = 'positive' if eligibility == 'ELIGIBLE' else 'negative'

                            with ui.row().classes('items-center gap-2'):
                                ui.icon('check_circle' if eligibility == 'ELIGIBLE' else 'cancel') \
                                    .classes(f'text-{eligibility_color}')
                                ui.label(f'Eligibility: {eligibility}').classes('text-sm')

                            ui.separator().classes('my-2')

                            # Operator actions
                            ui.label('Operator Actions:').classes('text-sm font-semibold mb-2')

                            def refresh_after_action():
                                """Refresh view after operator action."""
                                load_recommendations()

                            create_operator_actions(
                                user_id=selected_user_id,
                                recommendation_title=rec_title,
                                on_action_complete=refresh_after_action,
                                theme_classes=ThemeManager.get_button_classes()
                            )

        load_button.on_click(load_recommendations)

        # Auto-load first user
        if user_options:
            load_recommendations()


# =============================================================================
# TAB 5: DECISION TRACE VIEWER
# =============================================================================

@ui.refreshable
def render_decision_trace_viewer_tab():
    """Render Decision Trace Viewer tab with full audit trail."""
    users_df = data_cache['users']

    if users_df is None or users_df.empty:
        ui.label('No users data available').classes('text-center p-8 text-gray-500')
        return

    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label('Decision Trace Viewer').classes('text-xl font-bold mb-4')
        ui.label('View complete decision trace for audit and compliance').classes('text-sm text-gray-600 mb-6')

        # User selector
        user_ids = users_df['user_id'].tolist()
        user_names = users_df['name'].tolist()

        user_options = {f"{uid} - {name}": uid for uid, name in zip(user_ids, user_names)}

        trace_container = ui.column().classes('w-full')

        user_select = ui.select(
            label='Select User',
            options=list(user_options.keys()),
            value=list(user_options.keys())[0] if user_options else None
        ).classes('w-96 mb-4')

        def display_trace():
            """Display trace for selected user."""
            trace_container.clear()

            if not user_select.value:
                return

            selected_user_id = user_options[user_select.value]
            trace = load_user_trace(selected_user_id)

            if not trace:
                with trace_container:
                    ui.label(f'No trace found for user {selected_user_id}').classes('text-orange-600')
                return

            with trace_container:
                # User info summary
                user_info = users_df[users_df['user_id'] == selected_user_id].iloc[0]

                with ui.card().classes('bg-blue-50 p-4 mb-4'):
                    ui.label('User Information').classes('text-lg font-bold mb-3')

                    with ui.row().classes('w-full gap-8'):
                        with ui.column():
                            ui.label(f"Name: {user_info.get('name', 'N/A')}").classes('text-sm')
                            ui.label(f"Persona: {user_info.get('persona', 'N/A')}").classes('text-sm')

                        with ui.column():
                            consent = user_info.get('consent_granted', False)
                            ui.label(f"Consent: {'Granted' if consent else 'Not Granted'}").classes('text-sm')
                            ui.label(f"Age: {user_info.get('age', 'N/A')} | Gender: {user_info.get('gender', 'N/A')}").classes('text-sm')

                # Behavioral signals
                with ui.expansion('Behavioral Signals', icon='analytics', value=False).classes('w-full mb-2'):
                    signals = trace.get('behavioral_signals', {})

                    if signals:
                        # 30d signals
                        signals_30d = signals.get('30d', {})
                        if signals_30d:
                            ui.label('30-Day Signals:').classes('font-semibold mb-2')
                            ui.json_editor(signals_30d).props('mode=view readonly').classes('w-full mb-4')

                        # 180d signals
                        signals_180d = signals.get('180d', {})
                        if signals_180d:
                            ui.label('180-Day Signals:').classes('font-semibold mb-2')
                            ui.json_editor(signals_180d).props('mode=view readonly').classes('w-full')
                    else:
                        ui.label('No behavioral signals in trace').classes('text-gray-500')

                # Persona assignment
                with ui.expansion('Persona Assignment', icon='category', value=False).classes('w-full mb-2'):
                    persona_data = trace.get('persona_assignment', {})

                    if persona_data:
                        ui.json_editor(persona_data).props('mode=view readonly').classes('w-full')
                    else:
                        ui.label('No persona assignment in trace').classes('text-gray-500')

                # Recommendations
                with ui.expansion('Recommendations', icon='recommend', value=False).classes('w-full mb-2'):
                    recommendations_data = trace.get('recommendations', {})

                    if recommendations_data:
                        # Summary
                        recs = recommendations_data.get('recommendations', [])
                        ui.label(f"Generated {len(recs)} recommendations").classes('font-semibold mb-2')

                        ui.json_editor(recommendations_data).props('mode=view readonly').classes('w-full')
                    else:
                        ui.label('No recommendations in trace').classes('text-gray-500')

                # Guardrail decisions
                with ui.expansion('Guardrail Decisions', icon='shield', value=False).classes('w-full mb-2'):
                    guardrail_decisions = trace.get('guardrail_decisions', [])

                    if guardrail_decisions:
                        ui.label(f"Total decisions: {len(guardrail_decisions)}").classes('font-semibold mb-2')

                        for idx, decision in enumerate(guardrail_decisions):
                            with ui.expansion(f"Decision {idx+1}: {decision.get('decision_type', 'Unknown')}", icon='rule') \
                                    .classes('w-full mb-2'):
                                ui.json_editor(decision).props('mode=view readonly').classes('w-full')
                    else:
                        ui.label('No guardrail decisions in trace').classes('text-gray-500')

                # Raw JSON
                with ui.expansion('Raw JSON', icon='code', value=False).classes('w-full'):
                    with ui.row().classes('w-full justify-end mb-2'):
                        def copy_json():
                            ui.notify('JSON copied to clipboard!', type='positive')

                        ui.button('Copy to Clipboard', icon='content_copy', on_click=copy_json).props('flat dense')

                    ui.json_editor(trace).props('mode=view readonly').classes('w-full h-96')

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
    guardrail_summary = data_cache['guardrail_summary']
    users_df = data_cache['users']

    if guardrail_summary is None:
        ui.label('No guardrails data available').classes('text-center p-8 text-gray-500')
        return

    # Summary metrics
    total_users = guardrail_summary.get('total_users', 0)
    users_with_consent = guardrail_summary.get('users_with_consent', 0)
    tone_violations_list = guardrail_summary.get('tone_violations', [])
    blocked_offers_list = guardrail_summary.get('blocked_offers', [])

    metrics = [
        {'title': 'Total Users', 'value': total_users, 'icon': 'people'},
        {'title': 'With Consent', 'value': users_with_consent, 'icon': 'verified_user'},
        {'title': 'Tone Violations', 'value': len(tone_violations_list), 'icon': 'warning', 'delta': '-12%', 'delta_color': 'green'},
        {'title': 'Blocked Offers', 'value': len(blocked_offers_list), 'icon': 'block', 'delta': '-8%', 'delta_color': 'green'},
    ]

    create_summary_metrics_row(metrics, ThemeManager.get_metric_card_classes())

    ui.separator().classes('my-6')

    # Tone violations detail
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label('Tone Violations Detail').classes('text-xl font-bold mb-4')

        if tone_violations_list:
            # Count occurrences of each prohibited phrase
            from collections import Counter
            violation_counts = Counter(tone_violations_list)

            violation_data = []
            for phrase, count in violation_counts.most_common():
                violation_data.append({
                    'phrase': phrase,
                    'count': count
                })

            violations_df = pd.DataFrame(violation_data)

            create_data_table(
                data=violations_df,
                columns=[
                    {'name': 'phrase', 'label': 'Prohibited Phrase', 'field': 'phrase', 'align': 'left', 'sortable': True},
                    {'name': 'count', 'label': 'Occurrences', 'field': 'count', 'align': 'center', 'sortable': True},
                ],
                pagination=10,
                theme_classes=ThemeManager.get_table_classes()
            )
        else:
            ui.label('No tone violations found').classes('text-green-600 font-semibold')

    ui.separator().classes('my-6')

    # Blocked offers detail
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label('Blocked Offers Detail').classes('text-xl font-bold mb-4')

        if blocked_offers_list:
            # Show first 10 blocked offers
            display_count = min(10, len(blocked_offers_list))

            for i, offer in enumerate(blocked_offers_list[:display_count]):
                with ui.expansion(f"Blocked Offer {i+1}", icon='block').classes('w-full'):
                    ui.json_editor(offer).props('mode=view readonly').classes('w-full')

            if len(blocked_offers_list) > 10:
                ui.label(f'...and {len(blocked_offers_list) - 10} more blocked offers').classes('text-sm text-gray-600 mt-2')
        else:
            ui.label('No blocked offers').classes('text-green-600 font-semibold')

    ui.separator().classes('my-6')

    # Consent audit trail
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label('Recent Consent Changes').classes('text-xl font-bold mb-4')

        if users_df is not None and not users_df.empty:
            # Get users with recent consent changes
            consent_df = users_df[['user_id', 'name', 'consent_granted', 'consent_timestamp']].copy()
            consent_df = consent_df.dropna(subset=['consent_timestamp'])

            # Sort by timestamp descending and take top 10
            consent_df = consent_df.sort_values('consent_timestamp', ascending=False).head(10)

            # Format consent status
            consent_df['status'] = consent_df['consent_granted'].apply(lambda x: 'Granted' if x else 'Revoked')

            create_data_table(
                data=consent_df,
                columns=[
                    {'name': 'user_id', 'label': 'User ID', 'field': 'user_id', 'align': 'left'},
                    {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                    {'name': 'status', 'label': 'Consent Status', 'field': 'status', 'align': 'center'},
                    {'name': 'consent_timestamp', 'label': 'Timestamp', 'field': 'consent_timestamp', 'align': 'left'},
                ],
                pagination=10,
                theme_classes=ThemeManager.get_table_classes()
            )
        else:
            ui.label('No consent history available').classes('text-gray-500')


# =============================================================================
# TAB 7: DATA GENERATION (NEW)
# =============================================================================

@ui.refreshable
def render_data_generation_tab():
    """Render Data Generation tab with parameter controls."""
    with ui.card().classes(ThemeManager.get_card_classes()):
        ui.label('Data Generation Configuration').classes('text-xl font-bold mb-4')
        ui.label('Configure parameters and generate synthetic test data').classes('text-sm text-gray-600 mb-6')

        # Load current config
        current_config = load_config()

        # Parameter controls
        with ui.column().classes('gap-6 w-full'):
            # Seed
            with ui.row().classes('items-center gap-4 w-full'):
                ui.label('Random Seed:').classes('w-48 font-semibold')
                seed_slider = ui.slider(min=0, max=9999, value=current_config.get('seed', 42), step=1) \
                    .classes('flex-grow').props('label-always')
                seed_input = ui.number(value=current_config.get('seed', 42), min=0, max=9999) \
                    .classes('w-32').bind_value(seed_slider, 'value')

            # Num users
            with ui.row().classes('items-center gap-4 w-full'):
                ui.label('Number of Users:').classes('w-48 font-semibold')
                users_slider = ui.slider(min=10, max=1000, value=current_config.get('num_users', 100), step=10) \
                    .classes('flex-grow').props('label-always')
                users_input = ui.number(value=current_config.get('num_users', 100), min=10, max=1000) \
                    .classes('w-32').bind_value(users_slider, 'value')

            # Months history
            with ui.row().classes('items-center gap-4 w-full'):
                ui.label('Months of History:').classes('w-48 font-semibold')
                months_slider = ui.slider(min=1, max=24, value=current_config.get('months_history', 6), step=1) \
                    .classes('flex-grow').props('label-always')
                months_input = ui.number(value=current_config.get('months_history', 6), min=1, max=24) \
                    .classes('w-32').bind_value(months_slider, 'value')

            # Avg transactions
            with ui.row().classes('items-center gap-4 w-full'):
                ui.label('Avg Transactions/Month:').classes('w-48 font-semibold')
                trans_slider = ui.slider(min=10, max=100, value=current_config.get('avg_transactions_per_month', 30), step=5) \
                    .classes('flex-grow').props('label-always')
                trans_input = ui.number(value=current_config.get('avg_transactions_per_month', 30), min=10, max=100) \
                    .classes('w-32').bind_value(trans_slider, 'value')

        ui.separator().classes('my-6')

        # Preview section
        with ui.card().classes('bg-gray-50 p-4'):
            ui.label('Configuration Preview').classes('font-semibold mb-2')

            preview_config = {
                'seed': current_config.get('seed', 42),
                'num_users': current_config.get('num_users', 100),
                'months_history': current_config.get('months_history', 6),
                'avg_transactions_per_month': current_config.get('avg_transactions_per_month', 30),
            }

            config_preview = ui.json_editor(preview_config).props('mode=view readonly').classes('w-full h-48')

            def update_preview():
                """Update preview when sliders change."""
                new_config = {
                    'seed': int(seed_slider.value),
                    'num_users': int(users_slider.value),
                    'months_history': int(months_slider.value),
                    'avg_transactions_per_month': int(trans_slider.value),
                }
                config_preview.set_value(new_config)

            seed_slider.on_value_change(lambda: update_preview())
            users_slider.on_value_change(lambda: update_preview())
            months_slider.on_value_change(lambda: update_preview())
            trans_slider.on_value_change(lambda: update_preview())

            # Estimated data volume
            est_transactions = int(users_slider.value) * int(months_slider.value) * int(trans_slider.value)
            est_label = ui.label(f'Estimated transactions: {est_transactions:,}').classes('text-sm text-gray-600 mt-2')

            def update_estimate():
                est_count = int(users_slider.value) * int(months_slider.value) * int(trans_slider.value)
                est_label.set_text(f'Estimated transactions: {est_count:,}')

            users_slider.on_value_change(lambda: update_estimate())
            months_slider.on_value_change(lambda: update_estimate())
            trans_slider.on_value_change(lambda: update_estimate())

        ui.separator().classes('my-6')

        # Action buttons
        with ui.row().classes('gap-4'):
            async def generate_data():
                """Generate data with current parameters."""
                # Save config
                new_config = {
                    'seed': int(seed_slider.value),
                    'num_users': int(users_slider.value),
                    'months_history': int(months_slider.value),
                    'avg_transactions_per_month': int(trans_slider.value),
                    'generation_timestamp': datetime.now().isoformat(),
                }

                save_config(new_config)

                ui.notify('Starting data generation...', type='info')

                # Run data generator
                try:
                    process = await asyncio.create_subprocess_exec(
                        'uv', 'run', 'python', '-m', 'ingest.data_generator',
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )

                    stdout, stderr = await process.communicate()

                    if process.returncode == 0:
                        ui.notify('Data generation complete!', type='positive')
                        refresh_data()
                        render_overview_tab.refresh()
                    else:
                        ui.notify(f'Generation failed: {stderr.decode()}', type='negative')

                except Exception as e:
                    ui.notify(f'Error: {str(e)}', type='negative')

            ui.button('Generate Data', icon='play_arrow', on_click=generate_data) \
                .props('color=primary size=lg').classes(ThemeManager.get_button_classes())

            def reset_defaults():
                """Reset to default values."""
                seed_slider.value = 42
                users_slider.value = 100
                months_slider.value = 6
                trans_slider.value = 30

            ui.button('Reset to Defaults', icon='refresh', on_click=reset_defaults) \
                .props('flat').classes(ThemeManager.get_button_classes())

            def load_from_config():
                """Load from saved config."""
                config = load_config()
                seed_slider.value = config.get('seed', 42)
                users_slider.value = config.get('num_users', 100)
                months_slider.value = config.get('months_history', 6)
                trans_slider.value = config.get('avg_transactions_per_month', 30)
                ui.notify('Config loaded', type='positive')

            ui.button('Load from Config', icon='upload', on_click=load_from_config) \
                .props('flat').classes(ThemeManager.get_button_classes())


# =============================================================================
# MAIN PAGE
# =============================================================================

@ui.page('/')
async def main_page():
    """Main operator dashboard page."""
    # Initialize themes
    ThemeManager.initialize_themes()
    # Always use Clean & Minimal theme
    ThemeManager.set_theme(Theme.CLEAN_MINIMAL)
    ThemeManager.apply_theme(Theme.CLEAN_MINIMAL)

    # Initialize operator name from storage
    if 'operator_name' not in app.storage.user:
        app.storage.user['operator_name'] = ''

    # Always refresh data on page load to reflect external changes
    refresh_data()

    # Header
    with ui.header().classes('items-center justify-between px-6'):
        with ui.row().classes('items-center gap-4'):
            ui.icon('engineering').classes('text-3xl')
            with ui.column().classes('gap-0'):
                ui.label('SpendSense Operator Dashboard').classes('text-xl font-bold')
                ui.label('Compliance & Oversight Interface').classes('text-sm opacity-80')

        with ui.row().classes('items-center gap-4'):
            # Operator name input
            ui.input(label='Operator Name', placeholder='Your name') \
                .bind_value(app.storage.user, 'operator_name') \
                .props('outlined dense dark label-color=white input-class=text-white color=white clearable') \
                .classes('w-64')

            # Refresh button
            def handle_refresh():
                refresh_data()
                ui.notify('Data refreshed', type='positive')
                render_overview_tab.refresh()
                render_user_management_tab.refresh()
                render_behavioral_signals_tab.refresh()
                render_recommendation_review_tab.refresh()
                render_decision_trace_viewer_tab.refresh()
                render_guardrails_monitor_tab.refresh()
                render_data_generation_tab.refresh()

            ui.button(icon='refresh', on_click=handle_refresh).props('flat round')

    # Main content with tabs
    with ui.tabs().classes('w-full') as tabs:
        tab_overview = ui.tab('Overview', icon='dashboard')
        tab_users = ui.tab('Users', icon='people')
        tab_signals = ui.tab('Signals', icon='trending_up')
        tab_recommendations = ui.tab('Recommendations', icon='recommend')
        tab_traces = ui.tab('Traces', icon='timeline')
        tab_guardrails = ui.tab('Guardrails', icon='shield')
        tab_datagen = ui.tab('Data Generation', icon='build')

    with ui.tab_panels(tabs, value=tab_overview).classes('w-full p-6'):
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


# =============================================================================
# RUN APP
# =============================================================================

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='SpendSense Operator Dashboard',
        port=8081,
        reload=True,
        show=True,
        storage_secret='spendsense-operator-dashboard-secret-key-change-in-production'
    )

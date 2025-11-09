"""
SpendSense MVP V2 - NiceGUI User Dashboard

Educational interface for bank customers to view their financial behavioral
patterns and receive personalized educational recommendations.

Key Features:
- Consent onboarding with opt-in flow
- Personal dashboard showing active persona and detected patterns
- Glassmorphism persona transactions table
- Learning feed with personalized recommendations
- Privacy settings for consent management

Design Principles:
- Educational and supportive tone
- No shaming language
- Clear explanations with concrete data
- User control over data processing

Run with: uv run python ui/app_user_nicegui.py
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import sqlite3

from nicegui import ui, app

# Import utilities
from ui.utils.data_loaders import (
    load_all_users,
    DB_PATH,
    SIGNALS_PATH,
)

# Import recommendation engine
try:
    from recommend.engine import generate_recommendations
    RECOMMENDATIONS_AVAILABLE = True
except ImportError:
    RECOMMENDATIONS_AVAILABLE = False

# =============================================================================
# GLOBAL STATE
# =============================================================================

user_state = {
    "selected_user_id": None,
    "current_page": "dashboard",
}

# =============================================================================
# DATA LOADING FUNCTIONS
# =============================================================================


def load_user_data(user_id: str) -> Dict[str, Any]:
    """Load user demographics and consent status."""
    if not DB_PATH.exists():
        return {}

    with sqlite3.connect(DB_PATH) as conn:
        user_df = pd.read_sql("SELECT * FROM users WHERE user_id = ?", conn, params=(user_id,))

        if len(user_df) == 0:
            return {}

        user_data = user_df.iloc[0].to_dict()
        user_data["consent_granted"] = bool(user_data.get("consent_granted", False))

        return user_data


def load_persona_assignment(user_id: str) -> Optional[Dict[str, Any]]:
    """Load user's persona assignment."""
    if not DB_PATH.exists():
        return None

    with sqlite3.connect(DB_PATH) as conn:
        persona_df = pd.read_sql(
            "SELECT * FROM persona_assignments WHERE user_id = ? ORDER BY assigned_at DESC LIMIT 1",
            conn,
            params=(user_id,),
        )

        if len(persona_df) == 0:
            return None

        persona_data = persona_df.iloc[0].to_dict()
        if "criteria_met" in persona_data:
            try:
                import json
                persona_data["criteria_met"] = json.loads(persona_data["criteria_met"])
            except:
                persona_data["criteria_met"] = []

        return persona_data


def load_behavioral_signals(user_id: str) -> Dict[str, Any]:
    """Load user's behavioral signals from features/signals.parquet."""
    if not SIGNALS_PATH.exists():
        return {}

    signals_df = pd.read_parquet(SIGNALS_PATH)
    user_signals = signals_df[signals_df["user_id"] == user_id]

    if len(user_signals) == 0:
        return {}

    signals_dict = user_signals.iloc[0].to_dict()
    signals_dict.pop("user_id", None)

    return signals_dict


def load_persona_transactions(user_id: str, persona: str, limit: int = 10) -> pd.DataFrame:
    """
    Load transactions relevant to user's persona.

    Args:
        user_id: User identifier
        persona: Assigned persona name
        limit: Maximum number of transactions to return

    Returns:
        DataFrame with relevant transactions
    """
    if not DB_PATH.exists():
        return pd.DataFrame()

    with sqlite3.connect(DB_PATH) as conn:
        # Get user's accounts
        accounts_query = """
            SELECT account_id, account_type, account_subtype, name, mask
            FROM accounts
            WHERE user_id = ?
        """
        accounts_df = pd.read_sql(accounts_query, conn, params=(user_id,))

        if len(accounts_df) == 0:
            return pd.DataFrame()

        account_ids = accounts_df["account_id"].tolist()
        placeholders = ",".join(["?"] * len(account_ids))

        # Build query based on persona
        if persona == "High Utilization":
            # Show credit card transactions
            query = f"""
                SELECT t.*, a.account_subtype, a.name as account_name, a.mask
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.account_id IN ({placeholders})
                  AND a.account_type = 'credit'
                ORDER BY t.date DESC
                LIMIT ?
            """
            params = (*account_ids, limit)

        elif persona == "Subscription-Heavy":
            # Show recurring subscription transactions
            recurring_merchants = [
                "Netflix", "Spotify", "Amazon Prime", "Apple Music", "Hulu",
                "Disney+", "NYT Subscription", "WSJ", "LA Fitness", "Planet Fitness",
                "Adobe Creative Cloud", "Microsoft 365", "Dropbox", "LinkedIn Premium"
            ]
            merchant_conditions = " OR ".join(["t.merchant_name LIKE ?" for _ in recurring_merchants])
            query = f"""
                SELECT t.*, a.account_subtype, a.name as account_name, a.mask
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.account_id IN ({placeholders})
                  AND ({merchant_conditions})
                ORDER BY t.date DESC
                LIMIT ?
            """
            params = (*account_ids, *[f"%{m}%" for m in recurring_merchants], limit)

        elif persona == "Variable Income Budgeter":
            # Show income transactions (payroll)
            query = f"""
                SELECT t.*, a.account_subtype, a.name as account_name, a.mask
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.account_id IN ({placeholders})
                  AND (t.personal_finance_category = 'INCOME'
                       OR t.merchant_name LIKE '%Payroll%'
                       OR t.merchant_name LIKE '%Deposit%')
                ORDER BY t.date DESC
                LIMIT ?
            """
            params = (*account_ids, limit)

        elif persona == "Savings Builder":
            # Show savings-related transactions
            query = f"""
                SELECT t.*, a.account_subtype, a.name as account_name, a.mask
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.account_id IN ({placeholders})
                  AND (a.account_subtype = 'savings'
                       OR t.personal_finance_category = 'TRANSFER_IN')
                ORDER BY t.date DESC
                LIMIT ?
            """
            params = (*account_ids, limit)

        elif persona == "Cash Flow Optimizer":
            # Show recent spending transactions
            query = f"""
                SELECT t.*, a.account_subtype, a.name as account_name, a.mask
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.account_id IN ({placeholders})
                  AND t.amount > 0
                  AND t.personal_finance_category NOT IN ('INCOME', 'TRANSFER_IN')
                ORDER BY t.date DESC
                LIMIT ?
            """
            params = (*account_ids, limit)

        else:
            # General: Show all recent transactions
            query = f"""
                SELECT t.*, a.account_subtype, a.name as account_name, a.mask
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.account_id IN ({placeholders})
                ORDER BY t.date DESC
                LIMIT ?
            """
            params = (*account_ids, limit)

        transactions_df = pd.read_sql(query, conn, params=params)

    return transactions_df


def get_persona_description(persona: str) -> Dict[str, str]:
    """Get user-friendly description for each persona."""
    descriptions = {
        "High Utilization": {
            "title": "Credit Optimizer",
            "description": "You're focused on optimizing credit utilization and managing card balances effectively.",
            "icon": "💳",
            "color": "#FF6B6B",
        },
        "Variable Income Budgeter": {
            "title": "Flexible Budgeter",
            "description": "You're managing variable income with smart budgeting strategies.",
            "icon": "📊",
            "color": "#4ECDC4",
        },
        "Subscription-Heavy": {
            "title": "Subscription Manager",
            "description": "You're optimizing recurring expenses and subscription spending.",
            "icon": "🔄",
            "color": "#95E1D3",
        },
        "Cash Flow Optimizer": {
            "title": "Cash Flow Manager",
            "description": "You're focused on balancing spending with income and building financial reserves.",
            "icon": "💰",
            "color": "#FFA07A",
        },
        "Savings Builder": {
            "title": "Savings Champion",
            "description": "You're actively building savings and growing your financial cushion.",
            "icon": "🎯",
            "color": "#38B6FF",
        },
        "General": {
            "title": "Getting Started",
            "description": "We're learning about your financial patterns. Keep using your accounts to unlock personalized insights!",
            "icon": "🌱",
            "color": "#A8DADC",
        },
    }

    return descriptions.get(persona, descriptions["General"])


# =============================================================================
# UI COMPONENTS
# =============================================================================


def create_glassmorphism_persona_table(user_id: str, persona: str, persona_info: Dict[str, str]):
    """
    Create a beautiful glassmorphism table showing persona-related transactions.

    Args:
        user_id: User identifier
        persona: Assigned persona name
        persona_info: Persona metadata (color, icon, etc.)
    """
    transactions_df = load_persona_transactions(user_id, persona, limit=10)

    if len(transactions_df) == 0:
        ui.label("No relevant transactions found for this persona.").classes("text-gray-500 text-center p-4")
        return

    # Get persona-specific context
    persona_context = {
        "High Utilization": {
            "title": "Credit Card Transactions",
            "description": "Recent credit card charges contributing to your utilization",
        },
        "Subscription-Heavy": {
            "title": "Recurring Subscriptions",
            "description": "Monthly subscription services detected",
        },
        "Variable Income Budgeter": {
            "title": "Income Deposits",
            "description": "Recent paychecks and income sources",
        },
        "Savings Builder": {
            "title": "Savings Activity",
            "description": "Deposits and transfers to your savings accounts",
        },
        "Cash Flow Optimizer": {
            "title": "Recent Spending",
            "description": "Major expenses and spending patterns",
        },
        "General": {
            "title": "Recent Transactions",
            "description": "Your latest account activity",
        },
    }

    context = persona_context.get(persona, persona_context["General"])
    persona_color = persona_info.get("color", "#A8DADC")

    # Inject glassmorphism CSS
    ui.add_head_html(f"""
        <style>
        .persona-table-container {{
            background: linear-gradient(135deg,
                {persona_color}15 0%,
                {persona_color}08 100%);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            border: 1px solid {persona_color}40;
            padding: 24px;
            margin: 20px 0;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        }}

        .persona-table-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }}

        .persona-table-icon {{
            font-size: 28px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }}

        .persona-table-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #1a202c;
            margin: 0;
        }}

        .persona-table-description {{
            color: #4a5568;
            font-size: 0.95rem;
            margin-bottom: 20px;
            font-weight: 500;
        }}

        .transaction-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 0.9rem;
        }}

        .transaction-table thead {{
            background: linear-gradient(135deg, {persona_color}25, {persona_color}15);
            border-radius: 8px;
        }}

        .transaction-table th {{
            padding: 14px 16px;
            text-align: left;
            font-weight: 700;
            color: #2d3748;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.5px;
            border-bottom: 2px solid {persona_color}50;
        }}

        .transaction-table th:first-child {{
            border-top-left-radius: 8px;
        }}

        .transaction-table th:last-child {{
            border-top-right-radius: 8px;
        }}

        .transaction-table tbody tr {{
            transition: all 0.2s ease;
            background: rgba(255, 255, 255, 0.6);
            border-bottom: 1px solid {persona_color}20;
        }}

        .transaction-table tbody tr:hover {{
            background: {persona_color}20;
            transform: translateX(4px);
            box-shadow: -4px 0 0 0 {persona_color};
        }}

        .transaction-table td {{
            padding: 14px 16px;
            color: #2d3748;
        }}

        .transaction-date {{
            font-weight: 600;
            color: #4a5568;
            font-variant-numeric: tabular-nums;
        }}

        .transaction-merchant {{
            font-weight: 600;
            color: #1a202c;
        }}

        .transaction-category {{
            font-size: 0.8rem;
            color: #718096;
            background: {persona_color}20;
            padding: 4px 10px;
            border-radius: 12px;
            display: inline-block;
            font-weight: 500;
        }}

        .transaction-amount {{
            font-weight: 700;
            font-variant-numeric: tabular-nums;
            text-align: right;
        }}

        .transaction-amount.positive {{
            color: #38a169;
        }}

        .transaction-amount.negative {{
            color: #e53e3e;
        }}

        .transaction-account {{
            font-size: 0.85rem;
            color: #718096;
            font-family: 'Monaco', 'Menlo', monospace;
        }}
        </style>
    """)

    # Build table HTML
    table_rows = []
    for _, row in transactions_df.iterrows():
        date_str = pd.to_datetime(row["date"]).strftime("%b %d, %Y")
        merchant = row["merchant_name"]
        category = row["personal_finance_category"].replace("_", " ").title()
        amount = row["amount"]
        account = f"{row['account_name']} (••{row['mask']})"

        # Format amount with proper sign
        if amount < 0:
            amount_display = f"+${abs(amount):,.2f}"
            amount_class = "positive"
        else:
            amount_display = f"-${amount:,.2f}"
            amount_class = "negative"

        table_rows.append(f"""
            <tr>
                <td><span class="transaction-date">{date_str}</span></td>
                <td><span class="transaction-merchant">{merchant}</span></td>
                <td><span class="transaction-category">{category}</span></td>
                <td><span class="transaction-amount {amount_class}">{amount_display}</span></td>
                <td><span class="transaction-account">{account}</span></td>
            </tr>
        """)

    table_html = f"""
    <div class="persona-table-container">
        <div class="persona-table-header">
            <div class="persona-table-icon">{persona_info.get('icon', '💳')}</div>
            <h3 class="persona-table-title">{context['title']}</h3>
        </div>
        <p class="persona-table-description">{context['description']}</p>

        <table class="transaction-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Merchant</th>
                    <th>Category</th>
                    <th style="text-align: right;">Amount</th>
                    <th>Account</th>
                </tr>
            </thead>
            <tbody>
                {"".join(table_rows)}
            </tbody>
        </table>
    </div>
    """

    ui.html(table_html)


def create_dashboard_page(user_id: str):
    """Create the main dashboard page."""
    user_data = load_user_data(user_id)
    persona_data = load_persona_assignment(user_id)
    signals = load_behavioral_signals(user_id)

    if not user_data.get("consent_granted", False):
        with ui.card().classes("w-full p-6"):
            ui.label("Welcome! Please grant consent to see your personalized dashboard.").classes("text-lg font-bold mb-4")
            ui.label("To enable personalized insights, grant consent in the Privacy tab.").classes("text-gray-600")
        return

    # Dashboard header
    ui.label("🏠 Your Financial Dashboard").classes("text-3xl font-bold mb-6")

    # Persona section
    if persona_data:
        persona = persona_data.get("persona", "General")
        persona_info = get_persona_description(persona)

        with ui.card().classes("w-full p-6 mb-6"):
            ui.label(f"{persona_info['icon']} Your Financial Profile: {persona_info['title']}").classes("text-2xl font-bold mb-2")
            ui.label(persona_info['description']).classes("text-lg text-gray-700 mb-4")

            # Show criteria met
            if persona_data.get("criteria_met"):
                with ui.expansion("📋 Why this profile?").classes("w-full"):
                    ui.label("Key patterns detected:").classes("font-bold mb-2")
                    for criterion in persona_data.get("criteria_met", []):
                        ui.label(f"• {criterion}").classes("text-gray-700")

        # Glassmorphism persona transactions table
        create_glassmorphism_persona_table(user_id, persona, persona_info)
    else:
        with ui.card().classes("w-full p-6"):
            ui.label("No persona assigned yet.").classes("text-lg font-bold text-yellow-600")
            ui.label("We need more data to understand your financial patterns.").classes("text-gray-600")

    # Behavioral signals metrics
    ui.label("📊 Your Financial Patterns").classes("text-2xl font-bold mt-8 mb-4")

    with ui.row().classes("w-full gap-4"):
        # Credit metrics
        with ui.card().classes("flex-1 p-4"):
            ui.label("Credit Cards").classes("text-sm text-gray-600 mb-1")
            ui.label(str(int(signals.get("credit_num_cards", 0)))).classes("text-3xl font-bold")
            if signals.get("credit_avg_util_pct"):
                ui.label(f"Avg Utilization: {signals.get('credit_avg_util_pct', 0):.1f}%").classes("text-sm text-gray-600 mt-2")

        # Subscription metrics
        with ui.card().classes("flex-1 p-4"):
            ui.label("Recurring Services").classes("text-sm text-gray-600 mb-1")
            ui.label(str(int(signals.get("sub_180d_recurring_count", 0)))).classes("text-3xl font-bold")
            if signals.get("sub_180d_monthly_spend"):
                ui.label(f"Monthly: ${signals.get('sub_180d_monthly_spend', 0):,.2f}").classes("text-sm text-gray-600 mt-2")

        # Savings metrics
        with ui.card().classes("flex-1 p-4"):
            ui.label("Savings Growth (6mo)").classes("text-sm text-gray-600 mb-1")
            if signals.get("sav_180d_net_inflow") is not None:
                ui.label(f"${signals.get('sav_180d_net_inflow', 0):,.2f}").classes("text-3xl font-bold")
            else:
                ui.label("N/A").classes("text-3xl font-bold text-gray-400")

        # Income metrics
        with ui.card().classes("flex-1 p-4"):
            ui.label("Typical Pay Gap").classes("text-sm text-gray-600 mb-1")
            if signals.get("inc_180d_median_pay_gap_days"):
                ui.label(f"{int(signals.get('inc_180d_median_pay_gap_days', 0))} days").classes("text-3xl font-bold")
            else:
                ui.label("N/A").classes("text-3xl font-bold text-gray-400")


def create_privacy_page(user_id: str):
    """Create privacy and consent settings page."""
    user_data = load_user_data(user_id)

    ui.label("🔒 Privacy & Consent Settings").classes("text-3xl font-bold mb-6")

    with ui.card().classes("w-full p-6 mb-6"):
        ui.label("Your Data, Your Control").classes("text-2xl font-bold mb-4")
        ui.label("SpendSense respects your privacy and puts you in control of your financial data.").classes("text-gray-700")

    # Current status
    ui.label("📋 Current Status").classes("text-2xl font-bold mb-4")

    consent_granted = user_data.get("consent_granted", False)

    with ui.row().classes("w-full gap-4 mb-6"):
        with ui.card().classes("flex-1 p-4"):
            ui.label("Consent Status").classes("text-sm text-gray-600 mb-1")
            ui.label("✅ Active" if consent_granted else "⏸️ Not Granted").classes("text-2xl font-bold")
            if consent_granted and user_data.get("consent_timestamp"):
                ui.label(f"Granted: {user_data.get('consent_timestamp', 'Unknown')[:10]}").classes("text-sm text-gray-600 mt-2")

        with ui.card().classes("flex-1 p-4"):
            ui.label("Data Processing").classes("text-sm text-gray-600 mb-1")
            ui.label("Enabled" if consent_granted else "Disabled").classes("text-2xl font-bold")

    # Consent management
    ui.label("⚙️ Manage Consent").classes("text-2xl font-bold mb-4")

    async def toggle_consent():
        if consent_granted:
            # Revoke consent
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "UPDATE users SET consent_granted = 0, revoked_timestamp = ? WHERE user_id = ?",
                    (datetime.now().isoformat(), user_id),
                )
                conn.commit()
            ui.notify("Consent revoked. All processing has stopped.", type="positive")
        else:
            # Grant consent
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "UPDATE users SET consent_granted = 1, consent_timestamp = ? WHERE user_id = ?",
                    (datetime.now().isoformat(), user_id),
                )
                conn.commit()
            ui.notify("Consent granted! Loading your dashboard...", type="positive")

        await asyncio.sleep(0.5)
        ui.navigate.reload()

    if consent_granted:
        with ui.card().classes("w-full p-6 bg-green-50 mb-4"):
            ui.label("✅ You've granted consent for data processing.").classes("text-lg font-bold text-green-700 mb-4")
            ui.label("What this means:").classes("font-bold mb-2")
            ui.label("• We analyze your transaction data to detect behavioral patterns").classes("text-gray-700")
            ui.label("• We generate personalized educational content based on your profile").classes("text-gray-700")
            ui.label("• We suggest partner offers that may be relevant to your situation").classes("text-gray-700 mb-4")
            ui.label("You can revoke consent at any time. All data processing will stop immediately.").classes("text-gray-700")

        with ui.card().classes("w-full p-6 bg-yellow-50"):
            ui.label("⚠️ Revoke Consent").classes("text-lg font-bold text-yellow-700 mb-4")
            ui.label("Revoking consent will:").classes("font-bold mb-2")
            ui.label("• Stop all data processing immediately").classes("text-gray-700")
            ui.label("• Clear your recommendations and insights").classes("text-gray-700")
            ui.label("• Preserve your transaction data (no deletion)").classes("text-gray-700")
            ui.label("• Allow you to opt back in at any time").classes("text-gray-700 mb-4")

            ui.button("🚫 Revoke My Consent", on_click=toggle_consent).classes("bg-red-500 text-white")
    else:
        with ui.card().classes("w-full p-6 bg-blue-50 mb-4"):
            ui.label("⏸️ You have not granted consent for data processing.").classes("text-lg font-bold text-blue-700 mb-4")
            ui.label("To enable personalized insights:").classes("font-bold mb-2")
            ui.label("• Grant consent below").classes("text-gray-700")
            ui.label("• We'll analyze your transaction patterns").classes("text-gray-700")
            ui.label("• You'll receive educational content tailored to your profile").classes("text-gray-700 mb-4")
            ui.label("You remain in control and can revoke at any time.").classes("text-gray-700")

        ui.button("✅ Grant Consent", on_click=toggle_consent).classes("bg-green-500 text-white")


# =============================================================================
# MAIN APP
# =============================================================================


@ui.page("/")
async def main_page():
    """Main application page."""

    # Load users
    users_df = load_all_users()

    if len(users_df) == 0:
        with ui.card().classes("w-full p-6"):
            ui.label("No users found. Please run data generation first.").classes("text-lg font-bold text-red-600")
        return

    # Header with user selection
    with ui.header().classes("items-center justify-between bg-blue-600 text-white px-6 py-4"):
        ui.label("SpendSense").classes("text-2xl font-bold")

        # User selector
        user_options = [
            f"{row['user_id']} - {row['name']}" + (" ✅" if row["consent_granted"] else " ⏸️")
            for _, row in users_df.iterrows()
        ]

        selected_idx = ui.select(
            user_options,
            label="Select User",
            value=user_options[0],
            on_change=lambda e: handle_user_change(e.value, users_df, user_options)
        ).classes("w-64 text-black bg-white rounded")

    # Set initial user
    if user_state["selected_user_id"] is None:
        user_state["selected_user_id"] = users_df.iloc[0]["user_id"]

    # Navigation tabs
    with ui.tabs().classes("w-full bg-gray-100") as tabs:
        dashboard_tab = ui.tab("🏠 Dashboard", "dashboard")
        privacy_tab = ui.tab("🔒 Privacy", "privacy")

    # Tab panels
    with ui.tab_panels(tabs, value=user_state["current_page"]).classes("w-full p-6"):
        with ui.tab_panel("dashboard"):
            create_dashboard_page(user_state["selected_user_id"])

        with ui.tab_panel("privacy"):
            create_privacy_page(user_state["selected_user_id"])

    # Footer
    with ui.footer().classes("bg-gray-200 text-gray-700 px-6 py-4 text-center"):
        ui.label("Disclaimer: Educational content only, not financial advice.").classes("text-sm")


def handle_user_change(selected_option: str, users_df: pd.DataFrame, user_options: list):
    """Handle user selection change."""
    selected_idx = user_options.index(selected_option)
    user_state["selected_user_id"] = users_df.iloc[selected_idx]["user_id"]
    ui.navigate.reload()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="SpendSense - User Dashboard",
        favicon="🎯",
        port=8081,
        reload=True,
        show=True,
    )

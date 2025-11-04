"""
SpendSense MVP V2 - End User Dashboard

Educational interface for bank customers to view their financial behavioral
patterns and receive personalized educational recommendations.

Key Features:
- Consent onboarding with opt-in flow
- Personal dashboard showing active persona and detected patterns
- Learning feed with personalized recommendations
- Privacy settings for consent management

Design Principles:
- Educational and supportive tone
- No shaming language
- Clear explanations with concrete data
- User control over data processing
"""

import streamlit as st
import sqlite3
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Configure Streamlit page
st.set_page_config(
    page_title="SpendSense - Your Financial Learning Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Resolve project root relative to this file so paths are stable regardless of CWD
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Database and data paths
DB_PATH = PROJECT_ROOT / "data" / "users.sqlite"
SIGNALS_PATH = PROJECT_ROOT / "features" / "signals.parquet"
TRACES_DIR = PROJECT_ROOT / "docs" / "traces"

# Import recommendation engine
try:
    from recommend.engine import generate_recommendations
except ImportError:
    generate_recommendations = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def load_all_users() -> pd.DataFrame:
    """Load all users from database."""
    if not DB_PATH.exists():
        return pd.DataFrame()

    with sqlite3.connect(DB_PATH) as conn:
        users_df = pd.read_sql(
            "SELECT user_id, name, consent_granted FROM users ORDER BY user_id", conn
        )
    return users_df


def load_user_data(user_id: str) -> Dict[str, Any]:
    """Load user demographics and consent status."""
    with sqlite3.connect(DB_PATH) as conn:
        user_df = pd.read_sql("SELECT * FROM users WHERE user_id = ?", conn, params=(user_id,))

        if len(user_df) == 0:
            return {}

        user_data = user_df.iloc[0].to_dict()
        user_data["consent_granted"] = bool(user_data.get("consent_granted", False))

        return user_data


def load_persona_assignment(user_id: str) -> Optional[Dict[str, Any]]:
    """Load user's persona assignment."""
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


def grant_consent(user_id: str) -> bool:
    """Grant consent for a user."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "UPDATE users SET consent_granted = 1, consent_timestamp = ? WHERE user_id = ?",
                (datetime.now().isoformat(), user_id),
            )
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Error granting consent: {e}")
        return False


def revoke_consent(user_id: str) -> bool:
    """Revoke consent for a user."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "UPDATE users SET consent_granted = 0, revoked_timestamp = ? WHERE user_id = ?",
                (datetime.now().isoformat(), user_id),
            )
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Error revoking consent: {e}")
        return False


def get_persona_description(persona: str) -> Dict[str, str]:
    """Get user-friendly description for each persona."""
    descriptions = {
        "high_utilization": {
            "title": "Credit Optimizer",
            "description": "You're focused on optimizing credit utilization and managing card balances effectively.",
            "icon": "💳",
            "color": "#FF6B6B",
        },
        "variable_income": {
            "title": "Flexible Budgeter",
            "description": "You're managing variable income with smart budgeting strategies.",
            "icon": "📊",
            "color": "#4ECDC4",
        },
        "subscription_heavy": {
            "title": "Subscription Manager",
            "description": "You're optimizing recurring expenses and subscription spending.",
            "icon": "🔄",
            "color": "#95E1D3",
        },
        "savings_builder": {
            "title": "Savings Champion",
            "description": "You're actively building savings and growing your financial cushion.",
            "icon": "🎯",
            "color": "#38B6FF",
        },
        "general": {
            "title": "Getting Started",
            "description": "We're learning about your financial patterns. Keep using your accounts to unlock personalized insights!",
            "icon": "🌱",
            "color": "#A8DADC",
        },
    }

    return descriptions.get(persona, descriptions["general"])


def format_currency(amount: float) -> str:
    """Format number as currency."""
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format number as percentage."""
    return f"{value:.1f}%"


# =============================================================================
# UI COMPONENTS
# =============================================================================


def render_consent_banner(user_id: str):
    """Render consent banner for users who haven't opted in."""
    st.warning("⚠️ **Consent Required**")

    st.markdown(
        """
    ### Welcome to SpendSense!

    To provide you with personalized financial education and insights, we need your consent to analyze your transaction data.

    **What we do:**
    - Detect spending patterns (subscriptions, savings, credit usage, income stability)
    - Assign you to an educational persona based on your behaviors
    - Provide personalized learning content and partner offers

    **What we don't do:**
    - Provide financial advice (this is educational content only)
    - Share your data with third parties without permission
    - Make decisions about your accounts

    **Your data rights:**
    - You can revoke consent at any time
    - All processing stops immediately upon revocation
    - Your data is stored securely and used only for generating insights
    """
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("✅ I Consent - Let's Get Started!", type="primary", use_container_width=True):
            if grant_consent(user_id):
                st.success("✅ Consent granted! Refreshing your dashboard...")
                st.rerun()


def render_sidebar():
    """Render sidebar with user selection and navigation."""
    with st.sidebar:
        st.title("💰 SpendSense")
        st.markdown("### Your Financial Learning Dashboard")

        st.divider()

        # User selection
        st.subheader("Select User")
        users_df = load_all_users()

        if len(users_df) == 0:
            st.error("No users found. Please run data generation first.")
            st.stop()

        # Format user options
        user_options = [
            f"{row['user_id']} - {row['name']}" + (" ✅" if row["consent_granted"] else " ⏸️")
            for _, row in users_df.iterrows()
        ]

        selected_idx = st.selectbox(
            "Choose a user profile:",
            range(len(user_options)),
            format_func=lambda i: user_options[i],
            key="user_selector",
        )

        selected_user_id = users_df.iloc[selected_idx]["user_id"]

        st.divider()

        # Navigation
        st.subheader("Navigation")
        page = st.radio(
            "Go to:", ["🏠 Dashboard", "📚 Learning Feed", "🔒 Privacy Settings"], key="navigation"
        )

        st.divider()

        # Disclaimer
        st.caption(
            "**Disclaimer:** This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."
        )

        return selected_user_id, page


def render_dashboard(
    user_id: str,
    user_data: Dict[str, Any],
    persona_data: Optional[Dict[str, Any]],
    signals: Dict[str, Any],
):
    """Render main dashboard page."""
    st.title("🏠 Your Financial Dashboard")

    # Get recommendations
    if generate_recommendations is None:
        st.error("Recommendation engine not available. Please check your installation.")
        return

    # Check consent
    if not user_data.get("consent_granted", False):
        st.info("👋 Welcome! To see your personalized dashboard, please grant consent below.")
        render_consent_banner(user_id)
        return

    # Refresh button
    col1, col2, col3 = st.columns([3, 1, 1])
    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.divider()

    # Persona section
    if persona_data:
        persona = persona_data.get("persona", "general")
        persona_info = get_persona_description(persona)

        st.markdown(f"## {persona_info['icon']} Your Financial Profile: {persona_info['title']}")
        st.markdown(f"**{persona_info['description']}**")

        # Show criteria met
        if persona_data.get("criteria_met"):
            with st.expander("📋 Why this profile?"):
                st.markdown("**Key patterns detected:**")
                for criterion in persona_data.get("criteria_met", []):
                    st.markdown(f"- {criterion}")
    else:
        st.warning(
            "No persona assigned yet. We need more data to understand your financial patterns."
        )

    st.divider()

    # Behavioral signals overview
    st.markdown("## 📊 Your Financial Patterns")

    col1, col2, col3, col4 = st.columns(4)

    # Credit metrics
    with col1:
        st.metric(
            label="Credit Cards",
            value=int(signals.get("credit_num_cards", 0)),
            help="Number of credit card accounts",
        )
        if signals.get("credit_avg_util_pct"):
            st.metric(
                label="Avg Utilization",
                value=format_percentage(signals.get("credit_avg_util_pct", 0)),
                help="Average credit utilization across all cards",
            )

    # Subscription metrics
    with col2:
        st.metric(
            label="Recurring Services",
            value=int(signals.get("sub_180d_recurring_count", 0)),
            help="Number of detected recurring subscriptions (180-day window)",
        )
        if signals.get("sub_180d_monthly_spend"):
            st.metric(
                label="Monthly Recurring",
                value=format_currency(signals.get("sub_180d_monthly_spend", 0)),
                help="Estimated monthly recurring spend",
            )

    # Savings metrics
    with col3:
        if signals.get("sav_180d_net_inflow") is not None:
            st.metric(
                label="Savings Growth (6mo)",
                value=format_currency(signals.get("sav_180d_net_inflow", 0)),
                help="Net inflow to savings accounts (180-day window)",
            )
        if signals.get("sav_180d_emergency_fund_months"):
            st.metric(
                label="Emergency Fund",
                value=f"{signals.get('sav_180d_emergency_fund_months', 0):.1f} mo",
                help="Months of expenses covered by savings",
            )

    # Income metrics
    with col4:
        if signals.get("inc_180d_median_pay_gap_days"):
            st.metric(
                label="Typical Pay Gap",
                value=f"{int(signals.get('inc_180d_median_pay_gap_days', 0))} days",
                help="Median days between paychecks (180-day window)",
            )
        if signals.get("inc_180d_cash_buffer_months"):
            st.metric(
                label="Cash Buffer",
                value=f"{signals.get('inc_180d_cash_buffer_months', 0):.1f} mo",
                help="Months of expenses available in checking",
            )

    st.divider()

    # Top recommendations preview
    st.markdown("## 💡 Top Recommendations for You")

    try:
        recommendations = generate_recommendations(user_id)

        if recommendations.get("recommendations"):
            recs = recommendations["recommendations"][:3]  # Show top 3

            for rec in recs:
                with st.container():
                    st.markdown(f"### {rec['title']}")
                    st.markdown(f"**{rec.get('description', '')}**")
                    st.info(f"**Why this matters:** {rec['rationale']}")
                    st.caption(rec.get("disclaimer", ""))
                    st.divider()

            if len(recommendations["recommendations"]) > 3:
                st.info(
                    f"💡 **{len(recommendations['recommendations']) - 3} more recommendations** available in the Learning Feed!"
                )
        else:
            reason = recommendations.get("metadata", {}).get("reason", "unknown")
            if reason == "general_persona_no_recommendations":
                st.info(
                    "🌱 **Getting to know you...** Keep using your accounts and we'll provide personalized recommendations soon!"
                )
            else:
                st.warning("No recommendations available at this time.")

    except Exception as e:
        st.error(f"Error loading recommendations: {e}")


def render_learning_feed(user_id: str, user_data: Dict[str, Any]):
    """Render learning feed with all recommendations."""
    st.title("📚 Your Learning Feed")

    # Check consent
    if not user_data.get("consent_granted", False):
        st.info("👋 To see your personalized learning feed, please grant consent below.")
        render_consent_banner(user_id)
        return

    # Refresh button
    col1, col2, col3 = st.columns([3, 1, 1])
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")

    try:
        recommendations = generate_recommendations(user_id)

        if not recommendations.get("recommendations"):
            reason = recommendations.get("metadata", {}).get("reason", "unknown")
            if reason == "general_persona_no_recommendations":
                st.info(
                    "🌱 **Getting to know you...** We're still learning about your financial patterns. Keep using your accounts and personalized content will appear here soon!"
                )
            elif reason == "insufficient_data":
                shortfall = recommendations.get("metadata", {}).get(
                    "education_eligibility_shortfall", 0
                )
                st.warning(
                    f"📊 **Limited data available.** We need more transaction history to provide {shortfall} additional personalized recommendations."
                )
            else:
                st.warning("No recommendations available at this time.")
            return

        # Separate education and offers
        education_items = [
            r for r in recommendations["recommendations"] if r["type"] == "education"
        ]
        partner_offers = [
            r for r in recommendations["recommendations"] if r["type"] == "partner_offer"
        ]

        # Education section
        if education_items:
            st.markdown("## 📖 Educational Content")
            st.markdown("*Learn strategies to improve your financial health*")
            st.markdown("---")

            for idx, rec in enumerate(education_items, 1):
                with st.container():
                    col1, col2 = st.columns([1, 20])
                    with col1:
                        st.markdown(f"### {idx}")
                    with col2:
                        st.markdown(f"### {rec['title']}")
                        st.markdown(f"**{rec.get('description', '')}**")
                        st.info(f"**Why this matters to you:** {rec['rationale']}")

                        # Category tag
                        category = rec.get("category", "general").replace("_", " ").title()
                        st.caption(f"📂 Category: {category}")

                        st.caption(f"⚖️ {rec.get('disclaimer', '')}")

                    st.markdown("---")

        # Partner offers section
        if partner_offers:
            st.markdown("## 🤝 Partner Offers")
            st.markdown("*Products and services that may help based on your profile*")
            st.markdown("---")

            for idx, rec in enumerate(partner_offers, 1):
                with st.container():
                    col1, col2 = st.columns([1, 20])
                    with col1:
                        st.markdown(f"### {idx}")
                    with col2:
                        st.markdown(f"### {rec['title']}")
                        st.markdown(f"**{rec.get('description', '')}**")
                        st.success(f"**Why we're suggesting this:** {rec['rationale']}")

                        # Category tag
                        category = rec.get("category", "general").replace("_", " ").title()
                        st.caption(f"📂 Category: {category}")

                        st.caption(f"⚖️ {rec.get('disclaimer', '')}")

                    st.markdown("---")

        # Metadata
        with st.expander("ℹ️ About these recommendations"):
            metadata = recommendations.get("metadata", {})
            st.markdown(f"**Generated:** {metadata.get('timestamp', 'Unknown')}")
            st.markdown(f"**Education items:** {metadata.get('education_count', 0)}")
            st.markdown(f"**Partner offers:** {metadata.get('offer_count', 0)}")
            st.markdown(
                f"**Tone check:** {'✅ Passed' if metadata.get('tone_check_passed', True) else '⚠️ Flagged for review'}"
            )

    except Exception as e:
        st.error(f"Error loading learning feed: {e}")
        st.exception(e)


def render_privacy_settings(user_id: str, user_data: Dict[str, Any]):
    """Render privacy and consent settings page."""
    st.title("🔒 Privacy & Consent Settings")

    st.markdown(
        """
    ### Your Data, Your Control

    SpendSense respects your privacy and puts you in control of your financial data.
    """
    )

    st.divider()

    # Current consent status
    st.markdown("## 📋 Current Status")

    consent_granted = user_data.get("consent_granted", False)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Consent Status", value="✅ Active" if consent_granted else "⏸️ Not Granted")

        if consent_granted and user_data.get("consent_timestamp"):
            st.caption(f"Granted: {user_data.get('consent_timestamp', 'Unknown')[:10]}")

        if not consent_granted and user_data.get("revoked_timestamp"):
            st.caption(f"Revoked: {user_data.get('revoked_timestamp', 'Unknown')[:10]}")

    with col2:
        st.metric(label="Data Processing", value="Enabled" if consent_granted else "Disabled")

    st.divider()

    # Consent management
    st.markdown("## ⚙️ Manage Consent")

    if consent_granted:
        st.success("✅ You've granted consent for data processing.")

        st.markdown(
            """
        **What this means:**
        - We analyze your transaction data to detect behavioral patterns
        - We generate personalized educational content based on your profile
        - We suggest partner offers that may be relevant to your situation

        **You can revoke consent at any time.** All data processing will stop immediately.
        """
        )

        st.warning("⚠️ **Revoke Consent**")
        st.markdown("Revoking consent will:")
        st.markdown("- Stop all data processing immediately")
        st.markdown("- Clear your recommendations and insights")
        st.markdown("- Preserve your transaction data (no deletion)")
        st.markdown("- Allow you to opt back in at any time")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚫 Revoke My Consent", type="secondary", use_container_width=True):
                if revoke_consent(user_id):
                    st.success("✅ Consent revoked. All processing has stopped.")
                    st.rerun()
    else:
        st.warning("⏸️ You have not granted consent for data processing.")

        st.markdown(
            """
        **To enable personalized insights:**
        - Grant consent below
        - We'll analyze your transaction patterns
        - You'll receive educational content tailored to your profile

        **You remain in control** and can revoke at any time.
        """
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ Grant Consent", type="primary", use_container_width=True):
                if grant_consent(user_id):
                    st.success("✅ Consent granted! Loading your dashboard...")
                    st.rerun()

    st.divider()

    # Data export (coming soon)
    st.markdown("## 📥 Export Your Data")

    st.info(
        """
    **Coming Soon:** Download your complete data package including:
    - Transaction history
    - Detected behavioral patterns
    - Persona assignments
    - Recommendation history
    - Decision trace logs
    """
    )

    st.button("📦 Export My Data", disabled=True, help="This feature is coming soon!")

    st.divider()

    # Privacy info
    with st.expander("ℹ️ How We Protect Your Privacy"):
        st.markdown(
            """
        ### Data Security

        - **Local Storage:** All data is stored locally in SQLite and Parquet files
        - **No External APIs:** We don't send your data to third parties
        - **Synthetic Data:** This demo uses synthetic transaction data
        - **Encrypted:** Production systems use encryption at rest and in transit

        ### What We Collect

        - Transaction data (amounts, dates, merchants, categories)
        - Account information (balances, types, limits)
        - Behavioral signals (computed metrics, not raw transactions)

        ### What We Don't Do

        - Provide financial advice (educational content only)
        - Make account decisions on your behalf
        - Share data without explicit permission
        - Store sensitive authentication credentials

        ### Your Rights

        - **Access:** View all data we've collected about you
        - **Control:** Grant or revoke consent at any time
        - **Export:** Download your complete data package (coming soon)
        - **Transparency:** Access decision traces explaining all recommendations
        """
        )


# =============================================================================
# MAIN APP
# =============================================================================


def main():
    """Main application entry point."""

    # Render sidebar and get user selection
    selected_user_id, page = render_sidebar()

    # Load user data
    user_data = load_user_data(selected_user_id)

    if not user_data:
        st.error(f"User {selected_user_id} not found in database.")
        st.stop()

    # Load persona and signals
    persona_data = load_persona_assignment(selected_user_id)
    signals = load_behavioral_signals(selected_user_id)

    # Route to appropriate page
    if page == "🏠 Dashboard":
        render_dashboard(selected_user_id, user_data, persona_data, signals)
    elif page == "📚 Learning Feed":
        render_learning_feed(selected_user_id, user_data)
    elif page == "🔒 Privacy Settings":
        render_privacy_settings(selected_user_id, user_data)


if __name__ == "__main__":
    main()

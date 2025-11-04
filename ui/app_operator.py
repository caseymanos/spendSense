"""
SpendSense MVP V2 - Operator Dashboard

Compliance and oversight interface for analysts and compliance team to:
- Monitor user consent and persona distribution
- Review behavioral signals and recommendations
- Approve/override/flag recommendations
- Inspect decision traces for auditability
- Monitor guardrail enforcement

Key Features:
- Overview tab with system health metrics
- User management with filtering by consent, persona, demographics
- Behavioral signals visualization with charts
- Recommendation review with approve/override/flag workflow
- Decision trace viewer for full audit trail
- Guardrails monitoring for compliance checks

Design Principles:
- Analytical and auditable
- Full transparency into system decisions
- Operator control for manual oversight
- Compliance-focused metrics and reports
"""

import streamlit as st
import sqlite3
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Configure Streamlit page
st.set_page_config(
    page_title="SpendSense - Operator Dashboard",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Database and data paths
DB_PATH = Path("data/users.sqlite")
SIGNALS_PATH = Path("features/signals.parquet")
TRANSACTIONS_PATH = Path("data/transactions.parquet")
TRACES_DIR = Path("docs/traces")
DECISION_LOG_PATH = Path("docs/decision_log.md")

# Import modules
try:
    from guardrails.consent import get_consent_history, batch_grant_consent, check_consent
    from guardrails.tone import scan_recommendations, validate_tone
    from guardrails.eligibility import get_eligibility_summary
    from recommend.engine import generate_recommendations
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    st.error(f"Module import error: {e}")


# =============================================================================
# HELPER FUNCTIONS - DATA LOADING
# =============================================================================


def load_all_users() -> pd.DataFrame:
    """Load all users with consent, persona, and demographic information."""
    if not DB_PATH.exists():
        return pd.DataFrame()

    with sqlite3.connect(DB_PATH) as conn:
        # Join users with their most recent persona assignment
        query = """
        SELECT
            u.user_id,
            u.name,
            u.consent_granted,
            u.consent_timestamp,
            u.revoked_timestamp,
            u.age,
            u.gender,
            u.income_tier,
            u.region,
            p.persona,
            p.assigned_at as persona_assigned_at
        FROM users u
        LEFT JOIN persona_assignments p ON u.user_id = p.user_id
        WHERE p.assignment_id IN (
            SELECT MAX(assignment_id)
            FROM persona_assignments
            GROUP BY user_id
        ) OR p.assignment_id IS NULL
        ORDER BY u.user_id
        """
        users_df = pd.read_sql(query, conn)
        users_df["consent_granted"] = users_df["consent_granted"].astype(bool)

    return users_df


def load_all_signals() -> pd.DataFrame:
    """Load all behavioral signals from parquet file."""
    if not SIGNALS_PATH.exists():
        return pd.DataFrame()

    signals_df = pd.read_parquet(SIGNALS_PATH)
    return signals_df


def load_user_trace(user_id: str) -> Optional[Dict[str, Any]]:
    """Load decision trace JSON for a specific user."""
    trace_file = TRACES_DIR / f"{user_id}.json"

    if not trace_file.exists():
        return None

    try:
        with open(trace_file, "r") as f:
            trace_data = json.load(f)
        return trace_data
    except Exception as e:
        st.error(f"Error loading trace for {user_id}: {e}")
        return None


def load_persona_distribution() -> Dict[str, int]:
    """Calculate persona distribution across all users."""
    if not DB_PATH.exists():
        return {}

    with sqlite3.connect(DB_PATH) as conn:
        query = """
        SELECT persona, COUNT(*) as count
        FROM persona_assignments
        WHERE assignment_id IN (
            SELECT MAX(assignment_id)
            FROM persona_assignments
            GROUP BY user_id
        )
        GROUP BY persona
        ORDER BY count DESC
        """
        df = pd.read_sql(query, conn)

    return dict(zip(df["persona"], df["count"]))


def load_guardrail_summary() -> Dict[str, Any]:
    """Aggregate guardrail decisions across all users."""
    summary = {
        "total_users": 0,
        "users_with_consent": 0,
        "tone_violations": [],
        "blocked_offers": [],
        "total_recommendations": 0,
    }

    if not TRACES_DIR.exists():
        return summary

    trace_files = list(TRACES_DIR.glob("*.json"))
    summary["total_users"] = len(trace_files)

    for trace_file in trace_files:
        try:
            with open(trace_file, "r") as f:
                trace = json.load(f)

            # Count consent
            if trace.get("recommendations", {}).get("consent_granted"):
                summary["users_with_consent"] += 1

            # Count recommendations
            recs = trace.get("recommendations", {}).get("recommendations", [])
            summary["total_recommendations"] += len(recs)

            # Extract guardrail decisions
            guardrail_decisions = trace.get("guardrail_decisions", [])
            for decision in guardrail_decisions:
                if decision.get("decision_type") == "tone_violations":
                    violations = decision.get("details", {}).get("violations", [])
                    summary["tone_violations"].extend(violations)
                elif decision.get("decision_type") == "offers_blocked":
                    blocked = decision.get("details", {}).get("blocked_offers", [])
                    summary["blocked_offers"].extend(blocked)

        except Exception:
            continue

    return summary


# =============================================================================
# HELPER FUNCTIONS - OPERATOR ACTIONS
# =============================================================================


def log_operator_override(
    user_id: str,
    operator_name: str,
    action: str,  # "approve", "override", "flag"
    reason: str,
    recommendation_title: str = None
) -> bool:
    """
    Log operator override to decision_log.md and update trace JSON.

    Returns True if successful, False otherwise.
    """
    timestamp = datetime.now()

    # 1. Append to decision_log.md
    try:
        log_entry = f"""
### Operator Override - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

**Date:** {timestamp.strftime('%Y-%m-%d')}
**Operator:** {operator_name}
**User:** {user_id}
**Action:** {action.upper()}
"""
        if recommendation_title:
            log_entry += f"**Recommendation:** {recommendation_title}  \n"

        log_entry += f"**Reason:** {reason}\n\n---\n\n"

        # Create operator overrides section if it doesn't exist
        if not DECISION_LOG_PATH.exists():
            DECISION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(DECISION_LOG_PATH, "w") as f:
                f.write("# Decision Log\n\n## Operator Overrides\n\n")

        # Check if operator overrides section exists
        with open(DECISION_LOG_PATH, "r") as f:
            content = f.read()

        if "## Operator Overrides" not in content:
            with open(DECISION_LOG_PATH, "a") as f:
                f.write("\n\n## Operator Overrides\n\n")

        # Append the override entry
        with open(DECISION_LOG_PATH, "a") as f:
            f.write(log_entry)

    except Exception as e:
        st.error(f"Failed to log to decision_log.md: {e}")
        return False

    # 2. Update trace JSON
    try:
        trace_file = TRACES_DIR / f"{user_id}.json"

        if trace_file.exists():
            with open(trace_file, "r") as f:
                trace = json.load(f)
        else:
            trace = {"user_id": user_id, "guardrail_decisions": []}

        # Add operator override to guardrail_decisions
        override_entry = {
            "timestamp": timestamp.isoformat(),
            "decision_type": "operator_override",
            "operator": operator_name,
            "action": action,
            "reason": reason,
        }

        if recommendation_title:
            override_entry["recommendation_title"] = recommendation_title

        if "guardrail_decisions" not in trace:
            trace["guardrail_decisions"] = []

        trace["guardrail_decisions"].append(override_entry)

        # Write back to trace file
        with open(trace_file, "w") as f:
            json.dump(trace, f, indent=2)

    except Exception as e:
        st.error(f"Failed to update trace JSON: {e}")
        return False

    return True


# =============================================================================
# UI COMPONENTS - SIDEBAR
# =============================================================================


def render_sidebar() -> str:
    """Render sidebar with navigation."""
    with st.sidebar:
        st.title("🔧 SpendSense")
        st.markdown("### Operator Dashboard")
        st.caption("Compliance & Oversight Interface")

        st.divider()

        # Navigation
        st.subheader("Navigation")
        tab = st.radio(
            "Select View:",
            [
                "📊 Overview",
                "👥 User Management",
                "📈 Behavioral Signals",
                "✅ Recommendation Review",
                "🔍 Decision Trace Viewer",
                "🛡️ Guardrails Monitor",
            ],
            key="navigation"
        )

        st.divider()

        # Quick stats
        st.subheader("Quick Stats")
        users_df = load_all_users()

        if len(users_df) > 0:
            st.metric("Total Users", len(users_df))
            st.metric("With Consent", users_df["consent_granted"].sum())

            persona_dist = load_persona_distribution()
            if persona_dist:
                most_common = max(persona_dist, key=persona_dist.get)
                st.metric("Most Common Persona", most_common, persona_dist[most_common])
        else:
            st.warning("No data loaded")

        st.divider()

        # System info
        st.caption(f"**Database:** {DB_PATH}")
        st.caption(f"**Signals:** {SIGNALS_PATH}")
        st.caption(f"**Traces:** {TRACES_DIR}")

        return tab


# =============================================================================
# UI COMPONENTS - OVERVIEW TAB
# =============================================================================


def render_overview_tab():
    """Render system overview with key metrics and persona distribution."""
    st.title("📊 System Overview")
    st.markdown("High-level metrics and system health")

    # Load data
    users_df = load_all_users()
    persona_dist = load_persona_distribution()
    guardrail_summary = load_guardrail_summary()

    if len(users_df) == 0:
        st.error("No users found. Please run data generation first.")
        st.code("uv run python -m ingest.data_generator")
        return

    # Top metrics row
    st.subheader("System Health")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Users",
            len(users_df),
            help="Total number of users in the system"
        )

    with col2:
        consent_count = users_df["consent_granted"].sum()
        consent_pct = (consent_count / len(users_df) * 100) if len(users_df) > 0 else 0
        st.metric(
            "Consent Granted",
            f"{consent_count} ({consent_pct:.1f}%)",
            help="Users who have opted in to data processing"
        )

    with col3:
        st.metric(
            "Personas Assigned",
            len(persona_dist),
            help="Distinct personas in use"
        )

    with col4:
        st.metric(
            "Total Recommendations",
            guardrail_summary.get("total_recommendations", 0),
            help="Total recommendations generated across all users"
        )

    st.divider()

    # Persona distribution
    st.subheader("Persona Distribution")

    if persona_dist:
        # Create dataframe for chart
        persona_df = pd.DataFrame([
            {"Persona": k.replace("_", " ").title(), "Count": v}
            for k, v in persona_dist.items()
        ])

        # Bar chart
        st.bar_chart(persona_df.set_index("Persona"))

        # Table with details
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(
                persona_df.style.format({"Count": "{:,.0f}"}),
                hide_index=True,
                use_container_width=True
            )

        with col2:
            # Persona descriptions
            persona_descriptions = {
                "High Utilization": "Credit utilization ≥50% or carrying interest",
                "Variable Income": "Irregular income with low cash buffer",
                "Subscription Heavy": "Multiple recurring subscriptions",
                "Savings Builder": "Positive savings growth and low utilization",
                "General": "Default persona with minimal signals",
            }

            st.markdown("**Persona Definitions:**")
            for persona, desc in persona_descriptions.items():
                if persona.lower().replace(" ", "_") in persona_dist:
                    st.caption(f"**{persona}:** {desc}")
    else:
        st.info("No persona assignments found. Run feature pipeline and persona assignment.")

    st.divider()

    # Guardrails summary
    st.subheader("Guardrails Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        tone_violation_count = len(guardrail_summary.get("tone_violations", []))
        st.metric(
            "Tone Violations",
            tone_violation_count,
            delta=f"-{tone_violation_count}" if tone_violation_count > 0 else None,
            delta_color="inverse",
            help="Recommendations flagged for inappropriate tone"
        )

    with col2:
        blocked_offer_count = len(guardrail_summary.get("blocked_offers", []))
        st.metric(
            "Blocked Offers",
            blocked_offer_count,
            delta=f"-{blocked_offer_count}" if blocked_offer_count > 0 else None,
            delta_color="inverse",
            help="Offers filtered due to eligibility or predatory product rules"
        )

    with col3:
        no_consent_count = len(users_df) - users_df["consent_granted"].sum()
        st.metric(
            "Users Without Consent",
            no_consent_count,
            delta=f"-{no_consent_count}" if no_consent_count > 0 else None,
            delta_color="inverse",
            help="Users who have not opted in to data processing"
        )

    # Recent activity (placeholder for future enhancement)
    st.divider()
    st.subheader("Recent Activity")
    st.info("📝 Recent operator overrides and system events will appear here (coming soon)")


# =============================================================================
# UI COMPONENTS - USER MANAGEMENT TAB
# =============================================================================


def render_user_management_tab():
    """Render user management interface with filtering and bulk operations."""
    st.title("👥 User Management")
    st.markdown("Search, filter, and manage user accounts")

    # Load data
    users_df = load_all_users()

    if len(users_df) == 0:
        st.error("No users found.")
        return

    # Filters
    st.subheader("Filters")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        consent_filter = st.selectbox(
            "Consent Status",
            ["All", "Granted", "Not Granted"],
            key="consent_filter"
        )

    with col2:
        personas = ["All"] + sorted(users_df["persona"].dropna().unique().tolist())
        persona_filter = st.selectbox(
            "Persona",
            personas,
            key="persona_filter"
        )

    with col3:
        genders = ["All"] + sorted(users_df["gender"].dropna().unique().tolist())
        gender_filter = st.selectbox(
            "Gender",
            genders,
            key="gender_filter"
        )

    with col4:
        income_tiers = ["All"] + sorted(users_df["income_tier"].dropna().unique().tolist())
        income_filter = st.selectbox(
            "Income Tier",
            income_tiers,
            key="income_filter"
        )

    # Apply filters
    filtered_df = users_df.copy()

    if consent_filter == "Granted":
        filtered_df = filtered_df[filtered_df["consent_granted"] == True]
    elif consent_filter == "Not Granted":
        filtered_df = filtered_df[filtered_df["consent_granted"] == False]

    if persona_filter != "All":
        filtered_df = filtered_df[filtered_df["persona"] == persona_filter]

    if gender_filter != "All":
        filtered_df = filtered_df[filtered_df["gender"] == gender_filter]

    if income_filter != "All":
        filtered_df = filtered_df[filtered_df["income_tier"] == income_filter]

    st.divider()

    # Results
    st.subheader(f"Users ({len(filtered_df)} of {len(users_df)})")

    # Format display
    display_df = filtered_df[[
        "user_id", "name", "consent_granted", "persona",
        "age", "gender", "income_tier", "region"
    ]].copy()

    display_df["consent_granted"] = display_df["consent_granted"].apply(
        lambda x: "✅ Yes" if x else "⏸️ No"
    )
    display_df["persona"] = display_df["persona"].fillna("(None)").apply(
        lambda x: x.replace("_", " ").title() if x != "(None)" else x
    )

    # Display table
    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "user_id": "User ID",
            "name": "Name",
            "consent_granted": "Consent",
            "persona": "Persona",
            "age": "Age",
            "gender": "Gender",
            "income_tier": "Income Tier",
            "region": "Region",
        }
    )

    st.divider()

    # Bulk operations
    st.subheader("Bulk Operations")
    st.caption("⚠️ Use with caution - for testing and setup only")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Grant Consent to Filtered Users**")
        st.caption(f"This will grant consent to {len(filtered_df[~filtered_df['consent_granted'].str.contains('Yes')])} users")

        if st.button("Grant Consent to Filtered Users", type="secondary"):
            if MODULES_AVAILABLE:
                user_ids = filtered_df[~filtered_df["consent_granted"].str.contains("Yes")]["user_id"].tolist()
                if user_ids:
                    result = batch_grant_consent(user_ids)
                    st.success(f"✅ Granted consent to {result.get('granted_count', 0)} users")
                    st.rerun()
                else:
                    st.info("All filtered users already have consent")
            else:
                st.error("Guardrails module not available")

    with col2:
        st.markdown("**User Detail View**")
        selected_user = st.selectbox(
            "Select user to view details:",
            filtered_df["user_id"].tolist(),
            format_func=lambda uid: f"{uid} - {filtered_df[filtered_df['user_id']==uid].iloc[0]['name']}",
            key="detail_user_selector"
        )

        if st.button("View User Details", type="primary"):
            st.session_state["trace_viewer_user"] = selected_user
            st.info(f"Navigate to 'Decision Trace Viewer' tab to see details for {selected_user}")


# =============================================================================
# UI COMPONENTS - BEHAVIORAL SIGNALS TAB
# =============================================================================


def render_signals_tab():
    """Render behavioral signals visualization with aggregate metrics and charts."""
    st.title("📈 Behavioral Signals")
    st.markdown("Aggregate metrics and distribution analysis")

    # Load data
    signals_df = load_all_signals()

    if len(signals_df) == 0:
        st.error("No signals data found. Run feature pipeline first.")
        st.code("uv run python -m features")
        return

    # Aggregate metrics
    st.subheader("Aggregate Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if "credit_max_util_pct" in signals_df.columns:
            avg_util = signals_df["credit_max_util_pct"].mean()
            st.metric(
                "Avg Credit Utilization",
                f"{avg_util:.1f}%",
                help="Average maximum credit utilization across all users"
            )
        else:
            st.metric("Avg Credit Utilization", "N/A")

    with col2:
        if "sub_30d_recurring_count" in signals_df.columns:
            avg_subs = signals_df["sub_30d_recurring_count"].mean()
            st.metric(
                "Avg Subscriptions",
                f"{avg_subs:.1f}",
                help="Average number of recurring subscriptions per user"
            )
        else:
            st.metric("Avg Subscriptions", "N/A")

    with col3:
        if "sav_180d_net_inflow" in signals_df.columns:
            median_savings = signals_df["sav_180d_net_inflow"].median()
            st.metric(
                "Median Savings Inflow (180d)",
                f"${median_savings:,.0f}",
                help="Median net savings inflow over 180 days"
            )
        else:
            st.metric("Median Savings Inflow", "N/A")

    with col4:
        if "inc_30d_median_pay_gap_days" in signals_df.columns:
            median_pay_gap = signals_df["inc_30d_median_pay_gap_days"].median()
            st.metric(
                "Median Pay Gap",
                f"{median_pay_gap:.0f} days",
                help="Median days between income deposits"
            )
        else:
            st.metric("Median Pay Gap", "N/A")

    st.divider()

    # Distribution charts
    st.subheader("Distribution Analysis")

    # Credit utilization histogram
    if "credit_max_util_pct" in signals_df.columns:
        st.markdown("**Credit Utilization Distribution**")

        util_data = signals_df[signals_df["credit_max_util_pct"].notna()]["credit_max_util_pct"]

        if len(util_data) > 0:
            # Create histogram bins
            bins = [0, 30, 50, 80, 100]
            labels = ["0-30% (Good)", "30-50% (Fair)", "50-80% (High)", "80-100% (Very High)"]
            util_counts = pd.cut(util_data, bins=bins, labels=labels, include_lowest=True).value_counts()

            util_df = pd.DataFrame({
                "Range": util_counts.index,
                "Count": util_counts.values
            })

            col1, col2 = st.columns([2, 1])

            with col1:
                st.bar_chart(util_df.set_index("Range"))

            with col2:
                st.dataframe(util_df, hide_index=True, use_container_width=True)

    st.divider()

    # Subscription count distribution
    if "sub_30d_recurring_count" in signals_df.columns:
        st.markdown("**Subscription Count Distribution**")

        sub_data = signals_df[signals_df["sub_30d_recurring_count"].notna()]["sub_30d_recurring_count"]

        if len(sub_data) > 0:
            sub_counts = sub_data.value_counts().sort_index()

            sub_df = pd.DataFrame({
                "Subscriptions": sub_counts.index,
                "Count": sub_counts.values
            })

            col1, col2 = st.columns([2, 1])

            with col1:
                st.bar_chart(sub_df.set_index("Subscriptions"))

            with col2:
                st.dataframe(sub_df, hide_index=True, use_container_width=True)

    st.divider()

    # 30d vs 180d comparison
    st.subheader("30-Day vs 180-Day Comparison")

    comparison_metrics = []

    if "sub_30d_recurring_count" in signals_df.columns and "sub_180d_recurring_count" in signals_df.columns:
        comparison_metrics.append({
            "Metric": "Recurring Subscriptions",
            "30-Day Avg": f"{signals_df['sub_30d_recurring_count'].mean():.2f}",
            "180-Day Avg": f"{signals_df['sub_180d_recurring_count'].mean():.2f}",
        })

    if "inc_30d_median_pay_gap_days" in signals_df.columns and "inc_180d_median_pay_gap_days" in signals_df.columns:
        comparison_metrics.append({
            "Metric": "Median Pay Gap (days)",
            "30-Day Avg": f"{signals_df['inc_30d_median_pay_gap_days'].mean():.1f}",
            "180-Day Avg": f"{signals_df['inc_180d_median_pay_gap_days'].mean():.1f}",
        })

    if comparison_metrics:
        comp_df = pd.DataFrame(comparison_metrics)
        st.dataframe(comp_df, hide_index=True, use_container_width=True)

    st.divider()

    # Per-user drill-down
    st.subheader("Per-User Signal Drill-Down")

    users_df = load_all_users()
    if len(users_df) > 0:
        selected_user = st.selectbox(
            "Select user to view detailed signals:",
            signals_df["user_id"].tolist(),
            key="signals_user_selector"
        )

        if selected_user:
            user_signals = signals_df[signals_df["user_id"] == selected_user].iloc[0].to_dict()

            # Display key signals
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Credit Signals**")
                credit_cols = [col for col in signals_df.columns if col.startswith("credit_")]
                for col in credit_cols:
                    value = user_signals.get(col)
                    if pd.notna(value):
                        st.caption(f"**{col}:** {value}")

                st.markdown("**Subscription Signals**")
                sub_cols = [col for col in signals_df.columns if col.startswith("sub_")]
                for col in sub_cols:
                    value = user_signals.get(col)
                    if pd.notna(value):
                        st.caption(f"**{col}:** {value}")

            with col2:
                st.markdown("**Savings Signals**")
                sav_cols = [col for col in signals_df.columns if col.startswith("sav_")]
                for col in sav_cols:
                    value = user_signals.get(col)
                    if pd.notna(value):
                        st.caption(f"**{col}:** {value}")

                st.markdown("**Income Signals**")
                inc_cols = [col for col in signals_df.columns if col.startswith("inc_")]
                for col in inc_cols:
                    value = user_signals.get(col)
                    if pd.notna(value):
                        st.caption(f"**{col}:** {value}")


# =============================================================================
# UI COMPONENTS - RECOMMENDATION REVIEW TAB
# =============================================================================


def render_recommendations_tab():
    """Render recommendation review interface with approve/override/flag workflow."""
    st.title("✅ Recommendation Review")
    st.markdown("Review, approve, override, or flag recommendations")

    if not MODULES_AVAILABLE:
        st.error("Recommendation engine not available. Please check your installation.")
        return

    # User selection
    users_df = load_all_users()

    if len(users_df) == 0:
        st.error("No users found.")
        return

    st.subheader("Select User")

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_user = st.selectbox(
            "Choose user to review recommendations:",
            users_df["user_id"].tolist(),
            format_func=lambda uid: f"{uid} - {users_df[users_df['user_id']==uid].iloc[0]['name']} ({users_df[users_df['user_id']==uid].iloc[0]['persona'] or 'No Persona'})",
            key="review_user_selector"
        )

    with col2:
        if st.button("Load Recommendations", type="primary"):
            st.session_state["review_loaded"] = True
            st.rerun()

    if not st.session_state.get("review_loaded"):
        st.info("👆 Select a user and click 'Load Recommendations' to begin review")
        return

    st.divider()

    # Generate recommendations
    user_data = users_df[users_df["user_id"] == selected_user].iloc[0]

    st.subheader(f"Recommendations for {user_data['name']} ({selected_user})")
    st.caption(f"**Persona:** {user_data['persona'] or 'None'} | **Consent:** {'✅ Granted' if user_data['consent_granted'] else '⏸️ Not Granted'}")

    try:
        recs = generate_recommendations(selected_user)
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        st.exception(e)
        return

    # Display metadata
    metadata = recs.get("metadata", {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Education Items", metadata.get("education_count", 0))

    with col2:
        st.metric("Partner Offers", metadata.get("offer_count", 0))

    with col3:
        tone_passed = metadata.get("tone_check_passed", True)
        st.metric(
            "Tone Check",
            "✅ Passed" if tone_passed else "⚠️ Issues",
            delta=None if tone_passed else metadata.get("tone_violations_count", 0),
            delta_color="off" if tone_passed else "inverse"
        )

    with col4:
        if metadata.get("reason"):
            st.warning(f"⚠️ {metadata['reason']}")

    st.divider()

    # Display recommendations
    recommendations = recs.get("recommendations", [])

    if len(recommendations) == 0:
        st.info("No recommendations generated for this user.")

        if not user_data["consent_granted"]:
            st.warning("User has not granted consent. No recommendations will be generated.")
        elif not user_data["persona"] or user_data["persona"] == "general":
            st.warning("User has 'general' persona with insufficient behavioral signals.")

        return

    st.subheader(f"Review {len(recommendations)} Recommendations")

    for idx, rec in enumerate(recommendations, 1):
        with st.expander(f"#{idx} - {rec.get('title', 'Untitled')}", expanded=(idx == 1)):
            # Display recommendation details
            st.markdown(f"**Type:** {rec.get('type', 'unknown').replace('_', ' ').title()}")
            st.markdown(f"**Category:** {rec.get('category', 'N/A')}")

            st.markdown("**Description:**")
            st.markdown(rec.get("description", "No description available"))

            st.markdown("**Rationale (with concrete data):**")
            st.info(rec.get("rationale", "No rationale provided"))

            st.caption(rec.get("disclaimer", ""))

            st.divider()

            # Guardrail checks
            st.markdown("**Guardrail Checks:**")

            col1, col2 = st.columns(2)

            with col1:
                # Tone validation
                tone_result = validate_tone(rec.get("rationale", "") + " " + rec.get("description", ""))
                if len(tone_result) == 0:
                    st.success("✅ Tone: Passed")
                else:
                    st.error(f"⚠️ Tone: {len(tone_result)} violations detected")
                    for violation in tone_result:
                        st.caption(f"- {violation.get('phrase')}")

            with col2:
                # Eligibility (simplified check for display)
                if rec.get("type") == "partner_offer":
                    st.info("💼 Partner Offer - Eligibility Checked")
                else:
                    st.success("📚 Educational Content")

            st.divider()

            # Operator actions
            st.markdown("**Operator Actions:**")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(f"✅ Approve #{idx}", key=f"approve_{idx}", use_container_width=True):
                    operator = st.session_state.get("operator_name", "Unknown Operator")
                    success = log_operator_override(
                        user_id=selected_user,
                        operator_name=operator,
                        action="approve",
                        reason="Recommendation approved after review",
                        recommendation_title=rec.get("title")
                    )
                    if success:
                        st.success(f"✅ Approved recommendation #{idx}")
                    else:
                        st.error("Failed to log approval")

            with col2:
                if st.button(f"⚠️ Override #{idx}", key=f"override_{idx}", use_container_width=True):
                    st.session_state[f"override_mode_{idx}"] = True
                    st.rerun()

            with col3:
                if st.button(f"🚩 Flag #{idx}", key=f"flag_{idx}", use_container_width=True):
                    st.session_state[f"flag_mode_{idx}"] = True
                    st.rerun()

            # Override form
            if st.session_state.get(f"override_mode_{idx}"):
                st.markdown("---")
                st.markdown("**Override Form:**")

                operator = st.text_input("Your Name:", key=f"override_operator_{idx}")
                reason = st.text_area("Reason for Override:", key=f"override_reason_{idx}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Submit Override", key=f"submit_override_{idx}", type="primary"):
                        if operator and reason:
                            success = log_operator_override(
                                user_id=selected_user,
                                operator_name=operator,
                                action="override",
                                reason=reason,
                                recommendation_title=rec.get("title")
                            )
                            if success:
                                st.success(f"✅ Override logged for recommendation #{idx}")
                                st.session_state[f"override_mode_{idx}"] = False
                                st.session_state["operator_name"] = operator  # Remember operator
                                st.rerun()
                            else:
                                st.error("Failed to log override")
                        else:
                            st.warning("Please provide your name and reason")

                with col2:
                    if st.button("Cancel", key=f"cancel_override_{idx}"):
                        st.session_state[f"override_mode_{idx}"] = False
                        st.rerun()

            # Flag form
            if st.session_state.get(f"flag_mode_{idx}"):
                st.markdown("---")
                st.markdown("**Flag for Review:**")

                operator = st.text_input("Your Name:", key=f"flag_operator_{idx}")
                reason = st.text_area("Reason for Flagging:", key=f"flag_reason_{idx}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Submit Flag", key=f"submit_flag_{idx}", type="primary"):
                        if operator and reason:
                            success = log_operator_override(
                                user_id=selected_user,
                                operator_name=operator,
                                action="flag",
                                reason=reason,
                                recommendation_title=rec.get("title")
                            )
                            if success:
                                st.success(f"🚩 Flagged recommendation #{idx} for review")
                                st.session_state[f"flag_mode_{idx}"] = False
                                st.session_state["operator_name"] = operator  # Remember operator
                                st.rerun()
                            else:
                                st.error("Failed to log flag")
                        else:
                            st.warning("Please provide your name and reason")

                with col2:
                    if st.button("Cancel", key=f"cancel_flag_{idx}"):
                        st.session_state[f"flag_mode_{idx}"] = False
                        st.rerun()


# =============================================================================
# UI COMPONENTS - DECISION TRACE VIEWER TAB
# =============================================================================


def render_trace_viewer_tab():
    """Render decision trace viewer for full audit trail."""
    st.title("🔍 Decision Trace Viewer")
    st.markdown("Inspect complete decision pipeline for any user")

    # User selection
    users_df = load_all_users()

    if len(users_df) == 0:
        st.error("No users found.")
        return

    # Check if user was selected from another tab
    default_user = st.session_state.get("trace_viewer_user", users_df["user_id"].iloc[0])

    selected_user = st.selectbox(
        "Select user to view trace:",
        users_df["user_id"].tolist(),
        index=users_df["user_id"].tolist().index(default_user) if default_user in users_df["user_id"].tolist() else 0,
        format_func=lambda uid: f"{uid} - {users_df[users_df['user_id']==uid].iloc[0]['name']}",
        key="trace_user_selector"
    )

    # Load trace
    trace = load_user_trace(selected_user)

    if not trace:
        st.error(f"No trace file found for {selected_user}")
        st.caption("Trace files are generated during the feature pipeline and recommendation generation.")
        return

    st.divider()

    # User info
    user_data = users_df[users_df["user_id"] == selected_user].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("User", user_data["name"])

    with col2:
        st.metric("Persona", (user_data["persona"] or "None").replace("_", " ").title())

    with col3:
        st.metric("Consent", "✅ Granted" if user_data["consent_granted"] else "⏸️ Not Granted")

    with col4:
        st.metric("Age", f"{user_data['age']} ({user_data['gender']})")

    st.divider()

    # Behavioral Signals
    with st.expander("📊 Behavioral Signals", expanded=True):
        signals = trace.get("signals", {})

        if signals:
            col1, col2 = st.columns(2)

            with col1:
                # Subscriptions
                st.markdown("**Subscriptions**")
                sub_30d = signals.get("subscriptions", {}).get("30d", {})
                sub_180d = signals.get("subscriptions", {}).get("180d", {})

                if sub_30d or sub_180d:
                    st.json({"30d": sub_30d, "180d": sub_180d})
                else:
                    st.caption("No subscription data")

                # Credit
                st.markdown("**Credit**")
                credit = signals.get("credit", {}).get("current", {})

                if credit:
                    st.json(credit)
                else:
                    st.caption("No credit data")

            with col2:
                # Savings
                st.markdown("**Savings**")
                sav_30d = signals.get("savings", {}).get("30d", {})
                sav_180d = signals.get("savings", {}).get("180d", {})

                if sav_30d or sav_180d:
                    st.json({"30d": sav_30d, "180d": sav_180d})
                else:
                    st.caption("No savings data")

                # Income
                st.markdown("**Income**")
                inc_30d = signals.get("income", {}).get("30d", {})
                inc_180d = signals.get("income", {}).get("180d", {})

                if inc_30d or inc_180d:
                    st.json({"30d": inc_30d, "180d": inc_180d})
                else:
                    st.caption("No income data")
        else:
            st.info("No signals data in trace")

    # Persona Assignment
    with st.expander("🎭 Persona Assignment", expanded=True):
        persona_data = trace.get("persona_assignment", {})

        if persona_data:
            st.markdown(f"**Assigned Persona:** {persona_data.get('persona', 'N/A').replace('_', ' ').title()}")
            st.markdown(f"**Timestamp:** {persona_data.get('timestamp', 'N/A')}")

            st.markdown("**Criteria Met:**")
            criteria_met = persona_data.get("criteria_met", {})
            if criteria_met:
                for key, value in criteria_met.items():
                    st.caption(f"- **{key}:** {value}")
            else:
                st.caption("No criteria data")

            st.markdown("**All Checks:**")
            all_checks = persona_data.get("all_checks", {})
            if all_checks:
                st.json(all_checks)
        else:
            st.info("No persona assignment data in trace")

    # Recommendations
    with st.expander("💡 Recommendations", expanded=True):
        recs_data = trace.get("recommendations", {})

        if recs_data:
            st.markdown(f"**Timestamp:** {recs_data.get('timestamp', 'N/A')}")
            st.markdown(f"**Persona:** {recs_data.get('persona', 'N/A').replace('_', ' ').title()}")
            st.markdown(f"**Consent Granted:** {'✅ Yes' if recs_data.get('consent_granted') else '⏸️ No'}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Education Items", recs_data.get("education_count", 0))

            with col2:
                st.metric("Partner Offers", recs_data.get("offer_count", 0))

            with col3:
                st.metric("Total", recs_data.get("total_recommendations", 0))

            st.markdown("**Recommendations:**")
            recommendations = recs_data.get("recommendations", [])

            if recommendations:
                for idx, rec in enumerate(recommendations, 1):
                    st.markdown(f"**#{idx} - {rec.get('title', 'Untitled')}**")
                    st.caption(f"Type: {rec.get('type', 'N/A')} | Category: {rec.get('category', 'N/A')}")
                    st.caption(f"Rationale: {rec.get('rationale', 'N/A')}")
                    st.divider()
            else:
                st.caption("No recommendations")
        else:
            st.info("No recommendations data in trace")

    # Guardrail Decisions
    with st.expander("🛡️ Guardrail Decisions", expanded=True):
        guardrail_decisions = trace.get("guardrail_decisions", [])

        if guardrail_decisions:
            for idx, decision in enumerate(guardrail_decisions, 1):
                decision_type = decision.get("decision_type", "unknown")
                timestamp = decision.get("timestamp", "N/A")

                st.markdown(f"**Decision #{idx} - {decision_type.replace('_', ' ').title()}**")
                st.caption(f"Timestamp: {timestamp}")

                # Display details based on type
                if decision_type == "operator_override":
                    st.markdown(f"**Operator:** {decision.get('operator', 'N/A')}")
                    st.markdown(f"**Action:** {decision.get('action', 'N/A').upper()}")
                    st.markdown(f"**Reason:** {decision.get('reason', 'N/A')}")
                    if decision.get("recommendation_title"):
                        st.markdown(f"**Recommendation:** {decision.get('recommendation_title')}")
                else:
                    details = decision.get("details", {})
                    if details:
                        st.json(details)

                st.divider()
        else:
            st.info("No guardrail decisions in trace")

    # Raw JSON view
    with st.expander("📄 Raw JSON", expanded=False):
        st.json(trace)


# =============================================================================
# UI COMPONENTS - GUARDRAILS MONITOR TAB
# =============================================================================


def render_guardrails_tab():
    """Render guardrails monitoring interface."""
    st.title("🛡️ Guardrails Monitor")
    st.markdown("Monitor consent, tone validation, and eligibility enforcement")

    # Load summary
    summary = load_guardrail_summary()

    # Summary metrics
    st.subheader("Summary Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Users",
            summary.get("total_users", 0),
            help="Total users with trace files"
        )

    with col2:
        st.metric(
            "With Consent",
            summary.get("users_with_consent", 0),
            help="Users who have granted consent"
        )

    with col3:
        tone_violations = len(summary.get("tone_violations", []))
        st.metric(
            "Tone Violations",
            tone_violations,
            delta=f"-{tone_violations}" if tone_violations > 0 else None,
            delta_color="inverse",
            help="Total tone violations detected across all recommendations"
        )

    with col4:
        blocked_offers = len(summary.get("blocked_offers", []))
        st.metric(
            "Blocked Offers",
            blocked_offers,
            delta=f"-{blocked_offers}" if blocked_offers > 0 else None,
            delta_color="inverse",
            help="Total offers blocked due to eligibility or predatory filtering"
        )

    st.divider()

    # Tone violations detail
    st.subheader("Tone Violations")

    tone_violations = summary.get("tone_violations", [])

    if tone_violations:
        st.warning(f"⚠️ {len(tone_violations)} tone violations detected")

        # Group by phrase
        violation_counts = {}
        for violation in tone_violations:
            phrase = violation.get("phrase", "unknown")
            violation_counts[phrase] = violation_counts.get(phrase, 0) + 1

        violation_df = pd.DataFrame([
            {"Prohibited Phrase": phrase, "Occurrences": count}
            for phrase, count in sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)
        ])

        st.dataframe(violation_df, hide_index=True, use_container_width=True)
    else:
        st.success("✅ No tone violations detected across all recommendations")

    st.divider()

    # Blocked offers detail
    st.subheader("Blocked Offers")

    blocked_offers = summary.get("blocked_offers", [])

    if blocked_offers:
        st.warning(f"⚠️ {len(blocked_offers)} offers blocked")

        # Display sample
        for idx, offer in enumerate(blocked_offers[:10], 1):
            st.caption(f"{idx}. {offer.get('title', 'Unknown')} - Reason: {offer.get('reason', 'N/A')}")

        if len(blocked_offers) > 10:
            st.caption(f"... and {len(blocked_offers) - 10} more")
    else:
        st.success("✅ No offers blocked (all passed eligibility checks)")

    st.divider()

    # Consent audit trail
    st.subheader("Consent Audit Trail")

    users_df = load_all_users()

    if len(users_df) > 0:
        # Recent consent changes
        consent_df = users_df[users_df["consent_timestamp"].notna()].copy()

        if len(consent_df) > 0:
            consent_df = consent_df.sort_values("consent_timestamp", ascending=False).head(10)

            display_df = consent_df[[
                "user_id", "name", "consent_granted", "consent_timestamp"
            ]].copy()

            display_df["consent_granted"] = display_df["consent_granted"].apply(
                lambda x: "✅ Granted" if x else "⏸️ Not Granted"
            )

            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "user_id": "User ID",
                    "name": "Name",
                    "consent_granted": "Status",
                    "consent_timestamp": "Timestamp",
                }
            )
        else:
            st.info("No consent activity recorded yet")


# =============================================================================
# MAIN APP
# =============================================================================


def main():
    """Main application entry point."""

    # Check if data exists
    if not DB_PATH.exists():
        st.error("❌ Database not found!")
        st.markdown("Please run data generation first:")
        st.code("uv run python -m ingest.data_generator")
        st.stop()

    # Render sidebar and get selected tab
    tab = render_sidebar()

    # Render selected tab
    if tab == "📊 Overview":
        render_overview_tab()

    elif tab == "👥 User Management":
        render_user_management_tab()

    elif tab == "📈 Behavioral Signals":
        render_signals_tab()

    elif tab == "✅ Recommendation Review":
        render_recommendations_tab()

    elif tab == "🔍 Decision Trace Viewer":
        render_trace_viewer_tab()

    elif tab == "🛡️ Guardrails Monitor":
        render_guardrails_tab()


if __name__ == "__main__":
    main()

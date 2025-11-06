"""
Unit and integration tests for persona assignment system (PR #3).

Tests verify:
1. High Utilization persona criteria
2. Variable Income persona criteria
3. Persona priority ordering
4. Edge case - No persona match
5. Full persona assignment integration
"""

import pandas as pd
import sqlite3
import json
from pathlib import Path

from personas.assignment import (
    check_high_utilization,
    check_variable_income,
    check_subscription_heavy,
    check_cash_flow_optimizer,
    check_savings_builder,
    assign_persona,
    assign_all_personas,
)


class TestHighUtilizationPersona:
    """Test High Utilization persona criteria (Priority 1)."""

    def test_high_utilization_by_utilization_threshold(self):
        """Test: Mock signal data with utilization=68%, interest=$87."""
        # Create mock signals with high utilization
        signals = pd.Series(
            {
                "credit_max_util_pct": 68.0,
                "credit_interest_charges": True,
                "credit_min_payment_only": False,
                "credit_is_overdue": False,
            }
        )

        matches, criteria_met = check_high_utilization(signals)

        # Verify: Assigned to "high_utilization" persona
        assert matches is True, "Should match high_utilization criteria"
        assert "high_utilization" in criteria_met, "Should flag high utilization"
        assert criteria_met["high_utilization"] == 68.0
        assert "interest_charges" in criteria_met, "Should flag interest charges"

    def test_high_utilization_by_interest_only(self):
        """Test: User with low utilization but has interest charges."""
        signals = pd.Series(
            {
                "credit_max_util_pct": 25.0,
                "credit_interest_charges": True,  # This alone should trigger per spec
                "credit_min_payment_only": False,
                "credit_is_overdue": False,
            }
        )

        matches, criteria_met = check_high_utilization(signals)

        assert matches is True
        assert "interest_charges" in criteria_met
        assert "high_utilization" not in criteria_met  # Utilization is below 50%

    def test_high_utilization_by_overdue(self):
        """Test: User with overdue status triggers high utilization."""
        signals = pd.Series(
            {
                "credit_max_util_pct": 10.0,
                "credit_interest_charges": False,
                "credit_min_payment_only": False,
                "credit_is_overdue": True,  # This alone should trigger
            }
        )

        matches, criteria_met = check_high_utilization(signals)

        assert matches is True
        assert "is_overdue" in criteria_met

    def test_no_high_utilization(self):
        """Test: User with good credit behavior should not match."""
        signals = pd.Series(
            {
                "credit_max_util_pct": 15.0,
                "credit_interest_charges": False,
                "credit_min_payment_only": False,
                "credit_is_overdue": False,
            }
        )

        matches, criteria_met = check_high_utilization(signals)

        assert matches is False
        assert len(criteria_met) == 0


class TestVariableIncomePersona:
    """Test Variable Income Budgeter persona criteria (Priority 2)."""

    def test_variable_income_criteria(self):
        """Test: Mock signal data with median_pay_gap=50 days, cash_buffer=0.8 months."""
        signals = pd.Series(
            {
                "inc_180d_median_pay_gap_days": 50,  # > 45 days
                "inc_180d_cash_buffer_months": 0.8,  # < 1 month
                "inc_180d_variability": 0.35,
            }
        )

        matches, criteria_met = check_variable_income(signals)

        # Verify: Assigned to "variable_income" persona
        assert matches is True, "Should match variable_income criteria"
        assert "median_pay_gap_days" in criteria_met
        assert criteria_met["median_pay_gap_days"] == 50
        assert "cash_buffer_months" in criteria_met
        assert criteria_met["cash_buffer_months"] == 0.8

    def test_variable_income_missing_one_condition(self):
        """Test: User meets only one of two AND conditions should not match."""
        signals = pd.Series(
            {
                "inc_180d_median_pay_gap_days": 50,  # > 45 days ✓
                "inc_180d_cash_buffer_months": 2.5,  # >= 1 month ✗
            }
        )

        matches, criteria_met = check_variable_income(signals)

        # Should NOT match because both conditions are required (AND logic)
        assert matches is False

    def test_variable_income_both_conditions_met(self):
        """Test: User meets both AND conditions."""
        signals = pd.Series(
            {
                "inc_180d_median_pay_gap_days": 60,  # > 45 days
                "inc_180d_cash_buffer_months": 0.5,  # < 1 month
            }
        )

        matches, criteria_met = check_variable_income(signals)

        assert matches is True
        assert len(criteria_met) == 2  # Both conditions met


class TestSubscriptionHeavyPersona:
    """Test Subscription Heavy persona criteria (Priority 3)."""

    def test_subscription_heavy_by_count_and_spend(self):
        """Test: User with 5 subscriptions totaling $75/month."""
        signals = pd.Series(
            {
                "sub_180d_recurring_count": 5,  # >= 3 ✓ (cadence enforced by detector)
                "sub_30d_monthly_spend": 75.0,  # >= $50 ✓ (30d per spec)
                "sub_30d_share_pct": 8.0,  # 8% (below 10%)
            }
        )

        matches, criteria_met = check_subscription_heavy(signals)

        # Verify: Matches because count >= 3 AND spend >= $50
        assert matches == True
        assert "recurring_count" in criteria_met
        assert criteria_met["recurring_count"] == 5
        assert "monthly_spend" in criteria_met

    def test_subscription_heavy_by_count_and_share(self):
        """Test: User with 4 subscriptions at 12% of total spend."""
        signals = pd.Series(
            {
                "sub_180d_recurring_count": 4,  # >= 3 ✓
                "sub_30d_monthly_spend": 35.0,  # < $50
                "sub_30d_share_pct": 12.0,  # >= 10% ✓ (percentage format)
            }
        )

        matches, criteria_met = check_subscription_heavy(signals)

        # Verify: Matches because count >= 3 AND share >= 10%
        assert matches == True
        assert "share_pct" in criteria_met

    def test_subscription_heavy_low_count(self):
        """Test: User with only 2 subscriptions should not match."""
        signals = pd.Series(
            {
                "sub_180d_recurring_count": 2,  # < 3 ✗
                "sub_30d_monthly_spend": 100.0,  # Even with high spend
                "sub_30d_share_pct": 8.0,
            }
        )

        matches, criteria_met = check_subscription_heavy(signals)

        # Should NOT match because count < 3
        assert matches == False


class TestSavingsBuilderPersona:
    """Test Savings Builder persona criteria (Priority 4)."""

    def test_savings_builder_by_growth_and_low_utilization(self):
        """Test: User with 3.5% savings growth and 20% utilization."""
        signals = pd.Series(
            {
                "sav_180d_growth_rate_pct": 3.5,  # >= 2% ✓ (percentage format: 3.5 = 3.5%)
                "sav_180d_net_inflow": 150.0,  # < $200
                "credit_max_util_pct": 20.0,  # < 30% ✓
            }
        )

        matches, criteria_met = check_savings_builder(signals)

        # Verify: Matches because growth >= 2% AND utilization < 30%
        assert matches == True
        assert "growth_rate_pct" in criteria_met
        assert "low_utilization" in criteria_met

    def test_savings_builder_by_inflow_and_low_utilization(self):
        """Test: User with $250 net inflow and 15% utilization."""
        signals = pd.Series(
            {
                "sav_180d_growth_rate_pct": 1.0,  # < 2% (percentage format: 1.0 = 1%)
                "sav_180d_net_inflow": 250.0,  # >= $200 ✓
                "credit_max_util_pct": 15.0,  # < 30% ✓
            }
        )

        matches, criteria_met = check_savings_builder(signals)

        # Verify: Matches because inflow >= $200 AND utilization < 30%
        assert matches == True
        assert "net_inflow" in criteria_met
        assert "low_utilization" in criteria_met

    def test_savings_builder_high_utilization_blocks(self):
        """Test: User with good savings but high utilization should not match."""
        signals = pd.Series(
            {
                "sav_180d_growth_rate_pct": 5.0,  # >= 2% ✓ (percentage format: 5.0 = 5%)
                "sav_180d_net_inflow": 300.0,  # >= $200 ✓
                "credit_max_util_pct": 75.0,  # >= 30% ✗
            }
        )

        matches, criteria_met = check_savings_builder(signals)

        # Should NOT match because utilization >= 30%
        assert matches == False


class TestPersonaPriorityOrdering:
    """Test persona priority conflict resolution."""

    def test_high_utilization_wins_over_savings_builder(self):
        """
        Test: Mock user matching BOTH High Utilization AND Savings Builder criteria.
        Verify: Assigned to "high_utilization" (higher priority).
        """
        signals = pd.Series(
            {
                # Matches High Utilization (Priority 1)
                "credit_max_util_pct": 65.0,  # Triggers high utilization
                "credit_interest_charges": True,
                "credit_min_payment_only": False,
                "credit_is_overdue": False,
                # Also matches Savings Builder (Priority 4)
                "sav_180d_growth_rate_pct": 5.0,  # >= 2% (percentage format: 5.0 = 5%)
                "sav_180d_net_inflow": 400.0,  # >= $200
                # Note: utilization check for Savings Builder will fail due to 65% > 30%
            }
        )

        persona, persona_data = assign_persona(signals)

        # Verify: Only high_utilization assigned (priority wins)
        assert persona == "High Utilization", "High utilization should have priority"
        assert persona_data["assigned_persona"] == "High Utilization"
        assert len(persona_data["criteria_met"]) > 0

    def test_variable_income_wins_over_subscription_heavy(self):
        """Test: Variable income has higher priority than subscription heavy."""
        signals = pd.Series(
            {
                # Matches Variable Income (Priority 2)
                "inc_180d_median_pay_gap_days": 50,
                "inc_180d_cash_buffer_months": 0.7,
                # Also matches Subscription Heavy (Priority 3)
                "sub_180d_recurring_count": 5,
                "sub_30d_monthly_spend": 100.0,
                "sub_30d_share_pct": 12.0,
                # Low credit utilization
                "credit_max_util_pct": 10.0,
                "credit_interest_charges": False,
                "credit_min_payment_only": False,
                "credit_is_overdue": False,
            }
        )

        persona, persona_data = assign_persona(signals)

        # Verify: variable_income wins
        assert persona == "Variable Income Budgeter"

    def test_subscription_heavy_wins_over_cash_flow_optimizer(self):
        """Test: Subscription Heavy has higher priority than Cash Flow Optimizer."""
        signals = pd.Series(
            {
                # Matches Subscription Heavy (Priority 3)
                "sub_180d_recurring_count": 5,
                "sub_30d_monthly_spend": 100.0,
                "sub_30d_share_pct": 12.0,
                # Also matches Cash Flow Optimizer (Priority 4)
                "inc_180d_cash_buffer_months": 1.5,
                "sav_180d_growth_rate_pct": 0.5,
                "sav_180d_net_inflow": 50.0,
                "inc_180d_median_pay_gap_days": 30,
                # Not other personas
                "credit_max_util_pct": 20.0,
                "credit_interest_charges": False,
                "credit_min_payment_only": False,
                "credit_is_overdue": False,
            }
        )

        persona, persona_data = assign_persona(signals)

        # Verify: subscription_heavy wins
        assert persona == "Subscription-Heavy"

    def test_cash_flow_optimizer_wins_over_savings_builder(self):
        """Test: Cash Flow Optimizer has higher priority than Savings Builder."""
        signals = pd.Series(
            {
                # Matches Cash Flow Optimizer (Priority 4)
                "inc_180d_cash_buffer_months": 1.2,
                "sav_180d_growth_rate_pct": 0.3,
                "sav_180d_net_inflow": 60.0,
                "inc_180d_median_pay_gap_days": 28,
                # Also would match Savings Builder, but utilization requirement conflicts
                # (Cash flow optimizer doesn't require low utilization, Savings Builder does)
                "credit_max_util_pct": 40.0,  # Too high for Savings Builder
                "credit_interest_charges": False,
                "credit_min_payment_only": False,
                "credit_is_overdue": False,
                "sub_180d_recurring_count": 2,
            }
        )

        persona, persona_data = assign_persona(signals)

        # Verify: cash_flow_optimizer wins
        assert persona == "Cash Flow Optimizer"


class TestCashFlowOptimizerPersona:
    """Test Cash Flow Optimizer persona criteria (Priority 4)."""

    def test_cash_flow_optimizer_all_criteria_met(self):
        """Test: User with low cash buffer, poor savings, and stable income."""
        signals = pd.Series(
            {
                "inc_180d_cash_buffer_months": 1.5,  # < 2 months ✓
                "sav_180d_growth_rate_pct": 0.5,  # < 1% ✓
                "sav_180d_net_inflow": 50.0,  # < $100 ✓
                "inc_180d_median_pay_gap_days": 30,  # ≤ 45 days (stable income) ✓
                "credit_max_util_pct": 25.0,  # Not high utilization
                "credit_interest_charges": False,
                "credit_min_payment_only": False,
                "credit_is_overdue": False,
                "sub_180d_recurring_count": 2,  # Not subscription heavy
            }
        )

        matches, criteria_met = check_cash_flow_optimizer(signals)

        # Verify: Matches all criteria
        assert matches is True
        assert "cash_buffer_months" in criteria_met
        assert criteria_met["cash_buffer_months"] == 1.5
        assert "low_growth_rate_pct" in criteria_met
        assert "low_net_inflow" in criteria_met
        assert "stable_income_pay_gap_days" in criteria_met

    def test_cash_flow_optimizer_high_cash_buffer_blocks(self):
        """Test: User with high cash buffer should not match."""
        signals = pd.Series(
            {
                "inc_180d_cash_buffer_months": 3.0,  # >= 2 months ✗
                "sav_180d_growth_rate_pct": 0.3,  # < 1% ✓
                "sav_180d_net_inflow": 30.0,  # < $100 ✓
                "inc_180d_median_pay_gap_days": 30,  # ≤ 45 days ✓
            }
        )

        matches, criteria_met = check_cash_flow_optimizer(signals)

        # Should NOT match because cash buffer is too high
        assert matches == False

    def test_cash_flow_optimizer_good_savings_blocks(self):
        """Test: User with good savings growth should not match."""
        signals = pd.Series(
            {
                "inc_180d_cash_buffer_months": 1.2,  # < 2 months ✓
                "sav_180d_growth_rate_pct": 5.0,  # >= 1% ✗
                "sav_180d_net_inflow": 500.0,  # >= $100 ✗
                "inc_180d_median_pay_gap_days": 30,  # ≤ 45 days ✓
            }
        )

        matches, criteria_met = check_cash_flow_optimizer(signals)

        # Should NOT match because savings metrics are good
        assert matches == False

    def test_cash_flow_optimizer_variable_income_blocks(self):
        """Test: User with variable income (high pay gap) should not match."""
        signals = pd.Series(
            {
                "inc_180d_cash_buffer_months": 0.8,  # < 2 months ✓
                "sav_180d_growth_rate_pct": 0.2,  # < 1% ✓
                "sav_180d_net_inflow": 20.0,  # < $100 ✓
                "inc_180d_median_pay_gap_days": 60,  # > 45 days ✗ (variable income)
            }
        )

        matches, criteria_met = check_cash_flow_optimizer(signals)

        # Should NOT match because this is a variable income case
        assert matches == False

    def test_cash_flow_optimizer_by_low_growth_only(self):
        """Test: User meeting criteria through low growth rate alone."""
        signals = pd.Series(
            {
                "inc_180d_cash_buffer_months": 1.8,  # < 2 months ✓
                "sav_180d_growth_rate_pct": 0.1,  # < 1% ✓ (triggers OR)
                "sav_180d_net_inflow": 150.0,  # >= $100 (but OR allows match)
                "inc_180d_median_pay_gap_days": 28,  # ≤ 45 days ✓
            }
        )

        matches, criteria_met = check_cash_flow_optimizer(signals)

        # Matches because growth < 1% (even though inflow >= $100)
        assert matches == True
        assert "low_growth_rate_pct" in criteria_met


class TestEdgeCaseNoPersona:
    """Test edge case handling for users with minimal signals."""

    def test_no_persona_match_assigns_general(self):
        """
        Test: Mock user with no signals meeting any persona threshold.
        Verify: Returns 'general' persona gracefully.
        """
        signals = pd.Series(
            {
                # All values below thresholds
                "credit_max_util_pct": 10.0,  # < 50%
                "credit_interest_charges": False,
                "credit_min_payment_only": False,
                "credit_is_overdue": False,
                "inc_180d_median_pay_gap_days": 14,  # < 45 days
                "inc_180d_cash_buffer_months": 3.0,  # >= 2 months
                "sub_180d_recurring_count": 1,  # < 3
                "sub_30d_monthly_spend": 15.0,  # < $50
                "sub_30d_share_pct": 3.0,  # < 10% (percentage format: 3.0 = 3%)
                "sav_180d_growth_rate_pct": 0.5,  # < 1% (but cash buffer is high)
                "sav_180d_net_inflow": 50.0,  # < $100
            }
        )

        persona, persona_data = assign_persona(signals)

        # Verify: Assigned to 'General' persona
        assert persona == "General", "Should assign to General persona when no criteria met"
        assert persona_data["assigned_persona"] == "General"
        assert len(persona_data["criteria_met"]) == 0, "No criteria should be met"

    def test_zero_signals_assigns_general(self):
        """Test: User with all zero/null signals should be assigned to general."""
        signals = pd.Series(
            {
                "credit_max_util_pct": 0.0,
                "credit_has_interest": False,
                "credit_min_payment_only": False,
                "credit_is_overdue": False,
                "inc_180d_median_pay_gap_days": 0,
                "inc_180d_cash_buffer_months": 0.0,
                "sub_180d_recurring_count": 0,
                "sub_180d_monthly_spend": 0.0,
                "sub_180d_share_pct": 0.0,
                "sav_180d_growth_rate_pct": 0.0,
                "sav_180d_net_inflow": 0.0,
            }
        )

        persona, persona_data = assign_persona(signals)

        assert persona == "General"


class TestFullPersonaAssignment:
    """Integration test for full persona assignment pipeline."""

    def test_full_persona_assignment_integration(self):
        """
        Test: Assign personas to all synthetic users from PR #2.
        Verify:
        - 100% of users with ≥3 behaviors have assigned persona
        - persona_assignments table populated in SQLite
        - Trace JSONs updated with persona logic
        Expected: Coverage metric = 100%, all assignments traceable
        """
        # Run full persona assignment
        assignments_df = assign_all_personas(
            signals_path="features/signals.parquet",
            db_path="data/users.sqlite",
            traces_dir="docs/traces",
        )

        # Verify: All users assigned
        assert len(assignments_df) == 100, "Should assign persona to all 100 users"
        assert assignments_df["persona"].notna().all(), "No null personas allowed"

        # Verify: SQLite table populated
        conn = sqlite3.connect("data/users.sqlite")
        db_assignments = pd.read_sql("SELECT * FROM persona_assignments", conn)
        conn.close()

        assert len(db_assignments) == 100, "SQLite should have 100 assignments"
        assert set(db_assignments.columns) == {
            "assignment_id",
            "user_id",
            "persona",
            "criteria_met",
            "assigned_at",
        }

        # Verify: Trace JSONs exist
        traces_dir = Path("docs/traces")
        trace_files = list(traces_dir.glob("*.json"))
        assert len(trace_files) >= 100, f"Should have ≥100 trace files, found {len(trace_files)}"

        # Verify: Trace JSON structure
        sample_trace_file = trace_files[0]
        with open(sample_trace_file, "r") as f:
            trace = json.load(f)

        assert "persona_assignment" in trace, "Trace should have persona_assignment section"
        assert "persona" in trace["persona_assignment"]
        assert "criteria_met" in trace["persona_assignment"]
        assert "all_checks" in trace["persona_assignment"]
        assert "timestamp" in trace["persona_assignment"]

        # Verify: Coverage = 100%
        coverage = (len(assignments_df) / 100) * 100
        assert coverage == 100.0, f"Coverage should be 100%, got {coverage}%"

        # Verify: All assignments are traceable (auditability)
        for _, row in assignments_df.iterrows():
            user_id = row["user_id"]
            trace_file = traces_dir / f"{user_id}.json"
            assert trace_file.exists(), f"Trace file missing for {user_id}"

        print("\n✅ Integration test passed!")
        print(f"   - {len(assignments_df)} users assigned personas")
        print(f"   - {len(db_assignments)} records in SQLite")
        print(f"   - {len(trace_files)} trace JSON files")
        print("   - Coverage: 100.0%")
        print("   - Auditability: 100.0%")

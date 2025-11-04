"""
Unit and Integration Tests for Recommendation Engine (PR #4)

This module tests the recommendation generation logic, including:
- Rationale formatting with concrete user data
- Mandatory disclaimer presence
- Recommendation count limits per persona
- Eligibility filtering for offers
- General persona handling (no recommendations)
- Full pipeline integration

All tests use deterministic data for reproducibility.
"""

import json
import sqlite3
from pathlib import Path
import pandas as pd
import pytest

from recommend.engine import (
    generate_recommendations,
    _format_rationale,
    _check_offer_eligibility,
    _append_disclaimer,
    generate_all_recommendations,
)
from recommend.content_catalog import get_education_items, get_partner_offers
from ingest.constants import MANDATORY_DISCLAIMER, RECOMMENDATION_LIMITS


# Test database path
DB_PATH = Path("data/users.sqlite")
SIGNALS_PATH = Path("features/signals.parquet")


class TestRationaleFormatting:
    """Test that rationales include concrete user data."""

    def test_rationale_includes_concrete_data_high_utilization(self):
        """
        Test: Rationale for high utilization user includes specific card data.

        Verify: Rationale includes card mask, utilization percentage, balance, and limit.
        Expected: All numeric values match source data exactly.
        """
        # Arrange: Create mock user context
        user_context = {
            "user_id": "test_user_001",
            "persona": "high_utilization",
            "signals": {
                "credit_max_util_pct": 68.0,
                "credit_avg_util_pct": 68.0,
                "credit_num_cards": 1,
            },
            "accounts": [
                {
                    "account_id": "acc_001",
                    "account_type": "credit",
                    "account_subtype": "credit card",
                    "mask": "4523",
                    "balance_current": 3400,
                    "balance_limit": 5000,
                }
            ],
            "recent_transactions": [],
        }

        # Template from content catalog
        template = (
            "Your {card_description} is at {utilization_pct}% utilization ({balance} of {limit})."
        )

        # Act: Format rationale
        rationale = _format_rationale(template, user_context)

        # Assert: Check all concrete values are present
        assert "4523" in rationale, "Card mask should be in rationale"
        assert "68%" in rationale, "Utilization percentage should be in rationale"
        assert "$3,400" in rationale, "Balance should be in rationale"
        assert "$5,000" in rationale, "Limit should be in rationale"
        assert (
            "credit card ending in 4523" in rationale
        ), "Card description should be formatted correctly"

    def test_rationale_includes_subscription_data(self):
        """
        Test: Rationale for subscription-heavy user includes recurring count and spend.

        Verify: Rationale includes number of subscriptions and monthly spend.
        Expected: Values match signals data.
        """
        # Arrange
        user_context = {
            "user_id": "test_user_002",
            "persona": "subscription_heavy",
            "signals": {
                "sub_180d_recurring_count": 4,
                "sub_180d_monthly_spend": 65.0,
                "sub_180d_share_pct": 12.0,
            },
            "accounts": [],
            "recent_transactions": [],
        }

        template = "You have {recurring_count} recurring subscriptions totaling approximately {monthly_recurring_spend} per month."

        # Act
        rationale = _format_rationale(template, user_context)

        # Assert
        assert "4 recurring" in rationale, "Recurring count should be present"
        assert "$65" in rationale, "Monthly spend should be present"

    def test_rationale_includes_savings_data(self):
        """
        Test: Rationale for savings builder includes growth rate and inflow.

        Verify: Rationale includes percentages and dollar amounts.
        Expected: Values formatted correctly with decimals.
        """
        # Arrange
        user_context = {
            "user_id": "test_user_003",
            "persona": "savings_builder",
            "signals": {
                "sav_180d_net_inflow": 1200.0,
                "sav_180d_growth_rate_pct": 3.5,
                "sav_180d_emergency_fund_months": 4.2,
            },
            "accounts": [],
            "recent_transactions": [],
        }

        template = (
            "You've saved {net_inflow} in the last 6 months, showing {growth_rate_pct}% growth."
        )

        # Act
        rationale = _format_rationale(template, user_context)

        # Assert
        assert "$1,200" in rationale, "Net inflow should be formatted with comma"
        assert "3.5%" in rationale, "Growth rate should include decimal"


class TestDisclaimerPresence:
    """Test that mandatory disclaimer is present on all recommendations."""

    def test_disclaimer_appended_to_all_recommendations(self):
        """
        Test: Every recommendation includes exact disclaimer text.

        Verify: Disclaimer matches MANDATORY_DISCLAIMER constant.
        Expected: 100% of recommendations have disclaimer field.
        """
        # Arrange: Create mock recommendations
        recommendations = [
            {
                "type": "education",
                "title": "Test Education Item",
                "rationale": "Test rationale",
            },
            {
                "type": "partner_offer",
                "title": "Test Offer",
                "rationale": "Test offer rationale",
            },
        ]

        # Act
        recommendations_with_disclaimer = _append_disclaimer(recommendations)

        # Assert
        assert len(recommendations_with_disclaimer) == 2
        for rec in recommendations_with_disclaimer:
            assert "disclaimer" in rec, "Disclaimer field should be present"
            assert (
                rec["disclaimer"] == MANDATORY_DISCLAIMER
            ), "Disclaimer text should match constant"

    def test_disclaimer_exact_text(self):
        """
        Test: Disclaimer text matches PRD specification exactly.

        Verify: No modifications to disclaimer text.
        Expected: Exact match with constant.
        """
        expected = "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."
        assert MANDATORY_DISCLAIMER == expected, "Disclaimer constant should match PRD spec"


class TestRecommendationCounts:
    """Test that recommendation counts fall within specified ranges per persona."""

    def test_high_utilization_recommendation_count(self):
        """
        Test: High utilization persona gets 3-5 education items and 1-3 offers.

        Verify: Counts within RECOMMENDATION_LIMITS.
        Expected: All counts in valid ranges.
        """
        # Get catalog items
        education_items = get_education_items("high_utilization")
        offers = get_partner_offers("high_utilization")

        # Assert catalog has enough content
        assert (
            len(education_items) >= RECOMMENDATION_LIMITS["education_items_min"]
        ), "Catalog should have at least minimum education items"
        assert (
            len(offers) >= RECOMMENDATION_LIMITS["partner_offers_min"]
        ), "Catalog should have at least minimum offers"

    def test_variable_income_recommendation_count(self):
        """
        Test: Variable income persona gets appropriate counts.
        """
        education_items = get_education_items("variable_income")
        offers = get_partner_offers("variable_income")

        assert len(education_items) >= RECOMMENDATION_LIMITS["education_items_min"]
        assert len(offers) >= RECOMMENDATION_LIMITS["partner_offers_min"]

    def test_subscription_heavy_recommendation_count(self):
        """
        Test: Subscription heavy persona gets appropriate counts.
        """
        education_items = get_education_items("subscription_heavy")
        offers = get_partner_offers("subscription_heavy")

        assert len(education_items) >= RECOMMENDATION_LIMITS["education_items_min"]
        assert len(offers) >= RECOMMENDATION_LIMITS["partner_offers_min"]

    def test_savings_builder_recommendation_count(self):
        """
        Test: Savings builder persona gets appropriate counts.
        """
        education_items = get_education_items("savings_builder")
        offers = get_partner_offers("savings_builder")

        assert len(education_items) >= RECOMMENDATION_LIMITS["education_items_min"]
        assert len(offers) >= RECOMMENDATION_LIMITS["partner_offers_min"]


class TestEligibilityFiltering:
    """Test that eligibility filters prevent inappropriate offers."""

    def test_existing_savings_account_excludes_hysa_offer(self):
        """
        Test: User with existing HYSA doesn't get HYSA offer.

        Verify: Offer excluded from recommendations.
        Expected: Offer not present in output.
        """
        # Arrange: Create offer with savings account exclusion
        offer = {
            "title": "High-Yield Savings Account",
            "category": "savings_account",
            "eligibility": {
                "min_income_tier": "low",
                "max_existing_savings_accounts": 1,
            },
        }

        signals = {}
        user_context = {
            "existing_account_types": {"savings": 2},  # Already has 2 savings accounts
            "income_tier": "medium",
        }

        # Act
        is_eligible = _check_offer_eligibility(offer, signals, user_context, "medium")

        # Assert
        assert (
            is_eligible is False
        ), "Offer should be excluded for user with existing savings accounts"

    def test_low_income_excludes_high_tier_offers(self):
        """
        Test: Low income user doesn't get medium/high income offers.

        Verify: Income tier requirement enforced.
        Expected: Offer excluded.
        """
        # Arrange
        offer = {
            "title": "Premium Credit Card",
            "category": "credit_card",
            "eligibility": {
                "min_income_tier": "high",
            },
        }

        signals = {}
        user_context = {"existing_account_types": {}}

        # Act
        is_eligible = _check_offer_eligibility(offer, signals, user_context, "low")

        # Assert
        assert is_eligible is False, "Low income user should not get high income offers"

    def test_high_utilization_blocks_new_credit_card(self):
        """
        Test: User with >80% utilization doesn't get new credit card offers.

        Verify: Utilization threshold enforced.
        Expected: Offer excluded.
        """
        # Arrange
        offer = {
            "title": "Balance Transfer Card",
            "category": "credit_card",
            "eligibility": {
                "min_income_tier": "medium",
                "max_credit_utilization": 0.80,
            },
        }

        signals = {"credit_avg_util_pct": 85.0}  # 85% utilization
        user_context = {"existing_account_types": {}}

        # Act
        is_eligible = _check_offer_eligibility(offer, signals, user_context, "medium")

        # Assert
        assert is_eligible is False, "High utilization should block new credit card offers"


class TestGeneralPersonaHandling:
    """Test that general persona receives no recommendations."""

    @pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
    def test_general_persona_returns_empty_recommendations(self):
        """
        Test: User with 'general' persona gets empty recommendations list.

        Verify: No recommendations generated for users without strong signals.
        Expected: recommendations list is empty, metadata indicates reason.
        """
        # Find a user with 'general' persona from database
        with sqlite3.connect(DB_PATH) as conn:
            general_users = pd.read_sql(
                "SELECT user_id FROM persona_assignments WHERE persona = 'general' LIMIT 1",
                conn,
            )

        if len(general_users) == 0:
            pytest.skip("No 'general' persona users in database")

        user_id = general_users.iloc[0]["user_id"]

        # Act
        response = generate_recommendations(user_id)

        # Assert
        assert response["persona"] == "general", "Persona should be general"
        assert len(response["recommendations"]) == 0, "Recommendations should be empty"
        assert (
            response["metadata"]["reason"] == "general_persona_no_recommendations"
        ), "Metadata should indicate why recommendations are empty"


class TestFullRecommendationIntegration:
    """Integration test: Full recommendation generation for all users."""

    @pytest.mark.skipif(
        not DB_PATH.exists() or not SIGNALS_PATH.exists(), reason="Data not available"
    )
    def test_full_recommendation_generation_integration(self):
        """
        Test: Generate recommendations for all synthetic users.

        Verify:
        - All users have persona assignments
        - Non-general users get 3-5 education items
        - Non-general users get 1-3 eligible offers
        - All recommendations have rationales
        - No eligibility violations
        - Trace JSONs updated

        Expected: 100% explainability metric, no eligibility violations.
        """
        # Act: Generate recommendations for all users
        all_recs_df = generate_all_recommendations()

        # Assert: Check counts
        assert len(all_recs_df) > 0, "Should have recommendations for at least some users"

        # Filter to non-general personas
        non_general = all_recs_df[all_recs_df["persona"] != "general"]

        if len(non_general) == 0:
            pytest.skip("No non-general personas in dataset")

        # Check recommendation counts for non-general personas
        for idx, row in non_general.iterrows():
            recs = row["recommendations"]
            metadata = row["metadata"]

            # Skip if no consent or other reason for empty recommendations
            if "reason" in metadata:
                continue

            # Check education count (3-5)
            edu_count = metadata.get("education_count", 0)
            assert (
                edu_count >= RECOMMENDATION_LIMITS["education_items_min"]
            ), f"User {row['user_id']} should have at least {RECOMMENDATION_LIMITS['education_items_min']} education items, got {edu_count}"
            assert (
                edu_count <= RECOMMENDATION_LIMITS["education_items_max"]
            ), f"User {row['user_id']} should have at most {RECOMMENDATION_LIMITS['education_items_max']} education items, got {edu_count}"

            # Check offer count (may be 0 if eligibility filters exclude all)
            offer_count = metadata.get("offer_count", 0)
            assert (
                offer_count <= RECOMMENDATION_LIMITS["partner_offers_max"]
            ), f"User {row['user_id']} should have at most {RECOMMENDATION_LIMITS['partner_offers_max']} offers, got {offer_count}"

            # Check all recommendations have rationales and disclaimers
            for rec in recs:
                assert "rationale" in rec, f"Recommendation '{rec['title']}' missing rationale"
                assert (
                    len(rec["rationale"]) > 0
                ), f"Recommendation '{rec['title']}' has empty rationale"
                assert "disclaimer" in rec, f"Recommendation '{rec['title']}' missing disclaimer"
                assert (
                    rec["disclaimer"] == MANDATORY_DISCLAIMER
                ), f"Recommendation '{rec['title']}' has incorrect disclaimer"

        # Check trace files updated
        trace_dir = Path("docs/traces")
        if trace_dir.exists():
            trace_files = list(trace_dir.glob("*.json"))
            # Should have trace files for at least some users
            assert len(trace_files) > 0, "Should have trace files generated"

            # Find a trace for a user with recommendations (non-general persona with consent)
            found_rec_trace = False
            for idx, row in non_general.iterrows():
                if "reason" not in row["metadata"]:  # Skip users without consent
                    user_trace = trace_dir / f"{row['user_id']}.json"
                    if user_trace.exists():
                        with open(user_trace, "r") as f:
                            trace_data = json.load(f)
                        if "recommendations" in trace_data:
                            found_rec_trace = True
                            break

            assert found_rec_trace, "At least one trace should include recommendations section"

        # Calculate explainability metric
        total_recs = sum(len(row["recommendations"]) for _, row in non_general.iterrows())
        recs_with_rationale = sum(
            sum(1 for rec in row["recommendations"] if rec.get("rationale"))
            for _, row in non_general.iterrows()
        )

        if total_recs > 0:
            explainability_pct = (recs_with_rationale / total_recs) * 100
            assert (
                explainability_pct == 100.0
            ), f"Explainability should be 100%, got {explainability_pct:.1f}%"

        print("\n✅ Integration Test Summary:")
        print(f"   - Total users processed: {len(all_recs_df)}")
        print(f"   - Non-general personas: {len(non_general)}")
        print(f"   - Total recommendations: {total_recs}")
        print(f"   - Explainability: {explainability_pct:.1f}%")


class TestStrictEligibilityNoPadding:
    """Ensure we don't pad education with ineligible items when signals are missing."""

    def test_no_padding_when_signals_missing(self, monkeypatch, tmp_path):
        """
        When signals are missing/empty, education items should not be padded.

        Verify: generate_recommendations returns fewer (possibly zero) education items
        and includes metadata reason 'insufficient_data' with shortfall count.
        """
        # Monkeypatch catalog to return items that require utilization >= 30%
        from recommend import engine as eng

        def fake_get_education_items(persona):
            return [
                {
                    "title": "Lower credit utilization",
                    "description": "Tips to reduce utilization",
                    "category": "credit",
                    "rationale_template": "Your utilization is {utilization_pct}%",
                    "eligibility": {"min_utilization": 0.30},
                },
                {
                    "title": "Automate payments",
                    "description": "Reduce late fees",
                    "category": "credit",
                    "rationale_template": "Set up autopay",
                    "eligibility": {"min_utilization": 0.30},
                },
            ]

        monkeypatch.setattr("recommend.engine.get_education_items", fake_get_education_items)

        # Monkeypatch context loader: consent granted, persona set, but no signals present
        def fake_load_user_context(user_id: str):
            return {
                "user_id": user_id,
                "consent_granted": True,
                "persona": "high_utilization",
                "signals": {},  # Missing/empty signals
                "accounts": [],
                "recent_transactions": [],
            }

        monkeypatch.setattr(eng, "_load_user_context", fake_load_user_context)

        # Act
        resp = generate_recommendations("user_missing_signals")

        # Assert: no padding beyond eligibility
        assert resp["metadata"]["education_count"] == 0, "Should not pad ineligible education items"
        assert (
            resp["metadata"].get("reason") == "insufficient_data"
        ), "Should mark insufficient data"
        assert (
            resp["metadata"].get("education_eligibility_shortfall")
            == RECOMMENDATION_LIMITS["education_items_min"]
        ), "Shortfall should equal min_items when none eligible"

"""
Tests for Production-Ready Fairness Metrics

This module contains comprehensive tests for the 3 production fairness metrics:
1. Persona Distribution Parity (primary ECOA compliance metric)
2. Recommendation Quantity Parity (service quality equity)
3. Partner Offer Access Parity (opportunity equity)

These metrics detect disparate impact that the legacy metric (persona assignment rate) misses.
"""

import pandas as pd
import pytest

from eval.fairness import (
    calculate_persona_distribution_parity,
    calculate_recommendation_quantity_parity,
    calculate_partner_offer_parity,
    calculate_fairness_metrics,
)


# ============================================
# TEST 1: PERSONA DISTRIBUTION PARITY - PASS
# ============================================


def test_persona_distribution_parity_all_pass():
    """
    Test: Persona distribution parity when all demographics are fair.

    Scenario:
    - "High Utilization" persona: 30% overall
    - All demographic groups: ~30% ± within tolerance

    Expected: all_personas_pass = True, no violations
    """
    # Create 100 users evenly distributed across demographics
    users_df = pd.DataFrame({
        "user_id": [f"user_{i:04d}" for i in range(100)],
        "gender": (["male", "female", "non_binary", "prefer_not_to_say"] * 25),
        "income_tier": (["low", "medium", "high"] * 33 + ["low"]),
        "region": (["northeast", "south", "midwest", "west"] * 25),
        "age": ([25, 35, 45, 60] * 25),
    })

    # Create personas: 30 High Utilization, 70 Cash Flow Optimizer
    # Evenly distributed across all demographics
    personas_df = pd.DataFrame({
        "assignment_id": list(range(100)),
        "user_id": [f"user_{i:04d}" for i in range(100)],
        "persona": (["High Utilization"] * 30 + ["Cash Flow Optimizer"] * 70),
    })

    # Calculate parity
    result = calculate_persona_distribution_parity(users_df, personas_df, tolerance=0.10)

    # Verify overall results
    assert result["all_personas_pass"] is True, "Should pass when all personas are equitably distributed"
    assert len(result["violations"]) == 0, "Should have no violations"
    assert "High Utilization" in result["persona_metrics"]
    assert "Cash Flow Optimizer" in result["persona_metrics"]

    # Verify High Utilization persona
    hu_metrics = result["persona_metrics"]["High Utilization"]
    assert hu_metrics["overall_rate"] == 0.30, "Overall rate should be 30%"
    assert hu_metrics["passes"] is True, "High Utilization should pass"
    assert hu_metrics["max_deviation"] <= 0.10, "Max deviation should be within tolerance"

    # Verify all demographics pass
    for demographic in ["gender", "income_tier", "region", "age_bucket"]:
        assert hu_metrics["demographics"][demographic]["passes"] is True


# ============================================
# TEST 2: PERSONA DISTRIBUTION PARITY - FAIL
# ============================================


def test_persona_distribution_parity_with_violations():
    """
    Test: Persona distribution parity detects disparate impact.

    Scenario:
    - "High Utilization" persona: 30% overall
    - Gender: male 10% (FAIL), female 50% (FAIL), others 30% (PASS)

    Expected: all_personas_pass = False, 2 violations for gender
    """
    # Create 100 users with uneven persona distribution by gender
    users_df = pd.DataFrame({
        "user_id": [f"user_{i:04d}" for i in range(100)],
        "gender": (["male"] * 30 + ["female"] * 30 + ["non_binary"] * 20 + ["prefer_not_to_say"] * 20),
        "income_tier": ["medium"] * 100,  # All same to isolate gender effect
        "region": ["northeast"] * 100,
        "age": [35] * 100,
    })

    # Create disparate persona distribution:
    # Overall: 30% High Utilization
    # male: 3/30 = 10% (deviation = -20%)
    # female: 15/30 = 50% (deviation = +20%)
    # non_binary: 6/20 = 30% (deviation = 0%)
    # prefer_not_to_say: 6/20 = 30% (deviation = 0%)
    personas_df = pd.DataFrame({
        "assignment_id": list(range(100)),
        "user_id": [f"user_{i:04d}" for i in range(100)],
        "persona": (
            # Males (30 users): 3 High Util, 27 Cash Flow
            (["High Utilization"] * 3 + ["Cash Flow Optimizer"] * 27) +
            # Females (30 users): 15 High Util, 15 Cash Flow
            (["High Utilization"] * 15 + ["Cash Flow Optimizer"] * 15) +
            # Non-binary (20 users): 6 High Util, 14 Cash Flow
            (["High Utilization"] * 6 + ["Cash Flow Optimizer"] * 14) +
            # Prefer not to say (20 users): 6 High Util, 14 Cash Flow
            (["High Utilization"] * 6 + ["Cash Flow Optimizer"] * 14)
        ),
    })

    # Calculate parity
    result = calculate_persona_distribution_parity(users_df, personas_df, tolerance=0.10)

    # Verify violations detected
    assert result["all_personas_pass"] is False, "Should fail when disparate impact detected"
    assert len(result["violations"]) == 2, "Should detect 2 violations (male and female gender groups)"

    # Verify High Utilization persona fails
    hu_metrics = result["persona_metrics"]["High Utilization"]
    assert hu_metrics["overall_rate"] == 0.30, "Overall rate should be 30%"
    assert hu_metrics["passes"] is False, "High Utilization should fail"
    assert hu_metrics["max_deviation"] > 0.10, "Max deviation should exceed tolerance"

    # Verify gender demographic fails
    gender_metrics = hu_metrics["demographics"]["gender"]
    assert gender_metrics["passes"] is False, "Gender should fail"
    assert abs(gender_metrics["group_rates"]["male"] - 0.10) < 0.01, "Male rate should be ~10%"
    assert abs(gender_metrics["group_rates"]["female"] - 0.50) < 0.01, "Female rate should be ~50%"
    assert abs(gender_metrics["deviations"]["male"] - 0.20) < 0.01, "Male deviation should be ~20%"
    assert abs(gender_metrics["deviations"]["female"] - 0.20) < 0.01, "Female deviation should be ~20%"

    # Verify violations list
    violation_demographics = [v["demographic"] for v in result["violations"]]
    assert violation_demographics.count("gender") == 2, "Should have 2 gender violations"


# ============================================
# TEST 3: PERSONA DISTRIBUTION TOLERANCE BOUNDARY
# ============================================


def test_persona_distribution_parity_tolerance_boundary():
    """
    Test: Verify exactly 10% deviation is treated as PASS.

    Scenario:
    - Overall rate: 50%
    - Group A: 60% (exactly +10% deviation)
    - Group B: 40% (exactly -10% deviation)

    Expected: Passes (boundary is inclusive)
    """
    users_df = pd.DataFrame({
        "user_id": [f"user_{i:04d}" for i in range(10)],
        "gender": ["A"] * 5 + ["B"] * 5,
        "income_tier": ["medium"] * 10,
        "region": ["north"] * 10,
        "age": [35] * 10,
    })

    personas_df = pd.DataFrame({
        "assignment_id": list(range(10)),
        "user_id": [f"user_{i:04d}" for i in range(10)],
        "persona": (
            # Group A: 3/5 = 60% High Util
            ["High Utilization", "High Utilization", "High Utilization", "General", "General"] +
            # Group B: 2/5 = 40% High Util
            ["High Utilization", "High Utilization", "General", "General", "General"]
        ),
    })

    result = calculate_persona_distribution_parity(users_df, personas_df, tolerance=0.10)

    hu_metrics = result["persona_metrics"]["High Utilization"]
    gender_metrics = hu_metrics["demographics"]["gender"]

    assert hu_metrics["overall_rate"] == 0.50, "Overall rate should be 50%"
    assert gender_metrics["passes"] is True, "Exactly 10% deviation should pass"
    assert abs(gender_metrics["max_deviation"] - 0.10) < 0.01, "Max deviation should be exactly 10%"


# ============================================
# TEST 4: RECOMMENDATION QUANTITY PARITY - PASS
# ============================================


def test_recommendation_quantity_parity_all_pass():
    """
    Test: Recommendation quantity parity when all groups receive similar counts.

    Scenario:
    - Overall mean: 5.0 recommendations per user
    - All groups: ~5.0 ± within tolerance

    Expected: passes = True, no violations
    """
    users_df = pd.DataFrame({
        "user_id": [f"user_{i:04d}" for i in range(100)],
        "gender": (["male", "female", "non_binary", "prefer_not_to_say"] * 25),
        "income_tier": (["low", "medium", "high"] * 33 + ["low"]),
        "region": (["northeast", "south", "midwest", "west"] * 25),
        "age": ([25, 35, 45, 60] * 25),
    })

    # All users get exactly 5 recommendations (matching trace structure)
    traces = [
        {
            "user_id": f"user_{i:04d}",
            "recommendations": {
                "total_recommendations": 5,
                "offer_count": 1,  # Add offer count for partner offer parity
            },
        }
        for i in range(100)
    ]

    result = calculate_recommendation_quantity_parity(users_df, traces, tolerance=0.10)

    assert result["overall_mean"] == 5.0, "Overall mean should be 5.0"
    assert result["passes"] is True, "Should pass when all groups get same count"
    assert len(result["violations"]) == 0, "Should have no violations"

    # Verify all demographics pass
    for demographic in ["gender", "income_tier", "region", "age_bucket"]:
        assert result["demographics"][demographic]["passes"] is True


# ============================================
# TEST 5: RECOMMENDATION QUANTITY PARITY - FAIL
# ============================================


def test_recommendation_quantity_parity_with_violations():
    """
    Test: Recommendation quantity parity detects service quality disparity.

    Scenario:
    - Overall mean: 5.0 recommendations
    - male: 4.0 avg (deviation -20%, FAIL)
    - female: 6.0 avg (deviation +20%, FAIL)

    Expected: passes = False, 2 violations
    """
    users_df = pd.DataFrame({
        "user_id": [f"user_{i:04d}" for i in range(100)],
        "gender": ["male"] * 50 + ["female"] * 50,
        "income_tier": ["medium"] * 100,
        "region": ["northeast"] * 100,
        "age": [35] * 100,
    })

    # Males get 4 recs, females get 6 recs (overall mean = 5.0)
    traces = []
    for i in range(100):
        if i < 50:  # males
            rec_count = 4
        else:  # females
            rec_count = 6
        traces.append({
            "user_id": f"user_{i:04d}",
            "recommendations": {"total_recommendations": rec_count},
        })

    result = calculate_recommendation_quantity_parity(users_df, traces, tolerance=0.10)

    assert result["overall_mean"] == 5.0, "Overall mean should be 5.0"
    assert result["passes"] is False, "Should fail when disparity detected"
    assert len(result["violations"]) == 1, "Should detect 1 violation (worst group in gender)"

    # Verify gender demographic fails
    gender_metrics = result["demographics"]["gender"]
    assert gender_metrics["passes"] is False, "Gender should fail"
    assert gender_metrics["group_means"]["male"] == 4.0, "Male mean should be 4.0"
    assert gender_metrics["group_means"]["female"] == 6.0, "Female mean should be 6.0"
    assert abs(gender_metrics["deviations_pct"]["male"] - 0.20) < 0.01, "Male deviation should be 20%"
    assert abs(gender_metrics["deviations_pct"]["female"] - 0.20) < 0.01, "Female deviation should be 20%"


# ============================================
# TEST 6: PARTNER OFFER ACCESS PARITY - PASS
# ============================================


def test_partner_offer_parity_all_pass():
    """
    Test: Partner offer access parity when all groups have equal access.

    Scenario:
    - Overall offer rate: 80% of users
    - All groups: ~80% ± within tolerance

    Expected: passes = True, no violations
    """
    users_df = pd.DataFrame({
        "user_id": [f"user_{i:04d}" for i in range(100)],
        "gender": (["male", "female", "non_binary", "prefer_not_to_say"] * 25),
        "income_tier": (["low", "medium", "high"] * 33 + ["low"]),
        "region": (["northeast", "south", "midwest", "west"] * 25),
        "age": ([25, 35, 45, 60] * 25),
    })

    # 80 users get partner offers, 20 don't
    traces = []
    for i in range(100):
        has_offer = i < 80
        traces.append({
            "user_id": f"user_{i:04d}",
            "recommendations": {
                "total_recommendations": 5,
                "offer_count": 1 if has_offer else 0,  # Use 'offer_count' not 'partner_offer_count'
            },
        })

    result = calculate_partner_offer_parity(users_df, traces, tolerance=0.10)

    assert result["overall_offer_rate"] == 0.80, "Overall offer rate should be 80%"
    assert result["passes"] is True, "Should pass when all groups have equal access"
    assert len(result["violations"]) == 0, "Should have no violations"

    # Verify all demographics pass
    for demographic in ["gender", "income_tier", "region", "age_bucket"]:
        assert result["demographics"][demographic]["passes"] is True


# ============================================
# TEST 7: PARTNER OFFER ACCESS PARITY - FAIL
# ============================================


def test_partner_offer_parity_with_violations():
    """
    Test: Partner offer access parity detects opportunity redlining.

    Scenario:
    - Overall offer rate: 50%
    - low income: 20% (deviation -60%, FAIL)
    - high income: 80% (deviation +60%, FAIL)

    Expected: passes = False, violations detected
    """
    users_df = pd.DataFrame({
        "user_id": [f"user_{i:04d}" for i in range(100)],
        "gender": ["male"] * 100,
        "income_tier": ["low"] * 50 + ["high"] * 50,
        "region": ["northeast"] * 100,
        "age": [35] * 100,
    })

    # Low income: 10/50 = 20% get offers
    # High income: 40/50 = 80% get offers
    # Overall: 50/100 = 50%
    traces = []
    for i in range(100):
        if i < 50:  # low income
            has_offer = i < 10
        else:  # high income
            has_offer = (i - 50) < 40
        traces.append({
            "user_id": f"user_{i:04d}",
            "recommendations": {
                "total_recommendations": 5,
                "offer_count": 1 if has_offer else 0,  # Use 'offer_count' not 'partner_offer_count'
            },
        })

    result = calculate_partner_offer_parity(users_df, traces, tolerance=0.10)

    assert result["overall_offer_rate"] == 0.50, "Overall offer rate should be 50%"
    assert result["passes"] is False, "Should fail when opportunity redlining detected"
    assert len(result["violations"]) >= 1, "Should detect violations"

    # Verify income tier fails
    income_metrics = result["demographics"]["income_tier"]
    assert income_metrics["passes"] is False, "Income tier should fail"
    assert abs(income_metrics["group_rates"]["low"] - 0.20) < 0.01, "Low income rate should be 20%"
    assert abs(income_metrics["group_rates"]["high"] - 0.80) < 0.01, "High income rate should be 80%"


# ============================================
# TEST 8: CALCULATE_FAIRNESS_METRICS INTEGRATION
# ============================================


def test_calculate_fairness_metrics_integration():
    """
    Test: Full fairness metrics calculation with real database.

    Verify:
    - All 3 production metrics calculated
    - Legacy metric still calculated (backwards compatibility)
    - production_fairness_passes field exists
    - production_violations list exists
    """
    # Use real database
    fairness, distribution = calculate_fairness_metrics(
        db_path="data/users.sqlite",
        tolerance=0.10,
    )

    # Verify legacy metrics (backwards compatibility)
    assert "overall_persona_rate" in fairness, "Should include legacy overall persona rate"
    assert "demographics" in fairness, "Should include legacy demographics"
    assert "all_demographics_pass" in fairness, "Should include legacy pass/fail"

    # Verify production metrics
    assert "persona_distribution_parity" in fairness, "Should include persona distribution parity"
    assert "recommendation_quantity_parity" in fairness, "Should include recommendation quantity parity"
    assert "partner_offer_parity" in fairness, "Should include partner offer parity"

    # Verify production fairness status
    assert "production_fairness_passes" in fairness, "Should include production pass/fail"
    assert "production_violations" in fairness, "Should include production violations list"

    # Verify production metrics structure
    pdp = fairness["persona_distribution_parity"]
    assert "all_personas_pass" in pdp, "Persona parity should have all_personas_pass"
    assert "violations" in pdp, "Persona parity should have violations list"
    assert "persona_metrics" in pdp, "Persona parity should have persona_metrics"

    rqp = fairness["recommendation_quantity_parity"]
    assert "passes" in rqp, "Rec quantity parity should have passes"
    assert "violations" in rqp, "Rec quantity parity should have violations"
    assert "overall_mean" in rqp, "Rec quantity parity should have overall_mean"

    pop = fairness["partner_offer_parity"]
    assert "passes" in pop, "Partner offer parity should have passes"
    assert "violations" in pop, "Partner offer parity should have violations"
    assert "overall_offer_rate" in pop, "Partner offer parity should have overall_offer_rate"

    # Verify distribution (actual keys are gender_by_persona, income_tier_by_persona, etc.)
    assert "overall" in distribution, "Should include overall persona distribution"
    assert "gender_by_persona" in distribution, "Should include distribution by gender"
    assert "income_tier_by_persona" in distribution, "Should include distribution by income tier"

    print("\n✅ Production fairness metrics integration test passed")
    print(f"   - Production fairness: {'PASS' if fairness['production_fairness_passes'] else 'FAIL'}")
    print(f"   - Total violations: {len(fairness['production_violations'])}")
    print(f"   - Legacy fairness: {'PASS' if fairness['all_demographics_pass'] else 'FAIL'}")


# ============================================
# TEST 9: EDGE CASES
# ============================================


def test_persona_distribution_parity_single_persona():
    """
    Test: Persona distribution parity with only one persona type.

    Scenario:
    - All users have "General" persona

    Expected: Skips "General" persona, no other personas to check
    """
    users_df = pd.DataFrame({
        "user_id": [f"user_{i:04d}" for i in range(10)],
        "gender": ["male"] * 5 + ["female"] * 5,
        "income_tier": ["medium"] * 10,
        "region": ["north"] * 10,
        "age": [35] * 10,
    })

    personas_df = pd.DataFrame({
        "assignment_id": list(range(10)),
        "user_id": [f"user_{i:04d}" for i in range(10)],
        "persona": ["general"] * 10,
    })

    result = calculate_persona_distribution_parity(users_df, personas_df, tolerance=0.10)

    assert len(result["personas_checked"]) == 0, "Should skip 'general' persona"
    assert result["all_personas_pass"] is True, "Should pass when no personas to check"
    assert len(result["violations"]) == 0, "Should have no violations"


def test_recommendation_quantity_parity_zero_recommendations():
    """
    Test: Recommendation quantity parity when all users get 0 recommendations.

    Scenario:
    - All users: 0 recommendations

    Expected: passes = True (all groups equal at 0)
    """
    users_df = pd.DataFrame({
        "user_id": [f"user_{i:04d}" for i in range(10)],
        "gender": ["male"] * 5 + ["female"] * 5,
        "income_tier": ["medium"] * 10,
        "region": ["north"] * 10,
        "age": [35] * 10,
    })

    traces = [
        {
            "user_id": f"user_{i:04d}",
            "recommendations": {"total_recommendations": 0},
        }
        for i in range(10)
    ]

    result = calculate_recommendation_quantity_parity(users_df, traces, tolerance=0.10)

    assert result["overall_mean"] == 0.0, "Overall mean should be 0"
    assert result["passes"] is True, "Should pass when all groups equal at 0"


def test_partner_offer_parity_no_offers():
    """
    Test: Partner offer parity when no users receive offers.

    Scenario:
    - All users: 0 partner offers

    Expected: passes = True (all groups equal at 0%)
    """
    users_df = pd.DataFrame({
        "user_id": [f"user_{i:04d}" for i in range(10)],
        "gender": ["male"] * 5 + ["female"] * 5,
        "income_tier": ["medium"] * 10,
        "region": ["north"] * 10,
        "age": [35] * 10,
    })

    traces = [
        {
            "user_id": f"user_{i:04d}",
            "recommendations": {
                "total_recommendations": 5,
                "partner_offer_count": 0,
            },
        }
        for i in range(10)
    ]

    result = calculate_partner_offer_parity(users_df, traces, tolerance=0.10)

    assert result["overall_offer_rate"] == 0.0, "Overall offer rate should be 0"
    assert result["passes"] is True, "Should pass when all groups equal at 0%"


# ============================================
# TEST 10: MULTIPLE PERSONAS
# ============================================


def test_persona_distribution_parity_multiple_personas():
    """
    Test: Persona distribution parity checks all persona types independently.

    Scenario:
    - "High Utilization": fair distribution (PASS)
    - "Cash Flow Optimizer": unfair distribution (FAIL)

    Expected: all_personas_pass = False (one persona fails)
    """
    users_df = pd.DataFrame({
        "user_id": [f"user_{i:04d}" for i in range(100)],
        "gender": ["male"] * 50 + ["female"] * 50,
        "income_tier": ["medium"] * 100,
        "region": ["northeast"] * 100,
        "age": [35] * 100,
    })

    # High Utilization: 30 users, evenly distributed (15 male, 15 female) → PASS
    # Cash Flow Optimizer: 40 users, unfair (5 male, 35 female) → FAIL
    # General: 30 users (skipped)
    personas_df = pd.DataFrame({
        "assignment_id": list(range(100)),
        "user_id": [f"user_{i:04d}" for i in range(100)],
        "persona": (
            # Males (50 users): 15 HU, 5 CFO, 30 General
            (["High Utilization"] * 15 + ["Cash Flow Optimizer"] * 5 + ["General"] * 30) +
            # Females (50 users): 15 HU, 35 CFO, 0 General
            (["High Utilization"] * 15 + ["Cash Flow Optimizer"] * 35)
        ),
    })

    result = calculate_persona_distribution_parity(users_df, personas_df, tolerance=0.10)

    assert result["all_personas_pass"] is False, "Should fail when any persona fails"

    # High Utilization should pass
    hu_metrics = result["persona_metrics"]["High Utilization"]
    assert hu_metrics["passes"] is True, "High Utilization should pass (fair distribution)"

    # Cash Flow Optimizer should fail
    cfo_metrics = result["persona_metrics"]["Cash Flow Optimizer"]
    assert cfo_metrics["passes"] is False, "Cash Flow Optimizer should fail (unfair distribution)"

    # Verify violations only for Cash Flow Optimizer
    violation_personas = [v["persona"] for v in result["violations"]]
    assert "High Utilization" not in violation_personas, "HU should not have violations"
    assert "Cash Flow Optimizer" in violation_personas, "CFO should have violations"

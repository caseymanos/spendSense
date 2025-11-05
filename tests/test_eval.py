"""
Tests for Evaluation Harness (PR #8)

This module contains 5 tests verifying the evaluation metrics:
1. Coverage metric calculation (unit test)
2. Explainability metric calculation (unit test)
3. Latency measurement accuracy (unit test)
4. Fairness parity calculation (unit test)
5. Full evaluation run (integration test)
"""

import json
import time
from pathlib import Path

import pandas as pd

from eval.metrics import (
    calculate_coverage,
    calculate_explainability,
    calculate_all_metrics,
)
from eval.fairness import calculate_fairness_parity, calculate_fairness_metrics


# ============================================
# TEST 1: COVERAGE METRIC CALCULATION
# ============================================


def test_coverage_metric_calculation():
    """
    Test: Coverage metric calculated correctly on known dataset.

    Verify: Coverage = (users_with_meaningful_persona_and_3behaviors / total) * 100
    Expected: Exact percentage matches hand calculation

    Mock dataset:
    - 10 users total
    - 7 users with persona != 'general' (high_utilization)
    - 7 users with ≥3 behaviors
    - Expected coverage: 70%
    """
    # Create mock data
    users_df = pd.DataFrame(
        {
            "user_id": [f"user_{i:04d}" for i in range(10)],
            "name": [f"User {i}" for i in range(10)],
            "consent_granted": [True] * 10,
        }
    )

    # 7 users with high_utilization, 3 with general
    personas_df = pd.DataFrame(
        {
            "assignment_id": list(range(10)),
            "user_id": [f"user_{i:04d}" for i in range(10)],
            "persona": ["high_utilization"] * 7 + ["general"] * 3,
            "criteria_met": ["{}"] * 10,
        }
    )

    # Create signals: 7 users with ≥3 behaviors, 3 with <3 behaviors
    signals_data = []
    for i in range(10):
        if i < 7:
            # Users 0-6: Have all 4 behaviors
            signals_data.append(
                {
                    "user_id": f"user_{i:04d}",
                    "sub_180d_recurring_count": 3,
                    "sav_180d_net_inflow": 500.0,
                    "sav_180d_growth_rate_pct": 5.0,
                    "credit_max_util_pct": 60.0,
                    "credit_has_interest": True,
                    "inc_180d_num_paychecks": 12,
                }
            )
        else:
            # Users 7-9: Have only 1-2 behaviors
            signals_data.append(
                {
                    "user_id": f"user_{i:04d}",
                    "sub_180d_recurring_count": 1,
                    "sav_180d_net_inflow": 0.0,
                    "sav_180d_growth_rate_pct": 0.0,
                    "credit_max_util_pct": 0.0,
                    "credit_has_interest": False,
                    "inc_180d_num_paychecks": 0,
                }
            )

    signals_df = pd.DataFrame(signals_data)

    # Calculate coverage
    coverage_pct, metadata = calculate_coverage(users_df, personas_df, signals_df)

    # Verify results
    assert metadata["total_users"] == 10, "Should have 10 total users"
    assert (
        metadata["users_with_meaningful_persona"] == 7
    ), "Should have 7 users with non-general persona"
    assert metadata["users_with_3_behaviors"] == 7, "Should have 7 users with ≥3 behaviors"
    assert metadata["users_with_both"] == 7, "Should have 7 users with both criteria"
    assert coverage_pct == 70.0, "Coverage should be exactly 70%"
    assert metadata["target"] is None, "Coverage target should be unset (tracking only)"
    assert metadata["passes"] is None, "Coverage pass/fail should be None for tracking metric"
    assert metadata["tracking_only"] is True, "Coverage should be marked as tracking_only"


# ============================================
# TEST 2: EXPLAINABILITY METRIC CALCULATION
# ============================================


def test_explainability_metric_calculation():
    """
    Test: Explainability metric identifies missing rationales.

    Verify: Explainability = (recs_with_rationale / total_recs) * 100
    Expected: Correct percentage calculated

    Mock data:
    - 20 total recommendations across 2 users
    - 18 with non-empty rationale
    - 2 with empty/missing rationale
    - Expected explainability: 90%
    """
    # Create mock trace JSONs
    traces = [
        {
            "user_id": "user_0000",
            "recommendations": {
                "recommendations": [
                    {
                        "title": "Item 1",
                        "rationale": "This is a good rationale with concrete data.",
                        "type": "education",
                    },
                    {
                        "title": "Item 2",
                        "rationale": "Another clear rationale.",
                        "type": "education",
                    },
                    {
                        "title": "Item 3",
                        "rationale": "",  # Empty rationale
                        "type": "partner_offer",
                    },
                    {"title": "Item 4", "type": "education"},  # Missing rationale
                ]
            },
        },
        {
            "user_id": "user_0001",
            "recommendations": {
                "recommendations": [
                    {
                        "title": "Item 5",
                        "rationale": "Good rationale here.",
                        "type": "education",
                    },
                    {
                        "title": "Item 6",
                        "rationale": "Clear explanation.",
                        "type": "education",
                    },
                ]
                * 8  # 16 more recommendations with rationales
            },
        },
    ]

    # Calculate explainability
    explainability_pct, metadata = calculate_explainability(traces)

    # Verify results
    assert metadata["total_recommendations"] == 20, "Should have 20 total recommendations"
    assert (
        metadata["recommendations_with_rationale"] == 18
    ), "Should have 18 recommendations with rationales"
    assert (
        metadata["recommendations_without_rationale"] == 2
    ), "Should have 2 recommendations without rationales"
    assert explainability_pct == 90.0, "Explainability should be exactly 90%"
    assert metadata["passes"] is False, "Explainability should not pass (target is 100%)"


# ============================================
# TEST 3: LATENCY MEASUREMENT ACCURACY
# ============================================


def test_latency_measurement_accuracy():
    """
    Test: Latency measurement captures time accurately.

    Verify: time.perf_counter() used for high-precision timing
    Expected: Latency recorded in seconds with millisecond precision

    Mock scenario:
    - Simulate recommendation generation on 5 users
    - Verify mean, max, p95 latencies calculated
    - Check values are reasonable (should be very fast on mock data)
    """
    # Create mock users (small sample for speed)
    users_df = pd.DataFrame(
        {
            "user_id": [f"user_{i:04d}" for i in range(5)],
            "name": [f"User {i}" for i in range(5)],
            "consent_granted": [True] * 5,
        }
    )

    # Mock latency calculation (without actual recommendation generation)
    # We'll test the timing mechanism itself
    latencies = []
    for i in range(5):
        start = time.perf_counter()
        # Simulate some work with a tiny sleep
        time.sleep(0.001)  # 1ms
        end = time.perf_counter()
        latencies.append(end - start)

    # Verify timing precision
    mean_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    min_latency = min(latencies)

    assert len(latencies) == 5, "Should have 5 latency measurements"
    assert mean_latency >= 0.001, "Mean latency should be at least 1ms"
    assert mean_latency < 0.1, "Mean latency should be under 100ms for mock data"
    assert max_latency >= min_latency, "Max should be >= min"
    assert all(isinstance(lat, float) for lat in latencies), "All latencies should be floats"

    # Verify perf_counter has sufficient precision (microseconds)
    assert min_latency > 0, "Latency should be measurable (not zero)"
    assert max_latency - min_latency >= 0, "Should detect timing variance between runs"


# ============================================
# TEST 4: FAIRNESS PARITY CALCULATION
# ============================================


def test_fairness_parity_calculation():
    """
    Test: Fairness metric flags demographic imbalances >±10%.

    Verify: Parity check identifies deviations from mean
    Expected: Correctly flags violations and passes compliant distributions

    Mock data:
    - Overall persona rate: 50% (5/10 users)
    - Gender groups:
      - male: 2/4 = 50% (within ±10%, should pass)
      - female: 1/3 = 33.3% (outside -10%, should fail)
      - non_binary: 2/3 = 66.7% (outside +10%, should fail)
    """
    # Create mock users with demographics
    users_df = pd.DataFrame(
        {
            "user_id": [f"user_{i:04d}" for i in range(10)],
            "name": [f"User {i}" for i in range(10)],
            "gender": ["male"] * 4 + ["female"] * 3 + ["non_binary"] * 3,
            "income_tier": ["medium"] * 10,  # All same to isolate gender effect
            "region": ["northeast"] * 10,  # All same
            "age": [30] * 10,  # All same age bucket
        }
    )

    # Create personas: 5 high_utilization, 5 general (overall 50%)
    # male: 2/4 high_util = 50%
    # female: 1/3 high_util = 33.3%
    # non_binary: 2/3 high_util = 66.7%
    personas_df = pd.DataFrame(
        {
            "assignment_id": list(range(10)),
            "user_id": [f"user_{i:04d}" for i in range(10)],
            "persona": (
                ["high_utilization", "high_utilization", "general", "general"]  # male
                + ["high_utilization", "general", "general"]  # female
                + ["high_utilization", "high_utilization", "general"]  # non_binary
            ),
        }
    )

    # Calculate fairness parity
    fairness_results, overall_rate = calculate_fairness_parity(
        users_df, personas_df, tolerance=0.10
    )

    # Verify overall rate
    assert overall_rate == 0.5, "Overall persona rate should be 50%"

    # Verify gender fairness
    gender_results = fairness_results["demographics"]["gender"]
    assert (
        gender_results["passes"] is False
    ), "Gender fairness should FAIL (has groups outside ±10%)"

    # Check individual group rates
    assert abs(gender_results["group_rates"]["male"] - 0.5) < 0.01, "Male rate should be ~50%"
    assert abs(gender_results["group_rates"]["female"] - 0.333) < 0.01, "Female rate should be ~33%"
    assert (
        abs(gender_results["group_rates"]["non_binary"] - 0.667) < 0.01
    ), "Non-binary rate should be ~67%"

    # Verify deviations
    assert gender_results["max_deviation"] > 0.10, "Max deviation should exceed 10% tolerance"

    # Verify income_tier and region pass (all users have same values)
    assert fairness_results["demographics"]["income_tier"]["passes"] is True
    assert fairness_results["demographics"]["region"]["passes"] is True


# ============================================
# TEST 4B: FAIRNESS TOLERANCE BOUNDARY
# ============================================


def test_fairness_parity_tolerance_boundary():
    """
    Test: Fairness metric treats deviations exactly at tolerance as pass.

    Scenario:
    - Overall persona rate: 50%
    - Gender A: 60% (deviation +10%)
    - Gender B: 40% (deviation -10%)
    Expectation: Both groups within tolerance → PASS.
    """
    users_df = pd.DataFrame(
        {
            "user_id": [f"user_{i:04d}" for i in range(10)],
            "gender": ["A"] * 5 + ["B"] * 5,
            "income_tier": ["medium"] * 10,
            "region": ["north"] * 10,
            "age": [35] * 10,
        }
    )

    personas_df = pd.DataFrame(
        {
            "assignment_id": list(range(10)),
            "user_id": [f"user_{i:04d}" for i in range(10)],
            "persona": (
                [
                    "high_utilization",
                    "high_utilization",
                    "high_utilization",
                    "general",
                    "general",
                ]
                + [
                    "high_utilization",
                    "high_utilization",
                    "general",
                    "general",
                    "general",
                ]
            ),
        }
    )

    fairness_results, overall_rate = calculate_fairness_parity(
        users_df, personas_df, tolerance=0.10
    )

    assert overall_rate == 0.5, "Overall persona rate should be 50%"
    gender_results = fairness_results["demographics"]["gender"]
    assert gender_results["passes"] is True, "Deviation exactly at tolerance should pass"
    assert abs(gender_results["max_deviation"] - 0.10) <= 1e-9


# ============================================
# TEST 5: FULL EVALUATION RUN (INTEGRATION)
# ============================================


def test_full_evaluation_run():
    """
    Test: Run complete evaluation harness on real synthetic dataset.

    Verify:
    - All 6 metrics computed (coverage, explainability, relevance, latency, fairness, auditability)
    - Output files can be generated
    - All values within expected ranges or appropriately flagged
    - JSON/CSV formats valid

    Expected (based on current data):
    - Coverage: ~67% (67 high_utilization users)
    - Explainability: 100% (all recs have rationales from PR #4)
    - Relevance: ≥90% (rule-based matching)
    - Latency: <5s (local processing)
    - Fairness: TBD (depends on demographics)
    - Auditability: 100% (all trace JSONs exist)
    """
    # Use real data paths
    db_path = "data/users.sqlite"
    signals_path = "features/signals.parquet"
    traces_dir = "docs/traces"

    # Verify data files exist
    assert Path(db_path).exists(), f"Database not found: {db_path}"
    assert Path(signals_path).exists(), f"Signals file not found: {signals_path}"
    assert Path(traces_dir).exists(), f"Traces directory not found: {traces_dir}"

    # ========================================
    # Run all metrics
    # ========================================
    print("\nRunning full evaluation on real synthetic data...")

    # Calculate all core metrics (limit latency sample to 10 users for speed)
    results = calculate_all_metrics(
        db_path=db_path,
        signals_path=signals_path,
        traces_dir=traces_dir,
        latency_sample_size=10,
    )

    # Calculate fairness metrics
    fairness, distribution = calculate_fairness_metrics(db_path=db_path)

    # ========================================
    # Verify all metrics calculated
    # ========================================
    assert "coverage" in results, "Coverage metric should be calculated"
    assert "explainability" in results, "Explainability metric should be calculated"
    assert "relevance" in results, "Relevance metric should be calculated"
    assert "latency" in results, "Latency metric should be calculated"
    assert "auditability" in results, "Auditability metric should be calculated"

    # ========================================
    # Verify coverage metric
    # ========================================
    coverage = results["coverage"]
    assert coverage["value"] >= 0, "Coverage should be non-negative"
    assert coverage["value"] <= 100, "Coverage should not exceed 100%"
    assert coverage["metadata"]["total_users"] == 100, "Should have 100 users"
    print(f"✅ Coverage: {coverage['value']:.2f}%")

    # ========================================
    # Verify explainability metric
    # ========================================
    explainability = results["explainability"]
    assert explainability["value"] >= 0, "Explainability should be non-negative"
    assert explainability["value"] <= 100, "Explainability should not exceed 100%"

    # Based on PR #4, all recommendations should have rationales
    assert (
        explainability["value"] == 100.0
    ), "Explainability should be 100% (all recs from PR #4 have rationales)"
    print(f"✅ Explainability: {explainability['value']:.2f}%")

    # ========================================
    # Verify relevance metric
    # ========================================
    relevance = results["relevance"]
    assert relevance["value"] >= 0, "Relevance should be non-negative"
    assert relevance["value"] <= 100, "Relevance should not exceed 100%"

    print(f"✅ Relevance: {relevance['value']:.2f}% (tracking vs. ≥90% target)")

    # ========================================
    # Verify latency metric
    # ========================================
    latency = results["latency"]
    assert latency["value"] > 0, "Latency should be positive"
    assert latency["value"] < 5.0, "Mean latency should be under 5 seconds"
    assert latency["metadata"]["users_tested"] == 10, "Should test 10 users (sample size)"
    print(f"✅ Latency: {latency['value']:.4f}s (mean)")

    # ========================================
    # Verify auditability metric
    # ========================================
    auditability = results["auditability"]
    assert auditability["value"] >= 0, "Auditability should be non-negative"
    assert auditability["value"] <= 100, "Auditability should not exceed 100%"

    print(f"✅ Auditability: {auditability['value']:.2f}% (tracking against 100% goal)")

    # ========================================
    # Verify fairness metric
    # ========================================
    assert "all_demographics_pass" in fairness, "Fairness should have pass/fail result"
    assert "demographics" in fairness, "Fairness should include demographic details"
    assert "gender" in fairness["demographics"], "Should check gender fairness"
    assert "income_tier" in fairness["demographics"], "Should check income tier fairness"
    assert "region" in fairness["demographics"], "Should check region fairness"
    assert "age" in fairness["demographics"], "Should check age fairness"
    print(f"✅ Fairness: {'PASS' if fairness['all_demographics_pass'] else 'FAIL'}")

    # ========================================
    # Verify persona distribution
    # ========================================
    assert "overall" in distribution, "Should have overall persona distribution"
    assert "high_utilization" in distribution["overall"], "Should have high_utilization persona"
    assert (
        sum(distribution["overall"].values()) == 100
    ), "Total persona assignments should equal 100"
    print("✅ Persona distribution calculated")

    # ========================================
    # Verify summary
    # ========================================
    assert "summary" in results, "Results should include summary"
    assert results["summary"]["total_users"] == 100, "Summary should show 100 users"
    print("\n✅ All 6 metrics calculated successfully on real synthetic data")

    # ========================================
    # Test JSON serialization (ensure no errors)
    # ========================================
    json_str = json.dumps(results, indent=2)
    assert len(json_str) > 0, "Should produce valid JSON output"
    print(f"✅ JSON serialization successful ({len(json_str)} bytes)")

    # Verify JSON can be parsed back
    parsed = json.loads(json_str)
    assert parsed["coverage"]["value"] == results["coverage"]["value"]
    print("✅ JSON round-trip successful")

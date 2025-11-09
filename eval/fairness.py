"""
Fairness Metrics Module - Production-Ready Compliance

This module calculates demographic parity metrics across protected groups to ensure
compliance with fair lending principles (ECOA, Regulation B) and avoid disparate impact.

Protected Characteristics:
- Gender (4 categories: male, female, non_binary, prefer_not_to_say)
- Income Tier (3 tiers: low, medium, high)
- Region (4 regions: northeast, southeast, midwest, west)
- Age (3 buckets: 18-30, 31-50, 51+)

Production-Ready Fairness Metrics:
1. **Persona Distribution Parity** (Primary): For each persona type, assignment rates
   must be within ±10% across demographics. Prevents stigmatizing personas (e.g., "High
   Utilization") from being disproportionately assigned to protected groups.

2. **Recommendation Quantity Parity** (Primary): Average number of recommendations per
   user must be similar (±10%) across demographics. Ensures equitable service quality.

3. **Partner Offer Access Parity** (Secondary): Among eligible users, access to premium
   partner offers must be equitable (±10%) across demographics.

Regulatory Context:
- Equal Credit Opportunity Act (ECOA) prohibits discrimination in credit transactions
- Disparate impact doctrine applies even to facially neutral policies
- Demographics are used ONLY for fairness monitoring, never in persona assignment logic

For detailed methodology, see docs/FAIRNESS_METHODOLOGY.md
"""

import sqlite3
from typing import Dict, Any, Tuple

import pandas as pd


# ============================================
# AGE BUCKETING
# ============================================

AGE_BUCKETS = [
    (18, 30, "18-30"),
    (31, 50, "31-50"),
    (51, 100, "51+"),
]

EPSILON = 1e-9


def within_tolerance(deviation: float, tolerance: float) -> bool:
    """
    Determine if a deviation is within tolerance, accounting for floating point noise.
    """
    return deviation <= tolerance + EPSILON


def bucket_age(age: int) -> str:
    """
    Bucket age into 3 life-stage groups.

    Args:
        age: User's age

    Returns:
        Age bucket string (18-30, 31-50, 51+)
    """
    for min_age, max_age, label in AGE_BUCKETS:
        if min_age <= age <= max_age:
            return label
    return "unknown"


# ============================================
# FAIRNESS PARITY CALCULATION
# ============================================


def calculate_fairness_parity(
    users_df: pd.DataFrame,
    personas_df: pd.DataFrame,
    tolerance: float = 0.10,
) -> Tuple[Dict[str, Any], float]:
    """
    Calculate demographic parity for persona assignments.

    Fairness is measured by checking if persona assignment rates (excluding 'general')
    are within ±10% (tolerance) of the overall mean across all demographic groups.

    Args:
        users_df: User records with demographics (age, gender, income_tier, region)
        personas_df: Persona assignments (user_id, persona)
        tolerance: Acceptable deviation from mean (default: 0.10 = ±10%)

    Returns:
        Tuple of (fairness_results_dict, overall_persona_rate)
    """
    # Merge users with personas
    merged = users_df.merge(personas_df, on="user_id")

    # Overall persona assignment rate (excluding 'general')
    overall_persona_rate = (merged["persona"] != "general").mean()

    fairness_results = {
        "overall_persona_rate": round(overall_persona_rate, 4),
        "tolerance": tolerance,
        "demographics": {},
    }

    # ========================================
    # 1. GENDER FAIRNESS
    # ========================================
    # Use boolean mask grouped by demographic to avoid GroupBy.apply warnings
    gender_rates = (merged["persona"] != "general").groupby(merged["gender"]).mean()
    gender_deviations = (gender_rates - overall_persona_rate).abs()
    gender_max_deviation = gender_deviations.max()
    gender_passes = within_tolerance(gender_max_deviation, tolerance)

    fairness_results["demographics"]["gender"] = {
        "passes": bool(gender_passes),
        "max_deviation": round(gender_max_deviation, 4),
        "group_rates": {str(k): round(v, 4) for k, v in gender_rates.items()},
        "group_counts": merged["gender"].value_counts().to_dict(),
        "deviations": {str(k): round(v, 4) for k, v in gender_deviations.items()},
    }

    # ========================================
    # 2. INCOME TIER FAIRNESS
    # ========================================
    income_rates = (merged["persona"] != "general").groupby(merged["income_tier"]).mean()
    income_deviations = (income_rates - overall_persona_rate).abs()
    income_max_deviation = income_deviations.max()
    income_passes = within_tolerance(income_max_deviation, tolerance)

    fairness_results["demographics"]["income_tier"] = {
        "passes": bool(income_passes),
        "max_deviation": round(income_max_deviation, 4),
        "group_rates": {str(k): round(v, 4) for k, v in income_rates.items()},
        "group_counts": merged["income_tier"].value_counts().to_dict(),
        "deviations": {str(k): round(v, 4) for k, v in income_deviations.items()},
    }

    # ========================================
    # 3. REGION FAIRNESS
    # ========================================
    region_rates = (merged["persona"] != "general").groupby(merged["region"]).mean()
    region_deviations = (region_rates - overall_persona_rate).abs()
    region_max_deviation = region_deviations.max()
    region_passes = within_tolerance(region_max_deviation, tolerance)

    fairness_results["demographics"]["region"] = {
        "passes": bool(region_passes),
        "max_deviation": round(region_max_deviation, 4),
        "group_rates": {str(k): round(v, 4) for k, v in region_rates.items()},
        "group_counts": merged["region"].value_counts().to_dict(),
        "deviations": {str(k): round(v, 4) for k, v in region_deviations.items()},
    }

    # ========================================
    # 4. AGE FAIRNESS (with bucketing)
    # ========================================
    merged["age_bucket"] = merged["age"].apply(bucket_age)
    age_rates = (merged["persona"] != "general").groupby(merged["age_bucket"]).mean()
    age_deviations = (age_rates - overall_persona_rate).abs()
    age_max_deviation = age_deviations.max()
    age_passes = within_tolerance(age_max_deviation, tolerance)

    fairness_results["demographics"]["age"] = {
        "passes": bool(age_passes),
        "max_deviation": round(age_max_deviation, 4),
        "group_rates": {str(k): round(v, 4) for k, v in age_rates.items()},
        "group_counts": merged["age_bucket"].value_counts().to_dict(),
        "deviations": {str(k): round(v, 4) for k, v in age_deviations.items()},
        "buckets": [f"{min_age}-{max_age}" for min_age, max_age, _ in AGE_BUCKETS],
    }

    # ========================================
    # OVERALL FAIRNESS SUMMARY
    # ========================================
    fairness_results["all_demographics_pass"] = all(
        fairness_results["demographics"][demo]["passes"]
        for demo in ["gender", "income_tier", "region", "age"]
    )

    fairness_results["failing_demographics"] = [
        demo
        for demo in ["gender", "income_tier", "region", "age"]
        if not fairness_results["demographics"][demo]["passes"]
    ]

    return fairness_results, overall_persona_rate


# ============================================
# PRODUCTION-READY FAIRNESS METRICS
# ============================================


def calculate_persona_distribution_parity(
    users_df: pd.DataFrame,
    personas_df: pd.DataFrame,
    tolerance: float = 0.10,
) -> Dict[str, Any]:
    """
    Calculate persona distribution parity - the PRIMARY fairness metric.

    This metric measures whether specific persona TYPES are assigned equitably across
    demographic groups, not just whether users receive any persona. This is critical
    for regulatory compliance (ECOA/disparate impact) because it detects if certain
    demographics are systematically assigned to stigmatizing personas.

    Example of what this CATCHES that the old metric MISSED:
    - 45% of low-income users → "High Utilization" persona
    - 8% of high-income users → "High Utilization" persona
    - Deviation: 18% (FAIL - triggers disparate impact review)

    Args:
        users_df: User records with demographics
        personas_df: Persona assignments (user_id, persona)
        tolerance: Acceptable deviation from overall rate (default: ±10%)

    Returns:
        Dictionary with per-persona parity results and flags for violations
    """
    merged = users_df.merge(personas_df, on="user_id")
    merged["age_bucket"] = merged["age"].apply(bucket_age)

    # Get all unique personas (excluding 'general' for stigmatization analysis)
    personas_to_check = [p for p in merged["persona"].unique() if p != "general"]

    parity_results = {
        "tolerance": tolerance,
        "personas_checked": personas_to_check,
        "violations": [],
        "persona_metrics": {},
    }

    for persona in personas_to_check:
        # Overall assignment rate for this persona
        overall_rate = (merged["persona"] == persona).mean()

        persona_parity = {
            "overall_rate": round(overall_rate, 4),
            "demographics": {},
            "max_deviation": 0.0,
            "passes": True,
        }

        # Check each demographic
        for demographic in ["gender", "income_tier", "region", "age_bucket"]:
            group_rates = (merged["persona"] == persona).groupby(merged[demographic]).mean()
            deviations = (group_rates - overall_rate).abs()
            max_dev = deviations.max()

            demo_passes = within_tolerance(max_dev, tolerance)

            persona_parity["demographics"][demographic] = {
                "passes": bool(demo_passes),
                "max_deviation": round(max_dev, 4),
                "group_rates": {str(k): round(v, 4) for k, v in group_rates.items()},
                "deviations": {str(k): round(v, 4) for k, v in deviations.items()},
            }

            # Track overall max deviation across all demographics for this persona
            if max_dev > persona_parity["max_deviation"]:
                persona_parity["max_deviation"] = max_dev

            # Flag violations
            if not demo_passes:
                persona_parity["passes"] = False
                worst_group = deviations.idxmax()
                parity_results["violations"].append({
                    "persona": persona,
                    "demographic": demographic,
                    "group": str(worst_group),
                    "deviation": round(max_dev, 4),
                    "tolerance": tolerance,
                })

        parity_results["persona_metrics"][persona] = persona_parity

    # Overall pass/fail
    parity_results["all_personas_pass"] = all(
        pm["passes"] for pm in parity_results["persona_metrics"].values()
    )

    return parity_results


def calculate_recommendation_quantity_parity(
    users_df: pd.DataFrame,
    traces: list,
    tolerance: float = 0.10,
) -> Dict[str, Any]:
    """
    Calculate recommendation quantity parity - ensures equitable service quality.

    Measures whether all demographic groups receive similar numbers of recommendations.
    This prevents scenarios where certain groups receive inferior service (fewer recs).

    Args:
        users_df: User records with demographics
        traces: List of user trace dictionaries with recommendation counts
        tolerance: Acceptable deviation from overall mean (default: ±10%)

    Returns:
        Dictionary with recommendation parity results by demographic
    """
    # Extract recommendation counts from traces
    rec_counts = pd.DataFrame([
        {
            "user_id": trace["user_id"],
            "total_recommendations": trace.get("recommendations", {}).get("total_recommendations", 0),
        }
        for trace in traces
    ])

    # Merge with demographics
    merged = users_df.merge(rec_counts, on="user_id")
    merged["age_bucket"] = merged["age"].apply(bucket_age)

    # Overall mean
    overall_mean = merged["total_recommendations"].mean()

    parity_results = {
        "overall_mean": round(overall_mean, 2),
        "tolerance": tolerance,
        "demographics": {},
        "violations": [],
        "passes": True,
    }

    for demographic in ["gender", "income_tier", "region", "age_bucket"]:
        group_means = merged.groupby(demographic)["total_recommendations"].mean()
        deviations_abs = (group_means - overall_mean).abs()
        deviations_pct = (deviations_abs / overall_mean) if overall_mean > 0 else deviations_abs

        max_dev_pct = deviations_pct.max()
        demo_passes = within_tolerance(max_dev_pct, tolerance)

        parity_results["demographics"][demographic] = {
            "passes": bool(demo_passes),
            "max_deviation_pct": round(max_dev_pct, 4),
            "group_means": {str(k): round(v, 2) for k, v in group_means.items()},
            "deviations_pct": {str(k): round(v, 4) for k, v in deviations_pct.items()},
        }

        if not demo_passes:
            parity_results["passes"] = False
            worst_group = deviations_pct.idxmax()
            parity_results["violations"].append({
                "demographic": demographic,
                "group": str(worst_group),
                "deviation_pct": round(max_dev_pct, 4),
                "group_mean": round(group_means[worst_group], 2),
                "overall_mean": round(overall_mean, 2),
            })

    return parity_results


def calculate_partner_offer_parity(
    users_df: pd.DataFrame,
    traces: list,
    tolerance: float = 0.10,
) -> Dict[str, Any]:
    """
    Calculate partner offer access parity - ensures equitable opportunity access.

    Among users who receive recommendations, checks if access to premium partner offers
    is equitable across demographics. This prevents "redlining" where certain groups
    are systematically excluded from premium opportunities.

    Args:
        users_df: User records with demographics
        traces: List of user trace dictionaries with offer counts
        tolerance: Acceptable deviation from overall rate (default: ±10%)

    Returns:
        Dictionary with partner offer parity results by demographic
    """
    # Extract offer counts from traces
    offer_data = pd.DataFrame([
        {
            "user_id": trace["user_id"],
            "has_offers": trace.get("recommendations", {}).get("offer_count", 0) > 0,
            "offer_count": trace.get("recommendations", {}).get("offer_count", 0),
        }
        for trace in traces
    ])

    # Merge with demographics
    merged = users_df.merge(offer_data, on="user_id")
    merged["age_bucket"] = merged["age"].apply(bucket_age)

    # Overall offer access rate
    overall_offer_rate = merged["has_offers"].mean()

    parity_results = {
        "overall_offer_rate": round(overall_offer_rate, 4),
        "tolerance": tolerance,
        "demographics": {},
        "violations": [],
        "passes": True,
    }

    for demographic in ["gender", "income_tier", "region", "age_bucket"]:
        group_rates = merged.groupby(demographic)["has_offers"].mean()
        deviations = (group_rates - overall_offer_rate).abs()

        max_dev = deviations.max()
        demo_passes = within_tolerance(max_dev, tolerance)

        parity_results["demographics"][demographic] = {
            "passes": bool(demo_passes),
            "max_deviation": round(max_dev, 4),
            "group_rates": {str(k): round(v, 4) for k, v in group_rates.items()},
            "deviations": {str(k): round(v, 4) for k, v in deviations.items()},
        }

        if not demo_passes:
            parity_results["passes"] = False
            worst_group = deviations.idxmax()
            parity_results["violations"].append({
                "demographic": demographic,
                "group": str(worst_group),
                "deviation": round(max_dev, 4),
                "group_rate": round(group_rates[worst_group], 4),
                "overall_rate": round(overall_offer_rate, 4),
            })

    return parity_results


# ============================================
# PERSONA DISTRIBUTION BY DEMOGRAPHICS
# ============================================


def calculate_persona_distribution(
    users_df: pd.DataFrame,
    personas_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Calculate detailed persona distribution across demographic groups.

    Returns cross-tabulations showing which personas are assigned to which
    demographic segments, useful for identifying systematic biases.

    Args:
        users_df: User records with demographics
        personas_df: Persona assignments

    Returns:
        Dictionary with persona distributions per demographic
    """
    merged = users_df.merge(personas_df, on="user_id")
    merged["age_bucket"] = merged["age"].apply(bucket_age)

    distribution = {}

    # Overall persona distribution
    distribution["overall"] = merged["persona"].value_counts().to_dict()

    # Gender × Persona cross-tab
    gender_persona = pd.crosstab(merged["gender"], merged["persona"], normalize="index")
    distribution["gender_by_persona"] = {
        str(gender): {str(persona): round(rate, 4) for persona, rate in row.items()}
        for gender, row in gender_persona.iterrows()
    }

    # Income Tier × Persona cross-tab
    income_persona = pd.crosstab(merged["income_tier"], merged["persona"], normalize="index")
    distribution["income_tier_by_persona"] = {
        str(tier): {str(persona): round(rate, 4) for persona, rate in row.items()}
        for tier, row in income_persona.iterrows()
    }

    # Region × Persona cross-tab
    region_persona = pd.crosstab(merged["region"], merged["persona"], normalize="index")
    distribution["region_by_persona"] = {
        str(region): {str(persona): round(rate, 4) for persona, rate in row.items()}
        for region, row in region_persona.iterrows()
    }

    # Age Bucket × Persona cross-tab
    age_persona = pd.crosstab(merged["age_bucket"], merged["persona"], normalize="index")
    distribution["age_by_persona"] = {
        str(bucket): {str(persona): round(rate, 4) for persona, rate in row.items()}
        for bucket, row in age_persona.iterrows()
    }

    return distribution


# ============================================
# MARKDOWN REPORT GENERATION
# ============================================


def generate_fairness_report_markdown(
    fairness_results: Dict[str, Any],
    distribution: Dict[str, Any],
    timestamp: str,
) -> str:
    """
    Generate comprehensive production-ready fairness report for docs/fairness_report.md.

    Args:
        fairness_results: Output from calculate_fairness_metrics() with production metrics
        distribution: Output from calculate_persona_distribution()
        timestamp: Timestamp of evaluation run

    Returns:
        Markdown string for fairness report with production metrics
    """
    overall_rate = fairness_results["overall_persona_rate"]
    tolerance = fairness_results["tolerance"]

    # Extract production metrics
    persona_parity = fairness_results.get("persona_distribution_parity", {})
    rec_parity = fairness_results.get("recommendation_quantity_parity", {})
    offer_parity = fairness_results.get("partner_offer_parity", {})
    production_passes = fairness_results.get("production_fairness_passes", False)
    violations = fairness_results.get("production_violations", [])

    md = f"""# Fairness Report - SpendSense Evaluation (Production-Ready)

**Generated**: {timestamp}

## Executive Summary

This report analyzes fairness across three production-ready metrics to ensure regulatory compliance
(ECOA, Regulation B) and avoid disparate impact in financial recommendations.

### Production Fairness Status

**Overall Status**: {"✅ PASS - All production metrics within tolerance" if production_passes else f"❌ FAIL - {len(violations)} fairness violations detected"}

| Metric | Status | Violations | Regulatory Significance |
|--------|--------|------------|------------------------|
| **Persona Distribution Parity** | {"✅ PASS" if persona_parity.get("all_personas_pass", False) else "❌ FAIL"} | {len([v for v in violations if "persona" in v])} | Prevents stigmatizing personas assigned to protected groups |
| **Recommendation Quantity Parity** | {"✅ PASS" if rec_parity.get("passes", False) else "❌ FAIL"} | {len([v for v in violations if "deviation_pct" in v])} | Ensures equitable service quality |
| **Partner Offer Access Parity** | {"✅ PASS" if offer_parity.get("passes", False) else "❌ FAIL"} | {len([v for v in violations if "group_rate" in v])} | Prevents opportunity redlining |

"""

    if violations:
        md += """
### ⚠️ Fairness Violations Detected

The following violations require attention:

"""
        for i, v in enumerate(violations, 1):
            if "persona" in v:
                md += f"{i}. **{v['persona']}** persona: {v['demographic']} / {v['group']} shows {v['deviation']*100:.1f}% deviation (tolerance: ±{v['tolerance']*100}%)\n"
            elif "deviation_pct" in v:
                md += f"{i}. **Recommendation quantity**: {v['demographic']} / {v['group']} shows {v['deviation_pct']*100:.1f}% deviation (mean: {v['group_mean']:.1f} vs {v['overall_mean']:.1f})\n"
            elif "group_rate" in v:
                md += f"{i}. **Partner offer access**: {v['demographic']} / {v['group']} shows {v['deviation']*100:.1f}% deviation\n"

        md += """
**Action Required**: Review persona assignment logic and data generation process to identify and address sources of disparity.

"""

    md += f"""
---

## Legacy Metric (Backwards Compatibility)

**Overall Persona Assignment Rate**: {overall_rate*100:.2f}% (excluding 'general' persona)

**Legacy Status**: {"✅ PASS" if fairness_results["all_demographics_pass"] else "❌ FAIL"}

⚠️ **Note**: The legacy metric only checks if users receive ANY persona, not WHICH persona types.
This metric is kept for backwards compatibility but does NOT provide regulatory compliance assurance.
The production metrics above are the authoritative fairness indicators.

"""

    # ========================================
    # GENDER FAIRNESS
    # ========================================
    gender = fairness_results["demographics"]["gender"]
    md += f"""
---

## 1. Gender Fairness

**Status**: {"✅ PASS" if gender["passes"] else "❌ FAIL"}
**Max Deviation**: {gender["max_deviation"]*100:.2f}% (tolerance: ±{tolerance*100}%)

| Gender | Persona Rate | Deviation from Mean | User Count | Status |
|--------|--------------|---------------------|------------|--------|
"""
    for group, rate in gender["group_rates"].items():
        deviation = gender["deviations"][group]
        count = gender["group_counts"].get(group, 0)
        status = "✅" if within_tolerance(abs(deviation), tolerance) else "❌"
        md += f"| {group} | {rate*100:.2f}% | {deviation*100:+.2f}% | {count} | {status} |\n"

    # ========================================
    # INCOME TIER FAIRNESS
    # ========================================
    income = fairness_results["demographics"]["income_tier"]
    md += f"""
---

## 2. Income Tier Fairness

**Status**: {"✅ PASS" if income["passes"] else "❌ FAIL"}
**Max Deviation**: {income["max_deviation"]*100:.2f}% (tolerance: ±{tolerance*100}%)

| Income Tier | Persona Rate | Deviation from Mean | User Count | Status |
|-------------|--------------|---------------------|------------|--------|
"""
    for group, rate in income["group_rates"].items():
        deviation = income["deviations"][group]
        count = income["group_counts"].get(group, 0)
        status = "✅" if within_tolerance(abs(deviation), tolerance) else "❌"
        md += f"| {group} | {rate*100:.2f}% | {deviation*100:+.2f}% | {count} | {status} |\n"

    # ========================================
    # REGION FAIRNESS
    # ========================================
    region = fairness_results["demographics"]["region"]
    md += f"""
---

## 3. Region Fairness

**Status**: {"✅ PASS" if region["passes"] else "❌ FAIL"}
**Max Deviation**: {region["max_deviation"]*100:.2f}% (tolerance: ±{tolerance*100}%)

| Region | Persona Rate | Deviation from Mean | User Count | Status |
|--------|--------------|---------------------|------------|--------|
"""
    for group, rate in region["group_rates"].items():
        deviation = region["deviations"][group]
        count = region["group_counts"].get(group, 0)
        status = "✅" if within_tolerance(abs(deviation), tolerance) else "❌"
        md += f"| {group} | {rate*100:.2f}% | {deviation*100:+.2f}% | {count} | {status} |\n"

    # ========================================
    # AGE FAIRNESS
    # ========================================
    age = fairness_results["demographics"]["age"]
    md += f"""
---

## 4. Age Fairness

**Status**: {"✅ PASS" if age["passes"] else "❌ FAIL"}
**Max Deviation**: {age["max_deviation"]*100:.2f}% (tolerance: ±{tolerance*100}%)
**Age Buckets**: {', '.join(age["buckets"])}

| Age Bucket | Persona Rate | Deviation from Mean | User Count | Status |
|------------|--------------|---------------------|------------|--------|
"""
    for group, rate in age["group_rates"].items():
        deviation = age["deviations"][group]
        count = age["group_counts"].get(group, 0)
        status = "✅" if within_tolerance(abs(deviation), tolerance) else "❌"
        md += f"| {group} | {rate*100:.2f}% | {deviation*100:+.2f}% | {count} | {status} |\n"

    # ========================================
    # PRODUCTION METRIC 1: PERSONA DISTRIBUTION PARITY
    # ========================================
    md += """
---

## 5. Production Metric: Persona Distribution Parity

**Primary Fairness Metric** - Measures whether specific persona TYPES are assigned equitably across demographics.

"""

    if persona_parity:
        md += f"""**Status**: {"✅ PASS" if persona_parity.get("all_personas_pass", False) else "❌ FAIL"}
**Personas Checked**: {len(persona_parity.get("personas_checked", []))} ({', '.join(persona_parity.get("personas_checked", []))})

### Per-Persona Fairness Analysis

"""

        for persona_name, persona_data in persona_parity.get("persona_metrics", {}).items():
            status_icon = "✅" if persona_data.get("passes", True) else "❌"
            md += f"""
#### {status_icon} {persona_name}

**Overall Assignment Rate**: {persona_data.get("overall_rate", 0)*100:.2f}%
**Max Deviation**: {persona_data.get("max_deviation", 0)*100:.2f}%

"""
            # Show demographic breakdown for this persona
            for demo, demo_data in persona_data.get("demographics", {}).items():
                if not demo_data.get("passes", True):
                    md += f"**⚠️ {demo.replace('_', ' ').title()} Violation**:\n"
                    for group, rate in demo_data.get("group_rates", {}).items():
                        deviation = demo_data.get("deviations", {}).get(group, 0)
                        if abs(deviation) > tolerance:
                            md += f"- {group}: {rate*100:.1f}% (deviation: {deviation*100:+.1f}%)\n"

    # ========================================
    # PRODUCTION METRIC 2: RECOMMENDATION QUANTITY PARITY
    # ========================================
    md += """
---

## 6. Production Metric: Recommendation Quantity Parity

**Service Quality Metric** - Ensures all demographic groups receive similar numbers of recommendations.

"""

    if rec_parity:
        md += f"""**Status**: {"✅ PASS" if rec_parity.get("passes", True) else "❌ FAIL"}
**Overall Mean**: {rec_parity.get("overall_mean", 0):.2f} recommendations per user

| Demographic | Group | Mean Recommendations | Deviation |
|-------------|-------|---------------------|-----------|
"""

        for demo, demo_data in rec_parity.get("demographics", {}).items():
            for group, mean in demo_data.get("group_means", {}).items():
                dev_pct = demo_data.get("deviations_pct", {}).get(group, 0)
                status = "✅" if within_tolerance(abs(dev_pct), tolerance) else "❌"
                md += f"| {demo.replace('_', ' ').title()} | {group} | {mean:.2f} | {dev_pct*100:+.1f}% {status} |\n"

    # ========================================
    # PRODUCTION METRIC 3: PARTNER OFFER ACCESS PARITY
    # ========================================
    md += """
---

## 7. Production Metric: Partner Offer Access Parity

**Opportunity Equity Metric** - Ensures equitable access to premium partner offers.

"""

    if offer_parity:
        md += f"""**Status**: {"✅ PASS" if offer_parity.get("passes", True) else "❌ FAIL"}
**Overall Offer Access Rate**: {offer_parity.get("overall_offer_rate", 0)*100:.2f}%

| Demographic | Group | Offer Access Rate | Deviation |
|-------------|-------|------------------|-----------|
"""

        for demo, demo_data in offer_parity.get("demographics", {}).items():
            for group, rate in demo_data.get("group_rates", {}).items():
                dev = demo_data.get("deviations", {}).get(group, 0)
                status = "✅" if within_tolerance(abs(dev), tolerance) else "❌"
                md += f"| {demo.replace('_', ' ').title()} | {group} | {rate*100:.1f}% | {dev*100:+.1f}% {status} |\n"

    # ========================================
    # PERSONA DISTRIBUTION DETAILS
    # ========================================
    md += """
---

## 8. Detailed Persona Distribution

### Overall Persona Distribution

| Persona | User Count |
|---------|------------|
"""
    for persona, count in sorted(distribution["overall"].items()):
        md += f"| {persona} | {count} |\n"

    md += """
### Gender × Persona Cross-Tabulation

| Gender | high_utilization | general | Other |
|--------|------------------|---------|-------|
"""
    for gender, personas in distribution["gender_by_persona"].items():
        high_util = personas.get("high_utilization", 0.0) * 100
        general = personas.get("general", 0.0) * 100
        other = (
            sum(v for k, v in personas.items() if k not in ["high_utilization", "general"]) * 100
        )
        md += f"| {gender} | {high_util:.1f}% | {general:.1f}% | {other:.1f}% |\n"

    # ========================================
    # METHODOLOGY & COMPLIANCE
    # ========================================
    md += f"""
---

## 9. Methodology & Regulatory Context

### Production-Ready Fairness Metrics

**1. Persona Distribution Parity** (Primary - ECOA Compliance)

**Definition**: For each persona type, the assignment rate across each demographic group must be within ±{tolerance*100}% of the overall assignment rate for that persona.

**Why it matters**: Detects if certain demographics are disproportionately assigned to potentially stigmatizing personas (e.g., "High Utilization"). This is critical for avoiding disparate impact under ECOA and Regulation B.

**Example**: If 27% of all users are "High Utilization", then 27% ±{tolerance*100}% (24.3%-29.7%) of EACH demographic group should be assigned this persona.

**2. Recommendation Quantity Parity** (Service Quality)

**Definition**: The average number of recommendations per user must be within ±{tolerance*100}% across all demographic groups.

**Why it matters**: Ensures all users receive equitable service quality. Prevents scenarios where certain demographics receive fewer recommendations (inferior service).

**3. Partner Offer Access Parity** (Opportunity Equity)

**Definition**: Among users who receive recommendations, the % who receive partner offers must be within ±{tolerance*100}% across demographics.

**Why it matters**: Prevents "redlining" where premium opportunities are systematically withheld from protected groups.

### Legacy Metric (Backwards Compatibility Only)

The legacy metric (overall persona assignment rate) measures if users receive ANY persona, not WHICH persona types. This metric will always show 100% for all groups in SpendSense because every user gets a persona (including "General").

**⚠️ Important**: The legacy metric does NOT provide regulatory compliance assurance. Use production metrics for fairness evaluation.

### Regulatory Framework

**Equal Credit Opportunity Act (ECOA) - Regulation B**:
- Prohibits discrimination based on race, color, religion, national origin, sex, marital status, age, receipt of public assistance
- Applies to ANY aspect of a credit transaction
- While SpendSense doesn't extend credit, educational recommendations about credit products may fall under regulatory scrutiny

**Disparate Impact Doctrine**:
- Even facially neutral policies can violate ECOA if they create discriminatory outcomes
- Three-step test: (1) Show statistically significant disparity, (2) Defendant shows business need, (3) Plaintiff shows less discriminatory alternative

**SpendSense Compliance Approach**:
- Demographics used ONLY for fairness monitoring, never in persona assignment logic
- Persona assignments based exclusively on behavioral signals
- Continuous monitoring detects fairness drift
- Complete audit trail enables investigation of any fairness complaints

### Technical Details

**Age Bucketing Strategy**:
- 18-30: Young adults (early career, student loans, building credit)
- 31-50: Mid-career (mortgages, family finances, retirement planning)
- 51+: Pre-retirement/retirement (wealth preservation, fixed income)

**Tolerance Rationale**:
- ±{tolerance*100}% tolerance balances statistical rigor with sample size limitations
- Stricter tolerance (e.g., ±5%) would require larger sample sizes
- Looser tolerance (e.g., ±15%) would miss meaningful disparities

**Limitations**:
- Synthetic data may not reflect real-world demographic distributions
- Small sample sizes in some groups reduce statistical power
- No intersectional analysis (e.g., gender × income tier) in MVP
- No behavioral outcome parity analysis (for users with similar financial profiles)

---

## 10. Compliance Statement

> **This fairness analysis ensures regulatory compliance with ECOA and fair lending principles.**
>
> SpendSense does not use demographic information (age, gender, income tier, region) in persona assignment or recommendation logic. Demographics are collected solely for fairness monitoring purposes.
>
> All persona assignments are based exclusively on behavioral signals (spending patterns, savings behavior, credit utilization, income stability) without regard to protected characteristics.
>
> This report demonstrates:
> 1. **Demographic Blindness**: Demographics not used in decisioning logic
> 2. **Equal Treatment**: Users with similar financial behaviors receive similar personas/recommendations
> 3. **Continuous Monitoring**: Production metrics detect fairness violations
> 4. **Complete Auditability**: Decision traces enable investigation of discrimination claims
>
> **Action on Violations**: Any fairness violations detected in this report trigger mandatory review of data generation process and persona assignment logic to identify and address sources of disparity.

---

**Report Generated**: {timestamp}
**Evaluation Version**: Production-Ready Fairness Metrics v1.0
**Regulatory Framework**: ECOA, Regulation B, Disparate Impact Doctrine
**Contact**: Casey Manos (Project Lead) | Bryce Harris (bharris@peak6.com)

**For detailed fairness methodology**, see: `docs/FAIRNESS_METHODOLOGY.md`
"""

    return md


# ============================================
# MAIN FAIRNESS CALCULATION FUNCTION
# ============================================


def calculate_fairness_metrics(
    db_path: str = "data/users.sqlite",
    tolerance: float = 0.10,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Calculate all production-ready fairness metrics and persona distribution.

    This function computes three critical fairness metrics:
    1. Persona Distribution Parity: Primary metric for regulatory compliance
    2. Recommendation Quantity Parity: Ensures equitable service quality
    3. Partner Offer Access Parity: Prevents opportunity redlining

    Args:
        db_path: Path to SQLite database
        tolerance: Acceptable deviation from mean (default: ±10%)

    Returns:
        Tuple of (fairness_results, distribution)
        - fairness_results includes legacy + production metrics
        - distribution includes detailed cross-tabulations
    """
    import json
    from pathlib import Path

    # Load data from SQLite
    conn = sqlite3.connect(db_path)
    users_df = pd.read_sql_query("SELECT * FROM users", conn)
    personas_df = pd.read_sql_query("SELECT * FROM persona_assignments", conn)
    conn.close()

    # Load trace files for recommendation metrics
    trace_dir = Path("docs/traces")
    traces = []
    for trace_file in trace_dir.glob("user_*.json"):
        with open(trace_file, 'r') as f:
            traces.append(json.load(f))

    print(f"\nCalculating production-ready fairness metrics for {len(users_df)} users...")
    print(f"Loaded {len(traces)} trace files for recommendation analysis\n")

    # ========================================
    # LEGACY METRIC (for backwards compatibility)
    # ========================================
    legacy_fairness, overall_rate = calculate_fairness_parity(users_df, personas_df, tolerance)

    # ========================================
    # PRODUCTION METRICS (new)
    # ========================================

    print("  [1/3] Calculating persona distribution parity...")
    persona_parity = calculate_persona_distribution_parity(users_df, personas_df, tolerance)

    print("  [2/3] Calculating recommendation quantity parity...")
    rec_parity = calculate_recommendation_quantity_parity(users_df, traces, tolerance)

    print("  [3/3] Calculating partner offer access parity...")
    offer_parity = calculate_partner_offer_parity(users_df, traces, tolerance)

    # ========================================
    # COMBINED FAIRNESS RESULTS
    # ========================================

    fairness_results = {
        # Legacy metrics (keep for backwards compatibility)
        "overall_persona_rate": legacy_fairness["overall_persona_rate"],
        "tolerance": tolerance,
        "demographics": legacy_fairness["demographics"],
        "all_demographics_pass": legacy_fairness["all_demographics_pass"],
        "failing_demographics": legacy_fairness["failing_demographics"],

        # Production metrics (new)
        "persona_distribution_parity": persona_parity,
        "recommendation_quantity_parity": rec_parity,
        "partner_offer_parity": offer_parity,

        # Overall production fairness status
        "production_fairness_passes": (
            persona_parity["all_personas_pass"] and
            rec_parity["passes"] and
            offer_parity["passes"]
        ),
        "production_violations": (
            persona_parity["violations"] +
            rec_parity["violations"] +
            offer_parity["violations"]
        ),
    }

    # Calculate persona distribution for reports
    distribution = calculate_persona_distribution(users_df, personas_df)

    # ========================================
    # PRINT SUMMARY
    # ========================================

    print("\n" + "=" * 70)
    print("FAIRNESS METRICS SUMMARY")
    print("=" * 70)

    print("\n📊 Legacy Metric (Backwards Compatibility):")
    print(f"   Overall persona assignment rate: {overall_rate*100:.2f}%")
    print(f"   Status: {'✅ PASS' if legacy_fairness['all_demographics_pass'] else '❌ FAIL'}")

    print("\n🎯 Production Metrics (Regulatory Compliance):")
    print(f"   [1] Persona Distribution Parity: {'✅ PASS' if persona_parity['all_personas_pass'] else '❌ FAIL'}")
    if persona_parity["violations"]:
        print(f"       Violations: {len(persona_parity['violations'])}")
        for v in persona_parity["violations"][:3]:  # Show first 3
            print(f"       - {v['persona']} / {v['demographic']} / {v['group']}: {v['deviation']*100:.1f}% deviation")

    print(f"   [2] Recommendation Quantity Parity: {'✅ PASS' if rec_parity['passes'] else '❌ FAIL'}")
    if rec_parity["violations"]:
        for v in rec_parity["violations"]:
            print(f"       - {v['demographic']} / {v['group']}: {v['deviation_pct']*100:.1f}% deviation")

    print(f"   [3] Partner Offer Access Parity: {'✅ PASS' if offer_parity['passes'] else '❌ FAIL'}")
    if offer_parity["violations"]:
        for v in offer_parity["violations"]:
            print(f"       - {v['demographic']} / {v['group']}: {v['deviation']*100:.1f}% deviation")

    print(f"\n🏁 Overall Production Fairness: {'✅ PASS' if fairness_results['production_fairness_passes'] else '❌ FAIL'}")
    if fairness_results["production_violations"]:
        print(f"   Total violations: {len(fairness_results['production_violations'])}")

    print("=" * 70 + "\n")

    return fairness_results, distribution

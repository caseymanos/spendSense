"""
Fairness Metrics Module

This module calculates demographic parity metrics across protected groups:
- Gender (4 categories: male, female, non_binary, prefer_not_to_say)
- Income Tier (3 tiers: low, medium, high)
- Region (4 regions: northeast, southeast, midwest, west)
- Age (3 buckets: 18-30, 31-50, 51+)

Fairness metric checks if persona assignment rates are within ±10% of overall mean
across all demographic groups, ensuring no group is systematically underserved or
overserved by the recommendation system.
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
    gender_passes = gender_max_deviation <= tolerance

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
    income_passes = income_max_deviation <= tolerance

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
    region_passes = region_max_deviation <= tolerance

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
    age_passes = age_max_deviation <= tolerance

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
    Generate markdown fairness report for docs/fairness_report.md.

    Args:
        fairness_results: Output from calculate_fairness_parity()
        distribution: Output from calculate_persona_distribution()
        timestamp: Timestamp of evaluation run

    Returns:
        Markdown string for fairness report
    """
    overall_rate = fairness_results["overall_persona_rate"]
    tolerance = fairness_results["tolerance"]

    md = f"""# Fairness Report - SpendSense Evaluation

**Generated**: {timestamp}

## Executive Summary

This report analyzes demographic parity in persona assignment across four protected characteristics: gender, income tier, region, and age. Fairness is measured by ensuring that persona assignment rates (excluding 'general' persona) are within ±{tolerance*100}% of the overall mean across all demographic groups.

**Overall Persona Assignment Rate**: {overall_rate*100:.2f}% (excluding 'general' persona)

**Fairness Status**: {"✅ PASS - All demographics within tolerance" if fairness_results["all_demographics_pass"] else f"❌ FAIL - {len(fairness_results['failing_demographics'])} demographics outside tolerance"}

"""

    if not fairness_results["all_demographics_pass"]:
        md += f"""
**Failing Demographics**: {', '.join(fairness_results['failing_demographics'])}

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
        status = "✅" if abs(deviation) <= tolerance else "❌"
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
        status = "✅" if abs(deviation) <= tolerance else "❌"
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
        status = "✅" if abs(deviation) <= tolerance else "❌"
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
        status = "✅" if abs(deviation) <= tolerance else "❌"
        md += f"| {group} | {rate*100:.2f}% | {deviation*100:+.2f}% | {count} | {status} |\n"

    # ========================================
    # PERSONA DISTRIBUTION DETAILS
    # ========================================
    md += """
---

## 5. Detailed Persona Distribution

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

## 6. Methodology

**Fairness Metric**: Demographic parity in persona assignment rates

**Definition**: For each demographic group, the persona assignment rate (excluding 'general' persona) must be within ±{tolerance*100}% of the overall mean.

**Rationale**:
- Demographics are used ONLY for fairness analysis, not for persona assignment logic
- 'General' persona is excluded because it represents users with insufficient behavioral signals
- ±{tolerance*100}% tolerance balances statistical rigor with sample size limitations

**Age Bucketing Strategy**:
- 18-30: Young adults (early career, student loans, building credit)
- 31-50: Mid-career (mortgages, family finances, retirement planning)
- 51+: Pre-retirement/retirement (wealth preservation, fixed income)

**Limitations**:
- Synthetic data may not reflect real-world demographic distributions
- Small sample sizes in some groups reduce statistical power
- No intersectional analysis (e.g., gender × income tier) in MVP

---

## 7. Compliance Statement

> **This fairness analysis is for internal quality assurance only.**
>
> SpendSense does not use demographic information (age, gender, income tier, region) in persona assignment logic. Demographics are collected solely for fairness monitoring purposes.
>
> All persona assignments are based exclusively on behavioral signals (spending patterns, savings behavior, credit utilization, income stability) without regard to protected characteristics.
>
> This report demonstrates compliance with the principle of equal treatment: all users with similar financial behaviors receive similar persona assignments and recommendations, regardless of demographic group membership.

---

**Report Generated**: {timestamp}
**Evaluation Version**: PR #8 Evaluation Harness
**Contact**: Casey Manos (Project Lead)
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
    Calculate all fairness metrics and persona distribution.

    Args:
        db_path: Path to SQLite database
        tolerance: Acceptable deviation from mean (default: ±10%)

    Returns:
        Tuple of (fairness_results, distribution)
    """
    # Load data from SQLite
    conn = sqlite3.connect(db_path)
    users_df = pd.read_sql_query("SELECT * FROM users", conn)
    personas_df = pd.read_sql_query("SELECT * FROM persona_assignments", conn)
    conn.close()

    print(f"Calculating fairness metrics for {len(users_df)} users...")

    # Calculate fairness parity
    fairness_results, overall_rate = calculate_fairness_parity(users_df, personas_df, tolerance)

    # Calculate persona distribution
    distribution = calculate_persona_distribution(users_df, personas_df)

    print(f"Overall persona rate: {overall_rate*100:.2f}%")
    print(f"Fairness status: {'PASS' if fairness_results['all_demographics_pass'] else 'FAIL'}")

    if not fairness_results["all_demographics_pass"]:
        print(f"Failing demographics: {', '.join(fairness_results['failing_demographics'])}")

    return fairness_results, distribution

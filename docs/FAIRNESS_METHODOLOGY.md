# SpendSense Fairness Methodology
**Production-Ready Compliance Framework**

**Version**: 1.0
**Date**: 2025-11-08
**Author**: Casey Manos (Project Lead)
**Technical Spec**: Bryce Harris (bharris@peak6.com)

---

## Executive Summary

This document defines the production-ready fairness methodology for SpendSense, designed to ensure regulatory compliance with the Equal Credit Opportunity Act (ECOA) and Regulation B's fair lending principles while avoiding disparate impact.

**Key Principles**:
- **Demographic Blindness**: Protected characteristics NEVER used in persona assignment or recommendation logic
- **Continuous Monitoring**: Production metrics detect fairness violations in real-time
- **Complete Auditability**: Every decision traceable to behavioral signals, not demographics
- **Regulatory Alignment**: Framework designed for ECOA/Regulation B compliance

**Three-Tier Production Metrics**:
1. **Persona Distribution Parity** (Primary): Detects disparate impact in persona type assignments
2. **Recommendation Quantity Parity**: Ensures equitable service quality
3. **Partner Offer Access Parity**: Prevents opportunity redlining

---

## Table of Contents

1. [Background: Why the Legacy Metric Was Insufficient](#background)
2. [Regulatory Framework](#regulatory-framework)
3. [Production-Ready Fairness Metrics](#production-metrics)
4. [Implementation Details](#implementation)
5. [Testing and Validation](#testing)
6. [Interpreting Results](#interpretation)
7. [Future Enhancements](#future-enhancements)
8. [References](#references)

---

<a name="background"></a>
## 1. Background: Why the Legacy Metric Was Insufficient

### Legacy Metric Definition

The original fairness metric measured:
```python
overall_persona_rate = (personas_df["persona"] != "general").mean()
```

This calculated the **percentage of users who receive ANY persona** (excluding "general" persona).

### The Critical Flaw

**The legacy metric would show 100% PASS even with severe disparate impact.**

**Example of what it MISSED**:
```
Scenario: "High Utilization" persona assignment by income tier

Low-income users:    45% assigned "High Utilization"
Medium-income users: 22% assigned "High Utilization"
High-income users:    8% assigned "High Utilization"

Legacy Metric: ✅ PASS (100% of all groups get SOME persona)
Actual Problem: ❌ FAIL (18% deviation = disparate impact risk)
```

### Why This Matters for Financial Services

Under ECOA and Regulation B:
- **Disparate Impact Doctrine**: Even facially neutral policies can violate ECOA if they create discriminatory outcomes
- **Stigmatizing Classifications**: Assigning "High Utilization" disproportionately to protected groups creates legal risk
- **Service Quality**: Providing fewer recommendations to certain demographics violates equal treatment principles

**Regulatory Risk**: The legacy metric provided a false sense of compliance. SpendSense could be in technical violation of fair lending principles while showing 100% fairness pass.

---

<a name="regulatory-framework"></a>
## 2. Regulatory Framework

### Equal Credit Opportunity Act (ECOA) - 15 U.S.C. § 1691

**Prohibits discrimination based on**:
- Race or color
- Religion
- National origin
- Sex
- Marital status
- Age (provided applicant has capacity to contract)
- Receipt of income from public assistance
- Good faith exercise of rights under Consumer Credit Protection Act

**Scope**: "ANY aspect of a credit transaction"

### Regulation B (12 CFR Part 1002)

Implements ECOA with detailed compliance requirements:
- **§ 1002.2(p)**: Prohibition on discriminatory credit practices
- **§ 1002.6(a)**: General rule prohibiting discrimination
- **§ 1002.9**: Notifications - adverse action notices required

### Disparate Impact Doctrine

Established in *Griggs v. Duke Power Co.* (1971), applied to lending in ECOA:

**Three-Step Test**:
1. **Plaintiff**: Shows statistically significant disparity across protected groups
2. **Defendant**: Shows legitimate business need for the challenged practice
3. **Plaintiff**: Shows less discriminatory alternative exists

**Key Point**: Intent is irrelevant. Even unintentional discrimination violates ECOA.

### Application to SpendSense

While SpendSense doesn't extend credit directly, it:
- Provides educational content about credit products
- Assigns behavioral personas that may influence user decisions
- Makes recommendations that could affect creditworthiness

**Conservative Compliance Approach**: Treat SpendSense as subject to ECOA scrutiny, even if legal status is ambiguous.

---

<a name="production-metrics"></a>
## 3. Production-Ready Fairness Metrics

### Metric 1: Persona Distribution Parity (Primary)

**Definition**: For each persona type, the assignment rate across each demographic group must be within ±10% of the overall assignment rate for that persona.

**Mathematical Formula**:
```python
For each persona P and demographic group G:
  overall_rate_P = count(users with persona P) / count(all users)
  group_rate_P_G = count(G users with persona P) / count(G users)

  deviation = |group_rate_P_G - overall_rate_P|

  PASS if deviation ≤ 0.10 (10% tolerance)
  FAIL if deviation > 0.10
```

**Example**:
```
Persona: "High Utilization"
Overall assignment rate: 27% of all users

Demographic: Gender
- Female: 48% assigned "High Utilization" → deviation = +21% ❌ FAIL
- Male: 12% assigned "High Utilization" → deviation = +15% ❌ FAIL
- Non-binary: 30% assigned "High Utilization" → deviation = +3% ✅ PASS
- Prefer not to say: 24% assigned "High Utilization" → deviation = +3% ✅ PASS

Result: Gender fails persona distribution parity for "High Utilization"
```

**Why It Matters**:
- Detects if stigmatizing personas (e.g., "High Utilization") are disproportionately assigned to protected groups
- Primary ECOA compliance metric
- Directly addresses disparate impact risk

**Implementation**: `eval/fairness.py::calculate_persona_distribution_parity()`

---

### Metric 2: Recommendation Quantity Parity

**Definition**: The average number of recommendations per user must be within ±10% across all demographic groups.

**Mathematical Formula**:
```python
For each demographic group G:
  overall_mean = mean(recommendation_count for all users)
  group_mean_G = mean(recommendation_count for users in G)

  deviation_pct = |group_mean_G - overall_mean| / overall_mean

  PASS if deviation_pct ≤ 0.10 (10% tolerance)
  FAIL if deviation_pct > 0.10
```

**Example**:
```
Overall mean: 4.96 recommendations per user

Demographic: Age Bucket
- 18-30: 4.82 avg → 2.8% deviation ✅ PASS
- 31-50: 4.42 avg → 10.8% deviation ❌ FAIL
- 51+: 5.64 avg → 13.6% deviation ❌ FAIL

Result: Age fails recommendation quantity parity
```

**Why It Matters**:
- Ensures equitable service quality across all demographics
- Prevents scenarios where certain groups receive "inferior" service (fewer recommendations)
- Addresses "separate and unequal" service quality concerns

**Implementation**: `eval/fairness.py::calculate_recommendation_quantity_parity()`

---

### Metric 3: Partner Offer Access Parity

**Definition**: Among users who receive recommendations, the percentage who receive partner offers must be within ±10% across demographics.

**Mathematical Formula**:
```python
For each demographic group G:
  eligible_users = users who received ≥1 recommendation
  overall_offer_rate = count(eligible users with partner offers) / count(eligible users)
  group_offer_rate_G = count(G eligible users with offers) / count(G eligible users)

  deviation_pct = |group_offer_rate_G - overall_offer_rate| / overall_offer_rate

  PASS if deviation_pct ≤ 0.10 (10% tolerance)
  FAIL if deviation_pct > 0.10
```

**Example**:
```
Overall partner offer access rate: 80% of eligible users

Demographic: Income Tier
- Low: 70.6% → 9.4% deviation ✅ PASS
- Medium: 81.8% → 1.8% deviation ✅ PASS
- High: 87.9% → 7.9% deviation ✅ PASS

Result: Income tier passes partner offer access parity
```

**Why It Matters**:
- Prevents "redlining" where premium opportunities are withheld from protected groups
- Ensures equitable access to value-added services
- Addresses opportunity equity beyond basic service provision

**Implementation**: `eval/fairness.py::calculate_partner_offer_parity()`

---

<a name="implementation"></a>
## 4. Implementation Details

### Data Flow

```
1. Data Generation (ingest/data_generator.py)
   ↓
   Synthetic users with demographics (gender, income_tier, region, age)
   ↓
2. Behavioral Feature Detection (features/)
   ↓
   Behavioral signals (subscriptions, savings, credit utilization, income stability)
   ↓
3. Persona Assignment (personas/persona_assigner.py)
   ↓
   Persona assigned based ONLY on behavioral signals (demographics NOT used)
   ↓
4. Recommendation Generation (recommend/recommendation_engine.py)
   ↓
   Recommendations + partner offers based on persona/behaviors (demographics NOT used)
   ↓
5. Fairness Evaluation (eval/fairness.py)
   ↓
   Retrospective analysis: Do outcomes differ by demographics?
   ↓
6. Reporting (docs/fairness_report.md)
```

### Key Code Locations

**Fairness Calculation Engine**: `eval/fairness.py`
- `calculate_persona_distribution_parity()` (lines 199-287)
- `calculate_recommendation_quantity_parity()` (lines 290-359)
- `calculate_partner_offer_parity()` (lines 362-429)
- `calculate_fairness_metrics()` (lines 709-835)

**Evaluation Orchestration**: `eval/run.py`
- Main evaluation harness that calls fairness metrics
- JSON/CSV output generation with production metrics

**Report Generation**: `eval/fairness.py::generate_fairness_report_markdown()`
- Comprehensive markdown report with regulatory context

### Demographics Collected (For Monitoring Only)

```python
demographics = {
    "gender": ["male", "female", "non_binary", "prefer_not_to_say"],
    "income_tier": ["low", "medium", "high"],
    "region": ["northeast", "south", "midwest", "west"],
    "age": continuous → bucketed as ["18-30", "31-50", "51+"]
}
```

**CRITICAL**: These demographics are used EXCLUSIVELY for fairness monitoring. They are NEVER inputs to:
- Persona assignment logic
- Recommendation generation
- Content filtering
- Eligibility determination

### Tolerance Rationale: Why ±10%?

**Statistical Considerations**:
- **Too Strict** (e.g., ±5%): With sample size of 100 users and 4 demographic groups per category, statistical noise could trigger false positives
- **Too Loose** (e.g., ±15%): Would miss meaningful disparities that could indicate systemic bias
- **Industry Standard**: ±10% balances statistical rigor with practical sample size constraints

**Regulatory Precedent**:
- FDIC guidance on fair lending testing often uses 10-20% thresholds for preliminary screening
- 10% is conservative (stricter than 20%) while accounting for sample variability

**Adjustable**: The tolerance is configurable in `calculate_fairness_metrics(tolerance=0.10)`

### Age Bucketing Strategy

```python
def bucket_age(age: int) -> str:
    if age < 31:
        return "18-30"  # Young adults: early career, student loans, building credit
    elif age < 51:
        return "31-50"  # Mid-career: mortgages, family finances, retirement planning
    else:
        return "51+"    # Pre-retirement/retirement: wealth preservation, fixed income
```

**Rationale**: Buckets align with distinct life stages and financial priorities while maintaining sufficient sample sizes.

---

<a name="testing"></a>
## 5. Testing and Validation

### Test Strategy

**Unit Tests** (Planned - `tests/test_fairness.py`):
- Test each fairness function in isolation with known-good test data
- Verify correct handling of edge cases (empty groups, single-user groups)
- Validate tolerance boundary conditions (exactly 10%, 9.9%, 10.1%)

**Integration Tests** (Planned):
- Run full evaluation pipeline with synthetic data designed to violate each metric
- Verify violations are correctly detected and reported
- Confirm JSON/CSV output includes all production metrics

**Validation with Real Data** (Current Approach):
```bash
uv run python -m eval.run
```
- Generates 100 synthetic users with personas and recommendations
- Calculates all 3 production fairness metrics
- Outputs detailed fairness_report.md with violations

**Current Test Results** (2025-11-08):
- ✅ Persona Distribution Parity: Correctly detected 3 violations
- ✅ Recommendation Quantity Parity: Correctly detected 2 violations
- ✅ Partner Offer Access Parity: Correctly showed PASS
- ✅ Legacy Metric: Maintained backwards compatibility (100% PASS)

### Regression Testing

After any changes to:
- Persona assignment logic (`personas/persona_assigner.py`)
- Recommendation engine (`recommend/recommendation_engine.py`)
- Data generation (`ingest/data_generator.py`)

**Required**:
```bash
uv run python -m eval.run
# Review docs/fairness_report.md for new violations
```

---

<a name="interpretation"></a>
## 6. Interpreting Results

### When All Metrics Pass ✅

**Interpretation**: The system demonstrates demographic parity across persona assignments, service quality, and opportunity access.

**Action**: Continue monitoring. Document passing results for compliance audit trail.

**Note**: Passing metrics do NOT guarantee legal compliance (e.g., they don't test intersectional fairness), but they demonstrate due diligence and systematic monitoring.

### When Persona Distribution Parity Fails ❌

**Example**: "High Utilization" persona assigned to 48% of females vs 27% overall (+21% deviation)

**Potential Causes**:
1. **Data Generation Bias**: Synthetic data generation may inadvertently correlate demographics with behaviors
2. **Behavioral Feature Bias**: Feature detection logic may have unintended demographic correlations
3. **Persona Assignment Logic**: Priority rules may amplify subtle behavioral differences

**Investigation Steps**:
1. Check data generation: Are low credit utilization behaviors correlated with gender in synthetic data?
2. Examine behavioral features: Do certain genders systematically trigger credit-related features?
3. Review persona assignment: Is the priority order amplifying demographic differences?

**Remediation**:
- Adjust data generation to decorrelate demographics from behaviors
- Review feature detection for implicit demographic proxies
- Consider alternative persona assignment strategies (e.g., probabilistic vs deterministic)

### When Recommendation Quantity Parity Fails ❌

**Example**: 51+ age group receives 5.64 avg recommendations vs 4.96 overall (+13.6% deviation)

**Potential Causes**:
1. **Persona Imbalance**: If certain personas generate more recommendations and certain demographics are over-represented in those personas
2. **Behavioral Feature Counts**: Older users may systematically have more detected behaviors (e.g., more subscriptions, more savings patterns)

**Investigation Steps**:
1. Cross-tabulate: Which personas are over-represented in 51+ group?
2. Behavioral analysis: Do older synthetic users have more detected behaviors?
3. Recommendation rules: Do certain personas generate disproportionately many recommendations?

**Remediation**:
- Normalize recommendation counts across personas
- Cap recommendations per user to prevent service quality disparity
- Review data generation for age-correlated behavior patterns

### When Partner Offer Access Parity Fails ❌

**Example**: Low-income users have 65% offer access vs 80% overall (+15% deviation)

**Potential Causes**:
1. **Eligibility Filters**: Partner offer eligibility may have income-correlated requirements (e.g., credit score minimums)
2. **Behavioral Proxies**: Behavioral patterns may serve as proxies for protected characteristics

**Investigation Steps**:
1. Review offer eligibility logic: Are there income-correlated eligibility requirements?
2. Behavioral analysis: Do low-income synthetic users systematically fail certain eligibility checks?
3. Partner offer rules: Are offers disproportionately available to certain personas?

**Remediation**:
- Review offer eligibility for demographic proxies
- Ensure offers are distributed equitably across personas
- Consider income-blind eligibility criteria

---

<a name="future-enhancements"></a>
## 7. Future Enhancements

### Intersectional Fairness Analysis

**Current Limitation**: Metrics analyze each demographic independently (gender, income, region, age separately).

**Enhancement**: Analyze intersections (e.g., low-income + female, 51+ + high-income)

**Rationale**: Disparate impact may only appear at intersections (e.g., system may be fair for "females overall" and "low-income overall" but unfair for "low-income females").

**Implementation**:
```python
# Proposed enhancement
intersectional_groups = [
    ("gender", "income_tier"),
    ("age_bucket", "income_tier"),
    ("gender", "region"),
]

for (demo1, demo2) in intersectional_groups:
    calculate_intersectional_parity(users_df, personas_df, demo1, demo2, tolerance)
```

### Behavioral Outcome Parity

**Current Limitation**: Metrics don't account for baseline behavioral differences.

**Enhancement**: For users with SIMILAR financial behaviors, do they receive SIMILAR personas/recommendations regardless of demographics?

**Rationale**: True fairness requires accounting for legitimate behavioral differences while detecting discrimination.

**Example**:
```python
# Proposed enhancement
# Among users with credit utilization 60-70%, savings rate 5-10%, 2-3 subscriptions:
# Do demographics affect persona assignment or recommendation count?

behavioral_cohorts = cluster_users_by_behavior(users_df, features_df)
for cohort in behavioral_cohorts:
    calculate_within_cohort_fairness(cohort, tolerance)
```

### Counterfactual Fairness

**Concept**: If a user's protected characteristics were changed, would their outcomes change?

**Implementation**: Generate "counterfactual" users with identical behaviors but different demographics, then check for outcome differences.

**Example**:
```python
# Proposed enhancement
user_original = {"age": 55, "income_tier": "low", "behaviors": [...]}
user_counterfactual = {"age": 35, "income_tier": "high", "behaviors": [...]}  # Same behaviors

persona_original = assign_persona(user_original)
persona_counterfactual = assign_persona(user_counterfactual)

assert persona_original == persona_counterfactual  # Should be identical
```

### Statistical Significance Testing

**Current Limitation**: 10% tolerance is fixed; doesn't account for sample size.

**Enhancement**: Use statistical hypothesis testing (e.g., chi-square, two-proportion z-test) to determine if deviations are statistically significant.

**Implementation**:
```python
from scipy.stats import chi2_contingency

# Proposed enhancement
def is_statistically_significant(group_rate, overall_rate, group_size, alpha=0.05):
    # Two-proportion z-test or chi-square test
    # Returns True if deviation is statistically significant at alpha level
    pass
```

### Continuous Monitoring Dashboard

**Current State**: Fairness calculated on-demand via `eval/run.py`

**Enhancement**: Real-time fairness monitoring dashboard in operator UI

**Features**:
- Live fairness metrics updated as new users are added
- Historical trend charts (fairness drift over time)
- Alerting when violations detected
- Drill-down into specific violations

**Implementation**: Add "Fairness" tab to `ui/app_operator_nicegui.py`

---

<a name="references"></a>
## 8. References

### Legal and Regulatory

1. **Equal Credit Opportunity Act (ECOA)** - 15 U.S.C. § 1691 et seq.
   https://www.consumerfinance.gov/rules-policy/regulations/1002/

2. **Regulation B** - 12 CFR Part 1002
   https://www.ecfr.gov/current/title-12/chapter-X/part-1002

3. **FDIC Fair Lending Laws and Regulations**
   https://www.fdic.gov/regulations/compliance/manual/5/v-2.1.pdf

4. **Disparate Impact and Fair Lending** - Consumer Financial Protection Bureau
   https://files.consumerfinance.gov/f/201311_cfpb_bulletin_lending_discrimination.pdf

### Technical and Academic

5. **Fairness Definitions Explained** - Verma & Rubin (2018)
   https://fairware.cs.umass.edu/papers/Verma.pdf

6. **Algorithmic Fairness** - Barocas, Hardt, Narayanan
   https://fairmlbook.org/

7. **50 Years of Test (Un)fairness** - Hutchinson & Mitchell (2019)
   https://arxiv.org/abs/1811.10104

### SpendSense Project Documentation

8. **Project Specification**: `docs/Platinum Project_ Peak6_SpendSense.md`
9. **Evaluation Summary**: `docs/eval_summary.md`
10. **Fairness Report** (Generated): `docs/fairness_report.md`
11. **Implementation**: `eval/fairness.py`, `eval/run.py`

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-08 | Initial production-ready fairness methodology | Casey Manos |

---

## Contact

**Project Lead**: Casey Manos
**Technical Spec**: Bryce Harris (bharris@peak6.com)
**Framework**: ECOA, Regulation B, Disparate Impact Doctrine
**Implementation**: Python 3.11+ with `pandas`, `numpy`, `json`

For questions about fairness methodology or regulatory compliance:
1. Review this document first
2. Check `docs/fairness_report.md` for latest fairness results
3. Contact project lead with specific questions

---

**Document Status**: ✅ Production-Ready
**Last Updated**: 2025-11-08
**Next Review**: After any changes to persona assignment or recommendation logic

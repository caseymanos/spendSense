# Fairness Report - SpendSense Evaluation (Production-Ready)

**Generated**: 2025-11-08T23-59-07

## Executive Summary

This report analyzes fairness across three production-ready metrics to ensure regulatory compliance
(ECOA, Regulation B) and avoid disparate impact in financial recommendations.

### Production Fairness Status

**Overall Status**: ❌ FAIL - 5 fairness violations detected

| Metric | Status | Violations | Regulatory Significance |
|--------|--------|------------|------------------------|
| **Persona Distribution Parity** | ❌ FAIL | 3 | Prevents stigmatizing personas assigned to protected groups |
| **Recommendation Quantity Parity** | ❌ FAIL | 2 | Ensures equitable service quality |
| **Partner Offer Access Parity** | ✅ PASS | 0 | Prevents opportunity redlining |


### ⚠️ Fairness Violations Detected

The following violations require attention:

1. **Cash Flow Optimizer** persona: gender / male shows 15.0% deviation (tolerance: ±10.0%)
2. **Cash Flow Optimizer** persona: region / northeast shows 11.0% deviation (tolerance: ±10.0%)
3. **High Utilization** persona: gender / female shows 21.0% deviation (tolerance: ±10.0%)
4. **Recommendation quantity**: gender / female shows 10.5% deviation (mean: 5.5 vs 5.0)
5. **Recommendation quantity**: age_bucket / 51+ shows 13.6% deviation (mean: 5.6 vs 5.0)

**Action Required**: Review persona assignment logic and data generation process to identify and address sources of disparity.


---

## Legacy Metric (Backwards Compatibility)

**Overall Persona Assignment Rate**: 100.00% (excluding 'general' persona)

**Legacy Status**: ✅ PASS

⚠️ **Note**: The legacy metric only checks if users receive ANY persona, not WHICH persona types.
This metric is kept for backwards compatibility but does NOT provide regulatory compliance assurance.
The production metrics above are the authoritative fairness indicators.


---

## 1. Gender Fairness

**Status**: ✅ PASS
**Max Deviation**: 0.00% (tolerance: ±10.0%)

| Gender | Persona Rate | Deviation from Mean | User Count | Status |
|--------|--------------|---------------------|------------|--------|
| female | 100.00% | +0.00% | 25 | ✅ |
| male | 100.00% | +0.00% | 25 | ✅ |
| non_binary | 100.00% | +0.00% | 25 | ✅ |
| prefer_not_to_say | 100.00% | +0.00% | 25 | ✅ |

---

## 2. Income Tier Fairness

**Status**: ✅ PASS
**Max Deviation**: 0.00% (tolerance: ±10.0%)

| Income Tier | Persona Rate | Deviation from Mean | User Count | Status |
|-------------|--------------|---------------------|------------|--------|
| high | 100.00% | +0.00% | 33 | ✅ |
| low | 100.00% | +0.00% | 34 | ✅ |
| medium | 100.00% | +0.00% | 33 | ✅ |

---

## 3. Region Fairness

**Status**: ✅ PASS
**Max Deviation**: 0.00% (tolerance: ±10.0%)

| Region | Persona Rate | Deviation from Mean | User Count | Status |
|--------|--------------|---------------------|------------|--------|
| midwest | 100.00% | +0.00% | 25 | ✅ |
| northeast | 100.00% | +0.00% | 25 | ✅ |
| south | 100.00% | +0.00% | 25 | ✅ |
| west | 100.00% | +0.00% | 25 | ✅ |

---

## 4. Age Fairness

**Status**: ✅ PASS
**Max Deviation**: 0.00% (tolerance: ±10.0%)
**Age Buckets**: 18-30, 31-50, 51-100

| Age Bucket | Persona Rate | Deviation from Mean | User Count | Status |
|------------|--------------|---------------------|------------|--------|
| 18-30 | 100.00% | +0.00% | 34 | ✅ |
| 31-50 | 100.00% | +0.00% | 33 | ✅ |
| 51+ | 100.00% | +0.00% | 33 | ✅ |

---

## 5. Production Metric: Persona Distribution Parity

**Primary Fairness Metric** - Measures whether specific persona TYPES are assigned equitably across demographics.

**Status**: ❌ FAIL
**Personas Checked**: 5 (Cash Flow Optimizer, High Utilization, General, Savings Builder, Subscription-Heavy)

### Per-Persona Fairness Analysis


#### ❌ Cash Flow Optimizer

**Overall Assignment Rate**: 57.00%
**Max Deviation**: 15.00%

**⚠️ Gender Violation**:
- female: 44.0% (deviation: +13.0%)
- male: 72.0% (deviation: +15.0%)
**⚠️ Region Violation**:
- northeast: 68.0% (deviation: +11.0%)

#### ❌ High Utilization

**Overall Assignment Rate**: 27.00%
**Max Deviation**: 21.00%

**⚠️ Gender Violation**:
- female: 48.0% (deviation: +21.0%)
- male: 12.0% (deviation: +15.0%)

#### ✅ General

**Overall Assignment Rate**: 8.00%
**Max Deviation**: 8.00%


#### ✅ Savings Builder

**Overall Assignment Rate**: 2.00%
**Max Deviation**: 4.06%


#### ✅ Subscription-Heavy

**Overall Assignment Rate**: 6.00%
**Max Deviation**: 6.00%


---

## 6. Production Metric: Recommendation Quantity Parity

**Service Quality Metric** - Ensures all demographic groups receive similar numbers of recommendations.

**Status**: ❌ FAIL
**Overall Mean**: 4.96 recommendations per user

| Demographic | Group | Mean Recommendations | Deviation |
|-------------|-------|---------------------|-----------|
| Gender | female | 5.48 | +10.5% ❌ |
| Gender | male | 4.72 | +4.8% ✅ |
| Gender | non_binary | 4.68 | +5.7% ✅ |
| Gender | prefer_not_to_say | 4.96 | +0.0% ✅ |
| Income Tier | high | 5.21 | +5.1% ✅ |
| Income Tier | low | 4.76 | +3.9% ✅ |
| Income Tier | medium | 4.91 | +1.0% ✅ |
| Region | midwest | 5.00 | +0.8% ✅ |
| Region | northeast | 5.28 | +6.5% ✅ |
| Region | south | 4.64 | +6.5% ✅ |
| Region | west | 4.92 | +0.8% ✅ |
| Age Bucket | 18-30 | 4.82 | +2.8% ✅ |
| Age Bucket | 31-50 | 4.42 | +10.8% ❌ |
| Age Bucket | 51+ | 5.64 | +13.6% ❌ |

---

## 7. Production Metric: Partner Offer Access Parity

**Opportunity Equity Metric** - Ensures equitable access to premium partner offers.

**Status**: ✅ PASS
**Overall Offer Access Rate**: 80.00%

| Demographic | Group | Offer Access Rate | Deviation |
|-------------|-------|------------------|-----------|
| Gender | female | 88.0% | +8.0% ✅ |
| Gender | male | 80.0% | +0.0% ✅ |
| Gender | non_binary | 72.0% | +8.0% ✅ |
| Gender | prefer_not_to_say | 80.0% | +0.0% ✅ |
| Income Tier | high | 87.9% | +7.9% ✅ |
| Income Tier | low | 70.6% | +9.4% ✅ |
| Income Tier | medium | 81.8% | +1.8% ✅ |
| Region | midwest | 80.0% | +0.0% ✅ |
| Region | northeast | 88.0% | +8.0% ✅ |
| Region | south | 72.0% | +8.0% ✅ |
| Region | west | 80.0% | +0.0% ✅ |
| Age Bucket | 18-30 | 82.3% | +2.4% ✅ |
| Age Bucket | 31-50 | 72.7% | +7.3% ✅ |
| Age Bucket | 51+ | 84.9% | +4.9% ✅ |

---

## 8. Detailed Persona Distribution

### Overall Persona Distribution

| Persona | User Count |
|---------|------------|
| Cash Flow Optimizer | 57 |
| General | 8 |
| High Utilization | 27 |
| Savings Builder | 2 |
| Subscription-Heavy | 6 |

### Gender × Persona Cross-Tabulation

| Gender | high_utilization | general | Other |
|--------|------------------|---------|-------|
| female | 0.0% | 0.0% | 100.0% |
| male | 0.0% | 0.0% | 100.0% |
| non_binary | 0.0% | 0.0% | 100.0% |
| prefer_not_to_say | 0.0% | 0.0% | 100.0% |

---

## 9. Methodology & Regulatory Context

### Production-Ready Fairness Metrics

**1. Persona Distribution Parity** (Primary - ECOA Compliance)

**Definition**: For each persona type, the assignment rate across each demographic group must be within ±10.0% of the overall assignment rate for that persona.

**Why it matters**: Detects if certain demographics are disproportionately assigned to potentially stigmatizing personas (e.g., "High Utilization"). This is critical for avoiding disparate impact under ECOA and Regulation B.

**Example**: If 27% of all users are "High Utilization", then 27% ±10.0% (24.3%-29.7%) of EACH demographic group should be assigned this persona.

**2. Recommendation Quantity Parity** (Service Quality)

**Definition**: The average number of recommendations per user must be within ±10.0% across all demographic groups.

**Why it matters**: Ensures all users receive equitable service quality. Prevents scenarios where certain demographics receive fewer recommendations (inferior service).

**3. Partner Offer Access Parity** (Opportunity Equity)

**Definition**: Among users who receive recommendations, the % who receive partner offers must be within ±10.0% across demographics.

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
- ±10.0% tolerance balances statistical rigor with sample size limitations
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

**Report Generated**: 2025-11-08T23-59-07
**Evaluation Version**: Production-Ready Fairness Metrics v1.0
**Regulatory Framework**: ECOA, Regulation B, Disparate Impact Doctrine
**Contact**: Casey Manos (Project Lead) | Bryce Harris (bharris@peak6.com)

**For detailed fairness methodology**, see: `docs/FAIRNESS_METHODOLOGY.md`

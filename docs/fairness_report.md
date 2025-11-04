# Fairness Report - SpendSense Evaluation

**Generated**: 2025-11-04T10-51-35

## Executive Summary

This report analyzes demographic parity in persona assignment across four protected characteristics: gender, income tier, region, and age. Fairness is measured by ensuring that persona assignment rates (excluding 'general' persona) are within ±10.0% of the overall mean across all demographic groups.

**Overall Persona Assignment Rate**: 73.00% (excluding 'general' persona)

**Fairness Status**: ❌ FAIL - 3 demographics outside tolerance


**Failing Demographics**: gender, income_tier, region


---

## 1. Gender Fairness

**Status**: ❌ FAIL
**Max Deviation**: 12.13% (tolerance: ±10.0%)

| Gender | Persona Rate | Deviation from Mean | User Count | Status |
|--------|--------------|---------------------|------------|--------|
| female | 78.57% | +5.57% | 28 | ✅ |
| male | 71.43% | +1.57% | 28 | ✅ |
| non_binary | 80.95% | +7.95% | 21 | ✅ |
| prefer_not_to_say | 60.87% | +12.13% | 23 | ❌ |

---

## 2. Income Tier Fairness

**Status**: ❌ FAIL
**Max Deviation**: 11.89% (tolerance: ±10.0%)

| Income Tier | Persona Rate | Deviation from Mean | User Count | Status |
|-------------|--------------|---------------------|------------|--------|
| high | 84.38% | +11.38% | 32 | ❌ |
| low | 75.00% | +2.00% | 32 | ✅ |
| medium | 61.11% | +11.89% | 36 | ❌ |

---

## 3. Region Fairness

**Status**: ❌ FAIL
**Max Deviation**: 15.31% (tolerance: ±10.0%)

| Region | Persona Rate | Deviation from Mean | User Count | Status |
|--------|--------------|---------------------|------------|--------|
| midwest | 57.69% | +15.31% | 26 | ❌ |
| northeast | 77.27% | +4.27% | 22 | ✅ |
| south | 84.62% | +11.62% | 26 | ❌ |
| west | 73.08% | +0.08% | 26 | ✅ |

---

## 4. Age Fairness

**Status**: ✅ PASS
**Max Deviation**: 5.57% (tolerance: ±10.0%)
**Age Buckets**: 18-30, 31-50, 51-100

| Age Bucket | Persona Rate | Deviation from Mean | User Count | Status |
|------------|--------------|---------------------|------------|--------|
| 18-30 | 70.83% | +2.17% | 24 | ✅ |
| 31-50 | 67.65% | +5.35% | 34 | ✅ |
| 51+ | 78.57% | +5.57% | 42 | ✅ |

---

## 5. Detailed Persona Distribution

### Overall Persona Distribution

| Persona | User Count |
|---------|------------|
| general | 27 |
| high_utilization | 35 |
| savings_builder | 12 |
| subscription_heavy | 26 |

### Gender × Persona Cross-Tabulation

| Gender | high_utilization | general | Other |
|--------|------------------|---------|-------|
| female | 32.1% | 21.4% | 46.4% |
| male | 39.3% | 28.6% | 32.1% |
| non_binary | 42.9% | 19.1% | 38.1% |
| prefer_not_to_say | 26.1% | 39.1% | 34.8% |

---

## 6. Methodology

**Fairness Metric**: Demographic parity in persona assignment rates

**Definition**: For each demographic group, the persona assignment rate (excluding 'general' persona) must be within ±10.0% of the overall mean.

**Rationale**:
- Demographics are used ONLY for fairness analysis, not for persona assignment logic
- 'General' persona is excluded because it represents users with insufficient behavioral signals
- ±10.0% tolerance balances statistical rigor with sample size limitations

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

**Report Generated**: 2025-11-04T10-51-35
**Evaluation Version**: PR #8 Evaluation Harness
**Contact**: Casey Manos (Project Lead)

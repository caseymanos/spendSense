# Fairness Report - SpendSense Evaluation

**Generated**: 2025-11-03T23-50-34

## Executive Summary

This report analyzes demographic parity in persona assignment across four protected characteristics: gender, income tier, region, and age. Fairness is measured by ensuring that persona assignment rates (excluding 'general' persona) are within ±10.0% of the overall mean across all demographic groups.

**Overall Persona Assignment Rate**: 35.00% (excluding 'general' persona)

**Fairness Status**: ❌ FAIL - 3 demographics outside tolerance


**Failing Demographics**: gender, region, age


---

## 1. Gender Fairness

**Status**: ❌ FAIL
**Max Deviation**: 21.96% (tolerance: ±10.0%)

| Gender | Persona Rate | Deviation from Mean | User Count | Status |
|--------|--------------|---------------------|------------|--------|
| female | 42.86% | +7.86% | 28 | ✅ |
| male | 39.29% | +4.29% | 28 | ✅ |
| non_binary | 42.86% | +7.86% | 21 | ✅ |
| prefer_not_to_say | 13.04% | +21.96% | 23 | ❌ |

---

## 2. Income Tier Fairness

**Status**: ✅ PASS
**Max Deviation**: 6.87% (tolerance: ±10.0%)

| Income Tier | Persona Rate | Deviation from Mean | User Count | Status |
|-------------|--------------|---------------------|------------|--------|
| high | 34.38% | +0.62% | 32 | ✅ |
| low | 28.12% | +6.87% | 32 | ✅ |
| medium | 41.67% | +6.67% | 36 | ✅ |

---

## 3. Region Fairness

**Status**: ❌ FAIL
**Max Deviation**: 15.77% (tolerance: ±10.0%)

| Region | Persona Rate | Deviation from Mean | User Count | Status |
|--------|--------------|---------------------|------------|--------|
| midwest | 19.23% | +15.77% | 26 | ❌ |
| northeast | 27.27% | +7.73% | 22 | ✅ |
| south | 46.15% | +11.15% | 26 | ❌ |
| west | 46.15% | +11.15% | 26 | ❌ |

---

## 4. Age Fairness

**Status**: ❌ FAIL
**Max Deviation**: 14.17% (tolerance: ±10.0%)
**Age Buckets**: 18-30, 31-50, 51-100

| Age Bucket | Persona Rate | Deviation from Mean | User Count | Status |
|------------|--------------|---------------------|------------|--------|
| 18-30 | 20.83% | +14.17% | 24 | ❌ |
| 31-50 | 41.18% | +6.18% | 34 | ✅ |
| 51+ | 38.10% | +3.10% | 42 | ✅ |

---

## 5. Detailed Persona Distribution

### Overall Persona Distribution

| Persona | User Count |
|---------|------------|
| general | 65 |
| high_utilization | 35 |

### Gender × Persona Cross-Tabulation

| Gender | high_utilization | general | Other |
|--------|------------------|---------|-------|
| female | 42.9% | 57.1% | 0.0% |
| male | 39.3% | 60.7% | 0.0% |
| non_binary | 42.9% | 57.1% | 0.0% |
| prefer_not_to_say | 13.0% | 87.0% | 0.0% |

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

**Report Generated**: 2025-11-03T23-50-34
**Evaluation Version**: PR #8 Evaluation Harness
**Contact**: Casey Manos (Project Lead)

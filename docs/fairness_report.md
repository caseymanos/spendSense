# Fairness Report - SpendSense Evaluation

**Generated**: 2025-11-04T21-52-49

## Executive Summary

This report analyzes demographic parity in persona assignment across four protected characteristics: gender, income tier, region, and age. Fairness is measured by ensuring that persona assignment rates (excluding 'general' persona) are within ±10.0% of the overall mean across all demographic groups.

**Overall Persona Assignment Rate**: 82.00% (excluding 'general' persona)

**Fairness Status**: ✅ PASS - All demographics within tolerance


---

## 1. Gender Fairness

**Status**: ✅ PASS
**Max Deviation**: 10.00% (tolerance: ±10.0%)

| Gender | Persona Rate | Deviation from Mean | User Count | Status |
|--------|--------------|---------------------|------------|--------|
| female | 72.00% | +10.00% | 25 | ✅ |
| male | 88.00% | +6.00% | 25 | ✅ |
| non_binary | 76.00% | +6.00% | 25 | ✅ |
| prefer_not_to_say | 92.00% | +10.00% | 25 | ✅ |

---

## 2. Income Tier Fairness

**Status**: ✅ PASS
**Max Deviation**: 2.85% (tolerance: ±10.0%)

| Income Tier | Persona Rate | Deviation from Mean | User Count | Status |
|-------------|--------------|---------------------|------------|--------|
| high | 84.85% | +2.85% | 33 | ✅ |
| low | 79.41% | +2.59% | 34 | ✅ |
| medium | 81.82% | +0.18% | 33 | ✅ |

---

## 3. Region Fairness

**Status**: ✅ PASS
**Max Deviation**: 10.00% (tolerance: ±10.0%)

| Region | Persona Rate | Deviation from Mean | User Count | Status |
|--------|--------------|---------------------|------------|--------|
| midwest | 72.00% | +10.00% | 25 | ✅ |
| northeast | 84.00% | +2.00% | 25 | ✅ |
| south | 84.00% | +2.00% | 25 | ✅ |
| west | 88.00% | +6.00% | 25 | ✅ |

---

## 4. Age Fairness

**Status**: ✅ PASS
**Max Deviation**: 6.24% (tolerance: ±10.0%)
**Age Buckets**: 18-30, 31-50, 51-100

| Age Bucket | Persona Rate | Deviation from Mean | User Count | Status |
|------------|--------------|---------------------|------------|--------|
| 18-30 | 85.29% | +3.29% | 34 | ✅ |
| 31-50 | 84.85% | +2.85% | 33 | ✅ |
| 51+ | 75.76% | +6.24% | 33 | ✅ |

---

## 5. Detailed Persona Distribution

### Overall Persona Distribution

| Persona | User Count |
|---------|------------|
| general | 18 |
| high_utilization | 33 |
| savings_builder | 18 |
| subscription_heavy | 31 |

### Gender × Persona Cross-Tabulation

| Gender | high_utilization | general | Other |
|--------|------------------|---------|-------|
| female | 36.0% | 28.0% | 36.0% |
| male | 36.0% | 12.0% | 52.0% |
| non_binary | 24.0% | 24.0% | 52.0% |
| prefer_not_to_say | 36.0% | 8.0% | 56.0% |

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

**Report Generated**: 2025-11-04T21-52-49
**Evaluation Version**: PR #8 Evaluation Harness
**Contact**: Casey Manos (Project Lead)

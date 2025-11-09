# Evaluation Summary - SpendSense

**Generated**: 2025-11-08T23-59-07

## Overall Status

⚠️ **FAIRNESS VIOLATIONS DETECTED**

**Total Users**: 100
**Core Metrics**: 5/5 ✅ (Coverage, Explainability, Relevance, Latency, Auditability)
**Fairness**: ❌ Production compliance FAIL (5 violations) | ✅ Legacy metric PASS

**Production-Ready Fairness**: The new compliance-grade metrics detect 5 fairness violations that require attention:
- 3 persona distribution parity violations (disparate impact risk)
- 2 recommendation quantity parity violations (service quality disparity)

See [fairness_report.md](fairness_report.md) for detailed regulatory analysis.

---

## Core Metrics

### 1. Coverage
**Definition**: % of users with assigned persona (including 'general')

- **Value**: 100.00%
- **Target**: 100.00%
- **Status**: ✅ PASS
- **Details**:
  - Total users: 100
  - Users with persona: 100
  - Users with meaningful persona (non-general): 100
  - Users with ≥3 behaviors: 57
  - Legacy metric (meaningful + ≥3 behaviors): 57

### 2. Explainability
**Definition**: % of recommendations with non-empty rationale text

- **Value**: 100.00%
- **Target**: 100.00%
- **Status**: ✅ PASS
- **Details**:
  - Total recommendations: 496
  - Recommendations with rationale: 496
  - Recommendations without rationale: 0

### 3. Relevance
**Definition**: Rule-based persona → content category alignment

- **Value**: 100.00%
- **Target**: 90.00%
- **Status**: ✅ PASS
- **Details**:
  - Total recommendations: 154
  - Relevant recommendations: 154
  - Irrelevant recommendations: 0

### 4. Latency
**Definition**: Mean time to generate recommendations per user

- **Value**: 0.0109s
- **Target**: <5.0s
- **Status**: ✅ PASS
- **Details**:
  - Users tested: 99
  - Mean: 0.0109s
  - Median: 0.0107s
  - P95: 0.0121s
  - Max: 0.0182s

### 5. Auditability
**Definition**: % of users with complete trace JSONs

- **Value**: 100.00%
- **Target**: 100.00%
- **Status**: ✅ PASS
- **Details**:
  - Total users: 100
  - Users with trace file: 100
  - Users with complete trace: 100
  - Completeness: 100.00%

### 6. Fairness (Production-Ready Compliance Metrics)
**Definition**: Regulatory compliance with ECOA/Regulation B via 3-tier fairness analysis

- **Production Status**: ❌ FAIL
- **Legacy Status**: ✅ PASS (backwards compatibility)
- **Total Violations**: 5 fairness issues detected
- **Details**:
  - **Persona Distribution Parity**: ❌ FAIL (3 violations)
    - Cash Flow Optimizer / gender / male: 15.0% deviation
    - Cash Flow Optimizer / region / northeast: 11.0% deviation
    - High Utilization / gender / female: 21.0% deviation
  - **Recommendation Quantity Parity**: ❌ FAIL (2 violations)
    - gender / female: 10.5% deviation
    - age_bucket / 51+: 13.6% deviation
  - **Partner Offer Access Parity**: ✅ PASS
  - **Legacy Metric** (overall persona rate): 100.00% ✅

**Note**: Production metrics detect disparate impact that legacy metric misses. See [fairness_report.md](fairness_report.md) for regulatory context and detailed analysis.

---

## Recommendations


---

## Files Generated

- **JSON**: `eval/results_2025-11-08T23-59-07.json`
- **CSV**: `eval/results_2025-11-08T23-59-07.csv`
- **Summary**: `docs/eval_summary.md` (this file)
- **Fairness Report**: `docs/fairness_report.md`

See detailed fairness analysis in [fairness_report.md](fairness_report.md).

---

**Evaluation Version**: PR #8 Evaluation Harness
**Contact**: Casey Manos (Project Lead)

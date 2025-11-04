# Evaluation Summary - SpendSense

**Generated**: 2025-11-04T11-03-53

## Overall Status

❌ **SOME METRICS FAIL**

**Total Users**: 100
**Metrics Passing**: 3/6

---

## Core Metrics

### 1. Coverage
**Definition**: % of users with meaningful persona + ≥3 detected behaviors

- **Value**: 65.00%
- **Target**: 100.00%
- **Status**: ❌ FAIL
- **Details**:
  - Total users: 100
  - Users with meaningful persona: 82
  - Users with ≥3 behaviors: 73
  - Users with both: 65

### 2. Explainability
**Definition**: % of recommendations with non-empty rationale text

- **Value**: 100.00%
- **Target**: 100.00%
- **Status**: ✅ PASS
- **Details**:
  - Total recommendations: 461
  - Recommendations with rationale: 461
  - Recommendations without rationale: 0

### 3. Relevance
**Definition**: Rule-based persona → content category alignment

- **Value**: 100.00%
- **Target**: 90.00%
- **Status**: ✅ PASS
- **Details**:
  - Total recommendations: 461
  - Relevant recommendations: 461
  - Irrelevant recommendations: 0

### 4. Latency
**Definition**: Mean time to generate recommendations per user

- **Value**: 0.0100s
- **Target**: <5.0s
- **Status**: ✅ PASS
- **Details**:
  - Users tested: 100
  - Mean: 0.0100s
  - Median: 0.0098s
  - P95: 0.0112s
  - Max: 0.0175s

### 5. Auditability
**Definition**: % of users with complete trace JSONs

- **Value**: 82.00%
- **Target**: 100.00%
- **Status**: ❌ FAIL
- **Details**:
  - Total users: 100
  - Users with trace file: 100
  - Users with complete trace: 82
  - Completeness: 82.00%

### 6. Fairness
**Definition**: Demographic parity in persona assignments (±10% tolerance)

- **Value**: FAIL
- **Target**: PASS
- **Status**: ❌ FAIL
- **Details**:
  - Overall persona rate: 82.00%
  - Failing demographics: gender
  - Gender: ❌
  - Income Tier: ✅
  - Region: ✅
  - Age: ✅

---

## Recommendations


### Coverage Improvement
- **Issue**: Only 65.00% of users have meaningful persona + ≥3 behaviors
- **Actions**:
  1. Review data generation to ensure diverse financial behaviors
  2. Consider lowering behavior detection thresholds
  3. Investigate users with 'general' persona for potential reclassification

### Fairness Improvement
- **Issue**: Demographic parity violations in gender
- **Actions**:
  1. Analyze persona assignment logic for potential bias
  2. Review synthetic data generation for demographic balance
  3. Consider threshold adjustments for underserved groups

---

## Files Generated

- **JSON**: `eval/results_2025-11-04T11-03-53.json`
- **CSV**: `eval/results_2025-11-04T11-03-53.csv`
- **Summary**: `docs/eval_summary.md` (this file)
- **Fairness Report**: `docs/fairness_report.md`

See detailed fairness analysis in [fairness_report.md](fairness_report.md).

---

**Evaluation Version**: PR #8 Evaluation Harness
**Contact**: Casey Manos (Project Lead)

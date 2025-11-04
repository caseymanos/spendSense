# Evaluation Summary - SpendSense

**Generated**: 2025-11-03T23-50-34

## Overall Status

❌ **SOME METRICS FAIL**

**Total Users**: 100
**Metrics Passing**: 3/6

---

## Core Metrics

### 1. Coverage
**Definition**: % of users with meaningful persona + ≥3 detected behaviors

- **Value**: 0.00%
- **Target**: 100.00%
- **Status**: ❌ FAIL
- **Details**:
  - Total users: 100
  - Users with meaningful persona: 35
  - Users with ≥3 behaviors: 0
  - Users with both: 0

### 2. Explainability
**Definition**: % of recommendations with non-empty rationale text

- **Value**: 100.00%
- **Target**: 100.00%
- **Status**: ✅ PASS
- **Details**:
  - Total recommendations: 39
  - Recommendations with rationale: 39
  - Recommendations without rationale: 0

### 3. Relevance
**Definition**: Rule-based persona → content category alignment

- **Value**: 100.00%
- **Target**: 90.00%
- **Status**: ✅ PASS
- **Details**:
  - Total recommendations: 38
  - Relevant recommendations: 38
  - Irrelevant recommendations: 0

### 4. Latency
**Definition**: Mean time to generate recommendations per user

- **Value**: 0.0102s
- **Target**: <5.0s
- **Status**: ✅ PASS
- **Details**:
  - Users tested: 10
  - Mean: 0.0102s
  - Median: 0.0101s
  - P95: 0.0111s
  - Max: 0.0112s

### 5. Auditability
**Definition**: % of users with complete trace JSONs

- **Value**: 97.00%
- **Target**: 100.00%
- **Status**: ❌ FAIL
- **Details**:
  - Total users: 100
  - Users with trace file: 100
  - Users with complete trace: 97
  - Completeness: 97.00%

### 6. Fairness
**Definition**: Demographic parity in persona assignments (±10% tolerance)

- **Value**: FAIL
- **Target**: PASS
- **Status**: ❌ FAIL
- **Details**:
  - Overall persona rate: 35.00%
  - Failing demographics: gender, region, age
  - Gender: ❌
  - Income Tier: ✅
  - Region: ❌
  - Age: ❌

---

## Recommendations


### Coverage Improvement
- **Issue**: Only 0.00% of users have meaningful persona + ≥3 behaviors
- **Actions**:
  1. Review data generation to ensure diverse financial behaviors
  2. Consider lowering behavior detection thresholds
  3. Investigate users with 'general' persona for potential reclassification

### Fairness Improvement
- **Issue**: Demographic parity violations in gender, region, age
- **Actions**:
  1. Analyze persona assignment logic for potential bias
  2. Review synthetic data generation for demographic balance
  3. Consider threshold adjustments for underserved groups

---

## Files Generated

- **JSON**: `eval/results_2025-11-03T23-50-34.json`
- **CSV**: `eval/results_2025-11-03T23-50-34.csv`
- **Summary**: `docs/eval_summary.md` (this file)
- **Fairness Report**: `docs/fairness_report.md`

See detailed fairness analysis in [fairness_report.md](fairness_report.md).

---

**Evaluation Version**: PR #8 Evaluation Harness
**Contact**: Casey Manos (Project Lead)

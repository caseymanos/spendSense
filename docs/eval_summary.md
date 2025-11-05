# Evaluation Summary - SpendSense

**Generated**: 2025-11-04T21-52-49

## Overall Status

❌ **SOME METRICS FAIL**

**Total Users**: 100
**Metrics Passing**: 4/5
**Tracking Only**: coverage

---

## Core Metrics

### 1. Coverage
**Definition**: % of users with meaningful persona + ≥3 detected behaviors

- **Value**: 29.00%
- **Target**: —
- **Status**: TRACKING (no pass/fail threshold set)
- **Details**:
  - Total users: 100
  - Users with meaningful persona: 82
  - Users with ≥3 behaviors: 38
  - Users with both: 29

### 2. Explainability
**Definition**: % of recommendations with non-empty rationale text

- **Value**: 100.00%
- **Target**: 100.00%
- **Status**: ✅ PASS
- **Details**:
  - Total recommendations: 204
  - Recommendations with rationale: 204
  - Recommendations without rationale: 0

### 3. Relevance
**Definition**: Rule-based persona → content category alignment

- **Value**: 84.14%
- **Target**: 90.00%
- **Status**: ❌ FAIL
- **Details**:
  - Total recommendations: 145
  - Relevant recommendations: 122
  - Irrelevant recommendations: 23

### 4. Latency
**Definition**: Mean time to generate recommendations per user

- **Value**: 0.0108s
- **Target**: <5.0s
- **Status**: ✅ PASS
- **Details**:
  - Users tested: 99
  - Mean: 0.0108s
  - Median: 0.0102s
  - P95: 0.0138s
  - Max: 0.0210s

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

### 6. Fairness
**Definition**: Demographic parity in persona assignments (±10% tolerance)

- **Value**: PASS
- **Target**: PASS
- **Status**: ✅ PASS
- **Details**:
  - Overall persona rate: 82.00%
  - Failing demographics: None
  - Gender: ✅
  - Income Tier: ✅
  - Region: ✅
  - Age: ✅

---

## Recommendations


### Coverage Improvement
- **Issue**: Only 29.00% of users have meaningful persona + ≥3 behaviors
- **Actions**:
  1. Review data generation to ensure diverse financial behaviors
  2. Consider lowering behavior detection thresholds
  3. Investigate users with 'general' persona for potential reclassification

### Relevance Improvement
- **Issue**: 84.14% relevance below 90% target
- **Actions**:
  1. Review content catalog category mappings
  2. Verify persona → content alignment logic
  3. Investigate irrelevant recommendations sample

---

## Files Generated

- **JSON**: `eval/results_2025-11-04T21-52-49.json`
- **CSV**: `eval/results_2025-11-04T21-52-49.csv`
- **Summary**: `docs/eval_summary.md` (this file)
- **Fairness Report**: `docs/fairness_report.md`

See detailed fairness analysis in [fairness_report.md](fairness_report.md).

---

**Evaluation Version**: PR #8 Evaluation Harness
**Contact**: Casey Manos (Project Lead)

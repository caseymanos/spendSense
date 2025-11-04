# Evaluation Summary - SpendSense

**Generated**: 2025-11-04T10-51-35

## Overall Status

❌ **SOME METRICS FAIL**

**Total Users**: 100
**Metrics Passing**: 2/6

---

## Core Metrics

### 1. Coverage
**Definition**: % of users with meaningful persona + ≥3 detected behaviors

- **Value**: 58.00%
- **Target**: 100.00%
- **Status**: ❌ FAIL
- **Details**:
  - Total users: 100
  - Users with meaningful persona: 73
  - Users with ≥3 behaviors: 64
  - Users with both: 58

### 2. Explainability
**Definition**: % of recommendations with non-empty rationale text

- **Value**: 100.00%
- **Target**: 100.00%
- **Status**: ✅ PASS
- **Details**:
  - Total recommendations: 173
  - Recommendations with rationale: 173
  - Recommendations without rationale: 0

### 3. Relevance
**Definition**: Rule-based persona → content category alignment

- **Value**: 70.51%
- **Target**: 90.00%
- **Status**: ❌ FAIL
- **Details**:
  - Total recommendations: 156
  - Relevant recommendations: 110
  - Irrelevant recommendations: 46

### 4. Latency
**Definition**: Mean time to generate recommendations per user

- **Value**: 0.0087s
- **Target**: <5.0s
- **Status**: ✅ PASS
- **Details**:
  - Users tested: 100
  - Mean: 0.0087s
  - Median: 0.0087s
  - P95: 0.0095s
  - Max: 0.0113s

### 5. Auditability
**Definition**: % of users with complete trace JSONs

- **Value**: 90.00%
- **Target**: 100.00%
- **Status**: ❌ FAIL
- **Details**:
  - Total users: 100
  - Users with trace file: 100
  - Users with complete trace: 90
  - Completeness: 90.00%

### 6. Fairness
**Definition**: Demographic parity in persona assignments (±10% tolerance)

- **Value**: FAIL
- **Target**: PASS
- **Status**: ❌ FAIL
- **Details**:
  - Overall persona rate: 73.00%
  - Failing demographics: gender, income_tier, region
  - Gender: ❌
  - Income Tier: ❌
  - Region: ❌
  - Age: ✅

---

## Recommendations


### Coverage Improvement
- **Issue**: Only 58.00% of users have meaningful persona + ≥3 behaviors
- **Actions**:
  1. Review data generation to ensure diverse financial behaviors
  2. Consider lowering behavior detection thresholds
  3. Investigate users with 'general' persona for potential reclassification

### Relevance Improvement
- **Issue**: 70.51% relevance below 90% target
- **Actions**:
  1. Review content catalog category mappings
  2. Verify persona → content alignment logic
  3. Investigate irrelevant recommendations sample

### Fairness Improvement
- **Issue**: Demographic parity violations in gender, income_tier, region
- **Actions**:
  1. Analyze persona assignment logic for potential bias
  2. Review synthetic data generation for demographic balance
  3. Consider threshold adjustments for underserved groups

---

## Files Generated

- **JSON**: `eval/results_2025-11-04T10-51-35.json`
- **CSV**: `eval/results_2025-11-04T10-51-35.csv`
- **Summary**: `docs/eval_summary.md` (this file)
- **Fairness Report**: `docs/fairness_report.md`

See detailed fairness analysis in [fairness_report.md](fairness_report.md).

---

**Evaluation Version**: PR #8 Evaluation Harness
**Contact**: Casey Manos (Project Lead)

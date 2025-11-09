# Evaluation Summary - SpendSense

**Generated**: 2025-11-08T21-53-10

## Overall Status

✅ **ALL METRICS PASS**

**Total Users**: 100
**Metrics Passing**: 6/6

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

- **Value**: 0.0105s
- **Target**: <5.0s
- **Status**: ✅ PASS
- **Details**:
  - Users tested: 99
  - Mean: 0.0105s
  - Median: 0.0102s
  - P95: 0.0119s
  - Max: 0.0201s

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
  - Overall persona rate: 100.00%
  - Failing demographics: None
  - Gender: ✅
  - Income Tier: ✅
  - Region: ✅
  - Age: ✅

---

## Recommendations


---

## Files Generated

- **JSON**: `eval/results_2025-11-08T21-53-10.json`
- **CSV**: `eval/results_2025-11-08T21-53-10.csv`
- **Summary**: `docs/eval_summary.md` (this file)
- **Fairness Report**: `docs/fairness_report.md`

See detailed fairness analysis in [fairness_report.md](fairness_report.md).

---

**Evaluation Version**: PR #8 Evaluation Harness
**Contact**: Casey Manos (Project Lead)

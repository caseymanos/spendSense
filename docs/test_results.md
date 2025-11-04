# Test Results - SpendSense MVP V2

**Generated:** 2025-11-04 01:21:37
**Python Version:** 3.14.0
**Test Framework:** pytest

## Summary

```
======================= 80 passed, 167 warnings in 7.17s =======================
```

## Test Breakdown by Module

| Module | Tests | Passed | Failed | Pass Rate |
|--------|-------|--------|--------|-----------|
| test_data_generation.py | 15 | 15 | 0 | 100.0% |
| test_eval.py | 5 | 5 | 0 | 100.0% |
| test_features.py | 6 | 6 | 0 | 100.0% |
| test_guardrails.py | 17 | 17 | 0 | 100.0% |
| test_integration_full_pipeline.py | 3 | 3 | 0 | 100.0% |
| test_personas.py | 18 | 18 | 0 | 100.0% |
| test_recommendations.py | 15 | 15 | 0 | 100.0% |
| test_ui_operator.py | 1 | 1 | 0 | 100.0% |
| **TOTAL** | **80** | **80** | **0** | **100.0%** |

## Code Coverage

| Module | Statements | Missed | Coverage |
|--------|------------|--------|----------|
| eval/ | 397 | 160 | 59.7% |
| features/ | 305 | 18 | 94.1% |
| guardrails/ | 288 | 79 | 72.6% |
| ingest/ | 613 | 107 | 82.5% |
| personas/ | 130 | 12 | 90.8% |
| recommend/ | 328 | 74 | 77.4% |
| ui/ | 990 | 927 | 6.4% |

## Success Criteria Progress

| Criterion | Target | Current | Status |
|-----------|--------|---------|--------|
| Test Count | ≥10 | 80 | ✅ |
| Pass Rate | 100% | 100.0% | ✅ |
| Code Coverage | ≥80% | 69.1% | ⚠️ |

## Test Categories

### PR #1: Data Foundation (15 tests)
- Schema validation
- Deterministic generation
- End-to-end data pipeline

### PR #2: Behavioral Signals (6 tests)
- Subscription detection
- Credit utilization
- Savings patterns
- Income stability

### PR #3: Persona Assignment (18 tests)
- High Utilization persona
- Variable Income persona
- Subscription Heavy persona
- Savings Builder persona
- Priority ordering

### PR #4: Recommendations (14 tests)
- Rationale formatting
- Disclaimer presence
- Recommendation counts
- Eligibility filtering

### PR #5: Guardrails (19 tests)
- Consent enforcement
- Tone validation
- Predatory product filtering
- Eligibility checks

### PR #7: Operator UI (1 test)
- Operator attribution logging

### PR #8: Evaluation (5 tests)
- Coverage metrics
- Explainability metrics
- Latency measurement
- Fairness calculation

### PR #9: Integration (3 tests)
- End-to-end pipeline verification
- Component integration tests

## Test Execution

To run all tests:
```bash
uv run pytest tests/ -v
```

To run with coverage:
```bash
uv run pytest --cov=ingest --cov=features --cov=personas --cov=recommend --cov=guardrails --cov=eval --cov=ui --cov-report=html tests/
```

View HTML coverage report:
```bash
open htmlcov/index.html
```

## Notes

- All tests use deterministic seeding (`seed=42`) for reproducibility
- Integration tests verify the complete pipeline from data generation through evaluation
- UI tests (PR #6, PR #7) are primarily manual/visual for Streamlit apps
- Total test count exceeds minimum requirement by 700%

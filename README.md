<<<<<<< HEAD
# spendSense
Explainable financial behavior analysis platform
=======
# SpendSense MVP V2

Explainable, consent-aware financial behavior analysis platform that transforms Plaid-style transaction data into personalized educational recommendations.

## Core Principles

- **Transparency over sophistication** - Every decision is auditable
- **User control over automation** - Explicit consent required
- **Education over sales** - Recommendations focus on learning, not advice
- **Fairness built in from day one** - Demographic parity monitoring

## Quick Start

### Prerequisites

- Python 3.11 or higher
- `uv` (recommended) or `pip`

### Installation

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Generate Synthetic Data

```bash
uv run python -m ingest.data_generator
```

This creates:
- `data/users.sqlite` - User profiles with consent tracking
- `data/transactions.parquet` - 6 months of transaction history for 100 users
- `data/config.json` - Generation configuration

### Run Tests

```bash
# All tests
uv run pytest tests/ -v

# With coverage
uv run pytest --cov=spendsense tests/

# Specific test file
uv run pytest tests/test_data_generation.py -v
```

### Launch Applications

```bash
# User dashboard (educational interface)
uv run streamlit run ui/app_user.py

# Operator dashboard (compliance interface)
uv run streamlit run ui/app_operator.py

# FastAPI backend
uv run uvicorn api.main:app --reload
```

Note for Operator Dashboard:
- Enter your name in the sidebar under "Operator Identity" before approving recommendations. Approvals are blocked until a non-empty operator name is provided to ensure every action is attributable for audit/compliance.

### Run Evaluation

```bash
uv run python -m eval.run --input data/transactions.parquet --output eval/results.json
```

## Project Structure

```
spendsense/
├── ingest/         # Synthetic data generation & validation
├── features/       # Behavioral signal detection
├── personas/       # Persona assignment logic
├── recommend/      # Recommendation engine
├── guardrails/     # Consent, eligibility, tone validation
├── ui/             # Streamlit user & operator dashboards
├── api/            # FastAPI REST endpoints
├── eval/           # Metrics harness
├── docs/           # Decision logs, schema, traces
├── tests/          # Unit & integration tests
└── data/           # SQLite DB + Parquet files (gitignored)
```

## Development

### Code Quality

```bash
# Lint
uv run ruff check .

# Format
uv run black .
```

### Data Schema

See `docs/schema.md` for complete data model documentation.

### Design Decisions

See `docs/decision_log.md` for rationale behind key choices.

## Current Status

**Completed PRs:**
- ✅ PR #1: Project Setup & Data Foundation (15 tests)
- ✅ PR #2: Behavioral Signal Detection (6 tests)
- ✅ PR #3: Persona Assignment System (18 tests)
- ✅ PR #4: Recommendation Engine (15 tests)
- ✅ PR #5: Guardrails & Consent Management (17 tests)
- ✅ PR #6: User Interface (Streamlit App)
- ✅ PR #7: Operator Dashboard (Streamlit App)
- ✅ PR #8: Evaluation Harness (5 tests)
- ✅ PR #9: Testing & Quality Assurance (3 tests)
- ✅ Reflex UI Implementation (web-based user dashboard)

**In Progress:**
- 🔄 PR #10: Documentation & Final Polish

**Total Test Count:** 80 tests passing (800% above minimum requirement)

See `docs/taskList.md` for full 10-PR implementation roadmap.

## Success Criteria

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Coverage | 100% of users with persona + ≥3 behaviors | 0.00% | ❌ FAIL (needs investigation) |
| Explainability | 100% of recommendations with rationale | 100.00% | ✅ PASS |
| Relevance | ≥90% persona-content alignment | 100.00% | ✅ PASS |
| Latency | <5 seconds per user | 0.0102s | ✅ PASS (400x faster) |
| Auditability | 100% trace availability | 97.00% | ⚠️  NEAR (97/100 users) |
| Fairness | ±10% demographic parity | FAIL (3 groups) | ❌ FAIL (gender, region, age) |
| Tests Passing | ≥10 tests | 80 tests | ✅ PASS (800% above target) |

**Note:** Coverage issue (0.00%) requires investigation of behavior detection thresholds or persona assignment logic. See `docs/eval_summary.md` for detailed analysis and recommendations.

## Contact

- Project Lead: Casey Manos
- Technical Spec: Bryce Harris (bharris@peak6.com)

## License

Internal use only. Not for public distribution.
>>>>>>> master

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

**PR #1: Project Setup & Data Foundation** ✅ (In Progress)

See `docs/taskList.md` for full 10-PR implementation roadmap.

## Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Coverage | 100% of users with persona + ≥3 behaviors | TBD |
| Explainability | 100% of recommendations with rationale | TBD |
| Latency | <5 seconds per user | TBD |
| Auditability | 100% trace availability | TBD |
| Fairness | ±10% demographic parity | TBD |
| Tests Passing | ≥10 tests | TBD |

## Contact

- Project Lead: Casey Manos
- Technical Spec: Bryce Harris (bharris@peak6.com)

## License

Internal use only. Not for public distribution.

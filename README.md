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
- Node.js 18+ (for Next.js user dashboard)

### Installation

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt

# Install Next.js dependencies
cd web
npm install
cd ..
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
# All tests (excluding video generation tests)
uv run pytest tests/ -v --ignore=tests/test_video_generation.py

# With coverage
uv run pytest --cov=spendsense tests/ --ignore=tests/test_video_generation.py

# Specific test file
uv run pytest tests/test_personas.py -v
```

**Test Results:** 134 tests passing, 1 skipped

### Launch Applications

#### FastAPI Backend (Required)
```bash
uv run uvicorn api.main:app --reload
# → http://localhost:8000
```

#### Next.js User Dashboard (Recommended)
```bash
cd web
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
# → http://localhost:3000
```

#### NiceGUI Operator Dashboard
```bash
uv run python ui/app_operator_nicegui.py
# → http://localhost:8081
```

Note for Operator Dashboard:
- Enter your name in the sidebar under "Operator Identity" before approving recommendations
- Approvals are blocked until a non-empty operator name is provided to ensure every action is attributable for audit/compliance

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
├── ui/             # NiceGUI operator dashboard
├── web/            # Next.js user dashboard
├── api/            # FastAPI REST endpoints
├── eval/           # Metrics harness (including fairness)
├── docs/           # Decision logs, schema, traces
├── tests/          # Unit & integration tests (134 passing)
└── data/           # SQLite DB + Parquet files (gitignored)
```

## Development

### Code Quality

```bash
# Lint
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format
uv run black .
```

### Documentation

- `docs/schema.md` - Complete data model documentation
- `docs/decision_log.md` - Rationale behind key choices
- `docs/FAIRNESS_METHODOLOGY.md` - Production fairness metrics
- `docs/fairness_report.md` - Latest fairness evaluation
- `docs/taskList.md` - 10-PR implementation roadmap

## Current Status

**Completed Features:**
- ✅ Data Generation & Validation
- ✅ Behavioral Signal Detection
- ✅ Persona Assignment System (5 personas + General)
- ✅ Recommendation Engine with Rationales
- ✅ Consent & Guardrails System
- ✅ Next.js User Dashboard
- ✅ NiceGUI Operator Dashboard
- ✅ FastAPI Backend
- ✅ Evaluation Harness with Production Fairness Metrics
- ✅ Comprehensive Test Suite (134 tests)

**Production Fairness Metrics:**
- Persona Distribution Parity (ECOA compliance)
- Recommendation Quantity Parity (service quality)
- Partner Offer Access Parity (opportunity equity)

**Test Coverage:** 134 tests passing (1340% above minimum requirement of 10 tests)

## Success Criteria

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Coverage | 100% of users with persona + ≥3 behaviors | 100% | ✅ PASS |
| Explainability | 100% of recommendations with rationale | 100% | ✅ PASS |
| Relevance | ≥90% persona-content alignment | 100% | ✅ PASS |
| Latency | <5 seconds per user | ~0.01s | ✅ PASS (500x faster) |
| Auditability | 100% trace availability | 100% | ✅ PASS |
| Production Fairness | ±10% parity (3 metrics) | ⚠️ 5 violations | ⚠️ NEEDS ATTENTION |
| Tests Passing | ≥10 tests | 134 tests | ✅ PASS |

**Fairness Status:**
- ❌ Persona Distribution Parity: 3 violations
- ❌ Recommendation Quantity Parity: 2 violations
- ✅ Partner Offer Access Parity: PASS

See `docs/fairness_report.md` for detailed fairness analysis and mitigation recommendations.

## Deployment

Documentation for production deployment can be found in:
- `docs/deployment/` - Consolidated deployment guides
- `scripts/deployment/` - Deployment helper scripts

## Contact

- Project Lead: Casey Manos
- Technical Spec: Bryce Harris (bharris@peak6.com)

## License

Internal use only. Not for public distribution.

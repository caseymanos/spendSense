# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SpendSense MVP V2 is an explainable, consent-aware financial behavior analysis system that:
- Processes synthetic Plaid-style transaction data
- Detects spending/savings patterns and assigns behavioral personas
- Provides educational recommendations with strict transparency guardrails
- Built on principles: transparency over sophistication, user control over automation, education over sales

**Current Status:** Project is in planning phase. Implementation follows a 10-PR roadmap documented in `docs/taskList.md`.

## Tech Stack

- **Environment Manager:** `uv` (modern Python environment management)
- **Language:** Python 3.11+
- **Frameworks:** `streamlit` (UI), `fastapi` (REST endpoints)
- **Data Tools:** `pandas`, `pyarrow`, `faker`, `numpy`
- **Storage:** SQLite (relational), Parquet (analytics), JSON (logs)
- **Testing:** `pytest` with deterministic seeding (`seed=42`)

## Essential Commands

### Environment Setup
```bash
# Initialize uv environment and install dependencies
uv sync

# Or with pip fallback
uv pip install -r requirements.txt
```

### Data Generation
```bash
# Generate synthetic dataset (50-100 users, 6 months transactions)
uv run python -m ingest.data_generator
```

### Testing
```bash
# Run full test suite
uv run pytest tests/ -v

# Run with coverage report
uv run pytest --cov=spendsense tests/

# Run specific test file
uv run pytest tests/test_data_generation.py -v
```

### User Interfaces
```bash
# Launch end-user educational dashboard
uv run streamlit run ui/app_user.py

# Launch operator/compliance dashboard
uv run streamlit run ui/app_operator.py
```

### Evaluation
```bash
# Run evaluation harness (generates metrics)
uv run python -m eval.run --input data/transactions.parquet --output eval/results.json
```

### Code Quality
```bash
# Lint code
uv run ruff check .

# Format code
uv run black .
```

## Architecture Overview

### Module Structure
```
ingest/         # Synthetic data generation, schema validation, data loading
features/       # Behavioral signal detection (subscriptions, savings, credit, income)
personas/       # Persona assignment logic with conflict-resolution priority
recommend/      # Rule-based recommendation engine with rationales
guardrails/     # Consent enforcement, eligibility filters, tone validation
ui/             # Streamlit apps (app_user.py, app_operator.py)
eval/           # Metrics harness (coverage, explainability, latency, fairness)
docs/           # Decision logs, schema docs, trace JSONs
tests/          # Unit and integration tests (target: 31+ tests)
data/           # SQLite DB, Parquet files, config JSON
```

### Data Flow Pipeline
1. **Ingestion:** Generate/validate synthetic Plaid data → SQLite + Parquet
2. **Feature Detection:** Extract behavioral signals (30d and 180d windows)
3. **Persona Assignment:** Apply priority rules to assign 1 of 5 personas
4. **Recommendation:** Generate 3-5 educational items + 1-3 partner offers
5. **Guardrails:** Enforce consent, eligibility, and tone checks
6. **Evaluation:** Compute coverage, explainability, latency, fairness metrics

### Persona Priority Order (Conflict Resolution)
1. High Utilization (credit strain)
2. Variable Income Budgeter (income instability)
3. Subscription Heavy (recurring spend optimization)
4. Savings Builder (positive reinforcement)
5. Custom Persona (reserved for future)

## Critical Design Constraints

### Consent Management
- All processing blocked if `consent_granted = FALSE`
- Users can opt-in/opt-out at any time
- Consent timestamps tracked in SQLite `users` table
- Revocation archives user data

### Recommendation Requirements
Every recommendation MUST include:
1. Clear "because" rationale citing actual user data (e.g., "Visa ending in 4523 at 68% utilization")
2. Plain-language educational focus (no financial advice)
3. Mandatory disclaimer: "This is educational content, not financial advice."

### Tone Validation
Prohibited phrases (shaming language):
- "overspending", "bad habits", "lack discipline"

Preferred alternatives:
- "consider reducing", "optimize your spending"

### Testing Philosophy
- All tests use deterministic data (`seed=42`)
- Unit tests verify component isolation
- Integration tests verify end-to-end flows
- Target: 100% coverage, explainability, auditability
- UI testing is manual for MVP

## Success Criteria (MVP Targets)

| Metric | Target |
|--------|--------|
| Coverage | 100% (users with persona + ≥3 behaviors) |
| Explainability | 100% (recommendations with rationale) |
| Latency | <5 seconds per user |
| Auditability | 100% (trace JSONs for all recommendations) |
| Fairness | ±10% demographic parity |
| Tests Passing | ≥10 (31 planned) |

## Development Workflow

### PR-Based Implementation
Follow the 10-PR roadmap in `docs/taskList.md`:
- PR #1: Project setup & data foundation
- PR #2: Behavioral signal detection
- PR #3: Persona assignment
- PR #4: Recommendation engine
- PR #5: Guardrails & consent
- PR #6: User interface
- PR #7: Operator dashboard
- PR #8: Evaluation harness
- PR #9: Testing & QA
- PR #10: Documentation & polish

### Before Each PR Merge
1. Run full test suite and ensure all tests pass
2. Verify deterministic output with `seed=42`
3. Update `docs/decision_log.md` with design choices
4. Generate trace JSONs for affected users

## Key Documentation Files

- `docs/SpendSense MVP V2.md` - Complete specification
- `docs/taskList.md` - 10-PR implementation plan with 31 tests
- `docs/schema.md` - Data model definitions
- `docs/decision_log.md` - Design choices and operator overrides
- `docs/limitations.md` - Known constraints and MVP trade-offs
- `docs/traces/{user_id}.json` - Per-user decision traces
- `docs/eval_summary.md` - Evaluation metrics and fairness results

## Important Notes

- **No real PII:** All data is synthetic via `faker`
- **Local-first:** No external APIs or cloud dependencies
- **Fairness-first:** Demographics used only for parity checks, not persona logic
- **Educational scope:** Never cross into regulated financial advice
- **Auditability:** Every recommendation must be traceable to source data

## Contact

- Project Lead: Casey Manos
- Technical Spec Origin: Bryce Harris (bharris@peak6.com)

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
- **Frontend:** Next.js 14 (React) user dashboard, NiceGUI operator dashboard
- **Backend:** FastAPI (REST API)
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
# Launch FastAPI backend (REQUIRED for all UIs)
uv run uvicorn api.main:app --reload
# → http://localhost:8000

# Launch Next.js user dashboard (RECOMMENDED)
cd web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
# → http://localhost:3000

# Launch NiceGUI operator dashboard (data generation & compliance)
uv run python ui/app_operator_nicegui.py
# → http://localhost:8081

# Legacy Streamlit dashboards (deprecated, reference only)
# uv run streamlit run ui/app_user.py
# uv run streamlit run ui/app_operator.py
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

### Fairness Framework (Production-Ready Compliance)

**Regulatory Context**: ECOA/Regulation B compliance to avoid disparate impact

**3-Tier Production Metrics**:
1. **Persona Distribution Parity** (Primary - ECOA compliance)
   - Detects if specific persona TYPES are assigned equitably across demographics
   - Example violation: 48% of females get "High Utilization" vs 27% overall
   - Tolerance: ±10% deviation from overall assignment rate for each persona
   - File: `eval/fairness.py::calculate_persona_distribution_parity()`

2. **Recommendation Quantity Parity** (Service Quality)
   - Ensures all demographic groups receive similar numbers of recommendations
   - Example violation: Females get 5.5 avg recs vs 5.0 overall (10.5% deviation)
   - Tolerance: ±10% deviation from overall mean
   - File: `eval/fairness.py::calculate_recommendation_quantity_parity()`

3. **Partner Offer Access Parity** (Opportunity Equity)
   - Prevents "redlining" where premium offers withheld from protected groups
   - Measures: % of users receiving partner offers by demographic
   - Tolerance: ±10% deviation from overall offer access rate
   - File: `eval/fairness.py::calculate_partner_offer_parity()`

**Key Principle**: Demographics NEVER used in persona assignment or recommendation logic. They are collected ONLY for retrospective fairness monitoring.

**Documentation**:
- Methodology: `docs/FAIRNESS_METHODOLOGY.md`
- Latest Report: `docs/fairness_report.md`
- Tests: `tests/test_fairness_production.py` (12 comprehensive tests)

**Running Fairness Checks**:
```bash
# Full evaluation with production fairness metrics
uv run python -m eval.run
# → Generates docs/fairness_report.md with violations

# Run fairness tests
uv run pytest tests/test_fairness_production.py -v
```

### Testing Philosophy
- All tests use deterministic data (`seed=42`)
- Unit tests verify component isolation
- Integration tests verify end-to-end flows
- **Fairness tests**: 12 tests covering all 3 production metrics + edge cases
- Target: 100% coverage, explainability, auditability, fairness compliance
- UI testing is manual for MVP

## Success Criteria (MVP Targets)

| Metric | Target | Status |
|--------|--------|--------|
| Coverage | 100% (users with persona + ≥3 behaviors) | ✅ 100% |
| Explainability | 100% (recommendations with rationale) | ✅ 100% |
| Latency | <5 seconds per user | ✅ 0.011s |
| Auditability | 100% (trace JSONs for all recommendations) | ✅ 100% |
| **Production Fairness** | **±10% parity (3 metrics)** | **⚠️ 5 violations** |
| Tests Passing | ≥31 tests | ✅ 43+ tests (12 fairness tests added) |

**Fairness Status Details**:
- ❌ Persona Distribution Parity: 3 violations
- ❌ Recommendation Quantity Parity: 2 violations
- ✅ Partner Offer Access Parity: PASS
- Note: Legacy fairness metric (100% assignment) kept for backwards compatibility

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
- use uv over python3

## MCP Agent Mail — coordination for multi-agent workflows

What it is
- A mail-like layer that lets coding agents coordinate asynchronously via MCP tools and resources.
- Provides identities, inbox/outbox, searchable threads, and advisory file reservations, with human-auditable artifacts in Git.

Why it's useful
- Prevents agents from stepping on each other with explicit file reservations (leases) for files/globs.
- Keeps communication out of your token budget by storing messages in a per-project archive.
- Offers quick reads (`resource://inbox/...`, `resource://thread/...`) and macros that bundle common flows.

How to use effectively
1) Same repository
   - Register an identity: call `ensure_project`, then `register_agent` using this repo's absolute path as `project_key`.
   - Reserve files before you edit: `file_reservation_paths(project_key, agent_name, ["src/**"], ttl_seconds=3600, exclusive=true)` to signal intent and avoid conflict.
   - Communicate with threads: use `send_message(..., thread_id="FEAT-123")`; check inbox with `fetch_inbox` and acknowledge with `acknowledge_message`.
   - Read fast: `resource://inbox/{Agent}?project=<abs-path>&limit=20` or `resource://thread/{id}?project=<abs-path>&include_bodies=true`.
   - Tip: set `AGENT_NAME` in your environment so the pre-commit guard can block commits that conflict with others' active exclusive file reservations.

2) Across different repos in one project (e.g., Next.js frontend + FastAPI backend)
   - Option A (single project bus): register both sides under the same `project_key` (shared key/path). Keep reservation patterns specific (e.g., `frontend/**` vs `backend/**`).
   - Option B (separate projects): each repo has its own `project_key`; use `macro_contact_handshake` or `request_contact`/`respond_contact` to link agents, then message directly. Keep a shared `thread_id` (e.g., ticket key) across repos for clean summaries/audits.

Macros vs granular tools
- Prefer macros when you want speed or are on a smaller model: `macro_start_session`, `macro_prepare_thread`, `macro_file_reservation_cycle`, `macro_contact_handshake`.
- Use granular tools when you need control: `register_agent`, `file_reservation_paths`, `send_message`, `fetch_inbox`, `acknowledge_message`.

Common pitfalls
- "from_agent not registered": always `register_agent` in the correct `project_key` first.
- "FILE_RESERVATION_CONFLICT": adjust patterns, wait for expiry, or use a non-exclusive reservation when appropriate.
- Auth errors: if JWT+JWKS is enabled, include a bearer token with a `kid` that matches server JWKS; static bearer is used only when JWT is disabled.
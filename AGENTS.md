# Repository Guidelines

## Project Structure & Module Organization
- `ingest/` synthetic data generation and validation; writes to `data/` (gitignored).
- `features/` behavioral signal extraction; `guardrails/` consent, eligibility, tone checks.
- `personas/` assignment logic; `recommend/` recommendation engine.
- `ui/` Streamlit apps (user and operator); `api/` FastAPI service.
- `eval/` metrics harness and reports; `docs/` schema, decisions, traces; `tests/` unit/integration.
- Alternative UI prototype in `ui_reflex/` (optional).

## Build, Test, and Development Commands
- Setup (Python 3.11+): `uv sync` (or `pip install -r requirements.txt`).
- Lint/format: `uv run ruff check .` and `uv run black .`.
- Run tests: `uv run pytest -v` or with coverage `uv run pytest --cov=spendsense`.
- Generate sample data: `uv run python -m ingest.data_generator`.
- Start UI (user): `uv run streamlit run ui/app_user.py`.
- Start UI (operator): `uv run streamlit run ui/app_operator.py`.
- Start API: `uv run uvicorn api.main:app --reload`.
- Evaluate: `uv run python -m eval.run --input data/transactions.parquet --output eval/results.json`.

## Coding Style & Naming Conventions
- Python: 4-space indents, type hints where practical, docstrings for public APIs.
- Formatting: Black (line length 100). Linting: Ruff (target Python 3.11).
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Keep functions small, pure when possible; prefer explicit over implicit.

## Testing Guidelines
- Framework: pytest (see `pyproject.toml`). Tests live in `tests/` as `test_*.py`.
- Use fixtures (see `tests/conftest.py`) and deterministic seeds for data generation.
- Add tests for new behavior and edge cases; include coverage where feasible.
- Quick examples: `uv run pytest tests/test_features.py -v` or `-k keyword` to filter.

## Commit & Pull Request Guidelines
- Commits: present tense, concise; one logical change per commit. Prefer scoped subjects (e.g., `api: add health check`).
- PRs: clear description, linked issues, screenshots for UI changes, CLI output for APIs, and a brief test plan. Update docs (`docs/`, `README.md`) when behavior changes.

## Security & Configuration Tips
- Do not commit secrets or personal data. `data/` is gitignored by default.
- CORS in `api/` is permissive for local dev—tighten for production.
- Avoid committing generated artifacts in `eval/` and `.nicegui/`.

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
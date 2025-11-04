# SpendSense MVP V2 - Updated Task List with Strategic Testing

## PR #1: Project Setup & Data Foundation

**Goal:** Initialize project structure, environment, and synthetic data generation

### Tasks:
- [ ] **Initialize repository structure**
  - Files: `.gitignore`, `README.md`, `pyproject.toml`
  - Create all folders: `ingest/`, `features/`, `personas/`, `recommend/`, `guardrails/`, `ui/`, `eval/`, `tests/`, `docs/`, `data/`

- [ ] **Configure uv environment**
  - Files: `pyproject.toml`, `requirements.txt`
  - Dependencies: `pandas`, `numpy`, `pyarrow`, `faker`, `streamlit`, `fastapi`, `pytest`, `ruff`, `black`

- [ ] **Create data schemas (Plaid-compatible)**
  - Files: `ingest/schemas.py`
  - Define Pydantic models for: Accounts, Transactions, Liabilities, Users

- [ ] **Build synthetic data generator**
  - Files: `ingest/data_generator.py`
  - Generate 50-100 users with 6 months of transactions
  - Include demographic fields (age, gender, income_tier, region)
  - Use `seed=42` for deterministic output

- [ ] **Implement data validators**
  - Files: `ingest/validators.py`
  - Validate schema compliance
  - Check plausible value ranges
  - Generate validation report

- [ ] **Create data loader**
  - Files: `ingest/loader.py`
  - Load CSV/JSON to SQLite
  - Export to Parquet for analytics
  - Create `data/users.sqlite`, `data/transactions.parquet`, `data/config.json`

- [ ] **Initialize consent tracking**
  - Files: `ingest/schemas.py`, `ingest/loader.py`
  - Add users table with consent fields
  - SQL schema: `user_id`, `name`, `consent_granted`, `consent_timestamp`, `revoked_timestamp`

- [ ] **Create initial documentation**
  - Files: `docs/README.md`, `docs/schema.md`, `docs/decision_log.md`, `docs/limitations.md`
  - Document data model
  - Log design decisions

- [ ] **✅ UNIT TEST: Schema validation**
  - Files: `tests/test_data_generation.py`
  - **Test:** Validate that Pydantic models enforce required fields and data types
  - **Verify:** Invalid data raises ValidationError
  - **Expected:** All required fields must be present, types must match schema

- [ ] **✅ UNIT TEST: Deterministic generation**
  - Files: `tests/test_data_generation.py`
  - **Test:** Run data generator with `seed=42` twice and compare outputs
  - **Verify:** Identical user_ids, transaction amounts, and dates generated
  - **Expected:** SHA-256 hash of both outputs matches exactly

- [ ] **✅ INTEGRATION TEST: End-to-end data pipeline**
  - Files: `tests/test_data_generation.py`
  - **Test:** Generate data → Validate → Load to SQLite → Export to Parquet
  - **Verify:** 
    - 50-100 users created
    - Each user has transactions spanning 6 months
    - SQLite and Parquet files exist and are readable
    - Consent table initialized with default `consent_granted=False`
  - **Expected:** Pipeline completes without errors, all files present in `data/`

---

## PR #2: Behavioral Signal Detection

**Goal:** Extract financial behavior signals from transaction data

### Tasks:
- [ ] **Implement subscription detection**
  - Files: `features/subscriptions.py`
  - Detect recurring merchants (≥3 in 90 days)
  - Calculate monthly recurring spend
  - Compute subscription share of total spend
  - Output metrics for 30-day and 180-day windows

- [ ] **Implement savings signal detection**
  - Files: `features/savings.py`
  - Calculate net inflow to savings accounts
  - Compute growth rate percentage
  - Calculate emergency fund coverage = savings / avg monthly expenses

- [ ] **Implement credit signal detection**
  - Files: `features/credit.py`
  - Calculate utilization = balance / limit per card
  - Flag utilization levels (30%, 50%, 80%)
  - Detect minimum-payment-only pattern
  - Identify interest charges and overdue status

- [ ] **Implement income stability detection**
  - Files: `features/income.py`
  - Detect payroll ACH transactions
  - Calculate median pay gap and payment frequency
  - Compute income variability (std-dev)
  - Calculate cash-flow buffer in months

- [ ] **Create feature pipeline orchestrator**
  - Files: `features/__init__.py`
  - Coordinate all signal detection modules
  - Output consolidated `features/signals.parquet`
  - Generate per-user trace logs in `docs/traces/{user_id}.json`

- [ ] **✅ UNIT TEST: Subscription detection logic**
  - Files: `tests/test_features.py`
  - **Test:** Create mock transaction data with known recurring pattern (Netflix, $15.99, monthly for 4 months)
  - **Verify:** Detector identifies it as recurring, calculates correct monthly spend
  - **Expected:** `recurring_count=1`, `monthly_recurring_spend=$15.99`, detected within 30d window

- [ ] **✅ UNIT TEST: Credit utilization calculation**
  - Files: `tests/test_features.py`
  - **Test:** Mock credit card with `balance=$3,400`, `limit=$5,000`
  - **Verify:** Utilization calculated as 68%
  - **Expected:** Flags triggered for 50% and 30% thresholds, not 80%

- [ ] **✅ UNIT TEST: Emergency fund coverage**
  - Files: `tests/test_features.py`
  - **Test:** Mock user with `savings_balance=$6,000`, `avg_monthly_expenses=$2,000`
  - **Verify:** Coverage = 3.0 months
  - **Expected:** Exact calculation matches formula

- [ ] **✅ UNIT TEST: Edge case - No transactions**
  - Files: `tests/test_features.py`
  - **Test:** User with zero transactions in window
  - **Verify:** All signals return null/zero values without errors
  - **Expected:** No crashes, graceful handling with logged warning

- [ ] **✅ INTEGRATION TEST: Full feature pipeline**
  - Files: `tests/test_features.py`
  - **Test:** Run all 4 signal detectors on synthetic dataset
  - **Verify:** 
    - `signals.parquet` generated with all columns
    - All 50-100 users have signal data for 30d and 180d windows
    - Trace JSONs created in `docs/traces/`
  - **Expected:** No exceptions, all users processed, output files valid

---

## PR #3: Persona Assignment System

**Goal:** Classify users into personas based on behavioral signals

### Tasks:
- [ ] **Define persona criteria**
  - Files: `personas/assignment.py`
  - Implement 4 required personas:
    - High Utilization (utilization ≥50% OR interest > 0 OR min-payment-only OR overdue)
    - Variable Income Budgeter (median pay gap > 45 days AND buffer < 1 month)
    - Subscription Heavy (recurring ≥3 AND spend ≥$50 OR ≥10%)
    - Savings Builder (growth ≥2% OR inflow ≥$200 AND utilization < 30%)

- [ ] **Implement persona priority logic**
  - Files: `personas/assignment.py`
  - Priority order: High Utilization → Variable Income → Subscription Heavy → Savings Builder → Custom
  - Handle multi-persona matches
  - Return single primary persona per user

- [ ] **Create persona assignment storage**
  - Files: `personas/assignment.py`
  - SQLite table: `persona_assignments` with fields: `user_id`, `persona`, `criteria_met`, `timestamp`
  - Generate decision trace JSON per user

- [ ] **Document custom persona slot**
  - Files: `docs/decision_log.md`
  - Reserve Persona 5 for post-MVP customization
  - Document extensibility pattern

- [ ] **✅ UNIT TEST: High Utilization persona criteria**
  - Files: `tests/test_personas.py`
  - **Test:** Mock signal data with `utilization=68%`, `interest=$87`
  - **Verify:** Assigned to "high_utilization" persona
  - **Expected:** Criteria_met includes both flags

- [ ] **✅ UNIT TEST: Variable Income persona criteria**
  - Files: `tests/test_personas.py`
  - **Test:** Mock signal data with `median_pay_gap=50 days`, `cash_buffer=0.8 months`
  - **Verify:** Assigned to "variable_income" persona
  - **Expected:** Both conditions satisfied

- [ ] **✅ UNIT TEST: Persona priority ordering**
  - Files: `tests/test_personas.py`
  - **Test:** Mock user matching BOTH High Utilization AND Savings Builder criteria
  - **Verify:** Assigned to "high_utilization" (higher priority)
  - **Expected:** Only one persona assigned, follows priority rules

- [ ] **✅ UNIT TEST: Edge case - No persona match**
  - Files: `tests/test_personas.py`
  - **Test:** Mock user with no signals meeting any persona threshold
  - **Verify:** Returns `None` or default persona gracefully
  - **Expected:** No crash, logged for manual review

- [ ] **✅ INTEGRATION TEST: Full persona assignment**
  - Files: `tests/test_personas.py`
  - **Test:** Assign personas to all synthetic users from PR #2
  - **Verify:** 
    - 100% of users with ≥3 behaviors have assigned persona
    - `persona_assignments` table populated in SQLite
    - Trace JSONs updated with persona logic
  - **Expected:** Coverage metric = 100%, all assignments traceable

---

## PR #4: Recommendation Engine

**Goal:** Generate personalized educational content and partner offers

### Tasks:
- [ ] **Create content catalog**
  - Files: `recommend/content_catalog.py`
  - Define 3-5 education items per persona
  - Define 1-3 partner offers per persona
  - Map personas to content types

- [ ] **Build recommendation engine**
  - Files: `recommend/engine.py`
  - Generate recommendations based on persona
  - Create plain-language rationales using actual data values
  - Format: "We noticed your Visa ending in 4523 is at 68% utilization..."

- [ ] **Implement eligibility filtering**
  - Files: `recommend/engine.py`
  - Check minimum income/credit requirements
  - Exclude products user already has
  - Filter based on account types

- [ ] **Add mandatory disclaimer**
  - Files: `recommend/engine.py`
  - Append to every recommendation: "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."

- [ ] **Create recommendation output format**
  - Files: `recommend/engine.py`
  - JSON structure with: `user_id`, `persona`, `recommendations[]`
  - Each recommendation: `type`, `title`, `rationale`, `disclaimer`

- [ ] **✅ UNIT TEST: Rationale includes concrete data**
  - Files: `tests/test_recommendations.py`
  - **Test:** Generate recommendation for High Utilization user with known card data
  - **Verify:** Rationale includes "Visa ending in 4523", "68%", "$3,400 of $5,000"
  - **Expected:** All numeric values match source data exactly

- [ ] **✅ UNIT TEST: Disclaimer present on all recommendations**
  - Files: `tests/test_recommendations.py`
  - **Test:** Generate recommendations for all 4 personas
  - **Verify:** Every recommendation includes exact disclaimer text
  - **Expected:** 100% of recommendations have disclaimer

- [ ] **✅ UNIT TEST: Recommendation count per persona**
  - Files: `tests/test_recommendations.py`
  - **Test:** Generate recommendations for each persona
  - **Verify:** 3-5 education items and 1-3 offers returned
  - **Expected:** Counts within specified ranges for all personas

- [ ] **✅ UNIT TEST: Eligibility filtering**
  - Files: `tests/test_recommendations.py`
  - **Test:** User with existing high-yield savings account
  - **Verify:** HYSA offer excluded from recommendations
  - **Expected:** Offer not present in output

- [ ] **✅ INTEGRATION TEST: Full recommendation generation**
  - Files: `tests/test_recommendations.py`
  - **Test:** Generate recommendations for all synthetic users
  - **Verify:**
    - All users have 3-5 education items
    - All users have 1-3 eligible offers
    - All recommendations have rationales
    - No ineligible offers present
  - **Expected:** 100% explainability metric, no eligibility violations

---

## PR #5: Guardrails & Consent Management

**Goal:** Implement consent, eligibility, and tone validation

### Tasks:
- [ ] **Implement consent enforcement**
  - Files: `guardrails/consent.py`
  - Check `consent_granted` before any processing
  - Implement opt-in/opt-out flows
  - Track consent timestamps
  - Block recommendations for users without consent

- [ ] **Build tone validation**
  - Files: `guardrails/tone.py`
  - Regex-based detection of judgmental phrases
  - Banned phrases: "overspending", "bad habits", "lack discipline"
  - Replacement suggestions: "consider lowering" vs "you overspent"
  - Flag recommendations for manual review if issues detected

- [ ] **Implement eligibility guardrails**
  - Files: `guardrails/eligibility.py`
  - Verify income minimums for offers
  - Check existing account holdings
  - Exclude predatory products (payday loans, etc.)
  - Document exclusion logic

- [ ] **Create guardrails orchestrator**
  - Files: `guardrails/__init__.py`
  - Run all checks before finalizing recommendations
  - Log guardrail decisions to trace files

- [ ] **✅ UNIT TEST: Consent blocking**
  - Files: `tests/test_guardrails.py`
  - **Test:** Attempt to generate recommendations for user with `consent_granted=False`
  - **Verify:** Processing blocked, exception raised or None returned
  - **Expected:** No recommendations generated, clear error message logged

- [ ] **✅ UNIT TEST: Consent revocation**
  - Files: `tests/test_guardrails.py`
  - **Test:** User opts in, then revokes consent
  - **Verify:** 
    - `consent_granted` changes to False
    - `revoked_timestamp` populated
    - Future processing blocked
  - **Expected:** State persists in SQLite, audit trail complete

- [ ] **✅ UNIT TEST: Tone validation - Detect violations**
  - Files: `tests/test_guardrails.py`
  - **Test:** Pass recommendation text containing "you're overspending" and "bad habits"
  - **Verify:** Tone validator flags both phrases
  - **Expected:** Returns list of violations with line numbers

- [ ] **✅ UNIT TEST: Tone validation - Clean text passes**
  - Files: `tests/test_guardrails.py`
  - **Test:** Pass recommendation text with "consider reducing" and "optimize your spending"
  - **Verify:** No violations detected
  - **Expected:** Returns empty list, text approved

- [ ] **✅ UNIT TEST: Eligibility check - Predatory product blocked**
  - Files: `tests/test_guardrails.py`
  - **Test:** Attempt to recommend payday loan offer
  - **Verify:** Offer blocked by guardrail
  - **Expected:** Excluded from final recommendations, logged as blocked

- [ ] **✅ INTEGRATION TEST: Full guardrail pipeline**
  - Files: `tests/test_guardrails.py`
  - **Test:** Run all guardrails on full recommendation set from PR #4
  - **Verify:**
    - Users without consent have zero recommendations
    - All recommendations pass tone validation
    - All offers pass eligibility checks
    - Trace logs include guardrail decisions
  - **Expected:** No violations in final output, 100% compliance

---

## PR #6: User Interface (Streamlit App)

**Goal:** Build end-user educational dashboard

### Tasks:
- [ ] **Create consent onboarding screen**
  - Files: `ui/app_user.py`
  - Display consent request on first load
  - Checkbox for opt-in
  - Store consent in SQLite

- [ ] **Build personal dashboard**
  - Files: `ui/app_user.py`
  - Display active persona
  - Show detected behavioral patterns
  - Render 3-5 education cards with rationales
  - Display 1-3 partner offers

- [ ] **Create learning feed view**
  - Files: `ui/app_user.py`
  - Display articles, tips, calculators
  - Filter by persona-relevant content

- [ ] **Build privacy settings page**
  - Files: `ui/app_user.py`
  - View current consent status
  - Revoke consent button
  - Data export option (future)

- [ ] **Add styling and UX polish**
  - Files: `ui/app_user.py`
  - Educational and supportive theme
  - Clear navigation
  - Mobile-friendly layout (Streamlit native)

**Note:** UI testing is manual/visual for MVP. No automated tests required for this PR.

---

## PR #7: Operator Dashboard (Streamlit App)

**Goal:** Build compliance and oversight interface

### Tasks:
- [ ] **Create user management tab**
  - Files: `ui/app_operator.py`
  - Filter users by consent status
  - Filter by persona
  - Filter by demographic segment

- [ ] **Build signals visualization tab**
  - Files: `ui/app_operator.py`
  - Display 30-day and 180-day metrics
  - Charts for subscriptions, savings, credit, income
  - Per-user drill-down

- [ ] **Create persona distribution view**
  - Files: `ui/app_operator.py`
  - Show persona assignment counts
  - Display criteria breakdown
  - Highlight multi-persona users

- [ ] **Build recommendation review tab**
  - Files: `ui/app_operator.py`
  - List pending recommendations
  - Show rationales and decision traces
  - Approve/override/flag actions
  - Log overrides to `docs/decision_log.md`

- [ ] **Create decision trace viewer**
  - Files: `ui/app_operator.py`
  - Load and display `docs/traces/{user_id}.json`
  - Show full signal → persona → recommendation pipeline

- [ ] **Add evaluation summary tab**
  - Files: `ui/app_operator.py`
  - Display metrics from `eval/results.json`
  - Show coverage, explainability, latency, fairness

**Note:** UI testing is manual/visual for MVP. No automated tests required for this PR.

---

## PR #8: Evaluation Harness

**Goal:** Measure system performance and fairness

### Tasks:
- [ ] **Implement coverage metric**
  - Files: `eval/run.py`
  - Calculate % of users with ≥3 behaviors and ≥1 persona
  - Target: 100%

- [ ] **Implement explainability metric**
  - Files: `eval/run.py`
  - Calculate % of recommendations with rationales
  - Target: 100%

- [ ] **Implement relevance scoring**
  - Files: `eval/run.py`
  - Rule-based scoring of persona → education alignment
  - Target: ≥90%

- [ ] **Implement latency measurement**
  - Files: `eval/run.py`
  - Measure time per user with `time.perf_counter()`
  - Target: <5 seconds per user

- [ ] **Implement fairness metric**
  - Files: `eval/run.py`
  - Compute demographic parity across age, gender, income_tier, region
  - Target: ±10% of mean distribution

- [ ] **Implement auditability check**
  - Files: `eval/run.py`
  - Verify 100% of recommendations have trace JSONs

- [ ] **Generate evaluation outputs**
  - Files: `eval/run.py`
  - Output: `eval/results.json`, `eval/results.csv`, `eval/summary.md`
  - Append timestamp for longitudinal tracking

- [ ] **Create fairness report**
  - Files: `eval/run.py`
  - Generate `docs/fairness_report.md`
  - Visualize demographic distribution across personas

- [ ] **✅ UNIT TEST: Coverage metric calculation**
  - Files: `tests/test_eval.py`
  - **Test:** Mock dataset with known persona/behavior counts
  - **Verify:** Coverage = (users_with_persona_and_3behaviors / total_users) * 100
  - **Expected:** Exact percentage matches hand calculation

- [ ] **✅ UNIT TEST: Explainability metric calculation**
  - Files: `tests/test_eval.py`
  - **Test:** Mock recommendations, some with rationales, some without
  - **Verify:** Explainability = (recs_with_rationale / total_recs) * 100
  - **Expected:** Correct percentage calculated

- [ ] **✅ UNIT TEST: Latency measurement accuracy**
  - Files: `tests/test_eval.py`
  - **Test:** Run evaluation on single user, measure time
  - **Verify:** Latency captured in milliseconds/seconds
  - **Expected:** Reasonable time recorded (0.1-2 seconds for single user)

- [ ] **✅ UNIT TEST: Fairness parity calculation**
  - Files: `tests/test_eval.py`
  - **Test:** Mock demographics with known distribution skew
  - **Verify:** Parity metric flags deviations >±10%
  - **Expected:** Correctly identifies demographic imbalances

- [ ] **✅ INTEGRATION TEST: Full evaluation run**
  - Files: `tests/test_eval.py`
  - **Test:** Run evaluation harness on complete synthetic dataset
  - **Verify:**
    - All metrics computed (coverage, explainability, latency, fairness, auditability)
    - Output files generated (`results.json`, `results.csv`, `summary.md`)
    - All values within expected ranges or flagged
  - **Expected:** Clean execution, all targets met, files valid JSON/CSV/Markdown

---

## PR #9: Testing & Quality Assurance

**Goal:** Achieve ≥10 passing tests with full coverage

### Tasks:
- [ ] **Consolidate and verify all tests from previous PRs**
  - Files: All `tests/*.py` files
  - Ensure all unit and integration tests from PR #1-8 are present and passing

- [ ] **Run full test suite**
  - Command: `uv run pytest tests/ -v`
  - Generate `docs/test_results.md`
  - Verify ≥10 passing tests

- [ ] **✅ Count verification: Minimum 10 tests**
  - **Verify:** 
    - PR #1: 3 tests
    - PR #2: 5 tests
    - PR #3: 5 tests
    - PR #4: 5 tests
    - PR #5: 6 tests
    - PR #8: 5 tests
    - **TOTAL: 29 tests** ✅ (exceeds minimum of 10)

- [ ] **Generate test coverage report**
  - Command: `uv run pytest --cov=spendsense tests/`
  - Files: Coverage report in terminal and `htmlcov/`
  - Target: ≥80% coverage on core modules

- [ ] **✅ INTEGRATION TEST: End-to-end system verification**
  - Files: `tests/test_integration_full_pipeline.py` (new)
  - **Test:** Run complete pipeline from data generation through evaluation
  - **Verify:**
    1. Generate synthetic data
    2. Detect behavioral signals
    3. Assign personas
    4. Generate recommendations
    5. Apply guardrails
    6. Run evaluation
    7. All success criteria met
  - **Expected:** 
    - Coverage = 100%
    - Explainability = 100%
    - Latency < 5s per user
    - Auditability = 100%
    - All files generated correctly

- [ ] **Add CI/CD configuration (optional but recommended)**
  - Files: `.github/workflows/tests.yml`
  - Automate testing on push to main
  - Run on PR creation

---

## PR #10: Documentation & Final Polish

**Goal:** Complete all documentation and prepare for submission

### Tasks:
- [ ] **Finalize schema documentation**
  - Files: `docs/schema.md`
  - Document all Plaid-compatible fields
  - Provide examples for each table

- [ ] **Complete decision log**
  - Files: `docs/decision_log.md`
  - Document all design choices
  - Log operator overrides (if any)
  - Explain persona prioritization logic

- [ ] **Document limitations**
  - Files: `docs/limitations.md`
  - Synthetic-only dataset
  - No real Plaid API
  - Local-only runtime
  - No authentication
  - No feedback loop

- [ ] **Finalize evaluation summary**
  - Files: `docs/eval_summary.md`
  - Link to `eval/results.json`
  - Summarize key findings

- [ ] **Create comprehensive README**
  - Files: `README.md`
  - Setup instructions with uv
  - How to run data generation
  - How to launch user app
  - How to launch operator dashboard
  - How to run evaluation
  - Compliance disclaimer

- [ ] **Add success criteria checklist**
  - Files: `docs/README.md`
  - Coverage: 100%
  - Explainability: 100%
  - Latency: <5s
  - Auditability: 100%
  - Tests: ≥10
  - Documentation: Complete

- [ ] **Generate demo data and run full pipeline**
  - Command: `uv run python -m ingest.data_generator`
  - Command: `uv run python -m eval.run`
  - Verify all outputs present

- [ ] **Create demo video or screenshots**
  - Files: `docs/demo/` (screenshots or video)
  - Show user app
  - Show operator dashboard
  - Show evaluation metrics

- [ ] **Final code quality pass**
  - Run: `uv run ruff check .`
  - Run: `uv run black .`
  - Fix any linting issues

- [ ] **✅ VERIFICATION TEST: Documentation completeness**
  - Files: `tests/test_documentation.py` (new)
  - **Test:** Check all required documentation files exist
  - **Verify:**
    - `docs/schema.md` exists and non-empty
    - `docs/decision_log.md` exists and non-empty
    - `docs/limitations.md` exists and non-empty
    - `docs/eval_summary.md` exists and non-empty
    - `docs/test_results.md` exists and non-empty
    - `docs/fairness_report.md` exists and non-empty
    - `README.md` contains setup instructions
  - **Expected:** All files present and contain required sections

- [ ] **✅ VERIFICATION TEST: Output file validation**
  - Files: `tests/test_documentation.py`
  - **Test:** Verify all expected output files exist
  - **Verify:**
    - `data/users.sqlite` exists and has user table
    - `data/transactions.parquet` exists and readable
    - `features/signals.parquet` exists
    - `eval/results.json` exists and valid JSON
    - `eval/results.csv` exists and readable
    - At least 1 trace JSON in `docs/traces/`
  - **Expected:** All files present and properly formatted

---

## Summary of Testing Strategy

### Total Test Count: **31 Tests Minimum**

| PR | Unit Tests | Integration Tests | Total |
|----|------------|------------------|-------|
| PR #1 | 2 | 1 | 3 |
| PR #2 | 4 | 1 | 5 |
| PR #3 | 4 | 1 | 5 |
| PR #4 | 4 | 1 | 5 |
| PR #5 | 5 | 1 | 6 |
| PR #6 | 0 | 0 | 0 (manual UI testing) |
| PR #7 | 0 | 0 | 0 (manual UI testing) |
| PR #8 | 4 | 1 | 5 |
| PR #9 | 0 | 1 | 1 (full system verification) |
| PR #10 | 2 | 0 | 2 (documentation validation) |
| **TOTAL** | **25** | **7** | **32** ✅ |

### Testing Philosophy:
- **Unit tests** verify individual components work correctly in isolation
- **Integration tests** verify components work together end-to-end
- Tests serve as **verification gates** before merging each PR
- All tests use deterministic data (`seed=42`) for reproducibility
- Tests should fail fast and provide clear error messages
- UI testing remains manual for MVP (Streamlit apps are visual)
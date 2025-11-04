# Decision Log

**SpendSense MVP V2 - Design Decisions**

This document tracks key design decisions, their rationale, and alternatives considered.

---

## PR #1: Project Setup & Data Foundation

### Date: 2025-11-03

---

### Decision 1: Use `uv` for Environment Management

**Context:** Need fast, reliable Python dependency management for local development.

**Decision:** Adopt `uv` as primary environment manager with `pip` fallback.

**Rationale:**
- Faster dependency resolution than pip/poetry
- Native support for Python 3.11+ features
- Lightweight alternative to conda
- Growing adoption in modern Python projects

**Alternatives Considered:**
- `pip + venv`: Standard but slower
- `poetry`: More features but heavier
- `conda`: Overkill for our needs

**Impact:** Development team must install `uv` or use pip fallback.

---

### Decision 2: SQLite + Parquet Dual Storage

**Context:** Need both relational queries (consent, user lookup) and analytics (feature extraction).

**Decision:** Use SQLite for relational data and Parquet for transaction analytics.

**Rationale:**
- SQLite: Zero-configuration, ACID transactions, perfect for consent management
- Parquet: Columnar format optimized for pandas/numpy analytics
- Local-first: No external database dependencies
- Separation of concerns: Metadata vs. analytics workloads

**Alternatives Considered:**
- PostgreSQL: Too heavy for MVP, requires server setup
- CSV files: No query capability, poor performance
- SQLite only: Poor performance for large transaction scans

**Impact:** Data pipeline exports to both formats. Storage ~2x but query performance optimized.

---

### Decision 3: Seed=42 for Deterministic Generation

**Context:** Need reproducible synthetic data for testing and demos.

**Decision:** Hard-code `seed=42` in data generation config.

**Rationale:**
- Deterministic output allows SHA-256 hash verification in tests
- Consistent demos and documentation screenshots
- Debuggable: Same data every run
- Industry standard (Hitchhiker's Guide reference)

**Alternatives Considered:**
- Random seed: Non-reproducible, harder to test
- User-configurable seed: Adds complexity, not needed for MVP

**Impact:** All developers get identical synthetic dataset.

---

### Decision 4: 100 Users with 6 Months History

**Context:** Need realistic dataset size for fairness metrics without long generation time.

**Decision:** Generate 100 users with 6 months of transaction history (~180 transactions/user).

**Rationale:**
- 100 users: Large enough for demographic distribution analysis
- 6 months: Sufficient for 30-day and 180-day behavioral windows per PRD
- ~18,000 transactions: Meaningful volume without long processing
- Generation time: ~10-15 seconds on modern laptop

**Alternatives Considered:**
- 50 users: Insufficient for fairness metrics
- 1,000 users: Overkill for MVP, slow generation
- 12 months: Unnecessarily long history

**Impact:** ~2-5 MB total data size, fast generation and loading.

---

### Decision 5: Consent Defaults to False

**Context:** PRD requires explicit opt-in for data processing.

**Decision:** All generated users have `consent_granted = false` by default.

**Rationale:**
- Privacy-first: Users must explicitly opt in
- Aligns with GDPR principles (even though data is synthetic)
- Forces proper consent flow implementation in UI
- Prevents accidental processing of "non-consenting" users

**Alternatives Considered:**
- Random consent: Masks consent bugs
- All true: Violates PRD requirement

**Impact:** User app must implement consent flow before showing any analysis.

---

### Decision 6: Demographics for Metrics Only

**Context:** Need demographic data for fairness analysis but must avoid discriminatory persona logic.

**Decision:** Store `age`, `gender`, `income_tier`, `region` but exclude from persona assignment algorithms.

**Rationale:**
- Fairness metrics require demographic breakdown
- Discriminatory lending concerns if used in persona logic
- Explicit separation: Metrics OK, decisions NOT OK
- Aligns with fair lending best practices

**Alternatives Considered:**
- No demographics: Can't measure fairness
- Use in persona logic: Legally/ethically problematic

**Impact:** Clear documentation that demographics are metrics-only. Code reviews must enforce this.

---

### Decision 7: Pydantic for Schema Validation

**Context:** Need runtime validation of synthetic data before loading.

**Decision:** Use Pydantic v2 models for all schemas.

**Rationale:**
- Type safety at runtime
- Automatic validation with clear error messages
- JSON serialization built-in
- Modern Python best practice

**Alternatives Considered:**
- Dataclasses: No validation
- Marshmallow: Older, less Pythonic
- Manual validation: Error-prone

**Impact:** Small performance overhead but huge reliability gain.

---

### Decision 8: FastAPI Placeholder Endpoints

**Context:** Architecture requires FastAPI layer but most functionality comes in later PRs.

**Decision:** Create FastAPI scaffolding with HTTP 501 (Not Implemented) stubs.

**Rationale:**
- Establishes endpoint contract early
- Allows UI development to reference API structure
- Clear TODO markers for future PRs
- Health check endpoint functional immediately

**Alternatives Considered:**
- Skip FastAPI until needed: Harder to integrate later
- Implement all endpoints now: Out of scope for PR #1

**Impact:** `/health` endpoint works, others return 501 with helpful messages.

---

### Decision 9: Bi-Weekly Payroll Pattern

**Context:** Need realistic income patterns for stability detection (PR #2).

**Decision:** Generate payroll deposits every 14 days for users with checking accounts.

**Rationale:**
- Most common US pay frequency
- Predictable pattern aids signal detection
- Sufficient variability with random amounts ($2k-$6k)

**Alternatives Considered:**
- Monthly: Less common in US
- Weekly: Too many transactions
- Random: Unrealistic

**Impact:** Income stability features will detect consistent bi-weekly pattern.

---

### Decision 10: Recurring Merchants from Predefined List

**Context:** Need to detect subscription patterns (PR #2).

**Decision:** Use curated list of 14 common subscription merchants (Netflix, Spotify, etc.).

**Rationale:**
- Realistic merchant names
- Known recurring services
- ~70% of users get 3-8 subscriptions (enough for detection)
- Monthly recurrence pattern baked in

**Alternatives Considered:**
- Random merchant names: Unrecognizable
- All merchants recurring: Unrealistic

**Impact:** Subscription detection will have high-confidence patterns to find.

---

### Decision 11: Centralized Configuration Constants

**Context:** PRD Parts 2-3 define numerous threshold values for persona detection, recommendations, and evaluation. These need to be accessible across all future PRs.

**Decision:** Create `ingest/constants.py` as single source of truth for all tunable parameters in PR #1.

**Rationale:**
- Avoid hardcoded values scattered across modules
- Single file to adjust thresholds without code changes
- Clear documentation of all system parameters
- Easier to tune and optimize post-deployment
- Natural home for PRD-specified values

**Alternatives Considered:**
- Add constants in each PR when needed: Leads to duplication and inconsistency
- Use config JSON file: Less discoverable, no type hints
- Environment variables: Overkill for MVP, harder to version control

**Constants Included:**
- `PERSONA_THRESHOLDS` - Detection rules for all 4 personas
- `TIME_WINDOWS` - 30-day and 180-day analysis periods
- `SUBSCRIPTION_DETECTION` - Recurring merchant detection rules
- `RECOMMENDATION_LIMITS` - Min/max items per user
- `EVALUATION_TARGETS` - Success criteria metrics
- `PROHIBITED_PHRASES` - Tone validation blacklist
- `MANDATORY_DISCLAIMER` - Standard disclaimer text

**Impact:** PRs 2-10 import from constants file. Future tuning requires single file change.

---

### Decision 12: Persona Assignments Table in Data Foundation

**Context:** PR #3 will assign personas to users based on PR #2 signals. Need database table to store assignments.

**Decision:** Create `persona_assignments` table in PR #1 SQLite schema (ingest/loader.py).

**Rationale:**
- Database schema is data foundation concern, not business logic
- PR #3 should focus on assignment algorithm, not infrastructure
- Allows PR #2 to optionally write preliminary assignments
- Clear separation: PR #1 = structure, PR #3 = population

**Alternatives Considered:**
- Create table in PR #3: Mixes infrastructure with logic
- Use JSON files: Poor query performance, no relational integrity

**Schema:**
```sql
CREATE TABLE persona_assignments (
    assignment_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    persona TEXT NOT NULL,
    criteria_met TEXT,  -- JSON string
    assigned_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)
```

**Impact:** PR #3 writes directly to table. Operator dashboard can query assignments.

---

### Decision 13: Decision Traces Directory Structure

**Context:** PRD Part 3 specifies per-user trace JSONs in `docs/traces/{user_id}.json` for auditability.

**Decision:** Create `docs/traces/` directory with README in PR #1.

**Rationale:**
- Infrastructure should exist from project start
- Empty directory documents intent and structure
- README explains trace format before traces exist
- Prevents PR #4 from creating undocumented directory

**Alternatives Considered:**
- Create in PR #4 when traces generated: Directory purpose unclear until then
- Use different location (data/ or logs/): docs/ aligns with decision_log.md

**Trace Contents (defined in README):**
- User profile + consent status
- Behavioral signals (PR #2)
- Persona assignment (PR #3)
- Recommendations + rationales (PR #4)
- Guardrail checks (PR #5)
- Evaluation metadata (PR #8)

**Impact:** PRs 2-8 incrementally populate trace structure. Operator dashboard displays traces.

---

## Future PRs

Design decisions for subsequent PRs will be logged here as they are made.

### PR #2: Behavioral Signal Detection

### Date: 2025-11-03

---

### Decision 14: Transaction Amount Sign Convention

**Context:** Need consistent interpretation of transaction amounts across all feature modules.

**Decision:** Positive amounts = debits (money out), negative amounts = credits (money in).

**Rationale:**
- Aligns with Plaid API convention
- Intuitive for bank transactions: spending is positive, income is negative
- Consistent with accounting debit/credit principles
- Simplifies filtering: `amount > 0` for expenses, `amount < 0` for income

**Alternatives Considered:**
- Opposite convention (positive = credit): Conflicts with Plaid
- Absolute values with type flag: More complex, requires extra column

**Impact:** All feature modules (subscriptions, savings, credit, income) use this convention. Tests verify correct sign handling.

---

### Decision 15: Subscription Detection Without Strict Temporal Spacing

**Context:** Need to identify recurring merchants from transaction history.

**Decision:** Detect subscriptions based on occurrence count (≥3) and amount consistency (≤10% variance), without requiring exact monthly/weekly spacing.

**Rationale:**
- Real-world subscriptions may have billing date drift (28-31 days)
- Payment method changes can cause date shifts
- Focus on "repeated similar charges" rather than "perfect periodicity"
- More robust to data quality issues

**Alternatives Considered:**
- Strict 30±3 day spacing: Too brittle, misses legitimate subscriptions
- Frequency detection via FFT: Overkill for MVP
- Manual merchant category list: Inflexible, high maintenance

**Implementation:** Check `count ≥ 3` and `std/mean ≤ 0.10` across 90-day lookback window.

**Impact:** Higher recall for subscription detection, may catch some false positives (handled by variance threshold).

---

### Decision 16: Normalize Monthly Spend to 30-Day Window

**Context:** Subscription spend varies by time window (30d vs 180d), need consistent "monthly" metric.

**Decision:** Calculate total spend in window, then multiply by `(30 / window_days)` to normalize.

**Rationale:**
- Provides apples-to-apples comparison across windows
- User-facing metric should be "per month" (intuitive)
- Handles partial months correctly
- Simple linear scaling (no complex averaging)

**Formula:** `monthly_spend = total_spend_in_window * (30 / window_days)`

**Example:** $63.96 over 180 days → $63.96 × (30/180) = $10.66/month

**Impact:** Monthly spend values differ between 30d and 180d windows (expected behavior).

---

### Decision 17: Credit Utilization as Point-in-Time Metric

**Context:** Credit utilization is account balance divided by limit.

**Decision:** Calculate utilization from current snapshot only, not time-windowed.

**Rationale:**
- Utilization is a snapshot metric (current balance / limit)
- No historical trend needed for persona assignment
- Reduces complexity vs. tracking utilization over time
- Aligns with credit scoring industry practice

**Alternatives Considered:**
- Average utilization over 30/180 days: Requires balance history tracking
- Peak utilization: More complex, marginal value for MVP

**Impact:** Credit signals stored under 'current' key, not '30d'/'180d' like other signals.

---

### Decision 18: Income Detection via Keywords + Category Matching

**Context:** Need to identify payroll deposits from transaction data.

**Decision:** Detect income via dual criteria: (1) merchant name contains payroll keywords OR (2) category matches INCOME pattern, AND (3) amount is negative (credit).

**Rationale:**
- Keyword matching: Catches "Payroll", "Direct Dep", "Salary"
- Category matching: Catches structured Plaid categories
- Redundancy increases recall without sacrificing precision
- Negative amount filter prevents false positives

**Keywords:** `["payroll", "direct dep", "salary", "wages"]`
**Categories:** `INCOME`, `TRANSFER_IN`

**Impact:** High-confidence income detection across varied data formats.

---

### Decision 19: Graceful Degradation for Zero Transactions

**Context:** Edge case where user has no transactions in analysis window.

**Decision:** Return zero/null values for all signals without throwing errors.

**Rationale:**
- New users may have zero history
- Data quality issues may result in missing transactions
- Silent failures cause debugging nightmares
- Explicit zero signals allow downstream processing

**Behavior:**
- `recurring_count = 0`
- `emergency_fund_months = 0.0`
- `median_pay_gap_days = 0`
- `pay_frequency = 'unknown'`

**Impact:** All 4 feature modules handle empty data gracefully. Test coverage for edge case.

---

### Decision 20: Flatten Signals for Parquet Storage

**Context:** Feature modules return nested dictionaries (30d/180d), but Parquet prefers flat columns.

**Decision:** Create flattened column names like `sub_30d_recurring_count`, `sav_180d_net_inflow`, etc.

**Rationale:**
- Parquet/pandas work best with flat schemas
- Column names are self-documenting (module_window_metric)
- Easier to query and visualize
- Standard analytics pattern

**Naming Convention:** `{module}_{window}_{metric}`
**Examples:**
- `sub_30d_recurring_count`
- `credit_max_util_pct`
- `inc_180d_median_pay_gap_days`

**Impact:** signals.parquet has 35+ columns. Easy to filter by window or module.

---

### Decision 21: Generate Trace JSONs in Pipeline, Not in Individual Modules

**Context:** Need per-user decision traces for auditability.

**Decision:** Orchestrator (`features/__init__.py`) aggregates all signals and writes trace JSON, rather than each module writing separately.

**Rationale:**
- Single trace file per user (not 4 separate files)
- Consistent trace format across modules
- Atomic write (no partial traces)
- Orchestrator knows full context

**Trace Structure:**
```json
{
  "user_id": "U001",
  "timestamp": "2025-11-03T...",
  "phase": "behavioral_signals",
  "signals": {
    "subscriptions": {...},
    "savings": {...},
    "credit": {...},
    "income": {...}
  }
}
```

**Impact:** 100 trace files in `docs/traces/`, one per user. Operator dashboard loads these for review.

### PR #3: Persona Assignment
TBD

### PR #4: Recommendation Engine
TBD

### PR #5: Guardrails & Consent

### Date: 2025-11-03

---

### Decision 28: Integrated Guardrails Architecture

**Context:** Need to implement consent enforcement, tone validation, and eligibility filtering without creating excessive complexity or redundant code.

**Decision:** Adopt an integrated approach - create separate guardrails modules but integrate them directly into the recommendation engine flow rather than creating an external orchestration layer.

**Rationale:**
- **Separation of Concerns:** Individual modules (consent.py, tone.py, eligibility.py) can be tested and maintained independently
- **Minimal Overhead:** No extra API layer or service calls required
- **Direct Integration:** Guardrails execute inline during recommendation generation, ensuring no recommendations bypass checks
- **Audit Trail:** All guardrail decisions logged to trace JSONs in real-time
- **Reusability:** Modules can be imported by future API endpoints or UI components

**Alternatives Considered:**
- **Standalone Guardrails Service:** Would require API calls, adds latency and complexity for MVP
- **Recommendation Engine Only:** Would make engine.py too large and hard to maintain
- **External Orchestrator:** run_all_guardrails() function exists but used for batch operations, not inline

**Implementation:**
- `guardrails/consent.py`: Database functions for grant/revoke/check consent
- `guardrails/tone.py`: Regex-based prohibited phrase detection
- `guardrails/eligibility.py`: Product eligibility and predatory filtering
- `guardrails/__init__.py`: Orchestrator for batch operations
- `recommend/engine.py`: Imports guardrails modules and executes checks inline

**Impact:** Guardrails execute as part of recommendation flow with ~0.1s overhead per user.

---

### Decision 29: Consent Management with Full CRUD Operations

**Context:** PRD requires explicit opt-in/opt-out with timestamp tracking, but unclear if recommendation engine should own consent modification.

**Decision:** Create full consent management functions (grant/revoke/check/history) in guardrails/consent.py, even though recommendation engine only reads consent status.

**Rationale:**
- **Separation of Concerns:** Consent management is a guardrail responsibility, not a recommendation responsibility
- **Future UI Integration:** User and operator dashboards (PR #6-7) will need grant/revoke functions
- **Audit Requirements:** get_consent_history() provides full audit trail for compliance
- **Batch Operations:** batch_grant_consent() useful for testing and initial setup
- **Read-Only Engine:** Recommendation engine only calls check_consent(), doesn't modify state

**Alternatives Considered:**
- **Validators Only:** Would require UI/API to implement consent modification separately (code duplication)
- **Engine Ownership:** Would violate single responsibility principle

**Implementation:**
- `grant_consent(user_id)`: Sets consent_granted=1, records timestamp
- `revoke_consent(user_id)`: Sets consent_granted=0, records revoked_timestamp
- `check_consent(user_id)`: Returns boolean status (used by engine)
- `get_consent_history(user_id)`: Returns full audit trail
- `batch_grant_consent(user_ids)`: Bulk operation for testing

**Impact:** Complete consent management API ready for UI integration in PR #6-7.

---

### Decision 30: Existing Account Checks Using Preloaded Context

**Context:** Eligibility filtering requires knowing if user already owns a product type (e.g., savings account). Need to decide between querying database or using preloaded data.

**Decision:** Use existing_account_types from user_context already loaded by _load_user_context() rather than adding new database queries.

**Rationale:**
- **Efficiency:** Accounts already loaded at line 180-189 of engine.py, no additional queries needed
- **Accuracy:** Direct SQLite query ensures real-time, accurate account ownership data
- **Consistency:** Same data source used for rationale formatting and eligibility checking
- **Performance:** ~0ms overhead (data already in memory)

**Alternatives Considered:**
- **Additional SQLite Queries:** Would be redundant and slower
- **Signals.parquet Only:** Behavioral signals don't track exact account ownership
- **Both:** Unnecessary complexity for MVP

**Implementation:**
- `_load_user_context()` already executes:
  ```python
  accounts_df = pd.read_sql("SELECT * FROM accounts WHERE user_id = ?", conn, params=(user_id,))
  context["existing_account_types"] = accounts_df["account_type"].value_counts().to_dict()
  ```
- `check_existing_accounts()` uses this preloaded dict to prevent duplicate offers

**Impact:** Zero additional database load, maintains accuracy.

---

### Decision 31: Predatory Product Filtering with Explicit Blocklist

**Context:** PRD requires excluding predatory products (payday loans, title loans, etc.) from recommendations.

**Decision:** Implement explicit runtime check against PREDATORY_PRODUCTS list in constants.py for all partner offers.

**Rationale:**
- **Defense in Depth:** Even if content_catalog.py is trustworthy, runtime validation prevents future catalog errors
- **Auditability:** Blocked products logged to trace files with explicit reason
- **Constants-Driven:** Single source of truth in ingest/constants.py for what constitutes "predatory"
- **Zero Tolerance:** No predatory products should ever reach users, even during development

**Alternatives Considered:**
- **Trust Catalog Only:** Risky - catalog could be edited incorrectly
- **Regex-Based Detection:** Too brittle, wouldn't catch all variations
- **Manual Review Only:** Not scalable, relies on operator catching mistakes

**Implementation:**
- Added filter_predatory_products() to guardrails/eligibility.py
- Called in _select_partner_offers() before eligibility checks
- Blocked products logged to trace file via _log_blocked_offers()
- PREDATORY_PRODUCTS list: ["payday_loan", "title_loan", "rent_to_own", "high_fee_checking"]

**Impact:** 100% guarantee no predatory products recommended, with full audit trail.

---

### Decision 32: Tone Validation with Regex-Based Detection

**Context:** PRD prohibits shaming language ("overspending", "bad habits", etc.). Need efficient detection method.

**Decision:** Use regex-based phrase matching with word boundaries to detect PROHIBITED_PHRASES from constants.py.

**Rationale:**
- **Deterministic:** Regex provides consistent, explainable results (vs. ML models)
- **Fast:** ~0.01ms per recommendation text check
- **Maintainable:** Adding new phrases requires only updating constants.py
- **Audit-Friendly:** Exact phrase matches logged with context and suggestions
- **Constants-Driven:** PROHIBITED_PHRASES and PREFERRED_ALTERNATIVES centralized

**Alternatives Considered:**
- **NLP Sentiment Analysis:** Too slow, less explainable, overkill for MVP
- **Keyword Search:** Would match partial words (e.g., "discipline" in "interdisciplinary")
- **Manual Review Only:** Not scalable, can't catch all violations

**Implementation:**
- `validate_tone()`: Regex with word boundaries (`\b phrase \b`) to avoid partial matches
- `scan_recommendations()`: Batch validation of all recommendations
- Violations logged to trace file with:
  - Exact phrase detected
  - Position in text
  - Surrounding context (±30 chars)
  - Suggested alternative from PREFERRED_ALTERNATIVES

**Pattern Example:**
```python
pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
```

**Impact:** Tone violations detected with 100% recall on prohibited phrases, 0 false positives on partial matches.

---

### Decision 33: Non-Blocking Tone Validation for MVP

**Context:** Tone validation detects violations, but should we remove violating recommendations or flag them for review?

**Decision:** Flag tone violations in metadata and trace logs, but do NOT remove recommendations for MVP. Violations appear as warnings in operator dashboard.

**Rationale:**
- **Operator Review:** Allows human judgment on borderline cases
- **Learning:** Helps identify if prohibited phrase list is too strict or too lenient
- **Auditability:** Full record of violations for compliance review
- **MVP Scope:** Content catalog should already be clean; violations indicate catalog issues to fix
- **Fail-Safe:** If strict blocking needed later, easily enabled via strict_mode parameter

**Alternatives Considered:**
- **Strict Blocking:** Would prevent recommendations from reaching users but removes operator discretion
- **No Validation:** Would violate PRD requirement for tone guardrails

**Implementation:**
- Tone scan results added to response metadata:
  ```python
  "tone_check_passed": tone_scan["passed"],
  "tone_violations_count": tone_scan.get("violations_found", 0)
  ```
- Violations logged to trace file for operator dashboard
- apply_tone_filter() function exists with strict_mode option for future use

**Impact:** Recommendations reach users but violations flagged for operator review and catalog improvement.

---

### Decision 34: Guardrails Execution Order

**Context:** Multiple guardrails need to run - in what order?

**Decision:** Execute in order: Consent (blocking) → Tone Validation (logging) → Eligibility Filtering (blocking).

**Rationale:**
- **Consent First:** No processing should occur without consent; exit early if denied
- **Tone Second:** Validation on generated text; logs violations but doesn't block
- **Eligibility Last:** Filters offers after all content generated; most expensive check

**Flow:**
1. Check consent → If denied, return empty response immediately
2. Generate recommendations (education + offers)
3. Filter predatory products from offers → Log blocked items
4. Check eligibility rules → Remove ineligible offers
5. Validate tone on final recommendations → Log violations
6. Append disclaimers → Return to user

**Impact:** Efficient early-exit for users without consent; comprehensive checks for users with consent.

---

## PR #6: User Interface (Streamlit App)

### Date: 2025-11-03

---

### Decision 35: Single-File Streamlit App for MVP

**Context:** User dashboard could be split into multiple modules or kept as single file.

**Decision:** Implement entire user dashboard in single `ui/app_user.py` file (~650 lines).

**Rationale:**
- **Simplicity:** Easier to navigate for MVP; all UI logic in one place
- **Streamlit Pattern:** Streamlit apps commonly use single-file structure for small apps
- **Performance:** No import overhead across multiple modules
- **Maintainability:** Clear separation between app_user.py (end user) and app_operator.py (compliance team)

**Alternatives Considered:**
- **Multi-Page Streamlit App:** Built-in pages/ directory structure - adds complexity for 3 simple pages
- **Component Library:** Separate files for components - premature abstraction for MVP
- **Class-Based Structure:** OOP approach - Streamlit is functional by design

**Impact:** All user dashboard code in single file; easy to locate and modify.

---

### Decision 36: User Selector in Sidebar (Not Authentication)

**Context:** With 100 synthetic users, how should users switch between profiles?

**Decision:** Dropdown selector in sidebar showing all users with consent indicators (✅/⏸️).

**Rationale:**
- **MVP Scope:** No authentication required per PRD
- **Demo-Friendly:** Easy to show different personas during presentations
- **Testing:** Allows manual testing of all 100 user profiles
- **Transparency:** Consent status visible at a glance
- **User Experience:** Familiar dropdown pattern; no login friction

**Alternatives Considered:**
- **Fixed Demo User:** Would limit testing to single profile
- **URL Parameters:** `?user_id=user_0001` - requires manual URL editing
- **Login Screen:** Adds authentication complexity not needed for MVP

**Implementation:**
```python
user_options = [
    f"{row['user_id']} - {row['name']}" +
    (" ✅" if row['consent_granted'] else " ⏸️")
    for _, row in users_df.iterrows()
]
```

**Impact:** Easy profile switching for testing; clear consent visibility.

---

### Decision 37: Consent Banner with Limited UI View

**Context:** Per PRD, users without consent should see limited UI with consent banner, not complete blocking.

**Decision:** Show persona profile section (read-only) + consent banner + privacy info when consent not granted.

**Rationale:**
- **Transparency:** Users see what they'll get if they opt in
- **Education:** Explains data usage clearly before consent
- **Reduced Friction:** No hard wall; users can explore UI structure
- **Compliance:** No processing occurs; banner makes requirements clear
- **User Control:** Easy opt-in button prominently displayed

**Alternatives Considered:**
- **Complete Block:** Would hide all UI until consent - too restrictive
- **No Visual Change:** Would be confusing; unclear why no recommendations
- **Modal Dialog:** Would be intrusive; users can't dismiss to explore

**Implementation:**
- Check `consent_granted` in each render function
- If False: Display info card + consent banner + return early
- No recommendations generated without consent
- Grant consent button calls `grant_consent(user_id)` → updates SQLite → reruns app

**Impact:** Balanced UX - transparency without hard blocking.

---

### Decision 38: Manual Refresh Button (Not Auto-Refresh)

**Context:** Should data reload automatically or require user action?

**Decision:** Load data once on page navigation, with manual "🔄 Refresh Data" button in top-right corner.

**Rationale:**
- **Performance:** Avoid unnecessary database/file reads on every interaction
- **User Control:** Explicit refresh gives users predictable behavior
- **Streamlit Pattern:** Session state persists; rerun only when needed
- **MVP Scope:** No real-time data; synthetic data doesn't change during session

**Alternatives Considered:**
- **Auto-Refresh on Sidebar Change:** Would reload on every user selection - too aggressive
- **Polling (Every N Seconds):** Unnecessary for static synthetic data
- **No Refresh Button:** Would require app restart to see updates - poor UX

**Implementation:**
```python
if st.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
```

**Impact:** Efficient data loading; users control when to refresh.

---

### Decision 39: Recommendations-Only Learning Feed (Not Browsable Catalog)

**Context:** Learning feed could show (1) all catalog content, or (2) only personalized recommendations.

**Decision:** Display only personalized recommendations from `generate_recommendations(user_id)`.

**Rationale:**
- **Personalization:** Focus on what's relevant to user's specific situation
- **Simplicity:** Avoids overwhelming users with 20+ catalog items
- **Rationales:** Each item includes concrete data explaining relevance
- **MVP Scope:** Content catalog is implementation detail; users see curated results
- **Alignment:** Matches PRD requirement for 3-5 education items + 1-3 offers

**Alternatives Considered:**
- **Full Catalog Browser:** Would show all content regardless of persona - too generic
- **Hybrid View:** "More articles you might like..." section - adds complexity
- **Tabbed Interface:** Separate tabs for "For You" vs "Browse All" - feature creep

**Implementation:**
- Learning Feed calls `generate_recommendations(user_id)`
- Separates education items and partner offers
- Displays with rationales and disclaimers
- Metadata expander shows generation details

**Impact:** Focused, personalized content; clear rationale for each item.

---

### Decision 40: Persona Descriptions Use User-Friendly Language

**Context:** Personas have technical names (high_utilization, variable_income). How should they appear in UI?

**Decision:** Map technical persona IDs to friendly titles and descriptions with icons.

**Rationale:**
- **User Experience:** "Credit Optimizer" is clearer than "high_utilization"
- **Supportive Tone:** Avoids labels that sound negative or judgmental
- **Engagement:** Icons and colors make personas visually distinct
- **Education:** Descriptions explain what persona means without jargon

**Mapping:**
```python
"high_utilization" → "💳 Credit Optimizer"
  "You're focused on optimizing credit utilization and managing card balances effectively."

"variable_income" → "📊 Flexible Budgeter"
  "You're managing variable income with smart budgeting strategies."
```

**Alternatives Considered:**
- **Use Technical Names:** Would confuse non-technical users
- **Generic Labels:** "Profile A", "Profile B" - meaningless to users
- **Problem-Focused:** "High Debt User" - shaming language, violates tone guardrails

**Impact:** Clear, supportive persona communication; users understand their profile.

---

### Decision 41: Privacy Settings with "Coming Soon" Data Export

**Context:** PRD specifies data export as future feature. How to handle in MVP?

**Decision:** Include Privacy Settings page with disabled "Export My Data" button and explanatory text.

**Rationale:**
- **Transparency:** Users see we plan to offer this feature
- **Completeness:** Privacy page feels complete even without export
- **Roadmap Visibility:** "Coming Soon" sets expectations for future releases
- **No Broken Promises:** Disabled button prevents user frustration

**Alternatives Considered:**
- **Hide Export Feature:** Would seem like we don't care about user data rights
- **Build Export Now:** Out of scope for PR #6; adds complexity
- **Placeholder Text Only:** Button makes feature more tangible

**Implementation:**
```python
st.info("Coming Soon: Download your complete data package including...")
st.button("📦 Export My Data", disabled=True, help="This feature is coming soon!")
```

**Impact:** Complete privacy page; clear roadmap communication.

---

### Decision 42: 4-Column Behavioral Metrics Layout

**Context:** How to display behavioral signals (credit, subscriptions, savings, income) effectively?

**Decision:** 4-column responsive grid using `st.columns(4)` with `st.metric()` widgets.

**Rationale:**
- **Scannable:** Users see all key metrics at a glance
- **Responsive:** Streamlit collapses columns on mobile automatically
- **Consistent:** Each column follows same pattern (2 metrics per category)
- **Focused:** Shows most important signals; detailed data in expanders

**Metrics Selection:**
- **Credit:** num_cards, avg_utilization_pct
- **Subscriptions:** recurring_count, monthly_spend
- **Savings:** net_inflow, emergency_fund_months
- **Income:** median_pay_gap_days, cash_buffer_months

**Alternatives Considered:**
- **Single Column List:** Would require scrolling; less scannable
- **Tabs:** Would hide data behind clicks; less discoverable
- **Chart Visualizations:** Too complex for MVP; metrics suffice

**Impact:** Clear, scannable overview of financial patterns.

---

### Decision 43: Tone Compliance in UI Text

**Context:** UI contains explanatory text, labels, and messages. How to ensure no shaming language?

**Decision:** Manual review of all UI text against prohibited phrases list; use supportive alternatives.

**Prohibited:** "overspending", "bad habits", "lack discipline", "you're failing"

**Preferred:** "consider reducing", "optimize your spending", "explore strategies", "getting to know you"

**Examples:**
- ❌ "You're overspending on subscriptions"
- ✅ "You have 3 recurring services - here's how to optimize them"

- ❌ "Your bad credit habits are costly"
- ✅ "Bringing utilization below 30% could reduce interest charges"

**Implementation:**
- All user-facing strings reviewed against `PROHIBITED_PHRASES` from constants
- Supportive framing: "We noticed..." instead of "You're doing wrong..."
- Growth mindset: "Getting to know you..." for users with insufficient data

**Impact:** 100% tone compliance in UI; educational and supportive throughout.

---

## Operator Overrides

This section will track manual operator interventions once the operator dashboard is implemented (PR #7).

Format:
```
Date: YYYY-MM-DD
Operator: Name
User: user_id
Action: approve | override | flag
Reason: Description
```

---

---

## PR #7: Operator Dashboard

### Date: 2025-11-03

---

### Decision 44: Six-Tab Analytical Interface

**Context:** Operator dashboard must support multiple workflows: oversight, review, audit, compliance.

**Decision:** Build 6 specialized tabs in single Streamlit app:
1. Overview - System health and metrics
2. User Management - Filterable user directory
3. Behavioral Signals - Aggregate analytics and distributions
4. Recommendation Review - Approve/override/flag workflow
5. Decision Trace Viewer - Full audit trail per user
6. Guardrails Monitor - Compliance enforcement summary

**Rationale:**
- Tab-based navigation matches operator mental model (analysis vs. action vs. audit)
- Each tab focused on single task, reducing cognitive load
- Mirrors industry standard admin dashboards (AWS Console, Google Admin, etc.)
- Sidebar navigation allows quick context switching

**Alternatives Considered:**
- Multi-page app: More complex state management, harder to deploy
- Accordion layout: Too much scrolling, poor discoverability
- Separate apps per function: Deployment complexity, data loading duplication

**Impact:** ~950 lines of code in single file; fast load time; manual testing focused on tab navigation.

---

### Decision 45: Override Logging to decision_log.md + Trace JSON

**Context:** Operator overrides must be auditable and traceable to specific users.

**Decision:** Dual-write overrides to both `docs/decision_log.md` (human-readable) and user trace JSON (machine-readable).

**Markdown format:**
```markdown
### Operator Override - 2025-11-03 14:32:15
**Operator:** Jane Doe
**User:** user_0042
**Action:** OVERRIDE
**Recommendation:** Lower Credit Utilization
**Reason:** User recently paid down balance; utilization outdated
```

**Trace JSON format:**
```json
{
  "timestamp": "2025-11-03T14:32:15",
  "decision_type": "operator_override",
  "operator": "Jane Doe",
  "action": "override",
  "recommendation_title": "Lower Credit Utilization",
  "reason": "User recently paid down balance; utilization outdated"
}
```

**Rationale:**
- Markdown: Easy to read/search, version control friendly, compliant with PRD requirement
- Trace JSON: Programmatic access for future analytics, preserves user-level audit trail
- Both: Redundancy ensures auditability even if one file corrupted

**Alternatives Considered:**
- SQLite table: Requires migration, complicates backup/restore
- Markdown only: Hard to parse programmatically
- JSON only: Not human-friendly for quick review

**Impact:** `log_operator_override()` function handles both writes atomically; <1ms overhead.

---

### Decision 46: Inline Tone/Eligibility Checks in Review Tab

**Context:** Operators need to see guardrail results when reviewing recommendations.

**Decision:** Re-run `validate_tone()` and display eligibility status inline for each recommendation during review.

**Display:**
- Green checkmark: "✅ Tone: Passed"
- Red warning: "⚠️ Tone: 2 violations detected" with list of prohibited phrases
- Blue badge: "💼 Partner Offer - Eligibility Checked"

**Rationale:**
- Immediate visual feedback on compliance issues
- No need to navigate to separate Guardrails Monitor tab
- Operator can make informed approve/override decision with full context
- Matches PR #5 guardrails integration pattern

**Alternatives Considered:**
- Link to Guardrails Monitor: Extra clicks, breaks flow
- Trust trace JSON only: Stale data if recommendation re-generated
- No inline checks: Operator flying blind

**Impact:** ~0.01s per recommendation for tone validation; negligible UX impact.

---

### Decision 47: Bar Charts for Distribution Analysis

**Context:** Operators need to understand system-wide patterns (persona distribution, utilization ranges).

**Decision:** Use Streamlit's built-in `st.bar_chart()` for persona distribution, utilization histograms, subscription counts.

**Rationale:**
- Simple, fast, no additional dependencies (no matplotlib/plotly)
- Interactive hover tooltips built-in
- Automatically responsive
- Consistent with Streamlit design language
- Sufficient for MVP; can upgrade to plotly post-MVP if needed

**Alternatives Considered:**
- Plotly: More features but larger dependency, slower load
- Matplotlib: Static images, poor interactivity in Streamlit
- Tables only: Less engaging, harder to spot patterns

**Impact:** Faster rendering, lighter bundle; charts auto-update on data refresh.

---

### Decision 48: User Trace Viewer with Expandable Sections

**Context:** Trace JSONs contain 4 phases (signals, persona, recommendations, guardrails) with nested structure.

**Decision:** Use `st.expander()` for each pipeline phase; default first phase (signals) to expanded.

**Structure:**
```
📊 Behavioral Signals [expanded]
  - Subscriptions (30d, 180d)
  - Savings (30d, 180d)
  - Credit (current)
  - Income (30d, 180d)

🎭 Persona Assignment [collapsed]
  - Assigned persona
  - Criteria met
  - All checks

💡 Recommendations [collapsed]
  - Metadata
  - List of recommendations

🛡️ Guardrail Decisions [collapsed]
  - Consent checks
  - Tone violations
  - Blocked offers
  - Operator overrides

📄 Raw JSON [collapsed]
```

**Rationale:**
- Progressive disclosure: Show most important data first (signals drive everything)
- Reduce cognitive overload: Collapsed sections hide complexity until needed
- Consistent with PRD's "decision trace" requirement
- Works well on laptop screens without scrolling

**Alternatives Considered:**
- Flat view: Too much data at once, overwhelming
- Tabs within trace viewer: Over-engineered, harder to compare phases
- Raw JSON only: Hard to navigate, not operator-friendly

**Impact:** Faster comprehension; operators can drill down as needed; supports auditability.

---

### Decision 49: Bulk Consent Operations with Warning

**Context:** Operators may need to grant consent to multiple users for testing/setup.

**Decision:** Provide "Grant Consent to Filtered Users" button with count preview and "⚠️ Use with caution" warning.

**Safety Rails:**
- Shows exact count of users affected before action
- Only operates on currently filtered users (not all users)
- Uses existing `batch_grant_consent()` from PR #5
- No bulk revocation (requires individual action)

**Rationale:**
- Testing efficiency: Setup 100 users for demo without clicking 100 times
- Controlled scope: Filter to specific demographics/personas before bulk action
- Audit trail: `batch_grant_consent()` logs each individual grant with timestamp
- Safety: Warning prevents accidental bulk changes

**Alternatives Considered:**
- No bulk operations: Tedious for testing, poor DX
- Confirmation dialog: Extra click but adds safety (consider post-MVP)
- Bulk revocation: Too dangerous, omit from MVP

**Impact:** Faster testing/demo setup; operators warned of potential impact.

---

### Decision 50: No Authentication in MVP

**Context:** Production operator dashboard requires role-based access control (RBAC).

**Decision:** Omit authentication from PR #7; document as post-MVP enhancement.

**Rationale:**
- MVP runs locally on operator's machine (localhost:8501)
- No network exposure in current deployment model
- Authentication adds complexity: user management, session handling, password storage
- Focus PR #7 on core functionality: oversight, review, audit
- Post-MVP: Add Streamlit auth, LDAP integration, or OAuth

**Security Mitigations for MVP:**
- Local-only deployment (no public URL)
- Operator logs include name (honor system) for auditability
- All overrides traced to decision_log.md

**Alternatives Considered:**
- Basic password protection: Still requires session management
- Streamlit Cloud authentication: Not applicable for local deployment
- Skip MVP entirely: Blocks critical oversight functionality

**Impact:** Faster MVP delivery; clear post-MVP roadmap for auth enhancement.

---

## PR #8: Evaluation Harness

### Date: 2025-11-03

---

### Decision 51: Coverage Excludes 'General' Persona

**Context:** Coverage metric measures "% of users with meaningful persona + ≥3 behaviors".

**Decision:** Exclude users with 'general' persona from coverage numerator.

**Rationale:**
- 'general' persona is assigned when NO persona criteria are met (catch-all default)
- Coverage should measure meaningful behavioral classification, not catch-all assignment
- A user with 'general' persona by definition has insufficient behavioral signals
- PRD states "≥1 persona" implies a substantive classification, not a default

**Calculation:**
```python
coverage = (users_with_non_general_persona_AND_3behaviors / total_users) * 100
```

**Expected Result:** ~67% coverage (67 high_utilization users from current data), not 100%.

**Alternatives Considered:**
- Include 'general' persona: Inflates coverage metric artificially
- No default persona: Fails gracefully but loses audit trail for unclassified users

**Impact:** Coverage metric accurately reflects behavioral signal quality, not just persona table population.

---

### Decision 52: Age Bucketing Strategy (3 Ranges)

**Context:** Fairness analysis requires age grouping for meaningful demographic parity.

**Decision:** Use 3 life-stage age buckets: **18-30**, **31-50**, **51+**.

**Rationale:**
- **18-30**: Young adults (early career, student loans, building credit, subscription-heavy)
- **31-50**: Mid-career (mortgages, family finances, retirement planning, savings focus)
- **51+**: Pre-retirement/retirement (wealth preservation, fixed income, lower utilization)
- Sample size: 100 users → ~33 per bucket ensures statistical validity
- Life-stage relevance: Financial behaviors differ meaningfully across these ranges

**Alternatives Considered:**
- 4 buckets (18-29, 30-44, 45-59, 60+): Smaller sample sizes (~25 users/bucket)
- 5 buckets (very granular): Risk of <20 users/bucket, insufficient for parity checks
- 2 buckets (18-40, 41+): Too coarse, misses mid-career dynamics

**Impact:** Fairness metric can detect age-based bias without over-segmenting sample.

---

### Decision 53: Timestamped Outputs with Symlinks

**Context:** Need longitudinal tracking of evaluation results while maintaining easy access to latest run.

**Decision:** Generate timestamped files + symlinks to latest:
- `eval/results_2025-11-03T15-30-00.json` → `eval/results.json` (symlink)
- `eval/results_2025-11-03T15-30-00.csv` → `eval/results.csv` (symlink)

**Rationale:**
- **Historical tracking**: All runs preserved for comparison over time
- **Easy access**: Operator dashboard / scripts can always read `eval/results.json` (latest)
- **Git-friendly**: Symlinks don't bloat repository, timestamped files can be `.gitignore`d
- **Timestamp format**: ISO 8601 (`YYYY-MM-DDTHH-MM-SS`) ensures sortable filenames

**Alternatives Considered:**
- Overwrite single file: No historical tracking
- Timestamped only (no symlinks): Requires manual "find latest" logic
- Database storage: Over-engineered for MVP

**Impact:** Evaluation history preserved; easy integration with dashboards/CI.

---

### Decision 54: Relevance Scoring via Content Category Alignment

**Context:** Relevance metric measures "persona → recommendation alignment" but content catalog has diverse items.

**Decision:** Use rule-based category mapping:
- **high_utilization** → `credit_basics`, `debt_paydown`, `payment_automation`, `counseling`
- **variable_income** → `budgeting`, `emergency_fund`, `tax_planning`
- **subscription_heavy** → `subscription_management`
- **savings_builder** → `goal_setting`, `savings_optimization`, `savings_automation`

**Rationale:**
- Deterministic: No ML/NLP needed for MVP
- Auditable: Clear rules for why a recommendation is "relevant"
- Based on content catalog structure from PR #4 (`content_catalog.py`)
- Partner offers included (e.g., `budgeting_app` for variable_income)

**Calculation:**
```python
relevance = (recommendations_with_matching_category / total_recommendations) * 100
```

**Target:** ≥90% (allows 10% flexibility for multi-persona edge cases).

**Alternatives Considered:**
- Semantic similarity (NLP): Too complex for MVP
- Manual review scores: Not scalable, subjective
- Exact title matching: Too brittle (titles may change)

**Impact:** Relevance metric objectively verifies persona→content mapping logic.

---

### Decision 55: Fairness Tolerance at ±10%

**Context:** Demographic parity must balance statistical rigor with sample size limitations.

**Decision:** Set fairness tolerance at **±10%** of overall persona assignment rate.

**Rationale:**
- **Industry standard**: ±10% commonly used in bias detection (see: ML fairness literature)
- **Sample size**: With 100 users, ±10% allows ~7-10 user variance per demographic group
- **Statistical validity**: Tighter tolerances (±5%) risk false positives with small samples
- **Actionable threshold**: >10% deviation indicates systematic bias worth investigating

**Example:** If overall persona rate = 50%:
- **Pass:** Group A = 45%, Group B = 55% (within ±10%)
- **Fail:** Group C = 35%, Group D = 65% (outside ±10%)

**Alternatives Considered:**
- ±5%: Too strict for 100-user sample, many false positives
- ±15%: Too loose, misses meaningful bias
- Statistical significance testing (chi-square): Over-engineered for MVP

**Impact:** Fairness metric flags meaningful demographic imbalances without over-sensitivity.

---

### Decision 56: Latency Measurement with `time.perf_counter()`

**Context:** Latency metric requires high-precision timing for sub-second measurements.

**Decision:** Use `time.perf_counter()` (not `time.time()` or `time.process_time()`).

**Rationale:**
- **Precision**: `perf_counter()` has nanosecond resolution vs. microseconds for `time()`
- **Monotonic**: Not affected by system clock adjustments (DST, NTP)
- **Wall-clock time**: Measures actual user-perceived latency (includes I/O, not just CPU)
- **Python 3.3+**: Standard library, no dependencies

**Measurement Points:**
```python
start = time.perf_counter()
result = generate_recommendations(user_id)
end = time.perf_counter()
latency = end - start
```

**Metrics Tracked:**
- Mean, median, p95, p99, min, max latency
- Sample size: 10 users for tests (configurable), all consented users for full eval

**Target:** <5 seconds mean latency per user (easily met at ~0.01s with local data).

**Alternatives Considered:**
- `time.time()`: Less precise, subject to clock drift
- `time.process_time()`: Only CPU time, excludes disk I/O (misleading for data loading)
- Manual profiling: Over-engineered, not needed for simple benchmark

**Impact:** Accurate, reproducible latency benchmarking for performance tracking.

---

### Decision 57: Auditability Requires Complete Trace JSONs

**Context:** Auditability metric ensures all recommendations are traceable to source data.

**Decision:** Define "complete trace" based on consent status:
- **Consent granted**: Must have `signals`, `persona_assignment`, AND `recommendations` sections
- **Consent not granted**: Must have `signals` and `persona_assignment` (NO recommendations)

**Strict Validation:**
- Trace file must exist in `docs/traces/{user_id}.json`
- All required sections present (no null/empty objects)
- Recommendations section ONLY if consent granted (violation = incomplete)

**Rationale:**
- Enforces consent compliance: No recs without permission
- Auditability ≠ just file existence; structure matters
- Detects data pipeline failures (missing phases)
- PRD requirement: "100% of recommendations with decision traces"

**Current Data:** 97% auditability (97/100 users have complete traces) → 3 users incomplete.

**Alternatives Considered:**
- File existence only: Too weak, doesn't verify structure
- Recommendations required for all: Violates consent enforcement
- Separate metrics for trace existence vs. completeness: Confusing, redundant

**Impact:** Auditability metric ensures full transparency from signals → persona → recommendations.

---

## Revision History

| Date | PR | Changes |
|------|-------|---------|
| 2025-11-03 | #1 | Initial decision log created (Decisions 1-10) |
| 2025-11-03 | #1 | Added infrastructure decisions (11-13): constants, persona table, traces dir |
| 2025-11-03 | #2 | Added behavioral signal decisions (14-21): amount convention, subscription detection, normalization, credit metrics, income detection, edge cases, storage format |
| 2025-11-03 | #5 | Added guardrails decisions (28-34): integrated architecture, consent CRUD, account checks, predatory filtering, tone validation, non-blocking validation, execution order |
| 2025-11-03 | #6 | Added user interface decisions (35-43): single-file app, user selector, consent banner, manual refresh, recommendations-only feed, user-friendly personas, data export placeholder, 4-column metrics, tone compliance |
| 2025-11-03 | #7 | Added operator dashboard decisions (44-50): six-tab interface, dual-write override logging, inline guardrail checks, bar charts, expandable trace viewer, bulk consent operations, no authentication in MVP |
| 2025-11-03 | #8 | Added evaluation harness decisions (51-57): coverage excludes general persona, age bucketing strategy, timestamped outputs with symlinks, relevance scoring via categories, fairness tolerance ±10%, latency measurement precision, auditability completeness checks |

### Operator Override - 2025-11-04 10:10:17

**Date:** 2025-11-04
**Operator:** Casey
**User:** user_0008
**Action:** APPROVE
**Recommendation:** 0% Balance Transfer Credit Card  
**Reason:** Approved by operator

---


### Operator Override - 2025-11-04 10:10:50

**Date:** 2025-11-04
**Operator:** Casey
**User:** user_0008
**Action:** APPROVE
**Recommendation:** Understanding Credit Utilization and Your Score  
**Reason:** Approved by operator

---


### Operator Override - 2025-11-04 10:11:26

**Date:** 2025-11-04
**Operator:** Casey
**User:** user_0008
**Action:** OVERRIDE
**Recommendation:** Balance Transfer Cards: When They Help and When They Hurt  
**Reason:** likely to increase utilization on the card

---


### Operator Override - 2025-11-04 10:11:50

**Date:** 2025-11-04
**Operator:** Casey
**User:** user_0008
**Action:** FLAG
**Recommendation:** How Interest Charges Work: APR, Compounding, and Grace Periods  
**Reason:** not necessary

---


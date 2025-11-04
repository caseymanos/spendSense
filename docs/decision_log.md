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
TBD

### PR #3: Persona Assignment
TBD

### PR #4: Recommendation Engine
TBD

### PR #5: Guardrails & Consent
TBD

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

## Revision History

| Date | PR | Changes |
|------|-------|---------|
| 2025-11-03 | #1 | Initial decision log created (Decisions 1-10) |
| 2025-11-03 | #1 | Added infrastructure decisions (11-13): constants, persona table, traces dir |

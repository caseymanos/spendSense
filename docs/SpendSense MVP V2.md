SpendSense MVP V2
1. Overview

Goal:
Build an explainable, consent-aware financial behavior analysis system using synthetic Plaid-style data, that detects spending and savings patterns, assigns behavioral personas, and provides educational recommendations — all within strict guardrails of transparency, fairness, and user control.

Core Principles:

Transparency over sophistication

User control over automation

Education over sales

Fairness built in from day one

Scope:
This MVP focuses on the rule-based, auditable foundation.
No AI/NLP integrations or post-MVP creative formats are included.

2. Technical Environment
Component	Tooling
Environment Manager	uv (modern alternative to venv / pip)
Language	Python 3.11+
Frameworks	streamlit, fastapi (for local REST endpoints)
Data Tools	pandas, pyarrow, faker, numpy
Storage	SQLite (relational) + Parquet (analytics) + JSON (logs)
Testing	pytest
Randomness	Deterministic via seeded RNG

All components run locally with no external dependencies.

3. Data Generation (Temporal Synthetic Dataset)

Objective:
Simulate 50–100 users with realistic, time-series Plaid-style financial activity over a six-month period.

Data Schema:

Accounts:
account_id, type/subtype, balances, iso_currency_code, holder_category

Transactions:
account_id, date, amount, merchant_name, payment_channel, personal_finance_category, pending

Liabilities:
APR, minimum_payment, last_payment, overdue_status, next_due_date

Characteristics:

Generated with faker for names/merchants; numeric patterns with numpy

No real PII; only masked synthetic identifiers

Each user includes 6 months of dated transactions (temporal series)

Demographic fields (age, gender, income tier, region) for fairness analysis

Export formats:

data/users.sqlite — relational store

data/transactions.parquet — analytics store

data/config.json — generation settings

4. Behavioral Signal Detection

Compute four behavioral categories for each user over two time windows (30 days and 180 days):

Category	Key Signals
Subscriptions	Recurring merchants ≥ 3 in 90 days; recurring spend %; monthly recurring total
Savings	Net inflow to savings accounts; growth rate %; emergency fund coverage
Credit	Utilization %; flags for ≥ 30/50/80 %; min-payment-only; interest/overdue detection
Income Stability	Payroll ACH detection; pay frequency; variability; cash-flow buffer in months

Signals are recomputed periodically to emulate live data refresh.

5. Persona Assignment

Assign each user to one of five personas based on detected behaviors:

High Utilization

Variable Income Budgeter

Subscription Heavy

Savings Builder

Custom Persona (reserved for later)

Conflict-Resolution Rule:

Priority	Persona	Rationale
1️⃣	High Utilization	Immediate financial strain
2️⃣	Variable Income Budgeter	Stability and planning gap
3️⃣	Subscription Heavy	Spending pattern optimization
4️⃣	Savings Builder	Positive reinforcement
5️⃣	Custom Persona	Applied if none above match
persona_priority = ["high_utilization", "variable_income", "subscription_heavy", "savings_builder", "custom"]
user_persona = next((p for p in persona_priority if criteria[p]), None)

6. Recommendation Engine (Rule-Based)

Purpose: Generate 3–5 educational items + 1–3 partner offers per user/persona.

Each recommendation must include:

A clear “because” rationale citing user data

A plain-language educational focus

The disclosure:
"This is educational content, not financial advice."

Examples:

“We noticed your Visa ending in 4523 is at 68% utilization ($3,400 / $5,000 limit). Lowering this below 30% can improve your credit health.”

“You’ve had three recurring subscriptions totaling $112/mo; consider reviewing active memberships.”

7. Consent & Eligibility Guardrails

Storage (SQLite):

CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    consent_granted BOOLEAN DEFAULT 0,
    consent_timestamp DATETIME,
    revoked_timestamp DATETIME
);


Consent Path:

User opens the app → consent screen shown.

If consent_granted = FALSE, no data processing occurs.

On opt-in → set flag = TRUE + timestamp.

On revoke → flag = FALSE; user data archived.

Eligibility Filters:

Verify minimum income and credit thresholds

Skip offers for products already owned

Exclude predatory or high-risk recommendations

Tone Checks:

Rule-based string filter to detect “shaming” language

All text reviewed for neutral, empowering phrasing

8. User Interfaces
8.1 User App (app_user.py)

Purpose:
Educational and supportive experience for end users.

Features:

Consent onboarding

Personalized dashboard showing:

Active persona

Detected financial patterns

Recommendations + rationales

“Learn more” buttons linking to educational resources

Mobile-friendly Streamlit theme

8.2 Operator Dashboard (app_operator.py)

Purpose:
Analytical oversight for system operators.

Tabs:

Users – list with filters, consent status

Signals – view 30d/180d behavioral metrics

Personas – assignment visualization

Recommendations – review content + rationales

Decision Traces – JSON viewer for audit logs

Evaluation Summary – displays current metrics (coverage, fairness, latency)

Actions:

✅ Approve Recommendation

✏️ Override / Edit Persona

🚩 Flag for Review

Each action writes to /docs/decision_log.md.

9. Evaluation Harness

Command:

uv run python -m eval.run --input data/transactions.parquet --output eval/results.json


Metrics Computed:

Metric	Description
Coverage	% of users with ≥ 3 signals + assigned persona
Explainability	% of recommendations with rationale text
Relevance	Rule-based persona-content match score
Latency	Mean generation time per user (< 5 s target)
Fairness	Parity of coverage & explainability by demographic group
Auditability	% of recommendations with stored trace JSON

Outputs:

/eval/results.json – structured results

/eval/results.csv – tabular export

/eval/summary.md – human-readable report

10. Testing Plan

Use pytest with seeded data for deterministic validation.

#	Test	Description
1	Ingestion	Validate CSV/JSON schema & error handling
2	Data Integrity	Confirm Plaid-style field coverage
3	Subscriptions	Detect recurring merchants correctly
4	Savings	Compute inflow & emergency coverage accurately
5	Credit	Trigger utilization thresholds & flags
6	Persona	Correct persona given synthetic case files
7	Consent	Ensure processing blocked without consent
8	Recommendations	Generate expected counts w/ rationales
9	Tone	Detect disallowed phrases
10	Evaluation	Produce valid metrics JSON/CSV

All tests must pass before final evaluation.

11. Documentation Outputs
File	Purpose
/docs/schema.md	Data models for accounts, transactions, liabilities
/docs/decision_log.md	Key design choices, overrides, operator actions
/docs/limitations.md	Known trade-offs and MVP constraints
/docs/traces/{user_id}.json	Individual decision traces per user
/docs/eval_summary.md	Evaluation metrics & fairness results
12. Success Criteria
Category	Metric	Target
Coverage	Users with persona + ≥3 behaviors	100%
Explainability	Recs with rationale	100%
Latency	Recommendation time per user	< 5 s
Auditability	Trace availability	100%
Fairness	No demographic group under-represented by > 10%	✅
Testing	Unit/integration tests	≥ 10 passing
Documentation	Schema + decision logs	Complete
13. Deliverables

Full code repository (with /ingest, /features, /personas, /recommend, /guardrails, /ui, /eval, /docs, /tests)

Streamlit user app (app_user.py)

Streamlit operator app (app_operator.py)

Evaluation outputs (eval/results.*)

Documentation bundle (/docs/*)

Technical README with setup and usage instructions

14. Final Note

Financial AI must be explainable and auditable.
Every recommendation must cite a concrete data point.
Systems should empower, not persuade.
Build transparency, fairness, and user control into every decision.

Contact:
Project Lead: Casey Manos
Technical Contact (spec origin): Bryce Harris – bharris@peak6.com
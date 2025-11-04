
Excellent — here’s **Part 1 of 3** for your merged and extended PRD:
**`PRD_V2_Part1_DataFoundation.md`**

It combines your original PRD V1’s structure and user stories with the Peak6 SpendSense specification, updated for a modern `uv + Python + Streamlit` stack and fairness-first design.

---

# **SpendSense MVP V2 — Part 1: Data Foundation**

## **Peak6 SpendSense Mission Statement**

> **From Plaid to Personalized Learning**
> Banks generate massive transaction data through Plaid integrations but struggle to transform it into actionable insights without crossing into regulated financial advice.
>
> **SpendSense MVP V2** builds an explainable, consent-aware platform that detects financial behaviors, assigns user personas, and delivers personalized educational recommendations—with clear guardrails around eligibility, tone, and fairness.

---

## **1. Product Overview**

**Product Name:** SpendSense MVP V2
**Type:** Financial-behavior analysis and education platform
**Target Users:** Financial institutions and individuals leveraging Plaid-style transaction data
**Core Principles:**

* Transparency over sophistication
* User control over automation
* Education over sales
* Fairness built in from day one

### **Vision**

Transform anonymized transaction data into explainable financial learning experiences that educate, not advise.

### **Key Constraint**

All recommendations must remain within *educational* scope—no regulated financial advice.

---

## **2. User Stories**

### **2.1 End User (Bank Customer)**

**As a customer, I want to …**

1. **Understand my spending patterns**

   * So I can see where my money goes each month
   * *Acceptance:* View detected subscriptions, savings trends, and credit utilization

2. **Receive personalized financial education**

   * So I can improve my financial health based on behavior
   * *Acceptance:* 3–5 relevant educational items with plain-language rationales

3. **Control my data usage and consent**

   * So I feel safe sharing transaction data
   * *Acceptance:* Opt-in/out controls and visibility into data usage

4. **See eligible product offers only**

   * So I don’t waste time on irrelevant or ineligible options

5. **Feel supported, not judged**

   * So I stay engaged with learning materials

---

### **2.2 Operator (Compliance/Product Team)**

**As an operator, I want to …**

1. **Review recommendations before release**

   * *Acceptance:* View pending items, approve/override, see decision rationale

2. **Audit system decisions**

   * *Acceptance:* Access complete decision traces per user

3. **Monitor metrics and fairness**

   * *Acceptance:* View coverage, latency, persona distribution, and demographic parity

4. **Manage consent records**

   * *Acceptance:* View and revoke user consent in real time

5. **Flag and export problematic patterns**

   * *Acceptance:* Mark recommendations for review and export for analysis

---

### **2.3 System Administrator**

**As a system administrator, I want to …**

1. **Ingest new transaction data easily**

   * *Acceptance:* Upload CSV/JSON files with schema validation

2. **Monitor system health locally**

   * *Acceptance:* View processing times and error logs

3. **Ensure auditability**

   * *Acceptance:* Access traceable logs of all recommendations and persona assignments

---

## **3. Tech Stack and Architecture**

| Layer              | Tooling / Standard                                      | Purpose                                                             |
| ------------------ | ------------------------------------------------------- | ------------------------------------------------------------------- |
| **Environment**    | `uv` (Python environment manager)                       | Fast isolated dependency resolution                                 |
| **Language**       | Python 3.11 +                                           | Universal support for data and APIs                                 |
| **Frameworks**     | `streamlit`, `fastapi`                                  | Streamlit → UI for operator and user apps; FastAPI → REST endpoints |
| **Data Tools**     | `pandas`, `numpy`, `pyarrow`, `faker`                   | Synthetic data generation + analysis                                |
| **Storage**        | SQLite (relational) + Parquet (analytics) + JSON (logs) | Local persistence and audit logs                                    |
| **Testing**        | `pytest`                                                | Deterministic unit/integration testing                              |
| **Docs & Linting** | `markdown`, `ruff`, `black`                             | Documentation and code quality                                      |

**Project Structure**

```
spendsense/
├── ingest/         # Synthetic data gen & validation
├── features/       # Signal detection modules
├── personas/       # Persona logic
├── recommend/      # Recommendation engine
├── guardrails/     # Consent, eligibility, tone checks
├── ui/             # Streamlit UIs (user & operator)
├── eval/           # Metrics harness
├── docs/           # Decision logs & schema
├── tests/          # Unit/integration tests
└── data/           # SQLite & Parquet stores
```

**Design Philosophy:**
Local-first, fully auditable, deterministic execution.

---

## **4. Data Generation and Consent Foundation**

### **4.1 Synthetic Temporal Dataset**

**Goal:** Generate 50–100 synthetic users with 6 months of transaction history.

**Schema Requirements:** (Plaid-style structure)

* **Accounts:** `account_id`, `type/subtype`, `balances`, `currency`, `holder_category`
* **Transactions:** `account_id`, `date`, `amount`, `merchant_name`, `payment_channel`, `category`, `pending`
* **Liabilities:** `APR`, `minimum_payment`, `overdue_status`, `next_due_date`

**Generation Logic:**

* `faker` for user and merchant names
* `numpy` for amount distributions (positive/negative cash flows)
* Seeds for deterministic re-generation
* Variable income profiles (high earner, gig worker, student)
* Temporal windowing: 30-day and 180-day rolling metrics

**Demographic Fields (for fairness analysis):**
`age`, `gender`, `income_tier`, `region`

**Outputs:**

```
data/users.sqlite
data/transactions.parquet
data/config.json
```

---

### **4.2 Data Validation and Ingestion**

Modules in `ingest/`:

1. `data_generator.py` → Creates synthetic dataset
2. `validators.py` → Ensures schema compliance and plausible ranges
3. `loader.py` → Loads CSV/JSON to SQLite and Parquet
4. `schemas.py` → Central field definitions and Pydantic models

Each run produces a data-validation report (`docs/schema.md`).

---

### **4.3 Consent Tracking and Data Privacy**

**Objective:** Explicit, revocable user consent for data processing.

**Schema:**

```sql
CREATE TABLE users (
  user_id TEXT PRIMARY KEY,
  name TEXT,
  consent_granted BOOLEAN DEFAULT 0,
  consent_timestamp DATETIME,
  revoked_timestamp DATETIME
);
```

**Flow:**

1. User opens the app → Consent screen shown
2. If `consent_granted = FALSE` → no analysis runs
3. On opt-in → flag TRUE + timestamp
4. On revoke → flag FALSE, archive data

**Rationale:**

* SQLite offers auditable consent history
* Lightweight for MVP, no performance impact
* Meets “explicit opt-in/out” requirement from Peak6 spec 

---

### **4.4 Security and Fairness Foundations**

* **PII:** All names and IDs are synthetic.
* **Fairness:** Demographic fields included only for metric parity checks (not in persona logic).
* **Transparency:** Every user action and recommendation logged with timestamp and data snapshot.
* **Reproducibility:** `seed = 42` used for consistent synthetic data generation.

---

*(End of Part 1 — proceeds to Part 2: Personas and Recommender System)*

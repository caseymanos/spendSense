Excellent — continuing with **Part 2 of 3** for your merged PRD:
**`PRD_V2_Part2_Personas_and_Recommender.md`**

This section continues numbering from Part 1 and focuses on behavioral signals, persona logic, recommendations, guardrails, and the dual-UI design (user vs. operator).

---

# **SpendSense MVP V2 — Part 2: Personas & Recommender System**

## **5. Behavioral Signal Detection**

**Goal:** Identify key behavioral indicators from synthetic Plaid-style transaction data within two rolling windows: **30 days** and **180 days**.

**Core Categories & Signals**

| Category             | Detection Logic                                                                 | Metrics Produced                                                                                   |
| -------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **Subscriptions**    | Identify recurring merchants ≥ 3 in 90 days with monthly/weekly cadence         | • Recurring count  • Recurring spend %  • Avg subscription amount                                  |
| **Savings**          | Net inflow → savings-type accounts (savings, MM, HSA)                           | • Net inflow (Δ balance)  • Growth rate %  • Emergency-fund coverage = savings / avg monthly spend |
| **Credit**           | Balance ÷ limit per account; detect min-payment-only pattern & interest charges | • Utilization % flags (30/50/80)  • Interest presence  • Overdue status                            |
| **Income Stability** | Payroll ACH detection + variance of pay dates/amounts                           | • Median pay gap days  • Std-dev of income  • Cash-flow buffer (months)                            |

**Implementation:**

* Defined in `features/` as modular functions
* Computed via `pandas.groupby(["user_id"])`
* Results stored in `features/signals.parquet`
* Logged decisions → `docs/traces/{user_id}.json`

---

## **6. Persona Assignment System**

**Purpose:** Classify each user into one of five personas based on detected behaviors.

### **6.1 Persona Definitions**

| Persona                          | Criteria                                                                      | Educational Focus                                   |
| -------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------- |
| **1. High Utilization**          | Any card utilization ≥ 50%, interest > 0, min-payment-only, or overdue = true | Debt management basics & autopay education          |
| **2. Variable Income Budgeter**  | Median pay gap > 45 days AND cash-flow buffer < 1 month                       | Variable income budgeting & emergency fund planning |
| **3. Subscription Heavy**        | Recurring merchants ≥ 3 AND (recurring spend ≥ $50 OR ≥ 10 % of total spend)  | Subscription audit & bill-negotiation tips          |
| **4. Savings Builder**           | Savings growth ≥ 2 % OR net inflow ≥ $200 AND utilization < 30 %              | Goal setting & APY optimization                     |
| **5. Custom Persona (Reserved)** | Defined post-MVP                                                              | TBD by operator                                     |

### **6.2 Prioritization Logic**

If a user matches multiple personas:

| Priority | Persona                  | Rationale                              |
| -------- | ------------------------ | -------------------------------------- |
| 1️⃣      | High Utilization         | Immediate credit risk                  |
| 2️⃣      | Variable Income Budgeter | Income stability concerns              |
| 3️⃣      | Subscription Heavy       | Spending efficiency focus              |
| 4️⃣      | Savings Builder          | Positive reinforcement                 |
| 5️⃣      | Custom                   | Applied only if no higher priority met |

```python
persona_priority = [
    "high_utilization",
    "variable_income",
    "subscription_heavy",
    "savings_builder",
    "custom"
]
user_persona = next((p for p in persona_priority if criteria[p]), None)
```

### **6.3 Storage & Outputs**

* Table `personas_assignments` → `user_id`, `persona`, `criteria_met`, `timestamp`
* Decision trace JSON per user (used by operator dashboard)

---

## **7. Recommendation Engine**

**Goal:** Produce 3–5 educational items and 1–3 partner offers per user with plain-language rationales.

### **7.1 Recommendation Structure**

```json
{
  "user_id": "U1234",
  "persona": "high_utilization",
  "recommendations": [
    {
      "type": "education",
      "title": "Lower Credit Utilization",
      "rationale": "Your Visa ending 4523 is at 68% utilization ($3,400 of $5,000). Reducing below 30% may cut $87/mo interest.",
      "disclaimer": "Educational content, not financial advice."
    }
  ]
}
```

### **7.2 Rule-Based Generation**

* `recommend/engine.py` maps persona → education topics and offers.
* Rationale template uses live data values.
* All text validated via tone and eligibility checks.

### **7.3 Eligibility Checks**

| Persona            | Eligible Offer Examples                    |
| ------------------ | ------------------------------------------ |
| High Utilization   | Balance transfer cards, autopay setup apps |
| Variable Income    | Budgeting apps, emergency-fund calculators |
| Subscription Heavy | Subscription audit tools                   |
| Savings Builder    | High-yield savings accounts, CD optimizers |

Offers are excluded if user already holds similar accounts or fails eligibility (min income / credit threshold).

---

## **8. Guardrails & Tone Checks**

**Consent Validation:**
No processing without `consent_granted = TRUE` in SQLite.

**Tone Guardrails:**
Regex-based filters to detect judgmental phrases (“overspending”, “bad habits”).
Replacement phrasing examples:

* “Consider lowering utilization” instead of “You overspent.”
* “Explore automation tools” instead of “You lack discipline.”

**Eligibility Guardrails:**

* Skip offers already owned
* Enforce income minimums
* Exclude predatory products

**Disclosure (Required Footer):**

> *“This is educational content, not financial advice. Consult a licensed advisor for personalized guidance.”*

---

## **9. Dual User Interfaces**

SpendSense MVP V2 implements two Streamlit apps with distinct purposes.

### **9.1 User App (`app_user.py`)**

**Audience:** End users (banking customers).
**Theme:** Educational and supportive.

**Core Views**

1. Consent Onboarding (screen shown until opt-in)
2. Personal Dashboard – Shows active persona + detected patterns + education cards
3. Learning Feed – Short tips, articles, calculators
4. Privacy Settings – View/revoke consent, export own data

### **9.2 Operator Dashboard (`app_operator.py`)**

**Audience:** Analyst / Compliance team.
**Theme:** Analytical and auditable.

**Tabs / Modules**

| Tab                    | Purpose                                       |
| ---------------------- | --------------------------------------------- |
| **Users**              | Filter by consent, persona, fairness segment  |
| **Signals**            | Visualize 30d & 180d metrics                  |
| **Personas**           | View distribution + criteria                  |
| **Recommendations**    | Review text & rationale                       |
| **Decision Traces**    | Inspect JSON for any user                     |
| **Evaluation Summary** | Display key metrics from `/eval/results.json` |

**Operator Actions**

* ✅ **Approve** – Publishes recommendations to user app
* ✏️ **Override/Edit** – Manually adjust persona or content
* 🚩 **Flag for Review** – Marks case for follow-up; recorded in `docs/decision_log.md`

Authentication will be added post-MVP; local-only for now.

---

*(End of Part 2 — continues with Part 3: Evaluation & Quality Assurance.)*

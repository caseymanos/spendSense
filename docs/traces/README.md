# Decision Traces

This directory contains per-user decision trace logs in JSON format.

## Purpose

Decision traces provide complete audit trails for the SpendSense recommendation system. Every recommendation shown to a user is fully traceable back to the underlying data and logic that produced it.

## File Structure

Each file is named `{user_id}.json` and contains a complete decision trace for that user:

```
docs/traces/
├── user_0000.json
├── user_0001.json
├── user_0002.json
└── ...
```

## Trace Contents

Each trace JSON includes:

### 1. User Profile (from PR #1)
- User ID and demographics
- Consent status and timestamps
- Account summaries

### 2. Behavioral Signals (from PR #2)
- **Subscription Detection:** Recurring merchants identified, monthly spend
- **Savings Analysis:** Net inflow, growth rate, emergency fund coverage
- **Credit Signals:** Utilization per card, interest charges, overdue flags
- **Income Stability:** Payroll pattern, median gap, income variability

### 3. Persona Assignment (from PR #3)
- Primary persona assigned
- Criteria met for assignment
- Conflict resolution (if multiple personas matched)
- Assignment timestamp

### 4. Recommendations Generated (from PR #4)
- Educational content items (3-5)
- Partner offers (1-3)
- Rationales for each recommendation
- Data citations (e.g., "Visa ending in 4523 at 68% utilization")

### 5. Guardrail Checks (from PR #5)
- Consent verification
- Eligibility filters applied
- Tone validation results
- Predatory product exclusions

### 6. Evaluation Metadata (from PR #8)
- Generation timestamp
- Latency (milliseconds)
- Coverage flags
- Explainability scores

## Example Trace Structure

```json
{
  "user_id": "user_0042",
  "generated_at": "2025-11-03T18:45:00Z",
  "consent_granted": true,

  "signals": {
    "subscriptions": {
      "recurring_count": 5,
      "monthly_total": 67.94,
      "merchants": ["Netflix", "Spotify", "Amazon Prime", "NYT", "LinkedIn"]
    },
    "credit": {
      "total_utilization": 0.68,
      "accounts": [{
        "account_id": "acc_000123",
        "mask": "4523",
        "utilization": 0.68,
        "balance": 3400.00,
        "limit": 5000.00
      }]
    },
    "savings": {
      "growth_rate": 0.015,
      "net_inflow": 450.00
    },
    "income": {
      "median_gap_days": 14,
      "frequency": "bi_weekly",
      "variability": 0.12
    }
  },

  "persona": {
    "assigned": "high_utilization",
    "criteria_met": ["utilization >= 50%", "interest_charges > 0"],
    "timestamp": "2025-11-03T18:45:01Z"
  },

  "recommendations": [
    {
      "type": "education",
      "title": "Understanding Credit Utilization",
      "rationale": "Your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000 limit). Lowering this below 30% can improve your credit health.",
      "disclaimer": "This is educational content, not financial advice."
    }
  ],

  "guardrails": {
    "consent_check": "passed",
    "eligibility_filters": ["existing_savings < 2"],
    "tone_validation": "passed",
    "excluded_offers": []
  },

  "evaluation": {
    "latency_ms": 243,
    "coverage": true,
    "explainability": 1.0,
    "trace_complete": true
  }
}
```

## Generation Timing

Trace files are generated in the following PRs:

- **PR #2:** Behavioral signals section populated
- **PR #3:** Persona assignment section added
- **PR #4:** Recommendations and full trace generated
- **PR #5:** Guardrails section added
- **PR #8:** Evaluation metadata added

## Usage

### Reading Traces (Operator Dashboard)
The operator dashboard (PR #7) provides a UI to browse and inspect trace files:
- View by user ID
- Filter by persona
- Search by recommendation content
- Export traces for analysis

### Programmatic Access
```python
import json
from pathlib import Path

trace_path = Path("docs/traces/user_0042.json")
with open(trace_path) as f:
    trace = json.load(f)

print(f"User {trace['user_id']} assigned to {trace['persona']['assigned']}")
```

### Compliance & Auditing
These traces serve as the audit trail for:
- Consent verification
- Recommendation justification
- Fairness analysis
- Regulatory compliance

## Privacy & Security

⚠️ **Important:** Even though all data is synthetic for MVP, treat trace files as if they contain real PII:
- Do not commit trace files to git (included in .gitignore)
- Store in secure location if using real data
- Implement access controls for operator dashboard
- Consider encryption at rest for production

## Retention Policy

**MVP:** Traces persist indefinitely for demo purposes

**Production (Future):**
- Retain for 90 days minimum (compliance)
- Archive older traces to cold storage
- Purge upon user data deletion request

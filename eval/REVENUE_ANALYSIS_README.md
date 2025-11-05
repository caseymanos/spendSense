# Multi-Persona Revenue Analysis Tools

This directory contains tools for evaluating the revenue implications of persona priority ordering when users trigger multiple personas simultaneously.

## Overview

The SpendSense system uses a **priority-based** persona assignment system to handle cases where a user's behavioral signals match multiple personas. The current system prioritizes **educational value and user urgency** over revenue optimization.

These tools analyze:
1. **Revenue potential by persona** - Expected revenue per user for each persona
2. **Multi-persona co-occurrence** - How often users trigger multiple personas
3. **Opportunity cost** - Revenue left on the table with current priority order
4. **Priority order comparison** - Educational vs. revenue-optimal vs. hybrid approaches

## Quick Start

### 1. Run Full Revenue Analysis

```bash
uv run python eval/persona_revenue_analysis.py
```

**Output:**
- `eval/persona_revenue_results.json` - Detailed analysis results
- Console output with revenue comparison across priority orders

**What it does:**
- Analyzes all users in `features/signals.parquet`
- Runs each user through all 4 persona checks to find multi-triggers
- Simulates revenue under 4 different priority ordering strategies
- Calculates opportunity cost and revenue lift
- Generates comprehensive JSON results

**Time:** ~5-10 seconds for 100 users

---

### 2. Generate Visualizations

```bash
uv run python eval/persona_revenue_viz.py
```

**Output:**
- `eval/revenue_viz/*.html` - Individual chart HTML files
- `eval/revenue_viz/dashboard.html` - Combined dashboard

**Charts generated:**
1. **Revenue by Persona** - Bar chart showing expected revenue per user by persona
2. **Priority Order Comparison** - Side-by-side comparison of total and per-user revenue
3. **Revenue Lift** - Waterfall chart showing lift from baseline
4. **Persona Distribution** - Pie chart of current persona assignments
5. **Co-Occurrence Heatmap** - Heat map of multi-persona trigger patterns
6. **Opportunity Cost** - Bar chart of top opportunity cost scenarios
7. **LTV Multiplier Impact** - Stacked bar showing base vs. LTV revenue

**Time:** ~3-5 seconds

---

### 3. View Executive Summary

```bash
uv run python eval/persona_revenue_summary.py
```

**Output:**
- Console-based executive summary (no files written)
- Perfect for quick checks and stakeholder presentations

**Sections:**
1. Analysis snapshot (users analyzed, multi-trigger rate)
2. Revenue comparison (current vs. optimal)
3. Opportunity cost breakdown
4. Revenue potential by persona
5. Recommendation (maintain educational order)
6. Scenario analysis (detailed conflict examples)
7. Sensitivity analysis (conversion rate variations)

**Time:** ~1 second

---

## Key Findings (Current Dataset: 100 Users)

| Metric | Value |
|--------|-------|
| **Multi-Persona Trigger Rate** | 4% (4 users) |
| **Current Revenue** | $1,294.92 total / $12.95 per user |
| **Revenue-Optimal Revenue** | $1,399.18 total / $13.99 per user |
| **Revenue Lift** | +$104.26 (+8.1%) |
| **Users Affected** | 1 (1.0%) |
| **Opportunity Cost** | $104.26 |

### Revenue by Persona

| Persona | Expected Revenue/User | Primary Offer |
|---------|---------------------|---------------|
| Savings Builder | $108.00 | Fidelity Go Robo-Advisor (3x LTV multiplier) |
| Variable Income | $16.56 | High-Yield Savings + YNAB |
| High Utilization | $10.50 | 0% Balance Transfer Credit Card |
| Subscription Heavy | $3.74 | Rocket Money Subscription Manager |

### Recommendation

**✅ Maintain Current Educational Priority Order**

**Rationale:**
- Minimal opportunity cost (<$105 total, 8.1% of revenue)
- Affects only 1 user (1.0% of user base)
- Strong ethical positioning (urgency-first protects users with credit strain)
- Regulatory safety (CFPB compliance, fiduciary principles)
- User trust generates long-term value exceeding short-term optimization

---

## File Guide

### Analysis Scripts

| File | Purpose | Runtime | Output |
|------|---------|---------|--------|
| `persona_revenue_analysis.py` | Full revenue simulation | ~5s | JSON results file |
| `persona_revenue_viz.py` | Generate visualizations | ~3s | HTML charts |
| `persona_revenue_summary.py` | Executive summary | ~1s | Console output |

### Output Files

| File | Description |
|------|-------------|
| `persona_revenue_results.json` | Complete analysis results with all scenarios |
| `revenue_viz/dashboard.html` | Combined visualization dashboard |
| `revenue_viz/*.html` | Individual chart files |

### Documentation

| File | Description |
|------|-------------|
| `../docs/persona_revenue_evaluation.md` | Full evaluation report with recommendations |
| `REVENUE_ANALYSIS_README.md` | This file |

---

## Revenue Model Assumptions

### 1. High Utilization
- **Primary Offer:** 0% Balance Transfer Credit Card
- **Revenue per Conversion:** $150
- **Conversion Rate:** 7% (lower due to credit challenges)
- **LTV Multiplier:** 1.0x (one-time transaction)
- **Expected Revenue/User:** $10.50

**Rationale:**
- Credit card affiliate commissions are high ($100-300)
- But users with high utilization have lower approval rates
- No ongoing revenue (user pays off debt and closes account)

---

### 2. Variable Income
- **Primary Offer:** Marcus High-Yield Savings + YNAB Budgeting App
- **Revenue per Conversion:** $100 (savings account) + $15 (YNAB)
- **Conversion Rate:** 12%
- **LTV Multiplier:** 1.2x (ongoing deposit value)
- **Expected Revenue/User:** $16.56

**Rationale:**
- Deposit account opening bonuses ($50-150)
- App subscription affiliate revenue ($10-50)
- Ongoing interest spread from deposits (1.2x multiplier)

---

### 3. Subscription Heavy
- **Primary Offer:** Rocket Money Subscription Manager
- **Revenue per Conversion:** $20
- **Conversion Rate:** 17% (highest - immediate cost-saving value)
- **LTV Multiplier:** 1.1x
- **Expected Revenue/User:** $3.74

**Rationale:**
- Consumer app referrals are low value ($10-50)
- High conversion due to clear ROI (save $30/month on subscriptions)
- Minimal ongoing revenue

---

### 4. Savings Builder
- **Primary Offer:** Fidelity Go Robo-Advisor + Ally Savings Account
- **Revenue per Conversion:** $200 (investment account) + $100 (savings account)
- **Conversion Rate:** 12%
- **LTV Multiplier:** 3.0x (ongoing AUM fees)
- **Expected Revenue/User:** $108.00

**Rationale:**
- Investment account openings are high value ($100-300)
- Ongoing AUM fees (0.35% annually on growing balances)
- Users with proven savings behavior = high quality, long-term value
- 3-year LTV: $200 + $100 (initial) + $315 (AUM fees over 3 years) = $615
- LTV Multiplier: $615 / ($200 + $100) = ~3.0x

---

## Priority Orders Evaluated

### 1. Current Educational (Baseline)
```
Priority: High Utilization → Variable Income → Subscription Heavy → Savings Builder
```
- **Philosophy:** Help users with urgent needs first
- **Total Revenue:** $1,294.92
- **Rationale:** Credit strain is more urgent than investment opportunities

### 2. Revenue-Optimal
```
Priority: Savings Builder → High Utilization → Variable Income → Subscription Heavy
```
- **Philosophy:** Maximize lifetime value
- **Total Revenue:** $1,399.18 (+8.1%)
- **Rationale:** Savings Builder has 10x higher LTV than other personas

### 3. Hybrid Balanced
```
Priority: High Utilization → Savings Builder → Variable Income → Subscription Heavy
```
- **Philosophy:** Urgency first, then revenue
- **Total Revenue:** $1,399.18 (+8.1%)
- **Rationale:** Preserve urgency-first for credit strain, elevate Savings Builder for others

### 4. LTV-Optimal
```
Priority: Savings Builder → Variable Income → High Utilization → Subscription Heavy
```
- **Philosophy:** Maximize long-term value with LTV multipliers
- **Total Revenue:** $1,399.18 (+8.1%)
- **Rationale:** LTV multipliers compound over time (Savings Builder 3.0x, Variable Income 1.2x)

---

## Multi-Persona Co-Occurrence Patterns

### Most Common Combinations (4% of users trigger multiple)

1. **High Utilization + Subscription Heavy** (3 users, 75% of multi-trigger)
   - **Conflict:** High utilization wants debt paydown, subscriptions want cost-cutting
   - **Current Winner:** High Utilization (urgency-first)
   - **Revenue Impact:** Minimal (both low LTV)

2. **Savings Builder + Subscription Heavy** (1 user, 25% of multi-trigger)
   - **Conflict:** Savings Builder wants investment, subscriptions want cost-cutting
   - **Current Winner:** Subscription Heavy
   - **Revenue Impact:** HIGH ($104 opportunity cost)
   - **User:** user_0033 (the only user driving revenue loss)

### Why Low Multi-Trigger Rate?

Personas are **designed to be mutually exclusive**:
- High Utilization requires utilization ≥50% **OR** interest charges
- Savings Builder requires utilization <30% **AND** savings growth
- Variable Income requires cash buffer <1 month **AND** pay gap >45 days
- Subscription Heavy requires 3+ recurring merchants

Only **conflicting edge cases** (like user_0033 with both subscriptions AND savings) trigger multiple personas.

---

## Sensitivity Analysis

### How Conversion Rates Affect Results

| Scenario | Savings Builder | High Utilization | Revenue Gap |
|----------|----------------|------------------|-------------|
| Current (12%, 7%) | $108.00 | $10.50 | 10.3x |
| Conservative (-20%) | $86.40 | $8.40 | 10.3x |
| Optimistic (+20%) | $129.60 | $12.60 | 10.3x |

**Key Finding:** Even with ±20% conversion rate changes, Savings Builder remains 10x more valuable due to **LTV multiplier** (3.0x vs 1.0x).

---

## Ethical Considerations

### Why Educational Order Matters

1. **Urgency First**
   - High Utilization users face immediate financial risk (interest charges, credit score damage)
   - Showing investment offers to users with credit card debt could be harmful
   - Educational order prioritizes solving urgent problems first

2. **Fiduciary Principles**
   - Revenue-first could conflict with user's best interest
   - Example: User with 60% utilization + $200 savings inflow
     - Revenue-optimal: Show Fidelity Go ($108 revenue)
     - Educational-optimal: Show balance transfer card ($10.50 revenue)
     - **User's best interest:** Pay down high-interest debt before investing

3. **Regulatory Safety**
   - Financial product recommendations face CFPB oversight
   - Priority order must be defensible as user-first, not profit-first
   - Educational approach provides clear rationale for all recommendations

4. **User Trust**
   - Users who feel prioritized over profit are more likely to:
     - Follow through on recommendations (higher conversion)
     - Return to the platform (higher retention)
     - Recommend to others (viral growth)
   - **Long-term revenue** may exceed short-term optimization

---

## Scaling Projections

### Extrapolation to Larger User Base

| User Base | Multi-Trigger (4%) | Affected Users (1%) | Opportunity Cost |
|-----------|-------------------|---------------------|------------------|
| 100 | 4 | 1 | $104 |
| 1,000 | 40 | 10 | $1,043 |
| 10,000 | 400 | 100 | $10,426 |
| 100,000 | 4,000 | 1,000 | $104,260 |

**Note:** Assumes linear scaling with same persona distribution. Actual results may vary with:
- Different demographic mix
- Regional variations
- Seasonal behavior changes
- Product availability changes

---

## Integration with Main Evaluation Harness

The revenue analysis is designed as a **standalone tool** separate from the main technical evaluation harness (`eval/run.py`), which focuses on:
- Coverage, explainability, relevance, latency, auditability
- Fairness and demographic parity

**Why separate?**
- Revenue analysis is **business-focused**, not technical quality
- Not all stakeholders need revenue data
- Allows independent iteration on revenue modeling
- Keeps evaluation harness focused on product quality metrics

**To run together:**
```bash
# Run technical evaluation
uv run python -m eval.run

# Run revenue analysis
uv run python eval/persona_revenue_analysis.py

# View combined insights
uv run python eval/persona_revenue_summary.py
```

---

## Updating Revenue Assumptions

To update revenue model assumptions, edit `eval/persona_revenue_analysis.py`:

```python
PERSONA_REVENUE_MODEL = {
    "high_utilization": {
        "revenue_per_conversion": 150,  # ← Update based on actual affiliate rates
        "conversion_rate": 0.07,        # ← Update based on A/B test results
        "ltv_multiplier": 1.0,          # ← Update based on retention data
    },
    # ... other personas
}
```

Then re-run the analysis and regenerate visualizations.

---

## FAQ

### Q: Should we change the priority order to maximize revenue?

**A:** No. The current educational order leaves only 8.1% revenue on the table ($104 on 100 users) while providing strong ethical positioning, regulatory safety, and user trust. The long-term value of user trust likely exceeds the short-term revenue optimization.

### Q: What if multi-trigger rate increases above 10%?

**A:** Monitor multi-trigger rates over time. If it rises above 10% or opportunity cost exceeds 20% of revenue, consider the **hybrid balanced order** that preserves urgency-first while elevating Savings Builder.

### Q: How accurate are these revenue projections?

**A:** These are **modeled estimates** based on industry averages. Actual revenue depends on:
- Specific affiliate agreements
- User conversion behavior
- Product availability
- Competitive landscape
- Regulatory changes

Use these as **directional guidance**, not precise forecasts. Validate with A/B tests once live.

### Q: Can we show BOTH personas' recommendations to multi-trigger users?

**A:** Interesting idea! This would mean:
- **Pros:** Capture full revenue potential, give users choice
- **Cons:** More cognitive load, longer recommendation lists, potential confusion
- **Implementation:** Requires UI/UX redesign to present dual-persona recommendations

This is a future enhancement opportunity worth exploring.

---

## Contact

- **Project Lead:** Casey Manos
- **Technical Spec Origin:** Bryce Harris (bharris@peak6.com)
- **Revenue Analysis:** Generated 2025-11-05

For questions or updates to revenue modeling assumptions, see `docs/persona_revenue_evaluation.md`.

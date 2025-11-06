# SpendSense Persona Recommendation System - Complete Analysis

## Executive Summary

SpendSense uses a **priority-based persona assignment system** that classifies users into 5 behavioral personas based on detected financial signals. Each persona receives 3-5 educational recommendations and 1-3 partner offers, with every recommendation including a data-driven rationale and explicit disclaimers.

The system follows this flow:
1. **Feature Detection** → Extract behavioral signals from transaction/account data
2. **Persona Assignment** → Classify users using priority-ordered logic
3. **Recommendation Selection** → Retrieve persona-specific content
4. **Eligibility Filtering** → Apply guardrails and tone validation
5. **Rationale Injection** → Populate templates with actual user data
6. **Output & Tracing** → Return recommendations with complete audit trail

---

## Part 1: Behavioral Signal Detection

### Overview
Before persona assignment, the system detects 4 categories of behavioral signals:

**Time Windows:** 30-day (short-term) and 180-day (long-term) rolling windows

### 1.1 Credit Utilization Signals (`features/credit.py`)

**What it measures:**
- Current credit card balance vs. limit across all cards
- Interest charges and liability patterns
- Payment behavior (minimum-only vs. full payoff)
- Overdue status

**Key Metrics:**
- `credit_max_util_pct` - Highest utilization across cards (0-100%)
- `credit_avg_util_pct` - Average utilization across cards
- `credit_flag_30` - Any card ≥30% utilized
- `credit_flag_50` - Any card ≥50% utilized  
- `credit_flag_80` - Any card ≥80% utilized
- `credit_interest_charges` - Any interest charges posted (boolean)
- `credit_min_payment_only` - Last payment ≈ minimum payment (within 5%)
- `credit_is_overdue` - Any overdue amounts
- `credit_num_cards` - Total number of credit cards

**Detection Method:**
- Analyzes accounts table for credit cards
- Calculates utilization: (balance_current / balance_limit) × 100
- Checks liabilities table for payment patterns and interest

---

### 1.2 Income Stability Signals (`features/income.py`)

**What it measures:**
- Frequency and consistency of paychecks
- Gaps between income deposits
- Cash flow buffer (months of expenses covered)
- Income variability

**Key Metrics (180-day window):**
- `inc_180d_median_pay_gap_days` - Median days between paychecks
- `inc_180d_income_variability` - Coefficient of variation in paycheck amounts
- `inc_180d_cash_buffer_months` - Months of expenses covered by checking balance
- `inc_180d_pay_frequency` - "weekly" | "biweekly" | "monthly" | "variable"
- `inc_180d_num_paychecks` - Count of detected income deposits
- `inc_180d_avg_paycheck` - Average paycheck amount

**Detection Method:**
- Identifies payroll transactions: negative amounts (credits) with keywords: "payroll", "direct dep", "salary", "wages"
- Also scans personal_finance_category for "INCOME" or "TRANSFER_IN"
- Requires minimum 2 occurrences to establish pattern
- Calculates gaps between deposit dates
- Detects frequency within ±3 days tolerance

**Cash Buffer Calculation:**
- Current checking balance ÷ Average monthly expenses
- Average monthly expenses = (total debits over window) × (30 / window_days)

---

### 1.3 Subscription/Recurring Spend Signals (`features/subscriptions.py`)

**What it measures:**
- Recurring monthly charges (streaming, apps, memberships)
- How many subscriptions user maintains
- Total monthly spend on subscriptions
- Subscription as % of total spending

**Key Metrics (180-day window):**
- `sub_180d_recurring_count` - Number of distinct recurring merchants
- `sub_180d_monthly_spend` - Estimated monthly subscription spend (normalized to 30 days)
- `sub_180d_share_pct` - Subscriptions as % of total spend

**Detection Method:**
- Groups transactions by merchant
- Requires: ≥3 occurrences within 90-day lookback window
- Amount consistency check: standard deviation / mean ≤ 10%
- Time span check: occurrences must be spread within analysis horizon
- Calculates monthly average: total_spend × (30 / window_days)
- Calculates share: (subscription_spend / total_spend) × 100

**Example:**
- Netflix ($15.99), Spotify ($9.99), Amazon Prime ($14.99) = 3 merchants detected
- Monthly spend = $40.97
- If total spending = $2,000/month → share = 2.0%

---

### 1.4 Savings Signals (`features/savings.py`)

**What it measures:**
- Money flowing into savings accounts
- Growth rate of savings balance
- Emergency fund coverage (months of expenses)

**Key Metrics (180-day window):**
- `sav_180d_net_inflow` - Net money deposited to savings accounts
- `sav_180d_growth_rate_pct` - Percentage growth: (current - beginning) / beginning × 100
- `sav_180d_emergency_fund_months` - Current savings ÷ avg monthly expenses
- `sav_180d_balance` - Current total savings balance

**Detection Method:**
- Finds all savings accounts (account_type="depository", account_subtype="savings")
- Calculates net inflow: deposits - withdrawals
- Growth rate: (current_balance - beginning_balance) / beginning_balance × 100
  - Beginning balance estimated as: current - net_inflow
- Emergency fund: current_savings ÷ (total_expenses × (30 / window_days))

---

## Part 2: Persona Assignment Logic

### Priority Order for Conflict Resolution

When a user matches multiple personas, the system applies this **strict priority order**:

```
Priority 1: High Utilization (immediate financial strain)
Priority 2: Variable Income Budgeter (income stability)
Priority 3: Subscription-Heavy (spending optimization)
Priority 4: Cash Flow Optimizer (cash flow management - NEW in recent commit)
Priority 5: Savings Builder (positive reinforcement)
Priority 6: General (default fallback)
```

### 2.1 Priority 1: High Utilization Persona

**Who matches:**
Users with ANY of these conditions:
- Credit utilization ≥ 50% (on any card), OR
- Interest charges posted > $0, OR
- Minimum payment-only pattern detected, OR
- Overdue status = true

**Threshold:**
```python
utilization_threshold: 50.0  # percentage
```

**Rationale:**
Immediate financial strain requires priority attention. High utilization indicates debt burden and carries high interest costs.

**Example User:**
- Credit card at 68% utilization ($3,400 of $5,000 limit)
- Paying $87 in monthly interest
- Assigned to: **High Utilization**

---

### 2.2 Priority 2: Variable Income Budgeter Persona

**Who matches:**
Users with BOTH conditions (AND logic):
- Median pay gap > 45 days (180-day window), AND
- Cash buffer < 1 month (180-day window)

**Thresholds:**
```python
median_pay_gap_days: 45
cash_buffer_months: 1.0
```

**Rationale:**
Income instability combined with low savings creates planning challenges. These users need adaptive budgeting tools.

**Example User:**
- Receives paychecks every 50 days (freelancer/contractor)
- Has $2,500 in checking account
- Monthly expenses average $3,800
- Cash buffer = 2,500 / 3,800 = 0.66 months < 1 month
- Assigned to: **Variable Income Budgeter**

---

### 2.3 Priority 3: Subscription-Heavy Persona

**Who matches:**
Users with BOTH conditions (AND logic):
- Recurring merchant count ≥ 3, AND
- (Monthly subscription spend ≥ $50 OR subscription share ≥ 10%)

**Thresholds:**
```python
min_recurring_count: 3
recurring_spend_min: 50.0  # dollars
recurring_spend_pct: 10.0  # percentage
```

**Rationale:**
Multiple subscriptions present opportunity for cost optimization and fraud/waste detection.

**Example User:**
- Detected subscriptions: Netflix, Spotify, Amazon Prime, Hulu (4 merchants)
- Monthly subscription spend: $47.95
- Total monthly spend: $2,100
- Subscription share: 2.3%
- ✓ Recurring count (4) ≥ 3
- ✓ Monthly spend ($47.95) < $50 but share (2.3%) < 10%
- Result: Does NOT match (needs spend ≥$50 OR share ≥10%)

**Alternative Example (matches):**
- 6 subscriptions: streaming, apps, cloud storage, fitness, music, tools
- Monthly subscription spend: $145
- Total spend: $1,500
- Subscription share: 9.7%
- ✓ Recurring count (6) ≥ 3
- ✓ Monthly spend ($145) ≥ $50
- Assigned to: **Subscription-Heavy**

---

### 2.4 Priority 4: Cash Flow Optimizer Persona

**Who matches:**
Users with ALL three conditions (AND logic):
- Cash buffer < 2 months, AND
- (Savings growth rate < 1% OR net inflow < $100), AND
- Pay gap ≤ 45 days (stable income - differentiates from Variable Income)

**Thresholds:**
```python
max_cash_buffer_months: 2.0
max_growth_rate_pct: 1.0
max_net_inflow: 100.0
max_pay_gap_days: 45
```

**Rationale:**
These users have stable income but are spending at or above their means. They need help optimizing cash flow and preventing overspending patterns.

**Key Distinction from Variable Income:**
- Variable Income: unstable income (gap > 45 days) + low buffer
- Cash Flow Optimizer: stable income (gap ≤ 45 days) + low buffer + poor savings growth

**Example User:**
- Regular biweekly paychecks (pay gap = 14 days) ✓ stable
- Checking balance: $1,200, monthly expenses: $700
- Cash buffer: 1.2 / 0.7 = 1.7 months < 2 months ✓
- Savings growth over 180 days: 0.5% < 1% ✓
- Net inflow to savings: $45 < $100 ✓
- Assigned to: **Cash Flow Optimizer**

---

### 2.5 Priority 5: Savings Builder Persona

**Who matches:**
Users with ALL conditions (AND logic):
- (Savings growth rate ≥ 2% OR net inflow ≥ $200), AND
- Credit utilization < 30%

**Thresholds:**
```python
growth_rate_pct: 2.0
net_inflow_min: 200.0
max_utilization: 30.0
```

**Rationale:**
Positive savings behavior with low credit strain indicates responsible financial health. These users benefit from encouragement and growth strategies.

**Example User:**
- Net inflow to savings over 180 days: $3,200 > $200 ✓
- Credit utilization: 18% < 30% ✓
- Assigned to: **Savings Builder**

---

### 2.6 Priority 6: General Persona

**Who matches:**
Users that don't meet criteria for any specific persona.

**Rationale:**
Insufficient behavioral signals to warrant persona-specific recommendations.

**What they receive:**
Empty recommendations list with message: "You're doing great - no recommendations at this time."

---

## Part 3: Persona-to-Recommendation Mapping

### 3.1 High Utilization Content

**5 Educational Items:**
1. "Understanding Credit Utilization and Your Score"
   - Rationale: "Your Visa ending in 4523 is at {utilization_pct}% utilization ({balance} of {limit}). Reducing below 30% could improve your credit score and may reduce interest charges of approximately {monthly_interest}."

2. "Debt Avalanche vs. Debt Snowball"
   - Rationale: "With {num_cards} credit cards and total utilization of {avg_utilization_pct}%, a structured paydown plan could save you hundreds in interest."

3. "Setting Up Autopay to Avoid Late Fees and Interest"
   - Rationale: "Automating your credit card payments can help you avoid late fees. With {num_cards} cards to manage, automation reduces mental overhead."

4. "How Interest Charges Work: APR, Compounding, and Grace Periods"
   - Rationale: "You're currently paying approximately {monthly_interest} per month in interest charges."

5. "Balance Transfer Cards: When They Help and When They Hurt"
   - Rationale: "With your current utilization of {avg_utilization_pct}%, a 0% balance transfer could save you {estimated_savings} over 12-18 months."

**Partner Offers (1-3):**
- Balance transfer credit card offers
- 0% APR offers
- Debt consolidation services

---

### 3.2 Variable Income Budgeter Content

**5 Educational Items:**
1. "Percentage-Based Budgeting for Variable Income"
   - Rationale: "Your income varies with a median gap of {pay_gap_days} days between paychecks. Percentage budgeting adapts to fluctuations automatically."
   - Partner equivalent: YNAB budgeting app

2. "Building an Emergency Fund on Irregular Income"
   - Rationale: "With {cash_buffer_months} months of expenses saved, you're building a safety net."
   - Partner equivalent: Marcus HYSA

3. "Income Smoothing: Creating Your Own Paycheck"
   - Rationale: "Your pay gap of {pay_gap_days} days makes traditional budgeting challenging."

4. "Tax Planning for Freelancers and Gig Workers"
   - Rationale: "With variable income averaging {avg_paycheck} per payment, setting aside 25-30% for taxes protects you."
   - Partner equivalent: Keeper Tax

5. "Cash Flow Buffer Calculator"
   - Rationale: "Your current buffer of {cash_buffer_months} months provides some cushion."

**Partner Offers:**
- YNAB (You Need A Budget)
- Marcus High-Yield Savings
- Keeper Tax
- Wave Accounting

---

### 3.3 Subscription-Heavy Content

**5 Educational Items:**
1. "The Complete Subscription Audit Checklist"
   - Rationale: "You have {recurring_count} recurring subscriptions totaling approximately {monthly_recurring_spend} per month. A quarterly audit can identify unused services."
   - Partner equivalent: Rocket Money/Trim

2. "Negotiating Better Rates on Bills and Subscriptions"
   - Rationale: "With subscriptions making up {subscription_share_pct}% of your spending, negotiating just 2-3 services could save $10-30/month."
   - Partner equivalent: Trim

3. "Subscription Sharing: Ethical Ways to Split Costs"
   - Rationale: "Your {monthly_recurring_spend}/month in subscriptions could be reduced 30-50% through family plan sharing."

4. "Free Alternatives to Popular Paid Subscriptions"
   - Rationale: "Some of your {recurring_count} subscriptions may have free alternatives that meet 80% of your needs."
   - Eligibility: min_recurring_count ≥ 4

5. "Setting Up Bill Alerts to Catch Price Increases"
   - Rationale: "With {recurring_count} active subscriptions, alerts help you catch price changes quickly."
   - Eligibility: min_recurring_count ≥ 3

**Partner Offers:**
- Rocket Money (subscription manager)
- Trim (bill negotiator)
- Truebill subscription tracking

---

### 3.4 Cash Flow Optimizer Content

**4 Educational Items:**
1. "The Zero-Based Budget: Giving Every Dollar a Job"
   - Rationale: "With {cash_buffer_months} months of cash buffer, zero-based budgeting can help you allocate income more intentionally."
   - Partner equivalent: Budgeting apps

2. "Tracking Discretionary Spending: Where Does the Money Go?"
   - Rationale: "Understanding where your money goes is the first step to improving cash flow."
   - Partner equivalent: Mint/YNAB

3. "The 24-Hour Rule: Curbing Impulse Purchases"
   - Rationale: "Small behavioral changes can significantly improve your cash buffer over time."

4. "Building a Cash Buffer: The First $1000"
   - Rationale: "Your current buffer of {cash_buffer_months} months can be strengthened with focused savings."
   - Partner equivalent: HYSA offers

**Partner Offers:**
- High-yield savings accounts
- Budgeting apps (YNAB, Mint)
- Expense tracking tools

---

### 3.5 Savings Builder Content

**3 Educational Items:**
1. "Advanced Savings Strategies Beyond Emergency Fund"
   - Rationale: "Your savings are growing at {growth_rate_pct}% with net inflow of {net_inflow}. Build on this momentum."

2. "CD Laddering: Earning Higher Rates on Certificates of Deposit"
   - Rationale: "With {emergency_fund_months} months of emergency fund covered, consider allocating extra savings to CDs for higher yields."
   - Partner equivalent: CD accounts
   - Eligibility: emergency_fund_months ≥ 6

3. "Investment Account Basics: Building Wealth Beyond Savings"
   - Rationale: "Your emergency fund of {emergency_fund_months} months puts you in position to invest for long-term wealth."
   - Eligibility: emergency_fund_months ≥ 5

**Partner Offers:**
- High-yield savings accounts (Marcus, Ally)
- CD account offerings
- Investment account openings (Fidelity, Vanguard robo-advisors)

---

## Part 4: Recommendation Generation Flow

### Step 1: Load User Context
```
Inputs: user_id
Outputs: {
  user_id, persona, consent_granted, income_tier,
  signals (behavioral metrics),
  accounts (current holdings),
  recent_transactions (last 30 days),
  criteria_met (persona matching conditions)
}
```

**Consent Check:**
If `consent_granted = FALSE` → Return empty recommendations with message: "Consent not granted. Opt in from your profile to unlock personalized guidance."

**Persona Check:**
If `persona = "general"` or `persona = NULL` → Return empty recommendations with message: "You're doing great - no recommendations at this time."

---

### Step 2: Select Education Items (3-5 items)

**Process:**
1. Load all education items for the persona from content_catalog.py
2. Filter by eligibility criteria (e.g., min_utilization, min_recurring_count)
3. Score each eligible item by relevance (0-100 scale)
4. Sort by score descending
5. Select top items (up to max of 5, minimum 3)

**Scoring Rules:**

**Credit Category (utilization-based):**
- Base score: 50
- Max util > 70% → +30 (critical urgency)
- Max util > 50% → +20 (high urgency)
- Max util > 30% → +10 (moderate urgency)
- Estimate monthly interest from cards → +up to 15 points

**Subscription Category:**
- Base score: 50
- Recurring count ≥ 6 → +20
- Recurring count ≥ 4 → +10
- Monthly spend > $200 → +15
- Monthly spend > $100 → +10
- Share > 15% → +10

**Savings Category:**
- Base score: 50
- Net inflow > $2,000 → +20
- Net inflow > $1,000 → +15
- Net inflow > $500 → +10
- Growth rate > 5% → +10
- Growth rate > 3% → +5
- Emergency fund ≥ 6 months + CD topic → +15
- Emergency fund ≥ 5 months + investment topic → +10

**Income/Budgeting Category:**
- Base score: 50
- Pay gap > 45 days → +25
- Pay gap > 35 days → +15
- Pay gap > 30 days → +10
- Cash buffer < 2 months (emergency fund content) → +20
- Cash buffer < 4 months → +10

---

### Step 3: Select Partner Offers (1-3 offers)

**Process:**
1. Load all partner offers for the persona
2. Filter out predatory products (payday loans, title loans, etc.)
3. Filter by eligibility criteria
4. Score for relevance (same logic as education)
5. Select top offers (up to max of 3, minimum 1)

**Eligibility Rules Applied:**
- `min_income_tier`: User's tier must be ≥ required tier
- `exclude_existing`: Don't offer if user already has this account type
- `max_existing_savings_accounts`: Don't exceed limit if already have type
- `min_utilization` / `max_utilization`: Credit util bounds
- `min_recurring_count`: Subscription requirement
- `min_net_inflow`: Savings requirement
- `min_emergency_fund_months`: Emergency fund threshold

---

### Step 4: Deduplication and Diversity

**Rules:**
1. If education item has `partner_equivalent: true` AND a partner offer exists with same topic → **Remove the education item** (keep actionable offer)
2. Max 2 items per category across education + offers combined
3. Process offers first (higher priority), then education items

**Example:**
- Education: "Setting Up Autopay" (partner_equivalent: true, topic: autopay)
- Offer: "Autopay Service Pro" (topic: autopay)
- Result: Remove education item, keep offer

---

### Step 5: Format Rationales

**Template Injection:**
Each recommendation has a `rationale_template` with placeholders:

**Credit-related placeholders:**
- `{card_description}` → "Visa ending in 4523"
- `{utilization_pct}` → "68"
- `{balance}` → "$3,400"
- `{limit}` → "$5,000"
- `{avg_utilization_pct}` → "52"
- `{num_cards}` → "3"
- `{monthly_interest}` → "$87/month"
- `{estimated_savings}` → "$1,200"

**Income-related:**
- `{pay_gap_days}` → "50"
- `{cash_buffer_months}` → "0.66"
- `{avg_paycheck}` → "$2,450"

**Subscription-related:**
- `{recurring_count}` → "5"
- `{monthly_recurring_spend}` → "$87.95"
- `{subscription_share_pct}` → "4.2"

**Savings-related:**
- `{net_inflow}` → "$3,200"
- `{growth_rate_pct}` → "2.5"
- `{emergency_fund_months}` → "4.5"

**Example:** 
Template: "Your {card_description} is at {utilization_pct}% utilization. Reducing below 30% could save {monthly_interest}."

Output: "Your Visa ending in 4523 is at 68% utilization. Reducing below 30% could save $87/month."

---

### Step 6: Tone Validation

**Prohibited Phrases:**
- "overspending"
- "bad habits"
- "lack discipline"
- "irresponsible"
- "wasteful"
- "poor choices"
- "financial mistakes"
- "careless"

**Preferred Alternatives:**
- "overspending" → "consider reducing spending"
- "bad habits" → "habits to optimize"
- "lack discipline" → "explore automation tools"
- "irresponsible" → "opportunities to improve"
- "wasteful" → "areas to optimize"
- "poor choices" → "decisions to revisit"
- "financial mistakes" → "learning opportunities"
- "careless" → "attention to detail"

---

### Step 7: Append Mandatory Disclaimer

**Every recommendation gets:**
"This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."

---

### Step 8: Build Response

**Response Structure:**
```json
{
  "user_id": "user_0042",
  "persona": "high_utilization",
  "recommendations": [
    {
      "type": "education",
      "title": "Understanding Credit Utilization and Your Score",
      "description": "Learn how credit utilization affects your credit score...",
      "category": "credit_basics",
      "topic": "credit_utilization",
      "rationale": "Your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000). Reducing below 30% could improve your credit score and may reduce interest charges of approximately $87/month.",
      "disclaimer": "This is educational content, not financial advice..."
    },
    {
      "type": "partner_offer",
      "title": "0% APR Balance Transfer Card",
      "description": "Consolidate high-interest balances...",
      "category": "debt_paydown",
      "topic": "balance_transfer",
      "rationale": "With your current utilization of 52%, a 0% balance transfer could save you $1,200 over 12-18 months.",
      "disclaimer": "This is educational content, not financial advice..."
    }
  ],
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "education_count": 4,
    "offer_count": 2,
    "total_count": 6,
    "tone_check_passed": true,
    "tone_violations_count": 0,
    "consent_granted": true
  }
}
```

---

## Part 5: Complete Data Flow Example

### User Profile:
- user_0042
- Consent granted: YES
- Income tier: medium

### Step 1: Feature Detection
Signals computed from 180-day data:
```python
signals = {
  "credit_max_util_pct": 68.0,
  "credit_avg_util_pct": 52.0,
  "credit_num_cards": 3,
  "credit_interest_charges": True,  # $87/month
  "inc_180d_median_pay_gap_days": 14,  # Biweekly
  "inc_180d_cash_buffer_months": 2.4,
  "sub_180d_recurring_count": 2,  # Netflix, Spotify
  "sub_180d_monthly_spend": 25.98,
  "sub_180d_share_pct": 1.2,
  "sav_180d_net_inflow": 450.0,
  "sav_180d_growth_rate_pct": 3.2,
}
```

### Step 2: Persona Assignment
Persona priority check:
1. High Utilization? → `credit_max_util_pct (68) >= 50` ✓ AND `interest_charges = True` ✓ → **MATCHES**
2. Return "High Utilization" (priority 1 wins)

### Step 3: Education Selection
All high_utilization items scored:
1. "Credit Utilization 101" → Score 90 (high utilization + interest)
2. "Debt Avalanche vs Snowball" → Score 88 (multiple cards, high avg util)
3. "Autopay Setup" → Score 85
4. "Interest Charges Explained" → Score 87
5. "Balance Transfer Guide" → Score 89

Select top 4 (after dedup/diversity): #1, #2, #3, #5

### Step 4: Partner Offer Selection
All offers scored:
1. "0% APR Balance Transfer Card" → Score 95 (high savings potential)
2. "Debt Consolidation Loan" → Score 78 (lower score)

Eligibility check: Income tier medium ≥ required, existing cards < max → **Select #1**

Select 1 offer: #1

### Step 5: Rationale Injection
Template: "Your {card_description} is at {utilization_pct}% utilization ({balance} of {limit}). Reducing below 30% could improve your credit score and may reduce interest charges of approximately {monthly_interest}."

Replacements:
- {card_description} = "Visa ending in 4523"
- {utilization_pct} = "68"
- {balance} = "$3,400"
- {limit} = "$5,000"
- {monthly_interest} = "$87/month"

Output: "Your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000). Reducing below 30% could improve your credit score and may reduce interest charges of approximately $87/month."

### Step 6: Final Response
```json
{
  "user_id": "user_0042",
  "persona": "High Utilization",
  "recommendations": [
    {
      "type": "education",
      "title": "Understanding Credit Utilization and Your Score",
      "rationale": "Your Visa ending in 4523 is at 68% utilization...",
      "disclaimer": "This is educational content, not financial advice..."
    },
    ...
  ],
  "metadata": {
    "total_count": 5,
    "education_count": 4,
    "offer_count": 1,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Step 7: Tracing
Saved to `docs/traces/user_0042.json`:
```json
{
  "user_id": "user_0042",
  "persona_assignment": {
    "persona": "High Utilization",
    "criteria_met": {
      "high_utilization": 68.0,
      "interest_charges": true
    }
  },
  "recommendations": {
    "persona": "High Utilization",
    "education_count": 4,
    "offer_count": 1,
    "total_recommendations": 5,
    "recommendations": [...]
  }
}
```

---

## Part 6: Guardrails and Filters

### 6.1 Consent Enforcement
- All processing blocked if `consent_granted = FALSE`
- Users can opt-in/opt-out from UI
- Consent timestamps tracked in SQLite

### 6.2 Eligibility Filters
Applied before returning recommendations:

**Credit Products:**
- Exclude if max utilization > 80%
- Income tier minimum (medium or high)

**Savings Products:**
- Exclude if user already has 2+ savings accounts
- Available to all income tiers

**Predatory Product Blocking:**
- Payday loans
- Title loans
- Rent-to-own schemes
- High-fee checking (>$15/month)

### 6.3 Tone Validation
Scans all recommendations for shaming language. If violations detected:
- Logged to trace file for operator review
- Recommendations still returned (warnings for human review)

### 6.4 Fairness Tracking
Monitors demographic parity (±10% target):
- Age distribution of personas
- Gender distribution
- Income tier distribution
- Regional distribution

---

## Summary Table: Persona Characteristics

| Persona | Trigger Signals | Priority | Content Focus | Example |
|---------|-----------------|----------|---------------|---------| 
| **High Utilization** | Util ≥50% OR interest OR overdue | 1 | Debt paydown, credit management | 68% utilization, paying $87/mo interest |
| **Variable Income** | Pay gap >45d AND buffer <1mo | 2 | Adaptive budgeting, emergency fund | Freelancer, 50-day gaps, $700 buffer |
| **Subscription-Heavy** | ≥3 recurring AND (spend≥$50 OR share≥10%) | 3 | Subscription optimization, cost negotiation | 6 subscriptions, $145/mo, 9.7% of spend |
| **Cash Flow Optimizer** | Buffer <2mo AND (growth<1% OR inflow<$100) AND gap≤45d | 4 | Spending analysis, impulse control, cash building | Biweekly income, $1.2k buffer, 0.5% growth |
| **Savings Builder** | (Growth≥2% OR inflow≥$200) AND util<30% | 5 | Advanced savings, growth strategies, investments | 3.2% growth, 18% util, positive inflows |
| **General** | None of above | 6 | None (default) | Minimal signals detected |

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `personas/assignment.py` | Persona assignment logic + priority order |
| `ingest/constants.py` | All threshold values (single source of truth) |
| `features/credit.py` | Credit utilization signal detection |
| `features/income.py` | Income stability signal detection |
| `features/subscriptions.py` | Subscription/recurring spend detection |
| `features/savings.py` | Savings growth and emergency fund detection |
| `features/__init__.py` | Feature pipeline orchestrator |
| `recommend/engine.py` | Recommendation generation engine |
| `recommend/content_catalog.py` | Default content seed data |
| `recommend/content_loader.py` | Content loading with operator overrides |
| `guardrails/tone.py` | Tone validation (shaming language checks) |
| `guardrails/eligibility.py` | Eligibility filtering + predatory product blocking |
| `tests/test_personas.py` | Persona assignment tests |
| `tests/test_recommendations.py` | Recommendation generation tests |


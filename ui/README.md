# SpendSense UI Applications

This directory contains the Streamlit-based user interfaces for SpendSense MVP V2.

## Available Applications

### 1. User Dashboard (`app_user.py`) ✅
**Educational interface for bank customers**

**Features:**
- 🏠 **Dashboard:** View persona, behavioral patterns, and top recommendations
- 📚 **Learning Feed:** Browse all personalized educational content and partner offers
- 🔒 **Privacy Settings:** Manage consent and data preferences

**Launch:**
```bash
uv run streamlit run ui/app_user.py
```

**Default URL:** http://localhost:8501

---

### 2. Operator Dashboard (`app_operator.py`) ✅
**Compliance and oversight interface**

**Features:**
- 📊 **Overview:** System health metrics and persona distribution
- 👥 **User Management:** Filterable user directory with bulk operations
- 📈 **Behavioral Signals:** Aggregate analytics with charts
- ✅ **Recommendation Review:** Approve/override/flag workflow
- 🔍 **Decision Trace Viewer:** Full audit trail per user
- 🛡️ **Guardrails Monitor:** Compliance enforcement summary

**Launch:**
```bash
uv run streamlit run ui/app_operator.py
```

**Default URL:** http://localhost:8502 (or next available port)

---

## User Dashboard Guide

### First-Time Setup

1. **Generate synthetic data** (if not already done):
   ```bash
   uv run python -m ingest.data_generator
   ```

2. **Launch the app**:
   ```bash
   uv run streamlit run ui/app_user.py
   ```

3. **Select a user** from the dropdown in the sidebar

4. **Grant consent** when prompted (required for personalized insights)

### Navigation

The app has three main pages:

#### 🏠 Dashboard
- **Persona Profile:** Your financial behavioral category with description
- **Financial Patterns:** Key metrics across credit, subscriptions, savings, and income
- **Top Recommendations:** Preview of your personalized educational content

#### 📚 Learning Feed
- **Educational Content:** Strategies to improve your financial health
- **Partner Offers:** Products and services relevant to your profile
- All items include concrete rationales explaining why they're suggested

#### 🔒 Privacy Settings
- **Consent Management:** Grant or revoke data processing consent
- **Current Status:** View when consent was granted/revoked
- **Data Export:** (Coming soon) Download your complete data package

### User Selector

The sidebar shows all 100 synthetic users with consent indicators:
- ✅ = Consent granted
- ⏸️ = Consent not granted

### Consent Flow

**Without Consent:**
- Limited read-only view
- Persistent consent banner
- No recommendations generated
- No data processing occurs

**With Consent:**
- Full dashboard access
- Personalized recommendations
- Behavioral pattern analysis
- Manual refresh button to reload data

### Understanding Your Persona

Five possible personas based on your financial behaviors:

1. **💳 Credit Optimizer** (High Utilization)
   - Focus: Reducing credit utilization and interest charges
   - Criteria: Utilization ≥50%, interest charges, or payment struggles

2. **📊 Flexible Budgeter** (Variable Income)
   - Focus: Managing irregular income with smart budgeting
   - Criteria: Pay gap >45 days and low cash buffer

3. **🔄 Subscription Manager** (Subscription Heavy)
   - Focus: Optimizing recurring expenses
   - Criteria: ≥3 recurring services and significant subscription spend

4. **🎯 Savings Champion** (Savings Builder)
   - Focus: Growing savings and building emergency fund
   - Criteria: Positive savings growth and healthy credit utilization

5. **🌱 Getting Started** (General)
   - Default for users with insufficient behavioral signals
   - No personalized recommendations yet

### Key Metrics Explained

**Credit:**
- **Credit Cards:** Number of active credit card accounts
- **Avg Utilization:** Average balance/limit ratio across all cards

**Subscriptions:**
- **Recurring Services:** Detected subscription services (180-day window)
- **Monthly Recurring:** Estimated monthly subscription spend

**Savings:**
- **Savings Growth:** Net inflow to savings accounts (6-month window)
- **Emergency Fund:** Months of expenses covered by savings

**Income:**
- **Typical Pay Gap:** Median days between paychecks
- **Cash Buffer:** Months of expenses available in checking

### Recommendations

All recommendations include:
- **Title:** Clear description of the educational content
- **Description:** Detailed explanation
- **Rationale:** Concrete data explaining why this is relevant to you
- **Disclaimer:** Reminder that this is educational content, not financial advice

### Privacy & Data

**What we process:**
- Transaction data (amounts, dates, merchants)
- Account information (balances, types, limits)
- Behavioral signals (computed metrics)

**What we don't do:**
- Provide financial advice (educational only)
- Make account decisions
- Share data with third parties
- Store authentication credentials

**Your rights:**
- Grant or revoke consent at any time
- View all recommendations and decision traces
- Export your data (coming soon)

### Troubleshooting

**"No recommendations available"**
- Ensure you've granted consent
- Check if you have the 'general' persona (needs more transaction data)
- Try the refresh button

**"User not found"**
- Run data generation: `uv run python -m ingest.data_generator`
- Check that `data/users.sqlite` exists

**"Error loading recommendations"**
- Ensure behavioral signals exist: `features/signals.parquet`
- Run feature detection if needed
- Check console for detailed error messages

### Development Notes

**Session State:**
- App loads data once on navigation/refresh
- Use the "🔄 Refresh Data" button to reload

**Manual Testing:**
- Test different personas by selecting different users
- Verify consent grant/revoke functionality
- Check that recommendations match persona
- Ensure disclaimers appear on all content

**Mobile Responsiveness:**
- Streamlit provides native responsive layout
- Multi-column layouts collapse on mobile
- Test in browser responsive mode

### Design Principles

✅ **Educational Tone:** Supportive, not judgmental
✅ **Concrete Data:** Rationales cite specific amounts and percentages
✅ **User Control:** Consent required, easily revocable
✅ **Transparency:** Clear explanations for all recommendations
✅ **Accessibility:** Simple navigation, clear labels

---

## Operator Dashboard Guide

### Purpose
The operator dashboard provides compliance teams and analysts with full oversight into the SpendSense system, including user management, behavioral analytics, recommendation review, and audit trails.

### Six Main Tabs

#### 📊 Overview
**System health at a glance**
- Total users and consent status
- Persona distribution bar chart
- Guardrails summary (tone violations, blocked offers)
- Quick stats in sidebar

#### 👥 User Management
**Filterable user directory**
- Filter by: consent status, persona, gender, income tier
- Bulk consent operations (with safety warnings)
- User detail view (links to trace viewer)
- 100 users displayed in searchable table

#### 📈 Behavioral Signals
**Aggregate analytics and distributions**
- System-wide metrics (avg credit utilization, median savings, etc.)
- Distribution charts: credit utilization histogram, subscription counts
- 30d vs 180d metric comparison
- Per-user signal drill-down

#### ✅ Recommendation Review
**Approve/override/flag workflow**
- Select user and load their recommendations
- View all recommendations with rationales and guardrail checks
- Inline tone validation and eligibility status
- Three actions:
  - **Approve:** Log approval to decision_log.md and trace JSON
  - **Override:** Provide operator name + reason, log to both locations
  - **Flag:** Mark for manual review with explanation
- Operator name remembered across session

#### 🔍 Decision Trace Viewer
**Full audit trail per user**
- Expandable sections:
  - Behavioral Signals (subscriptions, savings, credit, income)
  - Persona Assignment (criteria met, all checks)
  - Recommendations (education items + partner offers)
  - Guardrail Decisions (consent, tone, eligibility, overrides)
  - Raw JSON (complete trace data)
- Progressive disclosure design (important data shown first)

#### 🛡️ Guardrails Monitor
**Compliance enforcement summary**
- Total users and consent status
- Tone violations grouped by prohibited phrase
- Blocked offers with reasons
- Consent audit trail with timestamps

### Override Logging

All operator actions (approve/override/flag) are logged to two locations:

**1. `docs/decision_log.md` (human-readable)**
```markdown
### Operator Override - 2025-11-03 14:32:15
**Operator:** Jane Doe
**User:** user_0042
**Action:** OVERRIDE
**Recommendation:** Lower Credit Utilization
**Reason:** User recently paid down balance; utilization outdated
```

**2. `docs/traces/{user_id}.json` (machine-readable)**
```json
{
  "decision_type": "operator_override",
  "operator": "Jane Doe",
  "action": "override",
  "recommendation_title": "Lower Credit Utilization",
  "reason": "User recently paid down balance; utilization outdated",
  "timestamp": "2025-11-03T14:32:15"
}
```

### Performance Expectations
- Page load: < 2 seconds
- Tab switching: < 0.5 seconds
- Recommendation generation: < 1 second per user
- Trace loading: < 0.1 seconds per user
- Bulk consent (100 users): < 2 seconds

### Known Limitations (MVP)
- No authentication (local-only deployment)
- No real-time updates (manual refresh required)
- Evaluation summary shows "coming soon" until PR #8

---

## Testing

**Manual testing checklist for `app_user.py`:**

- [ ] App launches without errors
- [ ] User selector shows all 100 users
- [ ] Consent indicators (✅/⏸️) display correctly
- [ ] Navigation works between all 3 pages
- [ ] Consent banner appears for users without consent
- [ ] Grant consent button updates database
- [ ] Dashboard shows persona and metrics
- [ ] Learning feed displays recommendations with rationales
- [ ] Privacy settings show correct consent status
- [ ] Revoke consent button works
- [ ] Refresh button reloads data
- [ ] All disclaimers present on recommendations
- [ ] No shaming language in any text
- [ ] Error handling for missing data

**Manual testing checklist for `app_operator.py`:**

- [ ] App launches without errors
- [ ] Sidebar shows total users, consent count, most common persona
- [ ] All 6 tabs navigate correctly

**Overview Tab:**
- [ ] Total users displays (100)
- [ ] Consent percentage shown
- [ ] Persona distribution bar chart renders
- [ ] Guardrails metrics display

**User Management Tab:**
- [ ] All 100 users in table
- [ ] Consent filter works (All/Granted/Not Granted)
- [ ] Persona filter works
- [ ] Gender and income tier filters work
- [ ] Multiple filters work together
- [ ] Bulk consent shows preview count
- [ ] Bulk consent grant button works

**Behavioral Signals Tab:**
- [ ] Aggregate metrics display
- [ ] Credit utilization histogram shows 4 bins
- [ ] Subscription count chart renders
- [ ] 30d vs 180d comparison table works
- [ ] Per-user drill-down displays signals

**Recommendation Review Tab:**
- [ ] User selector loads all users
- [ ] Load Recommendations button works
- [ ] Metadata shows counts and tone check status
- [ ] Inline guardrail checks display
- [ ] Approve button logs to decision_log.md
- [ ] Override form collects operator name and reason
- [ ] Override submission logs correctly
- [ ] Flag form works
- [ ] Operator name remembered in session

**Decision Trace Viewer Tab:**
- [ ] User selector works
- [ ] User info displays correctly
- [ ] All 5 expanders show correct data
- [ ] Raw JSON expander shows complete trace
- [ ] Operator overrides appear in Guardrail Decisions

**Guardrails Monitor Tab:**
- [ ] Summary metrics display
- [ ] Tone violations table works (if violations exist)
- [ ] Blocked offers list shows (if any blocked)
- [ ] Consent audit trail displays recent changes

---

## Future Enhancements

**Post-MVP features:**
- User authentication
- Feedback mechanism (thumbs up/down on recommendations)
- Historical tracking of persona changes
- Interactive calculators (emergency fund, debt payoff)
- Recommendation acceptance tracking
- Multi-language support
- Dark mode toggle
- Email/SMS notification preferences

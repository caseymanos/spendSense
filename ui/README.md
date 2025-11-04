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

### 2. Operator Dashboard (`app_operator.py`) 🚧
**Compliance and oversight interface** (Coming in PR #7)

**Planned Features:**
- User management and filtering
- Signal visualization
- Persona distribution analysis
- Recommendation review and approval
- Decision trace viewer
- Evaluation metrics summary

**Launch:** (Not yet implemented)
```bash
uv run streamlit run ui/app_operator.py
```

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

# SpendSense MVP V2 - Demo Documentation

This directory contains screenshots and demonstration materials for the SpendSense platform.

## Overview

SpendSense provides three user interfaces for different stakeholders:

1. **User Dashboard (Streamlit)** - Educational interface for end users
2. **Operator Dashboard (Streamlit)** - Compliance and oversight interface
3. **Reflex Web Dashboard** - Modern web-based user interface

## How to Capture Screenshots

### User Dashboard (Streamlit)

Launch the user dashboard:
```bash
uv run streamlit run ui/app_user.py
```

Navigate to `http://localhost:8501` and capture screenshots of:

1. **Consent Onboarding Screen**
   - Shows when a user has not granted consent
   - Displays consent request banner with explanation
   - "Grant Consent" button

2. **Dashboard View (After Consent)**
   - User selector dropdown showing all 100 users
   - Consent status badge (green checkmark)
   - Persona badge with icon and description
   - Behavioral metrics grid (4 columns):
     - Credit utilization
     - Subscriptions detected
     - Savings growth
     - Income stability
   - Top 3 recommendations preview

3. **Learning Feed**
   - Full list of personalized recommendations
   - Educational items with rationales
   - Partner offers with eligibility filtering
   - Disclaimers on all recommendations

4. **Privacy Settings**
   - Current consent status with timestamp
   - Grant/Revoke consent buttons
   - Data export placeholder (coming soon)

### Operator Dashboard (Streamlit)

Launch the operator dashboard:
```bash
uv run streamlit run ui/app_operator.py
```

Navigate to `http://localhost:8502` and capture screenshots of:

1. **Overview Tab**
   - Persona distribution chart
   - Summary statistics
   - User counts by persona

2. **User Management Tab**
   - Filterable user table
   - Consent status filters
   - Persona filters
   - Demographic filters
   - Bulk consent operations

3. **Behavioral Signals Tab**
   - Signal distribution charts
   - Per-user signal details
   - 30-day and 180-day metrics

4. **Recommendation Review Tab**
   - User selector
   - Recommendation cards with rationales
   - Approve/Override/Flag actions
   - Operator identity input (required for approvals)

5. **Decision Trace Viewer Tab**
   - User selector
   - Expandable sections for each pipeline phase:
     - Behavioral signals
     - Persona assignment
     - Recommendations generated
     - Guardrails applied
   - Raw JSON view

6. **Guardrails Monitor Tab**
   - Tone validation results
   - Blocked offers summary
   - Consent audit

### Reflex Web Dashboard

Launch the Reflex web dashboard:
```bash
cd ui_reflex
uv run reflex run
```

Navigate to `http://localhost:3000` and capture screenshots of:

1. **Initial Load**
   - Modern web interface
   - User selector
   - Consent status in navbar

2. **Dashboard with Consent**
   - Financial metrics cards
   - Persona badge
   - Recommendations preview
   - Clean, modern design

3. **No Consent State**
   - Banner explaining data processing is paused
   - Grant consent button
   - Limited read-only view

## Screenshot Naming Convention

Use the following naming pattern:
```
{interface}_{view}_{state}.png
```

Examples:
- `user_streamlit_consent_onboarding.png`
- `user_streamlit_dashboard_with_consent.png`
- `user_streamlit_learning_feed.png`
- `user_streamlit_privacy_settings.png`
- `operator_streamlit_overview.png`
- `operator_streamlit_user_management.png`
- `operator_streamlit_signals.png`
- `operator_streamlit_recommendation_review.png`
- `operator_streamlit_trace_viewer.png`
- `operator_streamlit_guardrails.png`
- `reflex_web_dashboard_initial.png`
- `reflex_web_dashboard_with_consent.png`
- `reflex_web_dashboard_no_consent.png`

## Screenshot Requirements

- **Resolution**: Minimum 1920x1080 (full HD)
- **Format**: PNG for best quality
- **Content**: Show real data from the synthetic dataset
- **Privacy**: All data is synthetic - no PII concerns
- **Browser**: Use Chrome or Firefox for consistency

## Key Features to Highlight

### User Dashboard
1. Clear consent management
2. Persona-based personalization
3. Concrete rationales citing actual data
4. Educational tone (no shaming language)
5. Mandatory disclaimers on all recommendations

### Operator Dashboard
1. Full auditability via decision traces
2. Approve/override/flag workflow
3. Operator attribution (name required for actions)
4. Guardrails monitoring
5. Fairness metrics visualization

### Reflex Web Dashboard
1. Modern, responsive design
2. Real-time state management
3. Component-based architecture
4. Clean user experience

## Video Demo (Optional)

If creating a video demo, include:

1. **Data Generation** (10 seconds)
   ```bash
   uv run python -m ingest.data_generator
   ```

2. **User App Walkthrough** (60 seconds)
   - Show consent flow
   - Navigate all tabs
   - Highlight key features

3. **Operator App Walkthrough** (60 seconds)
   - Show recommendation review
   - Demonstrate approve/override
   - View decision traces

4. **Evaluation Run** (10 seconds)
   ```bash
   uv run python -m eval.run
   ```

5. **Results Summary** (20 seconds)
   - Show eval_summary.md
   - Highlight passing metrics

Total video length: ~2-3 minutes

## Notes

- All screenshots should show the platform working with real synthetic data
- Highlight the transparency and explainability features
- Demonstrate both the user-facing and operator-facing interfaces
- Show the complete audit trail from behavior detection to recommendations

## Demo Data

Use the existing 100 synthetic users:
- Mix of personas (high utilization, variable income, subscription heavy, savings builder)
- Varied consent states (some granted, some not)
- Diverse behavioral patterns
- Representative of real-world financial behaviors

## Contact

For questions about demo materials:
- Project Lead: Casey Manos
- Technical Spec: Bryce Harris (bharris@peak6.com)

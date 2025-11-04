# NiceGUI Operator Dashboard

A modern, theme-switchable operator dashboard for SpendSense MVP V2, built with NiceGUI.

## Features

### 🎨 Three Visual Themes
- **Clean & Minimal** - Professional, minimal styling with subtle borders and shadows
- **Modern & Colorful** - Vibrant gradients, glassmorphism effects, modern animations
- **Dashboard & Analytics** - Dark mode, BI-tool style, data-focused design

### 📊 Seven Functional Tabs

1. **Overview** - System health metrics, persona distribution, guardrails summary
2. **User Management** - Multi-dimensional filtering, paginated user tables
3. **Behavioral Signals** - Signal analysis with charts, 30d vs 180d comparison, per-user drill-down
4. **Recommendation Review** - Review recommendations with approve/override/flag actions
5. **Decision Trace Viewer** - Complete audit trail with expandable JSON sections
6. **Guardrails Monitor** - Compliance metrics, tone violations, blocked offers
7. **Data Generation** - Interactive parameter controls for synthetic data generation

## Installation

### Prerequisites
- Python 3.11+
- `uv` package manager (or pip)

### Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

## Running the Dashboard

### Start the Server

```bash
uv run python ui/app_operator_nicegui.py
```

The dashboard will be available at: **http://localhost:8081**

### Default Settings
- **Port:** 8081 (avoids conflict with Streamlit on 8501)
- **Auto-reload:** Enabled (for development)
- **Storage:** Encrypted user storage for theme preferences and operator name

## Usage Guide

### Initial Setup

1. **Enter Operator Name** (top-right header)
   - Required for audit trail logging
   - Stored in user storage (persists across sessions)

2. **Select Theme** (top-right buttons)
   - Toggle between Clean/Minimal, Modern/Colorful, Dashboard/Analytics
   - Theme preference saved automatically

3. **Generate Data** (if needed)
   - Navigate to "Data Generation" tab
   - Adjust parameters with sliders
   - Click "Generate Data"

### Tab-by-Tab Guide

#### 1. Overview Tab
**Purpose:** High-level system health and metrics

**Features:**
- Total users, consent rate, persona count, recommendations generated
- Interactive persona distribution chart
- Persona definitions table with descriptions
- Guardrails summary (tone violations, blocked offers)

**When to use:** First view after login to assess system state

---

#### 2. User Management Tab
**Purpose:** Browse and filter user database

**Features:**
- **Filters:**
  - Consent Status (All / Granted / Not Granted)
  - Persona (All / High Utilization / Variable Income / etc.)
  - Gender (All / M / F / Non-binary)
  - Income Tier (All / Low / Medium / High / Very High)
- **User Table:** Displays user_id, name, consent, persona, age, gender, income, region
- **Pagination:** 20 users per page
- **Real-time filtering:** Updates instantly as you change filters

**When to use:**
- Finding specific users
- Analyzing demographic distributions
- Checking consent status across segments

---

#### 3. Behavioral Signals Tab
**Purpose:** Analyze financial behavior patterns

**Features:**
- **Aggregate Metrics:**
  - Average credit utilization
  - Average subscriptions count
  - Median savings inflow (180d)
  - Median pay gap variance
- **Distribution Charts:**
  - Credit utilization histogram (binned: 0-30%, 30-50%, 50-80%, 80-100%)
  - Subscription count distribution
- **30d vs 180d Comparison Table:** Compare signal values across time windows
- **Per-User Drill-Down:**
  - Select any user from dropdown
  - Expandable sections: Credit, Subscriptions, Savings, Income
  - Color-coded values for easy scanning

**When to use:**
- Investigating behavioral patterns
- Quality-checking signal detection
- Understanding user financial profiles

---

#### 4. Recommendation Review Tab
**Purpose:** Review and take action on recommendations

**Features:**
- **User Selection:** Choose user to review recommendations
- **Metadata Display:**
  - User ID, Persona, Consent status, Total recommendations
  - Education items count, Partner offers count
- **Per-Recommendation Cards:**
  - Type badge (Education / Partner Offer)
  - Category badge
  - Description (what the recommendation is about)
  - **Rationale** (highlighted in yellow - most important for compliance)
  - Disclaimer (highlighted in red)
  - Guardrail checks (Tone validation, Eligibility)
- **Operator Actions:**
  - **Approve** - Accept recommendation as-is
  - **Override** - Reject/modify with reason (opens dialog)
  - **Flag** - Mark for review with reason (opens dialog)
- **Audit Logging:** All actions logged to `docs/decision_log.md` and trace JSON

**When to use:**
- Daily recommendation review workflow
- Compliance oversight
- Manual approval process
- Investigating flagged content

**Important Notes:**
- Operator name MUST be set before taking actions
- All actions are permanently logged
- Rationales are critical - ensure they cite actual user data

---

#### 5. Decision Trace Viewer Tab
**Purpose:** Full audit trail for compliance and debugging

**Features:**
- **User Selection:** Choose user to view trace
- **User Information Card:** Name, persona, consent, demographics
- **Expandable Sections:**
  - **Behavioral Signals** - 30d and 180d signal data as JSON
  - **Persona Assignment** - Assignment timestamp, criteria met, all checks
  - **Recommendations** - Full recommendation list with metadata
  - **Guardrail Decisions** - All guardrail events including operator overrides
  - **Raw JSON** - Complete trace file with copy-to-clipboard
- **JSON Editor:** Read-only JSON viewer with syntax highlighting

**When to use:**
- Auditing decisions for compliance review
- Debugging persona assignment issues
- Verifying recommendation rationales
- Investigating guardrail blocks
- Exporting data for external analysis

---

#### 6. Guardrails Monitor Tab
**Purpose:** Compliance monitoring and violation tracking

**Features:**
- **Summary Metrics:**
  - Total users processed
  - Users with consent
  - Tone violations count (with delta indicator)
  - Blocked offers count (with delta indicator)
- **Tone Violations Detail:**
  - Table of prohibited phrases with occurrence counts
  - Sorted by frequency (most common first)
- **Blocked Offers Detail:**
  - First 10 blocked offers with full JSON
  - Expandable cards for each offer
- **Consent Audit Trail:**
  - 10 most recent consent changes
  - Shows user ID, name, status, timestamp

**When to use:**
- Daily compliance review
- Identifying problematic language patterns
- Monitoring consent grant/revoke activity
- Reporting to compliance team

---

#### 7. Data Generation Tab (NEW)
**Purpose:** Generate synthetic test data with custom parameters

**Features:**
- **Parameter Sliders:**
  - **Random Seed** (0-9999, default: 42) - Controls reproducibility
  - **Number of Users** (10-1000, default: 100) - User count
  - **Months of History** (1-24, default: 6) - Transaction history depth
  - **Avg Transactions/Month** (10-100, default: 30) - Transaction density
- **Live Preview:**
  - JSON editor showing current configuration
  - Estimated transaction count
- **Actions:**
  - **Generate Data** - Execute data generation with current parameters
  - **Reset to Defaults** - Restore default values
  - **Load from Config** - Load saved configuration from `data/config.json`
- **Progress Feedback:**
  - Notifications for start/complete/errors
  - Async execution (non-blocking)

**When to use:**
- Creating new test datasets
- Testing with different user volumes
- Reproducing specific scenarios (via seed)
- Generating data for demos

**Tips:**
- Use same seed for reproducible datasets
- Higher user counts = longer generation time
- Recommend starting with 50-100 users for testing

---

## Theme Switching

### How to Switch Themes

1. Click theme button in top-right header
2. Choose: Clean & Minimal / Modern & Colorful / Dashboard & Analytics
3. Page automatically reloads to apply new theme
4. Theme preference saved in user storage

### Theme Comparison

| Feature | Clean & Minimal | Modern & Colorful | Dashboard & Analytics |
|---------|-----------------|-------------------|----------------------|
| Background | White | Light gradient | Dark (#1E1E1E) |
| Cards | Subtle shadow | Elevated shadow | Dark with borders |
| Colors | Conservative | Vibrant | High contrast |
| Style | Professional | Modern/Fun | Data-focused |
| Best for | Corporate/Formal | Demos/Presentations | Data analysis |

## Operator Actions Workflow

### Approve Workflow
1. Navigate to "Recommendation Review" tab
2. Select user and click "Load Recommendations"
3. Expand recommendation card
4. Review rationale and guardrail checks
5. Click **Approve** button
6. Confirmation notification appears
7. Action logged to `docs/decision_log.md` and trace JSON

### Override Workflow
1. Follow steps 1-4 above
2. Click **Override** button
3. Dialog opens
4. Enter reason for override (required)
5. Click "Submit Override"
6. Action logged with full audit trail

### Flag Workflow
1. Follow steps 1-4 above
2. Click **Flag** button
3. Dialog opens
4. Enter reason for flagging (required)
5. Click "Submit Flag"
6. Recommendation marked for review

### Audit Trail
All operator actions are logged to:
- **`docs/decision_log.md`** - Markdown log with timestamps, operator, action, reason
- **`docs/traces/{user_id}.json`** - User-specific trace with guardrail_decisions array

## Data Files and Paths

| File | Purpose |
|------|---------|
| `data/users.sqlite` | User database with consent and demographics |
| `features/signals.parquet` | Behavioral signals (credit, subscriptions, savings, income) |
| `data/transactions.parquet` | Transaction history |
| `data/config.json` | Data generation configuration |
| `docs/traces/{user_id}.json` | Per-user decision traces |
| `docs/decision_log.md` | Operator override log |

## Troubleshooting

### Dashboard won't start
**Error:** `ModuleNotFoundError: No module named 'nicegui'`
**Solution:** Run `uv sync` to install dependencies

### No data visible
**Problem:** All tabs show "No data available"
**Solution:** Navigate to "Data Generation" tab and click "Generate Data"

### Theme not changing
**Problem:** Theme button clicked but no change
**Solution:** Wait for page reload (should happen automatically). If not, manually refresh browser.

### Operator actions failing
**Error:** "Please enter operator name"
**Solution:** Enter your name in top-right "Operator Name" input field

### Port already in use
**Error:** `Address already in use: 8081`
**Solution:** Stop other process using port 8081, or change port in `app_operator_nicegui.py` (line ~1170)

## Architecture

### File Structure
```
ui/
├── app_operator_nicegui.py    # Main application (1170 lines)
├── themes/
│   ├── theme_manager.py       # Theme system core
│   ├── clean_minimal.py       # Theme 1
│   ├── modern_colorful.py     # Theme 2
│   └── dashboard_analytics.py # Theme 3
├── components/
│   ├── metric_card.py         # KPI cards
│   ├── data_table.py          # Tables with filtering
│   ├── charts.py              # Plotly visualizations
│   └── operator_actions.py    # Approve/override/flag UI
└── utils/
    └── data_loaders.py        # Data loading functions
```

### Key Technologies
- **NiceGUI** - Web UI framework (Python)
- **Plotly** - Interactive charts
- **Pandas** - Data manipulation
- **SQLite** - User database
- **Parquet** - Signals storage
- **JSON** - Trace logs

### State Management
- **Global cache:** `data_cache` dict for users, signals, personas, guardrails
- **User storage:** Encrypted browser storage for theme, operator name
- **Refreshable decorators:** `@ui.refreshable` for reactive updates

## Performance Tips

1. **Use pagination:** Large user lists automatically paginated (20/page)
2. **Filter early:** Use filters in User Management to reduce data volume
3. **Refresh strategically:** Click refresh button only when data changes
4. **Theme switching:** Expect 1-2 second reload when changing themes
5. **Data generation:** 100 users × 6 months × 30 txns = ~18K transactions (~5 seconds)

## Security Notes

### Production Deployment
- **Change storage secret:** Line ~1170 in `app_operator_nicegui.py`
- **Enable HTTPS:** Use reverse proxy (nginx/traefik)
- **Restrict access:** Add authentication layer (not built-in)
- **Audit logs:** Monitor `docs/decision_log.md` for unauthorized actions

### Data Privacy
- All data is synthetic (no real PII)
- Operator names stored locally in browser
- No external API calls
- Logs stored on local filesystem

## Comparison: Streamlit vs NiceGUI

| Feature | Streamlit | NiceGUI |
|---------|-----------|---------|
| Performance | Full page reruns | Reactive updates only |
| State Management | `st.session_state` | `app.storage` + bindings |
| Interactivity | Form-based | Event-driven |
| Theming | Config file | Runtime switchable (3 themes) |
| Real-time updates | Limited | Native WebSockets |
| Custom styling | CSS in markdown | Direct CSS/JS access |
| Learning curve | Easy | Moderate |

## Future Enhancements

### Potential Additions
- [ ] Export data to CSV/Excel
- [ ] Bulk operator actions (approve multiple recommendations)
- [ ] Advanced filtering (date ranges, value ranges)
- [ ] Real-time tone validation in Recommendation Review
- [ ] User-level consent management (grant/revoke from UI)
- [ ] Notification system for flagged items
- [ ] Dashboard layout customization
- [ ] Additional chart types (line, scatter, heatmap)
- [ ] Search functionality across all tabs
- [ ] Keyboard shortcuts

## Support

### Getting Help
- Check `docs/SpendSense MVP V2.md` for system specifications
- Review `docs/taskList.md` for implementation roadmap
- Inspect `docs/decision_log.md` for audit trail examples

### Reporting Issues
Include:
1. Steps to reproduce
2. Expected vs actual behavior
3. Browser and OS version
4. Console errors (F12 → Console tab)
5. Screenshot if UI issue

## Credits

**Built with:**
- [NiceGUI](https://nicegui.io) - Python UI framework
- [Plotly](https://plotly.com/python/) - Interactive charts
- [Quasar Framework](https://quasar.dev) - UI components (via NiceGUI)

**Project:** SpendSense MVP V2
**Original Streamlit Dashboard:** `ui/app_operator.py`
**Specification:** Bryce Harris (bharris@peak6.com)

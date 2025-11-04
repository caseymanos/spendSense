# 🚀 SpendSense: Complete Setup & Running Guide

Complete guide to setting up and running all SpendSense frontend and backend components on your own machine.

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Initial Setup](#initial-setup)
4. [Frontend Options](#frontend-options)
   - [Reflex UI (Recommended)](#1-reflex-ui-modern-web-app)
   - [NiceGUI Operator Dashboard](#2-nicegui-operator-dashboard)
   - [Streamlit User Dashboard (Legacy)](#3-streamlit-user-dashboard-legacy)
5. [Backend API](#backend-fastapi-rest-api)
6. [Development Workflow](#development-workflow)
7. [Troubleshooting](#troubleshooting)
8. [Quick Reference](#quick-reference)

---

## Architecture Overview

SpendSense provides **multiple UI options** for different use cases:

| Interface | Technology | Port | Purpose | Status |
|-----------|-----------|------|---------|--------|
| **Reflex UI** | Reflex (Python-React) | 3000 | Modern themed user dashboard | ✅ **Recommended** |
| **NiceGUI Operator** | NiceGUI | 8081 | Compliance & data generation | ✅ Active |
| **Streamlit User** | Streamlit | 8501 | Legacy user dashboard | ⚠️ Legacy |
| **FastAPI** | FastAPI | 8000 | REST API backend | ✅ Active |

---

## Prerequisites

### Required Software

- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **uv** (Modern Python package manager) - [Installation guide](https://docs.astral.sh/uv/getting-started/installation/)
- **Git** - For version control

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# After installation, add to PATH (usually in ~/.zshrc or ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
uv --version
```

---

## Initial Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd SpendSense
```

### 2. Install Dependencies

```bash
# Install main project dependencies
uv sync

# This creates a virtual environment and installs all packages
```

### 3. Generate Synthetic Data (REQUIRED)

**⚠️ Important:** You must generate data before running any UI.

```bash
# Generate test data (100 users, 6 months of transactions)
uv run python -m ingest.data_generator
```

This creates:
- `data/users.sqlite` - User profiles with consent tracking
- `data/transactions.parquet` - Transaction history (50-100 per user)
- `data/config.json` - Generation configuration
- `features/signals.parquet` - Behavioral signals
- `docs/traces/*.json` - Decision audit trails

**Verify data generation:**
```bash
ls -lh data/
# Should show users.sqlite and transactions.parquet
```

---

## Frontend Options

### 1. Reflex UI (Modern Web App)

**✅ RECOMMENDED** - Modern themed dashboard with full interactivity.

#### Features
- 🎨 **5 Stunning Themes**: Default Light, Dark Mode, Glassmorphism, Minimal, Vibrant
- 🧭 **Full Navigation**: Dashboard, Learning Feed, Privacy pages
- ✅ **Consent Management**: Grant/revoke consent with UI updates
- 🎯 **Interactive**: Theme switcher, live data loading, responsive design
- 🐛 **Fixed**: React hydration errors resolved, all buttons functional

#### Setup

```bash
# Navigate to Reflex directory
cd ui_reflex

# Install Reflex dependencies
uv sync

# Or manually install
uv pip install reflex==0.8.18
```

#### Run

```bash
# Start Reflex development server
uv run reflex run

# Alternative: use full path to uv
~/.local/bin/uv run reflex run
```

#### Access

**URL:** http://localhost:3000

**Default Users:**
- `user_0001` through `user_0010` - Consent granted
- `user_0011+` - Test consent flow

#### Features in Action

1. **Theme Switcher**: Click floating theme button (bottom-right)
2. **Navigation**: Use top navbar to switch between Dashboard/Learning Feed/Privacy
3. **User Selection**: Dropdown to switch between users
4. **Consent Flow**:
   - Select user with no consent → See consent request banner
   - Click "Grant Consent" → Dashboard unlocks
   - Click "Revoke Consent" → Dashboard locks

#### Stop Server

```bash
# Ctrl+C in terminal, or:
lsof -ti:3000 | xargs kill
```

---

### 2. NiceGUI Operator Dashboard

**Modern operator interface** for compliance, monitoring, and data generation.

#### Features
- 📊 **7 Comprehensive Tabs**:
  1. Overview - System metrics and persona distribution
  2. User Management - User profiles and consent status
  3. Behavioral Signals - Financial pattern detection
  4. Recommendation Review - Approve/reject recommendations
  5. Decision Trace Viewer - Audit trail explorer
  6. Guardrails Monitor - Consent and eligibility checks
  7. **Data Generation** - Interactive synthetic data controls
- 🎨 **3 Visual Themes**: Clean/Minimal, Modern/Colorful, Dashboard/Analytics
- 🔧 **Data Generation Controls**: Adjust user counts, transaction patterns, date ranges
- 📝 **Full Audit Trail**: Operator identity tracking for compliance

#### Run

```bash
# From project root
cd /Users/caseymanos/GauntletAI/SpendSense

# Run NiceGUI operator app
uv run python ui/app_operator_nicegui.py
```

#### Access

**URL:** http://localhost:8081

**Auto-opens:** Browser opens automatically when server starts

#### Usage Tips

**Data Generation Tab:**
1. Navigate to "Data Generation" tab
2. Adjust parameters (users: 50-200, transactions/user: 30-150)
3. Set date ranges for realistic timelines
4. Click "Generate Data" to create new synthetic dataset
5. View generation logs in real-time

**Recommendation Review:**
1. Enter operator name in sidebar (required for audit compliance)
2. Review recommendations with rationale
3. Approve/reject with operator attribution
4. All actions logged to audit trail

**Theme Switching:**
- Click theme selector (top-right)
- Instant preview of all 3 themes
- Persists across sessions

#### Stop Server

```bash
# Ctrl+C in terminal, or:
lsof -ti:8081 | xargs kill
```

---

### 3. Streamlit User Dashboard (Legacy)

**⚠️ Legacy Interface** - Use Reflex UI for modern experience.

#### Run

```bash
# From project root
uv run streamlit run ui/app_user.py
```

#### Access

**URL:** http://localhost:8501

#### Features
- Basic user selection
- Consent management
- Financial metrics display
- Persona and recommendations

**Note:** Consider using Reflex UI (port 3000) for better UX.

---

## Backend: FastAPI REST API

RESTful API for programmatic access to SpendSense functionality.

### Run

```bash
# From project root
uv run uvicorn api.main:app --reload
```

### Access

- **API Base:** http://localhost:8000
- **Interactive Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Available Endpoints

Check `api/main.py` for complete API specification. Common endpoints:

```bash
# Health check
GET /

# User endpoints
GET /users/{user_id}
GET /users/{user_id}/signals
GET /users/{user_id}/persona
GET /users/{user_id}/recommendations

# Consent management
POST /users/{user_id}/consent
DELETE /users/{user_id}/consent
```

### Example API Call

```bash
# Get user recommendations
curl http://localhost:8000/users/user_0001/recommendations

# Grant consent
curl -X POST http://localhost:8000/users/user_0001/consent
```

### Stop Server

```bash
# Ctrl+C in terminal, or:
lsof -ti:8000 | xargs kill
```

---

## Development Workflow

### Recommended Multi-Service Setup

Run frontend and backend simultaneously for full-stack development:

#### Terminal 1: Reflex Frontend
```bash
cd /Users/caseymanos/GauntletAI/SpendSense/ui_reflex
uv run reflex run
# Access: http://localhost:3000
```

#### Terminal 2: NiceGUI Operator Dashboard
```bash
cd /Users/caseymanos/GauntletAI/SpendSense
uv run python ui/app_operator_nicegui.py
# Access: http://localhost:8081
```

#### Terminal 3: FastAPI Backend (Optional)
```bash
cd /Users/caseymanos/GauntletAI/SpendSense
uv run uvicorn api.main:app --reload
# Access: http://localhost:8000
```

### Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest --cov=spendsense tests/

# Run specific test file
uv run pytest tests/test_data_generation.py -v

# Run specific test
uv run pytest tests/test_personas.py::test_persona_assignment -v
```

### Code Quality

```bash
# Lint code
uv run ruff check .

# Format code
uv run black .

# Fix auto-fixable issues
uv run ruff check --fix .
```

### Data Management

```bash
# Regenerate all data
uv run python -m ingest.data_generator

# Custom data generation (via NiceGUI operator dashboard)
# 1. Open http://localhost:8081
# 2. Navigate to "Data Generation" tab
# 3. Adjust parameters interactively
# 4. Click "Generate Data"

# View data
sqlite3 data/users.sqlite "SELECT * FROM users LIMIT 5;"
```

---

## Troubleshooting

### Port Already in Use

```bash
# Kill process on specific port
lsof -ti:3000 | xargs kill  # Reflex
lsof -ti:8081 | xargs kill  # NiceGUI
lsof -ti:8501 | xargs kill  # Streamlit
lsof -ti:8000 | xargs kill  # FastAPI

# Find what's using a port
lsof -i:3000
```

### Data Files Not Found

**Error:** `FileNotFoundError: data/users.sqlite not found`

**Solution:**
```bash
cd /Users/caseymanos/GauntletAI/SpendSense
uv run python -m ingest.data_generator
```

### uv Command Not Found

**Error:** `zsh: command not found: uv`

**Solution:**
```bash
# Use full path
~/.local/bin/uv run <command>

# Or add to PATH permanently
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Module Not Found

**Error:** `ModuleNotFoundError: No module named 'reflex'`

**Solution:**
```bash
# Reinstall dependencies
cd /Users/caseymanos/GauntletAI/SpendSense
uv sync

# Or for Reflex specifically
cd ui_reflex
uv sync

# Clean reinstall if issues persist
rm -rf .venv
uv sync
```

### React Hydration Errors (Reflex)

**Error:** `<p> cannot be a descendant of <p>` in browser console

**Status:** ✅ Fixed in commit `2f4ae8b`

**If issue persists:**
```bash
cd ui_reflex
git pull origin main
uv run reflex run
```

### NiceGUI Port Conflicts

**Error:** `Address already in use: 8081`

**Solution:**
```bash
# Kill existing NiceGUI process
lsof -ti:8081 | xargs kill

# Or change port in app_operator_nicegui.py (line 1249):
# ui.run(port=8082, ...)
```

### Database Locked

**Error:** `sqlite3.OperationalError: database is locked`

**Solution:**
```bash
# Close all apps accessing database
lsof data/users.sqlite

# Kill processes if needed
kill <PID>

# Restart single UI instance
```

---

## Quick Reference

### All Run Commands

```bash
# ============= FRONTEND =============

# Reflex UI (RECOMMENDED)
cd ui_reflex && uv run reflex run
# → http://localhost:3000

# NiceGUI Operator Dashboard
uv run python ui/app_operator_nicegui.py
# → http://localhost:8081

# Streamlit User Dashboard (Legacy)
uv run streamlit run ui/app_user.py
# → http://localhost:8501

# ============= BACKEND =============

# FastAPI REST API
uv run uvicorn api.main:app --reload
# → http://localhost:8000

# ============= DATA =============

# Generate synthetic data
uv run python -m ingest.data_generator

# Run evaluation metrics
uv run python -m eval.run --input data/transactions.parquet --output eval/results.json

# ============= TESTING =============

# All tests
uv run pytest tests/ -v

# Coverage report
uv run pytest --cov=spendsense tests/

# ============= CODE QUALITY =============

# Lint and format
uv run ruff check .
uv run black .
```

### Port Reference

| Service | Port | URL |
|---------|------|-----|
| Reflex UI | 3000 | http://localhost:3000 |
| NiceGUI Operator | 8081 | http://localhost:8081 |
| Streamlit User | 8501 | http://localhost:8501 |
| FastAPI | 8000 | http://localhost:8000 |
| FastAPI Docs | 8000 | http://localhost:8000/docs |

### File Locations

```
SpendSense/
├── ui_reflex/              # Reflex UI (port 3000)
│   ├── user_app/           # Main app code
│   │   ├── user_app_themed.py  # Active UI file
│   │   ├── state/user_state.py # State management
│   │   ├── components/     # Reusable components
│   │   └── utils/          # Themes & formatters
│   └── rxconfig.py         # Reflex configuration
│
├── ui/                     # NiceGUI & Streamlit UIs
│   ├── app_operator_nicegui.py  # Operator dashboard (port 8081)
│   ├── app_user.py         # Streamlit user UI (port 8501)
│   ├── themes.py           # Theme system
│   └── components/         # Shared UI components
│
├── api/                    # FastAPI backend (port 8000)
│   ├── main.py             # API endpoints
│   └── models.py           # Pydantic models
│
├── data/                   # Generated data (gitignored)
│   ├── users.sqlite        # User database
│   ├── transactions.parquet # Transaction data
│   └── config.json         # Data generation config
│
├── features/               # Behavioral signal detection
│   └── signals.parquet     # Detected patterns
│
└── docs/                   # Documentation & audit trails
    ├── traces/             # Per-user decision traces
    ├── schema.md           # Data model docs
    └── RUNNING_THE_APP.md  # This file
```

---

## Current Status

### ✅ What's Working

- **Reflex UI**: All buttons, navigation, themes, consent flow
- **NiceGUI Operator**: Full 7-tab dashboard with data generation
- **FastAPI**: REST endpoints operational
- **Data Generation**: Synthetic data pipeline complete
- **Tests**: 80 tests passing (800% above target)

### 🔧 Recent Fixes

- **React Hydration Error** (Fixed in `2f4ae8b`):
  - Added `as_="div"` to Text components
  - All interactive buttons now functional
  - Navigation working across Dashboard/Learning Feed/Privacy

### 📊 Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Tests Passing | ≥10 | 80 | ✅ PASS (800%) |
| Explainability | 100% | 100% | ✅ PASS |
| Relevance | ≥90% | 100% | ✅ PASS |
| Latency | <5s | 0.01s | ✅ PASS (500x faster) |
| UI Functionality | 100% | 100% | ✅ PASS |

---

## Need Help?

### Documentation
- **Full Spec:** `docs/SpendSense MVP V2.md`
- **Task Plan:** `docs/taskList.md`
- **Data Schema:** `docs/schema.md`
- **Decision Log:** `docs/decision_log.md`

### Support
- **GitHub Issues:** [Report bugs](https://github.com/caseymanos/spendSense/issues)
- **Project Lead:** Casey Manos
- **Technical Spec:** Bryce Harris (bharris@peak6.com)

---

**Last Updated:** 2025-01-04
**Version:** 2.0
**Status:** Production Ready ✅

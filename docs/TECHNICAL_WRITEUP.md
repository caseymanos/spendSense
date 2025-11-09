# SpendSense: Technical Writeup
## Explainable Financial Behavior Analysis with Consent-Aware Guardrails

**Project:** SpendSense MVP V2
**Author:** Casey Manos
**Date:** November 2025
**Submission:** Peak6 Platinum Project

---

## Executive Summary

Financial institutions generate massive transaction data through Plaid integrations but struggle to transform it into actionable customer insights without crossing into regulated financial advice territory. SpendSense solves this challenge by providing an **explainable, consent-aware system** that detects behavioral patterns from synthetic Plaid-style transaction data, assigns evidence-based personas, and delivers personalized financial education with strict guardrails around eligibility, tone, and transparency.

The system achieves **100% coverage** of users with assigned personas, **100% explainability** with concrete data-backed rationales, and operates at **476x faster** than the target latency (0.0105s vs 5.0s target). All recommendations comply with "no shaming" tone validation and mandatory consent enforcement, demonstrating that sophisticated financial AI can be both powerful and trustworthy.

---

## Technical Approach

### 1. Synthetic Data Generation (Plaid-Compatible)

SpendSense generates realistic financial scenarios for 100 synthetic users over a 6-month window using a deterministic seeding strategy (seed=42 for reproducibility). The data pipeline creates:

- **Users**: Demographics, income levels, consent status, account holdings
- **Accounts**: Checking, savings, credit cards, money market, HSA accounts with accurate balance tracking
- **Transactions**: 10,000+ transactions with merchant names, categories (Plaid taxonomy), payment channels
- **Liabilities**: Credit card APRs, utilization rates, minimum payments, overdue tracking

**Key Innovation**: All data is synthetic using `faker` library—zero real PII, enabling safe development and demonstration without privacy concerns.

### 2. Behavioral Signal Detection (4 Signal Types)

The feature pipeline detects patterns across **30-day and 180-day windows**:

- **Subscriptions**: Recurring merchants (≥3 in 90 days), monthly subscription spend, subscription share of total spending
- **Savings**: Net inflow to savings-like accounts, growth rate percentage, emergency fund coverage
- **Credit**: Utilization ratios, flags for 30%/50%/80% thresholds, minimum-payment-only detection, interest charges
- **Income Stability**: Payroll ACH detection, payment frequency/variability, cash-flow buffer in months

### 3. Persona Assignment System (5 Personas)

Users are assigned to one of five personas based on priority-ordered criteria:

1. **High Utilization** (highest priority): Credit strain indicators (≥50% utilization OR interest charges OR overdue)
2. **Variable Income Budgeter**: Income instability (median pay gap >45 days AND cash buffer <1 month)
3. **Subscription-Heavy**: Recurring payment optimization opportunities (≥3 subscriptions AND ≥$50/month OR ≥10% of spend)
4. **Savings Builder**: Positive savings momentum (≥2% growth OR ≥$200/month inflow, AND utilization <30%)
5. **General**: Catch-all persona ensuring 100% coverage

**Priority Logic**: The system assigns the highest-priority persona when multiple criteria match, ensuring users receive the most actionable guidance for their financial situation.

### 4. AI-Enhanced Recommendation Engine

The recommendation engine combines rule-based logic with optional AI augmentation:

- **Rule-Based Foundation**: Content catalog with 40+ educational items mapped to persona needs
- **AI Enhancement** (Optional): OpenAI GPT integration (gpt-4o-mini, gpt-4o, gpt-3.5-turbo) for dynamic content generation
- **Rationale Generation**: Every recommendation includes a "because" statement citing specific data points

**Example Rationale**:
> "We noticed your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000 limit). Bringing this below 30% could improve your credit score and reduce interest charges of $87/month."

**Output per User**: 3-5 educational items + 1-3 partner offers with eligibility checks

### 5. Three-Layer Guardrail System

**Consent Management**:
- Explicit opt-in required before any data processing
- Revocation capability with full audit trail
- No recommendations generated without active consent
- Consent status tracked with timestamps in SQLite

**Eligibility Filtering**:
- Product eligibility checks (minimum income/credit requirements)
- Existing account filtering (don't offer savings if user has one)
- Predatory product blocking (payday loans, title loans explicitly banned)

**Tone Validation**:
- Prohibited phrase detection via regex (e.g., "overspending", "bad habits", "lack discipline")
- Positive alternative suggestions enforced
- Mandatory disclaimer on all content: *"This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."*

### 6. Multi-Interface Architecture

**Three User Interfaces**:

1. **Next.js Web Application** (Modern, Production-Ready)
   - React-based dashboard with Tailwind CSS styling
   - Real-time consent management
   - User switcher with consent indicators
   - Responsive mobile-friendly design
   - Port: 3000

2. **NiceGUI Operator Dashboard** (Compliance & Operations)
   - 7-tab interface: Overview, User Management, Behavioral Signals, Recommendation Review, Decision Traces, Guardrails Monitor, Data Generation
   - Approve/override/flag workflow for human oversight
   - Configurable themes for accessibility
   - Port: 8081

3. **Streamlit User Dashboard** (Legacy/Demo)
   - Basic user interface for demonstrations
   - Consent toggle and persona display
   - Port: 8501

**API Layer** (FastAPI):
- RESTful endpoints: `/users`, `/consent`, `/profile/{user_id}`, `/recommendations/{user_id}`, `/videos/{topic}`
- Interactive Swagger UI documentation at `/docs`
- CORS middleware for cross-origin support
- Port: 8000

### 7. Comprehensive Evaluation Harness

**Six Core Metrics**:
1. **Coverage**: 100% (all users assigned persona)
2. **Explainability**: 100% (496/496 recommendations with rationales)
3. **Relevance**: 100% (154/154 recommendations match persona needs)
4. **Latency**: 0.0105s mean (476x faster than 5s target, P95: 0.0119s)
5. **Auditability**: 100% (100/100 users with complete trace JSONs)
6. **Fairness**: PASS (all demographic groups within ±10% tolerance)

**Fairness Analysis**:
- 4 demographic dimensions: Age, Gender, Income Tier, Region
- Persona assignment rates measured across all groups
- Demographic parity enforcement (no group >10% deviation)
- Demographics used **only for evaluation**, never for persona logic

---

## Key Innovations Beyond Specification

### 1. AI Integration
- OpenAI GPT models for dynamic recommendation generation
- Tone validation applied to all AI-generated content
- Fallback to rule-based engine if AI unavailable
- Token usage tracking and cost optimization

### 2. Video Content Integration
- Educational YouTube videos linked to recommendation topics
- Database-backed video library with seeding scripts
- Embedded player with `youtube-video-element` and `player.style` UI

### 3. Chart & Image Generation
- Personalized financial visualizations (`chart_generator.py`)
- Persona-specific imagery for educational materials
- User-specific data insights rendered as interactive charts

### 4. Multi-Agent Development Workflow
- MCP (Model Context Protocol) agent coordination
- File reservation system for conflict-free parallel development
- Documented in `AGENTS.md` and `MCP_AGENT_MAIL_SETUP.md`

---

## Results Achieved

| **Metric** | **Target** | **Achieved** | **Performance** |
|------------|------------|--------------|-----------------|
| Coverage | 100% | **100.00%** | ✅ Target Met |
| Explainability | 100% | **100.00%** | ✅ Target Met |
| Relevance | 90% | **100.00%** | ✅ Exceeded by 10% |
| Latency | <5s | **0.0105s** | ✅ 476x faster |
| Auditability | 100% | **100.00%** | ✅ Target Met |
| Test Count | ≥10 | **80 tests** | ✅ 800% of target |
| Fairness | PASS | **PASS** | ✅ All groups compliant |

**Additional Achievements**:
- 100% test pass rate (80/80 tests passing)
- 69.1% code coverage across modules
- 29 documentation files totaling 150,000+ words
- Zero security vulnerabilities (no real PII, local-first architecture)
- 100+ user decision traces in JSON format for full auditability

---

## Architecture Highlights

**Modular Structure**:
```
SpendSense/
├── ingest/          # Data generation, validation, constants
├── features/        # Behavioral signal detection (4 modules)
├── personas/        # Persona assignment logic
├── recommend/       # Recommendation engine (7 files including AI, video, charts)
├── guardrails/      # Consent, eligibility, tone validation (3 modules)
├── ui/              # 3 user interfaces (Next.js, NiceGUI, Streamlit)
├── api/             # FastAPI REST endpoints
├── eval/            # Evaluation harness with 6 metrics
├── tests/           # 80 unit & integration tests
└── docs/            # 29 markdown files (schema, decisions, traces)
```

**Storage Strategy**:
- **SQLite**: Relational data (users, accounts, transactions, persona assignments, consent audit trail)
- **Parquet**: Analytics-optimized behavioral signals (10,000+ transactions compressed)
- **JSON**: Configuration, decision traces (100+ trace files), evaluation results

**Technology Stack**:
- Python 3.11+ with `uv` environment manager
- FastAPI for REST API (async/await support)
- Next.js 14 App Router for modern web UI
- Streamlit & NiceGUI for operator/demo interfaces
- Pandas & NumPy for data processing
- Pytest for testing (deterministic with seed=42)

---

## Limitations & Future Work

### Acknowledged MVP Limitations

1. **Data Scope**: Synthetic data only—no real Plaid API integration
2. **Architecture**: Local-only system (no authentication, no cloud deployment)
3. **Features**: Rule-based baseline (AI is optional enhancement)
4. **Compliance**: Educational content only—not financial advice compliant for production
5. **Testing**: No load testing or automated UI testing at scale

### Production Readiness Requirements

- User authentication & authorization (OAuth 2.0, JWT)
- Real Plaid API integration with webhook handling
- PII encryption at rest and in transit
- Multi-tenant database architecture
- Horizontal scaling with load balancers
- Regulatory compliance review (CFPB, state-level)
- A/B testing framework for content effectiveness
- Real-time feedback loop integration

### Enhancement Roadmap

- Expanded persona system (10+ personas with granular sub-types)
- Investment account analysis (currently excluded from MVP)
- Tax optimization recommendations
- Credit score tracking and simulation
- Gamified savings challenges
- SMS/email notification system
- Mobile native applications (iOS/Android)

---

## Conclusion

SpendSense demonstrates that **financial AI can be both sophisticated and transparent**. By prioritizing explainability over black-box complexity, consent over assumed permission, and education over sales, the system provides a blueprint for responsible AI in consumer finance.

**Core Principles Achieved**:
- ✅ **Transparency over sophistication**: Every recommendation has a clear "because"
- ✅ **User control over automation**: Consent required, revocable at any time
- ✅ **Education over sales**: No predatory products, tone validation enforced
- ✅ **Fairness built in from day one**: Demographic parity monitored and enforced

The project exceeds all Platinum Project success criteria while maintaining strict ethical guardrails, proving that trustworthy financial AI is not just possible—it's achievable with careful design and unwavering commitment to user protection.

---

## Technical Contact

**Project Lead**: Casey Manos
**Repository**: [GitHub - SpendSense](https://github.com/caseymanos/spendSense)
**Specification Origin**: Bryce Harris (bharris@peak6.com)
**Submission Date**: November 2025

**Quick Start**:
```bash
# Setup
uv sync

# Generate data
uv run python -m ingest.data_generator

# Run tests
uv run pytest tests/ -v

# Launch services
uv run python api/main.py  # API on :8000
npm run dev  # Web UI on :3000 (in web/ directory)
uv run streamlit run ui/app_operator.py  # Operator dashboard on :8081
```

**Documentation**: See `README.md`, `CLAUDE.md`, and 27 additional markdown files in `docs/`

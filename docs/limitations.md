# Known Limitations

**SpendSense MVP V2 - Constraints and Trade-offs**

This document explicitly describes the limitations of the current MVP implementation.

---

## Data Limitations

### 1. Synthetic Data Only

**Limitation:** All data is synthetically generated using Faker and NumPy.

**Impact:**
- No real user financial patterns
- Cannot validate against actual Plaid API responses
- Patterns may not reflect real-world complexity
- Edge cases may be missed

**Mitigation:**
- Use realistic value ranges and distributions
- Model common patterns (subscriptions, payroll)
- Deterministic generation for testing

**Future:** Integrate with Plaid Sandbox API or real anonymized data.

---

### 2. No Real Plaid API Integration

**Limitation:** No actual connection to Plaid's API.

**Impact:**
- Cannot test real-world API errors or rate limits
- No OAuth flow implementation
- No account refresh/update mechanisms
- Missing Plaid-specific features (e.g., identity verification)

**Mitigation:**
- Use Plaid-compatible schema
- Design for future API integration

**Future:** PR #11 could add Plaid Sandbox integration.

---

### 3. Fixed 6-Month Window

**Limitation:** All data covers exactly 6 months of history.

**Impact:**
- Cannot analyze long-term trends (>6 months)
- Insufficient for annual spending patterns
- Limited income stability signals

**Mitigation:**
- 6 months sufficient for MVP persona detection
- Both 30-day and 180-day windows supported

**Future:** Make history duration configurable.

---

## Architecture Limitations

### 4. Local-Only Execution

**Limitation:** Entire system runs on local machine (no cloud deployment).

**Impact:**
- No multi-user scalability
- No distributed processing
- SQLite single-writer limitations
- No high-availability setup

**Mitigation:**
- Adequate for MVP demo and testing
- Clear deployment path to cloud (FastAPI → AWS Lambda, SQLite → RDS)

**Future:** Dockerize and deploy to AWS/GCP.

---

### 5. No Authentication or Authorization

**Limitation:** No user login, no JWT tokens, no RBAC.

**Impact:**
- Any user can access any data
- No operator role enforcement
- Consent changes not authenticated
- Not production-ready

**Mitigation:**
- Fine for local demo environment
- FastAPI supports OAuth2/JWT easily

**Future:** PR #11 could add auth layer.

---

### 6. No Real-Time Data Refresh

**Limitation:** Data is static once generated; no periodic updates.

**Impact:**
- Cannot simulate account balance changes over time
- Recommendations don't update automatically
- No "live" transaction feed

**Mitigation:**
- MVP focuses on point-in-time analysis
- Re-run data generation to simulate updates

**Future:** Add scheduled data refresh and incremental updates.

---

## Feature Limitations

### 7. Rule-Based Recommendations Only

**Limitation:** No machine learning or NLP; pure rule-based logic.

**Impact:**
- Cannot learn from user feedback
- Fixed recommendation content
- No personalization beyond personas
- Cannot detect novel patterns

**Mitigation:**
- Aligns with MVP "transparency over sophistication" principle
- Rule-based systems are fully explainable
- Adequate for 5 predefined personas

**Future:** Post-MVP could add ML models with LIME/SHAP explainability.

---

### 8. Five Fixed Personas

**Limitation:** Only 5 personas defined (High Utilization, Variable Income, Subscription Heavy, Savings Builder, Custom).

**Impact:**
- Cannot capture all financial behavior patterns
- Users forced into nearest persona
- Limited personalization granularity

**Mitigation:**
- Persona priority handles overlaps
- Custom persona slot reserved for future expansion

**Future:** Add dynamic persona generation or sub-personas.

---

### 9. No Feedback Loop

**Limitation:** System doesn't learn from user actions (clicks, dismissals).

**Impact:**
- Cannot improve recommendations over time
- No A/B testing capability
- No engagement metrics

**Mitigation:**
- MVP focuses on core recommendation engine
- Feedback API endpoint stubbed for future use

**Future:** Implement feedback collection and analytics.

---

## Compliance Limitations

### 10. Not Financial Advice Compliant

**Limitation:** Disclaimer present but no legal review for regulatory compliance.

**Impact:**
- Cannot be used for actual financial advice
- May not meet SEC/FINRA requirements
- Liability not assessed

**Mitigation:**
- Clear "educational content only" disclaimer
- Recommendations designed to avoid advice territory

**Future:** Legal review and regulatory compliance assessment.

---

### 11. No PII Encryption

**Limitation:** Data stored in plaintext SQLite (even though it's synthetic).

**Impact:**
- If used with real data, violates security best practices
- No encryption at rest
- No field-level encryption

**Mitigation:**
- All data is synthetic (no real PII)
- Local-only storage

**Future:** Add SQLCipher or AWS KMS encryption.

---

### 12. Limited Fairness Metrics

**Limitation:** Demographics limited to 4 categories (age, gender, income, region).

**Impact:**
- Cannot detect bias across other dimensions (race, disability, etc.)
- US-centric regional breakdown
- Coarse income tiers

**Mitigation:**
- Sufficient for MVP fairness demonstration
- Framework extensible to additional demographics

**Future:** Expand demographic categories with privacy safeguards.

---

## Testing Limitations

### 13. No Load Testing

**Limitation:** No performance testing under scale.

**Impact:**
- Unknown behavior with 10,000+ users
- No latency benchmarks
- SQLite may not scale

**Mitigation:**
- Target is <5s per user for 100 users
- Clear migration path to PostgreSQL

**Future:** Add load testing with Locust or k6.

---

### 14. Manual UI Testing

**Limitation:** No automated UI tests (Streamlit and FastAPI docs only).

**Impact:**
- UI regressions not caught automatically
- No visual regression testing

**Mitigation:**
- Streamlit's simplicity reduces UI complexity
- Core logic covered by unit/integration tests

**Future:** Add Playwright or Selenium tests.

---

## Scope Exclusions

### 15. Not Included in MVP

The following features are explicitly out of scope:

- ❌ Investment account analysis
- ❌ Tax optimization recommendations
- ❌ Bill negotiation features
- ❌ Credit score tracking
- ❌ Debt payoff calculators (beyond recommendations)
- ❌ Multi-language support
- ❌ Mobile native apps (Streamlit web only)
- ❌ Email/SMS notifications
- ❌ Third-party integrations (beyond Plaid)
- ❌ Gamification or rewards

**Rationale:** MVP focuses on core recommendation engine with guardrails. Additional features can be added post-MVP based on user feedback.

---

## Acceptable Trade-offs

These limitations are **intentional design choices** for the MVP:

✅ Synthetic data → Faster iteration, no privacy concerns
✅ Local-only → Simpler setup, no cloud costs
✅ Rule-based → Full explainability, easier to audit
✅ Five personas → Manageable scope, covers common patterns
✅ No auth → Faster MVP development

---

## Revision History

| Date | PR | Changes |
|------|-------|---------|
| 2025-11-03 | #1 | Initial limitations document created |

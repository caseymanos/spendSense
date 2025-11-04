Excellent — here’s **Part 3 of 3** for your merged and extended PRD:
**`PRD_V2_Part3_Evaluation_and_Quality.md`**

This final section completes the continuous numbering and covers evaluation metrics, testing, documentation, success criteria, and project governance — tying back to the final two build phases in the Peak6 specification.

---

# **SpendSense MVP V2 — Part 3: Evaluation & Quality Assurance**

## **10. Evaluation Harness**

**Goal:** Quantitatively measure system performance, explainability, and fairness while maintaining full transparency of logic and data provenance.

### **10.1 Metrics Computed**

| Metric             | Description                                                   | Target       |
| ------------------ | ------------------------------------------------------------- | ------------ |
| **Coverage**       | % of users with ≥3 detected behaviors and ≥1 persona assigned | 100%         |
| **Explainability** | % of recommendations with explicit “because” rationale        | 100%         |
| **Relevance**      | Rule-based scoring of persona → education alignment           | ≥90%         |
| **Latency**        | Avg. time to generate recommendations per user                | < 5s         |
| **Fairness**       | Distribution parity across demographics                       | ±10% of mean |
| **Auditability**   | % of recommendations with decision-trace JSONs                | 100%         |

### **10.2 Implementation**

* Module: `eval/run.py`
* Metrics derived from output of `features/`, `personas/`, and `recommend/`
* Time captured via `time.perf_counter()`
* Stored as structured JSON, CSV, and Markdown summary

```bash
uv run python -m eval.run --input data/transactions.parquet --output eval/results.json
```

### **10.3 Outputs**

| File                    | Purpose                                |
| ----------------------- | -------------------------------------- |
| `/eval/results.json`    | Machine-readable metrics               |
| `/eval/results.csv`     | Tabular export for analysis            |
| `/eval/summary.md`      | Markdown overview for operators        |
| `/docs/eval_summary.md` | Linked in decision log for audit trail |

Each evaluation run appends its results with timestamps to allow longitudinal tracking.

---

## **11. Testing Plan**

**Framework:** `pytest`
**Goal:** Minimum of 10 deterministic, seed-stable tests validating end-to-end pipeline reliability.

| #  | Test                      | Scope       | Expected Result                                          |
| -- | ------------------------- | ----------- | -------------------------------------------------------- |
| 1  | Schema Validation         | Ingestion   | Schema must match Plaid spec; raise ValueError otherwise |
| 2  | Synthetic Data Generation | Data        | Deterministic output when seed fixed                     |
| 3  | Signal Detection          | Features    | All 4 categories return expected metrics                 |
| 4  | Persona Assignment        | Personas    | Correct persona given known test data                    |
| 5  | Recommendation Output     | Recommender | 3–5 recs, 1–3 offers per persona                         |
| 6  | Consent Enforcement       | Guardrails  | Processing blocked when consent=False                    |
| 7  | Tone Validation           | Guardrails  | Detects and removes negative phrasing                    |
| 8  | Eligibility Filters       | Guardrails  | Ineligible offers excluded                               |
| 9  | Evaluation Harness        | Eval        | Valid metrics JSON/CSV generated                         |
| 10 | Fairness Metric           | Eval        | Parity metric computed correctly per demographic         |

Tests reside in `/tests/` and log deterministic outputs to `/docs/test_results.md`.

---

## **12. Documentation Outputs**

**Purpose:** Guarantee traceability, reproducibility, and transparency.

| File                          | Description                                              |
| ----------------------------- | -------------------------------------------------------- |
| `/docs/schema.md`             | Plaid-compatible data model with examples                |
| `/docs/decision_log.md`       | Running record of design choices and operator overrides  |
| `/docs/limitations.md`        | Known simplifications and MVP boundaries                 |
| `/docs/traces/{user_id}.json` | Per-user trace logs linking inputs → persona → rationale |
| `/docs/eval_summary.md`       | Summary of latest evaluation metrics                     |
| `/docs/test_results.md`       | Unit/integration test summaries                          |
| `/docs/fairness_report.md`    | Demographic parity visualization                         |
| `/docs/README.md`             | Project overview and compliance statement                |

All documentation auto-generated or manually appended during each pipeline run.

---

## **13. Success Criteria**

| Category           | Metric                            | Target        | Validation      |
| ------------------ | --------------------------------- | ------------- | --------------- |
| **Coverage**       | Users with persona + ≥3 behaviors | 100%          | Automated test  |
| **Explainability** | Recs include rationales           | 100%          | Audit sample    |
| **Latency**        | Generation time per user          | < 5 s         | Benchmark run   |
| **Auditability**   | Trace logs exist per rec          | 100%          | File validation |
| **Fairness**       | Demographic group parity          | ±10% variance | Eval harness    |
| **Testing**        | Passing unit/integration tests    | ≥10           | CI log          |
| **Documentation**  | Schema + logs complete            | ✅             | Manual review   |

---

## **14. Risk Assessment & Limitations**

| Risk                           | Impact   | Mitigation                               |
| ------------------------------ | -------- | ---------------------------------------- |
| **Synthetic data unrealistic** | Moderate | Add variability + manual review          |
| **Persona overlap ambiguity**  | Moderate | Use explicit priority ordering           |
| **Operator overrides abused**  | Low      | Add audit trail + later auth             |
| **Streamlit state errors**     | Low      | Use `st.session_state` carefully         |
| **Fairness misinterpretation** | Moderate | Document demographic assumptions clearly |
| **Scope creep (AI features)**  | High     | Lock AI/NLP to post-MVP                  |
| **Data volume performance**    | Low      | Use Parquet and vectorized ops           |

**Known Limitations:**

* Synthetic-only dataset (no real Plaid API calls)
* Single-user local runtime (no multi-tenant support)
* Manual fairness review (not automated ethics testing)
* No authentication in MVP Streamlit apps
* No persistent feedback loop (user learning not yet tracked)

---

## **15. Implementation Phases Summary**

| Phase                        | Focus                                                          | Deliverables                    |
| ---------------------------- | -------------------------------------------------------------- | ------------------------------- |
| **1. Data Foundation**       | Synthetic data generation, schema validation, consent tracking | `ingest/`, `features/`, `/data` |
| **2. Feature Engineering**   | Behavioral signal detection & metrics                          | `features/` modules             |
| **3. Persona System**        | Persona logic & prioritization                                 | `personas/assignment.py`        |
| **4. Recommendation Engine** | Rule-based content + rationale                                 | `recommend/` modules            |
| **5. Guardrails & UX**       | Consent enforcement, tone validation, Streamlit UIs            | `guardrails/`, `ui/`            |
| **6. Evaluation & QA**       | Metrics, fairness, testing, docs                               | `eval/`, `docs/`, `tests/`      |

---

## **16. Deliverables**

1. **Codebase:**

   * Full modular structure (`ingest`, `features`, `personas`, `recommend`, `guardrails`, `ui`, `eval`, `docs`, `tests`)
2. **Streamlit Apps:**

   * `app_user.py` – End-user educational interface
   * `app_operator.py` – Operator dashboard with metrics and trace views
3. **Evaluation Outputs:**

   * `eval/results.json` + `/eval/summary.md`
4. **Documentation:**

   * `/docs/decision_log.md`, `/docs/schema.md`, `/docs/eval_summary.md`
5. **Testing Suite:**

   * ≥10 passing tests logged in `/docs/test_results.md`
6. **Fairness Report:**

   * `/docs/fairness_report.md` summarizing demographic parity
7. **README:**

   * Setup, run instructions, and compliance disclaimer

---

## **17. Final Note**

> **Financial AI must be explainable and auditable.**
> Every recommendation should cite a concrete data point.
> The system must educate, not persuade.
> Transparency, fairness, and user consent are non-negotiable pillars of SpendSense.

---

**Contact:**
Project Lead: *Casey Manos*
Technical Contact (spec origin): *Bryce Harris – [bharris@peak6.com](mailto:bharris@peak6.com)*

---

✅ *End of SpendSense MVP V2 — Part 3: Evaluation & Quality Assurance*

Together, Parts 1–3 provide a full, spec-compliant, modular PRD ready for development and submission under the Peak6 SpendSense challenge.

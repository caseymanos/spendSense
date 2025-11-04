graph LR
%% ============================================
%% FINAL PRD-PERFECT SYSTEM (SpendSense)
%% ============================================

%% External Actors
EndUser([End User<br/>Bank Customer])
Operator([Operator<br/>Compliance Team])
API[("FastAPI<br/>Endpoints")]

%% External Data
CSV[("CSV/JSON<br/>Synthetic/Plaid Data")]

%% ---------------- PHASE 1: INGESTION ----------------
subgraph Ingest["1️⃣ Ingestion (ingest/)"]
    Gen["data_generator.py<br/>faker, numpy<br/>seed=42"]
    Valid["validators.py<br/>Pydantic"]
    Load["loader.py<br/>pandas"]
end

%% ---------------- PHASE 2: STORAGE ----------------
subgraph Storage["2️⃣ Storage (data/)"]
    SQLite[("users.sqlite<br/>Consent, Demographics (metrics-only)")]
    Parquet[("transactions.parquet")]
end

%% ---------------- PHASE 3: FEATURES ----------------
subgraph Features["3️⃣ Features (features/)"]
    Sub["subscriptions.py"]
    Sav["savings.py"]
    Cred["credit.py"]
    Inc["income.py"]
end
FeatOut[("signals.parquet<br/>30d / 180d")]

%% ---------------- PHASE 4: PERSONAS ----------------
subgraph Personas["4️⃣ Personas (personas/)"]
    Pers["persona_engine.py<br/>map users → personas (1–5)"]
    PersConf["personas_config.json<br/>rules, thresholds"]
end

%% ---------------- PHASE 5: RECOMMENDER ----------------
subgraph Recommend["5️⃣ Recommender (recommend/)"]
    Rec["recommend_engine.py<br/>select content + offers"]
    Cat["content_catalog.py<br/>educational articles"]
    Offer["offer_catalog.py<br/>partner offers"]
    Rationale["rationale_generator.py<br/>explain each rec + disclosure"]
end

%% ---------------- PHASE 6: GUARDRAILS ----------------
subgraph Guardrails["6️⃣ Guardrails (guardrails/)"]
    Consent["consent_checker.py"]
    Tone["tone_validator.py"]
    Elig["eligibility_checker.py<br/>eligibility_config.json"]
    Pred["predatory_filter.py"]
    GuardOut["guardrails_report.json"]
end

%% ---------------- PHASE 7: EVALUATION ----------------
subgraph Eval["7️⃣ Evaluation (eval/)"]
    EvalRun["run.py<br/>metrics: coverage, explainability,<br/>latency, fairness, auditability"]
    Fair["fairness_metrics.py<br/>uses demographics (metrics-only)"]
    Audit["trace_audit.py"]
    EvalOut["eval_summary.md / eval_results.csv"]
end

%% ---------------- PHASE 8: UI ----------------
subgraph UI["8️⃣ User & Operator Interfaces (ui/)"]
    UserDash["user_dashboard.py<br/>Streamlit - learn & act"]
    OperDash["operator_dashboard.py<br/>review, override, trace view"]
end

%% ---------------- PHASE 9: DOCS ----------------
subgraph Docs["9️⃣ Documentation & Traceability (docs/)"]
    Trace["traces/{user_id}.json"]
    Overrides["overrides.jsonl"]
    Logs["decision_log.md"]
end

%% ---------------- FastAPI Endpoints ----------------
subgraph APIEndpoints["🔗 FastAPI Layer (api/)"]
    E1["POST /users"]
    E2["POST /consent"]
    E3["GET /profile/{id}"]
    E4["GET /recommendations/{id}"]
    E5["POST /feedback"]
    E6["GET /operator/review"]
    E7["POST /operator/review"]
    E8["GET /eval/summary"]
end

%% ============================================
%% FLOWS
%% ============================================
CSV --> Gen --> Valid --> Load --> SQLite
Load --> Parquet
SQLite --> Features
Parquet --> Features
Features --> FeatOut --> Personas
Personas --> Recommend
Recommend --> Guardrails
Guardrails --> Eval
Eval --> UI
UI --> Docs
Guardrails --> Docs
Recommend --> Docs
Personas --> Docs
Features --> Docs
Eval --> Docs
SQLite --> Fair
API --> E1
API --> E2
API --> E3
API --> E4
API --> E5
API --> E6
API --> E7
API --> E8
EndUser -->|via FastAPI / Streamlit| API
Operator -->|review + override| UI
Operator -->|actions logged| Overrides
Overrides --> Eval
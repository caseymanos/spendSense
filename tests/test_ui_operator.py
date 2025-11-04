"""
Unit tests for UI operator attribution.

This test stubs Streamlit to import ui.app_operator without requiring the
streamlit package, then verifies that log_operator_override writes the
operator name into the decision log and trace JSON.
"""

import sys
import json
import types


def test_log_operator_override_writes_operator_name(tmp_path, monkeypatch):
    # Stub a minimal streamlit module to allow importing ui.app_operator
    st = types.ModuleType("streamlit")

    def _noop(*args, **kwargs):
        return None

    # Minimal surface used at import and in logging function
    st.set_page_config = _noop
    st.error = _noop

    sys.modules["streamlit"] = st

    # Import after stubbing streamlit
    import importlib

    app_operator = importlib.import_module("ui.app_operator")

    # Point paths to tmp directory
    decision_log_path = tmp_path / "decision_log.md"
    traces_dir = tmp_path / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(app_operator, "DECISION_LOG_PATH", decision_log_path)
    monkeypatch.setattr(app_operator, "TRACES_DIR", traces_dir)

    # Execute the logging function
    user_id = "U_TEST_123"
    operator = "Test Operator"
    action = "approve"
    reason = "Recommendation approved after review"
    title = "Sample Recommendation"

    ok = app_operator.log_operator_override(
        user_id=user_id,
        operator_name=operator,
        action=action,
        reason=reason,
        recommendation_title=title,
    )

    assert ok is True

    # Verify decision log contains operator name
    assert decision_log_path.exists()
    log_text = decision_log_path.read_text()
    assert f"**Operator:** {operator}" in log_text
    assert f"**Action:** {action.upper()}" in log_text

    # Verify trace JSON updated with operator attribution
    trace_file = traces_dir / f"{user_id}.json"
    assert trace_file.exists()
    trace = json.loads(trace_file.read_text())
    assert trace.get("user_id") == user_id
    assert "guardrail_decisions" in trace and len(trace["guardrail_decisions"]) >= 1
    last = trace["guardrail_decisions"][-1]
    assert last["operator"] == operator
    assert last["action"] == action
    assert last.get("recommendation_title") == title

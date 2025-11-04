"""
Tests to validate documentation completeness and output file integrity.

These tests ensure all required documentation files exist and contain
appropriate content, and that all pipeline outputs are generated correctly.

PR #10: Documentation & Final Polish
"""

import os
import json
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class TestDocumentationCompleteness:
    """Verify all required documentation files exist and are non-empty."""

    def test_schema_documentation_exists(self):
        """Test that docs/schema.md exists and is non-empty."""
        schema_file = PROJECT_ROOT / "docs" / "schema.md"
        assert schema_file.exists(), "docs/schema.md does not exist"
        assert schema_file.stat().st_size > 0, "docs/schema.md is empty"

        # Check for essential sections
        content = schema_file.read_text()
        assert "User" in content, "schema.md missing User entity documentation"
        assert "Account" in content, "schema.md missing Account entity documentation"
        assert (
            "Transaction" in content
        ), "schema.md missing Transaction entity documentation"

    def test_decision_log_exists(self):
        """Test that docs/decision_log.md exists and is non-empty."""
        decision_log = PROJECT_ROOT / "docs" / "decision_log.md"
        assert decision_log.exists(), "docs/decision_log.md does not exist"
        assert decision_log.stat().st_size > 0, "docs/decision_log.md is empty"

        # Check for essential sections
        content = decision_log.read_text()
        assert (
            "Decision" in content or "decision" in content
        ), "decision_log.md missing decision documentation"
        # Should have multiple decisions documented
        assert (
            content.count("##") >= 5
        ), "decision_log.md should contain multiple documented decisions"

    def test_limitations_documentation_exists(self):
        """Test that docs/limitations.md exists and is non-empty."""
        limitations_file = PROJECT_ROOT / "docs" / "limitations.md"
        assert limitations_file.exists(), "docs/limitations.md does not exist"
        assert limitations_file.stat().st_size > 0, "docs/limitations.md is empty"

        # Check for essential sections
        content = limitations_file.read_text()
        assert (
            "limitation" in content.lower() or "constraint" in content.lower()
        ), "limitations.md missing limitation documentation"

    def test_eval_summary_exists(self):
        """Test that docs/eval_summary.md exists and is non-empty."""
        eval_summary = PROJECT_ROOT / "docs" / "eval_summary.md"
        assert eval_summary.exists(), "docs/eval_summary.md does not exist"
        assert eval_summary.stat().st_size > 0, "docs/eval_summary.md is empty"

        # Check for essential sections
        content = eval_summary.read_text()
        assert (
            "Coverage" in content
        ), "eval_summary.md missing Coverage metric documentation"
        assert (
            "Explainability" in content
        ), "eval_summary.md missing Explainability metric documentation"
        assert (
            "Latency" in content
        ), "eval_summary.md missing Latency metric documentation"

    def test_test_results_exists(self):
        """Test that docs/test_results.md exists and is non-empty."""
        test_results = PROJECT_ROOT / "docs" / "test_results.md"
        assert test_results.exists(), "docs/test_results.md does not exist"
        assert test_results.stat().st_size > 0, "docs/test_results.md is empty"

        # Check for test counts
        content = test_results.read_text()
        assert (
            "test" in content.lower() or "Test" in content
        ), "test_results.md missing test documentation"

    def test_fairness_report_exists(self):
        """Test that docs/fairness_report.md exists and is non-empty."""
        fairness_report = PROJECT_ROOT / "docs" / "fairness_report.md"
        assert fairness_report.exists(), "docs/fairness_report.md does not exist"
        assert fairness_report.stat().st_size > 0, "docs/fairness_report.md is empty"

        # Check for fairness metrics
        content = fairness_report.read_text()
        assert (
            "fairness" in content.lower() or "demographic" in content.lower()
        ), "fairness_report.md missing fairness documentation"

    def test_readme_contains_setup_instructions(self):
        """Test that README.md contains setup and usage instructions."""
        readme = PROJECT_ROOT / "README.md"
        assert readme.exists(), "README.md does not exist"
        assert readme.stat().st_size > 0, "README.md is empty"

        # Check for essential sections
        content = readme.read_text()
        assert (
            "uv" in content.lower() or "install" in content.lower()
        ), "README.md missing installation instructions"
        assert (
            "streamlit" in content.lower()
        ), "README.md missing Streamlit app launch instructions"
        assert (
            "Success Criteria" in content
        ), "README.md missing Success Criteria section"

    def test_trace_directory_exists(self):
        """Test that docs/traces/ directory exists and contains trace files."""
        traces_dir = PROJECT_ROOT / "docs" / "traces"
        assert traces_dir.exists(), "docs/traces/ directory does not exist"
        assert traces_dir.is_dir(), "docs/traces/ is not a directory"

        # Check that at least one trace file exists
        trace_files = list(traces_dir.glob("user_*.json"))
        assert (
            len(trace_files) > 0
        ), "docs/traces/ directory contains no user trace files"


class TestOutputFileValidation:
    """Verify all pipeline output files exist and are valid."""

    def test_users_sqlite_exists_and_valid(self):
        """Test that data/users.sqlite exists and has the user table."""
        db_path = PROJECT_ROOT / "data" / "users.sqlite"
        assert db_path.exists(), "data/users.sqlite does not exist"
        assert db_path.stat().st_size > 0, "data/users.sqlite is empty"

        # Connect and verify tables exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check users table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        assert cursor.fetchone() is not None, "users table does not exist in database"

        # Check users table has data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        assert user_count > 0, "users table is empty"

        conn.close()

    def test_transactions_parquet_exists_and_readable(self):
        """Test that data/transactions.parquet exists and is readable."""
        parquet_path = PROJECT_ROOT / "data" / "transactions.parquet"
        assert parquet_path.exists(), "data/transactions.parquet does not exist"
        assert parquet_path.stat().st_size > 0, "data/transactions.parquet is empty"

        # Try to read the parquet file
        df = pd.read_parquet(parquet_path)
        assert len(df) > 0, "transactions.parquet contains no data"
        # Transactions use account_id (which links to users via accounts table)
        assert (
            "account_id" in df.columns
        ), "transactions.parquet missing account_id column"
        assert (
            "transaction_id" in df.columns
        ), "transactions.parquet missing transaction_id column"

    def test_signals_parquet_exists(self):
        """Test that features/signals.parquet exists."""
        signals_path = PROJECT_ROOT / "features" / "signals.parquet"
        assert signals_path.exists(), "features/signals.parquet does not exist"
        assert signals_path.stat().st_size > 0, "features/signals.parquet is empty"

        # Try to read the parquet file
        df = pd.read_parquet(signals_path)
        assert len(df) > 0, "signals.parquet contains no data"
        assert "user_id" in df.columns, "signals.parquet missing user_id column"

    def test_eval_results_json_exists_and_valid(self):
        """Test that eval results JSON exists and is valid."""
        # Look for any eval results file (timestamped or symlinked)
        eval_dir = PROJECT_ROOT / "eval"
        results_files = list(eval_dir.glob("results*.json"))

        assert len(results_files) > 0, "No eval/results*.json files found"

        # Check the first results file
        results_file = results_files[0]
        assert results_file.stat().st_size > 0, f"{results_file.name} is empty"

        # Try to parse as JSON
        with open(results_file, "r") as f:
            results = json.load(f)

        # Verify essential metrics exist
        assert "metrics" in results, "eval results missing 'metrics' key"
        assert (
            "coverage" in results["metrics"]
        ), "eval results missing 'coverage' metric"
        assert (
            "explainability" in results["metrics"]
        ), "eval results missing 'explainability' metric"

    def test_eval_results_csv_exists_and_readable(self):
        """Test that eval results CSV exists and is readable."""
        # Look for any eval results CSV file
        eval_dir = PROJECT_ROOT / "eval"
        csv_files = list(eval_dir.glob("results*.csv"))

        assert len(csv_files) > 0, "No eval/results*.csv files found"

        # Check the first CSV file
        csv_file = csv_files[0]
        assert csv_file.stat().st_size > 0, f"{csv_file.name} is empty"

        # Try to read as CSV
        df = pd.read_csv(csv_file)
        assert len(df) > 0, "eval results CSV contains no data"

    def test_trace_json_files_valid(self):
        """Test that at least one trace JSON file is valid."""
        traces_dir = PROJECT_ROOT / "docs" / "traces"
        trace_files = list(traces_dir.glob("user_*.json"))

        assert len(trace_files) > 0, "No trace JSON files found"

        # Check first trace file
        trace_file = trace_files[0]
        assert trace_file.stat().st_size > 0, f"{trace_file.name} is empty"

        # Try to parse as JSON
        with open(trace_file, "r") as f:
            trace = json.load(f)

        # Verify essential fields
        assert "user_id" in trace, "trace JSON missing 'user_id' field"

    def test_config_json_exists_and_valid(self):
        """Test that data/config.json exists and is valid."""
        config_path = PROJECT_ROOT / "data" / "config.json"
        assert config_path.exists(), "data/config.json does not exist"
        assert config_path.stat().st_size > 0, "data/config.json is empty"

        # Try to parse as JSON
        with open(config_path, "r") as f:
            config = json.load(f)

        # Handle both old flat format and new nested format
        if "config" in config:
            # New nested format with operator controls
            inner_config = config["config"]
            assert "num_users" in inner_config, "config.json missing 'num_users' field"
            assert "seed" in inner_config, "config.json missing 'seed' field"
            # Optional: verify controls section exists
            assert "controls" in config, "config.json missing 'controls' section"
        else:
            # Old flat format (backwards compatibility)
            assert "num_users" in config, "config.json missing 'num_users' field"
            assert "seed" in config, "config.json missing 'seed' field"


class TestDocumentationQuality:
    """Verify documentation meets quality standards."""

    def test_all_required_docs_exist(self):
        """Test that all required documentation files exist."""
        required_docs = [
            "docs/schema.md",
            "docs/decision_log.md",
            "docs/limitations.md",
            "docs/eval_summary.md",
            "docs/test_results.md",
            "docs/fairness_report.md",
            "README.md",
        ]

        for doc_path in required_docs:
            full_path = PROJECT_ROOT / doc_path
            assert (
                full_path.exists()
            ), f"Required documentation file {doc_path} does not exist"

    def test_all_output_files_exist(self):
        """Test that all expected output files exist."""
        required_outputs = [
            "data/users.sqlite",
            "data/transactions.parquet",
            "data/config.json",
            "features/signals.parquet",
        ]

        for output_path in required_outputs:
            full_path = PROJECT_ROOT / output_path
            assert (
                full_path.exists()
            ), f"Required output file {output_path} does not exist"

    def test_success_criteria_documented_in_readme(self):
        """Test that README.md documents all success criteria."""
        readme = PROJECT_ROOT / "README.md"
        content = readme.read_text()

        required_metrics = [
            "Coverage",
            "Explainability",
            "Latency",
            "Auditability",
            "Fairness",
            "Tests",
        ]

        for metric in required_metrics:
            assert (
                metric in content
            ), f"README.md missing '{metric}' in Success Criteria section"

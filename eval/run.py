"""
Evaluation Harness - Main Entry Point

This module orchestrates the complete evaluation pipeline:
1. Calculate 5 core metrics (coverage, explainability, relevance, latency, auditability)
2. Calculate fairness metric (demographic parity)
3. Generate timestamped outputs (JSON, CSV, Markdown)
4. Create symlinks to latest results
5. Print summary to console

Usage:
    uv run python -m eval.run
    uv run python -m eval.run --db data/users.sqlite --output eval/results.json
    uv run python -m eval.run --timestamp 2025-11-03T15-30-00
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import pandas as pd

# Import metric calculation functions
from eval.metrics import calculate_all_metrics
from eval.fairness import (
    calculate_fairness_metrics,
    generate_fairness_report_markdown,
)


# ============================================
# TIMESTAMP GENERATION
# ============================================


def generate_timestamp() -> str:
    """
    Generate timestamp in ISO 8601 format for file naming.

    Returns:
        Timestamp string (YYYY-MM-DDTHH-MM-SS)
    """
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


# ============================================
# JSON OUTPUT GENERATION
# ============================================


def generate_json_output(
    metrics: Dict[str, Any],
    fairness: Dict[str, Any],
    timestamp: str,
) -> Dict[str, Any]:
    """
    Generate structured JSON output with all evaluation results.

    Args:
        metrics: Results from calculate_all_metrics()
        fairness: Results from calculate_fairness_metrics()
        timestamp: Evaluation timestamp

    Returns:
        Complete evaluation results dictionary
    """
    output = {
        "metadata": {
            "timestamp": timestamp,
            "version": "PR #8 Evaluation Harness",
            "total_users": metrics["summary"]["total_users"],
            "total_personas": metrics["summary"]["total_personas"],
            "total_traces": metrics["summary"]["total_traces"],
        },
        "metrics": {
            "coverage": {
                "value": metrics["coverage"]["value"],
                "target": metrics["coverage"]["metadata"]["target"],
                "passes": metrics["coverage"]["metadata"]["passes"],
                "users_with_both": metrics["coverage"]["metadata"]["users_with_both"],
            },
            "explainability": {
                "value": metrics["explainability"]["value"],
                "target": metrics["explainability"]["metadata"]["target"],
                "passes": metrics["explainability"]["metadata"]["passes"],
                "total_recommendations": metrics["explainability"]["metadata"][
                    "total_recommendations"
                ],
            },
            "relevance": {
                "value": metrics["relevance"]["value"],
                "target": metrics["relevance"]["metadata"]["target"],
                "passes": metrics["relevance"]["metadata"]["passes"],
                "total_recommendations": metrics["relevance"]["metadata"]["total_recommendations"],
            },
            "latency": {
                "value": metrics["latency"]["value"],
                "target": metrics["latency"]["metadata"]["target"],
                "passes": metrics["latency"]["metadata"]["passes"],
                "mean_seconds": metrics["latency"]["metadata"]["mean_seconds"],
                "p95_seconds": metrics["latency"]["metadata"]["p95_seconds"],
            },
            "auditability": {
                "value": metrics["auditability"]["value"],
                "target": metrics["auditability"]["metadata"]["target"],
                "passes": metrics["auditability"]["metadata"]["passes"],
                "completeness_percentage": metrics["auditability"]["metadata"][
                    "completeness_percentage"
                ],
            },
            "fairness": {
                "value": fairness["all_demographics_pass"],
                "target": True,
                "passes": fairness["all_demographics_pass"],
                "overall_persona_rate": fairness["overall_persona_rate"],
                "failing_demographics": fairness["failing_demographics"],
            },
        },
        "detailed_results": {
            "coverage": metrics["coverage"]["metadata"],
            "explainability": metrics["explainability"]["metadata"],
            "relevance": metrics["relevance"]["metadata"],
            "latency": metrics["latency"]["metadata"],
            "auditability": metrics["auditability"]["metadata"],
            "fairness": fairness,
        },
        "summary": {
            "all_metrics_pass": metrics["summary"]["all_metrics_pass"]
            and fairness["all_demographics_pass"],
            "metrics_passing": sum(
                [
                    metrics["coverage"]["metadata"]["passes"],
                    metrics["explainability"]["metadata"]["passes"],
                    metrics["relevance"]["metadata"]["passes"],
                    metrics["latency"]["metadata"]["passes"],
                    metrics["auditability"]["metadata"]["passes"],
                    fairness["all_demographics_pass"],
                ]
            ),
            "metrics_total": 6,
        },
    }

    return output


# ============================================
# CSV OUTPUT GENERATION
# ============================================


def generate_csv_output(
    metrics: Dict[str, Any],
    fairness: Dict[str, Any],
) -> pd.DataFrame:
    """
    Generate tabular CSV output for spreadsheet analysis.

    Args:
        metrics: Results from calculate_all_metrics()
        fairness: Results from calculate_fairness_metrics()

    Returns:
        DataFrame with metric rows
    """
    rows = []

    # Coverage
    rows.append(
        {
            "metric": "coverage",
            "value": metrics["coverage"]["value"],
            "target": metrics["coverage"]["metadata"]["target"],
            "passes": metrics["coverage"]["metadata"]["passes"],
            "unit": "percentage",
        }
    )

    # Explainability
    rows.append(
        {
            "metric": "explainability",
            "value": metrics["explainability"]["value"],
            "target": metrics["explainability"]["metadata"]["target"],
            "passes": metrics["explainability"]["metadata"]["passes"],
            "unit": "percentage",
        }
    )

    # Relevance
    rows.append(
        {
            "metric": "relevance",
            "value": metrics["relevance"]["value"],
            "target": metrics["relevance"]["metadata"]["target"],
            "passes": metrics["relevance"]["metadata"]["passes"],
            "unit": "percentage",
        }
    )

    # Latency
    rows.append(
        {
            "metric": "latency",
            "value": metrics["latency"]["value"],
            "target": metrics["latency"]["metadata"]["target"],
            "passes": metrics["latency"]["metadata"]["passes"],
            "unit": "seconds",
        }
    )

    # Auditability
    rows.append(
        {
            "metric": "auditability",
            "value": metrics["auditability"]["value"],
            "target": metrics["auditability"]["metadata"]["target"],
            "passes": metrics["auditability"]["metadata"]["passes"],
            "unit": "percentage",
        }
    )

    # Fairness
    rows.append(
        {
            "metric": "fairness",
            "value": 100.0 if fairness["all_demographics_pass"] else 0.0,
            "target": 100.0,
            "passes": fairness["all_demographics_pass"],
            "unit": "boolean",
        }
    )

    df = pd.DataFrame(rows)
    return df


# ============================================
# MARKDOWN SUMMARY GENERATION
# ============================================


def generate_summary_markdown(
    metrics: Dict[str, Any],
    fairness: Dict[str, Any],
    timestamp: str,
) -> str:
    """
    Generate human-readable markdown summary for docs/eval_summary.md.

    Args:
        metrics: Results from calculate_all_metrics()
        fairness: Results from calculate_fairness_metrics()
        timestamp: Evaluation timestamp

    Returns:
        Markdown string
    """
    total_users = metrics["summary"]["total_users"]
    all_pass = metrics["summary"]["all_metrics_pass"] and fairness["all_demographics_pass"]

    md = f"""# Evaluation Summary - SpendSense

**Generated**: {timestamp}

## Overall Status

{"✅ **ALL METRICS PASS**" if all_pass else "❌ **SOME METRICS FAIL**"}

**Total Users**: {total_users}
**Metrics Passing**: {sum([metrics["coverage"]["metadata"]["passes"], metrics["explainability"]["metadata"]["passes"], metrics["relevance"]["metadata"]["passes"], metrics["latency"]["metadata"]["passes"], metrics["auditability"]["metadata"]["passes"], fairness["all_demographics_pass"]])}/6

---

## Core Metrics

### 1. Coverage
**Definition**: % of users with meaningful persona + ≥3 detected behaviors

- **Value**: {metrics["coverage"]["value"]:.2f}%
- **Target**: {metrics["coverage"]["metadata"]["target"]:.2f}%
- **Status**: {"✅ PASS" if metrics["coverage"]["metadata"]["passes"] else "❌ FAIL"}
- **Details**:
  - Total users: {metrics["coverage"]["metadata"]["total_users"]}
  - Users with meaningful persona: {metrics["coverage"]["metadata"]["users_with_meaningful_persona"]}
  - Users with ≥3 behaviors: {metrics["coverage"]["metadata"]["users_with_3_behaviors"]}
  - Users with both: {metrics["coverage"]["metadata"]["users_with_both"]}

### 2. Explainability
**Definition**: % of recommendations with non-empty rationale text

- **Value**: {metrics["explainability"]["value"]:.2f}%
- **Target**: {metrics["explainability"]["metadata"]["target"]:.2f}%
- **Status**: {"✅ PASS" if metrics["explainability"]["metadata"]["passes"] else "❌ FAIL"}
- **Details**:
  - Total recommendations: {metrics["explainability"]["metadata"]["total_recommendations"]}
  - Recommendations with rationale: {metrics["explainability"]["metadata"]["recommendations_with_rationale"]}
  - Recommendations without rationale: {metrics["explainability"]["metadata"]["recommendations_without_rationale"]}

### 3. Relevance
**Definition**: Rule-based persona → content category alignment

- **Value**: {metrics["relevance"]["value"]:.2f}%
- **Target**: {metrics["relevance"]["metadata"]["target"]:.2f}%
- **Status**: {"✅ PASS" if metrics["relevance"]["metadata"]["passes"] else "❌ FAIL"}
- **Details**:
  - Total recommendations: {metrics["relevance"]["metadata"]["total_recommendations"]}
  - Relevant recommendations: {metrics["relevance"]["metadata"]["relevant_recommendations"]}
  - Irrelevant recommendations: {metrics["relevance"]["metadata"]["irrelevant_recommendations"]}

### 4. Latency
**Definition**: Mean time to generate recommendations per user

- **Value**: {metrics["latency"]["value"]:.4f}s
- **Target**: <{metrics["latency"]["metadata"]["target"]:.1f}s
- **Status**: {"✅ PASS" if metrics["latency"]["metadata"]["passes"] else "❌ FAIL"}
- **Details**:
  - Users tested: {metrics["latency"]["metadata"]["users_tested"]}
  - Mean: {metrics["latency"]["metadata"]["mean_seconds"]:.4f}s
  - Median: {metrics["latency"]["metadata"]["median_seconds"]:.4f}s
  - P95: {metrics["latency"]["metadata"]["p95_seconds"]:.4f}s
  - Max: {metrics["latency"]["metadata"]["max_seconds"]:.4f}s

### 5. Auditability
**Definition**: % of users with complete trace JSONs

- **Value**: {metrics["auditability"]["value"]:.2f}%
- **Target**: {metrics["auditability"]["metadata"]["target"]:.2f}%
- **Status**: {"✅ PASS" if metrics["auditability"]["metadata"]["passes"] else "❌ FAIL"}
- **Details**:
  - Total users: {metrics["auditability"]["metadata"]["total_users"]}
  - Users with trace file: {metrics["auditability"]["metadata"]["users_with_trace_file"]}
  - Users with complete trace: {metrics["auditability"]["metadata"]["users_with_complete_trace"]}
  - Completeness: {metrics["auditability"]["metadata"]["completeness_percentage"]:.2f}%

### 6. Fairness
**Definition**: Demographic parity in persona assignments (±10% tolerance)

- **Value**: {"PASS" if fairness["all_demographics_pass"] else "FAIL"}
- **Target**: PASS
- **Status**: {"✅ PASS" if fairness["all_demographics_pass"] else "❌ FAIL"}
- **Details**:
  - Overall persona rate: {fairness["overall_persona_rate"]*100:.2f}%
  - Failing demographics: {', '.join(fairness["failing_demographics"]) if fairness["failing_demographics"] else "None"}
  - Gender: {"✅" if fairness["demographics"]["gender"]["passes"] else "❌"}
  - Income Tier: {"✅" if fairness["demographics"]["income_tier"]["passes"] else "❌"}
  - Region: {"✅" if fairness["demographics"]["region"]["passes"] else "❌"}
  - Age: {"✅" if fairness["demographics"]["age"]["passes"] else "❌"}

---

## Recommendations

"""

    if not metrics["coverage"]["metadata"]["passes"]:
        md += """
### Coverage Improvement
- **Issue**: Only {:.2f}% of users have meaningful persona + ≥3 behaviors
- **Actions**:
  1. Review data generation to ensure diverse financial behaviors
  2. Consider lowering behavior detection thresholds
  3. Investigate users with 'general' persona for potential reclassification
""".format(
            metrics["coverage"]["value"]
        )

    if not metrics["explainability"]["metadata"]["passes"]:
        md += """
### Explainability Improvement
- **Issue**: {} recommendations lack rationales
- **Actions**:
  1. Review recommendation generation code for missing rationale templates
  2. Add validation to ensure all recommendations have rationales
""".format(
            metrics["explainability"]["metadata"]["recommendations_without_rationale"]
        )

    if not metrics["relevance"]["metadata"]["passes"]:
        md += """
### Relevance Improvement
- **Issue**: {:.2f}% relevance below 90% target
- **Actions**:
  1. Review content catalog category mappings
  2. Verify persona → content alignment logic
  3. Investigate irrelevant recommendations sample
""".format(
            metrics["relevance"]["value"]
        )

    if not fairness["all_demographics_pass"]:
        md += """
### Fairness Improvement
- **Issue**: Demographic parity violations in {}
- **Actions**:
  1. Analyze persona assignment logic for potential bias
  2. Review synthetic data generation for demographic balance
  3. Consider threshold adjustments for underserved groups
""".format(
            ", ".join(fairness["failing_demographics"])
        )

    md += f"""
---

## Files Generated

- **JSON**: `eval/results_{timestamp}.json`
- **CSV**: `eval/results_{timestamp}.csv`
- **Summary**: `docs/eval_summary.md` (this file)
- **Fairness Report**: `docs/fairness_report.md`

See detailed fairness analysis in [fairness_report.md](fairness_report.md).

---

**Evaluation Version**: PR #8 Evaluation Harness
**Contact**: Casey Manos (Project Lead)
"""

    return md


# ============================================
# SYMLINK CREATION
# ============================================


def create_symlink(source: Path, target: Path):
    """
    Create symlink, overwriting if exists.

    Args:
        source: Path to actual file
        target: Path to symlink
    """
    # Remove existing symlink/file if present
    if target.exists() or target.is_symlink():
        target.unlink()

    # Create new symlink
    target.symlink_to(source.name)


# ============================================
# CONSOLE SUMMARY
# ============================================


def print_console_summary(
    metrics: Dict[str, Any],
    fairness: Dict[str, Any],
):
    """
    Print formatted summary to console.

    Args:
        metrics: Results from calculate_all_metrics()
        fairness: Results from calculate_fairness_metrics()
    """
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(f"\n{'Metric':<20} {'Value':<15} {'Target':<15} {'Status':<10}")
    print("-" * 60)

    # Coverage
    print(
        f"{'Coverage':<20} {metrics['coverage']['value']:>6.2f}% "
        f"{metrics['coverage']['metadata']['target']:>12.2f}% "
        f"{'✅ PASS' if metrics['coverage']['metadata']['passes'] else '❌ FAIL':<10}"
    )

    # Explainability
    print(
        f"{'Explainability':<20} {metrics['explainability']['value']:>6.2f}% "
        f"{metrics['explainability']['metadata']['target']:>12.2f}% "
        f"{'✅ PASS' if metrics['explainability']['metadata']['passes'] else '❌ FAIL':<10}"
    )

    # Relevance
    print(
        f"{'Relevance':<20} {metrics['relevance']['value']:>6.2f}% "
        f"{metrics['relevance']['metadata']['target']:>12.2f}% "
        f"{'✅ PASS' if metrics['relevance']['metadata']['passes'] else '❌ FAIL':<10}"
    )

    # Latency
    print(
        f"{'Latency':<20} {metrics['latency']['value']:>6.4f}s "
        f"{metrics['latency']['metadata']['target']:>12.2f}s "
        f"{'✅ PASS' if metrics['latency']['metadata']['passes'] else '❌ FAIL':<10}"
    )

    # Auditability
    print(
        f"{'Auditability':<20} {metrics['auditability']['value']:>6.2f}% "
        f"{metrics['auditability']['metadata']['target']:>12.2f}% "
        f"{'✅ PASS' if metrics['auditability']['metadata']['passes'] else '❌ FAIL':<10}"
    )

    # Fairness
    fairness_val = "PASS" if fairness["all_demographics_pass"] else "FAIL"
    print(
        f"{'Fairness':<20} {fairness_val:>10} "
        f"{'PASS':>15} "
        f"{'✅ PASS' if fairness['all_demographics_pass'] else '❌ FAIL':<10}"
    )

    print("-" * 60)
    all_pass = metrics["summary"]["all_metrics_pass"] and fairness["all_demographics_pass"]
    print(f"\n{'OVERALL STATUS:':<20} {'✅ ALL PASS' if all_pass else '❌ SOME FAIL'}")
    print("=" * 60 + "\n")


# ============================================
# MAIN ENTRY POINT
# ============================================


def main():
    """
    Main entry point for evaluation harness.
    """
    parser = argparse.ArgumentParser(description="SpendSense Evaluation Harness - PR #8")
    parser.add_argument(
        "--db",
        type=str,
        default="data/users.sqlite",
        help="Path to SQLite database (default: data/users.sqlite)",
    )
    parser.add_argument(
        "--signals",
        type=str,
        default="features/signals.parquet",
        help="Path to signals Parquet file (default: features/signals.parquet)",
    )
    parser.add_argument(
        "--traces",
        type=str,
        default="docs/traces",
        help="Directory containing trace JSONs (default: docs/traces)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="eval",
        help="Output directory (default: eval/)",
    )
    parser.add_argument(
        "--timestamp",
        type=str,
        default=None,
        help="Custom timestamp (default: auto-generated)",
    )
    parser.add_argument(
        "--latency-sample",
        type=int,
        default=None,
        help="Number of users for latency test (default: all consented users)",
    )

    args = parser.parse_args()

    # Generate timestamp
    timestamp = args.timestamp if args.timestamp else generate_timestamp()
    print(f"\n🚀 Starting evaluation at {timestamp}\n")

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # ========================================
        # STEP 1: Calculate core metrics
        # ========================================
        print("=" * 60)
        print("STEP 1: Calculating core metrics...")
        print("=" * 60)

        metrics = calculate_all_metrics(
            db_path=args.db,
            signals_path=args.signals,
            traces_dir=args.traces,
            latency_sample_size=args.latency_sample,
        )

        # ========================================
        # STEP 2: Calculate fairness metrics
        # ========================================
        print("\n" + "=" * 60)
        print("STEP 2: Calculating fairness metrics...")
        print("=" * 60 + "\n")

        fairness, distribution = calculate_fairness_metrics(db_path=args.db)

        # ========================================
        # STEP 3: Generate outputs
        # ========================================
        print("\n" + "=" * 60)
        print("STEP 3: Generating outputs...")
        print("=" * 60 + "\n")

        # JSON output
        json_output = generate_json_output(metrics, fairness, timestamp)
        json_file = output_dir / f"results_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(json_output, f, indent=2)
        print(f"✅ Generated: {json_file}")

        # CSV output
        csv_df = generate_csv_output(metrics, fairness)
        csv_file = output_dir / f"results_{timestamp}.csv"
        csv_df.to_csv(csv_file, index=False)
        print(f"✅ Generated: {csv_file}")

        # Markdown summary
        summary_md = generate_summary_markdown(metrics, fairness, timestamp)
        summary_file = Path("docs/eval_summary.md")
        with open(summary_file, "w") as f:
            f.write(summary_md)
        print(f"✅ Generated: {summary_file}")

        # Fairness report
        fairness_md = generate_fairness_report_markdown(fairness, distribution, timestamp)
        fairness_file = Path("docs/fairness_report.md")
        with open(fairness_file, "w") as f:
            f.write(fairness_md)
        print(f"✅ Generated: {fairness_file}")

        # ========================================
        # STEP 4: Create symlinks
        # ========================================
        print("\n" + "=" * 60)
        print("STEP 4: Creating symlinks to latest results...")
        print("=" * 60 + "\n")

        create_symlink(json_file, output_dir / "results.json")
        print(f"✅ Symlink: eval/results.json → results_{timestamp}.json")

        create_symlink(csv_file, output_dir / "results.csv")
        print(f"✅ Symlink: eval/results.csv → results_{timestamp}.csv")

        # ========================================
        # STEP 5: Print console summary
        # ========================================
        print_console_summary(metrics, fairness)

        print("✅ Evaluation complete! See docs/eval_summary.md for details.\n")

        # Return 0 if all pass, 1 if any fail
        all_pass = metrics["summary"]["all_metrics_pass"] and fairness["all_demographics_pass"]
        sys.exit(0 if all_pass else 1)

    except Exception as e:
        print("\n❌ ERROR: Evaluation failed with exception:")
        print(f"   {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()

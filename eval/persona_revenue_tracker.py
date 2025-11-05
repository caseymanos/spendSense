"""
Revenue Metrics Tracker

Tracks revenue metrics over time to monitor changes in:
- Multi-persona trigger rates
- Opportunity cost trends
- Priority order performance
- Revenue by persona

Useful for monitoring how data changes affect revenue implications.

Usage:
    uv run python eval/persona_revenue_tracker.py --save
    uv run python eval/persona_revenue_tracker.py --compare
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_PATH = PROJECT_ROOT / "eval" / "persona_revenue_results.json"
HISTORY_PATH = PROJECT_ROOT / "eval" / "revenue_history.json"


def load_current_results() -> Dict[str, Any]:
    """Load current revenue analysis results."""
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(
            f"Results file not found: {RESULTS_PATH}\n"
            "Run: uv run python eval/persona_revenue_analysis.py"
        )

    with open(RESULTS_PATH, "r") as f:
        return json.load(f)


def load_history() -> List[Dict[str, Any]]:
    """Load historical revenue metrics."""
    if not HISTORY_PATH.exists():
        return []

    with open(HISTORY_PATH, "r") as f:
        return json.load(f)


def save_history(history: List[Dict[str, Any]]):
    """Save updated history."""
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)


def extract_key_metrics(results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key metrics from full results for tracking."""
    comparison = results["priority_order_comparison"]["priority_order_results"]
    co_occur = results["co_occurrence_analysis"]
    opp_cost = results["opportunity_cost_analysis"]

    return {
        "timestamp": datetime.now().isoformat(),
        "total_users": results["metadata"]["total_users_analyzed"],
        "multi_trigger_count": co_occur["multi_trigger_count"],
        "multi_trigger_percentage": co_occur["multi_trigger_percentage"],
        "current_educational_revenue": comparison["current_educational"]["total_expected_revenue"],
        "revenue_optimal_revenue": comparison["revenue_optimal"]["total_expected_revenue"],
        "opportunity_cost": opp_cost["total_opportunity_cost"],
        "affected_users": opp_cost["affected_user_count"],
        "revenue_lift_percentage": (
            (comparison["revenue_optimal"]["total_expected_revenue"]
             - comparison["current_educational"]["total_expected_revenue"])
            / comparison["current_educational"]["total_expected_revenue"] * 100
            if comparison["current_educational"]["total_expected_revenue"] > 0 else 0
        ),
        "persona_trigger_counts": co_occur["persona_trigger_counts"],
    }


def save_snapshot():
    """Save current metrics as a historical snapshot."""
    print("=" * 80)
    print("SAVING REVENUE METRICS SNAPSHOT")
    print("=" * 80)

    # Load current results
    print(f"\nLoading current results from {RESULTS_PATH}...")
    results = load_current_results()

    # Extract key metrics
    metrics = extract_key_metrics(results)

    # Load history
    history = load_history()

    # Add new snapshot
    history.append(metrics)

    # Save updated history
    save_history(history)

    print(f"\n✅ Snapshot saved to {HISTORY_PATH}")
    print(f"   Timestamp: {metrics['timestamp']}")
    print(f"   Total Users: {metrics['total_users']}")
    print(f"   Multi-Trigger Rate: {metrics['multi_trigger_percentage']:.1f}%")
    print(f"   Opportunity Cost: ${metrics['opportunity_cost']:,.2f}")
    print(f"   Total Snapshots: {len(history)}")
    print("=" * 80 + "\n")


def compare_snapshots():
    """Compare current results with historical snapshots."""
    print("=" * 80)
    print("REVENUE METRICS TREND ANALYSIS")
    print("=" * 80)

    # Load history
    history = load_history()

    if len(history) == 0:
        print("\n❌ No historical snapshots found.")
        print("   Save a snapshot first: uv run python eval/persona_revenue_tracker.py --save\n")
        return

    if len(history) == 1:
        print("\n⚠️  Only one snapshot found. Need at least 2 for comparison.")
        print("   Run analysis again later and save another snapshot.\n")
        return

    print(f"\nFound {len(history)} snapshots\n")

    # Print comparison table
    print("Snapshot History:")
    print("-" * 80)
    print(f"{'Date':<20} {'Users':<8} {'Multi-Trig%':<12} {'Opp Cost':<12} {'Revenue Lift%':<15}")
    print("-" * 80)

    for snapshot in history:
        date = snapshot["timestamp"][:10]
        users = snapshot["total_users"]
        multi_pct = snapshot["multi_trigger_percentage"]
        opp_cost = snapshot["opportunity_cost"]
        lift_pct = snapshot["revenue_lift_percentage"]

        print(f"{date:<20} {users:<8} {multi_pct:>10.1f}% ${opp_cost:>10,.0f} {lift_pct:>13.1f}%")

    print("-" * 80)

    # Calculate trends
    first = history[0]
    last = history[-1]

    print("\nTrends (First → Last):")
    print("-" * 80)

    # Multi-trigger rate
    trigger_change = last["multi_trigger_percentage"] - first["multi_trigger_percentage"]
    print(f"  Multi-Trigger Rate:    {first['multi_trigger_percentage']:.1f}% → {last['multi_trigger_percentage']:.1f}% ({trigger_change:+.1f} pp)")

    # Opportunity cost
    opp_cost_change = last["opportunity_cost"] - first["opportunity_cost"]
    opp_cost_pct_change = (opp_cost_change / first["opportunity_cost"] * 100) if first["opportunity_cost"] > 0 else 0
    print(f"  Opportunity Cost:      ${first['opportunity_cost']:,.0f} → ${last['opportunity_cost']:,.0f} ({opp_cost_pct_change:+.1f}%)")

    # Revenue lift
    lift_change = last["revenue_lift_percentage"] - first["revenue_lift_percentage"]
    print(f"  Revenue Lift:          {first['revenue_lift_percentage']:.1f}% → {last['revenue_lift_percentage']:.1f}% ({lift_change:+.1f} pp)")

    # Affected users
    affected_change = last["affected_users"] - first["affected_users"]
    print(f"  Affected Users:        {first['affected_users']} → {last['affected_users']} ({affected_change:+d})")

    print("-" * 80)

    # Persona distribution changes
    if "persona_trigger_counts" in first and "persona_trigger_counts" in last:
        print("\nPersona Trigger Count Changes:")
        print("-" * 80)

        all_personas = set(first["persona_trigger_counts"].keys()) | set(last["persona_trigger_counts"].keys())

        for persona in sorted(all_personas):
            first_count = first["persona_trigger_counts"].get(persona, 0)
            last_count = last["persona_trigger_counts"].get(persona, 0)
            change = last_count - first_count
            change_pct = (change / first_count * 100) if first_count > 0 else 0

            print(f"  {persona:<25} {first_count:>4} → {last_count:>4} ({change:+4d}, {change_pct:+.1f}%)")

        print("-" * 80)

    # Recommendations
    print("\nRecommendations:")
    print("-" * 80)

    if trigger_change > 2.0:
        print("  ⚠️  Multi-trigger rate increased significantly (+{:.1f} pp)".format(trigger_change))
        print("     Consider investigating why more users trigger multiple personas")

    if opp_cost_pct_change > 20.0:
        print("  ⚠️  Opportunity cost increased by {:.1f}%".format(opp_cost_pct_change))
        print("     May warrant re-evaluation of priority order if trend continues")

    if abs(trigger_change) < 1.0 and abs(opp_cost_pct_change) < 10.0:
        print("  ✅ Revenue metrics are stable")
        print("     Current educational priority order remains appropriate")

    print("=" * 80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Track revenue metrics over time")
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save current metrics as a snapshot"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare current metrics with historical snapshots"
    )

    args = parser.parse_args()

    if not args.save and not args.compare:
        print("\nUsage:")
        print("  uv run python eval/persona_revenue_tracker.py --save      # Save snapshot")
        print("  uv run python eval/persona_revenue_tracker.py --compare   # Compare snapshots")
        print("  uv run python eval/persona_revenue_tracker.py --save --compare  # Both\n")
        return

    try:
        if args.save:
            save_snapshot()

        if args.compare:
            compare_snapshots()

    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}\n")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

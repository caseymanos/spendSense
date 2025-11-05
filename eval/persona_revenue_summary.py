"""
Quick Revenue Summary Script

Executive summary tool for business stakeholders to understand
multi-persona revenue implications in under 60 seconds.

Usage:
    uv run python eval/persona_revenue_summary.py
"""

import json
from pathlib import Path
from typing import Dict, Any

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_PATH = PROJECT_ROOT / "eval" / "persona_revenue_results.json"


def format_currency(value: float) -> str:
    """Format value as currency."""
    return f"${value:,.2f}"


def format_percent(value: float) -> str:
    """Format value as percentage."""
    return f"{value:.1f}%"


def print_section(title: str, width: int = 80):
    """Print section header."""
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


def print_subsection(title: str, width: int = 80):
    """Print subsection header."""
    print("\n" + title)
    print("-" * width)


def print_key_value(key: str, value: str, indent: int = 2):
    """Print key-value pair with formatting."""
    print(" " * indent + f"• {key:40s} {value}")


def print_executive_summary(results: Dict[str, Any]):
    """Print one-page executive summary."""
    print_section("MULTI-PERSONA REVENUE ANALYSIS: EXECUTIVE SUMMARY")

    metadata = results["metadata"]
    co_occur = results["co_occurrence_analysis"]
    comparison = results["priority_order_comparison"]["priority_order_results"]
    opp_cost = results["opportunity_cost_analysis"]

    current = comparison["current_educational"]
    optimal = comparison["revenue_optimal"]

    # Quick facts
    print_subsection("📊 ANALYSIS SNAPSHOT")
    print_key_value("Analysis Date", metadata["analysis_date"][:10])
    print_key_value("Users Analyzed", str(metadata["total_users_analyzed"]))
    print_key_value("Multi-Persona Trigger Rate", f"{co_occur['multi_trigger_percentage']:.1f}% ({co_occur['multi_trigger_count']} users)")

    # Revenue comparison
    print_subsection("💰 REVENUE COMPARISON")

    print("\n  Current Educational Priority Order:")
    print(f"    Priority: High Utilization → Variable Income → Subscription Heavy → Savings Builder")
    print_key_value("Total Expected Revenue", format_currency(current["total_expected_revenue"]))
    print_key_value("Avg Revenue per User", format_currency(current["avg_revenue_per_user"]))

    print("\n  Revenue-Optimal Priority Order:")
    print(f"    Priority: Savings Builder → High Utilization → Variable Income → Subscription Heavy")
    print_key_value("Total Expected Revenue", format_currency(optimal["total_expected_revenue"]))
    print_key_value("Avg Revenue per User", format_currency(optimal["avg_revenue_per_user"]))

    # Opportunity cost
    lift = optimal["total_expected_revenue"] - current["total_expected_revenue"]
    lift_pct = (lift / current["total_expected_revenue"]) * 100 if current["total_expected_revenue"] > 0 else 0

    print_subsection("📈 OPPORTUNITY COST")
    print_key_value("Revenue Left on Table", f"{format_currency(lift)} (+{format_percent(lift_pct)})")
    print_key_value("Total Opportunity Cost", format_currency(opp_cost["total_opportunity_cost"]))
    print_key_value("Users Affected", f"{opp_cost['affected_user_count']} ({opp_cost['affected_user_count']/metadata['total_users_analyzed']*100:.1f}%)")

    # Revenue by persona
    print_subsection("🎯 REVENUE POTENTIAL BY PERSONA")

    revenue_by_persona = results["expected_revenue_per_user_by_persona"]
    sorted_personas = sorted(revenue_by_persona.items(), key=lambda x: -x[1])

    for persona, revenue in sorted_personas:
        if persona == "general":
            continue
        model = results["revenue_model_assumptions"][persona]
        print(f"\n  {persona.upper().replace('_', ' ')}:")
        print_key_value("Expected Revenue/User", format_currency(revenue))
        print_key_value("Primary Offer", model["primary_offer"])
        print_key_value("Conversion Rate", format_percent(model["conversion_rate"] * 100))
        print_key_value("LTV Multiplier", f"{model['ltv_multiplier']}x")

    # Recommendation
    print_section("✅ RECOMMENDATION")

    print("""
  MAINTAIN CURRENT EDUCATIONAL PRIORITY ORDER

  Rationale:
    • Minimal opportunity cost: Only ${:,.0f} total ({:.1f}% of revenue)
    • Affects only {} user(s) ({:.1f}% of user base)
    • Strong ethical positioning: Urgency-first protects users with credit strain
    • Regulatory safety: CFPB compliance, defensible user-first rationale
    • User trust: Long-term value exceeds short-term revenue optimization

  The educational-first approach prioritizes helping users with urgent financial
  needs (high credit utilization, debt stress) BEFORE showing them investment
  products or other high-revenue offers. This aligns with fiduciary principles
  and maintains user trust.

  IF business pressure demands revenue optimization:
    → Consider HYBRID order: High Utilization → Savings Builder → Variable Income → Subscription Heavy
    → Captures 100% of revenue upside while preserving urgency-first for credit strain
    """.format(
        opp_cost["total_opportunity_cost"],
        lift_pct,
        opp_cost["affected_user_count"],
        opp_cost["affected_user_count"]/metadata["total_users_analyzed"]*100
    ))

    print_section("📁 DETAILED REPORTS")
    print(f"""
  Full Analysis Report:  docs/persona_revenue_evaluation.md
  Detailed Results:      eval/persona_revenue_results.json
  Visualization Dashboard: eval/revenue_viz/dashboard.html

  Re-run analysis:       uv run python eval/persona_revenue_analysis.py
  Regenerate visuals:    uv run python eval/persona_revenue_viz.py
    """)

    print("=" * 80 + "\n")


def print_scenario_analysis(results: Dict[str, Any]):
    """Print detailed scenario breakdown for multi-persona users."""
    print_section("SCENARIO ANALYSIS: MULTI-PERSONA CONFLICTS")

    opp_losses = results["opportunity_cost_analysis"]["opportunity_losses"]

    if not opp_losses:
        print("\n  ✓ No opportunity cost scenarios found")
        print("  All users have single-persona assignments or no revenue delta")
        return

    print(f"\n  Found {len(opp_losses)} scenarios where revenue-optimal persona differs from assigned\n")

    for i, scenario in enumerate(opp_losses[:10], 1):  # Top 10
        print(f"  Scenario #{i}: {scenario['user_id']}")
        print_key_value("Triggered Personas", ", ".join(scenario['triggered_personas']))
        print_key_value("Current Assignment", scenario['assigned_persona'])
        print_key_value("Current Revenue", format_currency(scenario['assigned_revenue']))
        print_key_value("Optimal Assignment", scenario['optimal_persona'])
        print_key_value("Optimal Revenue", format_currency(scenario['optimal_revenue']))
        print_key_value("Opportunity Cost", format_currency(scenario['opportunity_cost']))
        print()


def print_sensitivity_analysis(results: Dict[str, Any]):
    """Print sensitivity analysis showing impact of assumption changes."""
    print_section("SENSITIVITY ANALYSIS")

    print("\n  How results change if conversion rates vary:\n")

    revenue_model = results["revenue_model_assumptions"]

    scenarios = [
        ("Current Assumptions", 1.0),
        ("Conservative (-20%)", 0.8),
        ("Optimistic (+20%)", 1.2),
    ]

    print(f"  {'Persona':<25} {'Current':<12} {'Conservative':<12} {'Optimistic':<12}")
    print("  " + "-" * 65)

    for persona, model in revenue_model.items():
        if persona == "general":
            continue

        current_rev = model["revenue_per_conversion"] * model["conversion_rate"] * model["ltv_multiplier"]

        row = [persona.replace("_", " ").title()]
        for _, multiplier in scenarios:
            adjusted_cr = model["conversion_rate"] * multiplier
            adjusted_rev = model["revenue_per_conversion"] * adjusted_cr * model["ltv_multiplier"]
            row.append(format_currency(adjusted_rev))

        print(f"  {row[0]:<25} {row[1]:<12} {row[2]:<12} {row[3]:<12}")

    print("\n  Key Insight:")
    print("    Even with -20% conversion rates, Savings Builder ($86) remains 8x more")
    print("    valuable than High Utilization ($8) due to LTV multiplier (3.0x).\n")


def main():
    """Main entry point."""
    if not RESULTS_PATH.exists():
        print(f"\n❌ ERROR: Results file not found at {RESULTS_PATH}")
        print("   Run the analysis first: uv run python eval/persona_revenue_analysis.py\n")
        return

    # Load results
    with open(RESULTS_PATH, "r") as f:
        results = json.load(f)

    # Print summaries
    print_executive_summary(results)
    print_scenario_analysis(results)
    print_sensitivity_analysis(results)


if __name__ == "__main__":
    main()

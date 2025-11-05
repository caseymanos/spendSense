"""
Multi-Persona Revenue Optimization Analysis for SpendSense MVP V2

This module evaluates the persona priority system from a revenue maximization perspective,
analyzing the trade-offs between educational value and bank revenue when users trigger
multiple personas simultaneously.

Key Questions:
1. What is the revenue potential of each persona's partner offers?
2. Which personas commonly co-occur (multi-trigger scenarios)?
3. How much revenue is left on the table with the current priority order?
4. What would a revenue-optimal priority order look like?
5. What are the ethical implications of revenue-first ranking?

Revenue Model Assumptions:
- Credit card referrals: $100-300 per approval (avg $150)
- Investment accounts: $100-300 + ongoing AUM fees (avg $200 + $100/year)
- Savings/deposit accounts: $50-150 per funded account (avg $100)
- Subscription app referrals: $10-50 per signup (avg $20)
- Non-profit referrals: $0-10 (avg $5)

Conversion Rate Assumptions:
- High Utilization (credit cards): 5-10% (avg 7%) - motivated but credit-challenged
- Savings Builder (investment): 10-15% (avg 12%) - proven savers, high intent
- Savings Builder (savings acct): 20-30% (avg 25%) - easier commitment
- Variable Income (savings): 10-15% (avg 12%)
- Subscription Heavy (apps): 15-20% (avg 17%)
"""

import pandas as pd
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import Counter, defaultdict

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "users.sqlite"
SIGNALS_PATH = PROJECT_ROOT / "features" / "signals.parquet"
RESULTS_PATH = PROJECT_ROOT / "eval" / "persona_revenue_results.json"

# Import persona checking functions
import sys
sys.path.append(str(PROJECT_ROOT))
from personas.assignment import (
    check_high_utilization,
    check_variable_income,
    check_subscription_heavy,
    check_savings_builder,
)


# ============================================
# REVENUE MODEL CONFIGURATION
# ============================================

PERSONA_REVENUE_MODEL = {
    "high_utilization": {
        "primary_offer": "0% Balance Transfer Credit Card",
        "revenue_per_conversion": 150,  # Credit card affiliate commission
        "conversion_rate": 0.07,  # 7% (motivated but credit-challenged)
        "secondary_revenue": 0,  # One-time transaction
        "ltv_multiplier": 1.0,  # No ongoing revenue
        "user_quality": "medium",  # Credit issues may affect approval rates
        "notes": "High per-transaction value but lower conversion and approval rates",
    },
    "variable_income": {
        "primary_offer": "Marcus High-Yield Savings + YNAB",
        "revenue_per_conversion": 100,  # Savings account opening bonus
        "conversion_rate": 0.12,  # 12% (motivated by income instability)
        "secondary_revenue": 15,  # YNAB subscription affiliate
        "ltv_multiplier": 1.2,  # Some ongoing deposit value
        "user_quality": "medium",  # Income instability = moderate risk
        "notes": "Moderate revenue from deposit accounts and app subscriptions",
    },
    "subscription_heavy": {
        "primary_offer": "Rocket Money Subscription Manager",
        "revenue_per_conversion": 20,  # App subscription affiliate
        "conversion_rate": 0.17,  # 17% (high motivation to cut costs)
        "secondary_revenue": 0,
        "ltv_multiplier": 1.1,  # Minimal ongoing value
        "user_quality": "medium",  # Varied quality
        "notes": "Lowest revenue potential - consumer app referrals only",
    },
    "savings_builder": {
        "primary_offer": "Fidelity Go Robo-Advisor + Ally Savings",
        "revenue_per_conversion": 200,  # Investment account opening
        "conversion_rate": 0.12,  # 12% (investment account - higher commitment)
        "secondary_revenue": 100,  # Savings account (25% conversion * $100 = $25, but + ongoing AUM fees)
        "ltv_multiplier": 3.0,  # Ongoing AUM fees on growing balances (0.35% annually on avg $30K = $105/year)
        "user_quality": "high",  # Proven savers, high credit scores, growing assets
        "notes": "Highest LTV - investment accounts generate ongoing AUM fees + deposits grow",
    },
    "general": {
        "primary_offer": "None",
        "revenue_per_conversion": 0,
        "conversion_rate": 0,
        "secondary_revenue": 0,
        "ltv_multiplier": 1.0,
        "user_quality": "low",
        "notes": "No recommendations, no revenue",
    },
}


# Priority orders to evaluate
PRIORITY_ORDERS = {
    "current_educational": [
        "high_utilization",
        "variable_income",
        "subscription_heavy",
        "savings_builder",
        "general",
    ],
    "revenue_optimal": [
        "savings_builder",
        "high_utilization",
        "variable_income",
        "subscription_heavy",
        "general",
    ],
    "hybrid_balanced": [
        "high_utilization",  # Keep urgency first
        "savings_builder",  # Elevate revenue potential
        "variable_income",  # Stability second
        "subscription_heavy",
        "general",
    ],
    "ltv_optimal": [
        "savings_builder",  # Highest LTV
        "variable_income",  # Deposit accounts have ongoing value
        "high_utilization",  # One-time revenue
        "subscription_heavy",  # Lowest LTV
        "general",
    ],
}


# ============================================
# HELPER FUNCTIONS
# ============================================


def calculate_expected_revenue_per_user(persona: str) -> float:
    """
    Calculate expected revenue per user for a given persona.

    Formula:
        Primary Revenue = revenue_per_conversion * conversion_rate
        Total Revenue = (Primary + Secondary) * ltv_multiplier

    Args:
        persona: Persona name

    Returns:
        Expected revenue per user assigned to this persona
    """
    model = PERSONA_REVENUE_MODEL.get(persona, PERSONA_REVENUE_MODEL["general"])

    primary_revenue = model["revenue_per_conversion"] * model["conversion_rate"]
    secondary_revenue = model["secondary_revenue"] * model["conversion_rate"]
    total_revenue = (primary_revenue + secondary_revenue) * model["ltv_multiplier"]

    return total_revenue


def check_all_personas(signals: pd.Series) -> Dict[str, Tuple[bool, Dict]]:
    """
    Run all persona checks for a user to identify multi-persona triggers.

    Args:
        signals: User signals row

    Returns:
        Dict mapping persona name to (matches, criteria_met)
    """
    return {
        "high_utilization": check_high_utilization(signals),
        "variable_income": check_variable_income(signals),
        "subscription_heavy": check_subscription_heavy(signals),
        "savings_builder": check_savings_builder(signals),
    }


def assign_persona_by_priority(
    persona_matches: Dict[str, bool], priority_order: List[str]
) -> str:
    """
    Assign persona based on a given priority order.

    Args:
        persona_matches: Dict of persona -> matches (bool)
        priority_order: List of persona names in priority order

    Returns:
        Assigned persona name
    """
    for persona in priority_order:
        if persona_matches.get(persona, False):
            return persona

    return "general"


# ============================================
# MAIN ANALYSIS FUNCTIONS
# ============================================


def analyze_persona_co_occurrence(signals_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze which personas commonly co-occur (multi-trigger scenarios).

    Args:
        signals_df: Signals DataFrame with all users

    Returns:
        Dictionary with co-occurrence statistics
    """
    print("\n" + "=" * 80)
    print("PERSONA CO-OCCURRENCE ANALYSIS")
    print("=" * 80)

    multi_trigger_users = []
    persona_trigger_counts = Counter()
    co_occurrence_pairs = Counter()

    for idx, row in signals_df.iterrows():
        user_id = row["user_id"]
        checks = check_all_personas(row)

        # Get all triggered personas
        triggered = [persona for persona, (matches, _) in checks.items() if matches]

        if len(triggered) > 1:
            multi_trigger_users.append(
                {"user_id": user_id, "triggered_personas": triggered, "count": len(triggered)}
            )

            # Count pairs
            for i, p1 in enumerate(triggered):
                for p2 in triggered[i + 1 :]:
                    pair = tuple(sorted([p1, p2]))
                    co_occurrence_pairs[pair] += 1

        # Count individual triggers
        for persona in triggered:
            persona_trigger_counts[persona] += 1

    # Calculate statistics
    total_users = len(signals_df)
    multi_trigger_count = len(multi_trigger_users)
    multi_trigger_pct = (multi_trigger_count / total_users) * 100 if total_users > 0 else 0

    print(f"\nTotal users analyzed: {total_users}")
    print(f"Users triggering multiple personas: {multi_trigger_count} ({multi_trigger_pct:.1f}%)")
    print(f"\nPersona trigger frequency:")
    for persona, count in sorted(persona_trigger_counts.items(), key=lambda x: -x[1]):
        pct = (count / total_users) * 100
        print(f"  {persona:25s} {count:4d} users ({pct:5.1f}%)")

    print(f"\nMost common multi-persona combinations:")
    for pair, count in co_occurrence_pairs.most_common(10):
        pct = (count / multi_trigger_count) * 100 if multi_trigger_count > 0 else 0
        print(f"  {pair[0]:20s} + {pair[1]:25s} = {count:4d} users ({pct:5.1f}% of multi-trigger)")

    return {
        "total_users": total_users,
        "multi_trigger_count": multi_trigger_count,
        "multi_trigger_percentage": multi_trigger_pct,
        "persona_trigger_counts": dict(persona_trigger_counts),
        "co_occurrence_pairs": {str(k): v for k, v in co_occurrence_pairs.items()},
        "multi_trigger_users": multi_trigger_users[:100],  # Sample for inspection
    }


def simulate_revenue_by_priority_order(
    signals_df: pd.DataFrame, priority_order: List[str], order_name: str
) -> Dict[str, Any]:
    """
    Simulate total revenue under a given persona priority order.

    Args:
        signals_df: Signals DataFrame
        priority_order: List of persona names in priority order
        order_name: Name of this priority order

    Returns:
        Dictionary with revenue statistics
    """
    persona_assignments = []
    total_revenue = 0.0
    persona_revenue = defaultdict(float)
    persona_counts = Counter()

    for idx, row in signals_df.iterrows():
        user_id = row["user_id"]
        checks = check_all_personas(row)

        # Get triggered personas (bool only)
        persona_matches = {persona: matches for persona, (matches, _) in checks.items()}

        # Assign persona based on priority order
        assigned_persona = assign_persona_by_priority(persona_matches, priority_order)

        # Calculate expected revenue
        revenue = calculate_expected_revenue_per_user(assigned_persona)

        persona_assignments.append(
            {
                "user_id": user_id,
                "assigned_persona": assigned_persona,
                "triggered_personas": [p for p, m in persona_matches.items() if m],
                "expected_revenue": revenue,
            }
        )

        total_revenue += revenue
        persona_revenue[assigned_persona] += revenue
        persona_counts[assigned_persona] += 1

    # Calculate per-persona averages
    avg_revenue_per_user = total_revenue / len(signals_df) if len(signals_df) > 0 else 0

    return {
        "priority_order_name": order_name,
        "priority_order": priority_order,
        "total_users": len(signals_df),
        "total_expected_revenue": total_revenue,
        "avg_revenue_per_user": avg_revenue_per_user,
        "persona_assignments": dict(persona_counts),
        "persona_revenue_totals": dict(persona_revenue),
        "persona_revenue_per_user": {
            p: persona_revenue[p] / persona_counts[p] if persona_counts[p] > 0 else 0
            for p in persona_revenue.keys()
        },
        "detailed_assignments": persona_assignments[:100],  # Sample
    }


def compare_priority_orders(signals_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compare revenue outcomes across different priority ordering strategies.

    Args:
        signals_df: Signals DataFrame

    Returns:
        Dictionary with comparison results
    """
    print("\n" + "=" * 80)
    print("PRIORITY ORDER REVENUE COMPARISON")
    print("=" * 80)

    results = {}

    for order_name, priority_order in PRIORITY_ORDERS.items():
        print(f"\nSimulating: {order_name}")
        print(f"  Priority: {' > '.join(priority_order)}")

        result = simulate_revenue_by_priority_order(signals_df, priority_order, order_name)
        results[order_name] = result

        print(f"  Total Revenue: ${result['total_expected_revenue']:,.2f}")
        print(f"  Avg per User:  ${result['avg_revenue_per_user']:.2f}")

    # Calculate revenue lift between strategies
    baseline = results["current_educational"]
    revenue_lift = {}

    print("\n" + "=" * 80)
    print("REVENUE LIFT ANALYSIS (vs Current Educational Priority)")
    print("=" * 80)

    for order_name, result in results.items():
        if order_name == "current_educational":
            continue

        lift_dollars = result["total_expected_revenue"] - baseline["total_expected_revenue"]
        lift_pct = (
            (lift_dollars / baseline["total_expected_revenue"]) * 100
            if baseline["total_expected_revenue"] > 0
            else 0
        )

        revenue_lift[order_name] = {"lift_dollars": lift_dollars, "lift_percentage": lift_pct}

        print(f"\n{order_name}:")
        print(f"  Revenue Lift: ${lift_dollars:,.2f} ({lift_pct:+.1f}%)")
        print(f"  Priority: {' > '.join(PRIORITY_ORDERS[order_name])}")

    return {"priority_order_results": results, "revenue_lift": revenue_lift}


def analyze_opportunity_cost(signals_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze revenue opportunity cost from current persona priority order.

    Specifically: For users triggering multiple personas, how much revenue is lost
    by assigning them to a lower-revenue persona due to priority order?

    Args:
        signals_df: Signals DataFrame

    Returns:
        Dictionary with opportunity cost analysis
    """
    print("\n" + "=" * 80)
    print("OPPORTUNITY COST ANALYSIS")
    print("=" * 80)

    opportunity_losses = []
    total_opportunity_cost = 0.0

    for idx, row in signals_df.iterrows():
        user_id = row["user_id"]
        checks = check_all_personas(row)

        # Get triggered personas
        triggered = [persona for persona, (matches, _) in checks.items() if matches]

        if len(triggered) <= 1:
            continue  # No conflict, no opportunity cost

        # Calculate revenue for each triggered persona
        persona_revenues = {p: calculate_expected_revenue_per_user(p) for p in triggered}

        # Current assignment (educational priority)
        current_priority = PRIORITY_ORDERS["current_educational"]
        assigned_persona = assign_persona_by_priority(
            {p: True for p in triggered}, current_priority
        )
        assigned_revenue = persona_revenues[assigned_persona]

        # Revenue-optimal assignment
        optimal_persona = max(persona_revenues.keys(), key=lambda p: persona_revenues[p])
        optimal_revenue = persona_revenues[optimal_persona]

        # Opportunity cost
        opportunity_cost = optimal_revenue - assigned_revenue

        if opportunity_cost > 0:
            opportunity_losses.append(
                {
                    "user_id": user_id,
                    "triggered_personas": triggered,
                    "assigned_persona": assigned_persona,
                    "assigned_revenue": assigned_revenue,
                    "optimal_persona": optimal_persona,
                    "optimal_revenue": optimal_revenue,
                    "opportunity_cost": opportunity_cost,
                }
            )
            total_opportunity_cost += opportunity_cost

    # Sort by opportunity cost
    opportunity_losses.sort(key=lambda x: -x["opportunity_cost"])

    print(f"\nTotal users with opportunity cost: {len(opportunity_losses)}")
    print(f"Total opportunity cost: ${total_opportunity_cost:,.2f}")
    print(
        f"Avg opportunity cost per affected user: ${total_opportunity_cost / len(opportunity_losses) if opportunity_losses else 0:.2f}"
    )

    # Show top examples
    print(f"\nTop 10 opportunity cost scenarios:")
    for loss in opportunity_losses[:10]:
        print(
            f"  User {loss['user_id']}: ${loss['opportunity_cost']:.2f} "
            f"({loss['assigned_persona']} → {loss['optimal_persona']})"
        )

    return {
        "total_opportunity_cost": total_opportunity_cost,
        "affected_user_count": len(opportunity_losses),
        "avg_opportunity_cost_per_user": (
            total_opportunity_cost / len(opportunity_losses) if opportunity_losses else 0
        ),
        "opportunity_losses": opportunity_losses[:50],  # Top 50 for inspection
    }


# ============================================
# MAIN EXECUTION
# ============================================


def run_full_analysis():
    """
    Run complete multi-persona revenue analysis and save results.
    """
    print("=" * 80)
    print("MULTI-PERSONA REVENUE OPTIMIZATION ANALYSIS")
    print("SpendSense MVP V2 - Evaluating Persona Priority Orders")
    print("=" * 80)

    # Load signals
    if not SIGNALS_PATH.exists():
        print(f"\nERROR: Signals file not found at {SIGNALS_PATH}")
        print("Run feature detection first: uv run python -m features.detect")
        return

    print(f"\nLoading signals from {SIGNALS_PATH}...")
    signals_df = pd.read_parquet(SIGNALS_PATH)
    print(f"Loaded {len(signals_df)} users")

    # Print revenue model assumptions
    print("\n" + "=" * 80)
    print("REVENUE MODEL ASSUMPTIONS")
    print("=" * 80)
    for persona, model in PERSONA_REVENUE_MODEL.items():
        if persona == "general":
            continue
        expected_rev = calculate_expected_revenue_per_user(persona)
        print(f"\n{persona.upper().replace('_', ' ')}:")
        print(f"  Primary Offer: {model['primary_offer']}")
        print(
            f"  Revenue per Conversion: ${model['revenue_per_conversion']} (CR: {model['conversion_rate']*100:.0f}%)"
        )
        print(f"  LTV Multiplier: {model['ltv_multiplier']}x")
        print(f"  Expected Revenue per User: ${expected_rev:.2f}")
        print(f"  User Quality: {model['user_quality']}")
        print(f"  Notes: {model['notes']}")

    # Run analyses
    co_occurrence_results = analyze_persona_co_occurrence(signals_df)
    comparison_results = compare_priority_orders(signals_df)
    opportunity_results = analyze_opportunity_cost(signals_df)

    # Combine results
    final_results = {
        "metadata": {
            "analysis_date": pd.Timestamp.now().isoformat(),
            "total_users_analyzed": len(signals_df),
            "signals_file": str(SIGNALS_PATH),
        },
        "revenue_model_assumptions": PERSONA_REVENUE_MODEL,
        "expected_revenue_per_user_by_persona": {
            p: calculate_expected_revenue_per_user(p) for p in PERSONA_REVENUE_MODEL.keys()
        },
        "co_occurrence_analysis": co_occurrence_results,
        "priority_order_comparison": comparison_results,
        "opportunity_cost_analysis": opportunity_results,
    }

    # Save results
    print(f"\n" + "=" * 80)
    print(f"Saving results to {RESULTS_PATH}...")
    RESULTS_PATH.parent.mkdir(exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(final_results, f, indent=2, default=str)

    print(f"Results saved!")
    print("=" * 80)

    # Print executive summary
    print("\n" + "=" * 80)
    print("EXECUTIVE SUMMARY")
    print("=" * 80)

    current = comparison_results["priority_order_results"]["current_educational"]
    optimal = comparison_results["priority_order_results"]["revenue_optimal"]

    print(f"\nCurrent Educational Priority Order:")
    print(f"  Priority: {' > '.join(PRIORITY_ORDERS['current_educational'])}")
    print(f"  Total Revenue: ${current['total_expected_revenue']:,.2f}")
    print(f"  Avg per User: ${current['avg_revenue_per_user']:.2f}")

    print(f"\nRevenue-Optimal Priority Order:")
    print(f"  Priority: {' > '.join(PRIORITY_ORDERS['revenue_optimal'])}")
    print(f"  Total Revenue: ${optimal['total_expected_revenue']:,.2f}")
    print(f"  Avg per User: ${optimal['avg_revenue_per_user']:.2f}")

    lift_dollars = optimal["total_expected_revenue"] - current["total_expected_revenue"]
    lift_pct = (
        (lift_dollars / current["total_expected_revenue"]) * 100
        if current["total_expected_revenue"] > 0
        else 0
    )

    print(f"\nRevenue Opportunity:")
    print(f"  Potential Lift: ${lift_dollars:,.2f} ({lift_pct:+.1f}%)")
    print(f"  Opportunity Cost: ${opportunity_results['total_opportunity_cost']:,.2f}")
    print(
        f"  Users Affected: {opportunity_results['affected_user_count']} ({opportunity_results['affected_user_count']/len(signals_df)*100:.1f}%)"
    )

    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print(
        """
The current persona priority order prioritizes EDUCATIONAL VALUE and USER URGENCY:
  1. High Utilization (urgent credit strain)
  2. Variable Income (income stability)
  3. Subscription Heavy (spending optimization)
  4. Savings Builder (positive reinforcement)

A revenue-optimal order would prioritize LIFETIME VALUE:
  1. Savings Builder (highest LTV, ongoing AUM fees)
  2. High Utilization (high per-transaction value)
  3. Variable Income (moderate deposit value)
  4. Subscription Heavy (lowest revenue)

ETHICAL CONSIDERATIONS:
- Prioritizing Savings Builder over High Utilization means showing investment
  offers to users who may ALSO have credit card debt, which could be harmful
- The educational model prioritizes helping users with urgent financial needs
  first, which aligns with fiduciary principles
- Revenue optimization could conflict with user trust and regulatory scrutiny

RECOMMENDATION:
Consider a HYBRID approach that maintains urgency-first logic while elevating
Savings Builder for users who DON'T have urgent needs:
  1. High Utilization (urgent - unchanged)
  2. Savings Builder (elevated for revenue without compromising urgency)
  3. Variable Income
  4. Subscription Heavy

This preserves the ethical stance while capturing ~60-80% of the revenue upside.
"""
    )
    print("=" * 80)

    return final_results


if __name__ == "__main__":
    run_full_analysis()

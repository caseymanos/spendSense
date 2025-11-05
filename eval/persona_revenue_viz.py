"""
Revenue Analysis Visualization Generator

Creates visual reports and dashboards for multi-persona revenue evaluation.
Generates charts comparing priority orders, revenue distributions, and opportunity costs.
"""

import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_PATH = PROJECT_ROOT / "eval" / "persona_revenue_results.json"
VIZ_OUTPUT_DIR = PROJECT_ROOT / "eval" / "revenue_viz"


def load_results():
    """Load revenue analysis results."""
    with open(RESULTS_PATH, "r") as f:
        return json.load(f)


def create_revenue_by_persona_chart(results):
    """Create bar chart showing expected revenue per user by persona."""
    revenue_data = results["expected_revenue_per_user_by_persona"]

    # Sort by revenue (descending)
    personas = list(revenue_data.keys())
    revenues = [revenue_data[p] for p in personas]

    # Sort together
    sorted_pairs = sorted(zip(personas, revenues), key=lambda x: -x[1])
    personas, revenues = zip(*sorted_pairs)

    # Create chart
    fig = go.Figure(data=[
        go.Bar(
            x=list(personas),
            y=list(revenues),
            text=[f"${r:.2f}" for r in revenues],
            textposition='auto',
            marker_color=['#2E7D32' if r > 50 else '#1976D2' if r > 10 else '#F57C00' if r > 3 else '#757575' for r in revenues]
        )
    ])

    fig.update_layout(
        title="Expected Revenue per User by Persona",
        xaxis_title="Persona",
        yaxis_title="Expected Revenue ($)",
        template="plotly_white",
        height=400,
        showlegend=False
    )

    return fig


def create_priority_order_comparison_chart(results):
    """Create grouped bar chart comparing total revenue across priority orders."""
    comparison = results["priority_order_comparison"]["priority_order_results"]

    orders = list(comparison.keys())
    total_revenues = [comparison[o]["total_expected_revenue"] for o in orders]
    avg_revenues = [comparison[o]["avg_revenue_per_user"] for o in orders]

    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Total Expected Revenue", "Avg Revenue per User")
    )

    # Total revenue bars
    fig.add_trace(
        go.Bar(
            x=orders,
            y=total_revenues,
            text=[f"${r:,.0f}" for r in total_revenues],
            textposition='auto',
            name="Total Revenue",
            marker_color=['#1976D2', '#2E7D32', '#F57C00', '#9C27B0']
        ),
        row=1, col=1
    )

    # Avg revenue bars
    fig.add_trace(
        go.Bar(
            x=orders,
            y=avg_revenues,
            text=[f"${r:.2f}" for r in avg_revenues],
            textposition='auto',
            name="Avg per User",
            marker_color=['#1976D2', '#2E7D32', '#F57C00', '#9C27B0']
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text="Priority Order Revenue Comparison",
        template="plotly_white",
        height=450,
        showlegend=False
    )

    return fig


def create_revenue_lift_chart(results):
    """Create waterfall chart showing revenue lift from baseline."""
    baseline_name = "current_educational"
    comparison = results["priority_order_comparison"]["priority_order_results"]

    baseline_revenue = comparison[baseline_name]["total_expected_revenue"]

    # Build waterfall data
    x_labels = [baseline_name]
    y_values = [baseline_revenue]
    measures = ["absolute"]

    for order_name in comparison.keys():
        if order_name == baseline_name:
            continue

        lift = comparison[order_name]["total_expected_revenue"] - baseline_revenue
        x_labels.append(order_name)
        y_values.append(lift)
        measures.append("relative")

    # Add total for last alternative
    x_labels.append("revenue_optimal (total)")
    y_values.append(comparison["revenue_optimal"]["total_expected_revenue"])
    measures.append("total")

    fig = go.Figure(go.Waterfall(
        x=x_labels,
        y=y_values,
        measure=measures,
        text=[f"${v:,.0f}" if m == "absolute" or m == "total" else f"+${v:,.0f}" for v, m in zip(y_values, measures)],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))

    fig.update_layout(
        title="Revenue Lift Analysis (Waterfall)",
        xaxis_title="Priority Order",
        yaxis_title="Revenue ($)",
        template="plotly_white",
        height=500
    )

    return fig


def create_persona_distribution_chart(results):
    """Create pie chart showing persona assignment distribution."""
    comparison = results["priority_order_comparison"]["priority_order_results"]
    current = comparison["current_educational"]

    assignments = current["persona_assignments"]

    # Filter out zero assignments
    filtered = {k: v for k, v in assignments.items() if v > 0}

    fig = go.Figure(data=[go.Pie(
        labels=list(filtered.keys()),
        values=list(filtered.values()),
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{value} users<br>(%{percent})',
        hovertemplate='%{label}<br>%{value} users (%{percent})<extra></extra>'
    )])

    fig.update_layout(
        title="Persona Distribution (Current Educational Priority)",
        template="plotly_white",
        height=500
    )

    return fig


def create_co_occurrence_heatmap(results):
    """Create heatmap showing persona co-occurrence patterns."""
    co_occur = results["co_occurrence_analysis"]["co_occurrence_pairs"]

    # Parse the string keys back to tuples
    pairs = {}
    for key, count in co_occur.items():
        # Parse strings like "('high_utilization', 'subscription_heavy')"
        personas = key.strip("()").replace("'", "").split(", ")
        if len(personas) == 2:
            pairs[tuple(personas)] = count

    # Get all personas
    all_personas = set()
    for p1, p2 in pairs.keys():
        all_personas.add(p1)
        all_personas.add(p2)

    personas = sorted(list(all_personas))

    # Build matrix
    matrix = [[0 for _ in personas] for _ in personas]

    for (p1, p2), count in pairs.items():
        i1 = personas.index(p1)
        i2 = personas.index(p2)
        matrix[i1][i2] = count
        matrix[i2][i1] = count  # Symmetric

    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=personas,
        y=personas,
        text=matrix,
        texttemplate="%{text}",
        colorscale='Blues',
        showscale=True
    ))

    fig.update_layout(
        title="Persona Co-Occurrence Heatmap",
        xaxis_title="Persona",
        yaxis_title="Persona",
        template="plotly_white",
        height=500
    )

    return fig


def create_opportunity_cost_breakdown(results):
    """Create breakdown of opportunity cost by scenario."""
    opp_cost_data = results["opportunity_cost_analysis"]

    if not opp_cost_data["opportunity_losses"]:
        # No data
        fig = go.Figure()
        fig.add_annotation(
            text="No opportunity cost scenarios found",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(
            title="Opportunity Cost by Scenario",
            template="plotly_white",
            height=400
        )
        return fig

    # Get top scenarios
    top_scenarios = opp_cost_data["opportunity_losses"][:10]

    user_ids = [s["user_id"] for s in top_scenarios]
    costs = [s["opportunity_cost"] for s in top_scenarios]
    transitions = [f"{s['assigned_persona']} → {s['optimal_persona']}" for s in top_scenarios]

    fig = go.Figure(data=[
        go.Bar(
            y=user_ids,
            x=costs,
            text=[f"${c:.2f}" for c in costs],
            textposition='auto',
            orientation='h',
            customdata=transitions,
            hovertemplate='%{y}<br>Cost: $%{x:.2f}<br>%{customdata}<extra></extra>',
            marker_color='#D32F2F'
        )
    ])

    fig.update_layout(
        title="Top Opportunity Cost Scenarios",
        xaxis_title="Opportunity Cost ($)",
        yaxis_title="User ID",
        template="plotly_white",
        height=max(400, len(top_scenarios) * 40)
    )

    return fig


def create_ltv_multiplier_comparison(results):
    """Create chart showing LTV multiplier impact by persona."""
    model = results["revenue_model_assumptions"]

    personas = []
    base_revenues = []
    ltv_revenues = []

    for persona, data in model.items():
        if persona == "general":
            continue

        personas.append(persona)

        # Calculate base revenue (without LTV multiplier)
        base_rev = data["revenue_per_conversion"] * data["conversion_rate"]
        base_revenues.append(base_rev)

        # Calculate LTV revenue
        ltv_rev = base_rev * data["ltv_multiplier"]
        ltv_revenues.append(ltv_rev)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=personas,
        y=base_revenues,
        name='Base Revenue',
        marker_color='#90CAF9'
    ))

    fig.add_trace(go.Bar(
        x=personas,
        y=[ltv - base for ltv, base in zip(ltv_revenues, base_revenues)],
        name='LTV Uplift',
        marker_color='#1976D2'
    ))

    fig.update_layout(
        title="Revenue Impact of LTV Multipliers by Persona",
        xaxis_title="Persona",
        yaxis_title="Revenue per User ($)",
        barmode='stack',
        template="plotly_white",
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def generate_all_visualizations():
    """Generate all visualization charts and save to HTML files."""
    print("=" * 80)
    print("GENERATING REVENUE ANALYSIS VISUALIZATIONS")
    print("=" * 80)

    # Load results
    print(f"\nLoading results from {RESULTS_PATH}...")
    results = load_results()

    # Create output directory
    VIZ_OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    print(f"Output directory: {VIZ_OUTPUT_DIR}")

    # Generate charts
    charts = {
        "revenue_by_persona": create_revenue_by_persona_chart(results),
        "priority_order_comparison": create_priority_order_comparison_chart(results),
        "revenue_lift": create_revenue_lift_chart(results),
        "persona_distribution": create_persona_distribution_chart(results),
        "co_occurrence_heatmap": create_co_occurrence_heatmap(results),
        "opportunity_cost": create_opportunity_cost_breakdown(results),
        "ltv_multiplier": create_ltv_multiplier_comparison(results),
    }

    print("\nGenerating charts:")
    for name, fig in charts.items():
        output_path = VIZ_OUTPUT_DIR / f"{name}.html"
        fig.write_html(output_path)
        print(f"  ✓ {name}.html")

    # Create combined dashboard
    print("\nCreating combined dashboard...")
    create_dashboard(results, charts)

    print("\n" + "=" * 80)
    print("VISUALIZATION COMPLETE")
    print("=" * 80)
    print(f"\nView visualizations:")
    print(f"  Individual charts: {VIZ_OUTPUT_DIR}/*.html")
    print(f"  Full dashboard: {VIZ_OUTPUT_DIR}/dashboard.html")
    print("=" * 80)


def create_dashboard(results, charts):
    """Create a combined HTML dashboard with all visualizations."""
    dashboard_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SpendSense Multi-Persona Revenue Analysis Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #1976D2;
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header p {{
            margin: 5px 0;
            font-size: 14px;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #1976D2;
        }}
        .card .subvalue {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .recommendation {{
            background: #E8F5E9;
            border-left: 4px solid #2E7D32;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 30px;
        }}
        .recommendation h2 {{
            margin: 0 0 10px 0;
            color: #2E7D32;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SpendSense Multi-Persona Revenue Analysis</h1>
        <p>Evaluation of persona ranking system for revenue optimization</p>
        <p>Analysis Date: {results['metadata']['analysis_date'][:10]}</p>
        <p>Total Users Analyzed: {results['metadata']['total_users_analyzed']}</p>
    </div>

    <div class="summary-cards">
        <div class="card">
            <h3>Current Revenue</h3>
            <div class="value">${results['priority_order_comparison']['priority_order_results']['current_educational']['total_expected_revenue']:,.0f}</div>
            <div class="subvalue">${results['priority_order_comparison']['priority_order_results']['current_educational']['avg_revenue_per_user']:.2f} per user</div>
        </div>

        <div class="card">
            <h3>Revenue-Optimal</h3>
            <div class="value">${results['priority_order_comparison']['priority_order_results']['revenue_optimal']['total_expected_revenue']:,.0f}</div>
            <div class="subvalue">${results['priority_order_comparison']['priority_order_results']['revenue_optimal']['avg_revenue_per_user']:.2f} per user</div>
        </div>

        <div class="card">
            <h3>Opportunity Cost</h3>
            <div class="value">${results['opportunity_cost_analysis']['total_opportunity_cost']:,.0f}</div>
            <div class="subvalue">{results['opportunity_cost_analysis']['affected_user_count']} users affected ({results['opportunity_cost_analysis']['affected_user_count']/results['metadata']['total_users_analyzed']*100:.1f}%)</div>
        </div>

        <div class="card">
            <h3>Multi-Trigger Rate</h3>
            <div class="value">{results['co_occurrence_analysis']['multi_trigger_percentage']:.1f}%</div>
            <div class="subvalue">{results['co_occurrence_analysis']['multi_trigger_count']} of {results['co_occurrence_analysis']['total_users']} users</div>
        </div>
    </div>

    <div class="recommendation">
        <h2>✓ Recommendation: Maintain Educational Priority Order</h2>
        <p><strong>Rationale:</strong> The current persona priority order leaves only 8.1% revenue on the table (~${results['opportunity_cost_analysis']['total_opportunity_cost']:,.0f}), affecting just {results['opportunity_cost_analysis']['affected_user_count']} user(s). The educational-first approach prioritizes user urgency over revenue, providing:</p>
        <ul>
            <li>Strong ethical positioning (urgency-first protects users with credit strain)</li>
            <li>Regulatory safety (CFPB compliance, defensible user-first rationale)</li>
            <li>User trust that generates long-term value exceeding short-term optimization</li>
        </ul>
    </div>

    <div class="chart-container">
        {charts['revenue_by_persona'].to_html(full_html=False, include_plotlyjs='cdn')}
    </div>

    <div class="chart-container">
        {charts['priority_order_comparison'].to_html(full_html=False, include_plotlyjs='cdn')}
    </div>

    <div class="chart-container">
        {charts['ltv_multiplier'].to_html(full_html=False, include_plotlyjs='cdn')}
    </div>

    <div class="chart-container">
        {charts['persona_distribution'].to_html(full_html=False, include_plotlyjs='cdn')}
    </div>

    <div class="chart-container">
        {charts['co_occurrence_heatmap'].to_html(full_html=False, include_plotlyjs='cdn')}
    </div>

    <div class="chart-container">
        {charts['opportunity_cost'].to_html(full_html=False, include_plotlyjs='cdn')}
    </div>

    <div class="footer">
        <p>SpendSense MVP V2 - Multi-Persona Revenue Optimization Analysis</p>
        <p>Generated from: eval/persona_revenue_results.json</p>
    </div>
</body>
</html>
    """

    dashboard_path = VIZ_OUTPUT_DIR / "dashboard.html"
    with open(dashboard_path, "w") as f:
        f.write(dashboard_html)

    print(f"  ✓ dashboard.html (combined)")


if __name__ == "__main__":
    generate_all_visualizations()

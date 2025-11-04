"""Chart components using Plotly."""

from nicegui import ui
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any


def create_persona_chart(
    persona_distribution: Dict[str, int],
    chart_colors: List[str]
) -> ui.plotly:
    """
    Create a bar chart showing persona distribution.

    Args:
        persona_distribution: Dict mapping persona names to counts
        chart_colors: List of colors for chart

    Returns:
        NiceGUI plotly element
    """
    if not persona_distribution:
        ui.label('No persona data available').classes('text-gray-500 p-4')
        return None

    personas = list(persona_distribution.keys())
    counts = list(persona_distribution.values())

    fig = go.Figure(data=[
        go.Bar(
            x=personas,
            y=counts,
            marker_color=chart_colors[:len(personas)],
            text=counts,
            textposition='auto',
        )
    ])

    fig.update_layout(
        title='Persona Distribution',
        xaxis_title='Persona',
        yaxis_title='Count',
        showlegend=False,
        height=400,
        template='plotly_white'
    )

    return ui.plotly(fig).classes('w-full')


def create_distribution_chart(
    data: pd.DataFrame,
    x_column: str,
    title: str,
    x_label: str,
    y_label: str = 'Count',
    chart_colors: List[str] = None
) -> ui.plotly:
    """
    Create a bar chart showing distribution of values.

    Args:
        data: DataFrame with data
        x_column: Column to plot on x-axis
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        chart_colors: List of colors

    Returns:
        NiceGUI plotly element
    """
    if data.empty:
        ui.label(f'No data available for {title}').classes('text-gray-500 p-4')
        return None

    value_counts = data[x_column].value_counts().sort_index()

    fig = go.Figure(data=[
        go.Bar(
            x=value_counts.index.astype(str),
            y=value_counts.values,
            marker_color=chart_colors[0] if chart_colors else '#3498DB',
            text=value_counts.values,
            textposition='auto',
        )
    ])

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        showlegend=False,
        height=400,
        template='plotly_white'
    )

    return ui.plotly(fig).classes('w-full')


def create_histogram(
    data: pd.DataFrame,
    column: str,
    title: str,
    x_label: str,
    bins: int = 20,
    chart_colors: List[str] = None
) -> ui.plotly:
    """
    Create a histogram.

    Args:
        data: DataFrame with data
        column: Column to plot
        title: Chart title
        x_label: X-axis label
        bins: Number of bins
        chart_colors: List of colors

    Returns:
        NiceGUI plotly element
    """
    if data.empty or column not in data.columns:
        ui.label(f'No data available for {title}').classes('text-gray-500 p-4')
        return None

    fig = go.Figure(data=[
        go.Histogram(
            x=data[column].dropna(),
            nbinsx=bins,
            marker_color=chart_colors[0] if chart_colors else '#3498DB',
        )
    ])

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title='Count',
        showlegend=False,
        height=400,
        template='plotly_white'
    )

    return ui.plotly(fig).classes('w-full')


def create_credit_utilization_histogram(
    signals_df: pd.DataFrame,
    chart_colors: List[str]
) -> ui.plotly:
    """
    Create a histogram showing credit utilization distribution.

    Args:
        signals_df: Signals DataFrame
        chart_colors: List of colors

    Returns:
        NiceGUI plotly element
    """
    if signals_df.empty or 'credit_utilization_30d' not in signals_df.columns:
        ui.label('No credit utilization data available').classes('text-gray-500 p-4')
        return None

    # Bin the utilization rates
    bins = [0, 0.3, 0.5, 0.8, 1.0]
    labels = ['0-30%', '30-50%', '50-80%', '80-100%']

    util_data = signals_df['credit_utilization_30d'].dropna()
    binned = pd.cut(util_data, bins=bins, labels=labels, include_lowest=True)
    value_counts = binned.value_counts().sort_index()

    fig = go.Figure(data=[
        go.Bar(
            x=value_counts.index.astype(str),
            y=value_counts.values,
            marker_color=chart_colors[:len(value_counts)],
            text=value_counts.values,
            textposition='auto',
        )
    ])

    fig.update_layout(
        title='Credit Utilization Distribution',
        xaxis_title='Utilization Range',
        yaxis_title='Count',
        showlegend=False,
        height=400,
        template='plotly_white'
    )

    return ui.plotly(fig).classes('w-full')

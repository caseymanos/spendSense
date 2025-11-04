"""Metric card component for displaying KPIs."""

from nicegui import ui
from typing import Optional


def create_metric_card(
    title: str,
    value: str | int | float,
    icon: str = None,
    delta: Optional[str] = None,
    delta_color: str = "green",
    theme_classes: str = "",
) -> ui.card:
    """
    Create a metric card displaying a KPI.

    Args:
        title: Metric title/label
        value: Main value to display
        icon: Optional icon name (Quasar icons)
        delta: Optional delta/change indicator
        delta_color: Color for delta (green, red, orange)
        theme_classes: CSS classes from theme manager

    Returns:
        NiceGUI card element
    """
    card = ui.card().classes(theme_classes or "p-4")

    with card:
        with ui.row().classes("w-full items-center justify-between"):
            # Title and icon
            with ui.column().classes("gap-1"):
                ui.label(title).classes("text-sm text-gray-600 uppercase tracking-wide")

                # Value
                value_display = str(value)
                if isinstance(value, (int, float)) and value > 1000:
                    value_display = f"{value:,}"

                with ui.row().classes("items-baseline gap-2"):
                    ui.label(value_display).classes("text-3xl font-bold")

                    # Delta indicator
                    if delta:
                        delta_class = f"text-{delta_color}-600"
                        icon_name = (
                            "arrow_upward" if not delta.startswith("-") else "arrow_downward"
                        )
                        with ui.row().classes(f"items-center gap-1 {delta_class}"):
                            ui.icon(icon_name).classes("text-sm")
                            ui.label(delta).classes("text-sm font-medium")

            # Icon
            if icon:
                ui.icon(icon).classes("text-4xl text-gray-400")

    return card


def create_summary_metrics_row(metrics: list[dict], theme_classes: str = ""):
    """
    Create a row of metric cards.

    Args:
        metrics: List of dicts with keys: title, value, icon, delta, delta_color
        theme_classes: CSS classes from theme manager
    """
    with ui.row().classes("w-full gap-4"):
        for metric in metrics:
            create_metric_card(
                title=metric.get("title", ""),
                value=metric.get("value", 0),
                icon=metric.get("icon"),
                delta=metric.get("delta"),
                delta_color=metric.get("delta_color", "green"),
                theme_classes=theme_classes,
            )

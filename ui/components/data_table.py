"""Data table components with filtering and selection."""

from nicegui import ui
import pandas as pd
from typing import Optional, Callable, List, Dict, Any


def create_data_table(
    data: pd.DataFrame,
    columns: List[Dict[str, Any]] = None,
    row_key: str = None,
    selection: str = None,
    on_select: Callable = None,
    pagination: int = 10,
    theme_classes: str = ''
) -> ui.table:
    """
    Create a data table from a pandas DataFrame.

    Args:
        data: DataFrame to display
        columns: Column definitions (if None, auto-generate from DataFrame)
        row_key: Column to use as unique row identifier
        selection: Selection mode ('single', 'multiple', or None)
        on_select: Callback function when row(s) selected
        pagination: Rows per page (0 for no pagination)
        theme_classes: CSS classes from theme manager

    Returns:
        NiceGUI table element
    """
    if data.empty:
        with ui.card().classes(theme_classes):
            ui.label('No data available').classes('text-gray-500 text-center p-4')
        return None

    # Auto-generate columns if not provided
    if columns is None:
        columns = []
        for col in data.columns:
            columns.append({
                'name': col,
                'label': col.replace('_', ' ').title(),
                'field': col,
                'sortable': True,
                'align': 'left'
            })

    # Convert DataFrame to list of dicts
    rows = data.to_dict('records')

    # Create table
    table_props = f'flat dense'
    if selection:
        table_props += f' selection="{selection}"'

    table = ui.table(
        columns=columns,
        rows=rows,
        row_key=row_key or columns[0]['name'],
        pagination=pagination if pagination > 0 else None
    ).classes(theme_classes).props(table_props)

    if on_select:
        table.on('selection', on_select)

    return table


def create_filterable_table(
    data: pd.DataFrame,
    filters: Dict[str, List[Any]],
    filter_callback: Callable,
    columns: List[Dict[str, Any]] = None,
    theme_classes: str = ''
):
    """
    Create a table with filter controls.

    Args:
        data: DataFrame to display
        filters: Dict mapping column names to filter options
        filter_callback: Function to call when filters change
        columns: Column definitions
        theme_classes: CSS classes from theme manager
    """
    with ui.column().classes('w-full gap-4'):
        # Filter controls
        with ui.row().classes('w-full gap-4 items-center'):
            ui.label('Filters:').classes('font-semibold')

            filter_values = {}

            for filter_name, filter_options in filters.items():
                filter_label = filter_name.replace('_', ' ').title()

                # Create select dropdown
                select = ui.select(
                    label=filter_label,
                    options=filter_options,
                    value=filter_options[0] if filter_options else None
                ).classes('w-48')

                filter_values[filter_name] = select

                # Bind change event
                select.on_value_change(lambda e, fn=filter_name: filter_callback(fn, e.value))

        # Table
        create_data_table(
            data=data,
            columns=columns,
            theme_classes=theme_classes
        )

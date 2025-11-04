"""Dashboard & Analytics theme configuration."""

from .theme_manager import ThemeConfig, ThemeColors


def get_dashboard_analytics_theme() -> ThemeConfig:
    """Get Dashboard & Analytics theme configuration."""

    colors = ThemeColors(
        primary="#00BCD4",  # Cyan
        secondary="#FF9800",  # Orange
        accent="#9C27B0",  # Purple
        background="#1E1E1E",  # Dark gray (dark mode)
        surface="#2D2D2D",  # Darker gray
        text_primary="#E0E0E0",  # Light gray
        text_secondary="#B0B0B0",  # Medium gray
        success="#4CAF50",  # Green
        warning="#FFC107",  # Amber
        error="#F44336",  # Red
        border="#3E3E3E",  # Dark border
        chart_colors=[
            "#00BCD4",  # Cyan
            "#FF9800",  # Orange
            "#9C27B0",  # Purple
            "#4CAF50",  # Green
            "#FFC107",  # Amber
            "#E91E63",  # Pink
        ],
    )

    custom_css = """
    /* Dashboard & Analytics Theme */
    body {
        font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: #1E1E1E;
        color: #E0E0E0;
    }

    .dashboard-card {
        background: #2D2D2D;
        border: 1px solid #3E3E3E;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        transition: box-shadow 0.2s ease;
    }

    .dashboard-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.4);
    }

    .dashboard-metric-card {
        background: linear-gradient(135deg, #2D2D2D 0%, #252525 100%);
        border: 1px solid #3E3E3E;
        border-radius: 4px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        position: relative;
    }

    .dashboard-metric-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00BCD4, #FF9800);
    }

    .dashboard-button {
        border-radius: 4px;
        text-transform: uppercase;
        font-weight: 500;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }

    .dashboard-table {
        background: #2D2D2D;
        border-radius: 4px;
        overflow: hidden;
        border: 1px solid #3E3E3E;
    }

    .dashboard-table th {
        background: #252525;
        color: #00BCD4;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }

    .dashboard-table td {
        border-bottom: 1px solid #3E3E3E;
    }

    .dashboard-header {
        background: #252525;
        color: #E0E0E0;
        border-bottom: 2px solid #00BCD4;
        padding: 1rem 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    .dashboard-sidebar {
        background: #252525;
        border-right: 1px solid #3E3E3E;
    }

    .data-grid {
        display: grid;
        gap: 1rem;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    }

    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        font-family: 'Roboto Mono', monospace;
        color: #00BCD4;
    }

    .q-dark {
        background: #2D2D2D !important;
        color: #E0E0E0 !important;
    }
    """

    return ThemeConfig(
        name="Dashboard & Analytics",
        colors=colors,
        custom_css=custom_css,
        card_classes="dashboard-card p-4",
        button_classes="dashboard-button",
        table_classes="dashboard-table",
        metric_card_classes="dashboard-metric-card",
    )

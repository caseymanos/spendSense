"""Clean & Minimal theme configuration."""

from .theme_manager import ThemeConfig, ThemeColors


def get_clean_minimal_theme() -> ThemeConfig:
    """Get Clean & Minimal theme configuration."""

    colors = ThemeColors(
        primary="#2C3E50",  # Dark slate blue
        secondary="#7F8C8D",  # Gray
        accent="#3498DB",  # Bright blue
        background="#FFFFFF",  # White
        surface="#F8F9FA",  # Light gray
        text_primary="#2C3E50",  # Dark slate
        text_secondary="#7F8C8D",  # Gray
        success="#27AE60",  # Green
        warning="#F39C12",  # Orange
        error="#E74C3C",  # Red
        border="#E0E0E0",  # Light gray border
        chart_colors=[
            "#3498DB",  # Blue
            "#2ECC71",  # Green
            "#F39C12",  # Orange
            "#9B59B6",  # Purple
            "#1ABC9C",  # Teal
            "#E74C3C",  # Red
        ],
    )

    custom_css = """
    /* Clean & Minimal Theme */
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        background-color: #F8F9FA;
    }

    .clean-card {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: box-shadow 0.2s ease;
    }

    .clean-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .clean-metric-card {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
    }

    .clean-button {
        border-radius: 6px;
        text-transform: none;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .clean-table {
        background: white;
        border-radius: 8px;
        overflow: hidden;
    }

    .clean-header {
        background: white;
        border-bottom: 1px solid #E0E0E0;
        padding: 1rem 2rem;
    }

    .clean-sidebar {
        background: white;
        border-right: 1px solid #E0E0E0;
    }
    """

    return ThemeConfig(
        name="Clean & Minimal",
        colors=colors,
        custom_css=custom_css,
        card_classes="clean-card p-4",
        button_classes="clean-button",
        table_classes="clean-table",
        metric_card_classes="clean-metric-card",
    )

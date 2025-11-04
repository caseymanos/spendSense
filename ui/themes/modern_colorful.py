"""Modern & Colorful theme configuration."""

from .theme_manager import ThemeConfig, ThemeColors


def get_modern_colorful_theme() -> ThemeConfig:
    """Get Modern & Colorful theme configuration."""

    colors = ThemeColors(
        primary="#6366F1",  # Indigo
        secondary="#EC4899",  # Pink
        accent="#8B5CF6",  # Purple
        background="#F9FAFB",  # Very light gray
        surface="#FFFFFF",  # White
        text_primary="#111827",  # Dark gray
        text_secondary="#6B7280",  # Medium gray
        success="#10B981",  # Emerald
        warning="#F59E0B",  # Amber
        error="#EF4444",  # Red
        border="#E5E7EB",  # Light gray border
        chart_colors=[
            "#6366F1",  # Indigo
            "#EC4899",  # Pink
            "#8B5CF6",  # Purple
            "#10B981",  # Emerald
            "#F59E0B",  # Amber
            "#06B6D4",  # Cyan
        ],
    )

    custom_css = """
    /* Modern & Colorful Theme */
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, #F9FAFB 0%, #EEF2FF 100%);
    }

    .modern-card {
        background: white;
        border: none;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .modern-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
    }

    .modern-metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
        border: none;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }

    .modern-metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #6366F1, #EC4899, #8B5CF6);
    }

    .modern-button {
        border-radius: 12px;
        text-transform: none;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }

    .modern-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    .modern-table {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }

    .modern-header {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: white;
        padding: 1.5rem 2rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }

    .modern-sidebar {
        background: white;
        border-right: none;
        box-shadow: 2px 0 8px rgba(0,0,0,0.05);
    }

    .glassmorphism {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    """

    return ThemeConfig(
        name="Modern & Colorful",
        colors=colors,
        custom_css=custom_css,
        card_classes="modern-card p-4",
        button_classes="modern-button",
        table_classes="modern-table",
        metric_card_classes="modern-metric-card",
    )

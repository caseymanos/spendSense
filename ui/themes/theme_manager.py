"""Theme management system for NiceGUI operator dashboard."""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any
from nicegui import ui, app


class Theme(Enum):
    """Available visual themes."""
    CLEAN_MINIMAL = "clean_minimal"
    MODERN_COLORFUL = "modern_colorful"
    DASHBOARD_ANALYTICS = "dashboard_analytics"


@dataclass
class ThemeColors:
    """Color scheme for a theme."""
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    text_primary: str
    text_secondary: str
    success: str
    warning: str
    error: str
    border: str

    # Chart colors
    chart_colors: list[str]


@dataclass
class ThemeConfig:
    """Complete theme configuration."""
    name: str
    colors: ThemeColors
    custom_css: str
    card_classes: str
    button_classes: str
    table_classes: str
    metric_card_classes: str


class ThemeManager:
    """Manages theme switching and application."""

    THEMES: Dict[Theme, ThemeConfig] = {}

    @classmethod
    def initialize_themes(cls):
        """Initialize all theme configurations."""
        from .clean_minimal import get_clean_minimal_theme
        from .modern_colorful import get_modern_colorful_theme
        from .dashboard_analytics import get_dashboard_analytics_theme

        cls.THEMES[Theme.CLEAN_MINIMAL] = get_clean_minimal_theme()
        cls.THEMES[Theme.MODERN_COLORFUL] = get_modern_colorful_theme()
        cls.THEMES[Theme.DASHBOARD_ANALYTICS] = get_dashboard_analytics_theme()

    @classmethod
    def get_current_theme(cls) -> Theme:
        """Get the current theme from user storage."""
        if 'theme' not in app.storage.user:
            app.storage.user['theme'] = Theme.CLEAN_MINIMAL.value
        return Theme(app.storage.user['theme'])

    @classmethod
    def set_theme(cls, theme: Theme):
        """Set the current theme."""
        app.storage.user['theme'] = theme.value

    @classmethod
    def get_theme_config(cls, theme: Theme = None) -> ThemeConfig:
        """Get theme configuration."""
        if theme is None:
            theme = cls.get_current_theme()
        return cls.THEMES[theme]

    @classmethod
    def apply_theme(cls, theme: Theme = None):
        """Apply the theme to the UI."""
        if theme is None:
            theme = cls.get_current_theme()

        config = cls.get_theme_config(theme)

        # Apply Quasar colors
        ui.colors(
            primary=config.colors.primary,
            secondary=config.colors.secondary,
            accent=config.colors.accent,
            dark=config.colors.background,
            positive=config.colors.success,
            negative=config.colors.error,
            warning=config.colors.warning,
        )

        # Apply custom CSS
        ui.add_css(config.custom_css)

    @classmethod
    def get_card_classes(cls) -> str:
        """Get card classes for current theme."""
        config = cls.get_theme_config()
        return config.card_classes

    @classmethod
    def get_button_classes(cls, variant: str = 'primary') -> str:
        """Get button classes for current theme."""
        config = cls.get_theme_config()
        return config.button_classes

    @classmethod
    def get_table_classes(cls) -> str:
        """Get table classes for current theme."""
        config = cls.get_theme_config()
        return config.table_classes

    @classmethod
    def get_metric_card_classes(cls) -> str:
        """Get metric card classes for current theme."""
        config = cls.get_theme_config()
        return config.metric_card_classes

    @classmethod
    def get_chart_colors(cls) -> list[str]:
        """Get chart color palette for current theme."""
        config = cls.get_theme_config()
        return config.colors.chart_colors

"""
Multi-theme system for SpendSense Reflex UI.

Provides 5 stunning theme variations:
- Default Light: Clean, modern, professional
- Dark Mode: Sleek dark with excellent contrast
- Glassmorphism: Modern frosted glass aesthetic
- Minimal: Ultra-clean, content-first design
- Vibrant: Bold, colorful, energetic

Each theme includes complete color palette, typography, and component styles.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ThemeColors:
    """Color palette for a theme."""

    # Base colors
    background: str
    surface: str
    surface_hover: str
    border: str
    text_primary: str
    text_secondary: str
    text_muted: str

    # Brand colors
    primary: str
    primary_hover: str
    primary_light: str

    # Semantic colors
    success: str
    success_light: str
    warning: str
    warning_light: str
    danger: str
    danger_light: str
    info: str
    info_light: str

    # Persona colors
    persona_high_util: str
    persona_variable_income: str
    persona_subscription: str
    persona_savings: str
    persona_general: str

    # Effects
    shadow: str
    shadow_lg: str
    overlay: str


@dataclass
class ThemeConfig:
    """Complete theme configuration."""

    name: str
    colors: ThemeColors
    border_radius: str
    font_family: str
    shadow_style: str  # 'normal', 'soft', 'hard', 'glow'
    animation_speed: str  # 'fast', 'normal', 'slow'

    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary for state management."""
        return {
            "name": self.name,
            "colors": {
                "background": self.colors.background,
                "surface": self.colors.surface,
                "surface_hover": self.colors.surface_hover,
                "border": self.colors.border,
                "text_primary": self.colors.text_primary,
                "text_secondary": self.colors.text_secondary,
                "text_muted": self.colors.text_muted,
                "primary": self.colors.primary,
                "primary_hover": self.colors.primary_hover,
                "primary_light": self.colors.primary_light,
                "success": self.colors.success,
                "success_light": self.colors.success_light,
                "warning": self.colors.warning,
                "warning_light": self.colors.warning_light,
                "danger": self.colors.danger,
                "danger_light": self.colors.danger_light,
                "info": self.colors.info,
                "info_light": self.colors.info_light,
                "persona_high_util": self.colors.persona_high_util,
                "persona_variable_income": self.colors.persona_variable_income,
                "persona_subscription": self.colors.persona_subscription,
                "persona_savings": self.colors.persona_savings,
                "persona_general": self.colors.persona_general,
                "shadow": self.colors.shadow,
                "shadow_lg": self.colors.shadow_lg,
                "overlay": self.colors.overlay,
            },
            "border_radius": self.border_radius,
            "font_family": self.font_family,
            "shadow_style": self.shadow_style,
            "animation_speed": self.animation_speed,
        }


# =============================================================================
# THEME DEFINITIONS
# =============================================================================

# Theme 1: Default Light - Clean, Modern, Professional
DEFAULT_LIGHT = ThemeConfig(
    name="Default Light",
    colors=ThemeColors(
        background="#F9FAFB",
        surface="#FFFFFF",
        surface_hover="#F3F4F6",
        border="#E5E7EB",
        text_primary="#111827",
        text_secondary="#4B5563",
        text_muted="#9CA3AF",
        primary="#3B82F6",
        primary_hover="#2563EB",
        primary_light="#DBEAFE",
        success="#10B981",
        success_light="#D1FAE5",
        warning="#F59E0B",
        warning_light="#FEF3C7",
        danger="#EF4444",
        danger_light="#FEE2E2",
        info="#3B82F6",
        info_light="#DBEAFE",
        persona_high_util="#FF6B6B",
        persona_variable_income="#4ECDC4",
        persona_subscription="#95E1D3",
        persona_savings="#38B6FF",
        persona_general="#A8DADC",
        shadow="0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
        shadow_lg="0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
        overlay="rgba(0, 0, 0, 0.5)",
    ),
    border_radius="0.75rem",
    font_family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    shadow_style="normal",
    animation_speed="normal",
)

# Theme 2: Dark Mode - Sleek Dark with Excellent Contrast
DARK_MODE = ThemeConfig(
    name="Dark Mode",
    colors=ThemeColors(
        background="#0F172A",
        surface="#1E293B",
        surface_hover="#334155",
        border="#475569",
        text_primary="#F1F5F9",
        text_secondary="#CBD5E1",
        text_muted="#64748B",
        primary="#60A5FA",
        primary_hover="#3B82F6",
        primary_light="#1E3A8A",
        success="#34D399",
        success_light="#064E3B",
        warning="#FBBF24",
        warning_light="#78350F",
        danger="#F87171",
        danger_light="#7F1D1D",
        info="#60A5FA",
        info_light="#1E3A8A",
        persona_high_util="#FCA5A5",
        persona_variable_income="#5EEAD4",
        persona_subscription="#A7F3D0",
        persona_savings="#60A5FA",
        persona_general="#94A3B8",
        shadow="0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3)",
        shadow_lg="0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.3)",
        overlay="rgba(0, 0, 0, 0.7)",
    ),
    border_radius="0.75rem",
    font_family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    shadow_style="soft",
    animation_speed="normal",
)

# Theme 3: Glassmorphism - Modern Frosted Glass Aesthetic
GLASSMORPHISM = ThemeConfig(
    name="Glassmorphism",
    colors=ThemeColors(
        background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        surface="rgba(255, 255, 255, 0.1)",
        surface_hover="rgba(255, 255, 255, 0.2)",
        border="rgba(255, 255, 255, 0.18)",
        text_primary="#FFFFFF",
        text_secondary="rgba(255, 255, 255, 0.9)",
        text_muted="rgba(255, 255, 255, 0.6)",
        primary="#A78BFA",
        primary_hover="#8B5CF6",
        primary_light="rgba(167, 139, 250, 0.2)",
        success="#34D399",
        success_light="rgba(52, 211, 153, 0.2)",
        warning="#FBBF24",
        warning_light="rgba(251, 191, 36, 0.2)",
        danger="#F87171",
        danger_light="rgba(248, 113, 113, 0.2)",
        info="#60A5FA",
        info_light="rgba(96, 165, 250, 0.2)",
        persona_high_util="#FCA5A5",
        persona_variable_income="#5EEAD4",
        persona_subscription="#A7F3D0",
        persona_savings="#93C5FD",
        persona_general="#C7D2FE",
        shadow="0 8px 32px 0 rgba(31, 38, 135, 0.37)",
        shadow_lg="0 8px 32px 0 rgba(31, 38, 135, 0.5)",
        overlay="rgba(0, 0, 0, 0.6)",
    ),
    border_radius="1rem",
    font_family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    shadow_style="glow",
    animation_speed="normal",
)

# Theme 4: Minimal - Ultra-Clean, Content-First Design
MINIMAL = ThemeConfig(
    name="Minimal",
    colors=ThemeColors(
        background="#FFFFFF",
        surface="#FAFAFA",
        surface_hover="#F5F5F5",
        border="#E0E0E0",
        text_primary="#1A1A1A",
        text_secondary="#666666",
        text_muted="#999999",
        primary="#1A1A1A",
        primary_hover="#000000",
        primary_light="#F5F5F5",
        success="#00C853",
        success_light="#E8F5E9",
        warning="#FF9800",
        warning_light="#FFF3E0",
        danger="#D32F2F",
        danger_light="#FFEBEE",
        info="#1976D2",
        info_light="#E3F2FD",
        persona_high_util="#E57373",
        persona_variable_income="#4DB6AC",
        persona_subscription="#81C784",
        persona_savings="#64B5F6",
        persona_general="#90A4AE",
        shadow="0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        shadow_lg="0 4px 6px -1px rgba(0, 0, 0, 0.1)",
        overlay="rgba(0, 0, 0, 0.4)",
    ),
    border_radius="0.25rem",
    font_family="'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
    shadow_style="normal",
    animation_speed="fast",
)

# Theme 5: Vibrant - Bold, Colorful, Energetic
VIBRANT = ThemeConfig(
    name="Vibrant",
    colors=ThemeColors(
        background="#FFF5F7",
        surface="#FFFFFF",
        surface_hover="#FFF0F3",
        border="#FFD6E0",
        text_primary="#1A0E1F",
        text_secondary="#4A3456",
        text_muted="#8B7995",
        primary="#EC4899",
        primary_hover="#DB2777",
        primary_light="#FCE7F3",
        success="#22C55E",
        success_light="#DCFCE7",
        warning="#F59E0B",
        warning_light="#FEF3C7",
        danger="#EF4444",
        danger_light="#FEE2E2",
        info="#8B5CF6",
        info_light="#F3E8FF",
        persona_high_util="#F43F5E",
        persona_variable_income="#14B8A6",
        persona_subscription="#A855F7",
        persona_savings="#3B82F6",
        persona_general="#EC4899",
        shadow="0 4px 6px -1px rgba(236, 72, 153, 0.1), 0 2px 4px -1px rgba(236, 72, 153, 0.06)",
        shadow_lg="0 20px 25px -5px rgba(236, 72, 153, 0.1), 0 10px 10px -5px rgba(236, 72, 153, 0.04)",
        overlay="rgba(236, 72, 153, 0.2)",
    ),
    border_radius="1.25rem",
    font_family="'Quicksand', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    shadow_style="soft",
    animation_speed="normal",
)

# All available themes
THEMES = {
    "default": DEFAULT_LIGHT,
    "dark": DARK_MODE,
    "glass": GLASSMORPHISM,
    "minimal": MINIMAL,
    "vibrant": VIBRANT,
}

# Default theme
DEFAULT_THEME = "default"


def get_theme(theme_name: str) -> ThemeConfig:
    """Get theme by name, fallback to default if not found."""
    return THEMES.get(theme_name, DEFAULT_LIGHT)


def get_theme_names() -> list[str]:
    """Get list of all available theme names."""
    return list(THEMES.keys())


def get_persona_color(theme: ThemeConfig, persona: str) -> str:
    """Get persona-specific color from theme."""
    persona_map = {
        "high_utilization": theme.colors.persona_high_util,
        "variable_income": theme.colors.persona_variable_income,
        "subscription_heavy": theme.colors.persona_subscription,
        "savings_builder": theme.colors.persona_savings,
        "general": theme.colors.persona_general,
    }
    return persona_map.get(persona, theme.colors.persona_general)

"""
Theme configuration for SpendSense Reflex UI.

Defines color palette, typography, spacing, and other design tokens
aligned with persona-based visual identity.
"""

# =============================================================================
# COLOR PALETTE
# =============================================================================

# Persona Colors
PERSONA_COLORS = {
    "high_utilization": "#FF6B6B",      # Coral/red - urgent attention
    "variable_income": "#4ECDC4",       # Teal - stability focus
    "subscription_heavy": "#95E1D3",    # Mint - optimization
    "savings_builder": "#38B6FF",       # Blue - growth
    "general": "#A8DADC",               # Gray-blue - neutral
}

# Primary Palette
PRIMARY = "#38B6FF"          # Blue - primary actions
PRIMARY_DARK = "#2A9BDF"     # Darker blue for hover states
PRIMARY_LIGHT = "#E6F7FF"    # Light blue for backgrounds

# Semantic Colors
SUCCESS = "#10B981"          # Green - success, consent granted
SUCCESS_LIGHT = "#D1FAE5"    # Light green background
WARNING = "#F59E0B"          # Orange - attention needed
WARNING_LIGHT = "#FEF3C7"    # Light orange background
DANGER = "#EF4444"           # Red - urgent/error
DANGER_LIGHT = "#FEE2E2"     # Light red background
INFO = "#3B82F6"             # Blue - informational
INFO_LIGHT = "#DBEAFE"       # Light blue background

# Neutral Grays
GRAY_50 = "#F9FAFB"          # Lightest gray - page backgrounds
GRAY_100 = "#F3F4F6"         # Very light gray - card backgrounds
GRAY_200 = "#E5E7EB"         # Light gray - borders
GRAY_300 = "#D1D5DB"         # Medium-light gray - dividers
GRAY_400 = "#9CA3AF"         # Medium gray - placeholder text
GRAY_500 = "#6B7280"         # Mid gray - secondary text
GRAY_600 = "#4B5563"         # Dark-medium gray - body text
GRAY_700 = "#374151"         # Dark gray - emphasis text
GRAY_800 = "#1F2937"         # Darker gray - headings
GRAY_900 = "#111827"         # Darkest gray - primary text
WHITE = "#FFFFFF"            # Pure white
BLACK = "#000000"            # Pure black

# =============================================================================
# TYPOGRAPHY
# =============================================================================

# Font Families
FONT_FAMILY_SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif"
FONT_FAMILY_MONO = "JetBrains Mono, 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace"

# Font Sizes (rem units)
FONT_SIZE_XS = "0.75rem"     # 12px
FONT_SIZE_SM = "0.875rem"    # 14px
FONT_SIZE_BASE = "1rem"      # 16px
FONT_SIZE_LG = "1.125rem"    # 18px
FONT_SIZE_XL = "1.25rem"     # 20px
FONT_SIZE_2XL = "1.5rem"     # 24px
FONT_SIZE_3XL = "1.875rem"   # 30px
FONT_SIZE_4XL = "2.25rem"    # 36px
FONT_SIZE_5XL = "3rem"       # 48px

# Font Weights
FONT_WEIGHT_NORMAL = "400"
FONT_WEIGHT_MEDIUM = "500"
FONT_WEIGHT_SEMIBOLD = "600"
FONT_WEIGHT_BOLD = "700"

# Line Heights
LINE_HEIGHT_TIGHT = "1.25"
LINE_HEIGHT_NORMAL = "1.5"
LINE_HEIGHT_RELAXED = "1.75"

# =============================================================================
# SPACING
# =============================================================================

# Base unit: 4px
# Scale: multiply base unit by scale value

SPACE_0 = "0"
SPACE_1 = "0.25rem"      # 4px
SPACE_2 = "0.5rem"       # 8px
SPACE_3 = "0.75rem"      # 12px
SPACE_4 = "1rem"         # 16px
SPACE_5 = "1.25rem"      # 20px
SPACE_6 = "1.5rem"       # 24px
SPACE_8 = "2rem"         # 32px
SPACE_10 = "2.5rem"      # 40px
SPACE_12 = "3rem"        # 48px
SPACE_16 = "4rem"        # 64px
SPACE_20 = "5rem"        # 80px

# =============================================================================
# BORDERS
# =============================================================================

# Border Radius
BORDER_RADIUS_SM = "0.25rem"     # 4px
BORDER_RADIUS_BASE = "0.5rem"    # 8px
BORDER_RADIUS_MD = "0.75rem"     # 12px
BORDER_RADIUS_LG = "1rem"        # 16px
BORDER_RADIUS_XL = "1.5rem"      # 24px
BORDER_RADIUS_FULL = "9999px"    # Fully rounded

# Border Widths
BORDER_WIDTH_0 = "0"
BORDER_WIDTH_1 = "1px"
BORDER_WIDTH_2 = "2px"
BORDER_WIDTH_4 = "4px"

# =============================================================================
# SHADOWS
# =============================================================================

SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
SHADOW_BASE = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)"
SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
SHADOW_2XL = "0 25px 50px -12px rgba(0, 0, 0, 0.25)"

# =============================================================================
# BREAKPOINTS (for responsive design)
# =============================================================================

BREAKPOINT_SM = "640px"      # Mobile landscape
BREAKPOINT_MD = "768px"      # Tablet
BREAKPOINT_LG = "1024px"     # Desktop
BREAKPOINT_XL = "1280px"     # Large desktop
BREAKPOINT_2XL = "1536px"    # Extra large desktop

# =============================================================================
# COMPONENT-SPECIFIC STYLES
# =============================================================================

# Cards
CARD_STYLES = {
    "padding": SPACE_5,
    "border_radius": BORDER_RADIUS_MD,
    "background": WHITE,
    "border": f"{BORDER_WIDTH_1} solid {GRAY_200}",
    "box_shadow": SHADOW_BASE,
}

CARD_HOVER_STYLES = {
    "box_shadow": SHADOW_MD,
    "transform": "translateY(-2px)",
    "transition": "all 0.2s ease-in-out",
}

# Buttons
BUTTON_PRIMARY_STYLES = {
    "background": PRIMARY,
    "color": WHITE,
    "padding": f"{SPACE_3} {SPACE_6}",
    "border_radius": BORDER_RADIUS_BASE,
    "font_weight": FONT_WEIGHT_SEMIBOLD,
    "border": "none",
    "cursor": "pointer",
}

BUTTON_SECONDARY_STYLES = {
    "background": WHITE,
    "color": GRAY_700,
    "padding": f"{SPACE_3} {SPACE_6}",
    "border_radius": BORDER_RADIUS_BASE,
    "font_weight": FONT_WEIGHT_SEMIBOLD,
    "border": f"{BORDER_WIDTH_1} solid {GRAY_300}",
    "cursor": "pointer",
}

# Badges
BADGE_STYLES = {
    "display": "inline-flex",
    "padding": f"{SPACE_1} {SPACE_3}",
    "border_radius": BORDER_RADIUS_FULL,
    "font_size": FONT_SIZE_XS,
    "font_weight": FONT_WEIGHT_MEDIUM,
}

# Metric Cards
METRIC_CARD_STYLES = {
    **CARD_STYLES,
    "padding": SPACE_4,
    "text_align": "center",
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_persona_color(persona: str) -> str:
    """Get the color associated with a persona."""
    return PERSONA_COLORS.get(persona, PERSONA_COLORS["general"])


def get_status_color(is_active: bool) -> str:
    """Get color for active/inactive status."""
    return SUCCESS if is_active else GRAY_400


def get_alert_colors(type: str) -> tuple[str, str]:
    """Get background and text colors for alert types.

    Args:
        type: One of 'success', 'warning', 'danger', 'info'

    Returns:
        Tuple of (background_color, text_color)
    """
    colors = {
        "success": (SUCCESS_LIGHT, SUCCESS),
        "warning": (WARNING_LIGHT, WARNING),
        "danger": (DANGER_LIGHT, DANGER),
        "info": (INFO_LIGHT, INFO),
    }
    return colors.get(type, colors["info"])

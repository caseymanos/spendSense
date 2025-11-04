# SpendSense Reflex Implementation Guide

## Quick Start

### What You Have Now

The foundation for the Reflex UI migration is complete:

```
ui_reflex/
├── state/
│   ├── __init__.py                 ✅ State module exports
│   └── user_state.py               ✅ Complete state management (220 lines)
├── components/
│   └── shared/
│       ├── metric_card.py          ✅ Metric display component
│       ├── persona_badge.py        ✅ Persona visual indicator
│       └── status_badge.py         ✅ Status/category badges
├── utils/
│   ├── theme.py                    ✅ Complete theme system (250 lines)
│   ├── formatters.py               ✅ Data formatting utilities
│   └── data_loaders.py             ✅ Backend integration wrappers
└── README.md                       ✅ Comprehensive documentation
```

### Next Steps (15 minutes)

1. **Initialize Reflex** (2 min)
```bash
cd ui_reflex
reflex init  # Creates rxconfig.py and .web/ folder
```

2. **Create Main App File** (5 min)

Create `ui_reflex/user_app.py`:

```python
"""SpendSense User Dashboard - Reflex Implementation"""

import reflex as rx
from state.user_state import UserAppState
from components.shared.metric_card import metric_card
from components.shared.persona_badge import persona_badge
from components.shared.status_badge import consent_badge
from utils.formatters import format_currency, format_percentage
from utils import theme


def navbar() -> rx.Component:
    """Top navigation bar."""
    return rx.box(
        rx.hstack(
            # Logo and title
            rx.heading("💰 SpendSense", size="lg", color=theme.PRIMARY),

            rx.spacer(),

            # Navigation buttons
            rx.button(
                "Dashboard",
                on_click=UserAppState.navigate_to_dashboard,
                variant="ghost",
                color_scheme="blue",
            ),
            rx.button(
                "Learning Feed",
                on_click=UserAppState.navigate_to_learning_feed,
                variant="ghost",
                color_scheme="blue",
            ),
            rx.button(
                "Privacy",
                on_click=UserAppState.navigate_to_privacy,
                variant="ghost",
                color_scheme="blue",
            ),

            # User info
            rx.hstack(
                rx.text(UserAppState.user_name, font_weight="500"),
                consent_badge(UserAppState.consent_granted),
                spacing="3",
            ),

            spacing="4",
            width="100%",
        ),
        padding="4",
        background=theme.WHITE,
        border_bottom=f"1px solid {theme.GRAY_200}",
        position="sticky",
        top="0",
        z_index="100",
    )


def user_selector() -> rx.Component:
    """User selection dropdown."""
    return rx.select(
        UserAppState.all_users.map(lambda user: user["user_id"]),
        value=UserAppState.selected_user_id,
        on_change=UserAppState.select_user,
        placeholder="Select a user...",
    )


def simple_dashboard() -> rx.Component:
    """Simplified dashboard page to get started."""
    return rx.box(
        navbar(),

        rx.container(
            # User selector
            rx.vstack(
                rx.heading("Select User", size="md"),
                user_selector(),
                spacing="2",
                align_items="flex-start",
                margin_bottom="8",
            ),

            # Loading state
            rx.cond(
                UserAppState.is_loading,
                rx.spinner(size="xl"),

                # Content (when not loading)
                rx.cond(
                    UserAppState.consent_granted,

                    # Dashboard content (consent granted)
                    rx.vstack(
                        # Persona section
                        rx.box(
                            persona_badge(
                                UserAppState.persona_info,
                                show_description=True,
                                size="lg",
                            ),
                            margin_bottom="6",
                        ),

                        # Metrics grid (simple example)
                        rx.heading("Your Financial Snapshot", size="lg", margin_bottom="4"),
                        rx.grid(
                            metric_card(
                                label="Credit Cards",
                                value=rx.cond(
                                    UserAppState.signals.get("credit_num_cards"),
                                    str(UserAppState.signals["credit_num_cards"]),
                                    "0",
                                ),
                                help_text="Active accounts",
                                color=theme.PERSONA_COLORS["high_utilization"],
                            ),
                            metric_card(
                                label="Subscriptions",
                                value=rx.cond(
                                    UserAppState.signals.get("sub_180d_recurring_count"),
                                    str(UserAppState.signals["sub_180d_recurring_count"]),
                                    "0",
                                ),
                                help_text="Recurring services",
                                color=theme.PERSONA_COLORS["subscription_heavy"],
                            ),
                            metric_card(
                                label="Savings (6mo)",
                                value=rx.cond(
                                    UserAppState.signals.get("sav_180d_net_inflow"),
                                    format_currency(UserAppState.signals["sav_180d_net_inflow"]),
                                    "$0.00",
                                ),
                                help_text="Net inflow",
                                color=theme.PERSONA_COLORS["savings_builder"],
                            ),
                            columns="3",
                            spacing="4",
                        ),

                        # Recommendations preview
                        rx.heading("Your Recommendations", size="lg", margin_top="8", margin_bottom="4"),
                        rx.cond(
                            UserAppState.has_recommendations,
                            rx.vstack(
                                rx.foreach(
                                    UserAppState.top_recommendations,
                                    lambda rec: rx.box(
                                        rx.heading(rec["title"], size="md"),
                                        rx.text(rec["description"]),
                                        rx.box(
                                            rx.text(rec["rationale"], font_style="italic"),
                                            padding="3",
                                            background=theme.INFO_LIGHT,
                                            border_radius="md",
                                            margin_top="2",
                                        ),
                                        padding="5",
                                        border=f"1px solid {theme.GRAY_200}",
                                        border_radius="lg",
                                        margin_bottom="3",
                                    ),
                                ),
                                spacing="3",
                            ),
                            rx.text("No recommendations available", color=theme.GRAY_500),
                        ),

                        spacing="4",
                        width="100%",
                    ),

                    # Consent banner (no consent)
                    rx.box(
                        rx.heading("Consent Required", size="lg", margin_bottom="4"),
                        rx.text(
                            "To provide personalized insights, we need your consent to analyze your data.",
                            margin_bottom="4",
                        ),
                        rx.button(
                            "Grant Consent",
                            on_click=UserAppState.grant_consent_confirmed,
                            color_scheme="blue",
                            size="lg",
                        ),
                        padding="8",
                        background=theme.WARNING_LIGHT,
                        border=f"2px solid {theme.WARNING}",
                        border_radius="lg",
                    ),
                ),
            ),

            padding="8",
            max_width="1200px",
        ),
    )


def index() -> rx.Component:
    """Main app entry point."""
    return simple_dashboard()


# Create app
app = rx.App()

# Add main page with data loading on mount
app.add_page(
    index,
    route="/",
    title="SpendSense - Your Financial Dashboard",
    on_load=UserAppState.on_load,
)
```

3. **Run the App** (1 min)
```bash
reflex run
```

Visit `http://localhost:3000` 🎉

### What This Gives You

✅ **Working UI** with:
- User selection dropdown
- Persona display with color coding
- 3 metric cards showing real data
- Recommendations display
- Consent flow
- Loading states
- Clean, modern design

✅ **Full State Management**:
- Automatic data loading
- Consent grant/revoke
- Page navigation ready
- Error handling

✅ **Backend Integration**:
- Reads from existing SQLite database
- Loads Parquet files for signals
- Generates recommendations via existing engine
- Preserves all guardrails and trace logging

### Iteration Strategy

**Phase 1 (Done Above)**: Simple dashboard with basic components

**Phase 2**: Add remaining layout
```bash
# Create navbar component file
# Create sidebar component file
# Create page routing
```

**Phase 3**: Build full dashboard components
```bash
# Consent banner with full educational content
# Persona section with criteria expansion
# Full metrics grid (4 columns, all signals)
# Recommendations preview with cards
```

**Phase 4**: Learning feed page
```bash
# Education card component
# Partner offer card component
# Feed layout with sections
```

**Phase 5**: Privacy page
```bash
# Consent controls with modals
# Privacy information accordions
# Data export section
```

**Phase 6**: Polish
```bash
# Responsive breakpoints
# Animations and transitions
# Accessibility features
# Error boundaries
# Loading skeletons
```

## Component Examples

### Using Metric Card

```python
from components.shared.metric_card import metric_card
from utils import theme

# Simple metric
metric_card(
    label="Credit Utilization",
    value="68%",
    help_text="Average across all cards",
    color=theme.WARNING,
)

# With icon
metric_card(
    label="Emergency Fund",
    value="3.2 months",
    help_text="Months of expenses covered",
    color=theme.SUCCESS,
    icon="💰",
)

# Loading state
from components.shared.metric_card import metric_card_skeleton
rx.cond(
    is_loading,
    metric_card_skeleton(),
    metric_card(...),
)
```

### Using Persona Badge

```python
from components.shared.persona_badge import persona_badge, persona_section_with_criteria
from utils.data_loaders import get_persona_description

# Simple badge
persona_info = get_persona_description("high_utilization")
persona_badge(persona_info, show_description=True, size="lg")

# With criteria (expandable)
persona_section_with_criteria(
    persona_info=persona_info,
    criteria_met=[
        "Credit utilization at 68%",
        "Carrying interest on 2 cards",
    ],
)

# Inline variant
from components.shared.persona_badge import persona_badge_inline
persona_badge_inline(persona_info)
```

### Using Status Badges

```python
from components.shared.status_badge import (
    consent_badge,
    category_badge,
    alert_badge,
)

# Consent status
consent_badge(consent_granted=True)

# Category tag
category_badge("credit", color="#FF6B6B")

# Alert
alert_badge("Action required", alert_type="warning")
```

## Styling Examples

### Layout Patterns

```python
# Card with hover effect
rx.box(
    content,
    padding=theme.SPACE_5,
    border_radius=theme.BORDER_RADIUS_MD,
    background=theme.WHITE,
    border=f"1px solid {theme.GRAY_200}",
    box_shadow=theme.SHADOW_BASE,
    _hover={
        "box_shadow": theme.SHADOW_MD,
        "transform": "translateY(-2px)",
        "transition": "all 0.2s ease-in-out",
    },
)

# Grid layout
rx.grid(
    item1,
    item2,
    item3,
    item4,
    columns="4",
    spacing=theme.SPACE_4,
)

# Stack with spacing
rx.vstack(
    item1,
    item2,
    item3,
    spacing=theme.SPACE_4,
    align_items="flex-start",
    width="100%",
)
```

### Conditional Rendering

```python
# Simple condition
rx.cond(
    condition,
    when_true_component,
    when_false_component,
)

# Multiple conditions
rx.cond(
    UserAppState.is_loading,
    rx.spinner(),
    rx.cond(
        UserAppState.consent_granted,
        dashboard_content(),
        consent_banner(),
    ),
)

# With foreach
rx.foreach(
    UserAppState.recommendations_data["recommendations"],
    lambda rec: recommendation_card(rec),
)
```

## Debugging Tips

### State Not Updating?
```python
# Make sure event handlers are marked with @rx.event
@rx.event
def my_handler(self):
    self.my_var = new_value  # This triggers re-render
```

### Data Not Loading?
```python
# Check paths are correct (relative to project root)
DB_PATH = Path("data/users.sqlite")  # Not ui_reflex/data/

# Check data exists
from utils.data_loaders import get_database_stats
stats = get_database_stats()
print(stats)  # Should show user_count > 0
```

### Component Not Rendering?
```python
# Always return rx.Component
def my_component() -> rx.Component:
    return rx.box(...)  # Not just a string or dict

# Conditional must have both branches
rx.cond(
    condition,
    rx.box("True"),   # Must be component
    rx.box("False"),  # Must be component
)
```

## Performance Tips

1. **Cache Computed Vars**
```python
@rx.var(cache=True)
def expensive_computation(self) -> str:
    return complex_calculation()
```

2. **Lazy Load Data**
```python
@rx.event
def load_recommendations_only_when_needed(self):
    if not self.recommendations_data:
        self.recommendations_data = get_recommendations(...)
```

3. **Use Skeleton Loaders**
```python
rx.cond(
    is_loading,
    skeleton_component(),
    actual_component(),
)
```

## Next: Build Your First Feature

Pick one:

1. **Consent Banner** (easiest)
   - Create `components/dashboard/consent_banner.py`
   - Use existing `UserAppState.grant_consent_confirmed()`
   - Style with theme colors

2. **Metrics Grid** (medium)
   - Create `components/dashboard/metrics_grid.py`
   - Use `metric_card` component you have
   - Pull from `UserAppState.signals`

3. **Recommendation Cards** (advanced)
   - Create `components/dashboard/recommendation_card.py`
   - Map over `UserAppState.recommendations_data`
   - Add expand/collapse functionality

Happy building! 🚀

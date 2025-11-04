# SpendSense Reflex User Interface

Beautiful, modern user interface for SpendSense financial behavior analysis, built with Reflex.

## What's Been Completed

### Phase 1: Foundation ✅

1. **Project Structure** ✅
   - Created `ui_reflex/` directory with complete folder structure
   - Organized components, state, utils, and assets

2. **Theme System** ✅ (`utils/theme.py`)
   - Persona-based color palette
   - Typography system (Inter/System UI)
   - Spacing scale (4px base unit)
   - Border radius, shadows, and component styles
   - Utility functions for color selection

3. **Backend Integration** ✅ (`utils/data_loaders.py`)
   - Wrappers for existing backend modules
   - Functions for loading users, personas, signals, recommendations
   - Consent management integration
   - Trace logging preserved
   - No changes to existing backend code

4. **State Management** ✅ (`state/user_state.py`)
   - `UserAppState` class with all required state variables
   - Event handlers for navigation, user selection, data loading
   - Consent grant/revoke events with confirmation modals
   - Computed properties for derived data

5. **Formatting Utilities** ✅ (`utils/formatters.py`)
   - Currency formatting
   - Percentage formatting
   - Account number masking
   - Duration formatting
   - Text truncation and pluralization

### Phase 2: Shared Components ✅

1. **Metric Card** ✅ (`components/shared/metric_card.py`)
   - Display financial metrics with label, value, help text
   - Icon support
   - Hover effects
   - Loading skeleton variant

2. **Persona Badge** ✅ (`components/shared/persona_badge.py`)
   - Visual persona indicator with icon and color
   - Multiple size variants (sm, md, lg)
   - Expandable criteria section
   - Inline compact variant

3. **Status Badge** ✅ (`components/shared/status_badge.py`)
   - Consent status indicators
   - Category badges for recommendations
   - Alert badges (success, warning, danger, info)
   - Icon support

## What Needs to Be Completed

### Phase 2: Layout Components (Remaining)

**Next Steps:**
1. Create `components/layout/navbar.py` - Top navigation bar
2. Create `components/layout/sidebar.py` - User selector sidebar

### Phase 3: Dashboard Page Components

1. Create `components/dashboard/consent_banner.py`
2. Create `components/dashboard/persona_section.py`
3. Create `components/dashboard/metrics_grid.py`
4. Create `components/dashboard/recommendations_preview.py`
5. Assemble in main `user_app.py`

### Phase 4: Learning Feed Page

1. Create `components/learning_feed/education_card.py`
2. Create `components/learning_feed/offer_card.py`
3. Assemble learning feed page

### Phase 5: Privacy Settings Page

1. Create `components/privacy/consent_controls.py`
2. Create `components/privacy/privacy_info.py`
3. Assemble privacy page

### Phase 6: Polish & Testing

1. Responsive design and mobile support
2. Animations and interactions
3. Accessibility (ARIA, keyboard navigation)
4. Performance optimization
5. Error handling and loading states

## How to Continue Development

### Step 1: Initialize Reflex Project

```bash
cd ui_reflex
reflex init
```

This will create `rxconfig.py` and other Reflex-specific files.

### Step 2: Create Main App File

Create `ui_reflex/user_app.py` with basic structure:

```python
import reflex as rx
from state.user_state import UserAppState

# Import components as you create them
# from components.layout.navbar import navbar
# from components.dashboard.dashboard_page import dashboard_page
# etc.

def index() -> rx.Component:
    """Main entry point."""
    return rx.box(
        rx.heading("SpendSense", size="lg"),
        rx.text("User Dashboard - Coming Soon"),
    )

app = rx.App()
app.add_page(index, on_load=UserAppState.on_load)
```

### Step 3: Install Dependencies

Add to `requirements.txt` or install directly:

```bash
pip install reflex pandas pyarrow sqlite3
```

### Step 4: Build Layout Components

Start with the navbar and sidebar:

```python
# components/layout/navbar.py
import reflex as rx
from state.user_state import UserAppState

def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.heading("💰 SpendSense"),
            rx.spacer(),
            # Navigation buttons
            rx.button("Dashboard", on_click=UserAppState.navigate_to_dashboard),
            rx.button("Learning Feed", on_click=UserAppState.navigate_to_learning_feed),
            rx.button("Privacy", on_click=UserAppState.navigate_to_privacy),
        ),
        # Add styling from theme
    )
```

### Step 5: Build Dashboard Components

Follow the component structure in the plan. Use the shared components you've already created.

Example metrics grid:

```python
# components/dashboard/metrics_grid.py
import reflex as rx
from components.shared.metric_card import metric_card
from state.user_state import UserAppState
from utils.formatters import format_currency, format_percentage

def metrics_grid() -> rx.Component:
    return rx.grid(
        # Credit column
        metric_card(
            label="Credit Cards",
            value=UserAppState.signals.get("credit_num_cards", 0),
            help_text="Number of credit card accounts",
        ),
        # Add more metrics...
        columns="4",
        spacing="4",
    )
```

### Step 6: Run the Application

```bash
cd ui_reflex
reflex run
```

The app will be available at `http://localhost:3000`

## Architecture Highlights

### State Management Flow

```
User Action → Event Handler → Backend Wrapper → Database/Files
                ↓
         Update State Variables
                ↓
         UI Re-renders Automatically
```

### Data Loading Pattern

```python
@rx.event
def load_user_data_event(self):
    # Load from backend
    self.user_data = load_user_data(self.selected_user_id)
    self.persona_data = load_persona_assignment(self.selected_user_id)
    # ... etc

    # UI automatically updates because state changed
```

### Component Composition

```python
def dashboard_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.cond(
            UserAppState.consent_granted,
            # Show full dashboard
            rx.vstack(
                persona_section(),
                metrics_grid(),
                recommendations_preview(),
            ),
            # Show consent banner
            consent_banner(),
        ),
    )
```

## Design Guidelines

### Colors

- Use `theme.PERSONA_COLORS` for persona-specific elements
- Use `theme.SUCCESS`, `theme.WARNING`, `theme.DANGER` for status
- Use `theme.GRAY_*` scale for text and backgrounds

### Typography

- Headings: `font_weight=theme.FONT_WEIGHT_BOLD`
- Body text: `font_size=theme.FONT_SIZE_BASE`
- Small text: `font_size=theme.FONT_SIZE_SM`

### Spacing

- Use `theme.SPACE_*` constants consistently
- Common: `spacing=theme.SPACE_4` (16px)
- Tight: `spacing=theme.SPACE_2` (8px)

### Components

- Always wrap in `rx.box()` or `rx.vstack()` for styling
- Use `padding`, `border_radius`, `box_shadow` from theme
- Add hover states with `_hover` prop

## Testing with Existing Data

The backend integration is complete, so you can test with the existing synthetic data:

```bash
# Generate data (if not already done)
uv run python -m ingest.data_generator

# Run Reflex app
cd ui_reflex
reflex run

# In another terminal, keep Streamlit running for comparison
uv run streamlit run ui/app_user.py
```

## Migration Strategy

1. **Parallel Development**: Keep Streamlit app running while building Reflex
2. **Component-by-Component**: Build one component at a time, test thoroughly
3. **Compare UIs**: Use Streamlit version as reference for functionality
4. **Gradual Rollout**: Test with users before deprecating Streamlit

## Benefits of This Architecture

1. **No Backend Changes**: All existing logic, tests, and guardrails work as-is
2. **Separation of Concerns**: UI, state, and business logic cleanly separated
3. **Reusable Components**: Shared components used across pages
4. **Type Safety**: Python types throughout the stack
5. **Modern Design**: Theme system ensures consistent, beautiful UI

## Next Steps

1. Continue with layout components (navbar, sidebar)
2. Build dashboard page components
3. Implement learning feed and privacy pages
4. Add animations, responsiveness, and accessibility
5. Test thoroughly with real user workflows
6. Deploy alongside Streamlit for gradual migration

## Questions or Issues?

Refer to:
- Reflex documentation: https://reflex.dev/docs
- Existing Streamlit code in `ui/app_user.py` for feature reference
- Theme system in `utils/theme.py` for styling
- State management in `state/user_state.py` for data flow

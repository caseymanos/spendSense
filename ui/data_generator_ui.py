"""
Enhanced Data Generator UI for SpendSense Operator Dashboard.
Production-level interface with Tailwind and Shad-CN styling via NiceGUI.
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from nicegui import ui, app

from ingest.schemas import DataGenerationConfig
from ingest.operator_controls import (
    OperatorControls,
    PersonaTarget,
    PRESET_CONFIGS,
)


class DataGeneratorUI:
    """
    Production-level data generator UI with granular controls.

    Features:
    - Persona selection and targeting with multi-select
    - Granular behavioral pattern controls
    - Live preview of configuration
    - Preset configurations for common scenarios
    - Validation and error handling
    - Tailwind/Shad-CN inspired styling
    """

    def __init__(self):
        self.config = DataGenerationConfig()
        self.controls = OperatorControls()
        self.selected_personas: set = set()

        # UI state
        self.config_preview = None
        self.preset_preview = None
        self.generation_status = None
        self.preset_selector = None

        # Reactive values - Basic Config
        self.seed_value = 42
        self.users_value = 100
        self.months_value = 6
        self.trans_value = 30

        # Reactive values - Behavioral Controls
        # Credit
        self.overdue_slider = None
        self.min_pay_slider = None

        # Subscriptions
        self.sub_adoption_slider = None
        self.sub_count_min = None
        self.sub_count_max = None

        # Savings
        self.sav_adoption_slider = None
        self.sav_growth_slider = None

        # Income
        self.weekly_slider = None
        self.biweekly_slider = None
        self.monthly_slider = None
        self.irregular_slider = None
        self.volatility_slider = None

        # Current preset for comparison
        self.current_preset_key = None
        self.current_preset_config = None

    def render(self):
        """Render the complete data generator UI"""
        with ui.column().classes("w-full gap-6 p-6"):
            self._render_header()
            self._render_preset_selector()

            with ui.row().classes("w-full gap-6"):
                # Left column: Configuration controls
                with ui.column().classes("flex-1 gap-4"):
                    self._render_basic_config()
                    self._render_persona_selector()
                    self._render_behavioral_controls()

                # Right column: Preview and actions
                with ui.column().classes("flex-1 gap-4"):
                    self._render_preview()
                    self._render_actions()
                    self._render_status()

        # Initial preview update after all components are rendered
        self._update_preview()

    def _render_header(self):
        """Render section header"""
        with ui.card().classes("w-full bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-indigo-500"):
            with ui.card_section():
                with ui.row().classes("items-center gap-3"):
                    ui.icon("science", size="2rem").classes("text-indigo-600")
                    with ui.column().classes("gap-1"):
                        ui.label("Data Generator").classes("text-2xl font-bold text-gray-800")
                        ui.label("Configure and generate synthetic transaction data with persona targeting").classes("text-sm text-gray-600")

    def _render_preset_selector(self):
        """Render preset configuration selector"""
        with ui.card().classes("w-full shadow-sm"):
            with ui.card_section():
                ui.label("Quick Start Presets").classes("text-lg font-semibold mb-2")
                ui.label("Load pre-configured settings for common testing scenarios").classes("text-sm text-gray-600 mb-3")

                # NiceGUI expects option mapping: actual value -> display label
                preset_options = {
                    "default": "Default (Natural Distribution)",
                    "high_utilization_focus": "High Utilization Focus",
                    "variable_income_focus": "Variable Income Focus",
                    "subscription_heavy_focus": "Subscription Heavy Focus",
                    "savings_builder_focus": "Savings Builder Focus",
                    "overlap_testing": "Overlap Testing (Multi-Persona)",
                }

                with ui.row().classes("w-full gap-2 items-center"):
                    self.preset_selector = ui.select(
                        options=preset_options,
                        label="Select Preset",
                        value="default",
                    ).classes("flex-1").props("outlined dense")

                    ui.button(
                        "Load Preset",
                        icon="download",
                        on_click=self._load_preset
                    ).props("flat color=primary")

    def _render_basic_config(self):
        """Render basic configuration controls"""
        with ui.card().classes("w-full shadow-sm"):
            with ui.card_section():
                ui.label("Basic Configuration").classes("text-lg font-semibold mb-3")

                # Seed
                with ui.row().classes("w-full items-center gap-3 mb-4"):
                    ui.label("Random Seed").classes("w-32 font-medium")
                    seed_slider = ui.slider(
                        min=1, max=9999, value=42, step=1
                    ).classes("flex-1").props("label-always")
                    seed_input = ui.number(
                        value=42, min=1, max=9999
                    ).classes("w-24").props("outlined dense")
                    seed_slider.bind_value(seed_input, "value")
                    self.seed_value = seed_slider

                # Number of users
                with ui.row().classes("w-full items-center gap-3 mb-4"):
                    ui.label("Users").classes("w-32 font-medium")
                    users_slider = ui.slider(
                        min=10, max=1000, value=100, step=10
                    ).classes("flex-1").props("label-always")
                    users_input = ui.number(
                        value=100, min=10, max=1000
                    ).classes("w-24").props("outlined dense")
                    users_slider.bind_value(users_input, "value")
                    self.users_value = users_slider

                # Months history
                with ui.row().classes("w-full items-center gap-3 mb-4"):
                    ui.label("History (months)").classes("w-32 font-medium")
                    months_slider = ui.slider(
                        min=1, max=24, value=6, step=1
                    ).classes("flex-1").props("label-always")
                    months_input = ui.number(
                        value=6, min=1, max=24
                    ).classes("w-24").props("outlined dense")
                    months_slider.bind_value(months_input, "value")
                    self.months_value = months_slider

                # Avg transactions per month
                with ui.row().classes("w-full items-center gap-3"):
                    ui.label("Trans/Month").classes("w-32 font-medium")
                    trans_slider = ui.slider(
                        min=10, max=100, value=30, step=5
                    ).classes("flex-1").props("label-always")
                    trans_input = ui.number(
                        value=30, min=10, max=100
                    ).classes("w-24").props("outlined dense")
                    trans_slider.bind_value(trans_input, "value")
                    self.trans_value = trans_slider

    def _render_persona_selector(self):
        """Render persona targeting controls"""
        with ui.card().classes("w-full shadow-sm border-l-4 border-purple-500"):
            with ui.card_section():
                with ui.row().classes("items-center gap-2 mb-2"):
                    ui.icon("psychology", size="1.5rem").classes("text-purple-600")
                    ui.label("Persona Targeting").classes("text-lg font-semibold")

                ui.label("Select one or more personas to skew data generation. Leave empty for natural distribution.").classes("text-sm text-gray-600 mb-3")

                # Persona checkboxes with descriptions
                persona_descriptions = {
                    "high_utilization": "Credit utilization ≥50%, interest charges, overdue payments",
                    "variable_income": "Irregular income patterns, unstable cash flow",
                    "subscription_heavy": "3+ recurring subscriptions, significant monthly spend",
                    "savings_builder": "Regular savings transfers, low credit utilization",
                    "general": "No specific behavioral patterns (baseline)",
                }

                with ui.column().classes("w-full gap-2"):
                    for persona in PersonaTarget:
                        with ui.row().classes("items-start gap-2 p-2 hover:bg-gray-50 rounded"):
                            checkbox = ui.checkbox(persona.value.replace("_", " ").title())
                            checkbox.on_value_change(lambda e, p=persona: self._toggle_persona(p, e.value))
                            with ui.column().classes("gap-0 flex-1"):
                                ui.label(persona_descriptions[persona.value]).classes("text-xs text-gray-600")

                # Persona weights (shown when multiple selected)
                self.persona_weights_container = ui.column().classes("w-full gap-2 mt-3")
                self._update_persona_weights_ui()

    def _render_behavioral_controls(self):
        """Render detailed behavioral pattern controls"""
        with ui.expansion("Advanced Behavioral Controls", icon="tune").classes("w-full shadow-sm").props("dense"):
            with ui.column().classes("w-full gap-4 p-4"):

                # Credit Behavior
                with ui.card().classes("bg-red-50"):
                    with ui.card_section():
                        ui.label("Credit Behavior").classes("font-semibold text-red-800 mb-2")

                        with ui.row().classes("w-full items-center gap-2 mb-2"):
                            ui.label("Overdue Probability").classes("w-48 text-sm")
                            self.overdue_slider = ui.slider(
                                min=0, max=1, value=0.15, step=0.05
                            ).classes("flex-1").props("label-always")
                            self.overdue_slider.on_value_change(self._update_preview)

                        with ui.row().classes("w-full items-center gap-2"):
                            ui.label("Min Payment Only").classes("w-48 text-sm")
                            self.min_pay_slider = ui.slider(
                                min=0, max=1, value=0.25, step=0.05
                            ).classes("flex-1").props("label-always")
                            self.min_pay_slider.on_value_change(self._update_preview)

                # Subscription Behavior
                with ui.card().classes("bg-blue-50"):
                    with ui.card_section():
                        ui.label("Subscription Patterns").classes("font-semibold text-blue-800 mb-2")

                        with ui.row().classes("w-full items-center gap-2 mb-2"):
                            ui.label("Adoption Rate").classes("w-48 text-sm")
                            self.sub_adoption_slider = ui.slider(
                                min=0, max=1, value=0.50, step=0.05
                            ).classes("flex-1").props("label-always")
                            self.sub_adoption_slider.on_value_change(self._update_preview)

                        with ui.row().classes("w-full items-center gap-2 mb-2"):
                            ui.label("Count Range").classes("w-48 text-sm")
                            self.sub_count_min = ui.number(value=3, min=1, max=10).classes("w-20").props("outlined dense")
                            self.sub_count_min.on_value_change(self._update_preview)
                            ui.label("to").classes("text-sm")
                            self.sub_count_max = ui.number(value=6, min=1, max=15).classes("w-20").props("outlined dense")
                            self.sub_count_max.on_value_change(self._update_preview)

                # Savings Behavior
                with ui.card().classes("bg-green-50"):
                    with ui.card_section():
                        ui.label("Savings Patterns").classes("font-semibold text-green-800 mb-2")

                        with ui.row().classes("w-full items-center gap-2 mb-2"):
                            ui.label("Adoption Rate").classes("w-48 text-sm")
                            self.sav_adoption_slider = ui.slider(
                                min=0, max=1, value=0.40, step=0.05
                            ).classes("flex-1").props("label-always")
                            self.sav_adoption_slider.on_value_change(self._update_preview)

                        with ui.row().classes("w-full items-center gap-2"):
                            ui.label("Growth Target %").classes("w-48 text-sm")
                            self.sav_growth_slider = ui.slider(
                                min=0, max=20, value=5, step=0.5
                            ).classes("flex-1").props("label-always")
                            self.sav_growth_slider.on_value_change(self._update_preview)

                # Income Patterns
                with ui.card().classes("bg-yellow-50"):
                    with ui.card_section():
                        ui.label("Income Patterns").classes("font-semibold text-yellow-800 mb-2")

                        ui.label("Payroll Distribution").classes("text-sm mb-2")
                        with ui.column().classes("w-full gap-2"):
                            with ui.row().classes("w-full items-center gap-2"):
                                ui.label("Weekly").classes("w-32 text-sm")
                                self.weekly_slider = ui.slider(min=0, max=1, value=0.15, step=0.05).classes("flex-1").props("label-always")
                                self.weekly_slider.on_value_change(self._update_preview)
                            with ui.row().classes("w-full items-center gap-2"):
                                ui.label("Biweekly").classes("w-32 text-sm")
                                self.biweekly_slider = ui.slider(min=0, max=1, value=0.30, step=0.05).classes("flex-1").props("label-always")
                                self.biweekly_slider.on_value_change(self._update_preview)
                            with ui.row().classes("w-full items-center gap-2"):
                                ui.label("Monthly").classes("w-32 text-sm")
                                self.monthly_slider = ui.slider(min=0, max=1, value=0.25, step=0.05).classes("flex-1").props("label-always")
                                self.monthly_slider.on_value_change(self._update_preview)
                            with ui.row().classes("w-full items-center gap-2"):
                                ui.label("Irregular").classes("w-32 text-sm")
                                self.irregular_slider = ui.slider(min=0, max=1, value=0.30, step=0.05).classes("flex-1").props("label-always")
                                self.irregular_slider.on_value_change(self._update_preview)

                        with ui.row().classes("w-full items-center gap-2 mt-2"):
                            ui.label("Income Volatility").classes("w-48 text-sm")
                            self.volatility_slider = ui.slider(min=0, max=1, value=0.5, step=0.05).classes("flex-1").props("label-always")
                            self.volatility_slider.on_value_change(self._update_preview)

    def _render_preview(self):
        """Render side-by-side configuration comparison"""
        with ui.card().classes("w-full shadow-md border-2 border-indigo-200"):
            with ui.card_section():
                with ui.row().classes("items-center gap-2 mb-3"):
                    ui.icon("compare_arrows", size="1.5rem").classes("text-indigo-600")
                    ui.label("Configuration Comparison").classes("text-lg font-semibold")

                with ui.row().classes("w-full gap-4"):
                    # Left panel: Current configuration
                    with ui.column().classes("flex-1"):
                        with ui.card().classes("bg-green-50 h-full"):
                            with ui.card_section():
                                with ui.row().classes("items-center gap-2 mb-2"):
                                    ui.icon("settings", size="1.2rem").classes("text-green-700")
                                    ui.label("Current Configuration").classes("font-semibold text-green-800")

                                self.config_preview = ui.json_editor({
                                    "Generation Settings": {},
                                    "Persona Targeting": {},
                                    "Behavioral Controls": {}
                                }).props("mode=view readonly").classes("w-full text-xs")

                    # Right panel: Preset configuration (or placeholder)
                    with ui.column().classes("flex-1"):
                        with ui.card().classes("bg-blue-50 h-full"):
                            with ui.card_section():
                                with ui.row().classes("items-center gap-2 mb-2"):
                                    ui.icon("bookmarks", size="1.2rem").classes("text-blue-700")
                                    ui.label("Preset Configuration").classes("font-semibold text-blue-800")

                                self.preset_preview = ui.json_editor({
                                    "status": "No preset selected",
                                    "tip": "Select and load a preset to see differences here"
                                }).props("mode=view readonly").classes("w-full text-xs")

                # Validation status
                self.validation_status = ui.label("").classes("text-sm mt-2")

                # Bind updates
                if hasattr(self, 'seed_value'):
                    self.seed_value.on_value_change(self._update_preview)
                if hasattr(self, 'users_value'):
                    self.users_value.on_value_change(self._update_preview)
                if hasattr(self, 'months_value'):
                    self.months_value.on_value_change(self._update_preview)
                if hasattr(self, 'trans_value'):
                    self.trans_value.on_value_change(self._update_preview)

    def _render_actions(self):
        """Render action buttons"""
        with ui.card().classes("w-full shadow-sm bg-gradient-to-r from-indigo-50 to-purple-50"):
            with ui.card_section():
                ui.label("Actions").classes("text-lg font-semibold mb-3")

                with ui.column().classes("w-full gap-2"):
                    ui.button(
                        "Generate Data",
                        icon="play_arrow",
                        on_click=self._generate_data
                    ).props("color=primary size=lg").classes("w-full")

                    with ui.row().classes("w-full gap-2"):
                        ui.button(
                            "Validate Config",
                            icon="check_circle",
                            on_click=self._validate_config
                        ).props("flat color=positive").classes("flex-1")

                        ui.button(
                            "Export Config",
                            icon="download",
                            on_click=self._export_config
                        ).props("flat color=info").classes("flex-1")

                    with ui.row().classes("w-full gap-2"):
                        ui.button(
                            "Reset to Defaults",
                            icon="refresh",
                            on_click=self._reset_defaults
                        ).props("flat").classes("flex-1")

                        ui.button(
                            "Load from File",
                            icon="upload",
                            on_click=self._load_from_file
                        ).props("flat").classes("flex-1")

    def _render_status(self):
        """Render generation status"""
        self.generation_status = ui.card().classes("w-full shadow-sm")
        with self.generation_status:
            with ui.card_section():
                ui.label("Generation Status").classes("text-lg font-semibold mb-2")
                self.status_label = ui.label("Ready to generate").classes("text-sm text-gray-600")
                self.status_progress = ui.linear_progress(value=0).classes("hidden")

    # =============================================================================
    # HELPER METHODS
    # =============================================================================

    def _get_current_behavioral_config(self) -> OperatorControls:
        """Build OperatorControls from current UI state"""
        # Get values with safety checks
        def safe_value(slider, default):
            return slider.value if slider and hasattr(slider, 'value') else default

        # Build payroll distribution
        payroll_dist = {
            "weekly": safe_value(self.weekly_slider, 0.15),
            "biweekly": safe_value(self.biweekly_slider, 0.30),
            "monthly": safe_value(self.monthly_slider, 0.25),
            "irregular": safe_value(self.irregular_slider, 0.30),
        }

        # Normalize payroll distribution to sum to 1.0
        payroll_total = sum(payroll_dist.values())
        if payroll_total > 0:
            payroll_dist = {k: v / payroll_total for k, v in payroll_dist.items()}

        return OperatorControls(
            target_personas=list(self.selected_personas),
            payroll_pattern_distribution=payroll_dist,
            irregular_income_volatility=safe_value(self.volatility_slider, 0.5),
            overdue_probability=safe_value(self.overdue_slider, 0.15),
            min_payment_only_probability=safe_value(self.min_pay_slider, 0.25),
            subscription_adoption_rate=safe_value(self.sub_adoption_slider, 0.50),
            subscription_count_min=int(safe_value(self.sub_count_min, 3)),
            subscription_count_max=int(safe_value(self.sub_count_max, 6)),
            savings_adoption_rate=safe_value(self.sav_adoption_slider, 0.40),
            savings_growth_target_pct=safe_value(self.sav_growth_slider, 5.0),
        )

    def _toggle_persona(self, persona: PersonaTarget, checked: bool):
        """Handle persona checkbox toggle"""
        if checked:
            self.selected_personas.add(persona)
        else:
            self.selected_personas.discard(persona)

        self._update_persona_weights_ui()
        self._update_preview()

    def _update_persona_weights_ui(self):
        """Update persona weights sliders based on selection"""
        self.persona_weights_container.clear()

        if len(self.selected_personas) > 1:
            with self.persona_weights_container:
                ui.label("Persona Weights (must sum to 1.0)").classes("text-sm font-medium mb-2")
                for persona in self.selected_personas:
                    with ui.row().classes("w-full items-center gap-2"):
                        ui.label(persona.value.replace("_", " ").title()).classes("w-48 text-sm")
                        ui.slider(
                            min=0, max=1, value=1.0/len(self.selected_personas), step=0.05
                        ).classes("flex-1").props("label-always")

    def _update_preview(self):
        """Update side-by-side configuration preview with validation"""
        if not self.config_preview:
            return

        # Get basic config values
        seed = int(self.seed_value.value) if hasattr(self.seed_value, 'value') else 42
        users = int(self.users_value.value) if hasattr(self.users_value, 'value') else 100
        months = int(self.months_value.value) if hasattr(self.months_value, 'value') else 6
        trans = int(self.trans_value.value) if hasattr(self.trans_value, 'value') else 30

        estimated = users * months * trans

        # Get current behavioral configuration
        current_controls = self._get_current_behavioral_config()

        # Build current configuration display
        current_config = {
            "Generation Settings": {
                "seed": seed,
                "num_users": users,
                "months_history": months,
                "avg_transactions_per_month": trans,
                "estimated_transactions": estimated,
                "estimated_accounts": users * 3,
            }
        }

        # Add behavioral controls using to_display_dict()
        current_config.update(current_controls.to_display_dict())

        # Update current config panel
        self.config_preview.set_value(current_config)

        # Validate and show status
        validation_messages = []

        # Validate payroll distribution
        payroll_sum = sum(current_controls.payroll_pattern_distribution.values())
        if not (0.99 <= payroll_sum <= 1.01):
            validation_messages.append(f"⚠️  Payroll distribution sums to {payroll_sum:.2f} (should be 1.0)")

        # Update validation status
        if validation_messages:
            self.validation_status.set_text(" | ".join(validation_messages))
            self.validation_status.classes("text-orange-600 font-semibold")
        else:
            self.validation_status.set_text("✓ Configuration is valid")
            self.validation_status.classes("text-green-600 font-semibold")

        # Update preset panel if a preset is selected
        if self.current_preset_config:
            preset_config = {
                "Generation Settings": {
                    "seed": seed,  # Same as current
                    "num_users": users,
                    "months_history": months,
                    "avg_transactions_per_month": trans,
                    "estimated_transactions": estimated,
                    "estimated_accounts": users * 3,
                }
            }
            # Add preset behavioral controls
            preset_config.update(self.current_preset_config.to_display_dict())
            self.preset_preview.set_value(preset_config)
        else:
            # No preset selected - show placeholder
            self.preset_preview.set_value({
                "status": "No preset selected",
                "tip": "Select a preset above and click 'Load Preset' to see comparison"
            })

    async def _generate_data(self):
        """Generate synthetic data with current configuration"""
        self.status_label.set_text("Starting generation...")
        self.status_progress.classes(remove="hidden")
        self.status_progress.set_value(0.1)

        try:
            # Build config
            config = DataGenerationConfig(
                seed=int(self.seed_value.value),
                num_users=int(self.users_value.value),
                months_history=int(self.months_value.value),
                avg_transactions_per_month=int(self.trans_value.value),
                generation_timestamp=datetime.now()
            )

            # Build controls from current UI state
            controls = self._get_current_behavioral_config()

            # Save to config file
            config_path = Path("data/operator_config.json")
            config_path.parent.mkdir(exist_ok=True)

            config_data = {
                "config": config.model_dump(mode="json"),
                "controls": controls.model_dump(mode="json")
            }

            with open(config_path, "w") as f:
                json.dump(config_data, f, indent=2, default=str)

            self.status_label.set_text("Running generator...")
            self.status_progress.set_value(0.3)

            # Run generator (will be implemented next)
            process = await asyncio.create_subprocess_exec(
                "uv", "run", "python", "-m", "ingest.persona_skewed_generator",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            self.status_progress.set_value(1.0)

            if process.returncode == 0:
                self.status_label.set_text(f"✓ Generation complete! {stdout.decode()}")
                ui.notify("Data generation successful!", type="positive")
            else:
                error_msg = stderr.decode() or "Unknown error"
                self.status_label.set_text(f"✗ Generation failed: {error_msg}")
                ui.notify(f"Generation failed: {error_msg}", type="negative")

        except Exception as e:
            self.status_label.set_text(f"✗ Error: {str(e)}")
            ui.notify(f"Error: {str(e)}", type="negative")
        finally:
            self.status_progress.classes(add="hidden")

    def _validate_config(self):
        """Validate current configuration"""
        try:
            config = DataGenerationConfig(
                seed=int(self.seed_value.value),
                num_users=int(self.users_value.value),
                months_history=int(self.months_value.value),
                avg_transactions_per_month=int(self.trans_value.value),
            )
            controls = self._get_current_behavioral_config()
            ui.notify("✓ Configuration is valid!", type="positive")
        except Exception as e:
            ui.notify(f"✗ Invalid configuration: {str(e)}", type="negative")

    def _export_config(self):
        """Export current configuration to file"""
        try:
            config = DataGenerationConfig(
                seed=int(self.seed_value.value),
                num_users=int(self.users_value.value),
                months_history=int(self.months_value.value),
                avg_transactions_per_month=int(self.trans_value.value),
            )
            controls = self._get_current_behavioral_config()

            export_path = Path("data/exported_config.json")
            export_path.parent.mkdir(exist_ok=True)

            config_data = {
                "config": config.model_dump(mode="json"),
                "controls": controls.model_dump(mode="json"),
                "exported_at": datetime.now().isoformat()
            }

            with open(export_path, "w") as f:
                json.dump(config_data, f, indent=2, default=str)

            ui.notify(f"✓ Configuration exported to {export_path}", type="positive")
        except Exception as e:
            ui.notify(f"✗ Export failed: {str(e)}", type="negative")

    def _reset_defaults(self):
        """Reset all controls to default values"""
        self.seed_value.set_value(42)
        self.users_value.set_value(100)
        self.months_value.set_value(6)
        self.trans_value.set_value(30)
        self.selected_personas.clear()
        self._update_persona_weights_ui()
        self._update_preview()
        ui.notify("Reset to defaults", type="info")

    def _load_from_file(self):
        """Load configuration from saved file"""
        try:
            config_path = Path("data/operator_config.json")
            if not config_path.exists():
                ui.notify("No saved configuration found", type="warning")
                return

            with open(config_path) as f:
                data = json.load(f)

            config_data = data.get("config", {})
            self.seed_value.set_value(config_data.get("seed", 42))
            self.users_value.set_value(config_data.get("num_users", 100))
            self.months_value.set_value(config_data.get("months_history", 6))
            self.trans_value.set_value(config_data.get("avg_transactions_per_month", 30))

            # Load persona targets
            controls_data = data.get("controls", {})
            persona_list = controls_data.get("target_personas", [])
            self.selected_personas = {PersonaTarget(p) for p in persona_list}

            self._update_persona_weights_ui()
            self._update_preview()
            ui.notify("Configuration loaded", type="positive")
        except Exception as e:
            ui.notify(f"Load failed: {str(e)}", type="negative")

    def _load_preset(self):
        """Load a preset configuration and show comparison"""
        preset_key = self.preset_selector.value
        if preset_key not in PRESET_CONFIGS:
            ui.notify("Invalid preset selected", type="warning")
            return

        preset = PRESET_CONFIGS[preset_key]

        # Store preset for comparison
        self.current_preset_key = preset_key
        self.current_preset_config = preset

        # Update persona selection
        self.selected_personas = set(preset.target_personas)
        self._update_persona_weights_ui()

        # Update behavioral controls from preset
        if self.overdue_slider:
            self.overdue_slider.set_value(preset.overdue_probability)
        if self.min_pay_slider:
            self.min_pay_slider.set_value(preset.min_payment_only_probability)

        if self.sub_adoption_slider:
            self.sub_adoption_slider.set_value(preset.subscription_adoption_rate)
        if self.sub_count_min:
            self.sub_count_min.set_value(preset.subscription_count_min)
        if self.sub_count_max:
            self.sub_count_max.set_value(preset.subscription_count_max)

        if self.sav_adoption_slider:
            self.sav_adoption_slider.set_value(preset.savings_adoption_rate)
        if self.sav_growth_slider:
            self.sav_growth_slider.set_value(preset.savings_growth_target_pct)

        # Update payroll distribution sliders
        payroll_dist = preset.payroll_pattern_distribution
        if self.weekly_slider:
            self.weekly_slider.set_value(payroll_dist.get("weekly", 0.15))
        if self.biweekly_slider:
            self.biweekly_slider.set_value(payroll_dist.get("biweekly", 0.30))
        if self.monthly_slider:
            self.monthly_slider.set_value(payroll_dist.get("monthly", 0.25))
        if self.irregular_slider:
            self.irregular_slider.set_value(payroll_dist.get("irregular", 0.30))

        if self.volatility_slider:
            self.volatility_slider.set_value(preset.irregular_income_volatility)

        # Update preview to show comparison
        self._update_preview()

        ui.notify(f"✓ Loaded preset: {preset_key.replace('_', ' ').title()}", type="positive")

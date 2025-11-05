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
        self.current_config_container = None
        self.preset_comparison_container = None
        self.preset_info_label = None
        self.generation_status = None
        self.preset_selector = None
        self.validation_status = None

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
        ui.query("body").style("background-color: #f8fafc")

        with ui.column().classes("w-full max-w-[1600px] mx-auto gap-6 p-6").style("min-height: 100vh"):
            self._render_header()
            self._render_preset_selector()

            with ui.row().classes("w-full gap-6 flex-wrap xl:flex-nowrap items-start"):
                # Left column: Configuration controls
                with ui.column().classes("w-full xl:w-7/12 gap-4"):
                    self._render_basic_config()
                    self._render_persona_selector()
                    self._render_behavioral_controls()

                # Right column: Preview and actions
                with ui.column().classes("w-full xl:w-5/12 gap-4").style(
                    "position: sticky; top: 1rem; align-self: flex-start;"
                ):
                    self._render_actions()
                    self._render_preview()
                    self._render_status()

        # Initial preview update after all components are rendered
        self._update_preview()

    def _render_header(self):
        """Render section header"""
        with ui.card().classes("w-full rounded-none shadow-sm").style(
            "background: linear-gradient(135deg, #334155 0%, #1e293b 100%); border: none; border-bottom: 1px solid rgba(255,255,255,0.1)"
        ):
            with ui.card_section().classes("py-5"):
                with ui.row().classes("items-center justify-between gap-4"):
                    with ui.row().classes("items-center gap-3"):
                        ui.icon("group", size="2rem").classes("text-white").style(
                            "background: rgba(34, 197, 94, 0.1); padding: 8px; border-radius: 8px"
                        )
                        with ui.column().classes("gap-0"):
                            ui.label("SpendSense Operator Dashboard").classes("text-white text-xl font-semibold")
                            ui.label("Compliance & Oversight Interface").classes("text-white/70 text-sm")

                    ui.input(placeholder="Operator Name").classes("max-w-xs").props("dark outlined dense").style(
                        "background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.2)"
                    )

    def _render_preset_selector(self):
        """Render preset configuration selector"""
        with ui.card().classes("w-full shadow-sm").style("border: 1px solid #e2e8f0"):
            with ui.card_section().classes("py-4"):
                with ui.row().classes("items-center gap-2 mb-1"):
                    ui.icon("flash_auto", size="1.2rem").classes("text-indigo-500")
                    ui.label("Quick Start Presets").classes("text-lg font-semibold text-slate-800")
                ui.label("Load pre-configured settings for common testing scenarios.").classes(
                    "text-sm text-slate-500 mb-4"
                )

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
                    ).classes("flex-1").props("outlined dense").style("border-color: #c7d2fe")

                    ui.button(
                        "Load Preset",
                        icon="download",
                        on_click=self._load_preset
                    ).props("flat color=primary").classes("px-4")

    def _render_basic_config(self):
        """Render basic configuration controls"""
        with ui.card().classes("w-full shadow-sm").style("border: 1px solid #e2e8f0"):
            with ui.card_section().classes("space-y-4"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("settings", size="1.2rem").classes("text-slate-600")
                    ui.label("Basic Configuration").classes("text-lg font-semibold text-slate-800")
                ui.label("Core generation parameters that set dataset scale.").classes(
                    "text-sm text-slate-500"
                )

                def slider_with_input(
                    label: str,
                    slider_kwargs: Dict[str, Any],
                    number_kwargs: Dict[str, Any],
                ):
                    with ui.column().classes("w-full gap-2"):
                        with ui.row().classes("items-center justify-between gap-3"):
                            ui.label(label).classes("font-medium text-slate-700")
                            number = ui.number(**number_kwargs).classes("w-24").props("outlined dense")
                        slider = ui.slider(**slider_kwargs).classes("w-full").props(
                            "color=primary label-always"
                        )
                        slider.bind_value(number, "value")
                    return slider

                self.seed_value = slider_with_input(
                    "Random Seed",
                    {"min": 1, "max": 9999, "value": 42, "step": 1},
                    {"value": 42, "min": 1, "max": 9999},
                )

                self.users_value = slider_with_input(
                    "Users",
                    {"min": 10, "max": 1000, "value": 100, "step": 10},
                    {"value": 100, "min": 10, "max": 1000},
                )

                self.months_value = slider_with_input(
                    "History (months)",
                    {"min": 1, "max": 24, "value": 6, "step": 1},
                    {"value": 6, "min": 1, "max": 24},
                )

                self.trans_value = slider_with_input(
                    "Trans/Month",
                    {"min": 10, "max": 100, "value": 30, "step": 5},
                    {"value": 30, "min": 10, "max": 100},
                )

    def _render_persona_selector(self):
        """Render persona targeting controls"""
        with ui.card().classes("w-full shadow-sm").style("border: 1px solid #e2e8f0; border-left: 4px solid #a855f7"):
            with ui.card_section().classes("space-y-4"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("psychology", size="1.4rem").classes("text-purple-600")
                    ui.label("Persona Targeting").classes("text-lg font-semibold text-slate-800")

                ui.label(
                    "Select one or more personas to skew data generation. Leave empty for natural distribution."
                ).classes("text-sm text-slate-500")

                # Persona checkboxes with descriptions
                persona_descriptions = {
                    "high_utilization": "Credit utilization ≥50%, interest charges, overdue payments",
                    "variable_income": "Irregular income patterns, unstable cash flow",
                    "subscription_heavy": "3+ recurring subscriptions, significant monthly spend",
                    "savings_builder": "Regular savings transfers, low credit utilization",
                    "general": "No specific behavioral patterns (baseline)",
                }

                with ui.column().classes("w-full gap-3"):
                    for persona in PersonaTarget:
                        with ui.row().classes("items-start gap-3 p-3 rounded-lg").style(
                            "border: 1px solid #e2e8f0; background: white;"
                        ):
                            checkbox = ui.checkbox(persona.value.replace("_", " ").title()).classes("mt-1")
                            checkbox.on_value_change(lambda e, p=persona: self._toggle_persona(p, e.value))
                            with ui.column().classes("gap-0 flex-1"):
                                ui.label(persona_descriptions[persona.value]).classes("text-sm text-slate-600")

                # Persona weights (shown when multiple selected)
                self.persona_weights_container = ui.column().classes("w-full gap-2 mt-2")
                self._update_persona_weights_ui()

    def _render_behavioral_controls(self):
        """Render detailed behavioral pattern controls"""
        with ui.expansion("Advanced Behavioral Controls", icon="tune").classes("w-full shadow-sm").props("dense"):
            with ui.column().classes("w-full gap-4 p-4"):

                # Credit Behavior
                with ui.card().classes("shadow-none").style("background: #fef2f2; border: 1px solid #fecaca"):
                    with ui.card_section().classes("space-y-3"):
                        ui.label("Credit Behavior").classes("font-semibold text-red-800")

                        ui.label("Overdue Probability").classes("text-sm text-gray-700")
                        self.overdue_slider = ui.slider(
                            min=0, max=1, value=0.15, step=0.05
                        ).classes("w-full").props("color=negative label-always")
                        self.overdue_slider.on_value_change(self._update_preview)

                        ui.label("Min Payment Only").classes("text-sm text-gray-700")
                        self.min_pay_slider = ui.slider(
                            min=0, max=1, value=0.25, step=0.05
                        ).classes("w-full").props("color=negative label-always")
                        self.min_pay_slider.on_value_change(self._update_preview)

                # Subscription Behavior
                with ui.card().classes("shadow-none").style("background: #eff6ff; border: 1px solid #bfdbfe"):
                    with ui.card_section().classes("space-y-3"):
                        ui.label("Subscription Patterns").classes("font-semibold text-blue-800")

                        ui.label("Adoption Rate").classes("text-sm text-gray-700")
                        self.sub_adoption_slider = ui.slider(
                            min=0, max=1, value=0.50, step=0.05
                        ).classes("w-full").props("color=primary label-always")
                        self.sub_adoption_slider.on_value_change(self._update_preview)

                        with ui.row().classes("w-full items-center gap-2"):
                            ui.label("Count Range").classes("text-sm text-gray-700 w-32")
                            self.sub_count_min = ui.number(value=3, min=1, max=10).classes("w-20").props("outlined dense")
                            self.sub_count_min.on_value_change(self._update_preview)
                            ui.label("to").classes("text-sm text-gray-600")
                            self.sub_count_max = ui.number(value=6, min=1, max=15).classes("w-20").props("outlined dense")
                            self.sub_count_max.on_value_change(self._update_preview)

                # Savings Behavior
                with ui.card().classes("shadow-none").style("background: #f0fdf4; border: 1px solid #bbf7d0"):
                    with ui.card_section().classes("space-y-3"):
                        ui.label("Savings Patterns").classes("font-semibold text-green-800")

                        ui.label("Adoption Rate").classes("text-sm text-gray-700")
                        self.sav_adoption_slider = ui.slider(
                            min=0, max=1, value=0.40, step=0.05
                        ).classes("w-full").props("color=positive label-always")
                        self.sav_adoption_slider.on_value_change(self._update_preview)

                        ui.label("Growth Target %").classes("text-sm text-gray-700")
                        self.sav_growth_slider = ui.slider(
                            min=0, max=20, value=5, step=0.5
                        ).classes("w-full").props("color=positive label-always")
                        self.sav_growth_slider.on_value_change(self._update_preview)

                # Income Patterns
                with ui.card().classes("shadow-none").style("background: #fffbeb; border: 1px solid #fde68a"):
                    with ui.card_section().classes("space-y-3"):
                        ui.label("Income Patterns").classes("font-semibold text-yellow-800")

                        ui.label("Payroll Distribution").classes("text-sm font-medium text-gray-700")
                        with ui.column().classes("w-full gap-2"):
                            for label_text, attr, default in [
                                ("Weekly", "weekly_slider", 0.15),
                                ("Biweekly", "biweekly_slider", 0.30),
                                ("Monthly", "monthly_slider", 0.25),
                                ("Irregular", "irregular_slider", 0.30),
                            ]:
                                ui.label(label_text).classes("text-xs text-gray-600")
                                slider = ui.slider(
                                    min=0, max=1, value=default, step=0.05
                                ).classes("w-full").props("color=warning label-always")
                                slider.on_value_change(self._update_preview)
                                setattr(self, attr, slider)

                        ui.label("Income Volatility").classes("text-sm text-gray-700")
                        self.volatility_slider = ui.slider(
                            min=0, max=1, value=0.5, step=0.05
                        ).classes("w-full").props("color=warning label-always")
                        self.volatility_slider.on_value_change(self._update_preview)

    def _render_preview(self):
        """Render the configuration summary and comparison layout."""
        with ui.card().classes("w-full shadow-md border border-indigo-200"):
            with ui.card_section().classes("space-y-4"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("compare_arrows", size="1.5rem").classes("text-indigo-600")
                    ui.label("Configuration Overview").classes("text-lg font-semibold")

                with ui.row().classes("w-full gap-4 flex-wrap xl:flex-nowrap items-stretch"):
                    with ui.card().classes("flex-1 shadow-sm h-full").style("min-width: 320px"):
                        with ui.card_section().classes("space-y-3"):
                            with ui.row().classes("items-center gap-2 mb-2"):
                                ui.icon("settings", size="1.2rem").classes("text-green-700")
                                ui.label("Current Configuration").classes("font-semibold text-green-800")
                            ui.label(
                                "Snapshot of the active generation settings and behavioral controls."
                            ).classes("text-xs text-gray-600")
                            self.current_config_container = ui.column().classes("w-full gap-3")

                    with ui.card().classes("flex-1 shadow-sm h-full").style("min-width: 320px"):
                        with ui.card_section().classes("space-y-3"):
                            with ui.row().classes("items-center gap-2 mb-2"):
                                ui.icon("bookmarks", size="1.2rem").classes("text-blue-700")
                                ui.label("Preset Comparison").classes("font-semibold text-blue-800")
                            self.preset_info_label = ui.label(
                                'Select a preset above and click "Load Preset" to compare settings.'
                            ).classes("text-xs text-gray-600 mb-2")
                            self.preset_comparison_container = ui.column().classes("w-full gap-3")

                self.validation_status = ui.label("").classes("text-sm")

                if hasattr(self, "seed_value"):
                    self.seed_value.on_value_change(self._update_preview)
                if hasattr(self, "users_value"):
                    self.users_value.on_value_change(self._update_preview)
                if hasattr(self, "months_value"):
                    self.months_value.on_value_change(self._update_preview)
                if hasattr(self, "trans_value"):
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
                ui.label("Persona Weights (must sum to 1.0)").classes(
                    "text-sm font-medium text-slate-700 mb-2"
                )
                for persona in self.selected_personas:
                    with ui.row().classes("w-full items-center gap-3 p-2 rounded-lg").style(
                        "background: #f8fafc; border: 1px dashed #cbd5f5"
                    ):
                        ui.label(persona.value.replace("_", " ").title()).classes(
                            "text-sm font-medium text-slate-700 w-48"
                        )
                        ui.slider(
                            min=0, max=1, value=1.0 / len(self.selected_personas), step=0.05
                        ).classes("flex-1").props("color=primary label-always")

    def _update_preview(self):
        """Update configuration summary and preset comparison"""
        if not self.current_config_container:
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

        self._populate_current_config(current_config)

        validation_messages = []

        payroll_sum = sum(current_controls.payroll_pattern_distribution.values())
        if not (0.99 <= payroll_sum <= 1.01):
            validation_messages.append(f"⚠️  Payroll distribution sums to {payroll_sum:.2f} (should be 1.0)")

        self._update_validation_status(validation_messages)
        self._update_preset_comparison(current_config)

    def _populate_current_config(self, config: Dict[str, Any]) -> None:
        """Render the current configuration snapshot."""
        self.current_config_container.clear()
        with self.current_config_container:
            generation_settings = config.get("Generation Settings", {})
            if generation_settings:
                with ui.row().classes("w-full gap-3 flex-wrap"):
                    self._render_stat_chip(
                        "Users",
                        f"{generation_settings.get('num_users', 0):,}",
                        "group",
                    )
                    self._render_stat_chip(
                        "History (months)",
                        generation_settings.get("months_history", 0),
                        "calendar_month",
                    )
                    self._render_stat_chip(
                        "Est. Transactions",
                        f"{generation_settings.get('estimated_transactions', 0):,}",
                        "data_thresholding",
                    )

            sections = {k: v for k, v in config.items() if k != "Generation Settings"}
            if sections:
                self._render_sections(sections, collapsed=True)

    def _update_validation_status(self, messages: list[str]) -> None:
        """Show validation state below the configuration overview."""
        if not self.validation_status:
            return

        self.validation_status.classes(remove="text-green-600 text-orange-600 font-semibold")
        if messages:
            self.validation_status.set_text(" | ".join(messages))
            self.validation_status.classes(add="text-orange-600 font-semibold")
        else:
            self.validation_status.set_text("✓ Configuration is valid")
            self.validation_status.classes(add="text-green-600 font-semibold")

    def _update_preset_comparison(self, current_config: Dict[str, Any]) -> None:
        """Render comparison details for the selected preset."""
        if not self.preset_comparison_container:
            return

        default_message = 'Select a preset above and click "Load Preset" to compare settings.'
        if not self.current_preset_config:
            self.preset_comparison_container.clear()
            if self.preset_info_label:
                self.preset_info_label.set_text(default_message)
                self.preset_info_label.classes(remove="text-blue-700 font-semibold")
                self.preset_info_label.classes(add="text-gray-600")
            return

        preset_display = self.current_preset_config.to_display_dict()
        differences = self._calculate_differences(current_config, preset_display)

        if self.preset_info_label:
            preset_name = self._format_preset_name(self.current_preset_key or "Preset")
            highlight = f"Comparing against preset: {preset_name}"
            if differences:
                highlight += f" • {len(differences)} difference(s) detected"
            self.preset_info_label.set_text(highlight)
            self.preset_info_label.classes(remove="text-gray-600")
            self.preset_info_label.classes(add="text-blue-700 font-semibold")

        self.preset_comparison_container.clear()
        with self.preset_comparison_container:
            if differences:
                columns = [
                    {"name": "metric", "label": "Metric", "field": "metric", "align": "left"},
                    {"name": "current", "label": "Current", "field": "current", "align": "left"},
                    {"name": "preset", "label": "Preset", "field": "preset", "align": "left"},
                ]
                ui.table(
                    row_key="id",
                    columns=columns,
                    rows=differences,
                ).props("dense flat hide-bottom").classes("w-full text-sm")
            else:
                with ui.row().classes("items-center gap-2"):
                    ui.icon("check_circle", size="1.1rem").classes("text-green-600")
                    ui.label("Current configuration already matches the loaded preset.").classes(
                        "text-sm text-green-700"
                    )

            with ui.expansion("Preset Details", icon="visibility").classes(
                "w-full bg-blue-50 border border-blue-100 rounded-lg mt-2"
            ):
                with ui.column().classes("w-full gap-2"):
                    self._render_sections(preset_display, collapsed=False)

    def _render_sections(self, sections: Dict[str, Any], *, collapsed: bool) -> None:
        """Render a collection of sections in a responsive grid."""
        with ui.grid(columns=1).classes("w-full gap-3 md:grid-cols-2 items-stretch"):
            for title, values in sections.items():
                self._render_section(title, values, collapsed=collapsed)

    def _render_section(self, title: str, values: Any, *, collapsed: bool) -> None:
        """Render a configuration section either as an expansion or static block."""
        label = self._humanize_label(title)
        icon = self._section_icon(label)

        if collapsed:
            with ui.expansion(label, value=True, icon=icon).classes(
                "bg-white border border-gray-200 rounded-lg shadow-sm h-full"
            ):
                with ui.column().classes("w-full gap-1 py-1"):
                    self._render_section_body(values)
        else:
            with ui.card().classes(
                "shadow-none border border-blue-100 bg-blue-50 h-full"
            ):
                with ui.card_section().classes("py-2"):
                    with ui.row().classes("items-center gap-2 mb-1"):
                        ui.icon(icon, size="1rem").classes("text-blue-600")
                        ui.label(label).classes("text-sm font-semibold text-blue-800")
                    with ui.column().classes("w-full gap-1"):
                        self._render_section_body(values, indent=False)

    def _render_section_body(self, values: Any, *, indent: bool = False) -> None:
        """Render rows for the contents of a section."""
        if isinstance(values, dict):
            for key, value in values.items():
                display_key = self._humanize_label(key)
                if isinstance(value, dict):
                    ui.label(display_key).classes("text-xs font-semibold text-gray-500 uppercase mt-2")
                    for sub_key, sub_value in value.items():
                        self._render_metric_row(self._humanize_label(sub_key), sub_value, indent=True)
                else:
                    self._render_metric_row(display_key, value, indent=indent)
        else:
            self._render_metric_row("Value", values, indent=indent)

    def _render_metric_row(self, label: str, value: Any, *, indent: bool = False) -> None:
        """Render a single key/value metric row."""
        label_classes = "text-sm text-gray-600"
        if indent:
            label_classes = "pl-4 " + label_classes

        with ui.row().classes("w-full items-start justify-between gap-2 py-1"):
            ui.label(label).classes(label_classes)
            ui.label(self._format_value(value)).classes(
                "text-sm font-medium text-gray-800 text-right whitespace-pre-wrap"
            )

    def _render_stat_chip(self, label: str, value: Any, icon: str) -> None:
        """Render a small stat card for headline metrics."""
        with ui.card().classes("w-full sm:flex-1 shadow-none border border-green-100 bg-green-50"):
            with ui.card_section().classes("py-2"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon(icon, size="1.2rem").classes("text-green-600")
                    ui.label(str(value)).classes("text-lg font-semibold text-green-700")
                ui.label(label).classes("text-xs text-green-700 mt-1")

    def _format_value(self, value: Any) -> str:
        """Format values for display."""
        if isinstance(value, float):
            if 0 <= value <= 1:
                return f"{value:.0%}"
            return f"{value:.2f}".rstrip("0").rstrip(".")
        if isinstance(value, int):
            return f"{value:,}"
        if isinstance(value, (list, tuple, set)):
            if not value:
                return "None"
            formatted = [
                self._humanize_label(getattr(item, "value", item))
                for item in value
            ]
            return ", ".join(formatted)
        if isinstance(value, dict):
            return ", ".join(
                f"{self._humanize_label(k)}: {self._format_value(v)}" for k, v in value.items()
            )
        if isinstance(value, str):
            if "_" in value and " " not in value and not value.startswith("$"):
                return self._humanize_label(value)
            return value
        return str(value)

    def _humanize_label(self, label: Any) -> str:
        """Convert snake_case identifiers into readable labels."""
        text = str(label)
        if "_" in text and not text.startswith("$"):
            return text.replace("_", " ").title()
        return text

    def _section_icon(self, title: str) -> str:
        """Icon mapping for configuration sections."""
        icons = {
            "Generation Settings": "tune",
            "Persona Targeting": "psychology",
            "Income Patterns": "savings",
            "Credit Behavior": "credit_score",
            "Subscriptions": "subscriptions",
            "Savings": "savings",
            "Spending": "shopping_cart",
            "Account Structure": "account_balance",
        }
        return icons.get(title, "tune")

    def _flatten_config(self, data: Dict[str, Any], prefix: str | None = None) -> Dict[str, Any]:
        """Flatten nested configuration data for comparison."""
        flat: Dict[str, Any] = {}
        for key, value in data.items():
            label = self._humanize_label(key)
            path = f"{prefix} > {label}" if prefix else label
            if isinstance(value, dict):
                flat.update(self._flatten_config(value, path))
            else:
                flat[path] = value
        return flat

    def _calculate_differences(
        self, current_config: Dict[str, Any], preset_display: Dict[str, Any]
    ) -> list[Dict[str, Any]]:
        """Calculate human-readable differences between current and preset configs."""
        current_flat = self._flatten_config(current_config)
        preset_flat = self._flatten_config(preset_display)

        differences: list[Dict[str, Any]] = []
        for idx, key in enumerate(sorted(preset_flat.keys())):
            preset_value = preset_flat[key]
            current_value = current_flat.get(key)
            if current_value is None:
                continue
            if not self._values_equal(current_value, preset_value):
                differences.append(
                    {
                        "id": idx,
                        "metric": key,
                        "current": self._format_value(current_value),
                        "preset": self._format_value(preset_value),
                    }
                )
        return differences

    def _values_equal(self, first: Any, second: Any) -> bool:
        """Equality helper with tolerance for floats and sequences."""
        if isinstance(first, float) and isinstance(second, float):
            return abs(first - second) < 1e-6
        if isinstance(first, (list, tuple)) and isinstance(second, (list, tuple)):
            return len(first) == len(second) and all(
                self._values_equal(x, y) for x, y in zip(first, second)
            )
        return first == second

    def _format_preset_name(self, key: str) -> str:
        """Format preset identifier into a readable name."""
        return key.replace("_", " ").title()

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

        preset = PRESET_CONFIGS[preset_key].model_copy(deep=True)

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

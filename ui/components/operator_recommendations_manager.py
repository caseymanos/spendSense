"""
Operator Recommendations Manager UI Component
Table-based bulk management interface for operator recommendations.
"""

import requests
import json
from nicegui import ui
from typing import Optional, Dict, Any, List


class OperatorRecommendationsManager:
    """Manager for operator-created and edited recommendations with table view."""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.table = None
        self.table_container = None
        self.selected_user_filter = "All Users"
        self.source_filter = "All"
        self.status_filter = "Active"
        self.all_recommendations = []

    def fetch_all_recommendations(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch recommendations for all users."""
        all_recs = []
        for user_id in user_ids:
            try:
                # Fetch from user endpoint (merged auto + operator)
                response = requests.get(f"{self.api_base_url}/recommendations/{user_id}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    for rec in data.get('recommendations', []):
                        rec['user_id'] = user_id
                        rec['persona'] = data.get('persona', 'Unknown')
                        all_recs.append(rec)
            except Exception as e:
                print(f"Error fetching recs for {user_id}: {e}")
        return all_recs

    def fetch_operator_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch operator recommendations for a specific user (including overridden for audit)."""
        try:
            response = requests.get(f"{self.api_base_url}/operator/recommendations/{user_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('recommendations', [])
        except Exception as e:
            print(f"Error fetching operator recs for {user_id}: {e}")
        return []

    def create_recommendation(self, rec_data: Dict[str, Any]) -> bool:
        """Create new operator recommendation via API."""
        try:
            response = requests.post(
                f"{self.api_base_url}/operator/recommendations",
                json=rec_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error creating recommendation: {e}")
            return False

    def update_recommendation(self, rec_id: str, rec_data: Dict[str, Any]) -> bool:
        """Update existing operator recommendation via API."""
        try:
            response = requests.put(
                f"{self.api_base_url}/operator/recommendations/{rec_id}",
                json=rec_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error updating recommendation: {e}")
            return False

    def delete_recommendation(self, rec_id: str, operator_name: str) -> bool:
        """Delete operator recommendation via API."""
        try:
            response = requests.delete(
                f"{self.api_base_url}/operator/recommendations/{rec_id}?operator_name={operator_name}",
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting recommendation: {e}")
            return False

    def filter_recommendations(self) -> List[Dict[str, Any]]:
        """Apply filters to recommendations."""
        filtered = []

        for rec in self.all_recommendations:
            # User filter
            if self.selected_user_filter != "All Users":
                if rec.get('user_id') != self.selected_user_filter:
                    continue

            # Source filter
            if self.source_filter != "All":
                source_map = {
                    "Auto-Generated": "auto_generated",
                    "Operator Created": "operator_created",
                    "Operator Override": "operator_override"
                }
                if rec.get('source') != source_map.get(self.source_filter):
                    continue

            # Status filter (for operator recs only)
            if self.status_filter != "All":
                rec_status = rec.get('status', 'active')
                if rec_status != self.status_filter.lower():
                    continue

            filtered.append(rec)

        return filtered

    def render_table(self):
        """Render recommendations table with filters and actions."""
        if not self.table_container:
            return

        self.table_container.clear()

        filtered_recs = self.filter_recommendations()

        with self.table_container:
            ui.label(f"Showing {len(filtered_recs)} recommendations").classes("text-sm text-gray-600 mb-2")

            if not filtered_recs:
                ui.label("No recommendations match filters").classes("text-gray-500 italic p-4")
                return

            # Prepare table data
            columns = [
                {"name": "user_id", "label": "User ID", "field": "user_id", "align": "left", "sortable": True},
                {"name": "title", "label": "Title", "field": "title", "align": "left", "sortable": True},
                {"name": "type", "label": "Type", "field": "type", "align": "center", "sortable": True},
                {"name": "source", "label": "Source", "field": "source", "align": "center", "sortable": True},
                {"name": "created_by", "label": "Created By", "field": "created_by", "align": "center"},
                {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
            ]

            rows = []
            for rec in filtered_recs:
                rows.append({
                    "user_id": rec.get('user_id', ''),
                    "title": rec.get('title', ''),
                    "type": rec.get('type', 'education'),
                    "source": rec.get('source', 'auto_generated'),
                    "created_by": rec.get('created_by', 'system'),
                    "recommendation_id": rec.get('recommendation_id', ''),
                    "rec_data": rec  # Store full rec for detail view
                })

            self.table = ui.table(
                columns=columns,
                rows=rows,
                row_key='recommendation_id',
                pagination={"rowsPerPage": 20, "sortBy": "user_id"}
            ).classes("w-full")

            # Add custom action buttons column
            self.table.add_slot('body-cell-actions', '''
                <q-td :props="props">
                    <q-btn size="sm" flat dense icon="visibility" color="blue">
                        <q-tooltip>View Details</q-tooltip>
                    </q-btn>
                    <q-btn size="sm" flat dense icon="edit" color="green" v-if="props.row.source !== 'auto_generated'">
                        <q-tooltip>Edit</q-tooltip>
                    </q-btn>
                    <q-btn size="sm" flat dense icon="content_copy" color="orange">
                        <q-tooltip>Create Override</q-tooltip>
                    </q-btn>
                    <q-btn size="sm" flat dense icon="delete" color="red" v-if="props.row.source !== 'auto_generated'">
                        <q-tooltip>Delete</q-tooltip>
                    </q-btn>
                </q-td>
            ''')

    def open_create_dialog(self, users_df):
        """Open dialog to create new operator recommendation."""
        with ui.dialog() as dialog, ui.card().classes("w-[800px] max-w-[90vw] max-h-[90vh] overflow-auto"):
            ui.label("Create New Recommendation").classes("text-xl font-bold mb-4")

            # Form fields
            user_id_select = ui.select(
                label="User",
                options=users_df["user_id"].tolist() if users_df is not None else [],
                value=users_df["user_id"].tolist()[0] if users_df is not None and not users_df.empty else None
            ).classes("w-full mb-2")

            title_input = ui.input("Title", placeholder="Enter recommendation title").classes("w-full mb-2")
            description_input = ui.textarea("Description", placeholder="Detailed description").classes("w-full mb-2").props("rows=3")

            with ui.row().classes("w-full gap-2 mb-2"):
                type_select = ui.select(
                    "Type",
                    options=["education", "partner_offer"],
                    value="education"
                ).classes("flex-1")
                category_input = ui.input("Category", placeholder="e.g., budgeting").classes("flex-1")
                topic_input = ui.input("Topic", placeholder="e.g., Emergency Fund").classes("flex-1")

            rationale_input = ui.textarea(
                "Rationale",
                placeholder="Because... (explain why this recommendation is relevant)"
            ).classes("w-full mb-2").props("rows=4")

            disclaimer_input = ui.textarea(
                "Disclaimer (optional)",
                placeholder="This is educational content, not financial advice."
            ).classes("w-full mb-2").props("rows=2")

            operator_name_input = ui.input(
                "Your Name",
                placeholder="Operator name",
                value="Operator"
            ).classes("w-full mb-4")

            # Action buttons
            with ui.row().classes("gap-2 justify-end w-full"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button(
                    "Create",
                    icon="save",
                    on_click=lambda: self._handle_create(
                        dialog,
                        user_id_select.value,
                        title_input.value,
                        description_input.value,
                        type_select.value,
                        category_input.value,
                        topic_input.value,
                        rationale_input.value,
                        operator_name_input.value,
                        disclaimer_input.value
                    )
                ).props("color=primary")

        dialog.open()

    def _handle_create(self, dialog, user_id, title, description, rec_type, category, topic, rationale, operator_name, disclaimer):
        """Handle create recommendation form submission."""
        if not user_id or not title or not rationale:
            ui.notify("Please fill in required fields (User, Title, Rationale)", type="negative")
            return

        rec_data = {
            "user_id": user_id,
            "type": rec_type,
            "title": title,
            "description": description or "",
            "category": category or "general",
            "topic": topic or "General",
            "rationale": rationale,
            "disclaimer": disclaimer or "This is educational content, not financial advice.",
            "operator_name": operator_name or "Operator"
        }

        if self.create_recommendation(rec_data):
            ui.notify("✓ Recommendation created successfully", type="positive")
            dialog.close()
            # Refresh table
            self.refresh_data()
        else:
            ui.notify("Failed to create recommendation", type="negative")

    def open_detail_dialog(self, rec):
        """Open read-only dialog showing full recommendation details."""
        with ui.dialog() as dialog, ui.card().classes("w-[800px] max-w-[90vw] max-h-[90vh] overflow-auto"):
            ui.label(rec.get('title', 'Recommendation Details')).classes("text-xl font-bold mb-4")

            # Display all fields read-only
            with ui.column().classes("gap-3 w-full"):
                self._detail_field("User ID", rec.get('user_id', 'N/A'))
                self._detail_field("Type", rec.get('type', 'N/A'))
                self._detail_field("Category", rec.get('category', 'N/A'))
                self._detail_field("Topic", rec.get('topic', 'N/A'))
                self._detail_field("Source", rec.get('source', 'auto_generated'))
                self._detail_field("Created By", rec.get('created_by', 'system'))

                ui.separator().classes("my-2")

                self._detail_field("Description", rec.get('description', 'N/A'), multiline=True)
                self._detail_field("Rationale", rec.get('rationale', 'N/A'), multiline=True)
                self._detail_field("Disclaimer", rec.get('disclaimer', 'N/A'), multiline=True, small=True)

            with ui.row().classes("gap-2 justify-end w-full mt-4"):
                ui.button("Close", on_click=dialog.close).props("color=primary")

        dialog.open()

    def _detail_field(self, label: str, value: str, multiline: bool = False, small: bool = False):
        """Render a detail field."""
        ui.label(label + ":").classes("font-bold text-sm text-gray-700")
        if multiline:
            text_classes = "text-sm mb-3 whitespace-pre-wrap" if not small else "text-xs text-gray-600 mb-3 whitespace-pre-wrap"
            ui.label(value).classes(text_classes)
        else:
            ui.label(value).classes("mb-3")

    def refresh_data(self):
        """Refresh recommendations data and re-render table."""
        # This will be called from parent to trigger refresh
        pass


def render_operator_recommendations_manager_ui(users_df, theme_manager):
    """Render the operator recommendations manager UI."""
    manager = OperatorRecommendationsManager()

    with ui.card().classes(theme_manager.get_card_classes() if theme_manager else ""):
        ui.label("Recommendation Management").classes("text-xl font-bold mb-4")

        # Filters row
        with ui.row().classes("w-full gap-4 mb-4"):
            user_filter = ui.select(
                label="Filter by User",
                options=["All Users"] + (users_df["user_id"].tolist() if users_df is not None and not users_df.empty else []),
                value="All Users"
            ).classes("w-64")

            source_filter = ui.select(
                label="Source",
                options=["All", "Auto-Generated", "Operator Created", "Operator Override"],
                value="All"
            ).classes("w-48")

        # Action buttons
        with ui.row().classes("gap-2 mb-4"):
            ui.button(
                "+ Create New",
                icon="add",
                on_click=lambda: manager.open_create_dialog(users_df)
            ).props("color=primary")

        # Table container
        table_container = ui.column().classes("w-full")

        # Bind manager to UI elements
        manager.table_container = table_container
        manager.selected_user_filter = user_filter.value
        manager.source_filter = source_filter.value

        def on_filter_change():
            manager.selected_user_filter = user_filter.value
            manager.source_filter = source_filter.value
            manager.render_table()

        user_filter.on_value_change(lambda: on_filter_change())
        source_filter.on_value_change(lambda: on_filter_change())

        # Initial load
        if users_df is not None and not users_df.empty:
            manager.all_recommendations = manager.fetch_all_recommendations(users_df["user_id"].tolist())
            manager.render_table()
        else:
            with table_container:
                ui.label("No users data available").classes("text-gray-500 p-4")

    return manager

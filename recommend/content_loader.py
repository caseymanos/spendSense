"""
Content Loader for Recommendation Engine

This module provides a hybrid content management system that:
1. Loads default content from content_catalog.py (developer-managed seed data)
2. Applies operator overrides from data/content_overrides.json (if exists)
3. Enables runtime editing without modifying Python code

Design Principles:
- Non-destructive: Never modifies content_catalog.py
- Version control friendly: Overrides stored separately as JSON
- Easy rollback: Delete overrides.json to reset to defaults
- Hot reload: Changes apply immediately without restart
"""

import json
import copy
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from recommend.content_catalog import (
    EDUCATIONAL_CONTENT,
    PARTNER_OFFERS,
)


# Path to operator overrides file
_PROJECT_ROOT = Path(__file__).parent.parent
OVERRIDES_PATH = _PROJECT_ROOT / "data" / "content_overrides.json"


def load_content_catalog() -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Load recommendation content catalog with operator overrides applied.

    Returns:
        Dictionary with structure:
        {
            "educational": {
                "high_utilization": [list of items],
                "variable_income": [list of items],
                ...
            },
            "offers": {
                "high_utilization": [list of items],
                "variable_income": [list of items],
                ...
            }
        }
    """
    # Start with base catalog from Python code
    catalog = {
        "educational": copy.deepcopy(EDUCATIONAL_CONTENT),
        "offers": copy.deepcopy(PARTNER_OFFERS),
    }

    # Apply overrides if they exist
    if OVERRIDES_PATH.exists():
        try:
            with open(OVERRIDES_PATH, "r") as f:
                overrides = json.load(f)

            # Merge overrides into catalog
            catalog = _apply_overrides(catalog, overrides)
        except (json.JSONDecodeError, IOError) as e:
            # If overrides file is corrupt, log and use defaults
            print(f"Warning: Could not load content overrides: {e}")
            print("Using default catalog from content_catalog.py")

    return catalog


def _apply_overrides(
    base_catalog: Dict[str, Any], overrides: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply operator overrides to base catalog.

    Override precedence:
    - Items with matching 'id' are replaced
    - Items with 'deleted': true are removed
    - Items without 'id' are added

    Args:
        base_catalog: Base content from content_catalog.py
        overrides: Operator modifications from JSON

    Returns:
        Merged catalog
    """
    result = copy.deepcopy(base_catalog)

    for content_type in ["educational", "offers"]:
        if content_type not in overrides:
            continue

        for persona, override_items in overrides[content_type].items():
            if persona not in result[content_type]:
                result[content_type][persona] = []

            # Build ID-indexed dict of base items
            base_items = result[content_type][persona]
            base_by_id = {
                _generate_id(item): item for item in base_items
            }

            # Apply overrides
            for override_item in override_items:
                item_id = override_item.get("id") or _generate_id(override_item)

                if override_item.get("deleted", False):
                    # Mark as deleted (remove from result)
                    base_by_id.pop(item_id, None)
                else:
                    # Add or update
                    base_by_id[item_id] = override_item

            # Rebuild list maintaining order
            result[content_type][persona] = list(base_by_id.values())

    return result


def _generate_id(item: Dict[str, Any]) -> str:
    """
    Generate unique ID for a content item based on title and topic.

    Args:
        item: Content item dictionary

    Returns:
        Unique identifier string
    """
    title = item.get("title", "").lower().replace(" ", "_")
    topic = item.get("topic", "")
    return f"{title}_{topic}" if topic else title


def save_override(
    content_type: str,
    persona: str,
    item: Dict[str, Any],
    deleted: bool = False,
) -> None:
    """
    Save a content override to the overrides file.

    Args:
        content_type: "educational" or "offers"
        persona: Persona key (high_utilization, etc.)
        item: Content item to save or delete
        deleted: If True, marks item as deleted
    """
    # Load existing overrides or create new structure
    overrides = {}
    if OVERRIDES_PATH.exists():
        with open(OVERRIDES_PATH, "r") as f:
            overrides = json.load(f)

    # Ensure structure exists
    if content_type not in overrides:
        overrides[content_type] = {}
    if persona not in overrides[content_type]:
        overrides[content_type][persona] = []

    # Add or update item
    item_id = item.get("id") or _generate_id(item)
    item["id"] = item_id  # Ensure ID is set

    if deleted:
        item["deleted"] = True

    # Find and replace existing override, or append
    override_list = overrides[content_type][persona]
    existing_idx = next(
        (i for i, x in enumerate(override_list) if x.get("id") == item_id),
        None
    )

    if existing_idx is not None:
        override_list[existing_idx] = item
    else:
        override_list.append(item)

    # Add metadata
    if "metadata" not in overrides:
        overrides["metadata"] = {}
    overrides["metadata"]["last_updated"] = datetime.now().isoformat()
    overrides["metadata"]["version"] = "1.0"

    # Save to file
    OVERRIDES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OVERRIDES_PATH, "w") as f:
        json.dump(overrides, f, indent=2)


def delete_override(content_type: str, persona: str, item_id: str) -> None:
    """
    Mark a content item as deleted in overrides.

    Args:
        content_type: "educational" or "offers"
        persona: Persona key
        item_id: ID of item to delete
    """
    if not OVERRIDES_PATH.exists():
        return

    with open(OVERRIDES_PATH, "r") as f:
        overrides = json.load(f)

    # Find the item and mark as deleted
    if content_type in overrides and persona in overrides[content_type]:
        for item in overrides[content_type][persona]:
            if item.get("id") == item_id:
                item["deleted"] = True
                break

    # Save
    overrides["metadata"] = overrides.get("metadata", {})
    overrides["metadata"]["last_updated"] = datetime.now().isoformat()

    with open(OVERRIDES_PATH, "w") as f:
        json.dump(overrides, f, indent=2)


def reset_to_defaults() -> None:
    """
    Delete all operator overrides, reverting to default catalog.
    """
    if OVERRIDES_PATH.exists():
        OVERRIDES_PATH.unlink()


def export_catalog(output_path: Optional[Path] = None) -> Path:
    """
    Export the full merged catalog to a JSON file.

    Args:
        output_path: Where to save (defaults to data/content_export.json)

    Returns:
        Path to exported file
    """
    if output_path is None:
        output_path = _PROJECT_ROOT / "data" / "content_export.json"

    catalog = load_content_catalog()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(catalog, f, indent=2)

    return output_path


def import_overrides(import_path: Path) -> None:
    """
    Import overrides from a JSON file.

    Args:
        import_path: Path to JSON file to import
    """
    with open(import_path, "r") as f:
        imported = json.load(f)

    # Validate structure
    if not isinstance(imported, dict):
        raise ValueError("Import file must be a JSON object")

    # Add metadata
    imported["metadata"] = {
        "last_updated": datetime.now().isoformat(),
        "imported_from": str(import_path),
        "version": "1.0",
    }

    # Save as overrides
    OVERRIDES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OVERRIDES_PATH, "w") as f:
        json.dump(imported, f, indent=2)


def get_education_items(persona: str) -> List[Dict[str, Any]]:
    """
    Get educational content for a persona (with overrides applied).

    Args:
        persona: Persona key

    Returns:
        List of educational items
    """
    catalog = load_content_catalog()
    return catalog.get("educational", {}).get(persona, [])


def get_partner_offers(persona: str) -> List[Dict[str, Any]]:
    """
    Get partner offers for a persona (with overrides applied).

    Args:
        persona: Persona key

    Returns:
        List of partner offers
    """
    catalog = load_content_catalog()
    return catalog.get("offers", {}).get(persona, [])


def get_all_personas() -> List[str]:
    """
    Get list of all personas with content.

    Returns:
        List of persona keys
    """
    catalog = load_content_catalog()
    personas = set()
    personas.update(catalog.get("educational", {}).keys())
    personas.update(catalog.get("offers", {}).keys())
    return sorted(personas)

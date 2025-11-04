"""
CLI entry point for data generation with operator controls.
"""

import json
import sys
from pathlib import Path

from ingest.schemas import DataGenerationConfig
from ingest.operator_controls import OperatorControls, PersonaTarget
from ingest.persona_skewed_generator import PersonaSkewedGenerator
from ingest.loader import DataLoader
from ingest.validators import DataValidator


def main():
    """
    Main entry point for data generation.
    Loads operator config if available, otherwise uses defaults.
    """
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Try to load operator configuration
    operator_config_path = data_dir / "operator_config.json"

    if operator_config_path.exists():
        print(f"📂 Loading operator configuration from {operator_config_path}")
        with open(operator_config_path) as f:
            config_data = json.load(f)

        # Parse configuration
        config_dict = config_data.get("config", {})
        config = DataGenerationConfig(**config_dict)

        # Parse controls
        controls_dict = config_data.get("controls", {})
        # Convert persona strings back to PersonaTarget enums
        if "target_personas" in controls_dict:
            controls_dict["target_personas"] = [
                PersonaTarget(p) for p in controls_dict["target_personas"]
            ]
        controls = OperatorControls(**controls_dict)

        print(f"✓ Using operator-configured parameters")
    else:
        print(f"📋 No operator config found, using defaults")
        config = DataGenerationConfig(seed=42, num_users=100, months_history=6)
        controls = OperatorControls()

    # Generate data
    generator = PersonaSkewedGenerator(config, controls)
    users, accounts, transactions, liabilities = generator.generate_all()

    # Save config
    config_path = data_dir / "config.json"
    full_config = {
        "config": config.model_dump(mode="json"),
        "controls": controls.model_dump(mode="json"),
    }
    with open(config_path, "w") as f:
        json.dump(full_config, f, indent=2, default=str)
    print(f"✓ Saved config to {config_path}")

    # Prepare data for loader
    data = {
        "users": [u.model_dump(mode="json") for u in users],
        "accounts": [a.model_dump(mode="json") for a in accounts],
        "transactions": [t.model_dump(mode="json") for t in transactions],
        "liabilities": [l.model_dump(mode="json") for l in liabilities],
    }

    # Save intermediate JSON
    json_path = data_dir / "synthetic_data.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"✓ Saved JSON data to {json_path}")

    # Validate data
    print("\n🔍 Validating data...")
    validator = DataValidator()
    report = validator.validate_all(data)

    if not report.is_valid():
        print("\n" + report.summary())
        print("\n❌ Validation failed. Please fix errors before loading.")
        sys.exit(1)
    print(f"✓ Validation passed: {report.stats['total_records']} records")

    # Load to SQLite and Parquet
    print("\n📊 Loading data to SQLite and Parquet...")
    try:
        loader = DataLoader()
        loader.load_all(data)
        print("✅ Data generation and loading complete!")

        # Show persona assignment preview
        if generator.user_persona_assignments:
            print("\n📈 Persona Target Assignments (first 10 users):")
            for i, (user_id, persona) in enumerate(list(generator.user_persona_assignments.items())[:10]):
                print(f"   • {user_id}: {persona}")
            if len(generator.user_persona_assignments) > 10:
                print(f"   ... and {len(generator.user_persona_assignments) - 10} more")

        print("\n🎯 Next steps:")
        print("   1. Run persona assignment: uv run python -m personas.assignment")
        print("   2. Launch operator dashboard: uv run python ui/app_operator_nicegui.py")

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

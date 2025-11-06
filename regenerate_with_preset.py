#!/usr/bin/env python3
"""
Regenerate data using the Cash Flow Optimizer preset.
This script applies the preset and calls the pipeline scripts.
"""

import sys
import json
import subprocess
from pathlib import Path

# Import the preset
from ingest.operator_controls import PRESET_CONFIGS


def apply_preset(preset_name: str = "cash_flow_optimizer_focus"):
    """Apply the Cash Flow Optimizer preset to operator_config.json"""

    preset = PRESET_CONFIGS[preset_name]

    # Load existing config to preserve generation parameters
    config_path = Path("data/operator_config.json")

    if config_path.exists():
        with open(config_path, "r") as f:
            existing = json.load(f)
            config_section = existing.get("config", {})
    else:
        config_section = {
            "seed": 42,
            "num_users": 100,
            "months_history": 6,
            "avg_transactions_per_month": 30,
        }

    # Convert preset to dict
    from datetime import datetime
    config_section["generation_timestamp"] = datetime.now().isoformat()

    new_config = {
        "config": config_section,
        "controls": preset.model_dump()
    }

    # Save the updated config
    with open(config_path, "w") as f:
        json.dump(new_config, f, indent=2)

    print(f"✓ Applied '{preset_name}' preset to {config_path}")
    print(f"  - Target personas: {preset.target_personas}")
    print(f"  - Savings adoption: {preset.savings_adoption_rate}")
    print(f"  - High spender probability: {preset.high_spender_probability}")
    print(f"  - Savings growth target: {preset.savings_growth_target_pct}%")


def run_command(cmd: list, description: str):
    """Run a command and handle errors"""
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ Error: {result.stderr}")
        sys.exit(1)
    print(f"  ✓ {description}")
    return result


def main():
    """Main execution flow"""
    print("=" * 80)
    print("Cash Flow Optimizer Data Regeneration")
    print("=" * 80)
    print()

    # Step 1: Apply preset
    print("[1/5] Applying Cash Flow Optimizer preset...")
    apply_preset("cash_flow_optimizer_focus")
    print()

    # Step 2: Generate data
    print("[2/5] Generating synthetic data...")
    run_command(
        ["uv", "run", "python", "-m", "ingest.data_generator"],
        "Data generation complete"
    )
    print()

    # Step 3: Load data
    print("[3/5] Loading data into SQLite and Parquet...")
    run_command(
        ["uv", "run", "python", "-m", "ingest.loader"],
        "Data loading complete"
    )
    print()

    # Step 4: Extract features
    print("[4/5] Extracting behavioral signals...")
    run_command(
        ["uv", "run", "python", "-m", "features"],
        "Feature extraction complete"
    )
    print()

    # Step 5: Assign personas
    print("[5/5] Assigning personas...")
    run_command(
        ["uv", "run", "python", "-m", "personas.assignment"],
        "Persona assignment complete"
    )
    print()

    print("=" * 80)
    print("✅ Regeneration complete!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  - Check persona distribution in the NiceGUI dashboard")
    print("  - Review trace JSONs in docs/traces/")
    print("  - Verify Cash Flow Optimizer persona appears in distribution")


if __name__ == "__main__":
    main()

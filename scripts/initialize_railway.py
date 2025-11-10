#!/usr/bin/env python3
"""
Railway initialization script - runs full pipeline on startup
"""
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def main():
    """Run full pipeline"""
    steps = [
        ("python -m ingest.data_generator", "Step 1: Generate synthetic data"),
        ("python -m ingest.loader", "Step 2: Load data into SQLite/Parquet"),
        ("python -m eval.run", "Step 3: Run full pipeline (features, personas, recommendations)"),
        ("python scripts/seed_educational_videos.py", "Step 4: Seed educational videos"),
    ]

    for cmd, description in steps:
        if not run_command(cmd, description):
            print(f"\n❌ Failed at: {description}")
            sys.exit(1)

    print("\n✅ All pipeline steps completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

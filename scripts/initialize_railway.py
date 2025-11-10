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
        ("python -m features", "Step 3: Generate behavioral signals"),
        ("python personas/assignment.py", "Step 4: Assign personas"),
        ("python scripts/seed_educational_videos.py", "Step 5: Seed educational videos"),
    ]

    for cmd, description in steps:
        if not run_command(cmd, description):
            print(f"\n❌ Failed at: {description}")
            # Don't fail entirely - log and continue
            print(f"⚠️  Continuing despite error...")

    print("\n✅ Pipeline initialization complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

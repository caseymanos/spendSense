"""
Entry point for running the features module as a script.
Executes the feature pipeline to generate behavioral signals.
"""

from features import run_feature_pipeline

if __name__ == "__main__":
    signals_df = run_feature_pipeline()
    print("\n✅ Feature pipeline complete!")
    print(f"Generated signals for {len(signals_df)} users")
    print(f"\nSignal columns: {list(signals_df.columns)}")
    print(f"\nSample signals:\n{signals_df.head()}")

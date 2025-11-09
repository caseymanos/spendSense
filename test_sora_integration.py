#!/usr/bin/env python3
"""
SORA Video Generation Integration Test

Usage:
    export SORA_ENABLED=true
    export SORA_API_KEY="sk-your-key"
    uv run python test_sora_integration.py
"""

from recommend.engine import generate_recommendations
from ingest.constants import VIDEO_GENERATION_CONFIG

def main():
    print("=" * 70)
    print("SORA Video Generation Integration Test")
    print("=" * 70)
    print()

    # Check configuration
    print("1. Configuration Check:")
    print(f"   SORA Enabled: {VIDEO_GENERATION_CONFIG['enabled']}")
    print(f"   API Key Set: {bool(VIDEO_GENERATION_CONFIG['api_key'])}")

    if not VIDEO_GENERATION_CONFIG['enabled']:
        print("\n⚠️  SORA is disabled!")
        print("   Set: export SORA_ENABLED=true")
        print("   Then run this script again.")
        return

    if not VIDEO_GENERATION_CONFIG['api_key']:
        print("\n⚠️  SORA API key not set!")
        print("   Set: export SORA_API_KEY='sk-your-key'")
        print("   Then run this script again.")
        return

    print("   ✅ Configuration looks good!\n")

    # Test users with high_utilization persona (has credit_utilization topic)
    test_users = ['user_0001', 'user_0004', 'user_0007']

    for user_id in test_users:
        print(f"\n2. Testing {user_id}:")
        print("-" * 50)

        try:
            result = generate_recommendations(user_id)

            # Find video recommendations
            video_recs = [r for r in result['recommendations']
                         if 'video_url' in r or 'video_error' in r]

            if video_recs:
                for rec in video_recs:
                    print(f"   Title: {rec['title']}")
                    print(f"   Topic: {rec.get('topic', 'N/A')}")

                    if rec.get('video_url'):
                        print(f"   ✅ Video URL: {rec['video_url']}")
                        if 'video_metadata' in rec:
                            meta = rec['video_metadata']
                            print(f"   Duration: {meta.get('duration')}s")
                            print(f"   Resolution: {meta.get('resolution')}")
                    elif 'video_error' in rec:
                        print(f"   ⚠️  Video Error: {rec['video_error']}")
                        if 'error_detail' in rec:
                            print(f"   Details: {rec.get('error_detail', 'N/A')[:100]}...")
            else:
                # Check if any credit_utilization topics exist
                topics = [r.get('topic') for r in result['recommendations']]
                if 'credit_utilization' in topics:
                    print("   ⚠️  credit_utilization topic found but no video generated")
                else:
                    print(f"   ℹ️  No credit_utilization topic (topics: {topics})")

            print(f"   Total recommendations: {len(result['recommendations'])}")

        except Exception as e:
            print(f"   ❌ Error: {type(e).__name__}: {e}")

    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Check trace JSONs: cat docs/traces/user_0001.json | jq '.video_generation_log'")
    print("2. Review decision log: docs/decision_log.md")
    print("3. See manual runbook: docs/video_generation_runbook.md")

if __name__ == "__main__":
    main()

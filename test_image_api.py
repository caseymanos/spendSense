"""
Real API integration test for DALL-E 3 image generation.

Tests actual image generation with OpenAI API.
Run this manually when OPENAI_API_KEY is set.

Usage:
    export OPENAI_API_KEY="sk-..."
    export IMAGE_GENERATION_ENABLED="true"
    python test_image_api.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from recommend.image_generator import ImageGenerator
from recommend.prompt_templates import build_image_prompt, get_template_metadata


def test_real_api():
    """Test image generation with real OpenAI API."""

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Export your key: export OPENAI_API_KEY='sk-...'")
        return False

    print(f"API Key found: {api_key[:10]}...")
    print("\n" + "="*80)
    print("DALL-E 3 Image Generation Test")
    print("="*80 + "\n")

    # Initialize generator
    try:
        generator = ImageGenerator(api_key=api_key)
        print("✓ ImageGenerator initialized successfully\n")
    except Exception as e:
        print(f"✗ Failed to initialize ImageGenerator: {e}")
        return False

    # Test cases: Generate 5 different educational infographics
    test_cases = [
        {
            "topic": "credit_utilization",
            "persona": "high_utilization",
            "context": {"credit_max_util_pct": 73, "card_mask": "4523"},
            "description": "Credit Utilization Gauge"
        },
        {
            "topic": "debt_paydown_strategy",
            "persona": "high_utilization",
            "context": {"balance_high": "$7,500", "balance_low": "$2,100"},
            "description": "Debt Avalanche Strategy"
        },
        {
            "topic": "emergency_fund",
            "persona": "variable_income",
            "context": {},
            "description": "Emergency Fund Building"
        },
        {
            "topic": "subscription_audit",
            "persona": "subscription_heavy",
            "context": {"monthly_savings": "$45"},
            "description": "Subscription Optimization"
        },
        {
            "topic": "automation",
            "persona": "savings_builder",
            "context": {},
            "description": "Automated Savings"
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}/5: {test_case['description']}")
        print("-" * 80)

        try:
            # Build prompt
            prompt = build_image_prompt(
                topic=test_case["topic"],
                persona=test_case["persona"],
                user_context=test_case["context"]
            )

            print(f"Prompt length: {len(prompt)} characters")
            print(f"Prompt preview: {prompt[:150]}...\n")

            # Get metadata
            metadata = get_template_metadata(
                topic=test_case["topic"],
                persona=test_case["persona"]
            )

            print(f"Image specs: {metadata['size']}, {metadata['quality']} quality")
            print("Generating image (this may take 5-10 seconds)...\n")

            # Generate image
            result = generator.generate_image(
                prompt=prompt,
                size=metadata["size"],
                quality=metadata["quality"]
            )

            if result.get("image_url"):
                print(f"✓ SUCCESS")
                print(f"  Image URL: {result['image_url']}")
                print(f"  Generated: {result['generated_at']}")
                print(f"  DALL-E revised prompt: {result['revised_prompt'][:100]}...")
                results.append({
                    "test": test_case['description'],
                    "status": "success",
                    "url": result['image_url']
                })
            else:
                print(f"✗ FAILED: {result.get('error', 'unknown error')}")
                print(f"  Details: {result.get('error_detail', 'N/A')}")
                results.append({
                    "test": test_case['description'],
                    "status": "failed",
                    "error": result.get('error')
                })

        except Exception as e:
            print(f"✗ EXCEPTION: {type(e).__name__}: {e}")
            results.append({
                "test": test_case['description'],
                "status": "exception",
                "error": str(e)
            })

        print("\n")

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80 + "\n")

    successful = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] != "success")

    print(f"Total tests: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}\n")

    if successful > 0:
        print("Generated image URLs:")
        for r in results:
            if r["status"] == "success":
                print(f"  • {r['test']}: {r['url']}")

    print("\n" + "="*80)

    return successful == len(results)


if __name__ == "__main__":
    success = test_real_api()
    sys.exit(0 if success else 1)

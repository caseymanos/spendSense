"""
Mock DALL-E 3 API client for testing image generation without making actual API calls.

This mock simulates:
- API latency
- Success/failure scenarios
- Deterministic image URL generation
- Error conditions
"""

import time
import hashlib
from typing import Dict, Optional
from datetime import datetime


class MockImageResponse:
    """Mock response object from DALL-E 3 API."""

    def __init__(self, url: str, revised_prompt: str):
        self.url = url
        self.revised_prompt = revised_prompt


class MockImageData:
    """Mock data container for image response."""

    def __init__(self, response: MockImageResponse):
        self.data = [response]


class MockImageGenerator:
    """
    Mock ImageGenerator client for testing.

    Simulates API behavior without making real network calls.
    Useful for unit testing and integration testing.

    Args:
        simulate_error: Exception to raise (simulates API failure)
        delay_seconds: Artificial delay to simulate network latency
    """

    def __init__(self, api_key: str = "mock-key", simulate_error: Optional[Exception] = None, delay_seconds: float = 0.2):
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.api_key = api_key
        self.simulate_error = simulate_error
        self.delay_seconds = delay_seconds
        self.generation_count = 0

    def generate_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard") -> Dict:
        """
        Mock image generation method.

        Args:
            prompt: Image generation prompt
            size: Image dimensions
            quality: Image quality level

        Returns:
            Dict with image_url, revised_prompt, size, quality, generated_at

        Raises:
            Exception if simulate_error was set
        """
        self.generation_count += 1

        # Simulate network latency
        time.sleep(self.delay_seconds)

        # Simulate errors if configured
        if self.simulate_error:
            raise self.simulate_error

        # Generate deterministic URL based on prompt hash
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:8]

        return {
            "image_url": f"https://mock-dalle.test/img/{prompt_hash}.png",
            "revised_prompt": f"Enhanced: {prompt[:50]}...",
            "size": size,
            "quality": quality,
            "generated_at": datetime.now().isoformat()
        }


class MockImageAPIError(Exception):
    """Mock API error exception to simulate DALL-E 3 API errors."""
    pass


class MockImageRateLimit(Exception):
    """Mock rate limit exception to simulate DALL-E 3 API rate limiting."""
    pass

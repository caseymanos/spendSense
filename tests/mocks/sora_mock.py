"""
Mock SORA API client for testing video generation without making actual API calls.

This mock simulates:
- API latency
- Success/failure scenarios
- Deterministic video URL generation
- Timeout and error conditions
"""

import time
import hashlib
from typing import Optional
from datetime import datetime


class MockVideoResponse:
    """Mock response object from SORA API."""

    def __init__(self, url: str, duration: int, resolution: str):
        self.url = url
        self.duration = duration
        self.resolution = resolution
        self.created_at = datetime.now().isoformat()


class MockSORAClient:
    """
    Mock SORA client for testing.

    Simulates API behavior without making real network calls.
    Useful for unit testing and integration testing.

    Args:
        simulate_error: Exception to raise (simulates API failure)
        delay_seconds: Artificial delay to simulate network latency
    """

    def __init__(self, simulate_error: Optional[Exception] = None, delay_seconds: float = 0.5):
        self.simulate_error = simulate_error
        self.delay_seconds = delay_seconds
        self.generation_count = 0
        self.sora = self  # Mock the nested sora attribute

    def generate(self, prompt: str, timeout: int = 30, **kwargs) -> MockVideoResponse:
        """
        Mock video generation method.

        Args:
            prompt: Video generation prompt
            timeout: Timeout in seconds (not enforced in mock)
            **kwargs: Additional parameters (ignored)

        Returns:
            MockVideoResponse with deterministic URL

        Raises:
            Exception if simulate_error was set
        """
        self.generation_count += 1

        # Simulate network latency
        time.sleep(self.delay_seconds)

        # Simulate errors if configured
        if self.simulate_error:
            raise self.simulate_error

        # Simulate timeout if delay exceeds timeout
        if self.delay_seconds > timeout:
            raise TimeoutError(f"Request timed out after {timeout}s")

        # Generate deterministic URL based on prompt hash
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:8]

        return MockVideoResponse(
            url=f"https://mock-sora.test/v/{prompt_hash}",
            duration=8,  # Default 8-second videos
            resolution="720p"
        )


class MockSORATimeout(Exception):
    """Mock timeout exception to simulate SORA API timeouts."""
    pass


class MockSORARateLimit(Exception):
    """Mock rate limit exception to simulate SORA API rate limiting."""
    pass

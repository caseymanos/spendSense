"""
SORA Video Generator Module

Handles integration with OpenAI's SORA API for generating educational
financial behavior videos. Includes retry logic, error handling, and
graceful degradation.

Design Pattern: Synchronous API client with decorator-based retries
(see docs/decision_log.md Decision 58 for rationale)
"""

import time
import logging
from typing import Dict, Any, Optional
from functools import wraps

import openai
from ingest.constants import VIDEO_GENERATION_CONFIG


logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, backoff_seconds: float = 2.0):
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        backoff_seconds: Initial backoff time (doubles each retry)

    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (openai.APITimeoutError, openai.APIConnectionError) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = backoff_seconds * (2 ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_attempts} attempts failed: {e}")
            # If all retries exhausted, return error dict
            return {"video_url": None, "error": str(last_exception)}
        return wrapper
    return decorator


class SORAVideoGenerator:
    """
    OpenAI SORA API client for video generation.

    Provides synchronous video generation with automatic retries,
    timeout enforcement, and structured error handling.

    Usage:
        generator = SORAVideoGenerator(api_key="sk-...", timeout=30)
        result = generator.generate_video(prompt="...", metadata={})

    Returns:
        Dict with video_url, duration, resolution, generated_at on success
        Dict with video_url=None, error="reason" on failure
    """

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize SORA video generator.

        Args:
            api_key: OpenAI API key with SORA access
            timeout: Request timeout in seconds

        Raises:
            ValueError: If API key is empty or invalid
        """
        if not api_key:
            raise ValueError("SORA API key is required")

        self.api_key = api_key
        self.timeout = timeout
        self.client = openai.Client(api_key=api_key, timeout=timeout)

        logger.info(f"SORAVideoGenerator initialized (timeout={timeout}s)")

    @retry(
        max_attempts=VIDEO_GENERATION_CONFIG["max_retries"],
        backoff_seconds=VIDEO_GENERATION_CONFIG["retry_backoff_seconds"]
    )
    def generate_video(self, prompt: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video using SORA API.

        Args:
            prompt: Video generation prompt (visual description)
            metadata: Additional parameters (resolution, duration, etc.)

        Returns:
            Success: {
                "video_url": "https://...",
                "duration": 8,
                "resolution": "720p",
                "generated_at": "2025-11-05T10:00:00Z"
            }

            Failure: {
                "video_url": None,
                "error": "timeout | api_error | rate_limit"
            }
        """
        try:
            logger.info(f"Generating video with prompt (length={len(prompt)})")

            # Note: The actual SORA API endpoint may differ
            # This is based on expected OpenAI API patterns
            # Update when SORA API documentation is available
            response = self.client.sora.generate(
                prompt=prompt,
                model=VIDEO_GENERATION_CONFIG["model"],
                resolution=VIDEO_GENERATION_CONFIG["resolution"],
                timeout=self.timeout,
                **metadata
            )

            result = {
                "video_url": response.url,
                "duration": response.duration,
                "resolution": response.resolution,
                "generated_at": response.created_at
            }

            logger.info(f"Video generated successfully: {result['video_url']}")
            return result

        except openai.APITimeoutError as e:
            logger.error(f"SORA API timeout after {self.timeout}s: {e}")
            return {
                "video_url": None,
                "error": "timeout",
                "error_detail": str(e)
            }

        except openai.RateLimitError as e:
            logger.error(f"SORA API rate limit exceeded: {e}")
            return {
                "video_url": None,
                "error": "rate_limit",
                "error_detail": str(e)
            }

        except openai.APIError as e:
            logger.error(f"SORA API error: {e}")
            return {
                "video_url": None,
                "error": "api_error",
                "error_detail": str(e)
            }

        except Exception as e:
            logger.error(f"Unexpected error during video generation: {e}")
            return {
                "video_url": None,
                "error": "unknown_error",
                "error_detail": str(e)
            }


# Module-level singleton (initialized in recommend/engine.py)
VIDEO_GENERATOR: Optional[SORAVideoGenerator] = None

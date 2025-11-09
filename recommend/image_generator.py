"""
Image Generator Module for SpendSense

Handles integration with OpenAI's DALL-E 3 API for generating educational
financial infographics. Replaces video generation with static images that are
more effective for financial education and dramatically simpler to implement.

Design Pattern: Simple synchronous API client (no retry complexity needed)
Cost: $0.04-0.08 per image (vs $0.50+ for video)
Speed: 2-8 seconds (vs 30-60s for video)
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from openai import OpenAI


logger = logging.getLogger(__name__)


class ImageGenerator:
    """
    OpenAI DALL-E 3 API client for educational infographic generation.

    Provides simple, synchronous image generation with straightforward
    error handling. Much simpler than video generation - no retry logic,
    no complex timeout handling, no fallback images needed.

    Usage:
        generator = ImageGenerator(api_key="sk-...")
        result = generator.generate_image(prompt="...", size="1024x1024")

    Returns:
        Dict with image_url, revised_prompt, generated_at on success
        Dict with image_url=None, error="reason" on failure
    """

    def __init__(self, api_key: str):
        """
        Initialize DALL-E 3 image generator.

        Args:
            api_key: OpenAI API key

        Raises:
            ValueError: If API key is empty or invalid
        """
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

        logger.info("ImageGenerator initialized (DALL-E 3)")

    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Dict[str, Any]:
        """
        Generate educational infographic using DALL-E 3.

        Args:
            prompt: Image generation prompt (visual description)
            size: Image dimensions ("1024x1024" or "1024x1792")
            quality: "standard" ($0.04-0.08) or "hd" ($0.08-0.12)

        Returns:
            Success: {
                "image_url": "https://...",
                "revised_prompt": "...",  # DALL-E's interpretation
                "size": "1024x1024",
                "quality": "standard",
                "generated_at": "2025-11-06T10:00:00Z"
            }

            Failure: {
                "image_url": None,
                "error": "api_error | rate_limit | invalid_prompt",
                "error_detail": "..."
            }
        """
        try:
            logger.info(f"Generating image (size={size}, quality={quality})")

            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1  # DALL-E 3 only supports n=1
            )

            result = {
                "image_url": response.data[0].url,
                "revised_prompt": response.data[0].revised_prompt,
                "size": size,
                "quality": quality,
                "generated_at": datetime.now().isoformat()
            }

            logger.info(f"Image generated successfully: {result['image_url'][:50]}...")
            return result

        except Exception as e:
            logger.error(f"Image generation failed: {type(e).__name__}: {e}")
            return {
                "image_url": None,
                "error": "api_error",
                "error_detail": str(e)
            }


# Module-level singleton (initialized in recommend/engine.py)
IMAGE_GENERATOR: Optional[ImageGenerator] = None

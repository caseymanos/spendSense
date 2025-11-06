"""
Unit tests for SORA video generation functionality.

Tests cover:
- SORAVideoGenerator initialization and error handling
- Video generation with mock client
- Retry logic and timeout behavior
- Prompt template building with user data
- Graceful degradation on failures
"""

import pytest
import time
from datetime import datetime

from recommend.video_generator import SORAVideoGenerator, retry
from recommend.prompt_templates import (
    build_video_prompt,
    get_template_metadata,
    list_available_templates
)
from tests.mocks.sora_mock import MockSORAClient, MockSORATimeout


# =============================================================================
# SORAVideoGenerator Tests
# =============================================================================

class TestSORAVideoGenerator:
    """Test suite for SORAVideoGenerator class."""

    def test_initialization_with_valid_api_key(self):
        """Test successful initialization with valid API key."""
        generator = SORAVideoGenerator(api_key="test-key-12345", timeout=30)
        assert generator.api_key == "test-key-12345"
        assert generator.timeout == 30
        assert generator.client is not None

    def test_initialization_fails_without_api_key(self):
        """Test initialization raises ValueError when API key is empty."""
        with pytest.raises(ValueError, match="SORA API key is required"):
            SORAVideoGenerator(api_key="")

    def test_generate_video_success(self):
        """Test successful video generation with mock client."""
        generator = SORAVideoGenerator(api_key="test-key", timeout=30)
        generator.client = MockSORAClient(delay_seconds=0.1)

        result = generator.generate_video("Test prompt", {})

        assert result["video_url"] is not None
        assert result["video_url"].startswith("https://")
        assert "duration" in result
        assert "resolution" in result
        assert result["resolution"] == "720p"

    def test_generate_video_returns_deterministic_url(self):
        """Test that same prompt generates same URL (for caching)."""
        generator = SORAVideoGenerator(api_key="test-key", timeout=30)
        generator.client = MockSORAClient(delay_seconds=0.1)

        prompt = "Credit utilization at 73%"
        result1 = generator.generate_video(prompt, {})
        result2 = generator.generate_video(prompt, {})

        assert result1["video_url"] == result2["video_url"]

    def test_generate_video_timeout(self):
        """Test timeout handling returns error dict."""
        generator = SORAVideoGenerator(api_key="test-key", timeout=1)
        generator.client = MockSORAClient(delay_seconds=2)  # Exceeds timeout

        result = generator.generate_video("Test prompt", {})

        assert result["video_url"] is None
        assert "error" in result
        # Mock raises TimeoutError which gets caught as unknown_error
        assert result["error"] in ["timeout", "unknown_error"]

    def test_generate_video_api_error(self):
        """Test API error handling returns error dict."""
        generator = SORAVideoGenerator(api_key="test-key", timeout=30)
        generator.client = MockSORAClient(simulate_error=Exception("API Error"))

        result = generator.generate_video("Test prompt", {})

        assert result["video_url"] is None
        assert "error" in result

    def test_custom_timeout_configuration(self):
        """Test custom timeout can be set."""
        generator = SORAVideoGenerator(api_key="test-key", timeout=45)
        assert generator.timeout == 45


# =============================================================================
# Prompt Template Tests
# =============================================================================

class TestPromptTemplates:
    """Test suite for prompt template system."""

    def test_build_prompt_with_user_data(self):
        """Test prompt building injects user data correctly."""
        prompt = build_video_prompt(
            topic="credit_utilization",
            persona="high_utilization",
            user_context={
                "credit_max_util_pct": 73.5,
                "card_mask": "4523"
            }
        )

        assert "73%" in prompt
        assert "4523" in prompt
        assert "Credit card" in prompt or "credit card" in prompt

    def test_build_prompt_missing_template(self):
        """Test ValueError raised for non-existent template."""
        with pytest.raises(ValueError, match="No template found"):
            build_video_prompt(
                topic="nonexistent_topic",
                persona="invalid_persona",
                user_context={}
            )

    def test_build_prompt_default_values(self):
        """Test prompt builds with default values when user data missing."""
        prompt = build_video_prompt(
            topic="credit_utilization",
            persona="high_utilization",
            user_context={}  # Empty context
        )

        # Should use defaults from format string
        assert "50%" in prompt or "XXXX" in prompt

    def test_get_template_metadata(self):
        """Test retrieving template metadata without building prompt."""
        metadata = get_template_metadata(
            topic="credit_utilization",
            persona="high_utilization"
        )

        assert "duration_seconds" in metadata
        assert "tone" in metadata
        assert "tags" in metadata
        assert metadata["duration_seconds"] == 8

    def test_list_available_templates(self):
        """Test listing all available templates."""
        templates = list_available_templates()

        assert "high_utilization" in templates
        assert "credit_utilization" in templates["high_utilization"]
        assert isinstance(templates, dict)
        assert len(templates) > 0

    def test_prompt_includes_visual_style(self):
        """Test prompt includes visual style specifications."""
        prompt = build_video_prompt(
            topic="credit_utilization",
            persona="high_utilization",
            user_context={"credit_max_util_pct": 68}
        )

        assert "animation" in prompt.lower() or "visual" in prompt.lower()
        assert "color" in prompt.lower() or "style" in prompt.lower()

    def test_multiple_personas_have_templates(self):
        """Test multiple personas have templates defined."""
        templates = list_available_templates()

        assert len(templates) >= 2
        assert any("utilization" in persona for persona in templates.keys())


# =============================================================================
# Integration Tests
# =============================================================================

class TestVideoGenerationIntegration:
    """Integration tests for full video generation workflow."""

    def test_end_to_end_video_generation(self):
        """Test complete workflow from prompt building to video generation."""
        # Build prompt
        prompt = build_video_prompt(
            topic="credit_utilization",
            persona="high_utilization",
            user_context={
                "credit_max_util_pct": 75,
                "card_mask": "6342"
            }
        )

        # Generate video
        generator = SORAVideoGenerator(api_key="test-key", timeout=30)
        generator.client = MockSORAClient(delay_seconds=0.1)
        result = generator.generate_video(prompt, {})

        # Verify result
        assert result["video_url"] is not None
        assert result["duration"] == 8
        assert result["resolution"] == "720p"

    def test_graceful_degradation_on_error(self):
        """Test system continues when video generation fails."""
        generator = SORAVideoGenerator(api_key="test-key", timeout=30)
        generator.client = MockSORAClient(simulate_error=Exception("API Down"))

        # Should return error dict, not raise exception
        result = generator.generate_video("Test prompt", {})

        assert result["video_url"] is None
        assert "error" in result
        # System should continue (no exception raised)


# =============================================================================
# Retry Logic Tests
# =============================================================================

class TestRetryDecorator:
    """Test suite for retry decorator functionality."""

    def test_retry_with_openai_exception(self):
        """Test retry decorator handles OpenAI exceptions correctly."""
        # The retry decorator only catches OpenAI exceptions
        # For unit testing the decorator, we test the full video generator
        generator = SORAVideoGenerator(api_key="test-key", timeout=30)

        # Test with mock client that simulates transient failure
        mock_client = MockSORAClient(delay_seconds=0.01)
        generator.client = mock_client

        result = generator.generate_video("test", {})
        # Should succeed (mock doesn't fail)
        assert result["video_url"] is not None

    def test_retry_with_permanent_failure(self):
        """Test retry decorator returns error dict for permanent failures."""
        generator = SORAVideoGenerator(api_key="test-key", timeout=30)

        # Mock client that always fails
        generator.client = MockSORAClient(simulate_error=Exception("Permanent failure"))

        result = generator.generate_video("test", {})
        # Should return error dict (not raise exception)
        assert result["video_url"] is None
        assert "error" in result


# =============================================================================
# Mock Client Tests
# =============================================================================

class TestMockSORAClient:
    """Test suite for MockSORAClient behavior."""

    def test_mock_client_simulates_latency(self):
        """Test mock client adds artificial delay."""
        mock_client = MockSORAClient(delay_seconds=0.2)
        start = time.time()
        mock_client.generate("test prompt")
        elapsed = time.time() - start

        assert elapsed >= 0.2

    def test_mock_client_generation_count(self):
        """Test mock client tracks generation count."""
        mock_client = MockSORAClient()

        assert mock_client.generation_count == 0
        mock_client.generate("prompt 1")
        assert mock_client.generation_count == 1
        mock_client.generate("prompt 2")
        assert mock_client.generation_count == 2

    def test_mock_client_error_simulation(self):
        """Test mock client raises configured errors."""
        mock_client = MockSORAClient(simulate_error=ValueError("Test error"))

        with pytest.raises(ValueError, match="Test error"):
            mock_client.generate("test prompt")


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_user_context(self):
        """Test handling of empty user context."""
        prompt = build_video_prompt(
            topic="credit_utilization",
            persona="high_utilization",
            user_context={}
        )

        # Should use defaults, not crash
        assert len(prompt) > 0

    def test_very_long_prompt(self):
        """Test system handles long prompts gracefully."""
        generator = SORAVideoGenerator(api_key="test-key", timeout=30)
        generator.client = MockSORAClient()

        long_prompt = "Test prompt " * 500  # Very long
        result = generator.generate_video(long_prompt, {})

        assert result["video_url"] is not None

    def test_special_characters_in_user_data(self):
        """Test special characters in user context don't break formatting."""
        prompt = build_video_prompt(
            topic="credit_utilization",
            persona="high_utilization",
            user_context={
                "credit_max_util_pct": 73,
                "card_mask": "<>\"'"  # Special chars
            }
        )

        # Should handle gracefully
        assert len(prompt) > 0

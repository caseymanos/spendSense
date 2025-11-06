"""
Tests for DALL-E 3 image generation integration.

Verifies image generation functionality with mock API client.
Tests prompt building, error handling, and metadata tracking.
"""

import pytest
from recommend.image_generator import ImageGenerator
from recommend.prompt_templates import (
    build_image_prompt,
    get_template_metadata,
    list_available_templates,
)
from tests.mocks.image_mock import MockImageGenerator, MockImageAPIError


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_image_generator():
    """Mock image generator with default settings."""
    return MockImageGenerator(api_key="test-key", delay_seconds=0.1)


@pytest.fixture
def mock_image_generator_with_error():
    """Mock image generator that raises API errors."""
    return MockImageGenerator(
        api_key="test-key",
        simulate_error=MockImageAPIError("Rate limit exceeded"),
        delay_seconds=0.1
    )


# =============================================================================
# IMAGE GENERATION TESTS
# =============================================================================


def test_image_generator_initialization():
    """Test ImageGenerator initialization."""
    generator = MockImageGenerator(api_key="test-key")
    assert generator.api_key == "test-key"
    assert generator.generation_count == 0


def test_image_generator_missing_api_key():
    """Test ImageGenerator rejects empty API key."""
    with pytest.raises(ValueError, match="OpenAI API key is required"):
        MockImageGenerator(api_key="")


def test_image_generation_success(mock_image_generator):
    """Test successful image generation."""
    result = mock_image_generator.generate_image(
        prompt="Create a financial infographic",
        size="1024x1024",
        quality="standard"
    )

    assert result["image_url"] is not None
    assert result["image_url"].startswith("https://mock-dalle.test/img/")
    assert result["size"] == "1024x1024"
    assert result["quality"] == "standard"
    assert "generated_at" in result
    assert "revised_prompt" in result


def test_image_generation_api_error(mock_image_generator_with_error):
    """Test image generation with API error."""
    with pytest.raises(MockImageAPIError):
        mock_image_generator_with_error.generate_image(
            prompt="Test prompt",
            size="1024x1024"
        )


def test_image_generation_different_sizes(mock_image_generator):
    """Test image generation with different sizes."""
    sizes = ["1024x1024", "1024x1792"]

    for size in sizes:
        result = mock_image_generator.generate_image(
            prompt="Test prompt",
            size=size
        )
        assert result["size"] == size


def test_image_generation_quality_levels(mock_image_generator):
    """Test image generation with different quality levels."""
    qualities = ["standard", "hd"]

    for quality in qualities:
        result = mock_image_generator.generate_image(
            prompt="Test prompt",
            quality=quality
        )
        assert result["quality"] == quality


# =============================================================================
# PROMPT TEMPLATE TESTS
# =============================================================================


def test_build_image_prompt_credit_utilization():
    """Test building image prompt for credit_utilization topic."""
    prompt = build_image_prompt(
        topic="credit_utilization",
        persona="high_utilization",
        user_context={
            "credit_max_util_pct": 73.5,
            "card_mask": "4523"
        }
    )

    assert "credit card utilization" in prompt.lower()
    assert "73%" in prompt
    assert "4523" in prompt
    assert "30%" in prompt  # Target utilization


def test_build_image_prompt_debt_paydown():
    """Test building image prompt for debt_paydown_strategy topic."""
    prompt = build_image_prompt(
        topic="debt_paydown_strategy",
        persona="high_utilization",
        user_context={
            "balance_high": "$7,500",
            "balance_low": "$2,100"
        }
    )

    assert "avalanche" in prompt.lower()
    assert "$7,500" in prompt
    assert "$2,100" in prompt


def test_build_image_prompt_emergency_fund():
    """Test building image prompt for emergency_fund topic."""
    prompt = build_image_prompt(
        topic="emergency_fund",
        persona="variable_income",
        user_context={}
    )

    assert "emergency fund" in prompt.lower()
    assert "3-6 months" in prompt.lower() or "3 months" in prompt.lower()


def test_build_image_prompt_missing_template():
    """Test building prompt with invalid persona/topic combination."""
    with pytest.raises(ValueError, match="No template found"):
        build_image_prompt(
            topic="invalid_topic",
            persona="high_utilization",
            user_context={}
        )


def test_build_image_prompt_defaults():
    """Test prompt building with default user context values."""
    prompt = build_image_prompt(
        topic="credit_utilization",
        persona="high_utilization",
        user_context={}
    )

    # Should use defaults
    assert "50%" in prompt  # Default utilization
    assert "XXXX" in prompt  # Default card mask


# =============================================================================
# TEMPLATE METADATA TESTS
# =============================================================================


def test_get_template_metadata_credit_utilization():
    """Test retrieving metadata for credit_utilization template."""
    metadata = get_template_metadata(
        topic="credit_utilization",
        persona="high_utilization"
    )

    assert metadata["size"] == "1024x1024"
    assert metadata["quality"] == "standard"
    assert "supportive" in metadata["tone"]
    assert "credit" in metadata["tags"]


def test_get_template_metadata_missing():
    """Test metadata retrieval for non-existent template."""
    with pytest.raises(ValueError, match="No template found"):
        get_template_metadata(
            topic="invalid_topic",
            persona="high_utilization"
        )


def test_list_available_templates():
    """Test listing all available templates."""
    templates = list_available_templates()

    assert "high_utilization" in templates
    assert "variable_income" in templates
    assert "subscription_heavy" in templates
    assert "savings_builder" in templates

    # Check specific topics
    assert "credit_utilization" in templates["high_utilization"]
    assert "emergency_fund" in templates["variable_income"]


# =============================================================================
# END-TO-END IMAGE GENERATION TESTS
# =============================================================================


def test_end_to_end_image_generation(mock_image_generator):
    """Test full image generation pipeline."""
    # Build prompt
    prompt = build_image_prompt(
        topic="credit_utilization",
        persona="high_utilization",
        user_context={
            "credit_max_util_pct": 68,
            "card_mask": "8234"
        }
    )

    # Get metadata
    metadata = get_template_metadata(
        topic="credit_utilization",
        persona="high_utilization"
    )

    # Generate image
    result = mock_image_generator.generate_image(
        prompt=prompt,
        size=metadata["size"],
        quality=metadata["quality"]
    )

    assert result["image_url"] is not None
    assert result["size"] == "1024x1024"
    assert result["quality"] == "standard"


def test_multiple_image_generations(mock_image_generator):
    """Test generating multiple images sequentially."""
    topics_and_personas = [
        ("credit_utilization", "high_utilization"),
        ("emergency_fund", "variable_income"),
        ("subscription_audit", "subscription_heavy"),
    ]

    for topic, persona in topics_and_personas:
        prompt = build_image_prompt(topic, persona, {})
        result = mock_image_generator.generate_image(prompt)
        assert result["image_url"] is not None

    # Should have generated 3 images
    assert mock_image_generator.generation_count == 3


def test_image_generation_deterministic_urls(mock_image_generator):
    """Test that same prompt generates same URL (deterministic hashing)."""
    prompt = "Test prompt for determinism"

    result1 = mock_image_generator.generate_image(prompt)
    result2 = mock_image_generator.generate_image(prompt)

    assert result1["image_url"] == result2["image_url"]

"""
AI-Powered Recommendations Generator for SpendSense MVP V2

This module uses OpenAI's API to generate personalized financial recommendations
based on user behavioral data, persona, and signals.

Core Functions:
- generate_ai_recommendations(user_id, api_key): Generate AI recommendations for a user
- _build_prompt_context(user_context): Build detailed context for OpenAI prompt
- _parse_ai_response(response): Parse and validate OpenAI response

Design Principles:
- Leverages user behavioral signals and persona for context
- Generates recommendations with explicit rationales
- Maintains guardrails and tone validation
- Full auditability via trace JSONs
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ingest.constants import MANDATORY_DISCLAIMER
from guardrails.tone import scan_recommendations


# Logger
logger = logging.getLogger(__name__)

# Project root
_PROJECT_ROOT = Path(__file__).parent.parent


def generate_ai_recommendations(
    user_id: str,
    api_key: str,
    user_context: Optional[Dict[str, Any]] = None,
    model: str = "gpt-4o-mini",
    max_recommendations: int = 5,
) -> Dict[str, Any]:
    """
    Generate AI-powered recommendations for a user using OpenAI.

    Args:
        user_id: User identifier
        api_key: OpenAI API key
        user_context: Optional pre-loaded user context (if None, will load)
        model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
        max_recommendations: Maximum number of recommendations to generate

    Returns:
        Dictionary containing:
        - user_id
        - persona
        - recommendations: List of AI-generated recommendations
        - metadata: generation details, token usage, etc.
    """
    if not OPENAI_AVAILABLE:
        return {
            "user_id": user_id,
            "persona": None,
            "recommendations": [],
            "metadata": {
                "error": "OpenAI library not installed. Run: uv pip install openai",
                "timestamp": datetime.now().isoformat(),
            },
        }

    if not api_key:
        return {
            "user_id": user_id,
            "persona": None,
            "recommendations": [],
            "metadata": {
                "error": "OpenAI API key not provided",
                "timestamp": datetime.now().isoformat(),
            },
        }

    # Load user context if not provided
    if user_context is None:
        from recommend.engine import _load_user_context
        user_context = _load_user_context(user_id)

    # Check consent
    if not user_context.get("consent_granted", False):
        return {
            "user_id": user_id,
            "persona": user_context.get("persona"),
            "recommendations": [],
            "metadata": {
                "error": "User has not granted consent",
                "timestamp": datetime.now().isoformat(),
            },
        }

    # Build prompt context
    prompt_context = _build_prompt_context(user_context, max_recommendations)

    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        return {
            "user_id": user_id,
            "persona": user_context.get("persona"),
            "recommendations": [],
            "metadata": {
                "error": f"Failed to initialize OpenAI client: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            },
        }

    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": _get_system_prompt(),
                },
                {
                    "role": "user",
                    "content": prompt_context,
                },
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        # Parse response
        ai_response = json.loads(response.choices[0].message.content)
        recommendations = _parse_ai_response(ai_response, user_context)

        # Apply tone validation
        tone_scan = scan_recommendations(recommendations)
        if not tone_scan["passed"]:
            logger.warning(f"AI recommendations for {user_id} failed tone check")

        # Append disclaimer
        for rec in recommendations:
            rec["disclaimer"] = MANDATORY_DISCLAIMER

        # Build response
        return {
            "user_id": user_id,
            "persona": user_context.get("persona"),
            "recommendations": recommendations,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "total_count": len(recommendations),
                "tone_check_passed": tone_scan["passed"],
                "tone_violations_count": tone_scan.get("violations_found", 0),
                "token_usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "source": "ai_generated",
            },
        }

    except Exception as e:
        logger.error(f"OpenAI API call failed for user {user_id}: {e}")
        return {
            "user_id": user_id,
            "persona": user_context.get("persona"),
            "recommendations": [],
            "metadata": {
                "error": f"OpenAI API call failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            },
        }


def _get_system_prompt() -> str:
    """
    Get the system prompt for OpenAI that defines behavior and constraints.
    """
    return """You are a financial education assistant for SpendSense, an explainable financial behavior analysis system.

Your role is to generate personalized, educational financial recommendations based on user behavioral data.

CRITICAL CONSTRAINTS:
1. Educational Focus: Provide educational content, NOT financial advice
2. Transparency: Every recommendation MUST include a "rationale" that cites specific user data
3. Tone: Use encouraging, supportive language. NEVER use shaming language like "overspending", "bad habits", "lack discipline"
4. Data-Driven: Base recommendations on actual user signals provided in the context
5. Persona-Aligned: Tailor recommendations to the user's assigned behavioral persona

REQUIRED OUTPUT FORMAT (JSON):
{
  "recommendations": [
    {
      "title": "Clear, actionable title",
      "description": "2-3 sentence description of the recommendation",
      "category": "one of: credit_basics, debt_paydown, subscription_management, savings_optimization, budgeting, emergency_fund",
      "type": "education or partner_offer",
      "rationale": "Explicit 'because' statement citing concrete user data (e.g., 'Your Visa card ending in 4523 is at 68% utilization')"
    }
  ]
}

TONE GUIDELINES:
✅ DO USE: "consider reducing", "optimize your spending", "you're making progress", "opportunity to save"
❌ NEVER USE: "overspending", "bad habits", "lack discipline", "wasteful", "irresponsible"

Your recommendations should empower users with knowledge and actionable insights."""


def _build_prompt_context(user_context: Dict[str, Any], max_recommendations: int) -> str:
    """
    Build detailed context for the OpenAI prompt.

    Args:
        user_context: Full user context with signals, persona, accounts
        max_recommendations: Maximum number of recommendations to request

    Returns:
        Formatted prompt string with user context
    """
    persona = user_context.get("persona", "general")
    signals = user_context.get("signals", {})
    accounts = user_context.get("accounts", [])

    # Build persona description
    persona_descriptions = {
        "high_utilization": "User with high credit utilization (≥50%) or carrying interest charges",
        "variable_income_budgeter": "User with irregular income and low cash buffer",
        "subscription_heavy": "User with multiple recurring subscriptions",
        "cash_flow_optimizer": "User with low cash buffer, stable income, poor savings accumulation",
        "savings_builder": "User with positive savings growth and low credit utilization",
        "general": "User with minimal behavioral signals",
    }

    prompt = f"""Generate {max_recommendations} personalized financial education recommendations for this user.

USER PROFILE:
- Persona: {persona.replace('_', ' ').title()}
- Description: {persona_descriptions.get(persona, 'General user')}
- Age: {user_context.get('age', 'N/A')}
- Income Tier: {user_context.get('income_tier', 'unknown').title()}
- Region: {user_context.get('region', 'N/A')}

BEHAVIORAL SIGNALS:
"""

    # Add credit signals
    if any(k.startswith("credit_") for k in signals.keys()):
        prompt += "\nCredit Signals:\n"
        prompt += f"- Average Utilization: {signals.get('credit_avg_util_pct', 0):.1f}%\n"
        prompt += f"- Maximum Utilization: {signals.get('credit_max_util_pct', 0):.1f}%\n"
        prompt += f"- Number of Cards: {int(signals.get('credit_num_cards', 0))}\n"

        # Add specific card details
        credit_cards = [a for a in accounts if a.get("account_type") == "credit"]
        if credit_cards:
            prompt += "\nCredit Cards:\n"
            for card in credit_cards[:3]:  # Limit to 3 cards
                mask = card.get("mask", "XXXX")
                balance = card.get("balance_current", 0)
                limit = card.get("balance_limit", 1)
                util = (balance / limit * 100) if limit > 0 else 0
                prompt += f"- {card.get('account_subtype', 'Card')} ending in {mask}: ${balance:,.0f} / ${limit:,.0f} ({util:.0f}% utilization)\n"

    # Add subscription signals
    if any(k.startswith("sub_") for k in signals.keys()):
        prompt += "\nSubscription Signals:\n"
        prompt += f"- Recurring Subscriptions (180d): {int(signals.get('sub_180d_recurring_count', 0))}\n"
        prompt += f"- Monthly Recurring Spend: ${signals.get('sub_180d_monthly_spend', 0):,.0f}\n"
        prompt += f"- Subscription Share of Spending: {signals.get('sub_180d_share_pct', 0):.1f}%\n"

    # Add savings signals
    if any(k.startswith("sav_") for k in signals.keys()):
        prompt += "\nSavings Signals:\n"
        prompt += f"- Net Inflow (180d): ${signals.get('sav_180d_net_inflow', 0):,.0f}\n"
        prompt += f"- Growth Rate: {signals.get('sav_180d_growth_rate_pct', 0):.1f}%\n"
        prompt += f"- Emergency Fund: {signals.get('sav_180d_emergency_fund_months', 0):.1f} months\n"

    # Add income signals
    if any(k.startswith("inc_") for k in signals.keys()):
        prompt += "\nIncome Signals:\n"
        prompt += f"- Median Pay Gap: {int(signals.get('inc_180d_median_pay_gap_days', 0))} days\n"
        prompt += f"- Cash Buffer: {signals.get('inc_180d_cash_buffer_months', 0):.1f} months\n"
        prompt += f"- Average Paycheck: ${signals.get('inc_180d_avg_paycheck', 0):,.0f}\n"

    prompt += f"""
TASK:
Generate {max_recommendations} educational recommendations that:
1. Are relevant to the user's persona and behavioral signals
2. Include specific rationales citing the data above
3. Use encouraging, supportive tone
4. Provide actionable educational insights

Return your response as a JSON object with a "recommendations" array."""

    return prompt


def _parse_ai_response(ai_response: Dict[str, Any], user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse and validate OpenAI response.

    Args:
        ai_response: Parsed JSON from OpenAI
        user_context: User context for validation

    Returns:
        List of validated recommendation dicts
    """
    recommendations = []

    raw_recs = ai_response.get("recommendations", [])

    for rec in raw_recs:
        # Validate required fields
        if not all(k in rec for k in ["title", "description", "rationale"]):
            logger.warning(f"Skipping AI recommendation missing required fields: {rec}")
            continue

        # Build recommendation dict
        validated_rec = {
            "type": rec.get("type", "education"),
            "title": rec.get("title", "").strip(),
            "description": rec.get("description", "").strip(),
            "category": rec.get("category", "general"),
            "topic": rec.get("topic", "general"),
            "rationale": rec.get("rationale", "").strip(),
        }

        # Ensure rationale includes concrete data
        if not validated_rec["rationale"]:
            validated_rec["rationale"] = f"Based on your {user_context.get('persona', 'general').replace('_', ' ')} profile"

        recommendations.append(validated_rec)

    return recommendations

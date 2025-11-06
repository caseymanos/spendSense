"""
Image Prompt Templates for Educational Infographics

Defines visual specifications and prompt templates for generating
educational financial infographics using DALL-E 3. Each template includes:
- Visual description (layout, elements, style, mood)
- Size and quality specifications
- Tone guidelines
- Topic tags

Templates are organized by persona and topic for easy lookup.
Previously used for SORA video generation, adapted for static images.
"""

from typing import Dict, Any


# =============================================================================
# PROMPT TEMPLATES BY PERSONA
# =============================================================================

PROMPT_TEMPLATES = {
    "high_utilization": {
        "credit_utilization": {
            "visual_description": """
Create a modern, educational infographic about credit card utilization.

Layout (vertical orientation, 1024×1024):
- Top section (15%): Credit card icon with "Card ending in {card_mask}" label
- Middle section (55%): Large circular progress meter/gauge
  - Current utilization: {utilization_pct}% shown prominently in red zone (#EF4444)
  - Target zone: 30% marked with green indicator (#22C55E)
  - Color gradient zones: Red (50%+), Yellow (#FBBF24, 30-50%), Green (<30%)
  - Clear percentage numbers labeled
  - Meter styled like modern fintech app UI
- Bottom left (15%): "Credit Score Impact" callout box
  - Shows "650 → 720" with upward arrow icon
  - Green checkmark indicating improvement
- Bottom right (15%): Key message box with bold text
  - "Below 30% = Better Score"

Visual Style:
- Clean, minimalist flat design (banking app aesthetic)
- Professional color palette: Red #EF4444, Yellow #FBBF24, Green #22C55E, Navy #1E3A8A for text
- Modern sans-serif typography (medium weight for readability)
- No human characters or faces (accessibility first)
- Generous white space for clarity
- Subtle shadows/depth for visual hierarchy
- Think Mint.com or NerdWallet design aesthetic

Mood: Educational, empowering, supportive, hopeful
Visual tone: Professional but approachable, calm not alarming
Avoid: Aggressive visuals, warning symbols, scary imagery, shame-inducing language
""",
            "size": "1024x1024",
            "quality": "standard",
            "tone": "supportive, educational, empowering",
            "tags": ["credit", "utilization", "debt_reduction", "credit_score"]
        },

        "debt_paydown_strategy": {
            "visual_description": """
Create an educational infographic explaining the debt avalanche paydown strategy.

Layout (vertical orientation, 1024×1024):
- Title section (10%): "Avalanche Method: Highest Interest First"
- Main visual (60%): Side-by-side comparison layout
  - Left card: Card A with {balance_high} balance, labeled "High Interest" in amber (#F59E0B)
  - Right card: Card B with {balance_low} balance, labeled "Low Interest" in blue (#3B82F6)
  - Large arrow pointing from wallet icon to Card A (priority indicator)
  - Each card shows interest rate and monthly payment
- Bottom section (30%): Results callout
  - "Interest Saved" box with dollar amount
  - "Time Saved" box with month count
  - Green checkmarks indicating benefits

Visual Style:
- Split layout with clear visual hierarchy
- Color coding: Amber for high priority, Blue for lower priority, Green (#22C55E) for savings
- Clean card representations with payment flow indicators
- Modern fintech design aesthetic
- Icons: wallet, credit cards, arrows, checkmarks
- Sans-serif typography, clear labeling

Mood: Strategic, clear, motivating, action-oriented
Visual tone: Logical and systematic, empowering through knowledge
Avoid: Overwhelming complexity, judgment of debt situations
""",
            "size": "1024x1024",
            "quality": "standard",
            "tone": "strategic, clear, action-oriented",
            "tags": ["debt", "strategy", "interest", "paydown"]
        }
    },

    "variable_income": {
        "emergency_fund": {
            "visual_description": """
Create a modern, educational infographic about emergency fund building for variable income.

Layout (vertical orientation, 1024×1024):
- Top section (20%): Title "Emergency Fund for Variable Income"
  - Subtitle: "Protect Against Income Fluctuations"
- Middle section (55%): Central visual metaphor
  - Left side: Wavy line graph showing variable monthly income
    - Different bar heights representing income variability
    - Color gradient: Blue (#3B82F6) for highs, Teal (#14B8A6) for lows
  - Right side: Large transparent jar/container
    - Shows "fill level" at 3-month mark (50% full)
    - Shield icon overlaid on jar indicating protection
    - Progress labels: "1 month", "3 months", "6 months" (target)
  - Arrow flowing from income graph to jar
- Bottom section (25%): Two callout boxes side-by-side
  - Left box: "Variable Income?" with wave icon
  - Right box: "3-6 Months = Safety Net" with checkmark

Visual Style:
- Ocean wave metaphor for income variability
- Transparent/translucent jar showing liquid fill level
- Calming blue (#3B82F6) and teal (#14B8A6) color palette
- Modern sans-serif typography
- Clean, minimalist design with generous white space
- Icons: waves, shield, checkmark, jar/container

Mood: Reassuring, protective, achievable, supportive
Visual tone: Calm and steady (countering income anxiety)
Avoid: Alarming imagery, stress-inducing visuals
""",
            "size": "1024x1024",
            "quality": "standard",
            "tone": "reassuring, protective, achievable",
            "tags": ["savings", "emergency_fund", "variable_income", "budgeting"]
        }
    },

    "subscription_heavy": {
        "subscription_audit": {
            "visual_description": """
Create a modern, educational infographic about subscription management and optimization.

Layout (vertical orientation, 1024×1024):
- Top section (15%): Title "Subscription Audit"
  - Subtitle: "Find Hidden Savings in Recurring Charges"
- Middle section (60%): Two-column comparison
  - Left column (labeled "Current"): Grid of 8-10 subscription icons
    - App-style colorful icons (streaming, gym, software, etc.)
    - Each icon has price tag underneath
    - Total shown at bottom in red (#EF4444): "$XXX/month"
  - Center divider: Large arrow pointing right with "Optimize" label
  - Right column (labeled "Optimized"): Reduced grid
    - 3-4 icons faded/grayed out (cancelled subscriptions)
    - Remaining active subscriptions highlighted
    - Total shown at bottom in green (#22C55E): "$YYY/month"
- Bottom section (25%): Savings callout box
  - Piggy bank icon
  - "${monthly_savings}/month Saved" in large bold text
  - Sparkle/star accents around savings amount
  - Subtext: "Redirect to savings or debt paydown"

Visual Style:
- Colorful, recognizable app-style subscription icons
- Price tags in clean sans-serif typography
- Visual distinction: Active (full color) vs Cancelled (grayed/faded)
- Green (#22C55E) for savings, Red (#EF4444) for current cost
- Modern fintech aesthetic with card-based layout
- Icons: streaming services, gym, software, piggy bank

Mood: Eye-opening, empowering, actionable, motivating
Visual tone: Practical and achievement-focused
Avoid: Judgment about subscription choices
""",
            "size": "1024x1024",
            "quality": "standard",
            "tone": "eye-opening, empowering, actionable",
            "tags": ["subscriptions", "recurring", "optimization", "savings"]
        }
    },

    "savings_builder": {
        "automation": {
            "visual_description": """
Create a modern, educational infographic about automated savings strategies.

Layout (vertical orientation, 1024×1024):
- Top section (15%): Title "Automate Your Savings"
  - Subtitle: "Save First, Spend Second"
- Middle section (60%): Flow diagram showing automation
  - Left element: Paycheck representation
    - Envelope or direct deposit icon
    - Dollar amount shown
  - Center flow: Automatic split visualization
    - Dotted/dashed path line showing 10% splitting off
    - "Auto Transfer" label on path
    - Calculator/gear icon indicating automation
  - Right element split into two accounts:
    - Upper account (30%): Savings account
      - Shows balance increasing
      - Progress bar with "10% saved" label
      - Green (#22C55E) color theme
    - Lower account (70%): Checking account
      - Shows remaining 90%
      - Blue (#3B82F6) color theme
- Bottom section (25%): Benefits callout boxes (3 side-by-side)
  - Box 1: "Set & Forget" with automation icon
  - Box 2: "Consistent Growth" with upward trend arrow
  - Box 3: "Reach Goals Faster" with target/bullseye icon

Visual Style:
- Clean, modern banking interface aesthetic
- Flow diagram with clear directional indicators
- Dotted/dashed lines for automated transfers
- Progress bars with percentage labels
- Soft green (#22C55E) and blue (#3B82F6) color scheme
- Professional typography with clear hierarchy
- Icons: envelope, calculator/gear, progress bars, arrows

Mood: Effortless, smart, forward-thinking, empowering
Visual tone: Simple and achievable (emphasizing ease of automation)
Avoid: Complexity that undermines "effortless" message
""",
            "size": "1024x1024",
            "quality": "standard",
            "tone": "effortless, smart, forward-thinking",
            "tags": ["automation", "savings", "habit", "goals"]
        }
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def build_image_prompt(topic: str, persona: str, user_context: Dict[str, Any]) -> str:
    """
    Build DALL-E 3 image prompt by merging template with user data.

    Args:
        topic: Topic identifier (e.g., "credit_utilization")
        persona: Persona identifier (e.g., "high_utilization")
        user_context: Dict with user-specific data for interpolation
            - credit_max_util_pct: Credit utilization percentage
            - card_mask: Last 4 digits of credit card
            - balance_high: Highest balance
            - balance_low: Lowest balance
            - monthly_savings: Potential monthly savings

    Returns:
        Formatted prompt string ready for DALL-E 3 API

    Raises:
        ValueError: If template not found for persona/topic combination

    Example:
        prompt = build_image_prompt(
            topic="credit_utilization",
            persona="high_utilization",
            user_context={"credit_max_util_pct": 73.5, "card_mask": "4523"}
        )
    """
    # Lookup template
    template = PROMPT_TEMPLATES.get(persona, {}).get(topic)
    if not template:
        raise ValueError(f"No template found for persona='{persona}', topic='{topic}'")

    # Extract visual description
    visual_desc = template["visual_description"]

    # Inject user-specific data
    prompt = visual_desc.format(
        utilization_pct=int(user_context.get("credit_max_util_pct", 50)),
        card_mask=user_context.get("card_mask", "XXXX"),
        balance_high=user_context.get("balance_high", "$5,000"),
        balance_low=user_context.get("balance_low", "$1,200"),
        monthly_savings=user_context.get("monthly_savings", "$45")
    )

    return prompt


def get_template_metadata(topic: str, persona: str) -> Dict[str, Any]:
    """
    Get template metadata without building full prompt.

    Useful for checking size, quality, tone, tags before generation.

    Args:
        topic: Topic identifier
        persona: Persona identifier

    Returns:
        Dict with size, quality, tone, tags

    Raises:
        ValueError: If template not found
    """
    template = PROMPT_TEMPLATES.get(persona, {}).get(topic)
    if not template:
        raise ValueError(f"No template found for persona='{persona}', topic='{topic}'")

    return {
        "size": template["size"],
        "quality": template["quality"],
        "tone": template["tone"],
        "tags": template["tags"]
    }


def list_available_templates() -> Dict[str, list]:
    """
    List all available templates by persona.

    Returns:
        Dict mapping persona to list of available topics
    """
    return {
        persona: list(topics.keys())
        for persona, topics in PROMPT_TEMPLATES.items()
    }

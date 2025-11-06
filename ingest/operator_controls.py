"""
Operator controls for synthetic data generation.
Allows granular manipulation of behavioral patterns and persona distributions.
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class PersonaTarget(str, Enum):
    """Personas available for targeted generation"""
    HIGH_UTILIZATION = "High Utilization"
    VARIABLE_INCOME = "Variable Income Budgeter"
    SUBSCRIPTION_HEAVY = "Subscription-Heavy"
    CASH_FLOW_OPTIMIZER = "Cash Flow Optimizer"
    SAVINGS_BUILDER = "Savings Builder"
    GENERAL = "General"


class PayrollPattern(str, Enum):
    """Payroll frequency patterns"""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    IRREGULAR = "irregular"


class CreditUtilizationTier(str, Enum):
    """Credit utilization tiers"""
    LOW = "low"  # < 30%
    MEDIUM = "medium"  # 30-50%
    HIGH = "high"  # 50-80%
    CRITICAL = "critical"  # > 80%


class OperatorControls(BaseModel):
    """
    Operator-controlled parameters for data generation.
    Allows fine-grained control over behavioral patterns and distributions.
    """

    # =============================================================================
    # PERSONA TARGETING
    # =============================================================================

    target_personas: List[PersonaTarget] = Field(
        default_factory=list,
        description="List of personas to skew generation towards (empty = natural distribution)"
    )

    persona_weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Custom weights for each persona (must sum to 1.0). If None, equal weights used."
    )

    # =============================================================================
    # PAYROLL & INCOME PATTERNS
    # =============================================================================

    payroll_pattern_distribution: Dict[str, float] = Field(
        default={
            "weekly": 0.15,
            "biweekly": 0.30,
            "monthly": 0.25,
            "irregular": 0.30,
        },
        description="Distribution of payroll patterns (must sum to 1.0)"
    )

    irregular_income_volatility: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Volatility factor for irregular income (0=stable, 1=highly variable)"
    )

    # =============================================================================
    # CREDIT UTILIZATION DISTRIBUTION
    # =============================================================================

    credit_utilization_distribution: Dict[str, float] = Field(
        default={
            "low": 0.40,  # < 30%
            "medium": 0.35,  # 30-50%
            "high": 0.20,  # 50-80%
            "critical": 0.05,  # > 80%
        },
        description="Distribution of credit utilization tiers (must sum to 1.0)"
    )

    overdue_probability: float = Field(
        default=0.15,
        ge=0.0,
        le=1.0,
        description="Probability a high-utilization account is overdue"
    )

    min_payment_only_probability: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="Probability of min-payment-only behavior for high utilization"
    )

    # =============================================================================
    # SUBSCRIPTION PATTERNS
    # =============================================================================

    subscription_adoption_rate: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Percentage of users with recurring subscriptions"
    )

    subscription_count_min: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Minimum number of subscriptions for subscription-heavy users"
    )

    subscription_count_max: int = Field(
        default=6,
        ge=1,
        le=15,
        description="Maximum number of subscriptions for subscription-heavy users"
    )

    subscription_monthly_spend_range: tuple[float, float] = Field(
        default=(30.0, 150.0),
        description="Range of monthly subscription spend for heavy users"
    )

    # =============================================================================
    # SAVINGS BEHAVIOR
    # =============================================================================

    savings_adoption_rate: float = Field(
        default=0.40,
        ge=0.0,
        le=1.0,
        description="Percentage of users with regular savings transfers"
    )

    savings_transfer_range: tuple[float, float] = Field(
        default=(100.0, 400.0),
        description="Range of monthly savings transfer amounts"
    )

    savings_growth_target_pct: float = Field(
        default=5.0,
        ge=0.0,
        le=50.0,
        description="Target savings growth rate (%) over 6 months for savings builders"
    )

    # =============================================================================
    # SPENDING PATTERNS
    # =============================================================================

    high_spender_probability: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="Probability a user is a high spender (1.5x transactions)"
    )

    transaction_volatility: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Volatility in transaction amounts (0=fixed, 1=highly variable)"
    )

    # =============================================================================
    # ACCOUNT STRUCTURE
    # =============================================================================

    accounts_per_user_distribution: Dict[str, float] = Field(
        default={
            "2": 0.25,  # Checking + Savings only
            "3": 0.50,  # + 1 credit card
            "4": 0.25,  # + 2 credit cards
        },
        description="Distribution of account counts per user"
    )

    credit_card_probability: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Probability a user has at least one credit card"
    )

    # =============================================================================
    # DATA VOLUME
    # =============================================================================

    transaction_multiplier: float = Field(
        default=1.0,
        ge=0.5,
        le=3.0,
        description="Multiplier for transaction volume (1.0 = default, 2.0 = double)"
    )

    @field_validator("payroll_pattern_distribution")
    @classmethod
    def validate_payroll_distribution(cls, v):
        total = sum(v.values())
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            raise ValueError(f"Payroll pattern distribution must sum to 1.0 (got {total})")
        return v

    @field_validator("credit_utilization_distribution")
    @classmethod
    def validate_credit_distribution(cls, v):
        total = sum(v.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Credit utilization distribution must sum to 1.0 (got {total})")
        return v

    @field_validator("accounts_per_user_distribution")
    @classmethod
    def validate_accounts_distribution(cls, v):
        total = sum(v.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Accounts distribution must sum to 1.0 (got {total})")
        return v

    @field_validator("persona_weights")
    @classmethod
    def validate_persona_weights(cls, v):
        if v is not None:
            total = sum(v.values())
            if not (0.99 <= total <= 1.01):
                raise ValueError(f"Persona weights must sum to 1.0 (got {total})")
        return v

    def get_persona_distribution_target(self, num_users: int) -> Dict[str, int]:
        """
        Calculate target user counts for each persona based on weights.

        Args:
            num_users: Total number of users to generate

        Returns:
            Dict mapping persona name to target user count
        """
        if not self.target_personas:
            # Natural distribution - return empty dict
            return {}

        # Use custom weights if provided, otherwise equal distribution
        if self.persona_weights:
            weights = self.persona_weights
        else:
            # Equal weights across selected personas
            weight = 1.0 / len(self.target_personas)
            weights = {p.value: weight for p in self.target_personas}

        # Calculate target counts
        distribution = {}
        remaining = num_users

        # Sort by weight descending to allocate largest first
        sorted_personas = sorted(weights.items(), key=lambda x: x[1], reverse=True)

        for i, (persona, weight) in enumerate(sorted_personas):
            if i == len(sorted_personas) - 1:
                # Last persona gets remaining users
                distribution[persona] = remaining
            else:
                count = int(num_users * weight)
                distribution[persona] = count
                remaining -= count

        return distribution

    def to_display_dict(self) -> Dict:
        """Convert to display-friendly dictionary for UI"""
        return {
            "Persona Targeting": {
                "Target Personas": [p.value for p in self.target_personas] if self.target_personas else "Natural Distribution",
                "Custom Weights": self.persona_weights or "Equal Distribution"
            },
            "Income Patterns": {
                "Payroll Distribution": self.payroll_pattern_distribution,
                "Irregular Income Volatility": f"{self.irregular_income_volatility:.1%}"
            },
            "Credit Behavior": {
                "Utilization Distribution": self.credit_utilization_distribution,
                "Overdue Probability": f"{self.overdue_probability:.1%}",
                "Min Payment Only": f"{self.min_payment_only_probability:.1%}"
            },
            "Subscriptions": {
                "Adoption Rate": f"{self.subscription_adoption_rate:.1%}",
                "Count Range": f"{self.subscription_count_min}-{self.subscription_count_max}",
                "Monthly Spend": f"${self.subscription_monthly_spend_range[0]:.0f}-${self.subscription_monthly_spend_range[1]:.0f}"
            },
            "Savings": {
                "Adoption Rate": f"{self.savings_adoption_rate:.1%}",
                "Transfer Range": f"${self.savings_transfer_range[0]:.0f}-${self.savings_transfer_range[1]:.0f}",
                "Growth Target": f"{self.savings_growth_target_pct:.1f}%"
            },
            "Spending": {
                "High Spender Probability": f"{self.high_spender_probability:.1%}",
                "Transaction Volatility": f"{self.transaction_volatility:.1%}",
                "Transaction Multiplier": f"{self.transaction_multiplier:.1f}x"
            },
            "Account Structure": {
                "Accounts Distribution": self.accounts_per_user_distribution,
                "Credit Card Probability": f"{self.credit_card_probability:.1%}"
            }
        }


# Preset configurations for common testing scenarios
PRESET_CONFIGS = {
    "default": OperatorControls(),

    "high_utilization_focus": OperatorControls(
        target_personas=[PersonaTarget.HIGH_UTILIZATION],
        credit_utilization_distribution={
            "low": 0.10,
            "medium": 0.15,
            "high": 0.40,
            "critical": 0.35,
        },
        overdue_probability=0.40,
        min_payment_only_probability=0.60,
    ),

    "variable_income_focus": OperatorControls(
        target_personas=[PersonaTarget.VARIABLE_INCOME],
        payroll_pattern_distribution={
            "weekly": 0.05,
            "biweekly": 0.10,
            "monthly": 0.15,
            "irregular": 0.70,
        },
        irregular_income_volatility=0.8,
        savings_adoption_rate=0.20,  # Lower savings for income instability
    ),

    "subscription_heavy_focus": OperatorControls(
        target_personas=[PersonaTarget.SUBSCRIPTION_HEAVY],
        subscription_adoption_rate=0.90,
        subscription_count_min=5,
        subscription_count_max=12,
        subscription_monthly_spend_range=(75.0, 250.0),
    ),

    "savings_builder_focus": OperatorControls(
        target_personas=[PersonaTarget.SAVINGS_BUILDER],
        savings_adoption_rate=0.95,
        savings_transfer_range=(200.0, 800.0),
        savings_growth_target_pct=10.0,
        credit_utilization_distribution={
            "low": 0.80,
            "medium": 0.15,
            "high": 0.05,
            "critical": 0.00,
        },
    ),

    "overlap_testing": OperatorControls(
        target_personas=[
            PersonaTarget.HIGH_UTILIZATION,
            PersonaTarget.SUBSCRIPTION_HEAVY,
            PersonaTarget.VARIABLE_INCOME,
        ],
        persona_weights={
            "High Utilization": 0.40,
            "Subscription-Heavy": 0.35,
            "Variable Income Budgeter": 0.25,
        },
        # Mix of behaviors to create overlaps
        subscription_adoption_rate=0.85,
        credit_utilization_distribution={
            "low": 0.15,
            "medium": 0.25,
            "high": 0.35,
            "critical": 0.25,
        },
        payroll_pattern_distribution={
            "weekly": 0.10,
            "biweekly": 0.20,
            "monthly": 0.30,
            "irregular": 0.40,
        },
    ),
    "cash_flow_optimizer_focus": OperatorControls(
        target_personas=[PersonaTarget.CASH_FLOW_OPTIMIZER],
        # Stable income pattern (differentiates from Variable Income)
        payroll_pattern_distribution={
            "weekly": 0.20,
            "biweekly": 0.50,  # Most common
            "monthly": 0.25,
            "irregular": 0.05,  # Very low - stable income is key
        },
        irregular_income_volatility=0.2,  # Low volatility
        # Very low savings activity - need low cash buffer
        savings_adoption_rate=0.15,  # Very low - many users won't save at all
        savings_transfer_range=(20.0, 80.0),  # Minimal transfers when they do save
        savings_growth_target_pct=0.1,  # Near-zero growth - minimal savings accumulation
        # High spending to drain cash reserves
        high_spender_probability=0.75,  # Most users are high spenders
        # Moderate credit utilization (not the primary concern)
        credit_utilization_distribution={
            "low": 0.50,
            "medium": 0.30,
            "high": 0.15,
            "critical": 0.05,
        },
        # Normal subscription behavior
        subscription_adoption_rate=0.50,  # Default level
        subscription_count_min=2,
        subscription_count_max=5,
    ),
}

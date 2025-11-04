"""
Data schemas for SpendSense MVP V2.
Plaid-compatible schema definitions using Pydantic.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# Enums for categorical fields
class AccountType(str, Enum):
    """Plaid account types"""
    DEPOSITORY = "depository"
    CREDIT = "credit"
    LOAN = "loan"
    INVESTMENT = "investment"


class AccountSubtype(str, Enum):
    """Plaid account subtypes"""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit card"
    PAYPAL = "paypal"


class PaymentChannel(str, Enum):
    """Transaction payment channels"""
    ONLINE = "online"
    IN_STORE = "in store"
    OTHER = "other"


class Gender(str, Enum):
    """Gender categories for fairness metrics"""
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class IncomeTier(str, Enum):
    """Income tiers for fairness analysis"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Region(str, Enum):
    """US regions for fairness analysis"""
    NORTHEAST = "northeast"
    SOUTH = "south"
    MIDWEST = "midwest"
    WEST = "west"


# Core data models
class User(BaseModel):
    """User profile with consent and demographic data"""
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User full name (synthetic)")
    consent_granted: bool = Field(default=False, description="Data processing consent flag")
    consent_timestamp: Optional[datetime] = Field(None, description="When consent was granted")
    revoked_timestamp: Optional[datetime] = Field(None, description="When consent was revoked")

    # Demographic fields (for fairness metrics only, not used in persona logic)
    age: int = Field(..., ge=18, le=100, description="User age")
    gender: Gender = Field(..., description="User gender")
    income_tier: IncomeTier = Field(..., description="Income tier")
    region: Region = Field(..., description="US region")
    created_at: datetime = Field(default_factory=datetime.now, description="Record creation time")

    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if not 18 <= v <= 100:
            raise ValueError("Age must be between 18 and 100")
        return v


class Account(BaseModel):
    """Bank account (Plaid-style)"""
    account_id: str = Field(..., description="Unique account identifier")
    user_id: str = Field(..., description="Owner user ID")
    account_type: AccountType = Field(..., description="Account type")
    account_subtype: AccountSubtype = Field(..., description="Account subtype")

    # Balances
    balance_current: float = Field(..., description="Current balance")
    balance_available: Optional[float] = Field(None, description="Available balance")
    balance_limit: Optional[float] = Field(None, description="Credit limit (if applicable)")

    # Metadata
    iso_currency_code: str = Field(default="USD", description="Currency code")
    holder_category: Literal["consumer", "business"] = Field(default="consumer")
    mask: str = Field(..., description="Last 4 digits of account number")
    name: str = Field(..., description="Account display name")
    official_name: Optional[str] = Field(None, description="Official institution name")

    @field_validator('balance_current')
    @classmethod
    def validate_balance(cls, v):
        if v < -100000 or v > 1000000:
            raise ValueError("Balance must be between -$100k and $1M")
        return v


class Transaction(BaseModel):
    """Financial transaction (Plaid-style)"""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    account_id: str = Field(..., description="Associated account ID")

    # Transaction details
    date: datetime = Field(..., description="Transaction date")
    amount: float = Field(..., description="Transaction amount (positive = debit, negative = credit)")
    merchant_name: str = Field(..., description="Merchant name")
    payment_channel: PaymentChannel = Field(..., description="Payment channel")

    # Categorization
    personal_finance_category: str = Field(..., description="Transaction category")
    personal_finance_subcategory: Optional[str] = Field(None, description="Transaction subcategory")

    # Status
    pending: bool = Field(default=False, description="Is transaction pending")

    # Additional metadata
    location_city: Optional[str] = Field(None, description="Transaction city")
    location_state: Optional[str] = Field(None, description="Transaction state")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if abs(v) > 50000:
            raise ValueError("Transaction amount exceeds reasonable limit ($50k)")
        return v


class Liability(BaseModel):
    """Credit account liability information"""
    liability_id: str = Field(..., description="Unique liability identifier")
    account_id: str = Field(..., description="Associated account ID")
    user_id: str = Field(..., description="Owner user ID")

    # Credit terms
    apr: float = Field(..., ge=0, le=100, description="Annual Percentage Rate")
    minimum_payment: float = Field(..., ge=0, description="Minimum payment amount")

    # Payment history
    last_payment_amount: Optional[float] = Field(None, description="Last payment amount")
    last_payment_date: Optional[datetime] = Field(None, description="Last payment date")
    next_due_date: Optional[datetime] = Field(None, description="Next payment due date")

    # Status flags
    is_overdue: bool = Field(default=False, description="Is payment overdue")
    overdue_amount: Optional[float] = Field(None, description="Amount overdue")

    @field_validator('apr')
    @classmethod
    def validate_apr(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("APR must be between 0 and 100")
        return v


class DataGenerationConfig(BaseModel):
    """Configuration for synthetic data generation"""
    seed: int = Field(default=42, description="Random seed for reproducibility")
    num_users: int = Field(default=100, ge=10, le=1000, description="Number of users to generate")
    months_history: int = Field(default=6, ge=1, le=24, description="Months of transaction history")
    avg_transactions_per_month: int = Field(default=30, ge=10, le=100, description="Average transactions per user per month")
    generation_timestamp: datetime = Field(default_factory=datetime.now, description="When data was generated")

    @field_validator('num_users')
    @classmethod
    def validate_num_users(cls, v):
        if not 10 <= v <= 1000:
            raise ValueError("Number of users must be between 10 and 1000")
        return v


# Category mappings for transaction generation
TRANSACTION_CATEGORIES = [
    ("FOOD_AND_DRINK", "Restaurants"),
    ("FOOD_AND_DRINK", "Groceries"),
    ("GENERAL_MERCHANDISE", "Superstores"),
    ("GENERAL_MERCHANDISE", "Online Marketplaces"),
    ("TRANSPORTATION", "Gas"),
    ("TRANSPORTATION", "Public Transit"),
    ("ENTERTAINMENT", "Streaming Services"),
    ("ENTERTAINMENT", "Movies and Music"),
    ("PERSONAL_CARE", "Gyms and Fitness"),
    ("GENERAL_SERVICES", "Subscription Services"),
    ("HOME_IMPROVEMENT", "Hardware"),
    ("MEDICAL", "Pharmacies"),
    ("INCOME", "Payroll"),
    ("TRANSFER_IN", "Deposit"),
    ("TRANSFER_OUT", "Transfer"),
]


# Merchant name lists for realistic generation
RECURRING_MERCHANTS = [
    "Netflix", "Spotify", "Amazon Prime", "Apple Music", "Hulu",
    "Disney+", "NYT Subscription", "WSJ", "LA Fitness", "Planet Fitness",
    "Adobe Creative Cloud", "Microsoft 365", "Dropbox", "LinkedIn Premium"
]

GROCERY_MERCHANTS = [
    "Whole Foods", "Trader Joe's", "Safeway", "Kroger", "Walmart Grocery",
    "Target", "Costco", "Sam's Club"
]

RESTAURANT_MERCHANTS = [
    "Chipotle", "Starbucks", "McDonald's", "Panera Bread", "Subway",
    "Chick-fil-A", "Taco Bell", "Olive Garden", "Cheesecake Factory"
]

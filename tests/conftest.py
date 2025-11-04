"""
Pytest configuration and shared fixtures for SpendSense tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from ingest.schemas import (
    User, Account, Transaction, Liability,
    AccountType, AccountSubtype, PaymentChannel,
    Gender, IncomeTier, Region, DataGenerationConfig
)


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return User(
        user_id="test_user_001",
        name="Test User",
        consent_granted=False,
        age=35,
        gender=Gender.MALE,
        income_tier=IncomeTier.MEDIUM,
        region=Region.WEST,
        created_at=datetime.now()
    )


@pytest.fixture
def sample_checking_account():
    """Create a sample checking account"""
    return Account(
        account_id="test_acc_001",
        user_id="test_user_001",
        account_type=AccountType.DEPOSITORY,
        account_subtype=AccountSubtype.CHECKING,
        balance_current=5000.0,
        mask="1234",
        name="Checking Account",
        official_name="Test Bank Checking"
    )


@pytest.fixture
def sample_credit_account():
    """Create a sample credit card account"""
    return Account(
        account_id="test_acc_002",
        user_id="test_user_001",
        account_type=AccountType.CREDIT,
        account_subtype=AccountSubtype.CREDIT_CARD,
        balance_current=3400.0,
        balance_available=1600.0,
        balance_limit=5000.0,
        mask="4523",
        name="Credit Card",
        official_name="Visa Test Bank"
    )


@pytest.fixture
def sample_transaction():
    """Create a sample transaction"""
    return Transaction(
        transaction_id="test_txn_001",
        account_id="test_acc_001",
        date=datetime.now() - timedelta(days=5),
        amount=15.99,
        merchant_name="Netflix",
        payment_channel=PaymentChannel.ONLINE,
        personal_finance_category="GENERAL_SERVICES",
        personal_finance_subcategory="Subscription Services",
        pending=False
    )


@pytest.fixture
def sample_liability():
    """Create a sample liability"""
    return Liability(
        liability_id="test_liab_001",
        account_id="test_acc_002",
        user_id="test_user_001",
        apr=18.99,
        minimum_payment=68.0,
        last_payment_amount=100.0,
        last_payment_date=datetime.now() - timedelta(days=15),
        next_due_date=datetime.now() + timedelta(days=15),
        is_overdue=False
    )


@pytest.fixture
def generation_config():
    """Create a data generation config for testing"""
    return DataGenerationConfig(
        seed=42,
        num_users=10,  # Small for fast tests
        months_history=6,
        avg_transactions_per_month=30
    )

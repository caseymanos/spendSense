"""
Unit and integration tests for data generation (PR #1).

Tests:
1. Schema validation
2. Deterministic generation
3. End-to-end pipeline
"""

import pytest
import json
import hashlib
from pathlib import Path
from datetime import datetime
from pydantic import ValidationError

from ingest.schemas import (
    User, Account, Transaction, Liability, DataGenerationConfig,
    AccountType, Gender, IncomeTier, Region
)
from ingest.data_generator import SyntheticDataGenerator
from ingest.validators import DataValidator
from ingest.loader import DataLoader


class TestSchemaValidation:
    """Test 1: Schema validation - Pydantic models enforce required fields and types"""

    def test_user_schema_valid(self, sample_user):
        """Valid user passes validation"""
        assert sample_user.user_id == "test_user_001"
        assert sample_user.consent_granted is False
        assert sample_user.age == 35

    def test_user_schema_missing_required_field(self):
        """Missing required field raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            User(
                user_id="test_user",
                # Missing 'name' field
                age=35,
                gender=Gender.MALE,
                income_tier=IncomeTier.MEDIUM,
                region=Region.WEST
            )
        assert "name" in str(exc_info.value).lower()

    def test_user_schema_invalid_age(self):
        """Age out of range raises ValidationError"""
        with pytest.raises(ValidationError):
            User(
                user_id="test_user",
                name="Test User",
                age=15,  # Below minimum 18
                gender=Gender.MALE,
                income_tier=IncomeTier.MEDIUM,
                region=Region.WEST
            )

    def test_account_schema_valid(self, sample_checking_account):
        """Valid account passes validation"""
        assert sample_checking_account.account_type == AccountType.DEPOSITORY
        assert sample_checking_account.balance_current == 5000.0

    def test_account_schema_invalid_balance(self):
        """Extremely large balance raises ValidationError"""
        with pytest.raises(ValidationError):
            Account(
                account_id="test_acc",
                user_id="test_user",
                account_type=AccountType.DEPOSITORY,
                account_subtype="checking",
                balance_current=2000000.0,  # Over $1M limit
                mask="1234",
                name="Test Account"
            )

    def test_transaction_schema_valid(self, sample_transaction):
        """Valid transaction passes validation"""
        assert sample_transaction.amount == 15.99
        assert sample_transaction.merchant_name == "Netflix"

    def test_transaction_schema_invalid_amount(self):
        """Extremely large amount raises ValidationError"""
        with pytest.raises(ValidationError):
            Transaction(
                transaction_id="test_txn",
                account_id="test_acc",
                date=datetime.now(),
                amount=100000.0,  # Over $50k limit
                merchant_name="Test Merchant",
                payment_channel="online",
                personal_finance_category="TEST"
            )

    def test_liability_schema_valid(self, sample_liability):
        """Valid liability passes validation"""
        assert sample_liability.apr == 18.99
        assert sample_liability.minimum_payment == 68.0

    def test_liability_schema_invalid_apr(self):
        """APR out of range raises ValidationError"""
        with pytest.raises(ValidationError):
            Liability(
                liability_id="test_liab",
                account_id="test_acc",
                user_id="test_user",
                apr=150.0,  # Over 100% limit
                minimum_payment=50.0
            )


class TestDeterministicGeneration:
    """Test 2: Deterministic generation - Identical output with seed=42"""

    def test_same_seed_produces_identical_users(self):
        """Two runs with seed=42 produce identical user data"""
        config1 = DataGenerationConfig(seed=42, num_users=10, months_history=1)
        config2 = DataGenerationConfig(seed=42, num_users=10, months_history=1)

        gen1 = SyntheticDataGenerator(config1)
        gen2 = SyntheticDataGenerator(config2)

        users1 = gen1.generate_users()
        users2 = gen2.generate_users()

        # Compare serialized data
        users1_json = [u.model_dump(mode='json') for u in users1]
        users2_json = [u.model_dump(mode='json') for u in users2]

        # Exclude timestamps which may vary slightly
        for u in users1_json + users2_json:
            u.pop('created_at', None)

        assert users1_json == users2_json, "Users differ between identical seeds"

    def test_same_seed_produces_identical_accounts(self):
        """Two runs with seed=42 produce identical account data"""
        config = DataGenerationConfig(seed=42, num_users=10, months_history=1)

        gen1 = SyntheticDataGenerator(config)
        gen2 = SyntheticDataGenerator(config)

        users1 = gen1.generate_users()
        users2 = gen2.generate_users()

        accounts1 = gen1.generate_accounts(users1)
        accounts2 = gen2.generate_accounts(users2)

        # Compare counts and first account
        assert len(accounts1) == len(accounts2)
        assert accounts1[0].account_id == accounts2[0].account_id
        assert accounts1[0].balance_current == accounts2[0].balance_current

    def test_same_seed_produces_identical_hash(self):
        """SHA-256 hash of full dataset matches for seed=42"""
        config = DataGenerationConfig(seed=42, num_users=10, months_history=1)

        gen1 = SyntheticDataGenerator(config)
        users1, accounts1, transactions1, liabilities1 = gen1.generate_all()

        gen2 = SyntheticDataGenerator(config)
        users2, accounts2, transactions2, liabilities2 = gen2.generate_all()

        # Create deterministic JSON representations
        data1 = {
            "users": [u.model_dump(mode='json') for u in users1],
            "accounts": [a.model_dump(mode='json') for a in accounts1],
            "transactions": [t.model_dump(mode='json') for t in transactions1],
            "liabilities": [l.model_dump(mode='json') for l in liabilities1]
        }

        data2 = {
            "users": [u.model_dump(mode='json') for u in users2],
            "accounts": [a.model_dump(mode='json') for a in accounts2],
            "transactions": [t.model_dump(mode='json') for t in transactions2],
            "liabilities": [l.model_dump(mode='json') for l in liabilities2]
        }

        # Remove timestamp fields for comparison
        for u in data1["users"] + data2["users"]:
            u.pop('created_at', None)
            u.pop('consent_timestamp', None)
        for t in data1["transactions"] + data2["transactions"]:
            t['date'] = str(t['date'])  # Normalize datetime
        for l in data1["liabilities"] + data2["liabilities"]:
            for field in ['last_payment_date', 'next_due_date']:
                if l.get(field):
                    l[field] = str(l[field])

        # Compute hashes
        json1 = json.dumps(data1, sort_keys=True, default=str)
        json2 = json.dumps(data2, sort_keys=True, default=str)

        hash1 = hashlib.sha256(json1.encode()).hexdigest()
        hash2 = hashlib.sha256(json2.encode()).hexdigest()

        assert hash1 == hash2, f"Hashes differ: {hash1} vs {hash2}"


class TestEndToEndPipeline:
    """Test 3: End-to-end pipeline - Generate → Validate → Load"""

    def test_full_pipeline_completes(self, temp_data_dir):
        """Full pipeline: generation → validation → SQLite + Parquet"""
        # Step 1: Generate data
        config = DataGenerationConfig(seed=42, num_users=100, months_history=6)
        generator = SyntheticDataGenerator(config)
        users, accounts, transactions, liabilities = generator.generate_all()

        # Verify generation
        assert len(users) == 100, "Should generate 100 users"
        assert len(accounts) >= 200, "Should have at least 2 accounts per user"
        assert len(transactions) > 0, "Should have transactions"
        assert len(liabilities) > 0, "Should have liabilities for credit accounts"

        # Step 2: Validate data
        data = {
            "users": [u.model_dump(mode='json') for u in users],
            "accounts": [a.model_dump(mode='json') for a in accounts],
            "transactions": [t.model_dump(mode='json') for t in transactions],
            "liabilities": [l.model_dump(mode='json') for l in liabilities]
        }

        validator = DataValidator()
        report = validator.validate_all(data)

        assert report.is_valid(), f"Validation failed: {report.summary()}"
        assert report.stats["users_validated"] == 100
        assert report.stats["accounts_validated"] == len(accounts)

        # Step 3: Load into storage
        sqlite_path = temp_data_dir / "test_users.sqlite"
        parquet_path = temp_data_dir / "test_transactions.parquet"

        loader = DataLoader(str(sqlite_path), str(parquet_path))
        loader.load_all(data)

        # Step 4: Verify files exist
        assert sqlite_path.exists(), "SQLite file should exist"
        assert parquet_path.exists(), "Parquet file should exist"
        assert sqlite_path.stat().st_size > 0, "SQLite file should not be empty"
        assert parquet_path.stat().st_size > 0, "Parquet file should not be empty"

        # Step 5: Verify consent table initialized
        import sqlite3
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users WHERE consent_granted = 0")
        no_consent_count = cursor.fetchone()[0]

        assert no_consent_count == 100, "All users should have consent_granted=False by default"

        conn.close()

    def test_each_user_has_6_months_transactions(self, temp_data_dir):
        """Each user has transactions spanning 6 months"""
        config = DataGenerationConfig(seed=42, num_users=10, months_history=6)
        generator = SyntheticDataGenerator(config)
        users, accounts, transactions, liabilities = generator.generate_all()

        # Group transactions by user (via account)
        account_to_user = {acc.account_id: acc.user_id for acc in accounts}
        user_transactions = {}

        for txn in transactions:
            user_id = account_to_user.get(txn.account_id)
            if user_id:
                if user_id not in user_transactions:
                    user_transactions[user_id] = []
                user_transactions[user_id].append(txn)

        # Check date ranges
        for user_id, txns in user_transactions.items():
            if len(txns) < 2:
                continue  # Skip users with too few transactions

            dates = sorted([t.date for t in txns])
            date_range = (dates[-1] - dates[0]).days

            assert date_range >= 150, f"User {user_id} has insufficient date range: {date_range} days"

    def test_sqlite_and_parquet_readable(self, temp_data_dir):
        """SQLite and Parquet files are readable after loading"""
        # Generate and load small dataset
        config = DataGenerationConfig(seed=42, num_users=10, months_history=1)
        generator = SyntheticDataGenerator(config)
        users, accounts, transactions, liabilities = generator.generate_all()

        data = {
            "users": [u.model_dump(mode='json') for u in users],
            "accounts": [a.model_dump(mode='json') for a in accounts],
            "transactions": [t.model_dump(mode='json') for t in transactions],
            "liabilities": [l.model_dump(mode='json') for l in liabilities]
        }

        sqlite_path = temp_data_dir / "test.sqlite"
        parquet_path = temp_data_dir / "test.parquet"

        loader = DataLoader(str(sqlite_path), str(parquet_path))
        loader.load_all(data)

        # Test SQLite queries
        import sqlite3
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        assert user_count == 10

        cursor.execute("SELECT COUNT(*) FROM accounts")
        account_count = cursor.fetchone()[0]
        assert account_count > 0

        conn.close()

        # Test Parquet reading
        import pandas as pd
        df = pd.read_parquet(parquet_path)

        assert len(df) > 0, "Parquet should have transactions"
        assert "transaction_id" in df.columns
        assert "amount" in df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

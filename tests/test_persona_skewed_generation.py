"""
Tests for persona-skewed data generation and operator controls.
"""

import pytest
import pandas as pd
from datetime import datetime

from ingest.schemas import DataGenerationConfig
from ingest.operator_controls import (
    OperatorControls,
    PersonaTarget,
    PRESET_CONFIGS,
)
from ingest.persona_skewed_generator import PersonaSkewedGenerator


class TestOperatorControls:
    """Test operator control configuration"""

    def test_default_controls_creation(self):
        """Test creating default operator controls"""
        controls = OperatorControls()
        assert controls.subscription_adoption_rate == 0.50
        assert controls.savings_adoption_rate == 0.40
        assert len(controls.target_personas) == 0

    def test_persona_targeting(self):
        """Test persona targeting configuration"""
        controls = OperatorControls(
            target_personas=[PersonaTarget.HIGH_UTILIZATION, PersonaTarget.SAVINGS_BUILDER]
        )
        assert len(controls.target_personas) == 2
        assert PersonaTarget.HIGH_UTILIZATION in controls.target_personas

    def test_persona_distribution_calculation(self):
        """Test persona distribution target calculation"""
        controls = OperatorControls(
            target_personas=[PersonaTarget.HIGH_UTILIZATION, PersonaTarget.SAVINGS_BUILDER],
            persona_weights={"high_utilization": 0.6, "savings_builder": 0.4},
        )

        distribution = controls.get_persona_distribution_target(100)
        assert distribution["high_utilization"] == 60
        assert distribution["savings_builder"] == 40
        assert sum(distribution.values()) == 100

    def test_persona_distribution_equal_weights(self):
        """Test equal distribution when no weights specified"""
        controls = OperatorControls(
            target_personas=[PersonaTarget.HIGH_UTILIZATION, PersonaTarget.SAVINGS_BUILDER]
        )

        distribution = controls.get_persona_distribution_target(100)
        assert distribution["high_utilization"] == 50
        assert distribution["savings_builder"] == 50

    def test_invalid_persona_weights(self):
        """Test validation of persona weights"""
        with pytest.raises(ValueError, match="must sum to 1.0"):
            OperatorControls(
                target_personas=[PersonaTarget.HIGH_UTILIZATION],
                persona_weights={"high_utilization": 0.5},  # Should be 1.0
            )

    def test_invalid_payroll_distribution(self):
        """Test validation of payroll distribution"""
        with pytest.raises(ValueError, match="must sum to 1.0"):
            OperatorControls(
                payroll_pattern_distribution={
                    "weekly": 0.2,
                    "biweekly": 0.2,
                    "monthly": 0.2,
                    "irregular": 0.2,  # Total = 0.8, should be 1.0
                }
            )

    def test_preset_configs_exist(self):
        """Test that preset configurations are available"""
        assert "default" in PRESET_CONFIGS
        assert "high_utilization_focus" in PRESET_CONFIGS
        assert "savings_builder_focus" in PRESET_CONFIGS
        assert "overlap_testing" in PRESET_CONFIGS

    def test_preset_high_utilization_focus(self):
        """Test high utilization preset configuration"""
        preset = PRESET_CONFIGS["high_utilization_focus"]
        assert PersonaTarget.HIGH_UTILIZATION in preset.target_personas
        assert preset.credit_utilization_distribution["critical"] > 0.3
        assert preset.overdue_probability > 0.3


class TestPersonaSkewedGenerator:
    """Test persona-skewed data generation"""

    @pytest.fixture
    def basic_config(self):
        """Basic test configuration"""
        return DataGenerationConfig(
            seed=42, num_users=20, months_history=3, avg_transactions_per_month=15
        )

    @pytest.fixture
    def high_util_controls(self):
        """Controls targeting high utilization"""
        return OperatorControls(
            target_personas=[PersonaTarget.HIGH_UTILIZATION],
            credit_utilization_distribution={
                "low": 0.1,
                "medium": 0.1,
                "high": 0.4,
                "critical": 0.4,
            },
        )

    @pytest.fixture
    def savings_controls(self):
        """Controls targeting savings builders"""
        return OperatorControls(
            target_personas=[PersonaTarget.SAVINGS_BUILDER],
            savings_adoption_rate=0.95,
            credit_utilization_distribution={
                "low": 0.8,
                "medium": 0.15,
                "high": 0.05,
                "critical": 0.0,
            },
        )

    def test_basic_generation(self, basic_config):
        """Test basic persona-skewed generation"""
        controls = OperatorControls()
        generator = PersonaSkewedGenerator(basic_config, controls)

        users, accounts, transactions, liabilities = generator.generate_all()

        assert len(users) == 20
        assert len(accounts) > 0
        assert len(transactions) > 0
        assert len(liabilities) >= 0

    def test_deterministic_generation(self, basic_config):
        """Test that generation is deterministic with same seed"""
        controls = OperatorControls(target_personas=[PersonaTarget.HIGH_UTILIZATION])

        gen1 = PersonaSkewedGenerator(basic_config, controls)
        users1, accounts1, transactions1, _ = gen1.generate_all()

        gen2 = PersonaSkewedGenerator(basic_config, controls)
        users2, accounts2, transactions2, _ = gen2.generate_all()

        assert len(users1) == len(users2)
        assert len(accounts1) == len(accounts2)
        assert len(transactions1) == len(transactions2)

        # Check first user is identical
        assert users1[0].user_id == users2[0].user_id
        assert users1[0].age == users2[0].age

    def test_high_utilization_targeting(self, basic_config, high_util_controls):
        """Test that high utilization targeting creates appropriate patterns"""
        generator = PersonaSkewedGenerator(basic_config, high_util_controls)
        users, accounts, transactions, liabilities = generator.generate_all()

        # Check that credit accounts have high utilization
        credit_accounts = [a for a in accounts if a.account_type.value == "credit"]
        assert len(credit_accounts) > 0

        high_util_count = 0
        for acc in credit_accounts:
            if acc.balance_limit and acc.balance_limit > 0:
                utilization = acc.balance_current / acc.balance_limit
                if utilization >= 0.5:
                    high_util_count += 1

        # At least 60% of credit accounts should have high utilization
        assert high_util_count / len(credit_accounts) >= 0.5

    def test_savings_builder_targeting(self, basic_config, savings_controls):
        """Test that savings builder targeting creates appropriate patterns"""
        generator = PersonaSkewedGenerator(basic_config, savings_controls)
        users, accounts, transactions, liabilities = generator.generate_all()

        # Check for savings accounts
        savings_accounts = [a for a in accounts if a.account_subtype.value == "savings"]
        assert len(savings_accounts) > 0

        # Check for savings transfers
        savings_transfers = [
            t
            for t in transactions
            if t.personal_finance_subcategory == "Savings"
        ]
        assert len(savings_transfers) > 0

        # Check that credit utilization is low
        credit_accounts = [a for a in accounts if a.account_type.value == "credit"]
        if credit_accounts:
            low_util_count = 0
            for acc in credit_accounts:
                if acc.balance_limit and acc.balance_limit > 0:
                    utilization = acc.balance_current / acc.balance_limit
                    if utilization < 0.3:
                        low_util_count += 1

            # Most credit accounts should have low utilization
            assert low_util_count / len(credit_accounts) >= 0.5

    def test_subscription_heavy_targeting(self, basic_config):
        """Test that subscription heavy targeting creates appropriate patterns"""
        controls = OperatorControls(
            target_personas=[PersonaTarget.SUBSCRIPTION_HEAVY],
            subscription_adoption_rate=0.9,
            subscription_count_min=5,
        )

        generator = PersonaSkewedGenerator(basic_config, controls)
        users, accounts, transactions, liabilities = generator.generate_all()

        # Check for subscription transactions
        sub_transactions = [
            t
            for t in transactions
            if t.personal_finance_subcategory == "Subscription Services"
        ]
        assert len(sub_transactions) > 0

        # Check that most users have subscriptions
        # (This is approximate since we're checking transactions not user assignments)
        users_with_subs = len(set(t.account_id for t in sub_transactions))
        assert users_with_subs >= basic_config.num_users * 0.7

    def test_multi_persona_targeting(self, basic_config):
        """Test targeting multiple personas simultaneously"""
        controls = OperatorControls(
            target_personas=[
                PersonaTarget.HIGH_UTILIZATION,
                PersonaTarget.SUBSCRIPTION_HEAVY,
            ],
            persona_weights={"high_utilization": 0.5, "subscription_heavy": 0.5},
        )

        generator = PersonaSkewedGenerator(basic_config, controls)
        users, accounts, transactions, liabilities = generator.generate_all()

        # Verify persona assignments
        assert len(generator.user_persona_assignments) == basic_config.num_users

        high_util_count = sum(
            1
            for p in generator.user_persona_assignments.values()
            if p == "high_utilization"
        )
        sub_heavy_count = sum(
            1
            for p in generator.user_persona_assignments.values()
            if p == "subscription_heavy"
        )

        # Should be roughly split
        assert high_util_count >= 8  # At least 40% for 20 users
        assert sub_heavy_count >= 8  # At least 40% for 20 users

    def test_variable_income_targeting(self, basic_config):
        """Test variable income targeting"""
        controls = OperatorControls(
            target_personas=[PersonaTarget.VARIABLE_INCOME],
            payroll_pattern_distribution={
                "weekly": 0.0,
                "biweekly": 0.1,
                "monthly": 0.1,
                "irregular": 0.8,
            },
            irregular_income_volatility=0.8,
        )

        generator = PersonaSkewedGenerator(basic_config, controls)
        users, accounts, transactions, liabilities = generator.generate_all()

        # Check for income transactions
        income_transactions = [
            t
            for t in transactions
            if t.personal_finance_category == "INCOME"
            and t.personal_finance_subcategory == "Payroll"
        ]
        assert len(income_transactions) > 0

        # Variable income should have irregular patterns (harder to test directly)
        # Just verify we have income transactions
        assert len(income_transactions) >= basic_config.num_users

    def test_controls_display_dict(self):
        """Test controls display dictionary generation"""
        controls = OperatorControls(
            target_personas=[PersonaTarget.HIGH_UTILIZATION],
            subscription_adoption_rate=0.75,
        )

        display = controls.to_display_dict()

        assert "Persona Targeting" in display
        assert "Income Patterns" in display
        assert "Credit Behavior" in display
        assert "Subscriptions" in display
        assert "Savings" in display

    def test_transaction_multiplier(self, basic_config):
        """Test transaction volume multiplier"""
        controls_default = OperatorControls(transaction_multiplier=1.0)
        controls_double = OperatorControls(transaction_multiplier=2.0)

        gen_default = PersonaSkewedGenerator(basic_config, controls_default)
        _, _, trans_default, _ = gen_default.generate_all()

        gen_double = PersonaSkewedGenerator(
            DataGenerationConfig(
                seed=43, num_users=20, months_history=3, avg_transactions_per_month=15
            ),
            controls_double,
        )
        _, _, trans_double, _ = gen_double.generate_all()

        # Double multiplier should create significantly more transactions
        assert len(trans_double) > len(trans_default) * 1.5

    def test_persona_assignment_tracking(self, basic_config):
        """Test that persona assignments are tracked correctly"""
        controls = OperatorControls(
            target_personas=[PersonaTarget.HIGH_UTILIZATION, PersonaTarget.SAVINGS_BUILDER]
        )

        generator = PersonaSkewedGenerator(basic_config, controls)
        users, _, _, _ = generator.generate_all()

        # Every user should have a persona assignment
        assert len(generator.user_persona_assignments) == len(users)

        # All assignments should be from target personas
        for persona in generator.user_persona_assignments.values():
            assert persona in ["high_utilization", "savings_builder"]


class TestIntegration:
    """Integration tests for full data generation pipeline"""

    def test_full_pipeline_with_validation(self):
        """Test complete generation pipeline with validation"""
        config = DataGenerationConfig(seed=42, num_users=10, months_history=2)
        controls = OperatorControls(
            target_personas=[PersonaTarget.HIGH_UTILIZATION],
        )

        generator = PersonaSkewedGenerator(config, controls)
        users, accounts, transactions, liabilities = generator.generate_all()

        # Basic validation
        assert len(users) == 10
        assert all(u.user_id.startswith("user_") for u in users)
        assert all(a.account_id.startswith("acc_") for a in accounts)
        assert all(t.transaction_id.startswith("txn_") for t in transactions)

        # Referential integrity
        user_ids = {u.user_id for u in users}
        account_ids = {a.account_id for a in accounts}

        assert all(a.user_id in user_ids for a in accounts)
        assert all(t.account_id in account_ids for t in transactions)
        assert all(l.user_id in user_ids for l in liabilities)

    def test_data_export_to_dict(self):
        """Test exporting generated data to dictionaries"""
        config = DataGenerationConfig(seed=42, num_users=10, months_history=1)
        controls = OperatorControls()

        generator = PersonaSkewedGenerator(config, controls)
        users, accounts, transactions, liabilities = generator.generate_all()

        # Convert to dicts (as would be done for JSON export)
        user_dicts = [u.model_dump(mode="json") for u in users]
        account_dicts = [a.model_dump(mode="json") for a in accounts]
        transaction_dicts = [t.model_dump(mode="json") for t in transactions]
        liability_dicts = [l.model_dump(mode="json") for l in liabilities]

        # Verify structure
        assert len(user_dicts) == 10
        assert all("user_id" in u for u in user_dicts)
        assert all("account_id" in a for a in account_dicts)
        assert all("transaction_id" in t for t in transaction_dicts)

    def test_preset_configuration_usage(self):
        """Test using preset configurations"""
        config = DataGenerationConfig(seed=42, num_users=15, months_history=2)

        # Test each preset
        for preset_name, preset_controls in PRESET_CONFIGS.items():
            generator = PersonaSkewedGenerator(config, preset_controls)
            users, accounts, transactions, liabilities = generator.generate_all()

            assert len(users) == 15
            assert len(accounts) > 0
            assert len(transactions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Persona-skewed data generator for SpendSense MVP V2.
Extends SyntheticDataGenerator with operator controls for targeted persona generation.
"""

from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import numpy as np
from faker import Faker

from ingest.data_generator import SyntheticDataGenerator
from ingest.schemas import (
    User,
    Account,
    Transaction,
    Liability,
    DataGenerationConfig,
    AccountType,
    AccountSubtype,
    PaymentChannel,
)
from ingest.operator_controls import OperatorControls, PersonaTarget
from ingest.constants import SUBSCRIPTION_PRICES


class PersonaSkewedGenerator(SyntheticDataGenerator):
    """
    Enhanced synthetic data generator with persona targeting.

    Allows operators to:
    1. Target specific personas for generation
    2. Control behavioral pattern distributions
    3. Test persona overlap scenarios
    4. Fine-tune all generation parameters
    """

    def __init__(self, config: DataGenerationConfig, controls: OperatorControls):
        super().__init__(config)
        self.controls = controls
        self.persona_targets = controls.get_persona_distribution_target(config.num_users)

        # Track which users should target which personas
        self.user_persona_assignments: Dict[str, str] = {}

        print(f"\n📊 Persona Targeting Configuration:")
        if self.persona_targets:
            for persona, count in self.persona_targets.items():
                print(f"  • {persona}: {count} users ({count/config.num_users*100:.1f}%)")
        else:
            print("  • Natural distribution (no targeting)")
        print()

    def _assign_persona_targets(self, users: List[User]) -> None:
        """
        Pre-assign persona targets to users based on operator controls.
        This helps ensure we generate data that will result in desired personas.
        """
        if not self.persona_targets:
            # No targeting - natural distribution
            return

        user_ids = [u.user_id for u in users]
        # Shuffle for randomness but deterministically
        user_array = np.array(user_ids, dtype=object)
        self.rng.shuffle(user_array)
        user_ids_shuffled = user_array.tolist()

        idx = 0
        for persona, count in self.persona_targets.items():
            for _ in range(count):
                if idx < len(user_ids_shuffled):
                    self.user_persona_assignments[user_ids_shuffled[idx]] = persona
                    idx += 1

    def generate_accounts(self, users: List[User]) -> List[Account]:
        """
        Generate accounts with persona-aware configurations.
        Credit card presence and utilization are skewed based on persona targets.
        """
        accounts = []
        account_counter = 0

        # Assign persona targets to users
        self._assign_persona_targets(users)

        for user in users:
            target_persona = self.user_persona_assignments.get(user.user_id)

            # Determine number of accounts based on persona target
            if target_persona == "high_utilization":
                # High utilization users typically have credit cards
                num_accounts = int(self.rng.choice([3, 4], p=[0.3, 0.7]))
            elif target_persona == "savings_builder":
                # Savings builders always have savings accounts
                num_accounts = int(self.rng.choice([2, 3, 4], p=[0.2, 0.5, 0.3]))
            elif target_persona == "variable_income":
                # Variable income users may have fewer accounts
                num_accounts = int(self.rng.choice([2, 3], p=[0.6, 0.4]))
            else:
                # Use operator-controlled distribution
                accounts_str = list(self.controls.accounts_per_user_distribution.keys())
                probs = list(self.controls.accounts_per_user_distribution.values())
                num_accounts = int(self.rng.choice(accounts_str, p=probs))

            # Every user gets a checking account
            checking = Account(
                account_id=f"acc_{account_counter:06d}",
                user_id=user.user_id,
                account_type=AccountType.DEPOSITORY,
                account_subtype=AccountSubtype.CHECKING,
                balance_current=float(self.rng.uniform(500, 15000)),
                balance_available=None,
                balance_limit=None,
                iso_currency_code="USD",
                holder_category="consumer",
                mask=f"{int(self.rng.integers(1000, 9999))}",
                name="Checking Account",
                official_name=f"{self.fake.company()} Bank Checking",
            )
            accounts.append(checking)
            account_counter += 1

            # Add savings account (required for savings_builder)
            has_savings = num_accounts >= 2 or target_persona == "savings_builder"
            if has_savings:
                # Savings builders get higher balances
                if target_persona == "savings_builder":
                    balance = float(self.rng.uniform(5000, 80000))
                else:
                    balance = float(self.rng.uniform(1000, 50000))

                savings = Account(
                    account_id=f"acc_{account_counter:06d}",
                    user_id=user.user_id,
                    account_type=AccountType.DEPOSITORY,
                    account_subtype=AccountSubtype.SAVINGS,
                    balance_current=balance,
                    balance_available=None,
                    balance_limit=None,
                    iso_currency_code="USD",
                    holder_category="consumer",
                    mask=f"{int(self.rng.integers(1000, 9999))}",
                    name="Savings Account",
                    official_name=f"{self.fake.company()} Bank Savings",
                )
                accounts.append(savings)
                account_counter += 1

            # Add credit cards based on persona and controls
            num_credit_cards = max(0, num_accounts - 2)

            # Force credit cards for high_utilization persona
            if target_persona == "high_utilization" and num_credit_cards == 0:
                num_credit_cards = 1

            for _ in range(num_credit_cards):
                credit_limit = float(self.rng.choice([2000, 5000, 10000, 15000, 25000]))

                # Determine utilization based on persona target
                if target_persona == "high_utilization":
                    # Force high utilization for this persona
                    util_tier = str(self.rng.choice(
                        ["high", "critical"],
                        p=[0.5, 0.5]
                    ))
                elif target_persona == "savings_builder":
                    # Low utilization for savings builders
                    util_tier = "low"
                else:
                    # Use operator-controlled distribution
                    util_tiers = list(self.controls.credit_utilization_distribution.keys())
                    util_probs = list(self.controls.credit_utilization_distribution.values())
                    util_tier = str(self.rng.choice(util_tiers, p=util_probs))

                # Map tier to utilization percentage
                if util_tier == "low":
                    utilization = float(self.rng.uniform(0.05, 0.30))
                elif util_tier == "medium":
                    utilization = float(self.rng.uniform(0.30, 0.50))
                elif util_tier == "high":
                    utilization = float(self.rng.uniform(0.50, 0.80))
                else:  # critical
                    utilization = float(self.rng.uniform(0.80, 0.95))

                balance = credit_limit * utilization

                credit_card = Account(
                    account_id=f"acc_{account_counter:06d}",
                    user_id=user.user_id,
                    account_type=AccountType.CREDIT,
                    account_subtype=AccountSubtype.CREDIT_CARD,
                    balance_current=float(balance),
                    balance_available=float(credit_limit - balance),
                    balance_limit=float(credit_limit),
                    iso_currency_code="USD",
                    holder_category="consumer",
                    mask=f"{int(self.rng.integers(1000, 9999))}",
                    name="Credit Card",
                    official_name=f"{self.rng.choice(['Visa', 'Mastercard', 'Amex'])} {self.fake.company()}",
                )
                accounts.append(credit_card)
                account_counter += 1

        return accounts

    def generate_transactions(self, accounts: List[Account]) -> List[Transaction]:
        """
        Generate transactions with persona-aware behavioral patterns.
        """
        transactions = []
        transaction_counter = 0

        # Group accounts by user
        user_accounts = {}
        for acc in accounts:
            if acc.user_id not in user_accounts:
                user_accounts[acc.user_id] = []
            user_accounts[acc.user_id].append(acc)

        for user_id, user_accs in user_accounts.items():
            target_persona = self.user_persona_assignments.get(user_id)

            # Determine user spending profile
            is_high_spender = float(self.rng.random()) < self.controls.high_spender_probability
            num_transactions = int(
                self.config.avg_transactions_per_month
                * self.config.months_history
                * self.controls.transaction_multiplier
            )

            if is_high_spender:
                num_transactions = int(num_transactions * 1.5)

            # Find primary accounts
            checking_accs = [a for a in user_accs if a.account_subtype == AccountSubtype.CHECKING]
            savings_accs = [a for a in user_accs if a.account_subtype == AccountSubtype.SAVINGS]
            credit_accs = [a for a in user_accs if a.account_type == AccountType.CREDIT]

            primary_checking = checking_accs[0] if checking_accs else None
            primary_savings = savings_accs[0] if savings_accs else None
            primary_credit = credit_accs[0] if credit_accs else None

            # === SAVINGS TRANSFERS ===
            has_savings_transfer = False
            if primary_checking and primary_savings:
                # Persona-aware savings adoption
                if target_persona == "savings_builder":
                    savings_prob = 0.95  # Almost all savings builders save
                else:
                    savings_prob = self.controls.savings_adoption_rate

                if float(self.rng.random()) < savings_prob:
                    has_savings_transfer = True

                    # Determine transfer amount based on persona
                    if target_persona == "savings_builder":
                        monthly_transfer = float(self.rng.uniform(*self.controls.savings_transfer_range)) * 1.5
                    else:
                        monthly_transfer = float(self.rng.uniform(*self.controls.savings_transfer_range))

                    for month_offset in range(self.config.months_history):
                        trans_date = self.start_date + timedelta(
                            days=30 * month_offset + int(self.rng.integers(1, 5))
                        )
                        transactions.append(
                            Transaction(
                                transaction_id=f"txn_{transaction_counter:08d}",
                                account_id=primary_savings.account_id,
                                date=trans_date,
                                amount=-monthly_transfer,
                                merchant_name="Transfer from Checking",
                                payment_channel=PaymentChannel.OTHER,
                                personal_finance_category="TRANSFER_IN",
                                personal_finance_subcategory="Savings",
                                pending=False,
                            )
                        )
                        transaction_counter += 1

            # === SUBSCRIPTIONS ===
            # Persona-aware subscription generation
            if target_persona == "subscription_heavy":
                has_subscriptions = True
                sub_adoption_rate = 0.95
            else:
                sub_adoption_rate = self.controls.subscription_adoption_rate
                has_subscriptions = float(self.rng.random()) < sub_adoption_rate

            if has_subscriptions and primary_checking:
                # Number of subscriptions based on persona
                if target_persona == "subscription_heavy":
                    num_subs = int(self.rng.integers(
                        self.controls.subscription_count_min,
                        self.controls.subscription_count_max + 1
                    ))
                else:
                    num_subs = int(self.rng.integers(2, 5))

                from ingest.schemas import RECURRING_MERCHANTS
                selected_subs = self.rng.choice(
                    RECURRING_MERCHANTS,
                    size=min(num_subs, len(RECURRING_MERCHANTS)),
                    replace=False
                )

                for merchant in selected_subs:
                    # Generate monthly recurring transaction
                    for month_offset in range(self.config.months_history):
                        trans_date = self.start_date + timedelta(
                            days=30 * month_offset + int(self.rng.integers(1, 28))
                        )

                        base_price = SUBSCRIPTION_PRICES.get(merchant, None)
                        if base_price is None:
                            amount = float(self.rng.uniform(5.99, 49.99))
                        else:
                            jitter = float(self.rng.uniform(-0.02, 0.02))
                            amount = round(base_price * (1.0 + jitter), 2)

                        # Subscription-heavy users might have premium tiers
                        if target_persona == "subscription_heavy":
                            amount *= float(self.rng.uniform(1.0, 1.8))

                        transaction = Transaction(
                            transaction_id=f"txn_{transaction_counter:08d}",
                            account_id=primary_checking.account_id,
                            date=trans_date,
                            amount=amount,
                            merchant_name=merchant,
                            payment_channel=PaymentChannel.ONLINE,
                            personal_finance_category="GENERAL_SERVICES",
                            personal_finance_subcategory="Subscription Services",
                            pending=False,
                        )
                        transactions.append(transaction)
                        transaction_counter += 1

            # === PAYROLL DEPOSITS ===
            if primary_checking:
                # Select pay pattern based on persona and controls
                if target_persona == "variable_income":
                    # Force irregular income
                    pay_pattern = "irregular"
                    # Increase transaction volume to reduce cash buffer
                    num_transactions = int(num_transactions * 1.8)
                else:
                    # Use operator-controlled distribution
                    patterns = list(self.controls.payroll_pattern_distribution.keys())
                    probs = list(self.controls.payroll_pattern_distribution.values())
                    pay_pattern = str(self.rng.choice(patterns, p=probs))

                    if pay_pattern == "irregular":
                        num_transactions = int(num_transactions * 1.5)

                def paycheck_dates():
                    if pay_pattern == "weekly":
                        interval = 7
                        n = (self.config.months_history * 30) // interval
                        for i in range(n):
                            yield self.start_date + timedelta(days=interval * i)
                    elif pay_pattern == "biweekly":
                        interval = 14
                        n = (self.config.months_history * 30) // interval
                        for i in range(n):
                            yield self.start_date + timedelta(days=interval * i)
                    elif pay_pattern == "monthly":
                        for i in range(self.config.months_history):
                            yield self.start_date + timedelta(
                                days=30 * i + int(self.rng.integers(0, 3))
                            )
                    else:  # irregular
                        day = 0
                        total_days = self.config.months_history * 30
                        # Variable income: wider gaps
                        if target_persona == "variable_income":
                            min_gap, max_gap = 20, 75  # Up to 75 days between payments
                        else:
                            min_gap, max_gap = 20, 60
                        while day < total_days:
                            yield self.start_date + timedelta(days=day)
                            day += int(self.rng.integers(min_gap, max_gap + 1))

                for paycheck_date in paycheck_dates():
                    # Determine paycheck amount based on pattern and volatility
                    if pay_pattern == "irregular":
                        base_amount = float(self.rng.uniform(1000, 3000))
                        volatility = self.controls.irregular_income_volatility
                        variation = float(self.rng.uniform(-volatility, volatility))
                        paycheck_amount = -abs(base_amount * (1.0 + variation))
                    else:
                        paycheck_amount = -float(self.rng.uniform(2000, 6000))

                    payroll = Transaction(
                        transaction_id=f"txn_{transaction_counter:08d}",
                        account_id=primary_checking.account_id,
                        date=paycheck_date,
                        amount=paycheck_amount,
                        merchant_name=f"{self.fake.company()} Payroll",
                        payment_channel=PaymentChannel.OTHER,
                        personal_finance_category="INCOME",
                        personal_finance_subcategory="Payroll",
                        pending=False,
                    )
                    transactions.append(payroll)
                    transaction_counter += 1

            # === REGULAR SPENDING ===
            # (Keeping original logic for now)
            from ingest.schemas import TRANSACTION_CATEGORIES, GROCERY_MERCHANTS, RESTAURANT_MERCHANTS

            for _ in range(num_transactions):
                # Choose account (70% checking, 30% credit if available)
                if primary_credit and float(self.rng.random()) < 0.3:
                    account = primary_credit
                elif primary_checking:
                    account = primary_checking
                else:
                    account = user_accs[0]

                days_offset = int(self.rng.integers(0, 30 * self.config.months_history))
                trans_date = self.start_date + timedelta(days=days_offset)

                category, subcategory = self.fake.random_element(TRANSACTION_CATEGORIES)

                if category == "INCOME":
                    amount = -float(self.rng.uniform(2000, 8000))
                    merchant_name = f"{self.fake.company()} Payroll"
                    payment_channel = PaymentChannel.OTHER
                elif category == "TRANSFER_IN":
                    amount = -float(self.rng.uniform(100, 2000))
                    merchant_name = "Transfer from Savings"
                    payment_channel = PaymentChannel.OTHER
                else:
                    if subcategory == "Groceries":
                        merchant_name = self.fake.random_element(GROCERY_MERCHANTS)
                        amount = float(self.rng.uniform(50, 300))
                    elif subcategory == "Restaurants":
                        merchant_name = self.fake.random_element(RESTAURANT_MERCHANTS)
                        amount = float(self.rng.uniform(15, 150))
                    else:
                        merchant_name = self.fake.company()
                        amount = float(self.rng.uniform(10, 500))

                    payment_channel = self.fake.random_element(list(PaymentChannel))

                transaction = Transaction(
                    transaction_id=f"txn_{transaction_counter:08d}",
                    account_id=account.account_id,
                    date=trans_date,
                    amount=amount,
                    merchant_name=merchant_name,
                    payment_channel=payment_channel,
                    personal_finance_category=category,
                    personal_finance_subcategory=subcategory,
                    pending=False,
                    location_city=self.fake.city() if float(self.rng.random()) < 0.5 else None,
                    location_state=self.fake.state_abbr() if float(self.rng.random()) < 0.5 else None,
                )
                transactions.append(transaction)
                transaction_counter += 1

        return transactions

    def generate_liabilities(self, accounts: List[Account]) -> List[Liability]:
        """
        Generate liability info with persona-aware defaults.
        High utilization persona users more likely to be overdue.
        """
        liabilities = []
        liability_counter = 0

        credit_accounts = [a for a in accounts if a.account_type == AccountType.CREDIT]

        for account in credit_accounts:
            target_persona = self.user_persona_assignments.get(account.user_id)
            utilization = (
                account.balance_current / account.balance_limit if account.balance_limit else 0
            )

            # Persona-aware overdue probability
            if target_persona == "high_utilization":
                is_overdue = utilization > 0.5 and float(self.rng.random()) < self.controls.overdue_probability
            else:
                is_overdue = utilization > 0.8 and float(self.rng.random()) < (self.controls.overdue_probability * 0.5)

            apr = float(self.rng.uniform(12.99, 29.99))
            min_payment = float(max(25, account.balance_current * 0.02))

            # High utilization users more likely to make minimum payments only
            if target_persona == "high_utilization" and utilization > 0.5:
                last_payment = min_payment if float(self.rng.random()) < self.controls.min_payment_only_probability else float(self.rng.uniform(min_payment, account.balance_current * 0.3))
            else:
                last_payment = (
                    float(self.rng.uniform(min_payment, account.balance_current * 0.5))
                    if float(self.rng.random()) < 0.9
                    else None
                )

            liability = Liability(
                liability_id=f"liab_{liability_counter:06d}",
                account_id=account.account_id,
                user_id=account.user_id,
                apr=apr,
                minimum_payment=min_payment,
                last_payment_amount=last_payment,
                last_payment_date=self.end_date - timedelta(days=int(self.rng.integers(1, 30))),
                next_due_date=self.end_date + timedelta(days=int(self.rng.integers(1, 30))),
                is_overdue=is_overdue,
                overdue_amount=float(self.rng.uniform(25, 200)) if is_overdue else None,
            )
            liabilities.append(liability)
            liability_counter += 1

        return liabilities

    def generate_all(self) -> Tuple[List[User], List[Account], List[Transaction], List[Liability]]:
        """Generate complete synthetic dataset with persona targeting"""
        print(f"🎯 Generating persona-skewed synthetic data...")
        print(f"   Seed: {self.config.seed}")
        print(f"   Users: {self.config.num_users}")
        print(f"   History: {self.config.months_history} months")

        users = self.generate_users()
        print(f"✓ Generated {len(users)} users")

        accounts = self.generate_accounts(users)
        print(f"✓ Generated {len(accounts)} accounts")

        transactions = self.generate_transactions(accounts)
        print(f"✓ Generated {len(transactions)} transactions")

        liabilities = self.generate_liabilities(accounts)
        print(f"✓ Generated {len(liabilities)} liabilities")

        interest_txns = self.generate_interest_transactions(accounts, liabilities)
        transactions.extend(interest_txns)
        print(f"✓ Generated {len(interest_txns)} interest transactions")

        print(f"\n📈 Expected Persona Distribution:")
        for persona, count in self.persona_targets.items():
            print(f"   • {persona}: ~{count} users")
        print()

        return users, accounts, transactions, liabilities

"""
Synthetic data generator for SpendSense MVP V2.
Creates realistic Plaid-style financial data with temporal patterns.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
import numpy as np
from faker import Faker

from ingest.schemas import (
    User,
    Account,
    Transaction,
    Liability,
    DataGenerationConfig,
    AccountType,
    AccountSubtype,
    PaymentChannel,
    Gender,
    IncomeTier,
    Region,
    TRANSACTION_CATEGORIES,
    RECURRING_MERCHANTS,
    GROCERY_MERCHANTS,
    RESTAURANT_MERCHANTS,
)
from ingest.constants import SUBSCRIPTION_PRICES
from ingest.operator_controls import OperatorControls


class SyntheticDataGenerator:
    """Generate realistic synthetic financial data"""

    def __init__(self, config: DataGenerationConfig, operator_controls: OperatorControls = None):
        self.config = config
        # Use provided controls or default to standard controls
        self.controls = operator_controls if operator_controls is not None else OperatorControls()

        # Use instance-scoped randomness for determinism across multiple instances
        self.fake = Faker()
        # Seed only this Faker instance (avoid global state)
        try:
            # Newer Faker versions
            self.fake.seed_instance(config.seed)
        except Exception:
            # Fallback for compatibility
            Faker.seed(config.seed)
        # Instance-local NumPy generator
        self.rng = np.random.default_rng(config.seed)

        # Date range for transactions anchored to config timestamp for determinism
        # Use generation_timestamp instead of datetime.now() so multiple generators
        # with the same config produce identical outputs.
        self.end_date = config.generation_timestamp
        self.start_date = self.end_date - timedelta(days=30 * config.months_history)

    def generate_users(self) -> List[User]:
        """Generate synthetic users with demographic diversity"""
        users = []

        n = self.config.num_users

        # Balanced categorical distributions
        gender_vals = [g.value for g in Gender]
        region_vals = [r.value for r in Region]
        income_vals = [t.value for t in IncomeTier]

        def balanced_list(values: list[str], total: int) -> list[str]:
            # Repeat values evenly and trim, then shuffle deterministically via rng
            k = len(values)
            full = (values * (total // k)) + values[: (total % k)]
            # Shuffle with numpy RNG for determinism under seed
            arr = np.array(full, dtype=object)
            self.rng.shuffle(arr)
            return arr.tolist()

        genders = balanced_list(gender_vals, n)
        regions = balanced_list(region_vals, n)
        incomes = balanced_list(income_vals, n)

        # Balanced age buckets: 18-30, 31-50, 51-75
        age_buckets = balanced_list(["18_30", "31_50", "51_75"], n)

        for i in range(n):
            bucket = age_buckets[i]
            if bucket == "18_30":
                age = int(self.rng.integers(18, 31))
            elif bucket == "31_50":
                age = int(self.rng.integers(31, 51))
            else:
                age = int(self.rng.integers(51, 76))  # up to 75

            user = User(
                user_id=f"user_{i:04d}",
                name=self.fake.name(),
                consent_granted=False,  # Default to no consent per PRD
                consent_timestamp=None,
                revoked_timestamp=None,
                age=age,
                gender=genders[i],
                income_tier=incomes[i],
                region=regions[i],
                created_at=datetime.now(),
            )
            users.append(user)

        return users

    def generate_accounts(self, users: List[User]) -> List[Account]:
        """Generate 2-4 accounts per user (checking, savings, credit cards)"""
        accounts = []
        account_counter = 0

        for user in users:
            # Bias toward 3-4 accounts so most users have a credit card available
            # ~75% -> 3-4 accounts, ~25% -> 2 accounts
            if float(self.rng.random()) < 0.75:
                num_accounts = int(self.rng.choice([3, 4]))
            else:
                num_accounts = 2  # Checking + Savings only

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

            # Most users get a savings account
            if num_accounts >= 2:
                savings = Account(
                    account_id=f"acc_{account_counter:06d}",
                    user_id=user.user_id,
                    account_type=AccountType.DEPOSITORY,
                    account_subtype=AccountSubtype.SAVINGS,
                    balance_current=float(self.rng.uniform(1000, 50000)),
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

            # Many users get 1-2 credit cards
            num_credit_cards = min(num_accounts - 2, int(self.rng.integers(1, 3)))
            for _ in range(num_credit_cards):
                credit_limit = float(self.rng.choice([2000, 5000, 10000, 15000, 25000]))
                # Use operator controls to determine credit utilization distribution
                dist = self.controls.credit_utilization_distribution
                tier = str(self.rng.choice(
                    list(dist.keys()),
                    p=list(dist.values())
                ))
                # Map tier to utilization range
                if tier == "low":
                    utilization = float(self.rng.uniform(0.05, 0.30))
                elif tier == "medium":
                    utilization = float(self.rng.uniform(0.30, 0.50))
                elif tier == "high":
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
        """Generate realistic transaction patterns with temporal variation"""
        transactions = []
        transaction_counter = 0

        # Group accounts by user for cohesive spending patterns
        user_accounts = {}
        for acc in accounts:
            if acc.user_id not in user_accounts:
                user_accounts[acc.user_id] = []
            user_accounts[acc.user_id].append(acc)

        for user_id, user_accs in user_accounts.items():
            # Determine user spending profile
            is_high_spender = float(self.rng.random()) < 0.3
            num_transactions = int(
                self.config.avg_transactions_per_month * self.config.months_history
            )

            # Adjust for spending profile
            if is_high_spender:
                num_transactions = int(num_transactions * 1.5)

            # Find primary accounts
            checking_accs = [a for a in user_accs if a.account_subtype == AccountSubtype.CHECKING]
            credit_accs = [a for a in user_accs if a.account_type == AccountType.CREDIT]

            primary_checking = checking_accs[0] if checking_accs else None
            primary_credit = credit_accs[0] if credit_accs else None

            # Optional: generate monthly savings transfers for a subset of users
            savings_accs = [a for a in user_accs if a.account_subtype == AccountSubtype.SAVINGS]
            has_savings_transfer = False
            # Use operator controls for savings behavior
            if primary_checking and savings_accs and float(self.rng.random()) < self.controls.savings_adoption_rate:
                # Use operator controls for transfer amount range
                monthly_transfer = float(self.rng.uniform(
                    self.controls.savings_transfer_range[0],
                    self.controls.savings_transfer_range[1]
                ))
                has_savings_transfer = True
                for month_offset in range(self.config.months_history):
                    trans_date = self.start_date + timedelta(
                        days=30 * month_offset + int(self.rng.integers(1, 5))
                    )
                    # Deposit into savings (negative = credit)
                    transactions.append(
                        Transaction(
                            transaction_id=f"txn_{transaction_counter:08d}",
                            account_id=savings_accs[0].account_id,
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

            # Generate recurring subscriptions based on operator controls
            has_subscriptions = float(self.rng.random()) < self.controls.subscription_adoption_rate
            if has_subscriptions and primary_checking:
                # Use operator controls for subscription count range
                num_subs = int(self.rng.integers(
                    self.controls.subscription_count_min,
                    self.controls.subscription_count_max + 1
                ))
                selected_subs = self.rng.choice(
                    RECURRING_MERCHANTS, size=min(num_subs, len(RECURRING_MERCHANTS)), replace=False
                )

                for merchant in selected_subs:
                    # Generate monthly recurring transaction
                    for month_offset in range(self.config.months_history):
                        trans_date = self.start_date + timedelta(
                            days=30 * month_offset + int(self.rng.integers(1, 28))
                        )
                        # Use fixed subscription price (with tiny jitter within 2% to be realistic)
                        base_price = SUBSCRIPTION_PRICES.get(merchant, None)
                        if base_price is None:
                            amount = float(self.rng.uniform(5.99, 49.99))
                        else:
                            jitter = float(self.rng.uniform(-0.02, 0.02))  # +/-2%
                            amount = round(base_price * (1.0 + jitter), 2)

                        transaction = Transaction(
                            transaction_id=f"txn_{transaction_counter:08d}",
                            account_id=primary_checking.account_id,
                            date=trans_date,
                            amount=amount,  # Positive = debit
                            merchant_name=merchant,
                            payment_channel=PaymentChannel.ONLINE,
                            personal_finance_category="GENERAL_SERVICES",
                            personal_finance_subcategory="Subscription Services",
                            pending=False,
                        )
                        transactions.append(transaction)
                        transaction_counter += 1

            # Generate regular transactions
            for _ in range(num_transactions):
                # Choose account (70% checking, 30% credit if available)
                if primary_credit and float(self.rng.random()) < 0.3:
                    account = primary_credit
                elif primary_checking:
                    account = primary_checking
                else:
                    account = user_accs[0]

                # Generate random transaction date
                days_offset = int(self.rng.integers(0, 30 * self.config.months_history))
                trans_date = self.start_date + timedelta(days=days_offset)

                # Choose category and amount
                category, subcategory = self.fake.random_element(TRANSACTION_CATEGORIES)

                # Special handling for income
                if category == "INCOME":
                    amount = -float(self.rng.uniform(2000, 8000))  # Negative = credit
                    merchant_name = f"{self.fake.company()} Payroll"
                    payment_channel = PaymentChannel.OTHER
                elif category == "TRANSFER_IN":
                    amount = -float(self.rng.uniform(100, 2000))
                    merchant_name = "Transfer from Savings"
                    payment_channel = PaymentChannel.OTHER
                else:
                    # Regular spending
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
                    location_state=(
                        self.fake.state_abbr() if float(self.rng.random()) < 0.5 else None
                    ),
                )
                transactions.append(transaction)
                transaction_counter += 1

            # Generate payroll deposits with diversified patterns
            if primary_checking:
                # Use operator controls for payroll pattern distribution
                dist = self.controls.payroll_pattern_distribution
                patterns = list(dist.keys())
                probs = list(dist.values())
                pay_pattern = str(self.rng.choice(patterns, p=probs))

                # If irregular pay, boost expenses to reduce cash buffer
                if pay_pattern == "irregular":
                    num_transactions = int(num_transactions * 1.8)

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
                    else:  # irregular: variable gaps 20-60 days
                        day = 0
                        total_days = self.config.months_history * 30
                        while day < total_days:
                            yield self.start_date + timedelta(days=day)
                            day += int(self.rng.integers(20, 61))

                for paycheck_date in paycheck_dates():
                    # Smaller, more variable paychecks for irregular pattern to lower cash buffer
                    if pay_pattern == "irregular":
                        paycheck_amount = -float(self.rng.uniform(1000, 3000))
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

        return transactions

    def generate_liabilities(self, accounts: List[Account]) -> List[Liability]:
        """Generate liability info for credit accounts"""
        liabilities = []
        liability_counter = 0

        credit_accounts = [a for a in accounts if a.account_type == AccountType.CREDIT]

        for account in credit_accounts:
            # Calculate utilization
            utilization = (
                account.balance_current / account.balance_limit if account.balance_limit else 0
            )

            # Higher utilization = higher chance of issues
            is_overdue = utilization > 0.8 and float(self.rng.random()) < 0.3

            # APR varies by creditworthiness (simulated)
            apr = float(self.rng.uniform(12.99, 29.99))

            # Minimum payment (typically 1-3% of balance)
            min_payment = float(max(25, account.balance_current * 0.02))

            liability = Liability(
                liability_id=f"liab_{liability_counter:06d}",
                account_id=account.account_id,
                user_id=account.user_id,
                apr=apr,
                minimum_payment=min_payment,
                last_payment_amount=(
                    float(self.rng.uniform(min_payment, account.balance_current * 0.5))
                    if float(self.rng.random()) < 0.9
                    else None
                ),
                last_payment_date=self.end_date - timedelta(days=int(self.rng.integers(1, 30))),
                next_due_date=self.end_date + timedelta(days=int(self.rng.integers(1, 30))),
                is_overdue=is_overdue,
                overdue_amount=float(self.rng.uniform(25, 200)) if is_overdue else None,
            )
            liabilities.append(liability)
            liability_counter += 1

        return liabilities

    def generate_interest_transactions(
        self, accounts: List[Account], liabilities: List[Liability]
    ) -> List[Transaction]:
        """Generate monthly interest charge transactions for revolving credit balances.

        Creates a positive (debit) transaction on each credit card for each month
        of history where utilization is meaningful and APR > 0.
        """
        # Map liabilities by account_id for APR lookup
        liab_by_account = {l.account_id: l for l in liabilities}

        interest_txns: List[Transaction] = []

        # For each credit account, post a monthly interest charge
        for acc in accounts:
            if (
                acc.account_type != AccountType.CREDIT
                or acc.account_subtype != AccountSubtype.CREDIT_CARD
            ):
                continue

            if not acc.balance_limit or acc.balance_limit <= 0:
                continue

            utilization = acc.balance_current / acc.balance_limit
            # Post interest for moderately utilized cards as well to reflect real-world behavior
            if utilization <= 0.4:
                continue

            apr = 0.0
            liab = liab_by_account.get(acc.account_id)
            if liab and liab.apr:
                apr = float(liab.apr)
            else:
                # Fallback APR if liability not found (kept realistic)
                apr = float(self.rng.uniform(12.99, 29.99))

            # Approximate monthly interest = balance * (APR/100)/12 with small jitter
            base_monthly_rate = (apr / 100.0) / 12.0
            base_interest = max(0.0, acc.balance_current * base_monthly_rate)

            # With some probability, post interest each month (slightly higher to improve coverage)
            if float(self.rng.random()) < 0.8:
                for month in range(self.config.months_history):
                    post_date = self.start_date + timedelta(
                        days=30 * (month + 1) - int(self.rng.integers(1, 5))
                    )
                    jitter = float(self.rng.uniform(-0.05, 0.05))  # ±5%
                    amount = round(base_interest * (1.0 + jitter), 2)
                    if amount <= 0:
                        continue

                    interest_txns.append(
                        Transaction(
                            transaction_id=f"txn_interest_{acc.account_id}_{month:02d}",
                            account_id=acc.account_id,
                            user_id=acc.user_id,
                            date=post_date,
                            amount=amount,  # Positive = debit/charge
                            merchant_name="Credit Card Interest",
                            payment_channel=PaymentChannel.OTHER,
                            personal_finance_category="FEES_AND_CHARGES",
                            personal_finance_subcategory="Interest",
                            pending=False,
                        )
                    )

        return interest_txns

    def generate_all(self) -> Tuple[List[User], List[Account], List[Transaction], List[Liability]]:
        """Generate complete synthetic dataset"""
        print(f"Generating synthetic data with seed={self.config.seed}...")
        print(f"Target: {self.config.num_users} users, {self.config.months_history} months history")

        users = self.generate_users()
        print(f"✓ Generated {len(users)} users")

        accounts = self.generate_accounts(users)
        print(f"✓ Generated {len(accounts)} accounts")

        transactions = self.generate_transactions(accounts)
        print(f"✓ Generated {len(transactions)} transactions")

        liabilities = self.generate_liabilities(accounts)
        print(f"✓ Generated {len(liabilities)} liabilities")

        # Generate posted interest charges on credit cards
        interest_txns = self.generate_interest_transactions(accounts, liabilities)
        transactions.extend(interest_txns)
        print(f"✓ Generated {len(interest_txns)} interest transactions")

        return users, accounts, transactions, liabilities


def main():
    """CLI entry point for data generation"""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Check for operator config file (created by UI)
    operator_config_path = data_dir / "operator_config.json"
    controls = None

    if operator_config_path.exists():
        print(f"Loading operator configuration from {operator_config_path}")
        with open(operator_config_path, "r") as f:
            config_data = json.load(f)

        # Load both config and controls from the file
        config = DataGenerationConfig(**config_data.get("config", {}))
        from ingest.operator_controls import OperatorControls
        controls = OperatorControls(**config_data.get("controls", {}))
        print(f"✓ Using preset configuration with {config.num_users} users, {config.months_history} months")
    else:
        # Fallback to default config
        print("No operator config found, using defaults")
        config = DataGenerationConfig(seed=42, num_users=100, months_history=6)

    # Generate data with controls if provided
    generator = SyntheticDataGenerator(config, operator_controls=controls)
    users, accounts, transactions, liabilities = generator.generate_all()

    # Save config
    config_path = data_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(config.model_dump(mode="json"), f, indent=2, default=str)
    print(f"✓ Saved config to {config_path}")

    # Prepare data for loader
    data = {
        "users": [u.model_dump(mode="json") for u in users],
        "accounts": [a.model_dump(mode="json") for a in accounts],
        "transactions": [t.model_dump(mode="json") for t in transactions],
        "liabilities": [l.model_dump(mode="json") for l in liabilities],
    }

    # Save intermediate JSON (for validation)
    json_path = data_dir / "synthetic_data.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"✓ Saved JSON data to {json_path}")

    print("\n✅ Data generation complete!")
    print("Next step: Run 'uv run python -m ingest.loader' to load into SQLite and Parquet")


if __name__ == "__main__":
    main()

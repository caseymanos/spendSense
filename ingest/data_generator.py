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
    User, Account, Transaction, Liability, DataGenerationConfig,
    AccountType, AccountSubtype, PaymentChannel, Gender, IncomeTier, Region,
    TRANSACTION_CATEGORIES, RECURRING_MERCHANTS, GROCERY_MERCHANTS, RESTAURANT_MERCHANTS
)


class SyntheticDataGenerator:
    """Generate realistic synthetic financial data"""

    def __init__(self, config: DataGenerationConfig):
        self.config = config
        self.fake = Faker()
        Faker.seed(config.seed)
        np.random.seed(config.seed)

        # Date range for transactions
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=30 * config.months_history)

    def generate_users(self) -> List[User]:
        """Generate synthetic users with demographic diversity"""
        users = []

        for i in range(self.config.num_users):
            user = User(
                user_id=f"user_{i:04d}",
                name=self.fake.name(),
                consent_granted=False,  # Default to no consent per PRD
                consent_timestamp=None,
                revoked_timestamp=None,
                age=np.random.randint(18, 76),  # Weighted toward working age
                gender=np.random.choice([g.value for g in Gender]),
                income_tier=np.random.choice([t.value for t in IncomeTier]),
                region=np.random.choice([r.value for r in Region]),
                created_at=datetime.now()
            )
            users.append(user)

        return users

    def generate_accounts(self, users: List[User]) -> List[Account]:
        """Generate 2-4 accounts per user (checking, savings, credit cards)"""
        accounts = []
        account_counter = 0

        for user in users:
            num_accounts = np.random.randint(2, 5)  # 2-4 accounts per user

            # Every user gets a checking account
            checking = Account(
                account_id=f"acc_{account_counter:06d}",
                user_id=user.user_id,
                account_type=AccountType.DEPOSITORY,
                account_subtype=AccountSubtype.CHECKING,
                balance_current=float(np.random.uniform(500, 15000)),
                balance_available=None,
                balance_limit=None,
                iso_currency_code="USD",
                holder_category="consumer",
                mask=f"{np.random.randint(1000, 9999)}",
                name="Checking Account",
                official_name=f"{self.fake.company()} Bank Checking"
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
                    balance_current=float(np.random.uniform(1000, 50000)),
                    balance_available=None,
                    balance_limit=None,
                    iso_currency_code="USD",
                    holder_category="consumer",
                    mask=f"{np.random.randint(1000, 9999)}",
                    name="Savings Account",
                    official_name=f"{self.fake.company()} Bank Savings"
                )
                accounts.append(savings)
                account_counter += 1

            # Many users get 1-2 credit cards
            num_credit_cards = min(num_accounts - 2, np.random.randint(1, 3))
            for _ in range(num_credit_cards):
                credit_limit = float(np.random.choice([2000, 5000, 10000, 15000, 25000]))
                utilization = np.random.uniform(0.1, 0.9)  # 10-90% utilization
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
                    mask=f"{np.random.randint(1000, 9999)}",
                    name="Credit Card",
                    official_name=f"{np.random.choice(['Visa', 'Mastercard', 'Amex'])} {self.fake.company()}"
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
            is_high_spender = np.random.random() < 0.3
            has_subscriptions = np.random.random() < 0.7
            num_transactions = int(self.config.avg_transactions_per_month * self.config.months_history)

            # Adjust for spending profile
            if is_high_spender:
                num_transactions = int(num_transactions * 1.5)

            # Find primary accounts
            checking_accs = [a for a in user_accs if a.account_subtype == AccountSubtype.CHECKING]
            credit_accs = [a for a in user_accs if a.account_type == AccountType.CREDIT]

            primary_checking = checking_accs[0] if checking_accs else None
            primary_credit = credit_accs[0] if credit_accs else None

            # Generate recurring subscriptions
            if has_subscriptions and primary_checking:
                num_subs = np.random.randint(3, 8)
                selected_subs = np.random.choice(RECURRING_MERCHANTS, size=min(num_subs, len(RECURRING_MERCHANTS)), replace=False)

                for merchant in selected_subs:
                    # Generate monthly recurring transaction
                    for month_offset in range(self.config.months_history):
                        trans_date = self.start_date + timedelta(days=30 * month_offset + np.random.randint(1, 28))
                        amount = float(np.random.uniform(5.99, 49.99))

                        transaction = Transaction(
                            transaction_id=f"txn_{transaction_counter:08d}",
                            account_id=primary_checking.account_id,
                            date=trans_date,
                            amount=amount,  # Positive = debit
                            merchant_name=merchant,
                            payment_channel=PaymentChannel.ONLINE,
                            personal_finance_category="GENERAL_SERVICES",
                            personal_finance_subcategory="Subscription Services",
                            pending=False
                        )
                        transactions.append(transaction)
                        transaction_counter += 1

            # Generate regular transactions
            for _ in range(num_transactions):
                # Choose account (70% checking, 30% credit if available)
                if primary_credit and np.random.random() < 0.3:
                    account = primary_credit
                elif primary_checking:
                    account = primary_checking
                else:
                    account = user_accs[0]

                # Generate random transaction date
                days_offset = np.random.randint(0, 30 * self.config.months_history)
                trans_date = self.start_date + timedelta(days=days_offset)

                # Choose category and amount
                category, subcategory = self.fake.random_element(TRANSACTION_CATEGORIES)

                # Special handling for income
                if category == "INCOME":
                    amount = -float(np.random.uniform(2000, 8000))  # Negative = credit
                    merchant_name = f"{self.fake.company()} Payroll"
                    payment_channel = PaymentChannel.OTHER
                elif category == "TRANSFER_IN":
                    amount = -float(np.random.uniform(100, 2000))
                    merchant_name = "Transfer from Savings"
                    payment_channel = PaymentChannel.OTHER
                else:
                    # Regular spending
                    if subcategory == "Groceries":
                        merchant_name = self.fake.random_element(GROCERY_MERCHANTS)
                        amount = float(np.random.uniform(50, 300))
                    elif subcategory == "Restaurants":
                        merchant_name = self.fake.random_element(RESTAURANT_MERCHANTS)
                        amount = float(np.random.uniform(15, 150))
                    else:
                        merchant_name = self.fake.company()
                        amount = float(np.random.uniform(10, 500))

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
                    location_city=self.fake.city() if np.random.random() < 0.5 else None,
                    location_state=self.fake.state_abbr() if np.random.random() < 0.5 else None
                )
                transactions.append(transaction)
                transaction_counter += 1

            # Generate payroll deposits (bi-weekly pattern)
            if primary_checking:
                num_paychecks = (self.config.months_history * 30) // 14  # Every 2 weeks
                for i in range(num_paychecks):
                    paycheck_date = self.start_date + timedelta(days=14 * i)
                    paycheck_amount = -float(np.random.uniform(2000, 6000))  # Negative = credit

                    payroll = Transaction(
                        transaction_id=f"txn_{transaction_counter:08d}",
                        account_id=primary_checking.account_id,
                        date=paycheck_date,
                        amount=paycheck_amount,
                        merchant_name=f"{self.fake.company()} Payroll",
                        payment_channel=PaymentChannel.OTHER,
                        personal_finance_category="INCOME",
                        personal_finance_subcategory="Payroll",
                        pending=False
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
            utilization = account.balance_current / account.balance_limit if account.balance_limit else 0

            # Higher utilization = higher chance of issues
            is_overdue = utilization > 0.8 and np.random.random() < 0.3

            # APR varies by creditworthiness (simulated)
            apr = float(np.random.uniform(12.99, 29.99))

            # Minimum payment (typically 1-3% of balance)
            min_payment = float(max(25, account.balance_current * 0.02))

            liability = Liability(
                liability_id=f"liab_{liability_counter:06d}",
                account_id=account.account_id,
                user_id=account.user_id,
                apr=apr,
                minimum_payment=min_payment,
                last_payment_amount=float(np.random.uniform(min_payment, account.balance_current * 0.5)) if np.random.random() < 0.9 else None,
                last_payment_date=datetime.now() - timedelta(days=np.random.randint(1, 30)),
                next_due_date=datetime.now() + timedelta(days=np.random.randint(1, 30)),
                is_overdue=is_overdue,
                overdue_amount=float(np.random.uniform(25, 200)) if is_overdue else None
            )
            liabilities.append(liability)
            liability_counter += 1

        return liabilities

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

        return users, accounts, transactions, liabilities


def main():
    """CLI entry point for data generation"""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Generate data
    config = DataGenerationConfig(seed=42, num_users=100, months_history=6)
    generator = SyntheticDataGenerator(config)
    users, accounts, transactions, liabilities = generator.generate_all()

    # Save config
    config_path = data_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(config.model_dump(mode='json'), f, indent=2, default=str)
    print(f"✓ Saved config to {config_path}")

    # Prepare data for loader
    data = {
        "users": [u.model_dump(mode='json') for u in users],
        "accounts": [a.model_dump(mode='json') for a in accounts],
        "transactions": [t.model_dump(mode='json') for t in transactions],
        "liabilities": [l.model_dump(mode='json') for l in liabilities]
    }

    # Save intermediate JSON (for validation)
    json_path = data_dir / "synthetic_data.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"✓ Saved JSON data to {json_path}")

    print("\n✅ Data generation complete!")
    print(f"Next step: Run 'uv run python -m ingest.loader' to load into SQLite and Parquet")


if __name__ == "__main__":
    main()

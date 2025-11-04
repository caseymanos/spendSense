"""
Data validators for SpendSense MVP V2.
Validates schema compliance and plausible value ranges.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from pydantic import ValidationError

from ingest.schemas import User, Account, Transaction, Liability


class ValidationReport:
    """Aggregates validation results"""

    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.stats: Dict[str, Any] = {}

    def add_error(self, entity_type: str, entity_id: str, message: str):
        """Add validation error"""
        self.errors.append({
            "type": entity_type,
            "id": entity_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    def add_warning(self, entity_type: str, entity_id: str, message: str):
        """Add validation warning"""
        self.warnings.append({
            "type": entity_type,
            "id": entity_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    def set_stats(self, stats: Dict[str, Any]):
        """Set validation statistics"""
        self.stats = stats

    def is_valid(self) -> bool:
        """Returns True if no errors"""
        return len(self.errors) == 0

    def summary(self) -> str:
        """Generate human-readable summary"""
        lines = [
            "=" * 60,
            "VALIDATION REPORT",
            "=" * 60,
            f"Errors: {len(self.errors)}",
            f"Warnings: {len(self.warnings)}",
            "",
            "Statistics:",
        ]

        for key, value in self.stats.items():
            lines.append(f"  {key}: {value}")

        if self.errors:
            lines.append("\nERRORS:")
            for err in self.errors[:10]:  # Show first 10
                lines.append(f"  [{err['type']}] {err['id']}: {err['message']}")
            if len(self.errors) > 10:
                lines.append(f"  ... and {len(self.errors) - 10} more errors")

        if self.warnings:
            lines.append("\nWARNINGS:")
            for warn in self.warnings[:10]:  # Show first 10
                lines.append(f"  [{warn['type']}] {warn['id']}: {warn['message']}")
            if len(self.warnings) > 10:
                lines.append(f"  ... and {len(self.warnings) - 10} more warnings")

        lines.append("=" * 60)
        return "\n".join(lines)


class DataValidator:
    """Validates synthetic financial data"""

    def __init__(self):
        self.report = ValidationReport()

    def validate_users(self, users: List[Dict[str, Any]]) -> List[User]:
        """Validate user data against schema"""
        validated_users = []

        for user_data in users:
            try:
                user = User(**user_data)
                validated_users.append(user)

                # Additional business logic checks
                if user.consent_granted and user.consent_timestamp is None:
                    self.report.add_warning("User", user.user_id,
                                          "Consent granted but no timestamp")

                if user.revoked_timestamp:
                    # If revoke exists without consent timestamp, flag as error
                    if user.consent_timestamp is None:
                        self.report.add_error(
                            "User",
                            user.user_id,
                            "Revoked timestamp present but consent timestamp is missing",
                        )
                    # If both exist, ensure revoke is not before consent
                    elif user.revoked_timestamp < user.consent_timestamp:
                        self.report.add_error(
                            "User",
                            user.user_id,
                            "Revoked timestamp before consent timestamp",
                        )

            except ValidationError as e:
                self.report.add_error("User", user_data.get("user_id", "unknown"),
                                    f"Schema validation failed: {str(e)}")

        return validated_users

    def validate_accounts(self, accounts: List[Dict[str, Any]]) -> List[Account]:
        """Validate account data"""
        validated_accounts = []

        for acc_data in accounts:
            try:
                account = Account(**acc_data)
                validated_accounts.append(account)

                # Business logic checks
                if account.account_type.value == "depository" and account.balance_current < 0:
                    self.report.add_warning("Account", account.account_id,
                                          f"Negative balance in depository account: ${account.balance_current:.2f}")

                if account.account_type.value == "credit":
                    if account.balance_limit is None:
                        self.report.add_error("Account", account.account_id,
                                            "Credit account missing balance_limit")
                    elif account.balance_limit > 0:
                        utilization = account.balance_current / account.balance_limit
                        if utilization > 1.0:
                            self.report.add_warning("Account", account.account_id,
                                                  f"Over-limit: {utilization*100:.1f}% utilization")

            except ValidationError as e:
                self.report.add_error("Account", acc_data.get("account_id", "unknown"),
                                    f"Schema validation failed: {str(e)}")

        return validated_accounts

    def validate_transactions(self, transactions: List[Dict[str, Any]],
                            accounts: List[Account]) -> List[Transaction]:
        """Validate transaction data"""
        validated_transactions = []
        account_ids = {acc.account_id for acc in accounts}

        # Date range check
        now = datetime.now()
        two_years_ago = now - timedelta(days=730)

        for txn_data in transactions:
            try:
                # Convert date string to datetime if needed
                if isinstance(txn_data.get('date'), str):
                    txn_data['date'] = datetime.fromisoformat(txn_data['date'].replace('Z', '+00:00'))

                transaction = Transaction(**txn_data)
                validated_transactions.append(transaction)

                # Business logic checks
                if transaction.account_id not in account_ids:
                    self.report.add_error("Transaction", transaction.transaction_id,
                                        f"References non-existent account: {transaction.account_id}")

                if transaction.date > now:
                    self.report.add_error("Transaction", transaction.transaction_id,
                                        "Transaction date in the future")

                if transaction.date < two_years_ago:
                    self.report.add_warning("Transaction", transaction.transaction_id,
                                          "Transaction older than 2 years")

                if abs(transaction.amount) < 0.01:
                    self.report.add_warning("Transaction", transaction.transaction_id,
                                          f"Very small amount: ${transaction.amount:.2f}")

            except ValidationError as e:
                self.report.add_error("Transaction", txn_data.get("transaction_id", "unknown"),
                                    f"Schema validation failed: {str(e)}")

        return validated_transactions

    def validate_liabilities(self, liabilities: List[Dict[str, Any]],
                           accounts: List[Account]) -> List[Liability]:
        """Validate liability data"""
        validated_liabilities = []
        account_ids = {acc.account_id for acc in accounts}
        credit_account_ids = {acc.account_id for acc in accounts if acc.account_type.value == "credit"}

        for liab_data in liabilities:
            try:
                # Convert date strings if needed
                for date_field in ['last_payment_date', 'next_due_date']:
                    if isinstance(liab_data.get(date_field), str):
                        liab_data[date_field] = datetime.fromisoformat(liab_data[date_field].replace('Z', '+00:00'))

                liability = Liability(**liab_data)
                validated_liabilities.append(liability)

                # Business logic checks
                if liability.account_id not in account_ids:
                    self.report.add_error("Liability", liability.liability_id,
                                        f"References non-existent account: {liability.account_id}")
                elif liability.account_id not in credit_account_ids:
                    self.report.add_error("Liability", liability.liability_id,
                                        "References non-credit account")

                if liability.is_overdue and not liability.overdue_amount:
                    self.report.add_warning("Liability", liability.liability_id,
                                          "Marked overdue but no overdue_amount specified")

                if liability.apr > 30:
                    self.report.add_warning("Liability", liability.liability_id,
                                          f"Very high APR: {liability.apr:.2f}%")

            except ValidationError as e:
                self.report.add_error("Liability", liab_data.get("liability_id", "unknown"),
                                    f"Schema validation failed: {str(e)}")

        return validated_liabilities

    def validate_all(self, data: Dict[str, List[Dict[str, Any]]]) -> ValidationReport:
        """Validate complete dataset"""
        print("Validating data...")

        # Validate in order of dependencies
        users = self.validate_users(data.get("users", []))
        print(f"✓ Validated {len(users)} users")

        accounts = self.validate_accounts(data.get("accounts", []))
        print(f"✓ Validated {len(accounts)} accounts")

        transactions = self.validate_transactions(data.get("transactions", []), accounts)
        print(f"✓ Validated {len(transactions)} transactions")

        liabilities = self.validate_liabilities(data.get("liabilities", []), accounts)
        print(f"✓ Validated {len(liabilities)} liabilities")

        # Compute statistics
        self.report.set_stats({
            "users_validated": len(users),
            "accounts_validated": len(accounts),
            "transactions_validated": len(transactions),
            "liabilities_validated": len(liabilities),
            "total_records": len(users) + len(accounts) + len(transactions) + len(liabilities),
            "validation_timestamp": datetime.now().isoformat()
        })

        return self.report


def validate_data_file(file_path: str) -> ValidationReport:
    """Convenience function to validate data from JSON file"""
    import json
    from pathlib import Path

    with open(file_path, 'r') as f:
        data = json.load(f)

    validator = DataValidator()
    report = validator.validate_all(data)

    print("\n" + report.summary())

    return report

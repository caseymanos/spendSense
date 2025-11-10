"""
Data loader for SpendSense MVP V2.
Loads validated data into SQLite (relational) and Parquet (analytics).
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd

from ingest.validators import DataValidator


class DataLoader:
    """Loads synthetic data into storage"""

    def __init__(
        self,
        sqlite_path: str = "data/users.sqlite",
        parquet_path: str = "data/transactions.parquet",
    ):
        self.sqlite_path = Path(sqlite_path)
        self.parquet_path = Path(parquet_path)

        # Ensure data directory exists
        self.sqlite_path.parent.mkdir(exist_ok=True)
        self.parquet_path.parent.mkdir(exist_ok=True)

    def create_sqlite_schema(self, conn: sqlite3.Connection):
        """Create SQLite database schema"""
        cursor = conn.cursor()

        # Users table with consent tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                consent_granted INTEGER DEFAULT 0,
                consent_timestamp TEXT,
                revoked_timestamp TEXT,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                income_tier TEXT NOT NULL,
                region TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """
        )

        # Accounts table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                account_type TEXT NOT NULL,
                account_subtype TEXT NOT NULL,
                balance_current REAL NOT NULL,
                balance_available REAL,
                balance_limit REAL,
                iso_currency_code TEXT DEFAULT 'USD',
                holder_category TEXT DEFAULT 'consumer',
                mask TEXT NOT NULL,
                name TEXT NOT NULL,
                official_name TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """
        )

        # Transactions table (minimal - full data in Parquet)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                merchant_name TEXT NOT NULL,
                payment_channel TEXT NOT NULL,
                personal_finance_category TEXT NOT NULL,
                pending INTEGER DEFAULT 0,
                FOREIGN KEY (account_id) REFERENCES accounts (account_id)
            )
        """
        )

        # Liabilities table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS liabilities (
                liability_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                apr REAL NOT NULL,
                minimum_payment REAL NOT NULL,
                last_payment_amount REAL,
                last_payment_date TEXT,
                next_due_date TEXT,
                is_overdue INTEGER DEFAULT 0,
                overdue_amount REAL,
                FOREIGN KEY (account_id) REFERENCES accounts (account_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """
        )

        # Persona assignments table (populated by PR #3)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS persona_assignments (
                assignment_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                persona TEXT NOT NULL,
                criteria_met TEXT,
                assigned_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """
        )

        # Recommendations table (stores pre-generated recommendations)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recommendations (
                user_id TEXT PRIMARY KEY,
                persona TEXT NOT NULL,
                recommendations_json TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """
        )

        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_user ON accounts(user_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_liabilities_user ON liabilities(user_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_persona_user ON persona_assignments(user_id)"
        )

        conn.commit()

    def load_users(self, conn: sqlite3.Connection, users: List[Dict[str, Any]]):
        """Load users into SQLite"""
        cursor = conn.cursor()

        for user_data in users:
            cursor.execute(
                """
                INSERT OR REPLACE INTO users (
                    user_id, name, consent_granted, consent_timestamp, revoked_timestamp,
                    age, gender, income_tier, region, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    user_data["user_id"],
                    user_data["name"],
                    1 if user_data["consent_granted"] else 0,
                    user_data.get("consent_timestamp"),
                    user_data.get("revoked_timestamp"),
                    user_data["age"],
                    user_data["gender"],
                    user_data["income_tier"],
                    user_data["region"],
                    user_data["created_at"],
                ),
            )

        conn.commit()

    def load_accounts(self, conn: sqlite3.Connection, accounts: List[Dict[str, Any]]):
        """Load accounts into SQLite"""
        cursor = conn.cursor()

        for acc_data in accounts:
            cursor.execute(
                """
                INSERT OR REPLACE INTO accounts (
                    account_id, user_id, account_type, account_subtype,
                    balance_current, balance_available, balance_limit,
                    iso_currency_code, holder_category, mask, name, official_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    acc_data["account_id"],
                    acc_data["user_id"],
                    acc_data["account_type"],
                    acc_data["account_subtype"],
                    acc_data["balance_current"],
                    acc_data.get("balance_available"),
                    acc_data.get("balance_limit"),
                    acc_data.get("iso_currency_code", "USD"),
                    acc_data.get("holder_category", "consumer"),
                    acc_data["mask"],
                    acc_data["name"],
                    acc_data.get("official_name"),
                ),
            )

        conn.commit()

    def load_transactions(self, conn: sqlite3.Connection, transactions: List[Dict[str, Any]]):
        """Load transactions into SQLite (metadata only)"""
        cursor = conn.cursor()

        for txn_data in transactions:
            # Convert datetime to ISO string if needed
            date_str = txn_data["date"]
            if isinstance(date_str, datetime):
                date_str = date_str.isoformat()

            cursor.execute(
                """
                INSERT OR REPLACE INTO transactions (
                    transaction_id, account_id, date, amount,
                    merchant_name, payment_channel, personal_finance_category, pending
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    txn_data["transaction_id"],
                    txn_data["account_id"],
                    date_str,
                    txn_data["amount"],
                    txn_data["merchant_name"],
                    txn_data["payment_channel"],
                    txn_data["personal_finance_category"],
                    1 if txn_data.get("pending", False) else 0,
                ),
            )

        conn.commit()

    def load_liabilities(self, conn: sqlite3.Connection, liabilities: List[Dict[str, Any]]):
        """Load liabilities into SQLite"""
        cursor = conn.cursor()

        for liab_data in liabilities:
            # Convert datetime fields
            last_payment_date = liab_data.get("last_payment_date")
            if isinstance(last_payment_date, datetime):
                last_payment_date = last_payment_date.isoformat()

            next_due_date = liab_data.get("next_due_date")
            if isinstance(next_due_date, datetime):
                next_due_date = next_due_date.isoformat()

            cursor.execute(
                """
                INSERT OR REPLACE INTO liabilities (
                    liability_id, account_id, user_id, apr, minimum_payment,
                    last_payment_amount, last_payment_date, next_due_date,
                    is_overdue, overdue_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    liab_data["liability_id"],
                    liab_data["account_id"],
                    liab_data["user_id"],
                    liab_data["apr"],
                    liab_data["minimum_payment"],
                    liab_data.get("last_payment_amount"),
                    last_payment_date,
                    next_due_date,
                    1 if liab_data.get("is_overdue", False) else 0,
                    liab_data.get("overdue_amount"),
                ),
            )

        conn.commit()

    def export_transactions_parquet(self, transactions: List[Dict[str, Any]]):
        """Export transactions to Parquet for analytics"""
        # Convert to DataFrame
        df = pd.DataFrame(transactions)

        # Convert datetime columns
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])

        # Write to Parquet with compression
        df.to_parquet(self.parquet_path, engine="pyarrow", compression="snappy", index=False)

    def load_all(self, data: Dict[str, List[Dict[str, Any]]]):
        """Load all data into storage"""
        print(f"Loading data into SQLite: {self.sqlite_path}")

        # Connect to SQLite
        conn = sqlite3.connect(self.sqlite_path)

        try:
            # Create schema
            self.create_sqlite_schema(conn)
            print("✓ Created database schema")

            # Load data
            self.load_users(conn, data["users"])
            print(f"✓ Loaded {len(data['users'])} users")

            self.load_accounts(conn, data["accounts"])
            print(f"✓ Loaded {len(data['accounts'])} accounts")

            self.load_transactions(conn, data["transactions"])
            print(f"✓ Loaded {len(data['transactions'])} transactions (SQLite)")

            self.load_liabilities(conn, data["liabilities"])
            print(f"✓ Loaded {len(data['liabilities'])} liabilities")

            # Export transactions to Parquet
            print(f"\nExporting transactions to Parquet: {self.parquet_path}")
            self.export_transactions_parquet(data["transactions"])
            print(f"✓ Exported {len(data['transactions'])} transactions (Parquet)")

        finally:
            conn.close()

        print("\n✅ Data loading complete!")


def main():
    """CLI entry point for data loading"""
    import sys

    # Load JSON data
    json_path = Path("data/synthetic_data.json")
    if not json_path.exists():
        print(f"❌ Error: {json_path} not found")
        print("Run 'uv run python -m ingest.data_generator' first")
        sys.exit(1)

    with open(json_path, "r") as f:
        data = json.load(f)

    # Validate data
    print("Step 1: Validating data...")
    validator = DataValidator()
    report = validator.validate_all(data)

    if not report.is_valid():
        print("\n" + report.summary())
        print("\n❌ Validation failed. Please fix errors before loading.")
        sys.exit(1)

    print(f"✓ Validation passed: {report.stats['total_records']} records")

    # Load data
    print("\nStep 2: Loading data into storage...")
    loader = DataLoader()
    loader.load_all(data)

    # Verify files exist
    print("\nStep 3: Verifying output files...")
    if loader.sqlite_path.exists():
        print(
            f"✓ SQLite database: {loader.sqlite_path} ({loader.sqlite_path.stat().st_size / 1024:.1f} KB)"
        )
    if loader.parquet_path.exists():
        print(
            f"✓ Parquet file: {loader.parquet_path} ({loader.parquet_path.stat().st_size / 1024:.1f} KB)"
        )

    print("\n✅ All data loaded successfully!")
    print("\nYou can now:")
    print("  - Query SQLite: sqlite3 data/users.sqlite")
    print(
        "  - Analyze Parquet: python -c 'import pandas as pd; df = pd.read_parquet(\"data/transactions.parquet\"); print(df.head())'"
    )


if __name__ == "__main__":
    main()

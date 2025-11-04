# Data Schema Documentation

**SpendSense MVP V2 - Data Model**

Last Updated: 2025-11-03

## Overview

SpendSense uses a Plaid-compatible data model with four core entities: Users, Accounts, Transactions, and Liabilities. Data is stored in SQLite for relational queries and Parquet for analytics.

## Storage Architecture

| Store | Purpose | Format | Location |
|-------|---------|--------|----------|
| SQLite | Relational queries, consent tracking | Normalized tables | `data/users.sqlite` |
| Parquet | Analytics, feature extraction | Columnar | `data/transactions.parquet` |
| JSON | Audit logs, decision traces | Documents | `docs/traces/` |

---

## Entity Schemas

### 1. Users

Stores user profiles with consent tracking and demographic data.

**Table:** `users`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | TEXT | ✓ | Unique identifier (e.g., `user_0001`) |
| `name` | TEXT | ✓ | Full name (synthetic via Faker) |
| `consent_granted` | INTEGER | ✓ | 0=no consent, 1=consent granted |
| `consent_timestamp` | TEXT | | ISO timestamp when consent granted |
| `revoked_timestamp` | TEXT | | ISO timestamp when consent revoked |
| `age` | INTEGER | ✓ | Age in years (18-100) |
| `gender` | TEXT | ✓ | `male`, `female`, `non_binary`, `prefer_not_to_say` |
| `income_tier` | TEXT | ✓ | `low`, `medium`, `high` |
| `region` | TEXT | ✓ | `northeast`, `south`, `midwest`, `west` |
| `created_at` | TEXT | ✓ | Record creation timestamp |

**Important:**
- Demographic fields (`age`, `gender`, `income_tier`, `region`) are used ONLY for fairness metrics, NOT for persona assignment logic
- Default `consent_granted = 0` per PRD requirements

**Example:**
```json
{
  "user_id": "user_0001",
  "name": "John Doe",
  "consent_granted": false,
  "age": 34,
  "gender": "male",
  "income_tier": "medium",
  "region": "west",
  "created_at": "2025-11-03T10:00:00"
}
```

---

### 2. Accounts

Bank accounts associated with users (Plaid-style).

**Table:** `accounts`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account_id` | TEXT | ✓ | Unique identifier (e.g., `acc_000001`) |
| `user_id` | TEXT | ✓ | Owner user ID (FK to users) |
| `account_type` | TEXT | ✓ | `depository`, `credit`, `loan`, `investment` |
| `account_subtype` | TEXT | ✓ | `checking`, `savings`, `credit card`, `paypal` |
| `balance_current` | REAL | ✓ | Current balance |
| `balance_available` | REAL | | Available balance |
| `balance_limit` | REAL | | Credit limit (credit accounts only) |
| `iso_currency_code` | TEXT | | Currency code (default: `USD`) |
| `holder_category` | TEXT | | `consumer` or `business` |
| `mask` | TEXT | ✓ | Last 4 digits of account number |
| `name` | TEXT | ✓ | Account display name |
| `official_name` | TEXT | | Official institution name |

**Account Types:**
- **Depository:** Checking and savings accounts
- **Credit:** Credit cards with limits
- **Loan:** Personal/auto loans (future)
- **Investment:** Brokerage accounts (future)

**Example:**
```json
{
  "account_id": "acc_000001",
  "user_id": "user_0001",
  "account_type": "credit",
  "account_subtype": "credit card",
  "balance_current": 3400.0,
  "balance_available": 1600.0,
  "balance_limit": 5000.0,
  "mask": "4523",
  "name": "Credit Card",
  "official_name": "Visa Chase"
}
```

---

### 3. Transactions

Financial transactions (full schema in Parquet, minimal in SQLite).

**Parquet Columns:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transaction_id` | string | ✓ | Unique identifier |
| `account_id` | string | ✓ | Associated account (FK) |
| `date` | datetime | ✓ | Transaction date |
| `amount` | float | ✓ | Amount (positive=debit, negative=credit) |
| `merchant_name` | string | ✓ | Merchant name |
| `payment_channel` | string | ✓ | `online`, `in store`, `other` |
| `personal_finance_category` | string | ✓ | Category (e.g., `FOOD_AND_DRINK`) |
| `personal_finance_subcategory` | string | | Subcategory (e.g., `Restaurants`) |
| `pending` | boolean | | Is transaction pending |
| `location_city` | string | | Transaction city |
| `location_state` | string | | Transaction state |

**Categories:**
- `FOOD_AND_DRINK` (Restaurants, Groceries)
- `GENERAL_MERCHANDISE` (Superstores, Online)
- `TRANSPORTATION` (Gas, Public Transit)
- `ENTERTAINMENT` (Streaming, Movies)
- `INCOME` (Payroll)
- `TRANSFER_IN` / `TRANSFER_OUT`

**Amount Convention:**
- Positive = money leaving account (debit)
- Negative = money entering account (credit)

**Example:**
```json
{
  "transaction_id": "txn_00000001",
  "account_id": "acc_000001",
  "date": "2025-09-15T10:30:00",
  "amount": 15.99,
  "merchant_name": "Netflix",
  "payment_channel": "online",
  "personal_finance_category": "GENERAL_SERVICES",
  "personal_finance_subcategory": "Subscription Services",
  "pending": false
}
```

---

### 4. Liabilities

Credit account liability information.

**Table:** `liabilities`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `liability_id` | TEXT | ✓ | Unique identifier |
| `account_id` | TEXT | ✓ | Associated credit account (FK) |
| `user_id` | TEXT | ✓ | Owner user ID (FK) |
| `apr` | REAL | ✓ | Annual Percentage Rate (0-100) |
| `minimum_payment` | REAL | ✓ | Minimum payment amount |
| `last_payment_amount` | REAL | | Last payment amount |
| `last_payment_date` | TEXT | | Last payment timestamp |
| `next_due_date` | TEXT | | Next payment due date |
| `is_overdue` | INTEGER | | 0=current, 1=overdue |
| `overdue_amount` | REAL | | Amount overdue (if applicable) |

**Example:**
```json
{
  "liability_id": "liab_000001",
  "account_id": "acc_000001",
  "user_id": "user_0001",
  "apr": 18.99,
  "minimum_payment": 68.00,
  "is_overdue": false
}
```

---

## Relationships

```
User (1) ──< (N) Accounts
     │
     └──< (N) Liabilities

Account (1) ──< (N) Transactions
        │
        └──< (1) Liability (if credit account)
```

---

## Data Generation

- **Tool:** `ingest/data_generator.py`
- **Seed:** 42 (deterministic)
- **Volume:** 100 users, ~180 transactions each over 6 months
- **Patterns:** Recurring subscriptions, bi-weekly payroll, variable spending

---

## Validation Rules

Enforced by `ingest/validators.py`:

1. **Schema:** All required fields present, correct types
2. **Ranges:** Balances between -$100k and $1M, APR 0-100%
3. **Referential:** Account IDs exist, credit accounts have liabilities
4. **Temporal:** Dates within 2-year window, no future dates
5. **Business Logic:** Depository accounts non-negative, utilization ≤ 100%

---

## Indexes

SQLite indexes for performance:
- `idx_accounts_user` on `accounts(user_id)`
- `idx_transactions_account` on `transactions(account_id)`
- `idx_transactions_date` on `transactions(date)`
- `idx_liabilities_user` on `liabilities(user_id)`

---

## Privacy & Security

- **No Real PII:** All data synthetic via Faker
- **Consent Gating:** Processing blocked if `consent_granted = 0`
- **Audit Trail:** All consent changes timestamped
- **Demographics:** Used only for fairness metrics, not persona logic

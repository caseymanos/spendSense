# Known Issues - SpendSense MVP V2

## P0 Issues (FIXED - 2025-11-03)

### ✅ Issue #1: Percentage Format Mismatch
**Status:** FIXED in commit 9f8ca0f
**Severity:** P0 - Critical
**Impact:** Thresholds were 100x too low, causing incorrect persona assignments

**Problem:**
- Feature modules output percentages in percentage format (12.0 = 12%)
- Constants used decimal format (0.10 = 10%)
- Comparison: `12.0 >= 0.10` always passed (should be `12.0 >= 10.0`)

**Files Affected:**
- `ingest/constants.py` - PERSONA_THRESHOLDS
- `tests/test_personas.py` - Test values

**Fix Applied:**
- Changed `recurring_spend_pct: 0.10 → 10.0`
- Changed `growth_rate_pct: 0.02 → 2.0`
- Credit utilization thresholds expressed as percentages (e.g., 30.0, 50.0, 80.0)
- Tests validate percent-form comparisons in `tests/test_personas.py`

**Evidence:**
```python
# Feature output (subscriptions.py line 93):
subscription_share_pct = (total_recurring_spend / total_spend * 100)
# Outputs: 12.0 for 12% share

# Feature output (savings.py line 79):
growth_rate_pct = ((current - beginning) / beginning * 100)
# Outputs: 2.5 for 2.5% growth

# Feature output (credit.py line 68):
utilization = (balance / limit) * 100
# Outputs: 68.0 for 68% utilization
```

---

### ✅ Issue #2: Subscription Lookback Not Honored (and 30d regression)
**Status:** FIXED in commits dbf310d, 3887c0d
**Severity:** P0 - Critical
**Impact:** Long-span occurrences in 180d caused false positives; later a 30-day minimum span broke the 30d signal

**Problem:**
- Original detector didn’t enforce the configured 90-day lookback in the 180-day window
- A subsequent change introduced a hard 30-day minimum span, disabling the 30-day window

**Fix Applied (final):** Honor lookback while keeping 30-day window functional
```python
# Enforce maximum allowed span based on config and window
days_span = (row['last_date'] - row['first_date']).days
max_allowed_span = min(lookback_days, window_days)
if days_span > max_allowed_span:
    continue
```

**Impact:**
- Prevents false positives from sparse occurrences across long windows
- Preserves short-window (30d) detection behavior

---

## P1 Issues (Data Generation - TO BE FIXED)

### Issue #3: Variable Subscription Amounts
**Status:** OPEN
**Severity:** P1 - High
**Impact:** Zero subscriptions detected despite data containing 3,676 subscription transactions

**Problem:**
Data generator created highly variable subscription amounts that failed variance checks.

**Evidence:**
```
WSJ charges for user_0000:
- $6.72, $49.69, $11.57, $45.47, $29.58, $33.35
- Variance: ~75% (exceeds 10% threshold)
- Should be: $29.99, $29.99, $29.99... (consistent)
```

**Fix Applied:**
- Added fixed prices for common recurring merchants in `ingest/constants.py` (SUBSCRIPTION_PRICES)
- Generator now uses fixed prices with minor ±2% jitter for realism
  - Ensures variance stays within 10% threshold for detection

**Files:**
- `ingest/constants.py`
- `ingest/data_generator.py`

**Recommended Fix:**
Create fixed price dictionary for subscription services:
```python
SUBSCRIPTION_PRICES = {
    'Netflix': 15.99,
    'Spotify': 9.99,
    'Adobe Creative Cloud': 52.99,
    'Amazon Prime': 14.99,
    'WSJ': 29.99,
    # etc.
}
```

**Expected Outcome After Fix (target):**
- A meaningful portion of users classified as subscription_heavy when consistent recurring charges exist
- Current synthetic data under-detects due to amount variability

---

### Issue #4: Uniform Income Patterns
**Status:** OPEN
**Severity:** P1 - High
**Impact:** Zero users assigned to variable_income persona

**Problem:**
All users have bi-weekly payroll deposits (14-day intervals).

**Current State:**
- 100% of users: 14-day pay gap
- Threshold: >45 days required
- Result: 0% match variable_income criteria

**File to Fix:**
- `ingest/data_generator.py` - Payroll generation logic

**Fix Applied:**
- Added diversified pay patterns (weekly/biweekly/monthly/irregular) per user with deterministic RNG

**Files:**
- `ingest/data_generator.py`

**Expected Outcome After Fix (target):**
- A reasonable share of users assigned to variable_income based on diversified patterns

---

### Issue #5: Overly Broad High Utilization Criteria
**Status:** OPEN
**Severity:** P2 - Medium
**Impact:** 67% of users assigned to high_utilization (may be too high)

**Problem:**
Persona criteria: `utilization ≥50% OR interest >0 OR min-payment OR overdue`

**Current State:**
- 100% of credit card holders have APR > 0 (interest charges possible)
- This alone triggers high_utilization persona
- Works as designed per PRD, but very broad

**Analysis:**
- 82 users (82%) have credit cards
- All 82 have APR > 0 → triggers "has_interest" check
- 67 users (67%) assigned high_utilization
- 15 users without credit cards → general persona

**Potential Fix (Optional):**
Consider checking for ACTUAL interest charges in transactions, not just APR > 0:
```python
# Instead of:
has_interest = liability['apr'] > 0

# Use:
has_interest = actual_interest_charges_in_transactions > 0
```

**Or tighten utilization threshold:**
- Current: 50% (catches 43% of cards)
- Alternative: 60% or 70% (more stringent)

**Expected Outcome:**
- More balanced distribution
- Some high-utilization users could be re-classified to savings_builder or subscription_heavy

---

## P2 Issues (Minor/Future)

### Issue #6: Savings Builder Blocked by Utilization Requirement
**Status:** OPEN
**Severity:** P2 - Low
**Impact:** Zero users assigned to savings_builder persona

**Problem:**
Criteria: `(growth ≥2% OR inflow ≥$200) AND utilization <30%`

**Analysis:**
- 77% of credit cards have utilization ≥30% (fail threshold)
- Users with <30% utilization already claimed by high_utilization (priority 1, APR > 0)
- Very few users can qualify

**Potential Fix:**
- Adjust credit data generation (more users with <30% utilization)
- OR reconsider strict <30% requirement
- OR check if user meets savings criteria despite utilization

---

## Summary

### Fixed (P0):
- ✅ Percentage format inconsistency (9f8ca0f)
- ✅ Subscription lookback honored and 30d window preserved (dbf310d, 3887c0d)

### Open (P1 - Data Generation):
- ⏳ Variable subscription amounts (blocks subscription_heavy detection)
- ⏳ Uniform income patterns (blocks variable_income detection)
- ⏳ Overly broad high_utilization criteria

### Open (P2 - Design):
- ⏳ Savings builder blocked by combined requirements

### Current Persona Distribution:
- Note: Distribution varies with data generation. Prior runs showed high share for high_utilization and low/zero for others due to generator constraints noted above.

### Test Status:
- 39/39 tests passing ✅
- All P0 fixes validated
- Ready for P1 data generation improvements (optional for MVP)

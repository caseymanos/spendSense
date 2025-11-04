# Data Generator Operator Guide

## Overview

The SpendSense data generator has been overhauled to provide production-level operator controls for generating synthetic transaction data with **persona targeting** and **granular behavioral pattern manipulation**.

This allows operators to:
- Generate datasets skewed toward specific personas
- Test persona overlap scenarios
- Fine-tune behavioral patterns (credit utilization, subscriptions, savings, income)
- Create reproducible test datasets for QA and development

## Quick Start

### Basic Generation (Natural Distribution)

```bash
# Generate default dataset
uv run python -m ingest
```

### Persona-Targeted Generation

```python
from ingest.schemas import DataGenerationConfig
from ingest.operator_controls import OperatorControls, PersonaTarget
from ingest.persona_skewed_generator import PersonaSkewedGenerator

# Configure generation
config = DataGenerationConfig(
    seed=42,
    num_users=100,
    months_history=6,
    avg_transactions_per_month=30
)

# Target high utilization users
controls = OperatorControls(
    target_personas=[PersonaTarget.HIGH_UTILIZATION],
    credit_utilization_distribution={
        "low": 0.1,
        "medium": 0.2,
        "high": 0.4,
        "critical": 0.3,
    }
)

# Generate
generator = PersonaSkewedGenerator(config, controls)
users, accounts, transactions, liabilities = generator.generate_all()
```

## Operator Controls

### Persona Targeting

Select one or more personas to skew data generation:

```python
controls = OperatorControls(
    target_personas=[
        PersonaTarget.HIGH_UTILIZATION,
        PersonaTarget.SUBSCRIPTION_HEAVY,
        PersonaTarget.VARIABLE_INCOME
    ],
    persona_weights={
        "high_utilization": 0.40,
        "subscription_heavy": 0.35,
        "variable_income": 0.25
    }
)
```

#### Available Personas

| Persona | Description | Key Characteristics |
|---------|-------------|---------------------|
| `HIGH_UTILIZATION` | Credit strain | Credit util ≥50%, interest charges, overdue payments |
| `VARIABLE_INCOME` | Income instability | Irregular payroll, unstable cash flow, low buffer |
| `SUBSCRIPTION_HEAVY` | High recurring spend | 3+ subscriptions, significant monthly cost |
| `SAVINGS_BUILDER` | Positive savings behavior | Regular transfers, low utilization, growth |
| `GENERAL` | Baseline behavior | No specific patterns |

### Behavioral Pattern Controls

#### Credit Behavior

```python
controls = OperatorControls(
    credit_utilization_distribution={
        "low": 0.40,      # <30% utilization
        "medium": 0.35,   # 30-50%
        "high": 0.20,     # 50-80%
        "critical": 0.05  # >80%
    },
    overdue_probability=0.15,           # 15% of high-util accounts overdue
    min_payment_only_probability=0.25   # 25% make minimum payments only
)
```

#### Income Patterns

```python
controls = OperatorControls(
    payroll_pattern_distribution={
        "weekly": 0.15,
        "biweekly": 0.30,
        "monthly": 0.25,
        "irregular": 0.30
    },
    irregular_income_volatility=0.5  # 0=stable, 1=highly variable
)
```

#### Subscription Patterns

```python
controls = OperatorControls(
    subscription_adoption_rate=0.60,        # 60% of users have subscriptions
    subscription_count_min=3,               # Min subscriptions for heavy users
    subscription_count_max=6,               # Max subscriptions
    subscription_monthly_spend_range=(30.0, 150.0)  # Monthly spend range
)
```

#### Savings Behavior

```python
controls = OperatorControls(
    savings_adoption_rate=0.40,            # 40% make regular transfers
    savings_transfer_range=(100.0, 400.0), # Monthly transfer amounts
    savings_growth_target_pct=5.0          # Target 5% growth over 6 months
)
```

#### Account Structure

```python
controls = OperatorControls(
    accounts_per_user_distribution={
        "2": 0.25,  # Checking + Savings only
        "3": 0.50,  # + 1 credit card
        "4": 0.25   # + 2 credit cards
    },
    credit_card_probability=0.75  # 75% have at least one credit card
)
```

## Preset Configurations

Pre-configured scenarios for common testing needs:

### Available Presets

```python
from ingest.operator_controls import PRESET_CONFIGS

# High utilization focus
controls = PRESET_CONFIGS["high_utilization_focus"]

# Variable income focus
controls = PRESET_CONFIGS["variable_income_focus"]

# Subscription heavy focus
controls = PRESET_CONFIGS["subscription_heavy_focus"]

# Savings builder focus
controls = PRESET_CONFIGS["savings_builder_focus"]

# Multi-persona overlap testing
controls = PRESET_CONFIGS["overlap_testing"]
```

## Testing Persona Overlap

To test scenarios where users exhibit multiple persona characteristics:

```python
controls = OperatorControls(
    target_personas=[
        PersonaTarget.HIGH_UTILIZATION,
        PersonaTarget.SUBSCRIPTION_HEAVY
    ],
    persona_weights={
        "high_utilization": 0.6,
        "subscription_heavy": 0.4
    },
    # Mix behaviors to create natural overlaps
    subscription_adoption_rate=0.85,
    credit_utilization_distribution={
        "low": 0.15,
        "medium": 0.25,
        "high": 0.35,
        "critical": 0.25
    }
)
```

This will create:
- 60% of users targeted for high utilization
- 40% targeted for subscription heavy
- Many users will exhibit both characteristics (overlap)

## NiceGUI Operator Interface

### Launching the Dashboard

```bash
uv run python ui/app_operator_nicegui.py
```

Navigate to: http://localhost:8081

### Data Generation Tab Features

1. **Quick Start Presets** - Load pre-configured scenarios
2. **Basic Configuration** - Seed, user count, history, transaction volume
3. **Persona Targeting** - Multi-select personas with visual weights
4. **Advanced Behavioral Controls** - Expandable section with:
   - Credit behavior sliders
   - Subscription pattern controls
   - Savings behavior settings
   - Income pattern distributions
5. **Live Preview** - Real-time JSON preview of configuration
6. **Validation** - Pre-flight validation before generation
7. **Export/Import** - Save and load configurations

### Workflow

1. Select a preset or configure manually
2. Choose target personas (or leave empty for natural distribution)
3. Adjust behavioral controls as needed
4. Review preview panel
5. Click "Generate Data"
6. Monitor status and refresh dashboard

## Configuration File Structure

Configurations are saved to `data/operator_config.json`:

```json
{
  "config": {
    "seed": 42,
    "num_users": 100,
    "months_history": 6,
    "avg_transactions_per_month": 30,
    "generation_timestamp": "2025-11-04T..."
  },
  "controls": {
    "target_personas": ["high_utilization", "subscription_heavy"],
    "persona_weights": {
      "high_utilization": 0.6,
      "subscription_heavy": 0.4
    },
    "subscription_adoption_rate": 0.75,
    "credit_utilization_distribution": {
      "low": 0.15,
      "medium": 0.25,
      "high": 0.35,
      "critical": 0.25
    },
    ...
  }
}
```

## CLI Usage

### Generate with Config File

```bash
# Save config to data/operator_config.json, then:
uv run python -m ingest
```

The generator will automatically load operator controls from the config file.

### Programmatic Usage

```python
import json
from pathlib import Path
from ingest.schemas import DataGenerationConfig
from ingest.operator_controls import OperatorControls, PersonaTarget
from ingest.persona_skewed_generator import PersonaSkewedGenerator
from ingest.loader import DataLoader

# Create config
config = DataGenerationConfig(seed=42, num_users=50, months_history=3)
controls = OperatorControls(
    target_personas=[PersonaTarget.HIGH_UTILIZATION]
)

# Save config
config_data = {
    "config": config.model_dump(mode="json"),
    "controls": controls.model_dump(mode="json")
}
Path("data/operator_config.json").write_text(json.dumps(config_data, indent=2, default=str))

# Generate
generator = PersonaSkewedGenerator(config, controls)
users, accounts, transactions, liabilities = generator.generate_all()

# Load to database
data = {
    "users": [u.model_dump(mode="json") for u in users],
    "accounts": [a.model_dump(mode="json") for a in accounts],
    "transactions": [t.model_dump(mode="json") for t in transactions],
    "liabilities": [l.model_dump(mode="json") for l in liabilities],
}

loader = DataLoader()
loader.load_all(data)
```

## Validation

All configurations are validated via Pydantic:

```python
from ingest.operator_controls import OperatorControls

# This will raise ValidationError
controls = OperatorControls(
    persona_weights={"high_utilization": 0.5}  # Must sum to 1.0
)

# This will work
controls = OperatorControls(
    persona_weights={"high_utilization": 1.0}  # Valid
)
```

Common validation rules:
- Distribution dicts must sum to 1.0 (±0.01 tolerance)
- Probabilities must be 0.0-1.0
- User count must be 10-1000
- Months history must be 1-24

## Testing

Comprehensive test suite included:

```bash
# Run all persona-skewed generation tests
uv run pytest tests/test_persona_skewed_generation.py -v

# Run with coverage
uv run pytest tests/test_persona_skewed_generation.py --cov=ingest -v
```

Test coverage includes:
- Operator control validation
- Persona targeting accuracy
- Behavioral pattern generation
- Deterministic generation (seed-based)
- Multi-persona overlaps
- Preset configurations
- Full pipeline integration

## Best Practices

### 1. Start with Presets

Use preset configurations as starting points:

```python
from ingest.operator_controls import PRESET_CONFIGS

controls = PRESET_CONFIGS["high_utilization_focus"]
# Adjust specific parameters as needed
controls.overdue_probability = 0.25
```

### 2. Use Deterministic Seeds

For reproducible test datasets:

```python
config = DataGenerationConfig(seed=42)  # Always use same seed
```

### 3. Test with Small Datasets First

```python
config = DataGenerationConfig(num_users=20, months_history=2)
```

### 4. Verify Downstream Personas

After generation, run persona assignment to verify targeting:

```bash
uv run python -m features  # Run feature detection
# Check docs/traces/*.json for assigned personas
```

### 5. Export Configurations

Save successful configurations for reuse:

```python
controls._export_config("configs/test_scenario_1.json")
```

## Troubleshooting

### Low Persona Coverage

**Issue**: Generated data doesn't result in expected personas

**Solutions**:
- Increase the strength of behavioral signals
- Verify thresholds in `ingest/constants.py`
- Check persona priority order (high_utilization wins conflicts)

### Distribution Not Summing to 1.0

**Issue**: Validation error about distribution sums

**Solution**:
```python
# Ensure distributions sum to 1.0
distribution = {"low": 0.3, "medium": 0.3, "high": 0.4}
assert abs(sum(distribution.values()) - 1.0) < 0.01
```

### Persona Overlap Too High

**Issue**: Too many users match multiple personas

**Solution**:
- Reduce behavioral signal overlap
- Use more distinct persona targets
- Adjust persona detection thresholds

### Not Enough Credit Cards

**Issue**: Savings builder targeting but no credit data

**Solution**:
```python
controls = OperatorControls(
    target_personas=[PersonaTarget.SAVINGS_BUILDER],
    credit_card_probability=0.9,  # Ensure credit cards exist
    accounts_per_user_distribution={"3": 0.5, "4": 0.5}  # Avoid 2-account users
)
```

## Performance Notes

- Generation time scales linearly with `num_users × months_history × avg_transactions`
- SQLite write performance: ~50K transactions/second
- Parquet write performance: ~100K transactions/second
- Typical 100-user, 6-month dataset: <5 seconds total

## Future Enhancements

Planned features:
- [ ] Custom merchant lists
- [ ] Category spending ratios (groceries vs. dining vs. entertainment)
- [ ] Multi-account holders (joint accounts, business + personal)
- [ ] Transaction amount distributions (currently uniform)
- [ ] Seasonal spending patterns (holidays, back-to-school)
- [ ] Geographic clustering (regional merchants)

## Support

For issues or questions:
- Check existing tests: `tests/test_persona_skewed_generation.py`
- Review examples in `ingest/operator_controls.py` (PRESET_CONFIGS)
- Consult main docs: `docs/SpendSense MVP V2.md`

## References

- **Personas**: `docs/SpendSense MVP V2.md` - Section 6.1
- **Feature Detection**: `docs/SpendSense MVP V2.md` - Section 5
- **Thresholds**: `ingest/constants.py`
- **Schemas**: `ingest/schemas.py`

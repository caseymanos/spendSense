"""
Personas module for SpendSense MVP V2.
Behavioral persona assignment system.
"""

from personas.assignment import (
    assign_persona,
    assign_all_personas,
    check_high_utilization,
    check_variable_income,
    check_subscription_heavy,
    check_savings_builder,
)

__all__ = [
    'assign_persona',
    'assign_all_personas',
    'check_high_utilization',
    'check_variable_income',
    'check_subscription_heavy',
    'check_savings_builder',
]


if __name__ == '__main__':
    # CLI entry point for running persona assignment
    from personas.assignment import assign_all_personas
    assign_all_personas()

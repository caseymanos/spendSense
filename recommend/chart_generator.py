"""
Chart data generator for recommendation visualizations.

This module generates structured chart data for the Next.js frontend components.
All charts are rendered client-side using Tremor React components.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional


class ChartGenerator:
    """Generates chart data structures for frontend visualization."""

    def __init__(self, output_dir: str):
        """
        Initialize chart generator.

        Args:
            output_dir: Directory for any generated assets (currently unused)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_credit_utilization_gauge(
        self,
        utilization: float,
        card_mask: str,
        current_balance: Optional[float] = None,
        credit_limit: Optional[float] = None,
        apr: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate credit utilization gauge chart data.

        Args:
            utilization: Utilization percentage (0-100)
            card_mask: Last 4 digits of card
            current_balance: Current balance amount
            credit_limit: Credit limit amount
            apr: Annual percentage rate

        Returns:
            Chart data structure for CreditUtilizationGauge component
        """
        data = {
            "utilization": round(utilization, 2),
            "cardMask": card_mask
        }

        # Add enhanced data if available
        if current_balance is not None:
            data["currentBalance"] = current_balance
        if credit_limit is not None:
            data["creditLimit"] = credit_limit
            data["availableCredit"] = credit_limit - (current_balance or 0)
        if apr is not None:
            data["apr"] = apr
            if current_balance:
                data["monthlyInterest"] = (current_balance * apr / 100) / 12

        # Calculate recommended balance (30% of limit)
        if credit_limit is not None:
            recommended = credit_limit * 0.30
            data["recommendedBalance"] = recommended
            if current_balance is not None:
                over_target = max(0, current_balance - recommended)
                data["amountOverTarget"] = over_target

        return {
            "type": "credit_utilization",
            "data": data
        }

    def generate_debt_avalanche_comparison(
        self,
        debts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate debt avalanche priority chart data.

        Args:
            debts: List of debt objects with balance, interestRate, name

        Returns:
            Chart data structure for DebtAvalancheChart component
        """
        # Sort by interest rate descending (avalanche method)
        sorted_debts = sorted(
            debts,
            key=lambda d: d.get("interestRate", 0),
            reverse=True
        )

        # Add priority numbers
        for idx, debt in enumerate(sorted_debts, start=1):
            debt["priority"] = idx

        return {
            "type": "debt_avalanche",
            "data": sorted_debts
        }

    def generate_emergency_fund_progress(
        self,
        current_amount: float,
        target_amount: float,
        monthly_expenses: float
    ) -> Dict[str, Any]:
        """
        Generate emergency fund progress chart data.

        Args:
            current_amount: Current emergency fund balance
            target_amount: Target emergency fund amount
            monthly_expenses: Average monthly expenses

        Returns:
            Chart data structure for EmergencyFundProgress component
        """
        months_covered = current_amount / monthly_expenses if monthly_expenses > 0 else 0
        progress_pct = (current_amount / target_amount * 100) if target_amount > 0 else 0

        return {
            "type": "emergency_fund",
            "data": {
                "current": current_amount,
                "target": target_amount,
                "monthsCovered": round(months_covered, 1),
                "progressPercent": min(100, round(progress_pct, 1)),
                "monthlyExpenses": monthly_expenses
            }
        }

    def generate_subscription_audit(
        self,
        subscriptions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate subscription audit chart data.

        Args:
            subscriptions: List of subscription objects

        Returns:
            Chart data structure for SubscriptionAuditChart component
        """
        total_monthly = sum(s.get("amount", 0) for s in subscriptions)
        total_annual = total_monthly * 12

        return {
            "type": "subscription_audit",
            "data": {
                "subscriptions": subscriptions,
                "totalMonthly": total_monthly,
                "totalAnnual": total_annual,
                "count": len(subscriptions)
            }
        }

    def generate_automated_savings_flow(
        self,
        monthly_income: float,
        current_savings_rate: float,
        recommended_savings_rate: float
    ) -> Dict[str, Any]:
        """
        Generate automated savings flow chart data.

        Args:
            monthly_income: Monthly income amount
            current_savings_rate: Current savings rate percentage
            recommended_savings_rate: Recommended savings rate percentage

        Returns:
            Chart data structure for AutomatedSavingsFlow component
        """
        current_savings = monthly_income * (current_savings_rate / 100)
        recommended_savings = monthly_income * (recommended_savings_rate / 100)
        potential_increase = recommended_savings - current_savings

        return {
            "type": "automated_savings",
            "data": {
                "monthlyIncome": monthly_income,
                "currentRate": current_savings_rate,
                "recommendedRate": recommended_savings_rate,
                "currentSavings": current_savings,
                "recommendedSavings": recommended_savings,
                "potentialIncrease": max(0, potential_increase)
            }
        }

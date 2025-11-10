"""
Chart data generator for recommendation visualizations.

This module generates structured chart data for the Next.js frontend components.
All charts are rendered client-side using Tremor React components.
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional

# Direct database access to avoid circular imports
def _load_credit_cards_direct(user_id: str):
    """Load credit card data directly from database to avoid circular imports."""
    import sqlite3
    from pathlib import Path
    
    db_path = Path(__file__).parent.parent / "data" / "users.sqlite"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT
            a.account_id,
            a.mask,
            a.balance_current,
            a.balance_limit,
            l.apr,
            l.minimum_payment
        FROM accounts a
        LEFT JOIN liabilities l ON a.account_id = l.account_id
        WHERE a.user_id = ? AND a.account_type = 'credit'
    """, (user_id,))
    
    class CreditCard:
        def __init__(self, account_id, mask, balance, credit_limit, apr, minimum_payment):
            self.account_id = account_id
            self.mask = mask or ""
            self.balance = balance or 0
            self.credit_limit = credit_limit or 0
            self.available_credit = self.credit_limit - self.balance
            self.utilization = round((self.balance / self.credit_limit * 100) if self.credit_limit > 0 else 0, 2)
            self.apr = apr
            self.monthly_interest = (self.balance * (apr / 100)) / 12 if apr and self.balance > 0 else None
            self.minimum_payment = minimum_payment
    
    cards = []
    for row in cursor.fetchall():
        account_id, mask, balance, credit_limit, apr, minimum_payment = row
        cards.append(CreditCard(account_id, mask, balance, credit_limit, apr, minimum_payment))
    
    conn.close()
    return cards


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

    def generate_credit_utilization_chart(
        self,
        user_id: str,
        signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate credit utilization chart with actual financial data.

        Args:
            user_id: User identifier to fetch credit card data
            signals: User behavioral signals

        Returns:
            Chart data structure with populated credit card financial data
        """
        # Fetch real credit card data
        credit_cards = _load_credit_cards_direct(user_id)

        if not credit_cards:
            return {
                "type": "credit_utilization",
                "data": None
            }

        # Build cards data from actual credit cards
        cards_data = []
        total_balance = 0
        total_limit = 0

        for card in credit_cards:
            cards_data.append({
                "name": f"Card ending in {card.mask}",
                "mask": card.mask,
                "utilization": card.utilization,
                "balance": card.balance,
                "credit_limit": card.credit_limit,
                "apr": card.apr,
                "monthly_interest": card.monthly_interest,
                "minimum_payment": card.minimum_payment,
                "available_credit": card.available_credit,
            })
            total_balance += card.balance
            total_limit += card.credit_limit

        # Calculate aggregate metrics
        avg_utilization = (total_balance / total_limit * 100) if total_limit > 0 else 0

        # Get highest utilization card for primary display
        highest_util_card = max(credit_cards, key=lambda c: c.utilization)

        return {
            "type": "credit_utilization",
            "data": {
                "cards": cards_data,
                "avg_utilization": round(avg_utilization, 2),
                "total_balance": total_balance,
                "total_limit": total_limit,
                # Primary card data (highest utilization)
                "utilization": highest_util_card.utilization,
                "card_mask": highest_util_card.mask,
                "balance": highest_util_card.balance,
                "credit_limit": highest_util_card.credit_limit,
                "apr": highest_util_card.apr,
                "monthly_interest": highest_util_card.monthly_interest,
                "minimum_payment": highest_util_card.minimum_payment,
                "available_credit": highest_util_card.available_credit,
            }
        }

    def generate_debt_avalanche_chart(
        self,
        user_id: str,
        signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate debt avalanche priority chart with actual debt data.

        Args:
            user_id: User identifier to fetch credit card data
            signals: User behavioral signals

        Returns:
            Chart data structure with populated debt information
        """
        # Fetch real credit card data
        credit_cards = _load_credit_cards_direct(user_id)

        # Build debt objects from credit cards with balances
        debts = []
        for card in credit_cards:
            if card.balance > 0:
                debts.append({
                    "name": f"Card ending in {card.mask}",
                    "balance": card.balance,
                    "apr": card.apr or 0,
                    "monthly_interest": card.monthly_interest or 0,
                    "minimum_payment": card.minimum_payment or 0,
                })

        # Sort by APR descending (avalanche method - highest interest first)
        sorted_debts = sorted(
            debts,
            key=lambda d: d.get("apr", 0),
            reverse=True
        )

        # Add priority numbers
        for idx, debt in enumerate(sorted_debts, start=1):
            debt["priority"] = idx

        return {
            "type": "debt_avalanche",
            "data": sorted_debts if sorted_debts else None
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

"""
Formatting utilities for displaying financial data.

Provides consistent formatting for currency, percentages, and other data types.
"""

def format_currency(amount: float) -> str:
    """Format a number as US currency.

    Args:
        amount: The amount to format

    Returns:
        Formatted string like "$1,234.56"
    """
    return f"${amount:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format a number as a percentage.

    Args:
        value: The value to format (e.g., 0.68 for 68%)
        decimals: Number of decimal places

    Returns:
        Formatted string like "68.0%"
    """
    return f"{value:.{decimals}f}%"


def format_large_number(value: float) -> str:
    """Format large numbers with K/M suffixes.

    Args:
        value: The number to format

    Returns:
        Formatted string like "1.2K" or "3.5M"
    """
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return f"{value:.0f}"


def format_account_mask(account_number: str, visible_digits: int = 4) -> str:
    """Mask an account number, showing only the last few digits.

    Args:
        account_number: Full account number
        visible_digits: Number of digits to show at the end

    Returns:
        Masked string like "****4523"
    """
    if len(account_number) <= visible_digits:
        return account_number

    mask = "*" * (len(account_number) - visible_digits)
    visible = account_number[-visible_digits:]
    return f"{mask}{visible}"


def format_card_type_with_mask(card_type: str, last_four: str) -> str:
    """Format card display with type and masked number.

    Args:
        card_type: Type of card (e.g., "Visa", "Mastercard")
        last_four: Last 4 digits of card number

    Returns:
        Formatted string like "Visa ending in 4523"
    """
    return f"{card_type} ending in {last_four}"


def format_duration(days: int) -> str:
    """Format a duration in days to a human-readable string.

    Args:
        days: Number of days

    Returns:
        Formatted string like "15 days" or "2 months"
    """
    if days == 0:
        return "today"
    elif days == 1:
        return "1 day"
    elif days < 30:
        return f"{days} days"
    elif days < 60:
        return "1 month"
    elif days < 365:
        months = days // 30
        return f"{months} months"
    else:
        years = days // 365
        return f"{years} year" if years == 1 else f"{years} years"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: String to append if truncated

    Returns:
        Truncated text with suffix if needed
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def pluralize(count: int, singular: str, plural: str = None) -> str:
    """Return singular or plural form based on count.

    Args:
        count: Number of items
        singular: Singular form of word
        plural: Plural form (if None, adds 's' to singular)

    Returns:
        Appropriate form with count, like "1 item" or "3 items"
    """
    if plural is None:
        plural = f"{singular}s"

    form = singular if count == 1 else plural
    return f"{count} {form}"

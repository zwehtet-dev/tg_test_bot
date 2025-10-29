"""
Currency utility functions
"""
import math


def round_mmk_amount(amount: float) -> float:
    """
    Round MMK amount to nearest 50
    
    Rounding rules:
    - Amounts ending in 00-50: round to nearest 50 (down to 00 or 50)
    - Amounts ending in 51-99: round UP to next 50
    
    Examples:
        1234510 -> 1234500 (10 rounds down to 00)
        1234525 -> 1234500 (25 rounds down to 00)
        1234551 -> 1234600 (51 rounds up to next 50)
        1234575 -> 1234600 (75 rounds up to next 50)
        123456 -> 123450 (56 rounds up, but to 50)
    
    Args:
        amount: Original MMK amount
        
    Returns:
        Rounded amount to nearest 50
    """
    import math
    
    # Get the last two digits
    last_two = int(amount) % 100
    base = int(amount) - last_two
    
    if last_two <= 50:
        # Round to nearest 50 (either 0 or 50)
        if last_two <= 25:
            return float(base)
        else:
            return float(base + 50)
    else:
        # 51-99: round UP to next 50
        return float(base + 100)


def round_thb_amount(amount: float) -> float:
    """
    Round THB amount to 2 decimal places
    
    Args:
        amount: Original THB amount
        
    Returns:
        Rounded amount to 2 decimal places
    """
    return round(amount, 2)


def format_amount(amount: float, currency: str) -> str:
    """
    Format amount based on currency
    
    Args:
        amount: Amount to format
        currency: Currency code (THB or MMK)
        
    Returns:
        Formatted amount string
    """
    if currency == 'MMK':
        return f"{amount:,.0f}"
    else:
        return f"{amount:,.2f}"


def calculate_exchange(
    from_amount: float,
    exchange_rate: float,
    from_currency: str,
    to_currency: str
) -> tuple[float, float]:
    """
    Calculate exchange with proper rounding
    
    Args:
        from_amount: Amount to exchange
        exchange_rate: Exchange rate (THB to MMK)
        from_currency: Source currency (THB or MMK)
        to_currency: Target currency (MMK or THB)
        
    Returns:
        Tuple of (from_amount, to_amount) with proper rounding
    """
    if from_currency == 'THB' and to_currency == 'MMK':
        # THB to MMK: round MMK to nearest 100
        to_amount = from_amount * exchange_rate
        to_amount = round_mmk_amount(to_amount)
        from_amount = round_thb_amount(from_amount)
        
    elif from_currency == 'MMK' and to_currency == 'THB':
        # MMK to THB: round MMK to nearest 100 first, then calculate THB
        from_amount = round_mmk_amount(from_amount)
        to_amount = from_amount / exchange_rate
        to_amount = round_thb_amount(to_amount)
        
    else:
        # Fallback
        from_amount = round(from_amount, 2)
        to_amount = round(to_amount, 2)
    
    return from_amount, to_amount

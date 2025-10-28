"""Text formatting utilities"""
from typing import List, Tuple


def format_currency(amount: float, currency: str) -> str:
    """
    Format currency amount
    
    Args:
        amount: Amount to format
        currency: Currency code (THB, MMK)
    
    Returns:
        Formatted currency string
    """
    if currency == "THB":
        return f"{amount:,.2f} THB"
    elif currency == "MMK":
        return f"{amount:,.0f} MMK"
    else:
        return f"{amount:,.2f} {currency}"


def format_transaction(
    from_currency: str,
    to_currency: str,
    sent_amount: float,
    received_amount: float,
    rate: float
) -> str:
    """
    Format transaction details
    
    Args:
        from_currency: Source currency
        to_currency: Target currency
        sent_amount: Amount sent
        received_amount: Amount received
        rate: Exchange rate
    
    Returns:
        Formatted transaction string
    """
    if from_currency == "THB":
        return f"{sent_amount:,.0f} THB × {rate} = {received_amount:,.0f} MMK"
    else:
        return f"{sent_amount:,.0f} MMK / {rate} = {received_amount:,.2f} THB"


def format_bank_list(banks: List[Tuple], show_balance: bool = False) -> str:
    """
    Format bank list for display
    
    Args:
        banks: List of bank tuples (id, currency, bank_name, account_number, account_name, is_active, display_name)
        show_balance: Whether to show balance
    
    Returns:
        Formatted bank list string
    """
    if not banks:
        return "No banks configured"
    
    lines = []
    for bank in banks:
        if len(bank) >= 7:
            _, currency, bank_name, account_number, account_name, is_active, display_name = bank[:7]
            display = display_name or bank_name
            
            if show_balance and len(bank) >= 8:
                balance = bank[7]
                lines.append(f"• {display}: {format_currency(balance, currency)}")
            else:
                lines.append(f"• {display}")
        else:
            lines.append(f"• {bank[2] if len(bank) > 2 else 'Unknown'}")
    
    return "\n".join(lines)

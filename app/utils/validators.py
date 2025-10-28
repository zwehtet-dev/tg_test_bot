"""Input validation utilities"""
import re
from typing import Tuple, Optional


def validate_amount(amount_str: str) -> Tuple[bool, Optional[float], str]:
    """
    Validate amount input
    
    Args:
        amount_str: Amount string to validate
    
    Returns:
        Tuple of (is_valid, amount, error_message)
    """
    try:
        # Remove commas and whitespace
        cleaned = amount_str.replace(',', '').strip()
        
        # Try to convert to float
        amount = float(cleaned)
        
        # Check if positive
        if amount <= 0:
            return False, None, "Amount must be greater than zero"
        
        # Check if reasonable (not too large)
        if amount > 10_000_000:
            return False, None, "Amount is too large"
        
        return True, amount, ""
        
    except ValueError:
        return False, None, "Invalid amount format. Please enter a valid number"


def validate_bank_info(bank_info_str: str) -> Tuple[bool, Optional[dict], str]:
    """
    Validate bank information input
    
    Args:
        bank_info_str: Bank info string in format "Bank | Account | Name"
    
    Returns:
        Tuple of (is_valid, bank_info_dict, error_message)
    """
    parts = bank_info_str.split('|')
    
    if len(parts) != 3:
        return False, None, (
            "Invalid format. Please use:\n"
            "`Bank Name | Account Number | Account Name`"
        )
    
    bank_name = parts[0].strip()
    account_number = parts[1].strip()
    account_name = parts[2].strip()
    
    # Validate bank name
    if not bank_name or len(bank_name) < 2:
        return False, None, "Bank name is too short"
    
    # Validate account number
    if not account_number or len(account_number) < 5:
        return False, None, "Account number is too short"
    
    # Validate account name
    if not account_name or len(account_name) < 2:
        return False, None, "Account name is too short"
    
    return True, {
        'bank_name': bank_name,
        'account_number': account_number,
        'account_name': account_name
    }, ""


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format
    
    Args:
        phone: Phone number string
    
    Returns:
        True if valid, False otherwise
    """
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it's all digits and reasonable length
    return cleaned.isdigit() and 8 <= len(cleaned) <= 15

"""Bank account data model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BankAccount:
    """Bank account data model"""
    id: Optional[int] = None
    currency: str = ""
    bank_name: str = ""
    account_number: str = ""
    account_name: str = ""
    balance: float = 0.0
    is_active: bool = True
    display_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def display(self) -> str:
        """Get display name or bank name"""
        return self.display_name or self.bank_name
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'currency': self.currency,
            'bank_name': self.bank_name,
            'account_number': self.account_number,
            'account_name': self.account_name,
            'balance': self.balance,
            'is_active': self.is_active,
            'display_name': self.display_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

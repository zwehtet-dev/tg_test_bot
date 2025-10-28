"""Transaction data model"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ExchangeDirection(Enum):
    """Exchange direction enum"""
    THB_TO_MMK = "THB_TO_MMK"
    MMK_TO_THB = "MMK_TO_THB"


@dataclass
class Transaction:
    """Transaction data model"""
    id: Optional[int] = None
    user_id: int = 0
    username: Optional[str] = None
    exchange_direction: ExchangeDirection = ExchangeDirection.THB_TO_MMK
    from_currency: str = "THB"
    to_currency: str = "MMK"
    sent_amount: float = 0.0
    received_amount: float = 0.0
    exchange_rate: float = 0.0
    user_bank_name: str = ""
    user_account_number: str = ""
    user_account_name: str = ""
    from_bank: str = ""
    admin_receiving_bank: str = ""
    receipt_path: Optional[str] = None
    admin_receipt_path: Optional[str] = None
    status: str = "pending"
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    
    @property
    def thb_amount(self) -> float:
        """Get THB amount regardless of direction"""
        return self.sent_amount if self.from_currency == "THB" else self.received_amount
    
    @property
    def mmk_amount(self) -> float:
        """Get MMK amount regardless of direction"""
        return self.received_amount if self.from_currency == "THB" else self.sent_amount
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'exchange_direction': self.exchange_direction.value,
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'sent_amount': self.sent_amount,
            'received_amount': self.received_amount,
            'exchange_rate': self.exchange_rate,
            'user_bank_name': self.user_bank_name,
            'user_account_number': self.user_account_number,
            'user_account_name': self.user_account_name,
            'from_bank': self.from_bank,
            'admin_receiving_bank': self.admin_receiving_bank,
            'receipt_path': self.receipt_path,
            'admin_receipt_path': self.admin_receipt_path,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
        }

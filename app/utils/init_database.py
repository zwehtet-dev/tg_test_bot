"""
Database initialization utility
Automatically initializes bank accounts and settings on first run
"""
import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)


# Bank accounts configuration
BANK_ACCOUNTS = [
    {
        'currency': 'THB',
        'bank_name': 'Siam Commercial',
        'account_number': '8842662935',
        'account_name': 'MIN MYAT NWE',
        'balance': 15000,
        'is_active': 1,
        'display_name': 'MMN (SCB)'
    },
    {
        'currency': 'THB',
        'bank_name': 'Krungthai',
        'account_number': '66xxxx0987',
        'account_name': 'THIN ZAR HTET',
        'balance': 15000,
        'is_active': 1,
        'display_name': 'TZH (Kbank)'
    },
    {
        'currency': 'MMK',
        'bank_name': 'KBZ Special',
        'account_number': '27251127201844001',
        'account_name': 'CHAW SU THU ZAR',
        'balance': 15000000,
        'is_active': 1,
        'display_name': 'CSTZ (KBZ)'
    },
    {
        'currency': 'MMK',
        'bank_name': 'AYA Special',
        'account_number': '40038204256',
        'account_name': 'CHAW SU THU ZAR',
        'balance': 15000000,
        'is_active': 1,
        'display_name': 'CSTZ (AYA)'
    },
    {
        'currency': 'MMK',
        'bank_name': 'Yoma',
        'account_number': '007011118014339',
        'account_name': 'DAW CHAW HSU THU ZAR',
        'balance': 15000000,
        'is_active': 1,
        'display_name': 'CSTZ (Yoma)'
    },
    {
        'currency': 'MMK',
        'bank_name': 'CB Special',
        'account_number': '0225100900026042',
        'account_name': 'CHAW SU THU ZAR',
        'balance': 15000000,
        'is_active': 1,
        'display_name': 'CSTZ (CB)'
    },
    {
        'currency': 'MMK',
        'bank_name': 'Myanmar Pay',
        'account_number': '223743000898082',
        'account_name': 'CHAW SU',
        'balance': 15000000,
        'is_active': 1,
        'display_name': 'CS (MMP)'
    },
    {
        'currency': 'MMK',
        'bank_name': 'AYA Pay',
        'account_number': '09799988991',
        'account_name': 'CHAW SU THU ZAR',
        'balance': 15000000,
        'is_active': 1,
        'display_name': 'CSTZ (AYA W)'
    },
    {
        'currency': 'MMK',
        'bank_name': 'KBZ Special',
        'account_number': '2237801114175047',
        'account_name': 'CHAW SU STORE',
        'balance': 15000000,
        'is_active': 1,
        'display_name': 'CSS (KBZ)'
    }
]


def initialize_bank_accounts(db_service) -> int:
    """
    Initialize bank accounts if they don't exist
    
    Args:
        db_service: DatabaseService instance
        
    Returns:
        Number of accounts added
    """
    existing_accounts = db_service.get_bank_accounts(active_only=False)
    
    # If accounts already exist, skip initialization
    if len(existing_accounts) > 0:
        logger.info(f"Bank accounts already initialized ({len(existing_accounts)} accounts found)")
        return 0
    
    logger.info("Initializing bank accounts...")
    added_count = 0
    
    for account in BANK_ACCOUNTS:
        account_id = db_service.add_bank_account(
            currency=account['currency'],
            bank_name=account['bank_name'],
            account_number=account['account_number'],
            account_name=account['account_name'],
            display_name=account['display_name'],
            initial_balance=account['balance']
        )
        
        if account_id:
            added_count += 1
            logger.info(f"✓ Added: {account['display_name']} - {account['bank_name']} ({account['currency']})")
    
    logger.info(f"Bank accounts initialization complete: {added_count} accounts added")
    return added_count


def initialize_settings(db_service, balance_topic_id: str = "3"):
    """
    Initialize bot settings if they don't exist
    
    Args:
        db_service: DatabaseService instance
        balance_topic_id: Balance topic ID (default: "3")
    """
    # Check if balance_topic_id is already set
    existing_topic_id = db_service.get_setting('balance_topic_id')
    
    if existing_topic_id:
        logger.info(f"Settings already initialized (balance_topic_id: {existing_topic_id})")
        return
    
    logger.info("Initializing bot settings...")
    
    # Set balance topic ID
    db_service.set_setting('balance_topic_id', balance_topic_id)
    logger.info(f"✓ Set balance_topic_id: {balance_topic_id}")
    
    logger.info("Bot settings initialization complete")


def initialize_database(db_service, balance_topic_id: str = "3"):
    """
    Complete database initialization
    
    Args:
        db_service: DatabaseService instance
        balance_topic_id: Balance topic ID (default: "3")
    """
    logger.info("=" * 60)
    logger.info("Starting database initialization...")
    logger.info("=" * 60)
    
    # Initialize bank accounts
    accounts_added = initialize_bank_accounts(db_service)
    
    # Initialize settings
    initialize_settings(db_service, balance_topic_id)
    
    logger.info("=" * 60)
    logger.info("Database initialization complete!")
    logger.info(f"Bank accounts: {accounts_added} added")
    logger.info("=" * 60)

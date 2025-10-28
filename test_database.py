#!/usr/bin/env python3
"""
Test script to verify database functionality
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing database functionality...")
print("-" * 60)

try:
    from app.services import DatabaseService
    from app.models import ExchangeDirection
    import tempfile
    import os
    
    # Create temporary database file for testing
    print("✓ Creating test database...")
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    db = DatabaseService(temp_db.name)
    print("  Database created successfully")
    
    # Test exchange rate
    print("✓ Testing exchange rate...")
    db.initialize_exchange_rate(121.5)
    rate = db.get_current_rate()
    print(f"  Current rate: {rate}")
    assert rate == 121.5, "Rate mismatch"
    
    # Test bank account
    print("✓ Testing bank accounts...")
    account_id = db.add_bank_account(
        currency='THB',
        bank_name='TestBank',
        account_number='1234567890',
        account_name='Test Account',
        display_name='Test Display',
        initial_balance=10000.0
    )
    print(f"  Bank account created: ID {account_id}")
    
    accounts = db.get_bank_accounts(currency='THB')
    print(f"  Found {len(accounts)} THB accounts")
    assert len(accounts) == 1, "Account count mismatch"
    
    # Test transaction
    print("✓ Testing transactions...")
    tx_id = db.create_transaction(
        user_id=123456,
        username='testuser',
        exchange_direction='THB_TO_MMK',
        from_currency='THB',
        to_currency='MMK',
        sent_amount=1000.0,
        received_amount=121500.0,
        exchange_rate=121.5,
        user_bank_name='KBZ',
        user_account_number='0987654321',
        user_account_name='Test User',
        from_bank='SCB',
        admin_receiving_bank='TestBank',
        receipt_path=None
    )
    print(f"  Transaction created: ID {tx_id}")
    
    # Get transaction
    tx = db.get_transaction(tx_id)
    print(f"  Transaction retrieved: {tx.exchange_direction.value}")
    assert tx.sent_amount == 1000.0, "Amount mismatch"
    
    # Test balance update
    print("✓ Testing balance updates...")
    db.update_balance('THB', 'TestBank', 1000.0)
    balances = db.get_balances()
    print(f"  Balances updated: {len(balances)} accounts")
    
    # Test validation
    print("✓ Testing account validation...")
    validated = db.validate_receiver_account(
        account_name='Test Account',
        bank_name='TestBank',
        currency='THB'
    )
    print(f"  Validation result: {'Success' if validated else 'Failed'}")
    assert validated is not None, "Validation failed"
    
    print("-" * 60)
    print("✅ All database tests passed!")
    print("")
    print("Your database is working correctly!")
    
    # Cleanup
    os.unlink(temp_db.name)
    
except AssertionError as e:
    print(f"❌ Test assertion failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

#!/usr/bin/env python3
"""Verify database with bot's database service"""
from app.services.database_service import DatabaseService

# Initialize database service
db = DatabaseService("data/exchange_bot.db")

print("\n" + "="*80)
print("VERIFYING DATABASE WITH BOT SERVICE")
print("="*80 + "\n")

# Get all bank accounts
print("THB Accounts:")
print("-" * 80)
thb_accounts = db.get_bank_accounts(currency='THB')
for acc in thb_accounts:
    print(f"  {acc.display_name:20} | {acc.bank_name:20} | {acc.account_number:20} | ฿{acc.balance:,.2f}")

print("\nMMK Accounts:")
print("-" * 80)
mmk_accounts = db.get_bank_accounts(currency='MMK')
for acc in mmk_accounts:
    print(f"  {acc.display_name:20} | {acc.bank_name:20} | {acc.account_number:20} | K{acc.balance:,.0f}")

print("\n" + "="*80)
print(f"Total THB accounts: {len(thb_accounts)}")
print(f"Total MMK accounts: {len(mmk_accounts)}")
print(f"Exchange rate: {db.get_current_rate()}")
print("="*80 + "\n")

print("✓ Database verification completed successfully!\n")

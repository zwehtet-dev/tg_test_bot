#!/usr/bin/env python3
"""
Script to recreate database with new bank accounts
"""
import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = "data/exchange_bot.db"

# Bank accounts data
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


def backup_database():
    """Backup existing database"""
    if os.path.exists(DB_PATH):
        backup_path = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(DB_PATH, backup_path)
        print(f"✓ Database backed up to: {backup_path}")
        return backup_path
    return None


def create_fresh_database():
    """Create fresh database with new structure"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                exchange_direction TEXT NOT NULL,
                from_currency TEXT NOT NULL,
                to_currency TEXT NOT NULL,
                sent_amount REAL NOT NULL,
                received_amount REAL NOT NULL,
                exchange_rate REAL NOT NULL,
                user_bank_name TEXT NOT NULL,
                user_account_number TEXT NOT NULL,
                user_account_name TEXT NOT NULL,
                from_bank TEXT,
                admin_receiving_bank TEXT,
                receipt_path TEXT,
                admin_receipt_path TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confirmed_at TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON transactions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON transactions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON transactions(created_at)")
        
        # Create bank accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bank_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency TEXT NOT NULL,
                bank_name TEXT NOT NULL,
                account_number TEXT NOT NULL,
                account_name TEXT NOT NULL,
                balance REAL DEFAULT 0.0,
                is_active INTEGER DEFAULT 1,
                display_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(currency, bank_name, account_number)
            )
        """)
        
        # Create exchange rate table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exchange_rate (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                rate REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create bot settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Initialize exchange rate
        cursor.execute("""
            INSERT OR REPLACE INTO exchange_rate (id, rate, updated_at)
            VALUES (1, 121.5, ?)
        """, (datetime.now(),))
        
        conn.commit()
        print("✓ Database tables created successfully")
        
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_bank_accounts():
    """Insert bank accounts into database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        for account in BANK_ACCOUNTS:
            cursor.execute("""
                INSERT INTO bank_accounts 
                (currency, bank_name, account_number, account_name, balance, is_active, display_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account['currency'],
                account['bank_name'],
                account['account_number'],
                account['account_name'],
                account['balance'],
                account['is_active'],
                account['display_name'],
                datetime.now(),
                datetime.now()
            ))
            print(f"✓ Added: {account['display_name']} - {account['bank_name']} ({account['currency'].upper()})")
        
        conn.commit()
        print(f"\n✓ Successfully inserted {len(BANK_ACCOUNTS)} bank accounts")
        
    except Exception as e:
        print(f"✗ Error inserting bank accounts: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_accounts():
    """Verify inserted accounts"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT currency, bank_name, account_number, account_name, balance, display_name
            FROM bank_accounts
            ORDER BY currency, bank_name
        """)
        
        accounts = cursor.fetchall()
        
        print("\n" + "="*80)
        print("BANK ACCOUNTS IN DATABASE")
        print("="*80)
        
        current_currency = None
        for acc in accounts:
            currency, bank_name, account_number, account_name, balance, display_name = acc
            
            if currency != current_currency:
                current_currency = currency
                print(f"\n{currency.upper()} Accounts:")
                print("-" * 80)
            
            balance_formatted = f"{balance:,.0f}" if currency == 'MMK' else f"{balance:,.2f}"
            print(f"  {display_name:20} | {bank_name:20} | {account_number:20} | {balance_formatted:>15}")
        
        print("\n" + "="*80)
        print(f"Total accounts: {len(accounts)}")
        print("="*80)
        
    except Exception as e:
        print(f"✗ Error verifying accounts: {e}")
    finally:
        conn.close()


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("RECREATING DATABASE WITH NEW BANK ACCOUNTS")
    print("="*80 + "\n")
    
    # Step 1: Backup existing database
    backup_path = backup_database()
    
    # Step 2: Create fresh database
    create_fresh_database()
    
    # Step 3: Insert bank accounts
    insert_bank_accounts()
    
    # Step 4: Verify accounts
    verify_accounts()
    
    print("\n✓ Database recreation completed successfully!")
    if backup_path:
        print(f"  Old database backed up to: {backup_path}")
    print(f"  New database: {DB_PATH}\n")


if __name__ == "__main__":
    main()

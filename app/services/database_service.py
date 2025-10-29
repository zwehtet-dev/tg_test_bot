"""
Database service for managing transactions and balances
Improved with better error handling and data models
"""
import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional
import logging
from pathlib import Path

from app.models import Transaction, ExchangeDirection, BankAccount

logger = logging.getLogger(__name__)


class DatabaseService:
    """Manages SQLite database operations with improved structure"""
    
    def __init__(self, db_path: str):
        """
        Initialize database service
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        logger.info(f"Database service initialized: {db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables with improved schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Transactions table
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
            
            # Create indexes separately
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON transactions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON transactions(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON transactions(created_at)")
            
            # Bank accounts table
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
            
            # Exchange rate table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exchange_rate (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    rate REAL NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Bot settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Database tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    # Exchange Rate Methods
    def get_current_rate(self) -> float:
        """Get current exchange rate"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT rate FROM exchange_rate WHERE id = 1")
            result = cursor.fetchone()
            return result['rate'] if result else 121.5
        except Exception as e:
            logger.error(f"Error getting exchange rate: {e}")
            return 121.5
        finally:
            conn.close()
    
    def update_rate(self, new_rate: float):
        """Update exchange rate"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO exchange_rate (id, rate, updated_at)
                VALUES (1, ?, ?)
            """, (new_rate, datetime.now()))
            conn.commit()
            logger.info(f"Exchange rate updated to {new_rate}")
        except Exception as e:
            logger.error(f"Error updating exchange rate: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def initialize_exchange_rate(self, default_rate: float):
        """Initialize exchange rate if not set"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM exchange_rate")
            if cursor.fetchone()['count'] == 0:
                cursor.execute(
                    "INSERT INTO exchange_rate (id, rate) VALUES (1, ?)",
                    (default_rate,)
                )
                conn.commit()
                logger.info(f"Exchange rate initialized to {default_rate}")
        except Exception as e:
            logger.error(f"Error initializing exchange rate: {e}")
            conn.rollback()
        finally:
            conn.close()

    # Bank Account Methods
    def add_bank_account(
        self,
        currency: str,
        bank_name: str,
        account_number: str,
        account_name: str,
        display_name: Optional[str] = None,
        initial_balance: float = 0.0
    ) -> Optional[int]:
        """Add a new bank account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO bank_accounts 
                (currency, bank_name, account_number, account_name, display_name, balance)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (currency, bank_name, account_number, account_name, display_name, initial_balance))
            conn.commit()
            account_id = cursor.lastrowid
            logger.info(f"Bank account added: {bank_name} - {account_number}")
            return account_id
        except sqlite3.IntegrityError:
            logger.warning(f"Bank account already exists: {bank_name} - {account_number}")
            return None
        except Exception as e:
            logger.error(f"Error adding bank account: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def get_bank_accounts(self, currency: Optional[str] = None, active_only: bool = True) -> List[BankAccount]:
        """Get bank accounts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = "SELECT * FROM bank_accounts WHERE 1=1"
            params = []
            
            if currency:
                query += " AND currency = ?"
                params.append(currency)
            
            if active_only:
                query += " AND is_active = 1"
            
            query += " ORDER BY currency, bank_name"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            accounts = []
            for row in rows:
                account = BankAccount(
                    id=row['id'],
                    currency=row['currency'],
                    bank_name=row['bank_name'],
                    account_number=row['account_number'],
                    account_name=row['account_name'],
                    balance=row['balance'],
                    is_active=bool(row['is_active']),
                    display_name=row['display_name'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )
                accounts.append(account)
            
            return accounts
            
        except Exception as e:
            logger.error(f"Error getting bank accounts: {e}")
            return []
        finally:
            conn.close()
    
    def update_balance(self, currency: str, bank_name: str, amount_change: float):
        """Update balance for a specific bank"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE bank_accounts 
                SET balance = balance + ?, updated_at = ?
                WHERE currency = ? AND bank_name = ? AND is_active = 1
            """, (amount_change, datetime.now(), currency, bank_name))
            
            if cursor.rowcount == 0:
                logger.warning(f"No active account found for {currency} {bank_name}")
            else:
                conn.commit()
                logger.info(f"Balance updated: {currency} {bank_name} {amount_change:+.2f}")
        except Exception as e:
            logger.error(f"Error updating balance: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def add_admin_bank_account(
        self,
        currency: str,
        bank_name: str,
        account_number: str,
        account_name: str,
        display_name: Optional[str] = None
    ) -> Optional[int]:
        """Add admin bank account (alias for add_bank_account)"""
        return self.add_bank_account(
            currency=currency,
            bank_name=bank_name,
            account_number=account_number,
            account_name=account_name,
            display_name=display_name,
            initial_balance=0.0
        )
    
    def deactivate_admin_bank_account(self, account_id: int):
        """Deactivate a bank account by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE bank_accounts 
                SET is_active = 0, updated_at = ?
                WHERE id = ?
            """, (datetime.now(), account_id))
            
            if cursor.rowcount == 0:
                logger.warning(f"No account found with ID {account_id}")
            else:
                conn.commit()
                logger.info(f"Bank account #{account_id} deactivated")
        except Exception as e:
            logger.error(f"Error deactivating account: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_balances(self) -> List[Tuple[str, str, float, Optional[str]]]:
        """Get all balances"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT currency, bank_name, balance, display_name
                FROM bank_accounts 
                WHERE is_active = 1
                ORDER BY currency, bank_name
            """)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting balances: {e}")
            return []
        finally:
            conn.close()
    
    def initialize_balances(self, initial_balances: List[Tuple[str, str, float]]):
        """Initialize balances for bank accounts"""
        for currency, bank, balance in initial_balances:
            # Check if account exists
            accounts = self.get_bank_accounts(currency=currency, active_only=False)
            account_exists = any(acc.bank_name == bank for acc in accounts)
            
            if not account_exists:
                # Create account with initial balance
                self.add_bank_account(
                    currency=currency,
                    bank_name=bank,
                    account_number="",  # Will be set by admin
                    account_name="",  # Will be set by admin
                    initial_balance=balance
                )
                logger.info(f"Initialized {currency} {bank} with balance {balance}")

    # Transaction Methods
    def create_transaction(
        self,
        user_id: int,
        username: Optional[str],
        exchange_direction: str,
        from_currency: str,
        to_currency: str,
        sent_amount: float,
        received_amount: float,
        exchange_rate: float,
        user_bank_name: str,
        user_account_number: str,
        user_account_name: str,
        from_bank: str,
        admin_receiving_bank: str,
        receipt_path: Optional[str] = None
    ) -> int:
        """Create a new transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO transactions (
                    user_id, username, exchange_direction, from_currency, to_currency,
                    sent_amount, received_amount, exchange_rate,
                    user_bank_name, user_account_number, user_account_name,
                    from_bank, admin_receiving_bank, receipt_path, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (
                user_id, username, exchange_direction, from_currency, to_currency,
                sent_amount, received_amount, exchange_rate,
                user_bank_name, user_account_number, user_account_name,
                from_bank, admin_receiving_bank, receipt_path
            ))
            
            transaction_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Transaction created: #{transaction_id} ({exchange_direction})")
            return transaction_id
            
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()
    
    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return Transaction(
                id=row['id'],
                user_id=row['user_id'],
                username=row['username'],
                exchange_direction=ExchangeDirection(row['exchange_direction']),
                from_currency=row['from_currency'],
                to_currency=row['to_currency'],
                sent_amount=row['sent_amount'],
                received_amount=row['received_amount'],
                exchange_rate=row['exchange_rate'],
                user_bank_name=row['user_bank_name'],
                user_account_number=row['user_account_number'],
                user_account_name=row['user_account_name'],
                from_bank=row['from_bank'],
                admin_receiving_bank=row['admin_receiving_bank'],
                receipt_path=row['receipt_path'],
                admin_receipt_path=row['admin_receipt_path'],
                status=row['status'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                confirmed_at=datetime.fromisoformat(row['confirmed_at']) if row['confirmed_at'] else None
            )
            
        except Exception as e:
            logger.error(f"Error getting transaction: {e}")
            return None
        finally:
            conn.close()
    
    def update_transaction_status(
        self,
        transaction_id: int,
        status: str,
        admin_receipt_path: Optional[str] = None
    ):
        """Update transaction status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if admin_receipt_path:
                cursor.execute("""
                    UPDATE transactions 
                    SET status = ?, admin_receipt_path = ?, confirmed_at = ?
                    WHERE id = ?
                """, (status, admin_receipt_path, datetime.now(), transaction_id))
            else:
                cursor.execute("""
                    UPDATE transactions 
                    SET status = ?, confirmed_at = ?
                    WHERE id = ?
                """, (status, datetime.now(), transaction_id))
            
            conn.commit()
            logger.info(f"Transaction #{transaction_id} status updated to {status}")
            
        except Exception as e:
            logger.error(f"Error updating transaction status: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def update_transaction_admin_receipt(self, transaction_id: int, admin_receipt_path: str):
        """Update admin receipt path for a transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE transactions 
                SET admin_receipt_path = ?
                WHERE id = ?
            """, (admin_receipt_path, transaction_id))
            
            conn.commit()
            logger.info(f"Transaction #{transaction_id} admin receipt updated")
            
        except Exception as e:
            logger.error(f"Error updating admin receipt: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def update_transaction_received_amount(self, transaction_id: int, received_amount: float):
        """Update received amount for a transaction (when actual amount differs from calculated)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE transactions 
                SET received_amount = ?
                WHERE id = ?
            """, (received_amount, transaction_id))
            
            conn.commit()
            logger.info(f"Transaction #{transaction_id} received_amount updated to {received_amount}")
            
        except Exception as e:
            logger.error(f"Error updating received amount: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_recent_transactions(self, limit: int = 10) -> List[Transaction]:
        """Get recent transactions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM transactions 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            transactions = []
            
            for row in rows:
                transaction = Transaction(
                    id=row['id'],
                    user_id=row['user_id'],
                    username=row['username'],
                    exchange_direction=ExchangeDirection(row['exchange_direction']),
                    from_currency=row['from_currency'],
                    to_currency=row['to_currency'],
                    sent_amount=row['sent_amount'],
                    received_amount=row['received_amount'],
                    exchange_rate=row['exchange_rate'],
                    user_bank_name=row['user_bank_name'],
                    user_account_number=row['user_account_number'],
                    user_account_name=row['user_account_name'],
                    from_bank=row['from_bank'],
                    admin_receiving_bank=row['admin_receiving_bank'],
                    receipt_path=row['receipt_path'],
                    admin_receipt_path=row['admin_receipt_path'],
                    status=row['status'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    confirmed_at=datetime.fromisoformat(row['confirmed_at']) if row['confirmed_at'] else None
                )
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting recent transactions: {e}")
            return []
        finally:
            conn.close()
    
    # Validation Methods
    def validate_receiver_account(
        self,
        account_name: str,
        bank_name: Optional[str],
        currency: str
    ) -> Optional[BankAccount]:
        """Validate if receiver account matches admin accounts"""
        accounts = self.get_bank_accounts(currency=currency, active_only=True)
        
        # Normalize input
        normalized_name = self._normalize_name(account_name)
        
        best_match = None
        best_similarity = 0.0
        threshold = 0.80  # 80% similarity
        
        for account in accounts:
            # Calculate name similarity
            similarity = self._calculate_similarity(account_name, account.account_name)
            
            # Check bank match if provided
            bank_matches = True
            if bank_name:
                bank_matches = self._banks_match(bank_name, account.bank_name)
            
            # Track best match
            if similarity >= threshold and bank_matches:
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = account
        
        if best_match:
            logger.info(f"Validated account: {account_name} → {best_match.account_name} ({best_similarity:.2%})")
        else:
            logger.warning(f"No match found for: {account_name} at {bank_name}")
        
        return best_match
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        if not name:
            return ""
        
        normalized = name.lower().strip()
        
        # Remove titles
        prefixes = ['miss', 'mr', 'mrs', 'ms', 'dr', 'prof']
        for prefix in prefixes:
            if normalized.startswith(prefix + ' ') or normalized.startswith(prefix + '.'):
                normalized = normalized[len(prefix):].strip(' .')
                break
        
        # Remove special characters
        normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
        
        # Remove spaces
        return ''.join(normalized.split())
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate Levenshtein similarity between two strings"""
        s1 = self._normalize_name(str1)
        s2 = self._normalize_name(str2)
        
        if s1 == s2:
            return 1.0
        
        if not s1 or not s2:
            return 0.0
        
        # Levenshtein distance
        len1, len2 = len(s1), len(s2)
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,
                    matrix[i][j-1] + 1,
                    matrix[i-1][j-1] + cost
                )
        
        distance = matrix[len1][len2]
        max_len = max(len1, len2)
        return 1 - (distance / max_len)
    
    def _banks_match(self, bank1: str, bank2: str) -> bool:
        """Check if two bank names match"""
        # Bank aliases
        aliases = {
            'scb': 'siamcommercialbank',
            'siamcommercial': 'siamcommercialbank',
            'ktb': 'krungthaibank',
            'krungthai': 'krungthaibank',
            'kbank': 'kasikorn',
            'kasikorn': 'kasikorn',
            'bbl': 'bangkokbank',
            'bangkok': 'bangkokbank',
        }
        
        norm1 = self._normalize_name(bank1)
        norm2 = self._normalize_name(bank2)
        
        # Apply aliases
        check1 = aliases.get(norm1, norm1)
        check2 = aliases.get(norm2, norm2)
        
        # Check various matching strategies
        return (
            check1 == check2 or
            check1 in check2 or
            check2 in check1 or
            norm1 in norm2 or
            norm2 in norm1
        )
    
    # Settings Methods
    def get_setting(self, key: str) -> Optional[str]:
        """Get bot setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT value FROM bot_settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result['value'] if result else None
        except Exception as e:
            logger.error(f"Error getting setting {key}: {e}")
            return None
        finally:
            conn.close()
    
    def set_setting(self, key: str, value: str):
        """Set bot setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO bot_settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value, datetime.now()))
            conn.commit()
            logger.info(f"Setting updated: {key}")
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")
            conn.rollback()
        finally:
            conn.close()

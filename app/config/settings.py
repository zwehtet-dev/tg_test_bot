"""
Bot Configuration
Centralized configuration management with validation
"""
import os
from pathlib import Path
from typing import List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Config:
    """Bot configuration with validation"""
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ADMIN_GROUP_ID: str = os.getenv("ADMIN_GROUP_ID", "")
    ADMIN_TOPIC_ID: str = os.getenv("ADMIN_TOPIC_ID", "")
    BALANCE_TOPIC_ID: str = os.getenv("BALANCE_TOPIC_ID", "3")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "exchange_bot.db"))
    
    # Exchange Configuration
    DEFAULT_EXCHANGE_RATE: float = float(os.getenv("DEFAULT_EXCHANGE_RATE", "121.5"))
    
    # Supported Banks
    THB_BANKS: List[str] = [
        "KBank", "SCB", "KTB", "Bangkok Bank", 
        "Kasikorn", "Siam Commercial", "PromptPay"
    ]
    MMK_BANKS: List[str] = [
        "KBZ", "AYA", "CB Bank", "KPay", "Wave Money", "UAB"
    ]
    
    # Initial Balances (currency, bank_name, balance)
    INITIAL_BALANCES: List[Tuple[str, str, float]] = [
    ]
    
    # File Paths
    RECEIPTS_DIR: Path = BASE_DIR / "receipts"
    ADMIN_RECEIPTS_DIR: Path = BASE_DIR / "admin_receipts"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "bot.log"))
    
    # Conversation States
    SELECT_DIRECTION: int = 0
    UPLOAD_RECEIPT: int = 1
    ENTER_AMOUNT: int = 2
    ENTER_BANK_INFO: int = 3
    
    # Timeouts (seconds)
    CONNECT_TIMEOUT: float = 30.0
    READ_TIMEOUT: float = 30.0
    WRITE_TIMEOUT: float = 30.0
    POOL_TIMEOUT: float = 30.0
    
    # Retry Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 2  # seconds
    
    # OCR Configuration
    OCR_SIMILARITY_THRESHOLD: float = 0.80  # 80% similarity for fuzzy matching
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        errors = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is not set")
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")
        
        if not cls.ADMIN_GROUP_ID:
            errors.append("ADMIN_GROUP_ID is not set")
        
        if errors:
            error_msg = "Configuration errors:\n" + "\n".join(f"- {e}" for e in errors)
            raise ValueError(error_msg)
        
        return True
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        cls.RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.ADMIN_RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        Path(cls.DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_database_path(cls) -> str:
        """Get absolute database path"""
        return str(Path(cls.DATABASE_PATH).resolve())

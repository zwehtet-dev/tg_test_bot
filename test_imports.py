#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")
print("-" * 60)

try:
    print("✓ Testing config...")
    from app.config import Config
    print(f"  Config loaded: {Config.__name__}")
    
    print("✓ Testing models...")
    from app.models import Transaction, ExchangeDirection, BankAccount
    print(f"  Models loaded: Transaction, ExchangeDirection, BankAccount")
    
    print("✓ Testing services...")
    from app.services import DatabaseService, OCRService
    print(f"  Services loaded: DatabaseService, OCRService")
    
    print("✓ Testing utils...")
    from app.utils import (
        private_chat_only, 
        admin_only,
        format_currency,
        validate_amount,
        setup_logger
    )
    print(f"  Utils loaded: decorators, formatters, validators, logger")
    
    print("✓ Testing handlers...")
    from app.handlers import UserHandlers, AdminHandlers
    print(f"  Handlers loaded: UserHandlers, AdminHandlers")
    
    print("✓ Testing main bot...")
    from app.bot import ExchangeBot
    print(f"  Bot loaded: ExchangeBot")
    
    print("-" * 60)
    print("✅ All imports successful!")
    print("")
    print("Your bot is ready to run!")
    print("Next steps:")
    print("  1. Configure .env file")
    print("  2. Run: python main.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

"""
Main entry point for THB ⇄ MMK Exchange Bot
"""
import sys
import logging
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import Config
from app.utils import setup_logger
from app.bot import ExchangeBot


def main():
    """Main function to start the bot"""
    try:
        # Setup logging
        logger = setup_logger(
            name="exchange_bot",
            log_file=Config.LOG_FILE,
            log_level=Config.LOG_LEVEL
        )
        
        logger.info("=" * 60)
        logger.info("Starting THB ⇄ MMK Exchange Bot v2.0")
        logger.info("=" * 60)
        
        # Validate configuration
        Config.validate()
        Config.create_directories()
        
        # Create and run bot
        bot = ExchangeBot()
        bot.run()
        
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

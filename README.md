# THB ⇄ MMK Exchange Bot

A Telegram bot for managing currency exchange between Thai Baht (THB) and Myanmar Kyat (MMK) with automated receipt processing, balance tracking, and admin management.

## Features

- 🔄 **Bidirectional Exchange**: THB → MMK and MMK → THB
- 📸 **OCR Receipt Processing**: Automatic receipt verification using OpenAI Vision
- 💰 **Balance Management**: Real-time balance tracking across multiple bank accounts
- 🏦 **Multi-Bank Support**: 9 pre-configured bank accounts (2 THB, 7 MMK)
- 👥 **Admin Controls**: Transaction approval, bank management, rate updates
- 📊 **Balance Reports**: Automated balance updates in dedicated topic
- 🔒 **Security**: Role-based access control and validation

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API Key
- Admin Group ID

### 1. Clone and Configure

```bash
git clone <your-repository-url>
cd currency_exchange_bot/tg_bot
cp .env.example .env
nano .env  # Edit with your credentials
```

### 2. Deploy

```bash
./start.sh
```

Or manually:

```bash
docker-compose up -d
```

That's it! The bot will automatically:
- ✅ Initialize database
- ✅ Create 9 bank accounts with balances
- ✅ Set up balance topic (ID: 3)
- ✅ Configure exchange rate (121.5)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Bank Accounts

### THB Accounts (2)
- **MMN (SCB)** - Siam Commercial Bank - 15,000 THB
- **TZH (Kbank)** - Krungthai Bank - 15,000 THB

### MMK Accounts (7)
- **CSTZ (KBZ)** - KBZ Special - 15,000,000 MMK
- **CSTZ (AYA)** - AYA Special - 15,000,000 MMK
- **CSTZ (Yoma)** - Yoma Bank - 15,000,000 MMK
- **CSTZ (CB)** - CB Special - 15,000,000 MMK
- **CS (MMP)** - Myanmar Pay - 15,000,000 MMK
- **CSTZ (AYA W)** - AYA Pay - 15,000,000 MMK
- **CSS (KBZ)** - KBZ Special (Store) - 15,000,000 MMK

## User Flow

1. User starts exchange with `/start`
2. Selects direction (THB → MMK or MMK → THB)
3. Uploads payment receipt
4. Bot extracts amount and bank details via OCR
5. User confirms bank account information
6. Admin receives notification in admin group
7. Admin uploads receipt and selects bank
8. User receives confirmation with admin receipt

## Admin Commands

- `/start` - Show admin menu
- `/setrate <rate>` - Update exchange rate
- `/balances` - View all bank balances
- `/addbank` - Add new bank account
- `/removebank` - Deactivate bank account
- `/recent` - View recent transactions
- `/settings` - View bot settings

## Architecture

```
tg_bot/
├── app/
│   ├── bot.py              # Main bot application
│   ├── config/             # Configuration
│   ├── handlers/           # User & admin handlers
│   ├── models/             # Data models
│   ├── services/           # Database & OCR services
│   └── utils/              # Utilities & helpers
├── data/                   # Database (volume)
├── receipts/               # User receipts (volume)
├── admin_receipts/         # Admin receipts (volume)
├── logs/                   # Application logs (volume)
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker Compose config
└── .env                    # Environment variables
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Telegram bot token |
| `ADMIN_GROUP_ID` | Yes | - | Admin group chat ID |
| `BALANCE_TOPIC_ID` | No | 3 | Balance updates topic ID |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `DEFAULT_EXCHANGE_RATE` | No | 121.5 | Initial exchange rate |

See `.env.example` for all available options.

## Development

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run bot
python main.py
```

### Project Structure

- **handlers/**: User and admin interaction handlers
- **services/**: Database and OCR service implementations
- **models/**: Data models (Transaction, BankAccount, etc.)
- **utils/**: Helper functions and decorators
- **config/**: Configuration management

## Technologies

- **Python 3.11+**
- **python-telegram-bot**: Telegram Bot API wrapper
- **OpenAI GPT-4 Vision**: OCR for receipt processing
- **SQLite**: Database for transactions and balances
- **Docker**: Containerization

## Security

- Environment variables for sensitive data
- Role-based access control (user/admin)
- Private chat validation
- Admin group verification
- Receipt validation and fuzzy matching

## Monitoring

### View Logs
```bash
docker-compose logs -f
```

### Check Status
```bash
docker-compose ps
```

### Database Backup
```bash
cp data/exchange_bot.db data/exchange_bot.db.backup_$(date +%Y%m%d)
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed troubleshooting guide.

Common issues:
- **ModuleNotFoundError**: Rebuild without cache: `docker-compose build --no-cache`
- **Bot not responding**: Check logs and verify bot token
- **OCR not working**: Verify OpenAI API key and credits
- **Admin commands not working**: Verify admin group ID

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md)
2. Review logs: `docker-compose logs -f`
3. Verify `.env` configuration

---

Made with ❤️ for seamless THB ⇄ MMK exchange

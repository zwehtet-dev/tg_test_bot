# Docker Deployment Guide

This guide will help you deploy the THB ⇄ MMK Exchange Bot on a VPS using Docker.

## Prerequisites

- VPS with Docker and Docker Compose installed
- Git installed on VPS
- Telegram Bot Token
- OpenAI API Key
- Admin Group ID

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd currency_exchange_bot/tg_bot
```

### 2. Configure Environment Variables

Copy the example environment file and edit it:

```bash
cp .env.example .env
nano .env  # or use vim, vi, etc.
```

Update the following required variables:

```env
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
ADMIN_GROUP_ID=-1001234567890  # Your actual admin group ID
BALANCE_TOPIC_ID=3  # Your balance topic ID (default: 3)
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. Start the Bot

```bash
# Build without cache to ensure fresh install
docker-compose build --no-cache
docker-compose up -d
```

Or use the quick start script:
```bash
./start.sh
```

That's it! The bot will:
- ✅ Automatically create the database
- ✅ Initialize all 9 bank accounts with balances
- ✅ Set up the balance topic ID
- ✅ Initialize the exchange rate to 121.5
- ✅ Start accepting transactions

## Verify Deployment

### Check if the bot is running:

```bash
docker-compose ps
```

### View logs:

```bash
docker-compose logs -f
```

You should see:
```
Starting database initialization...
Bank accounts already initialized (9 accounts found)
Settings already initialized (balance_topic_id: 3)
Database initialization complete!
```

### Check bot status in Telegram:

Send `/start` to your bot to verify it's responding.

## Bank Accounts Initialized

The following bank accounts are automatically initialized:

### THB Accounts (2):
- **MMN (SCB)** - Siam Commercial Bank - 15,000 THB
- **TZH (Kbank)** - Krungthai Bank - 15,000 THB

### MMK Accounts (7):
- **CSTZ (KBZ)** - KBZ Special - 15,000,000 MMK
- **CSTZ (AYA)** - AYA Special - 15,000,000 MMK
- **CSTZ (Yoma)** - Yoma Bank - 15,000,000 MMK
- **CSTZ (CB)** - CB Special - 15,000,000 MMK
- **CS (MMP)** - Myanmar Pay - 15,000,000 MMK
- **CSTZ (AYA W)** - AYA Pay - 15,000,000 MMK
- **CSS (KBZ)** - KBZ Special (Store) - 15,000,000 MMK

## Management Commands

### Stop the bot:
```bash
docker-compose down
```

### Restart the bot:
```bash
docker-compose restart
```

### Update the bot:
```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### View real-time logs:
```bash
docker-compose logs -f exchange-bot
```

### Access bot container:
```bash
docker-compose exec exchange-bot bash
```

## Data Persistence

The following directories are mounted as volumes and persist data:
- `./data` - Database file
- `./receipts` - User receipts
- `./admin_receipts` - Admin receipts
- `./logs` - Application logs

## Backup

To backup your data:

```bash
# Backup database
cp data/exchange_bot.db data/exchange_bot.db.backup_$(date +%Y%m%d_%H%M%S)

# Or backup everything
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz data/ receipts/ admin_receipts/ logs/
```

## Troubleshooting

### Bot not starting:

1. Check logs:
   ```bash
   docker-compose logs exchange-bot
   ```

2. Verify environment variables:
   ```bash
   docker-compose config
   ```

3. Check if ports are available:
   ```bash
   docker-compose ps
   ```

### Database issues:

If you need to reset the database:

```bash
docker-compose down
rm data/exchange_bot.db
docker-compose up -d
```

The database will be recreated with all bank accounts automatically.

### Permission issues:

```bash
sudo chown -R 1000:1000 data/ receipts/ admin_receipts/ logs/
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Your Telegram bot token |
| `ADMIN_GROUP_ID` | Yes | - | Admin group chat ID |
| `ADMIN_TOPIC_ID` | No | - | Admin topic ID (if using topics) |
| `BALANCE_TOPIC_ID` | No | 3 | Balance updates topic ID |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for OCR |
| `DATABASE_PATH` | No | data/exchange_bot.db | Database file path |
| `DEFAULT_EXCHANGE_RATE` | No | 121.5 | Initial exchange rate |
| `LOG_LEVEL` | No | INFO | Logging level |
| `LOG_FILE` | No | logs/bot.log | Log file path |

## Security Notes

- Never commit your `.env` file to git
- Keep your bot token and API keys secure
- Regularly backup your database
- Monitor logs for suspicious activity
- Use strong passwords for VPS access

## Support

If you encounter any issues:
1. Check the logs: `docker-compose logs -f`
2. Verify your `.env` configuration
3. Ensure Docker and Docker Compose are up to date
4. Check that all required ports are available

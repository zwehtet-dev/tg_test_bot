# 🚀 Quick Start Guide

## 1. Setup (30 seconds)

```bash
cd tg_bot
./setup.sh
```

This will:
- Create `.env` file if needed
- Create necessary directories
- Ask for deployment method (Docker or Local)
- Start the bot

## 2. Configure (1 minute)

Edit `.env` file:

```bash
nano .env
```

Add your credentials:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
ADMIN_GROUP_ID=-1001234567890
```

## 3. Start (10 seconds)

### With Docker (Recommended)
```bash
docker compose up -d
```

### Without Docker
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 4. Test (1 minute)

1. Send `/start` to your bot
2. You should see THB and MMK banks
3. Try clicking "🇹🇭 THB → MMK 🇲🇲"
4. Upload a test receipt

## 5. Monitor

```bash
# View logs
docker compose logs -f

# Check status
docker compose ps

# Restart
docker compose restart
```

## That's It! 🎉

Your bot is now running and ready to handle THB ⇄ MMK exchanges!

---

**Need help?** Check [README.md](README.md) for detailed documentation.

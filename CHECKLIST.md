# Pre-Deployment Checklist

Use this checklist before deploying to your VPS.

## ✅ Local Preparation

- [ ] All code changes committed to git
- [ ] `.env.example` is up to date
- [ ] `.env` is NOT committed (check `.gitignore`)
- [ ] Docker files are present:
  - [ ] `Dockerfile`
  - [ ] `docker-compose.yml`
  - [ ] `.dockerignore`
- [ ] Documentation is complete:
  - [ ] `README.md`
  - [ ] `DEPLOYMENT.md`
  - [ ] `CHECKLIST.md`

## ✅ Configuration Files

- [ ] `.env.example` contains all required variables
- [ ] `BALANCE_TOPIC_ID` default is set to `3`
- [ ] Bank accounts are defined in `app/utils/init_database.py`
- [ ] All 9 bank accounts are configured:
  - [ ] 2 THB accounts
  - [ ] 7 MMK accounts

## ✅ Code Verification

- [ ] No syntax errors: `python -m py_compile main.py`
- [ ] All imports are correct
- [ ] Database initialization is automatic
- [ ] Bank accounts initialize on first run
- [ ] Settings initialize on first run

## ✅ VPS Requirements

- [ ] VPS is accessible via SSH
- [ ] Docker is installed on VPS
- [ ] Docker Compose is installed on VPS
- [ ] Git is installed on VPS
- [ ] Sufficient disk space (at least 2GB free)
- [ ] Ports are available (bot doesn't need exposed ports)

## ✅ Telegram Setup

- [ ] Bot created via @BotFather
- [ ] Bot token obtained
- [ ] Admin group created
- [ ] Bot added to admin group as administrator
- [ ] Admin group ID obtained (use `/start` in group)
- [ ] Balance topic created (ID: 3 or custom)
- [ ] Bot has permission to post in topics

## ✅ API Keys

- [ ] OpenAI API key obtained
- [ ] OpenAI account has credits
- [ ] API key has access to GPT-4 Vision

## ✅ Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. On VPS - Clone Repository

```bash
git clone <your-repository-url>
cd currency_exchange_bot/tg_bot
```

### 3. On VPS - Configure Environment

```bash
cp .env.example .env
nano .env
```

Edit these required variables:
- [ ] `TELEGRAM_BOT_TOKEN=<your_bot_token>`
- [ ] `ADMIN_GROUP_ID=<your_admin_group_id>`
- [ ] `BALANCE_TOPIC_ID=3` (or your topic ID)
- [ ] `OPENAI_API_KEY=<your_openai_key>`

### 4. On VPS - Deploy

```bash
chmod +x start.sh
./start.sh
```

Or manually:
```bash
docker-compose up -d --build
```

### 5. Verify Deployment

- [ ] Check container is running: `docker-compose ps`
- [ ] Check logs: `docker-compose logs -f`
- [ ] Look for initialization messages:
  ```
  Starting database initialization...
  Bank accounts initialization complete: 9 accounts added
  Bot settings initialization complete
  ```
- [ ] Send `/start` to bot in Telegram
- [ ] Bot responds with menu
- [ ] Admin commands work in admin group

## ✅ Post-Deployment Verification

### Test User Flow
- [ ] User can start exchange
- [ ] User can upload receipt
- [ ] OCR extracts information correctly
- [ ] Admin receives notification
- [ ] Admin can upload receipt
- [ ] Admin can select bank
- [ ] User receives confirmation with admin receipt

### Test Admin Commands
- [ ] `/start` shows admin menu
- [ ] `/balances` shows all 9 bank accounts
- [ ] `/setrate` updates exchange rate
- [ ] `/recent` shows transactions
- [ ] `/settings` shows configuration

### Test Balance Updates
- [ ] Balance updates post to correct topic
- [ ] Balance overview is included
- [ ] All bank balances are shown

## ✅ Monitoring

- [ ] Set up log monitoring: `docker-compose logs -f`
- [ ] Set up disk space monitoring
- [ ] Set up backup schedule for database
- [ ] Document admin procedures

## ✅ Backup Strategy

- [ ] Database backup command documented
- [ ] Backup schedule established
- [ ] Backup restoration tested

## 🎉 Deployment Complete!

If all items are checked, your bot is ready for production use!

## Quick Commands Reference

```bash
# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart bot
docker-compose restart

# Stop bot
docker-compose down

# Update bot
git pull && docker-compose up -d --build

# Backup database
cp data/exchange_bot.db data/exchange_bot.db.backup_$(date +%Y%m%d)
```

## Troubleshooting

If something doesn't work:

1. **Check logs first**: `docker-compose logs -f exchange-bot`
2. **Verify .env**: `docker-compose config`
3. **Check container**: `docker-compose ps`
4. **Restart**: `docker-compose restart`
5. **Rebuild**: `docker-compose down && docker-compose up -d --build`

## Support

- Review `DEPLOYMENT.md` for detailed instructions
- Check logs for error messages
- Verify all environment variables are set correctly
- Ensure bot has proper permissions in Telegram group

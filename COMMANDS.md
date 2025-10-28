# Quick Command Reference

## Essential Commands for VPS

### First Time Deployment
```bash
git clone <your-repo-url>
cd currency_exchange_bot/tg_bot
cp .env.example .env
nano .env  # Edit with your credentials
mkdir -p data receipts admin_receipts logs
sudo chown -R 1000:1000 data receipts admin_receipts logs
docker-compose build --no-cache
docker-compose up -d
```

### Fix ModuleNotFoundError
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Fix Permission Errors
```bash
docker-compose down
sudo chown -R 1000:1000 data receipts admin_receipts logs
docker-compose up -d
```

### View Logs
```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Save logs to file
docker-compose logs > bot_logs.txt
```

### Check Status
```bash
# Container status
docker-compose ps

# Resource usage
docker stats

# Disk space
df -h
```

### Restart Bot
```bash
# Soft restart
docker-compose restart

# Hard restart
docker-compose down
docker-compose up -d
```

### Update Bot
```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Stop Bot
```bash
docker-compose down
```

### Backup Database
```bash
# Quick backup
cp data/exchange_bot.db data/exchange_bot.db.backup_$(date +%Y%m%d)

# Full backup
tar -czf backup_$(date +%Y%m%d).tar.gz data/ receipts/ admin_receipts/ logs/
```

### Clean Docker
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Clean everything
docker system prune -a
```

### Debug Commands
```bash
# Access container shell
docker-compose exec exchange-bot bash

# Check environment variables
docker-compose exec exchange-bot env

# Test database
docker-compose exec exchange-bot python -c "from app.services.database_service import DatabaseService; db = DatabaseService('data/exchange_bot.db'); print('Banks:', len(db.get_bank_accounts()))"

# Check Python packages
docker-compose exec exchange-bot pip list
```

### Emergency Reset
```bash
# CAUTION: This deletes all data!
docker-compose down
rm -rf data/ receipts/ admin_receipts/ logs/
mkdir -p data receipts admin_receipts logs
docker-compose build --no-cache
docker-compose up -d
```

## One-Liners

### Deploy from scratch
```bash
git clone <repo> && cd currency_exchange_bot/tg_bot && cp .env.example .env && nano .env && docker-compose build --no-cache && docker-compose up -d
```

### Quick fix and restart
```bash
docker-compose down && docker-compose build --no-cache && docker-compose up -d && docker-compose logs -f
```

### Update and restart
```bash
git pull && docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

### Backup and restart
```bash
cp data/exchange_bot.db data/exchange_bot.db.backup_$(date +%Y%m%d) && docker-compose restart
```

## Telegram Bot Commands

### User Commands
- `/start` - Start bot and show menu

### Admin Commands (in admin group)
- `/start` - Show admin menu
- `/setrate <rate>` - Update exchange rate
- `/balances` - View all bank balances
- `/addbank` - Add new bank account
- `/removebank` - Deactivate bank account
- `/recent` - View recent transactions
- `/settings` - View bot settings

## File Locations

- **Database:** `data/exchange_bot.db`
- **User Receipts:** `receipts/`
- **Admin Receipts:** `admin_receipts/`
- **Logs:** `logs/bot.log`
- **Config:** `.env`

## Important Notes

1. **Always use `--no-cache`** when building after updates
2. **Backup database** before major changes
3. **Check logs** if something doesn't work
4. **Never commit `.env`** to git
5. **Keep OpenAI credits** topped up for OCR

## Quick Checks

### Is bot running?
```bash
docker-compose ps | grep Up
```

### Any errors?
```bash
docker-compose logs --tail=50 | grep -i error
```

### Database OK?
```bash
ls -lh data/exchange_bot.db
```

### Disk space OK?
```bash
df -h | grep -E "Filesystem|/$"
```

---

**Bookmark this page for quick reference!**

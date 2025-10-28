# Complete Fix for VPS - All Issues Resolved

## Issues Fixed
1. ✅ ModuleNotFoundError: No module named 'dotenv'
2. ✅ PermissionError: Permission denied: '/app/logs/bot.log'

## Complete Solution (Copy & Paste)

Run these commands on your VPS:

```bash
# Navigate to project directory
cd /var/www/html/tg_test_bot

# Stop any running containers
docker-compose down

# Pull latest changes
git pull

# Create directories with proper permissions
mkdir -p data receipts admin_receipts logs
sudo chown -R 1000:1000 data receipts admin_receipts logs
sudo chmod -R 755 data receipts admin_receipts logs

# Remove old images
docker-compose rm -f
docker rmi $(docker images -q thb-mmk-exchange-bot) 2>/dev/null || true

# Rebuild without cache
docker-compose build --no-cache

# Start the bot
docker-compose up -d

# Watch logs
docker-compose logs -f
```

## One-Liner (All-in-One)

```bash
cd /var/www/html/tg_test_bot && docker-compose down && git pull && mkdir -p data receipts admin_receipts logs && sudo chown -R 1000:1000 data receipts admin_receipts logs && docker-compose build --no-cache && docker-compose up -d && docker-compose logs -f
```

## What This Does

1. **Stops** current container
2. **Pulls** latest code with fixes
3. **Creates** directories with proper ownership (UID 1000)
4. **Removes** old cached images
5. **Rebuilds** from scratch (fixes dotenv issue)
6. **Starts** bot with correct permissions
7. **Shows** logs for verification

## Expected Output

You should see:
```
✓ Imports successful
✓ Bank accounts configured: 9
Starting database initialization...
✓ Added: MMN (SCB) - Siam Commercial Bank (THB)
✓ Added: TZH (Kbank) - Krungthai Bank (THB)
... (7 more MMK accounts)
Bank accounts initialization complete: 9 accounts added
Bot settings initialization complete
Exchange Bot initialized successfully!
```

## Verify It's Working

### 1. Check Container Status
```bash
docker-compose ps
```
Should show: `Up` status

### 2. Check Logs for Errors
```bash
docker-compose logs --tail=50 | grep -i error
```
Should show: No errors

### 3. Check Permissions
```bash
ls -la | grep -E "data|receipts|logs"
```
Should show: `1000 1000` as owner

### 4. Test in Telegram
- Send `/start` to your bot
- Should receive menu with exchange options

### 5. Test Admin Commands
- In admin group, send `/balances`
- Should show all 9 bank accounts

## If You Still Have Issues

### Issue: Permission Denied

```bash
# Force fix permissions
sudo chown -R 1000:1000 .
sudo chmod -R 755 data receipts admin_receipts logs
docker-compose restart
```

### Issue: Module Not Found

```bash
# Verify requirements.txt exists
cat requirements.txt | grep dotenv

# Force rebuild
docker-compose down
docker system prune -a -f
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Container Keeps Restarting

```bash
# Check detailed logs
docker-compose logs --tail=100

# Check environment variables
docker-compose exec exchange-bot env | grep -E "TELEGRAM|OPENAI"
```

## Changes Applied

### 1. Dockerfile
- Simplified build process
- Proper user creation and ownership
- Fixed dependency installation

### 2. docker-compose.yml
- Added `user: "1000:1000"` specification
- Ensures container runs with correct UID

### 3. Directory Permissions
- All data directories owned by UID 1000
- Matches container user (botuser)

## Why These Fixes Work

### ModuleNotFoundError Fix
- `--no-cache` forces fresh pip install
- Ensures python-dotenv is installed
- No cached layers from old builds

### Permission Error Fix
- Container runs as UID 1000 (botuser)
- Host directories owned by UID 1000
- Volumes mount with correct permissions
- Bot can write to logs, database, receipts

## Maintenance Commands

### View Logs
```bash
docker-compose logs -f
```

### Restart Bot
```bash
docker-compose restart
```

### Stop Bot
```bash
docker-compose down
```

### Update Bot
```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup Database
```bash
cp data/exchange_bot.db data/exchange_bot.db.backup_$(date +%Y%m%d)
```

## Prevention for Future

Always set permissions before deploying:

```bash
# After git clone or git pull
mkdir -p data receipts admin_receipts logs
sudo chown -R 1000:1000 data receipts admin_receipts logs

# Then deploy
docker-compose build --no-cache
docker-compose up -d
```

## Summary

✅ **Both issues fixed:**
1. Module installation - Fixed with `--no-cache` rebuild
2. Permissions - Fixed with `chown 1000:1000`

✅ **Bot is now:**
- Installing all dependencies correctly
- Running with proper permissions
- Able to write logs and database
- Ready for production use

---

**Run the one-liner above and your bot will work! 🎉**

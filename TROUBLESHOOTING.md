# Troubleshooting Guide

## Common Issues and Solutions

### 1. ModuleNotFoundError: No module named 'dotenv'

**Symptoms:**
```
ModuleNotFoundError: No module named 'dotenv'
```

**Cause:** Docker build cache or incomplete dependency installation

**Solution:**

```bash
# Stop and remove containers
docker-compose down

# Remove old images
docker-compose rm -f
docker rmi thb-mmk-exchange-bot

# Rebuild without cache
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

**Alternative Solution:**
```bash
# One-liner to completely rebuild
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

### 2. Container Keeps Restarting

**Check logs:**
```bash
docker-compose logs -f exchange-bot
```

**Common causes:**
- Missing environment variables in `.env`
- Invalid bot token
- Invalid OpenAI API key
- Database permission issues

**Solution:**
1. Verify `.env` file has all required variables
2. Check logs for specific error messages
3. Ensure bot token is valid
4. Ensure OpenAI API key is valid

### 3. Permission Denied Errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: 'data/exchange_bot.db'
```

**Solution:**
```bash
# Fix permissions
sudo chown -R 1000:1000 data/ receipts/ admin_receipts/ logs/

# Or if that doesn't work
sudo chmod -R 777 data/ receipts/ admin_receipts/ logs/
```

### 4. Database Already Exists Error

**Symptoms:**
Bot starts but bank accounts aren't initialized

**Solution:**
The initialization is idempotent - it checks if data exists first. If you need to reset:

```bash
docker-compose down
rm data/exchange_bot.db
docker-compose up -d
```

### 5. Bot Not Responding in Telegram

**Check:**
1. Container is running: `docker-compose ps`
2. Logs show no errors: `docker-compose logs -f`
3. Bot token is correct in `.env`
4. Bot is not blocked by user

**Solution:**
```bash
# Restart bot
docker-compose restart

# If still not working, check token
docker-compose exec exchange-bot env | grep TELEGRAM_BOT_TOKEN
```

### 6. OCR Not Working

**Symptoms:**
Bot receives receipt but doesn't extract information

**Check:**
1. OpenAI API key is valid
2. OpenAI account has credits
3. API key has access to GPT-4 Vision

**Solution:**
```bash
# Check OpenAI key in container
docker-compose exec exchange-bot env | grep OPENAI_API_KEY

# Check logs for OpenAI errors
docker-compose logs -f | grep -i openai
```

### 7. Balance Updates Not Posting

**Symptoms:**
Transactions complete but balance updates don't appear in topic

**Check:**
1. `BALANCE_TOPIC_ID` is set correctly in `.env`
2. Bot has permission to post in topic
3. Topic exists in admin group

**Solution:**
```bash
# Check balance topic ID
docker-compose exec exchange-bot env | grep BALANCE_TOPIC_ID

# Verify in database
docker-compose exec exchange-bot python -c "
from app.services.database_service import DatabaseService
db = DatabaseService('data/exchange_bot.db')
print('Balance Topic ID:', db.get_setting('balance_topic_id'))
"
```

### 8. Docker Build Fails

**Symptoms:**
```
ERROR: failed to solve: process "/bin/sh -c pip install..." did not complete successfully
```

**Solution:**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

### 9. Out of Disk Space

**Check disk space:**
```bash
df -h
```

**Clean up Docker:**
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

### 10. Container Exits Immediately

**Check logs:**
```bash
docker-compose logs exchange-bot
```

**Common causes:**
- Configuration error in `.env`
- Missing required environment variables
- Python syntax error

**Solution:**
1. Check logs for specific error
2. Verify all required env vars are set
3. Test Python syntax locally if possible

## Debugging Commands

### View Container Status
```bash
docker-compose ps
```

### View Logs (Real-time)
```bash
docker-compose logs -f
```

### View Last 100 Lines of Logs
```bash
docker-compose logs --tail=100
```

### Access Container Shell
```bash
docker-compose exec exchange-bot bash
```

### Check Environment Variables
```bash
docker-compose exec exchange-bot env
```

### Test Database Connection
```bash
docker-compose exec exchange-bot python -c "
from app.services.database_service import DatabaseService
db = DatabaseService('data/exchange_bot.db')
print('Database OK')
print('Bank accounts:', len(db.get_bank_accounts()))
"
```

### Check Python Packages
```bash
docker-compose exec exchange-bot pip list
```

### Verify Bot Token
```bash
docker-compose exec exchange-bot python -c "
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
print('Token length:', len(token) if token else 0)
print('Token starts with:', token[:10] if token else 'None')
"
```

## Complete Reset

If nothing works, do a complete reset:

```bash
# Stop everything
docker-compose down

# Remove all data (BACKUP FIRST!)
rm -rf data/ receipts/ admin_receipts/ logs/

# Remove Docker images
docker rmi thb-mmk-exchange-bot

# Clean Docker cache
docker system prune -a

# Recreate directories
mkdir -p data receipts admin_receipts logs

# Rebuild and start
docker-compose build --no-cache
docker-compose up -d
```

## Getting Help

If you're still stuck:

1. **Check logs first:**
   ```bash
   docker-compose logs -f exchange-bot > bot_logs.txt
   ```

2. **Verify configuration:**
   ```bash
   docker-compose config > config_output.txt
   ```

3. **Check system resources:**
   ```bash
   docker stats
   df -h
   free -h
   ```

4. **Test network connectivity:**
   ```bash
   docker-compose exec exchange-bot ping -c 3 api.telegram.org
   docker-compose exec exchange-bot ping -c 3 api.openai.com
   ```

## Prevention Tips

1. **Always use `--no-cache` on first build:**
   ```bash
   docker-compose build --no-cache
   ```

2. **Keep backups:**
   ```bash
   # Daily backup script
   cp data/exchange_bot.db data/exchange_bot.db.backup_$(date +%Y%m%d)
   ```

3. **Monitor logs regularly:**
   ```bash
   docker-compose logs -f
   ```

4. **Update regularly:**
   ```bash
   git pull
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

5. **Test after updates:**
   - Send `/start` to bot
   - Check `/balances` in admin group
   - Test a small transaction

---

**Still having issues?** Check the logs carefully - they usually contain the exact error message that points to the solution.

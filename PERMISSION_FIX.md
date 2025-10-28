# Permission Fix - Complete Solution

## The Error
```
PermissionError: [Errno 13] Permission denied: '/app/logs/bot.log'
```

## Root Cause
The Docker container runs as user `botuser` (UID 1000), but the mounted volumes on the host are owned by root or another user.

## Complete Fix (Run on VPS)

### Step 1: Stop the Container
```bash
docker-compose down
```

### Step 2: Fix Directory Permissions
```bash
# Create directories if they don't exist
mkdir -p data receipts admin_receipts logs

# Set ownership to UID 1000 (matches botuser in container)
sudo chown -R 1000:1000 data receipts admin_receipts logs

# Set proper permissions
sudo chmod -R 755 data receipts admin_receipts logs
```

### Step 3: Rebuild and Start
```bash
# Rebuild without cache
docker-compose build --no-cache

# Start the bot
docker-compose up -d

# Check logs
docker-compose logs -f
```

## One-Liner Solution
```bash
docker-compose down && mkdir -p data receipts admin_receipts logs && sudo chown -R 1000:1000 data receipts admin_receipts logs && docker-compose build --no-cache && docker-compose up -d && docker-compose logs -f
```

## Verify Permissions
```bash
# Check directory ownership
ls -la | grep -E "data|receipts|logs"
```

Should show:
```
drwxr-xr-x  2 1000 1000  4096 Oct 28 15:00 data
drwxr-xr-x  2 1000 1000  4096 Oct 28 15:00 receipts
drwxr-xr-x  2 1000 1000  4096 Oct 28 15:00 admin_receipts
drwxr-xr-x  2 1000 1000  4096 Oct 28 15:00 logs
```

## Alternative: Run as Root (Not Recommended)

If you can't change ownership, you can run as root (less secure):

Edit `docker-compose.yml` and remove or comment out:
```yaml
# user: "1000:1000"
```

Then rebuild:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Prevention

When deploying fresh, always set permissions first:

```bash
# After cloning repository
cd currency_exchange_bot/tg_bot

# Create directories with proper ownership
mkdir -p data receipts admin_receipts logs
sudo chown -R 1000:1000 data receipts admin_receipts logs

# Then deploy
./start.sh
```

## Troubleshooting

### Still getting permission errors?

1. **Check current ownership:**
   ```bash
   ls -ln data receipts admin_receipts logs
   ```

2. **Force fix all permissions:**
   ```bash
   sudo chown -R 1000:1000 .
   sudo chmod -R 755 data receipts admin_receipts logs
   ```

3. **Check if directories are mounted:**
   ```bash
   docker-compose exec exchange-bot ls -la /app/
   ```

4. **Check container user:**
   ```bash
   docker-compose exec exchange-bot id
   ```
   Should show: `uid=1000(botuser) gid=1000(botuser)`

### Permission denied on specific files?

```bash
# Fix specific directory
sudo chown -R 1000:1000 logs/
sudo chmod -R 755 logs/

# Restart container
docker-compose restart
```

### Running on different user?

If your VPS user is not UID 1000, you have two options:

**Option 1: Match container UID to your user**
```bash
# Find your UID
id -u

# Edit docker-compose.yml
# Change: user: "1000:1000"
# To: user: "YOUR_UID:YOUR_UID"
```

**Option 2: Use UID 1000 (recommended)**
```bash
# Just set ownership to 1000
sudo chown -R 1000:1000 data receipts admin_receipts logs
```

## Summary

The key points:
1. ✅ Container runs as UID 1000 (botuser)
2. ✅ Host directories must be owned by UID 1000
3. ✅ Use `sudo chown -R 1000:1000` to fix
4. ✅ Always set permissions before first run

## Quick Reference

```bash
# Fix permissions
sudo chown -R 1000:1000 data receipts admin_receipts logs

# Restart bot
docker-compose restart

# Check logs
docker-compose logs -f
```

---

**After applying this fix, your bot should start without permission errors!**

# Quick Fix for VPS - ModuleNotFoundError

## The Problem
```
ModuleNotFoundError: No module named 'dotenv'
```

## The Solution

Run these commands on your VPS:

```bash
# 1. Stop the container
docker-compose down

# 2. Remove old images (force clean)
docker-compose rm -f
docker rmi $(docker images -q thb-mmk-exchange-bot) 2>/dev/null || true

# 3. Rebuild WITHOUT cache (this is critical!)
docker-compose build --no-cache

# 4. Start the bot
docker-compose up -d

# 5. Watch logs to verify it works
docker-compose logs -f
```

## One-Liner Solution

```bash
docker-compose down && docker-compose build --no-cache && docker-compose up -d && docker-compose logs -f
```

## What This Does

1. **Stops** the current broken container
2. **Removes** old cached images
3. **Rebuilds** from scratch (no cache = fresh install of all dependencies)
4. **Starts** the bot with fresh build
5. **Shows** logs so you can verify it's working

## Expected Output

You should see:
```
Starting database initialization...
✓ Added: MMN (SCB) - Siam Commercial Bank (THB)
✓ Added: TZH (Kbank) - Krungthai Bank (THB)
✓ Added: CSTZ (KBZ) - KBZ Special (MMK)
... (more bank accounts)
Bank accounts initialization complete: 9 accounts added
Bot settings initialization complete
Exchange Bot initialized successfully!
```

## If It Still Doesn't Work

1. **Check requirements.txt exists:**
   ```bash
   cat requirements.txt
   ```
   Should show `python-dotenv==1.0.0`

2. **Check Dockerfile:**
   ```bash
   cat Dockerfile | grep requirements
   ```
   Should show `COPY requirements.txt .` and `RUN pip install`

3. **Verify Docker can access files:**
   ```bash
   ls -la requirements.txt
   ls -la Dockerfile
   ```

4. **Try manual build:**
   ```bash
   docker build --no-cache -t thb-mmk-exchange-bot .
   docker-compose up -d
   ```

## Why This Happened

Docker was using cached layers from a previous build. The `--no-cache` flag forces Docker to:
- Re-copy requirements.txt
- Re-run pip install
- Install all dependencies fresh

## Prevention

Always use `--no-cache` on first build or after pulling updates:

```bash
git pull
docker-compose build --no-cache
docker-compose up -d
```

---

**After running the fix, your bot should start successfully!**

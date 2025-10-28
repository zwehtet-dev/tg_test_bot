# OpenAI Version Fix

## The Error
```
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```

## Root Cause
Version incompatibility between:
- `openai==1.54.3` (too new)
- `langchain-openai==0.2.8`
- `httpx` (missing version pin)

## Solution Applied

Updated `requirements.txt` with compatible versions:

```txt
# Before (incompatible)
openai==1.54.3
langchain-openai==0.2.8

# After (compatible)
openai==1.52.0
langchain-openai==0.2.5
httpx==0.27.2
```

## Fix on VPS

Run this command on your VPS:

```bash
cd /var/www/html/tg_test_bot && \
docker-compose down && \
git pull && \
mkdir -p data receipts admin_receipts logs && \
sudo chown -R 1000:1000 data receipts admin_receipts logs && \
docker-compose build --no-cache && \
docker-compose up -d && \
docker-compose logs -f
```

## What This Does

1. Stops current container
2. Pulls latest code with fixed package versions
3. Sets up permissions
4. Rebuilds with compatible packages
5. Starts bot
6. Shows logs

## Expected Result

You should see:
```
✓ OCR Service initialized with gpt-4o-mini
✓ Bank accounts already initialized (9 accounts found)
✓ Settings already initialized (balance_topic_id: 3)
✓ Exchange Bot initialized successfully!
```

## Why This Happened

OpenAI released version 1.54.3 which changed the internal API for `httpx` client initialization. The `langchain-openai` package wasn't updated yet to handle this change.

## Prevention

The requirements.txt now pins specific compatible versions, so this won't happen again.

## Verify It Works

```bash
# Check logs
docker-compose logs --tail=50

# Should NOT see "proxies" error
# Should see "Exchange Bot initialized successfully!"
```

## If Still Having Issues

```bash
# Force clean rebuild
docker-compose down
docker system prune -a -f
docker-compose build --no-cache
docker-compose up -d
```

---

**This fix is included in the latest code. Just run `git pull` and rebuild!**

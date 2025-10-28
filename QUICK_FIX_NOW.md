# 🚀 Quick Fix - Run This Now!

## The Command

Copy and paste this into your VPS terminal:

```bash
cd /var/www/html/tg_test_bot && docker-compose down && git pull && mkdir -p data receipts admin_receipts logs && sudo chown -R 1000:1000 data receipts admin_receipts logs && docker-compose build --no-cache && docker-compose up -d && docker-compose logs -f
```

## What It Does

1. ✅ Stops current container
2. ✅ Pulls latest code with fixed package versions
3. ✅ Sets up directories with correct permissions
4. ✅ Rebuilds Docker image (installs openai==1.52.0)
5. ✅ Starts bot
6. ✅ Shows logs

## Expected Output

```
✓ OCR Service initialized with gpt-4o-mini
✓ Bank accounts already initialized (9 accounts found)
✓ Settings already initialized (balance_topic_id: 3)
✓ Exchange Bot initialized successfully!
```

## Package Versions Fixed

- `openai==1.52.0` (compatible with langchain-openai 0.2.5)
- `langchain-openai==0.2.5`
- `httpx==0.27.2`

## Verify Success

```bash
# Check container is running
docker-compose ps

# Should show "Up" status
```

## Test in Telegram

1. Send `/start` to your bot
2. Should receive menu
3. In admin group, send `/balances`
4. Should show 9 bank accounts

---

**That's it! Your bot will work after running the command above.** 🎉

# Testing OCR Verification

## How to Test Admin Receipt Verification

### Setup
1. Deploy the bot to VPS
2. Ensure bot is running: `docker-compose ps`
3. Check logs: `docker-compose logs -f`

### Test Scenario 1: Correct Amount ✅

**Steps:**
1. User starts exchange: THB → MMK
2. User uploads receipt showing 1,000 THB
3. Bot calculates: 121,500 MMK (with rate 121.5)
4. Bot sends to admin group
5. **Admin replies with receipt showing 121,500 MMK**

**Expected Logs:**
```
INFO - Starting receipt verification for transaction #123, currency: MMK, expected: 121500.0
INFO - 🔍 Running OCR on admin receipt for transaction #123
INFO - OCR result for transaction #123: {'amount': '121500', ...}
INFO - 💰 Amount detected: 121500.0 MMK (expected: 121500.0 MMK)
INFO - ✅ Amount verified for transaction #123: 121500.0 MMK (diff: 0.0 MMK, within 1000 MMK tolerance)
```

**Expected Bot Response:**
```
✅ Receipt saved for Transaction #123

💰 Amount: 1,000.00 THB → 121,500 MMK
🏦 User's Bank: KBZ - 123456789

📤 Select which MMK bank you used for transfer:
[Bank buttons]
```

**No warning shown** ✅

---

### Test Scenario 2: Small Difference (Within Tolerance) ✅

**Steps:**
1. User exchange: 1,000 THB → 121,500 MMK
2. **Admin replies with receipt showing 121,000 MMK**

**Expected Logs:**
```
INFO - 💰 Amount detected: 121000.0 MMK (expected: 121500.0 MMK)
INFO - ✅ Amount verified for transaction #123: 121000.0 MMK (diff: 500.0 MMK, within 1000 MMK tolerance)
```

**Expected Bot Response:**
- No warning shown
- Shows bank selection buttons

**Difference: 500 MMK (within 1000 tolerance)** ✅

---

### Test Scenario 3: Amount Mismatch (Warning) ⚠️

**Steps:**
1. User exchange: 1,000 THB → 121,500 MMK
2. **Admin replies with receipt showing 120,000 MMK**

**Expected Logs:**
```
INFO - 💰 Amount detected: 120000.0 MMK (expected: 121500.0 MMK)
WARNING - ⚠️ AMOUNT MISMATCH in transaction #123: expected 121500.0, detected 120000.0, diff 1500.0
```

**Expected Bot Response:**
```
⚠️ Amount Mismatch Warning

Transaction #123
Expected: 121,500 MMK
Detected: 120,000 MMK
Difference: 1,500 MMK

Please verify the receipt shows the correct amount before proceeding.

---

✅ Receipt saved for Transaction #123
[Bank buttons still shown]
```

**Warning shown, but can still proceed** ⚠️

---

### Test Scenario 4: Major Mismatch ⚠️

**Steps:**
1. User exchange: 1,000 THB → 121,500 MMK
2. **Admin replies with receipt showing 100,000 MMK**

**Expected Logs:**
```
INFO - 💰 Amount detected: 100000.0 MMK (expected: 121500.0 MMK)
WARNING - ⚠️ AMOUNT MISMATCH in transaction #123: expected 121500.0, detected 100000.0, diff 21500.0
```

**Expected Bot Response:**
```
⚠️ Amount Mismatch Warning

Transaction #123
Expected: 121,500 MMK
Detected: 100,000 MMK
Difference: 21,500 MMK

Please verify the receipt shows the correct amount before proceeding.
```

**Large difference - likely wrong receipt** ⚠️

---

### Test Scenario 5: OCR Cannot Detect Amount

**Steps:**
1. User exchange: 1,000 THB → 121,500 MMK
2. **Admin replies with unclear/blurry receipt**

**Expected Logs:**
```
INFO - 🔍 Running OCR on admin receipt for transaction #123
INFO - OCR result for transaction #123: {'amount': None, ...}
WARNING - ⚠️ Could not detect amount in admin receipt #123
```

**Expected Bot Response:**
- No warning shown
- Shows bank selection buttons
- Proceeds normally

**OCR failure doesn't block workflow** ✅

---

### Test Scenario 6: THB Transaction (No Verification)

**Steps:**
1. User exchange: MMK → THB
2. Admin replies with receipt

**Expected Logs:**
```
INFO - Starting receipt verification for transaction #123, currency: THB, expected: 1000.0
INFO - Skipping OCR verification for transaction #123 (currency: THB, only MMK is verified)
```

**Expected Bot Response:**
- No OCR verification
- Shows bank selection buttons
- Proceeds normally

**Only MMK is verified** ✅

---

## How to View Logs

### Real-time Logs
```bash
docker-compose logs -f
```

### Filter for Verification
```bash
docker-compose logs | grep -E "🔍|💰|✅|⚠️|❌"
```

### Filter for Specific Transaction
```bash
docker-compose logs | grep "transaction #123"
```

### Last 100 Lines
```bash
docker-compose logs --tail=100
```

---

## Troubleshooting

### OCR Not Running

**Check 1: Is photo being uploaded?**
```bash
docker-compose logs | grep "No photo in message"
```

**Check 2: Is it a reply?**
```bash
docker-compose logs | grep "No reply_to_message"
```

**Check 3: Is OCR service initialized?**
```bash
docker-compose logs | grep "OCR Service initialized"
```

**Check 4: Is extract_receipt_info method being called?**
```bash
docker-compose logs | grep "extract_receipt_info"
```

**Check 4: OpenAI API key valid?**
```bash
docker-compose exec exchange-bot env | grep OPENAI_API_KEY
```

### OCR Running But No Detection

**Check logs for OCR result:**
```bash
docker-compose logs | grep "OCR result"
```

If you see:
```
OCR result for transaction #123: {'amount': None, ...}
```

This means OCR ran but couldn't detect the amount. Possible reasons:
- Receipt image is unclear
- Amount format not recognized
- Receipt is in unexpected format

### No Logs at All

**Check if handler is registered:**
```bash
docker-compose logs | grep "Admin receipt handler triggered"
```

If not appearing, the handler might not be triggered. Check:
1. Is admin replying to the correct message?
2. Does the message contain "Transaction ID:" or "Buy"?

---

## Expected Log Flow

Complete log flow for successful verification:

```
1. INFO - Admin receipt handler triggered. Replied text: ...
2. INFO - Found transaction #123 for user 123456 from message text
3. INFO - Admin receipt saved for transaction #123: admin_receipts/admin_123_...jpg
4. INFO - Starting receipt verification for transaction #123, currency: MMK, expected: 121500.0
5. INFO - 🔍 Running OCR on admin receipt for transaction #123
6. INFO - OCR result for transaction #123: {'amount': '121500', 'bank': 'KBZ', ...}
7. INFO - 💰 Amount detected: 121500.0 MMK (expected: 121500.0 MMK)
8. INFO - ✅ Amount verified for transaction #123: 121500.0 MMK (diff: 0.0 MMK, within 1000 MMK tolerance)
```

---

## Summary

✅ **OCR Verification is Working If You See:**
- "🔍 Running OCR on admin receipt"
- "💰 Amount detected"
- "✅ Amount verified" or "⚠️ AMOUNT MISMATCH"

❌ **OCR Verification is NOT Working If:**
- No logs about OCR
- No "🔍 Running OCR" message
- Errors in logs

🔧 **To Fix:**
1. Check OpenAI API key
2. Check OCR service initialization
3. Check photo is being uploaded
4. Check admin is replying to transaction message

---

**The feature is implemented and ready to test!**

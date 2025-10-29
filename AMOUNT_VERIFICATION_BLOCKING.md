# Amount Verification with Blocking

## Overview

When admin uploads a receipt with mismatched amount, the bot now **blocks** bank selection and requires either:
1. Upload correct receipt, OR
2. Click "Skip Verification" to proceed anyway

## How It Works

### Scenario 1: Amount Matches ✅

**Flow:**
1. Admin uploads receipt
2. Bot runs OCR: Detected 121,500 MMK
3. Bot compares: Expected 121,500 MMK
4. Difference: 0 MMK (within 1,000 tolerance)
5. ✅ Shows bank selection buttons immediately

**Bot Response:**
```
✅ Receipt saved for Transaction #123

💰 Amount: 1,000.00 THB → 121,500 MMK
🏦 User's Bank: KBZ

📤 Select which MMK bank you used for transfer:
[Bank buttons shown]
```

---

### Scenario 2: Small Difference (Within Tolerance) ✅

**Flow:**
1. Admin uploads receipt
2. Bot runs OCR: Detected 121,000 MMK
3. Bot compares: Expected 121,500 MMK
4. Difference: 500 MMK (within 1,000 tolerance)
5. ✅ Shows bank selection buttons

**Bot Response:**
```
✅ Receipt saved for Transaction #123

💰 Amount: 1,000.00 THB → 121,500 MMK
🏦 User's Bank: KBZ

📤 Select which MMK bank you used for transfer:
[Bank buttons shown]
```

---

### Scenario 3: Amount Mismatch (BLOCKED) ⚠️

**Flow:**
1. Admin uploads receipt
2. Bot runs OCR: Detected 305,250 MMK
3. Bot compares: Expected 199,900 MMK
4. Difference: 105,350 MMK (exceeds 1,000 tolerance)
5. ❌ **BLOCKS bank selection**
6. Shows warning with "Skip Verification" button

**Bot Response:**
```
⚠️ Amount Mismatch Detected

Transaction #15
Expected: 199,900 MMK
Detected: 305,250 MMK
Difference: 105,350 MMK

❌ Cannot proceed with bank selection

Options:
1. Upload the correct receipt (reply to this transaction again)
2. Click 'Skip Verification' below to proceed anyway

[⚠️ Skip Verification & Continue]
```

**Bank selection buttons NOT shown** ❌

---

### Scenario 4: Admin Uploads Correct Receipt

**Flow:**
1. Admin sees mismatch warning
2. Admin replies to transaction again with correct receipt
3. Bot runs OCR: Detected 199,900 MMK
4. Bot compares: Expected 199,900 MMK
5. ✅ Shows bank selection buttons

**Bot Response:**
```
✅ Receipt saved for Transaction #15

💰 Amount: 1,640.00 THB → 199,900 MMK
🏦 User's Bank: KBZ

📤 Select which MMK bank you used for transfer:
[Bank buttons shown]
```

---

### Scenario 5: Admin Clicks "Skip Verification"

**Flow:**
1. Admin sees mismatch warning
2. Admin clicks "⚠️ Skip Verification & Continue"
3. Bot logs: "Admin skipped verification"
4. Bot shows bank selection buttons

**Bot Response:**
```
⚠️ Verification Skipped by Admin

Transaction #15
💰 Amount: 1,640.00 THB → 199,900 MMK
🏦 User's Bank: KBZ

📤 Select which MMK bank you used for transfer:
[Bank buttons shown]
```

**Admin can now proceed** ✅

---

## Admin Options When Mismatch

### Option 1: Upload Correct Receipt (Recommended)
1. Find the correct receipt
2. Reply to the same transaction message
3. Upload the correct receipt photo
4. Bot will verify again

### Option 2: Skip Verification
1. Click "⚠️ Skip Verification & Continue" button
2. Bot will show bank selection
3. Transaction proceeds despite mismatch
4. **Logged for audit**

---

## Tolerance Settings

**Current Tolerance:** 1,000 MMK

**Examples:**
- Expected 150,000 MMK, Detected 150,500 MMK → ✅ Pass (500 diff)
- Expected 150,000 MMK, Detected 151,500 MMK → ⚠️ Block (1,500 diff)
- Expected 150,000 MMK, Detected 145,000 MMK → ⚠️ Block (5,000 diff)

**To Change Tolerance:**

Edit `app/handlers/admin_handlers.py`:
```python
# Current: 1,000 MMK
tolerance = 1000

# Change to 2,000 MMK
tolerance = 2000
```

---

## Logging

### Amount Match
```
INFO - ✅ Amount verified for transaction #123: 121500.0 MMK (diff: 0.0 MMK)
```

### Amount Mismatch (Blocked)
```
WARNING - ⚠️ AMOUNT MISMATCH in transaction #15: expected 199900, detected 305250, diff 105350
```

### Skip Verification
```
WARNING - ⚠️ Admin skipped verification for transaction #15
```

---

## Benefits

1. **Error Prevention**: Blocks wrong amounts from being confirmed
2. **Flexibility**: Admin can skip if needed (e.g., OCR error)
3. **Audit Trail**: All skips are logged
4. **User Protection**: Ensures correct amounts are sent
5. **Quality Control**: Forces verification of receipts

---

## Edge Cases

### OCR Fails to Detect Amount
- **Behavior**: Allows to proceed (doesn't block)
- **Reason**: Don't block workflow due to OCR failure
- **Logged**: Warning logged for review

### OCR Error/Exception
- **Behavior**: Allows to proceed (doesn't block)
- **Reason**: Don't block workflow due to technical error
- **Logged**: Error logged with stack trace

### THB Transactions
- **Behavior**: No verification (proceeds normally)
- **Reason**: Only MMK amounts are verified
- **Logged**: "Skipping OCR verification (currency: THB)"

---

## Testing

### Test 1: Correct Amount
1. Create transaction: 1,000 THB → 121,500 MMK
2. Admin uploads receipt showing 121,500 MMK
3. Expected: Bank buttons shown immediately

### Test 2: Wrong Amount
1. Create transaction: 1,000 THB → 121,500 MMK
2. Admin uploads receipt showing 100,000 MMK
3. Expected: Warning shown, bank buttons blocked
4. Admin uploads correct receipt
5. Expected: Bank buttons shown

### Test 3: Skip Verification
1. Create transaction: 1,000 THB → 121,500 MMK
2. Admin uploads receipt showing 100,000 MMK
3. Expected: Warning shown with skip button
4. Admin clicks "Skip Verification"
5. Expected: Bank buttons shown

---

## Summary

✅ **Mismatch Detection**: OCR verifies admin receipt amount  
❌ **Blocking**: Bank selection blocked if mismatch > 1,000 MMK  
🔄 **Re-upload**: Admin can upload correct receipt  
⚠️ **Skip Option**: Admin can skip verification if needed  
📝 **Audit Trail**: All actions logged  

**This ensures accurate transactions while maintaining flexibility!**

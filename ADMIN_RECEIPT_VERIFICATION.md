# Admin Receipt Verification Feature

## Overview

The bot now automatically verifies that the MMK amount in the admin's receipt matches the expected transaction amount using OCR.

## How It Works

### When Admin Uploads Receipt

1. **Admin replies with receipt photo** to a transaction
2. **Bot downloads and saves** the receipt
3. **Bot runs OCR** to extract the amount (for MMK only)
4. **Bot compares** detected amount with expected amount
5. **Bot warns** if there's a mismatch

### Verification Logic

```
Expected Amount: Transaction received_amount (MMK)
Detected Amount: OCR extracted from admin receipt
Tolerance: 1,000 MMK (fixed)

If |Detected - Expected| > 1,000 MMK:
    ⚠️ Show warning to admin
Else:
    ✅ Amount verified, proceed normally
```

## Example Scenarios

### Scenario 1: Amount Matches ✅

**Transaction:** User sends 1,000 THB → Receives 121,500 MMK

**Admin uploads receipt showing:** 121,500 MMK

**Result:** 
- ✅ Amount verified
- No warning shown
- Proceeds to bank selection

### Scenario 2: Amount Mismatch ⚠️

**Transaction:** User sends 1,000 THB → Receives 121,500 MMK

**Admin uploads receipt showing:** 120,000 MMK

**Result:**
```
⚠️ Amount Mismatch Warning

Transaction #123
Expected: 121,500 MMK
Detected: 120,000 MMK
Difference: 1,500 MMK

Please verify the receipt shows the correct amount before proceeding.
```

**Admin can:**
- Check the receipt again
- Upload a different receipt
- Proceed anyway (warning is informational)

### Scenario 3: OCR Cannot Detect Amount

**Admin uploads receipt** but OCR cannot extract amount

**Result:**
- No warning shown
- Proceeds normally
- Logged for admin review

## Features

### 1. Automatic Verification
- Runs automatically when admin uploads receipt
- No extra steps required
- Works in the background

### 2. Smart Tolerance
- Allows 1,000 MMK difference for OCR errors
- Example: For 121,500 MMK, allows 120,500 - 122,500 MMK range
- Prevents false alarms from minor OCR errors

### 3. MMK Only
- Only verifies MMK amounts (more critical)
- THB amounts are typically smaller and less prone to errors
- Can be extended to THB if needed

### 4. Non-Blocking
- Warning is informational only
- Admin can still proceed with transaction
- Doesn't stop the workflow

### 5. Logging
- All verifications logged
- Mismatches logged as warnings
- Helps track potential issues

## Benefits

1. **Error Prevention**: Catches wrong amounts before confirmation
2. **Quality Control**: Ensures admin uploaded correct receipt
3. **Audit Trail**: Logged for review
4. **User Protection**: Prevents sending wrong amounts
5. **Admin Awareness**: Alerts admin to double-check

## Technical Details

### Code Location
- **File**: `app/handlers/admin_handlers.py`
- **Function**: `handle_admin_receipt()`
- **Lines**: After receipt download, before bank selection

### OCR Service
- Uses same OCR service as user receipts
- Extracts amount from admin receipt
- Handles various receipt formats

### Tolerance Calculation
```python
tolerance = 1000  # Fixed 1,000 MMK
amount_diff = abs(detected_amount - expected_amount)

if amount_diff > tolerance:
    # Show warning
```

### Error Handling
- OCR errors don't block workflow
- Logged but transaction continues
- Admin can manually verify

## Configuration

### Adjust Tolerance

Edit `app/handlers/admin_handlers.py`:

```python
# Current: Fixed 1,000 MMK tolerance
tolerance = 1000

# Change to 2,000 MMK tolerance
tolerance = 2000

# Change to 500 MMK tolerance
tolerance = 500
```

### Enable for THB

Currently only checks MMK. To enable for THB:

```python
# Current
if to_currency == 'MMK':
    # verify

# Change to
if to_currency in ['MMK', 'THB']:
    # verify
```

## Examples

### Example 1: Perfect Match

```
Transaction: 150,000 MMK
Admin Receipt: 150,000 MMK
Difference: 0 MMK
Result: ✅ Verified, no warning
```

### Example 2: Within Tolerance

```
Transaction: 150,000 MMK
Admin Receipt: 150,500 MMK
Difference: 500 MMK
Tolerance: 1,000 MMK
Result: ✅ Within tolerance, no warning
```

### Example 3: Outside Tolerance

```
Transaction: 150,000 MMK
Admin Receipt: 145,000 MMK
Difference: 5,000 MMK
Tolerance: 1,000 MMK
Result: ⚠️ Warning shown
```

### Example 4: Major Mismatch

```
Transaction: 150,000 MMK
Admin Receipt: 100,000 MMK
Difference: 50,000 MMK
Tolerance: 1,000 MMK
Result: ⚠️ Warning shown - likely wrong receipt
```

## Admin Workflow

### Normal Flow (Amount Matches)

1. Admin replies with receipt to transaction
2. Bot: "✅ Receipt saved for Transaction #123"
3. Bot: Shows bank selection buttons
4. Admin: Selects bank
5. Transaction confirmed

### Warning Flow (Amount Mismatch)

1. Admin replies with receipt to transaction
2. Bot: "⚠️ Amount Mismatch Warning..."
3. Bot: Shows expected vs detected amounts
4. Bot: Still shows bank selection buttons
5. Admin: Can verify and proceed or upload new receipt

## Logging

### Success Log
```
INFO - Admin receipt amount verified: 150,000 MMK (expected 150,000 MMK)
```

### Warning Log
```
WARNING - Amount mismatch in admin receipt #123: expected 150000, detected 145000
```

### Error Log
```
ERROR - Error verifying admin receipt amount: [error details]
```

## Future Enhancements

Possible improvements:
1. Block transaction if mismatch is too large (>10%)
2. Require admin confirmation for mismatches
3. Verify bank name in receipt
4. Verify date/time in receipt
5. Store verification results in database
6. Admin dashboard showing verification stats

## Testing

To test the feature:

1. Create a transaction
2. Admin uploads receipt with correct amount → No warning
3. Admin uploads receipt with wrong amount → Warning shown
4. Check logs for verification messages

## Notes

- Verification is automatic and transparent
- Does not slow down the workflow
- Warning is informational, not blocking
- Helps catch human errors
- Improves transaction accuracy

---

**This feature adds an extra layer of verification to ensure transaction accuracy!**

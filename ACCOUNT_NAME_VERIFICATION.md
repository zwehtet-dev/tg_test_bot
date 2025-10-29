# Account Name Verification

## Overview

The bot now verifies that the account name in the admin's receipt matches the user's account name using OCR and fuzzy matching.

## How It Works

### Step 1: User Provides Account Info
```
User enters:
Bank: KBZ
Account Number: 123456789
Account Name: Aung Aung
```

### Step 2: Admin Uploads Receipt
```
Admin uploads receipt showing transfer to:
Account Name: Aung Aung
```

### Step 3: Bot Verifies
```
Bot extracts: "Aung Aung"
Bot compares with: "Aung Aung"
Similarity: 100%
✅ Verified!
```

---

## Scenarios

### Scenario 1: Exact Match ✅

**User Account:** Aung Aung  
**Receipt Shows:** Aung Aung  
**Similarity:** 100%

**Result:**
```
✅ Account name verified: 'Aung Aung' matches 'Aung Aung' (100% similarity)
```

**No warning shown** ✅

---

### Scenario 2: Minor Difference (High Similarity) ✅

**User Account:** Aung Aung  
**Receipt Shows:** AUNG AUNG  
**Similarity:** 100% (case-insensitive)

**Result:**
```
✅ Account name verified: 'AUNG AUNG' matches 'Aung Aung' (100% similarity)
```

**No warning shown** ✅

---

### Scenario 3: Typo (Medium Similarity) ✅

**User Account:** Aung Aung  
**Receipt Shows:** Aung Aaung  
**Similarity:** 90%

**Result:**
```
✅ Account name verified: 'Aung Aaung' matches 'Aung Aung' (90% similarity)
```

**No warning shown** (above 70% threshold) ✅

---

### Scenario 4: Different Name (Low Similarity) ⚠️

**User Account:** Aung Aung  
**Receipt Shows:** Kyaw Kyaw  
**Similarity:** 30%

**Result:**
```
WARNING - ⚠️ ACCOUNT NAME MISMATCH: expected 'Aung Aung', detected 'Kyaw Kyaw', similarity 30%
```

**Bot Response:**
```
⚠️ Account Name Warning

Transaction #15
Expected: Aung Aung
Detected: Kyaw Kyaw
Similarity: 30%

⚠️ Please verify you sent to the correct account!
```

**Warning shown but NOT blocking** ⚠️

---

### Scenario 5: OCR Cannot Detect Name

**User Account:** Aung Aung  
**Receipt Shows:** (unclear/not detected)

**Result:**
```
WARNING - ⚠️ Could not detect receiver account name in admin receipt #15
```

**No warning to admin** (proceeds normally)

---

## Fuzzy Matching

### How It Works

The bot uses **Levenshtein distance** to calculate similarity:

```python
similarity = _calculate_similarity("Aung Aung", "AUNG AUNG")
# Returns: 1.0 (100%)

similarity = _calculate_similarity("Aung Aung", "Aung Aaung")
# Returns: 0.9 (90%)

similarity = _calculate_similarity("Aung Aung", "Kyaw Kyaw")
# Returns: 0.3 (30%)
```

### Normalization

Names are normalized before comparison:
- **Case-insensitive**: "AUNG AUNG" = "aung aung"
- **Removes titles**: "Mr. Aung Aung" = "Aung Aung"
- **Removes spaces**: "Aung  Aung" = "AungAung"
- **Removes special chars**: "Aung-Aung" = "AungAung"

### Threshold

**Current:** 70% similarity

**Examples:**
- 100% - Exact match
- 90% - Minor typo
- 80% - Small difference
- 70% - Threshold (passes)
- 60% - Different name (fails)

---

## Behavior

### Non-Blocking

Account name verification is **informational only**:
- ✅ Shows warning if mismatch
- ✅ Does NOT block bank selection
- ✅ Admin can still proceed
- ✅ Logged for audit

### Why Non-Blocking?

1. OCR may not always detect name correctly
2. Name formats vary (with/without titles, etc.)
3. Admin can verify manually
4. Amount verification is more critical

---

## Configuration

### Adjust Similarity Threshold

Edit `app/handlers/admin_handlers.py`:

```python
# Current: 70% similarity
if similarity < 0.70:

# Change to 80% (stricter)
if similarity < 0.80:

# Change to 60% (more lenient)
if similarity < 0.60:
```

### Make It Blocking

To block on name mismatch:

```python
if similarity < 0.70:
    verification_passed = False  # Add this
    logger.warning(...)
    await update.message.reply_text(...)
    return  # Add this to block
```

---

## Logging

### Name Match
```
INFO - 👤 Checking account name: detected 'Aung Aung' vs expected 'Aung Aung'
INFO - ✅ Account name verified: 'Aung Aung' matches 'Aung Aung' (100% similarity)
```

### Name Mismatch
```
INFO - 👤 Checking account name: detected 'Kyaw Kyaw' vs expected 'Aung Aung'
WARNING - ⚠️ ACCOUNT NAME MISMATCH: expected 'Aung Aung', detected 'Kyaw Kyaw', similarity 30%
```

### Name Not Detected
```
WARNING - ⚠️ Could not detect receiver account name in admin receipt #15
```

---

## Examples

### Example 1: Perfect Match

```
User: Aung Aung
Receipt: Aung Aung
Result: ✅ Verified (100%)
```

### Example 2: Case Difference

```
User: Aung Aung
Receipt: AUNG AUNG
Result: ✅ Verified (100%)
```

### Example 3: With Title

```
User: Aung Aung
Receipt: Mr. Aung Aung
Result: ✅ Verified (100%)
```

### Example 4: Typo

```
User: Aung Aung
Receipt: Aung Aaung
Result: ✅ Verified (90%)
```

### Example 5: Wrong Name

```
User: Aung Aung
Receipt: Kyaw Kyaw
Result: ⚠️ Warning (30%)
```

---

## Combined Verification

### Both Amount and Name Verified ✅

```
✅ Amount verified: 200,000 MMK (exact match)
✅ Account name verified: 'Aung Aung' matches 'Aung Aung' (100% similarity)

[Bank selection buttons shown]
```

### Amount OK, Name Warning ⚠️

```
✅ Amount verified: 200,000 MMK (exact match)
⚠️ Account Name Warning
Expected: Aung Aung
Detected: Kyaw Kyaw

[Bank selection buttons still shown]
```

### Amount Mismatch (Blocked) ❌

```
⚠️ Amount Mismatch Detected
Expected: 199,900 MMK
Detected: 305,250 MMK

[Bank selection buttons NOT shown]
[Skip button shown]
```

---

## Benefits

1. **Error Detection**: Catches wrong account transfers
2. **Flexible**: Uses fuzzy matching for variations
3. **Non-Blocking**: Doesn't stop workflow
4. **Audit Trail**: All checks logged
5. **User Protection**: Warns admin of potential errors

---

## Limitations

1. **OCR Accuracy**: May not always detect name correctly
2. **Name Formats**: Different formats may affect matching
3. **Non-Blocking**: Admin can proceed despite warning
4. **Language**: Works best with English/Latin characters

---

## Summary

✅ **Verifies account name** from admin receipt  
✅ **Fuzzy matching** handles variations  
✅ **70% similarity threshold**  
⚠️ **Warning only** (non-blocking)  
📝 **All checks logged**  

**Helps ensure transfers go to the correct account!** 🎉

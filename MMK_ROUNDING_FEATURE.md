# MMK Rounding Feature

## Overview

All MMK amounts are automatically rounded to the nearest 100 MMK for cleaner transactions.

## How It Works

### Rounding Rules

MMK amounts are rounded to the nearest 50 with special rules:
- **00-50**: Round to nearest 50 (down to 00 or up to 50)
- **51-99**: Always round UP to next 00

**Examples:**
- `1,234,510 MMK` → `1,234,500 MMK` (10 rounds down)
- `1,234,525 MMK` → `1,234,500 MMK` (25 rounds down)
- `1,234,551 MMK` → `1,234,600 MMK` (51 rounds up)
- `123,456 MMK` → `123,500 MMK` (56 rounds up)
- `123,424 MMK` → `123,400 MMK` (24 rounds down)

### Exchange Calculations

#### THB → MMK
1. Calculate: `THB amount × exchange rate`
2. Round result to nearest 100 MMK

**Example (Rate: 121.5):**
- `1,000.00 THB` → `121,500 MMK` (exact, no rounding needed)
- `1,234.56 THB` → `150,000 MMK` (rounded from 149,999.04)
- `500.50 THB` → `60,800 MMK` (rounded from 60,810.75)

#### MMK → THB
1. Round MMK amount to nearest 100 first
2. Calculate: `Rounded MMK ÷ exchange rate`

**Example (Rate: 121.5):**
- `123,456 MMK` → `123,500 MMK` (56 rounds up) → `1,016.46 THB`
- `1,234,501 MMK` → `1,234,500 MMK` (01 rounds down) → `10,160.49 THB`
- `100,000 MMK` → `100,000 MMK` (already rounded) → `823.05 THB`

## Benefits

1. **Cleaner Amounts**: All amounts end in 00 or 50
2. **Easier Cash Handling**: Rounded to 50 MMK denominations
3. **Better User Experience**: Simpler amounts to remember
4. **Consistent**: Applied to all MMK transactions
5. **Fair Rounding**: 51-99 always rounds up for user benefit

## Implementation

The rounding is applied automatically in:
- Receipt OCR processing
- Manual amount entry
- Exchange calculations
- Transaction confirmations
- Admin notifications
- Balance updates

## Display Format

### MMK Amounts
- Displayed without decimals: `123,500 MMK`
- Always rounded to nearest 50 (ending in 00 or 50)

### THB Amounts
- Displayed with 2 decimals: `1,016.46 THB`
- Precise to the cent

## Examples

### User Flow Example

**User sends 1,234.56 THB:**
1. Bot calculates: `1,234.56 × 121.5 = 149,999.04 MMK`
2. Bot rounds: `149,999.04 → 150,000 MMK` (99 rounds up)
3. User sees: "You will receive **150,000 MMK**"

**User sends 123,456 MMK:**
1. Bot rounds first: `123,456 → 123,500 MMK` (56 rounds up)
2. Bot calculates: `123,500 ÷ 121.5 = 1,016.46 THB`
3. User sees: "Amount: **123,500 MMK** → You will receive **1,016.46 THB**"

## Testing

Run the test script to see rounding in action:

```bash
python test_rounding.py
```

## Code Location

- **Rounding Logic**: `app/utils/currency_utils.py`
- **Applied In**: 
  - `app/handlers/user_handlers.py` (user flow)
  - `app/handlers/admin_handlers.py` (admin notifications)

## Configuration

The rounding is set to 50 MMK with special rules (51-99 rounds up). To change:

Edit `app/utils/currency_utils.py`:
```python
def round_mmk_amount(amount: float) -> float:
    # Current: Rounds to 50 with 51-99 rounding up
    # Modify the logic in this function to change behavior
```

## Notes

- THB amounts are NOT rounded (kept at 2 decimal precision)
- Rounding happens BEFORE storing in database
- All historical transactions show rounded amounts
- Admin sees rounded amounts in all reports
- Amounts ending in 51-99 always round UP (user-friendly)
- All MMK amounts end in 00 or 50

---

**This feature ensures all MMK transactions use clean amounts ending in 00 or 50!**

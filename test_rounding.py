#!/usr/bin/env python3
"""
Test MMK rounding functionality
"""
from app.utils.currency_utils import round_mmk_amount, calculate_exchange

# Test cases for MMK rounding
test_cases = [
    1234510,  # Should be 1234500
    1234525,  # Should be ?
    1234551,  # You said should be 1234600
    1234575,  # Should be ?
    123456,   # Should be ?
    123475,   # Should be ?
    123424,   # Should be ?
    123450,   # Should be 123450
    123449,   # Should be ?
    100,
    99,
    75,
    50,
    25,
    1,
]

print("=" * 60)
print("MMK Rounding Test (Nearest 50)")
print("=" * 60)
print()

for amount in test_cases:
    rounded = round_mmk_amount(amount)
    print(f"{amount:>10,.0f} MMK  →  {rounded:>10,.0f} MMK")

print()
print("=" * 60)
print("Exchange Calculation Test (Rate: 121.5)")
print("=" * 60)
print()

rate = 121.5

# THB to MMK
print("THB → MMK:")
print("-" * 60)
thb_amounts = [1000, 1234.56, 500.50, 100]
for thb in thb_amounts:
    sent, received = calculate_exchange(thb, rate, 'THB', 'MMK')
    print(f"{thb:>10,.2f} THB  →  {received:>10,.0f} MMK (rounded)")

print()

# MMK to THB
print("MMK → THB:")
print("-" * 60)
mmk_amounts = [123456, 1234501, 100000, 50000]
for mmk in mmk_amounts:
    sent, received = calculate_exchange(mmk, rate, 'MMK', 'THB')
    print(f"{mmk:>10,.0f} MMK  →  {sent:>10,.0f} MMK (rounded)  →  {received:>10,.2f} THB")

print()
print("=" * 60)

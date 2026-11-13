# Money Problems · q10-03 · When cents overflow
# Python's ints never overflow, so we imitate a 32-bit signed integer.

def as_int32(n):
    n = n & 0xFFFFFFFF                     # keep the low 32 bits
    return n - 2**32 if n >= 2**31 else n  # reinterpret as signed

biggest = 2**31 - 1
print(f"largest 32-bit amount: {biggest} cents = ${biggest / 100:,.2f}")

balance = 2_000_000_000                    # $20,000,000.00 in cents
deposit = 200_000_000                      # $2,000,000.00 in cents
total = as_int32(balance + deposit)
print(f"$20,000,000.00 + $2,000,000.00 = {total / 100:,.2f} dollars")

safe = 2**53 - 1                           # JavaScript's Number.MAX_SAFE_INTEGER
print(f"JavaScript safe limit: {safe:,} cents")
print("next two whole numbers as floats:", float(safe + 1), float(safe + 2))

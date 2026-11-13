# Money Problems · q10-04 · Minor units that don't fit
# "Store cents" really means "store the smallest unit", and that varies.
from decimal import Decimal

minor_digits = {"USD": 2, "JPY": 0, "KWD": 3, "BTC": 8, "ETH": 18}
amount = Decimal("1234.5")
for code, digits in minor_digits.items():
    units = int(amount * 10**digits)
    print(f"{code}: 1234.5 = {units:,} minor units")

print("Wrong exponent: 1000 JPY stored as cents shows as",
      Decimal(1000) / 100, "JPY")

limit = 2**64 - 1                          # largest unsigned 64-bit integer
print("uint64 limit in wei:", limit)
print("that is only", Decimal(limit) / 10**18, "ether")

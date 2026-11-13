# Money Problems · q06-01 · Why 2.675 rounds down
# Try other prices: 2.665, 1.015, 0.625, 8.875 ...
from decimal import Decimal, ROUND_HALF_UP

for price in [2.675, 1.005, 0.125, 0.375]:
    print(f"round({price}, 2) = {round(price, 2)}")

print()
print("stored 2.675 =", Decimal(2.675))
print("stored 0.125 =", Decimal(0.125))

cent = Decimal("0.01")
print("Decimal('2.675') half-up =", Decimal("2.675").quantize(cent, ROUND_HALF_UP))

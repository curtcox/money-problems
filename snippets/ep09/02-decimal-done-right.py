# Money Problems · q09-02 · Decimal, done right
# Build decimals from strings, multiply, then round once, on purpose.
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

CENT = Decimal("0.01")
print("0.1 + 0.2       =", Decimal("0.1") + Decimal("0.2"))

price = Decimal("2.50")
rate = Decimal("0.05")
tax = price * rate
print("2.50 x 0.05     =", tax)
print("half up         =", tax.quantize(CENT, rounding=ROUND_HALF_UP))
print("half even       =", tax.quantize(CENT, rounding=ROUND_HALF_EVEN))

print("from '1.005'    =", Decimal("1.005").quantize(CENT, rounding=ROUND_HALF_UP))
print("from 1.005      =", Decimal(1.005).quantize(CENT, rounding=ROUND_HALF_UP))

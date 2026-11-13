# Money Problems · q10-01 · The Decimal(0.1) trap
# Decimal is exact, but only if you give it the digits you meant.
from decimal import Decimal

from_float = Decimal(0.1)        # the float's error comes along
from_text = Decimal("0.1")       # exactly one tenth

print("Decimal(0.1)   =", from_float)
print('Decimal("0.1") =', from_text)
print("equal?", from_float == from_text)

print("three dimes, from floats:", Decimal(0.1) * 3)
print("three dimes, from text:  ", Decimal("0.1") * 3)

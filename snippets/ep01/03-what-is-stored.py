# Money Problems · q01-03 · What the computer really stores
# Decimal(x) and Fraction(x) show the exact value of the double x, every digit.
from decimal import Decimal
from fractions import Fraction

stored = Fraction(0.1)
print("Decimal(0.1)  =", Decimal(0.1))
print("Fraction(0.1) =", stored)
print("denominator is 2**55:", stored.denominator == 2**55)

error = stored - Fraction(1, 10)
print("stored - 1/10 =", error)
print("              ≈", float(error))

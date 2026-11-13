# Money Problems · q10-02 · One third, to 28 places
# Decimal is base ten, but it still has a fixed number of digits.
from decimal import Decimal, getcontext, InvalidOperation

print("precision:", getcontext().prec, "digits")
third = Decimal(1) / Decimal(3)
print("1/3     =", third)
print("1/3 * 3 =", third * 3)
print("equals 1?", third * 3 == 1)

getcontext().prec = 6
print("with 6 digits: 1234.56 + 0.01 =", Decimal("1234.56") + Decimal("0.01"))
print("with 6 digits: 12345.67 + 0.01 =", Decimal("12345.67") + Decimal("0.01"))

try:
    print(Decimal("1.10") + 1.10)
except TypeError as error:
    print("Decimal + float:", error)

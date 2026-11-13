# Money Problems · q05-05 · Challenge: decimal arithmetic
# Python also ships base-ten and exact-fraction arithmetic.
# Challenge: try Decimal(0.1) without the quotes. What changes, and why?
from decimal import Decimal
from fractions import Fraction

print("floats:   ", 0.1 + 0.2, 0.1 + 0.2 == 0.3)
print("Decimal:  ", Decimal("0.1") + Decimal("0.2"),
      Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
print("Fraction: ", Fraction(1, 10) + Fraction(2, 10),
      Fraction(1, 10) + Fraction(2, 10) == Fraction(3, 10))

# Money Problems · q01-05 · Challenge: other denominators
# Prices in thousandths (mills) of a dollar: which ones are exact?
# Predict first, then try STEPS = 3, 8, 64, 1000, 1024, 100000 ...
from fractions import Fraction

STEPS = 1000
exact = [n for n in range(STEPS) if Fraction(n / STEPS) == Fraction(n, STEPS)]
print(len(exact), "of", STEPS, "are exact:", exact[:10])

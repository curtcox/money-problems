# Money Problems · q01-04 · Which cents are exact?
# For every amount from $0.00 to $0.99, compare the double with the true fraction.
from fractions import Fraction

exact = []
for cents in range(100):
    true_value = Fraction(cents, 100)
    stored = Fraction(cents / 100)       # the exact value of the double
    if stored == true_value:
        exact.append(cents)
print("exact:", exact)
print(len(exact), "of 100 cent values are stored exactly")

for cents in [10, 20, 30, 70]:
    diff = Fraction(cents / 100) - Fraction(cents, 100)
    side = "above" if diff > 0 else "below"
    print(f"0.{cents:02d} is stored {side} by {abs(float(diff)):.1e}")

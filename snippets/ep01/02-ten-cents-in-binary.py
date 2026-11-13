# Money Problems · q01-02 · Ten cents in binary
# Long division by doubling: double the fraction; the whole part is the next bit.
from fractions import Fraction

def binary_digits(x, count):
    bits = ""
    for _ in range(count):
        x = x * 2
        bit = int(x)          # 1 if the doubled value reached a whole one
        bits += str(bit)
        x = x - bit           # keep only the fraction
    return bits

print("1/4  = 0." + binary_digits(Fraction(1, 4), 8))
print("3/8  = 0." + binary_digits(Fraction(3, 8), 8))
print("1/10 = 0." + binary_digits(Fraction(1, 10), 32))
print("1/5  = 0." + binary_digits(Fraction(1, 5), 32))

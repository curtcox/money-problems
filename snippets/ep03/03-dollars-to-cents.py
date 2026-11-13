# Money Problems · q03-03 · Dollars to cents, the wrong way
# int() throws away the fraction, so 28.999999999999996 becomes 28.

for price in [0.29, 0.57, 1.15, 4.35, 19.99]:
    print(f"{price:>6}  * 100 = {price * 100!r:<20} int: {int(price * 100)}")

wrong = 0
for cents in range(10_000):                  # every amount from $0.00 to $99.99
    price = cents / 100
    if int(price * 100) != cents:
        wrong += 1
print(wrong, "of 10,000 amounts lose a cent with int()")
fixed = sum(round(c / 100 * 100) != c for c in range(10_000))
print(fixed, "of 10,000 amounts lose a cent with round()")

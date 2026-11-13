# Money Problems · q05-03 · JavaScript's integer ceiling
# JavaScript's Number is a double, so whole numbers are exact only up to 2**53.
# Python's int has no limit; float() shows what a double would hold.

limit = 2**53
print("2**53     =", limit)
for n in [limit - 1, limit, limit + 1, limit + 2, limit + 3]:
    print(f"{n} as a double -> {float(n):.0f}")

cents = limit + 1
print(f"${cents // 100:,}.{cents % 100:02d} in cents, as a double:", float(cents) == cents)

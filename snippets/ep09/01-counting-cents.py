# Money Problems · q09-01 · Counting cents
# The million-cent loop again: once with floats, once counting whole cents.

as_float = 0.0
as_cents = 0
for _ in range(1_000_000):
    as_float += 0.01           # measure a cent
    as_cents += 1              # count a cent

print("float total  =", as_float)
print("cents total  =", as_cents)
dollars, cents = divmod(as_cents, 100)
print(f"as money     = ${dollars:,}.{cents:02d}")
print("exactly $10,000.00?", as_cents == 10_000_00)

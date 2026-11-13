# Money Problems · q00-01 · Four surprises
# Each line works with dollars and cents. None of them prints what you'd expect.

print("0.10 + 0.20         =", 0.10 + 0.20)

total = 0.0
for _ in range(1_000_000):
    total += 0.01             # add one cent, a million times
print("a million cents     =", total)

print("int(1.15 * 100)     =", int(1.15 * 100))
print("round(2.675, 2)     =", round(2.675, 2))

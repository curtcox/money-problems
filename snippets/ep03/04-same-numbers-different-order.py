# Money Problems · q03-04 · Same numbers, different order
# A thousand random transactions, added up four ways. Change the seed!
import math
import random

def add_up(amounts):
    total = 0.0
    for amount in amounts:
        total += amount
    return total

random.seed(2024)
amounts = [random.randint(-50_000, 100_000) / 100 for _ in range(1_000)]

print("in order:   ", add_up(amounts))
print("reversed:   ", add_up(reversed(amounts)))
print("sorted:     ", add_up(sorted(amounts)))
print("sum():      ", sum(amounts))
print("math.fsum:  ", math.fsum(amounts))
print("exact cents:", sum(round(a * 100) for a in amounts) / 100)

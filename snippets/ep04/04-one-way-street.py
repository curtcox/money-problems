# Money Problems · q04-04 · Truncation's one-way street
# One day's interest on 100,000 accounts, cut to cents two ways.
import random
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_EVEN

random.seed(4)
CENT = Decimal("0.01")
DAILY = Decimal("0.05") / 365                    # 5% a year, one day
exact = truncated = rounded = Decimal(0)
for _ in range(100_000):
    balance = Decimal(random.randrange(1, 1_000_000)) / 100
    interest = balance * DAILY
    exact += interest
    truncated += interest.quantize(CENT, rounding=ROUND_DOWN)
    rounded += interest.quantize(CENT, rounding=ROUND_HALF_EVEN)

print("exact interest:   ", exact.quantize(CENT))
print("after truncating: ", truncated, " short by", (exact - truncated).quantize(CENT))
print("after rounding:   ", rounded, " off by", (exact - rounded).quantize(CENT))

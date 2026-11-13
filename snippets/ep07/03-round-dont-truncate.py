# Money Problems · q07-03 · Round, don't truncate
# The same 100,000 accounts. What's left over if the bank rounds to nearest?
import random
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

random.seed(1999)
cent = Decimal("0.01")
daily_rate = Decimal("0.035") / 365
interest = [Decimal(random.randint(1, 5_000_000)) / 100 * daily_rate
            for _ in range(100_000)]

for name, mode in [("truncate", ROUND_DOWN), ("half-up", ROUND_HALF_UP)]:
    slices = [i - i.quantize(cent, mode) for i in interest]
    kept = sum((s for s in slices if s > 0), Decimal(0))
    given = -sum((s for s in slices if s < 0), Decimal(0))
    print(f"{name:8}  bank keeps {kept.quantize(cent):>7}  bank gives {given.quantize(cent):>7}"
          f"  net {(kept - given).quantize(cent):>7}")

# Money Problems · q07-04 · The decimal point mistake
# Part 1: one wrong constant. Part 2: the same idea, with floats.
import random
from decimal import Decimal, ROUND_DOWN

random.seed(1999)
daily_rate = Decimal("0.035") / 365
interest = [Decimal(random.randint(1, 5_000_000)) / 100 * daily_rate
            for _ in range(10_000)]

def skim(unit):
    return sum(i - i.quantize(unit, ROUND_DOWN) for i in interest)

meant = skim(Decimal("0.01"))      # keep fractions of a cent
oops = skim(Decimal("1"))          # keep fractions of a dollar
print("meant:", meant.quantize(Decimal("0.01")), " oops:", oops.quantize(Decimal("0.01")),
      f" ({oops / meant:.0f} times as much)")

for dollars in [4.35, 1.15, 0.29]:
    cents = dollars * 100
    print(f"${dollars} is {cents!r} cents; float slice {cents - int(cents):.15f}¢")

# Money Problems · q07-05 · Challenge: catch the virus
# Every cent lands somewhere, so the books balance. Write a check that finds
# the skim. Hint: recompute each customer's interest with the bank's own rule
# (half-up to the cent) and compare it with what they were paid.
import random
from decimal import Decimal, ROUND_DOWN

random.seed(1999)
cent, tiny = Decimal("0.01"), Decimal("1e-10")
daily_rate = Decimal("0.035") / 365
balances = [Decimal(random.randint(1, 5_000_000)) / 100 for _ in range(1000)]

ledger = {"interest expense": Decimal(0), "customers": Decimal(0), "acct 1999": Decimal(0)}
paid = []
for b in balances:
    interest = (b * daily_rate).quantize(tiny)
    paid.append(interest.quantize(cent, ROUND_DOWN))
    ledger["interest expense"] -= interest
    ledger["customers"] += paid[-1]
    ledger["acct 1999"] += interest - paid[-1]

for name, amount in ledger.items():
    print(f"{name:17} {amount:>14}")
print("books balance:", sum(ledger.values()) == 0)
# Your check goes here.

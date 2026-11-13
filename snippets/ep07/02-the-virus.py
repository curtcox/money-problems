# Money Problems · q07-02 · The virus, in a few lines
# Our example, not the film's code: credit each account its daily interest
# truncated to the cent, and quietly keep whatever is left over.
import random
from decimal import Decimal, ROUND_DOWN

random.seed(1999)
cent = Decimal("0.01")
daily_rate = Decimal("0.035") / 365
N = 100_000
customers = hidden = Decimal(0)
for _ in range(N):
    balance = Decimal(random.randint(1, 5_000_000)) / 100   # $0.01 to $50,000
    interest = balance * daily_rate
    paid = interest.quantize(cent, ROUND_DOWN)             # truncate
    customers += paid
    hidden += interest - paid                              # the slice
print("accounts:       ", N)
print("paid to people: ", customers)
print("hidden account: ", hidden.quantize(cent))
print("average slice:  ", (hidden / N * 100).quantize(Decimal("0.001")), "cents")

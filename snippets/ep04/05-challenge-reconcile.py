# Money Problems · q04-05 · Challenge: reconcile these
# Three reports add the same 1,000 transactions in different orders.
# Challenge: store amounts as integer cents so all three agree exactly.
import random

def total(amounts):           # a plain running total, like most code and databases
    t = 0.0
    for a in amounts:
        t += a
    return t

random.seed(1)
amounts = [random.randrange(-50_000, 100_000) / 100 for _ in range(1000)]

print("in time order:  ", total(amounts))
print("largest first:  ", total(sorted(amounts, reverse=True)))
print("smallest first: ", total(sorted(amounts)))

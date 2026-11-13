# Money Problems · q09-05 · Challenge: test the invariant
# Ten thousand random splits: do the parts always add up to the whole?
# Challenge: add a test of your own, or break allocate and watch it fail.
import random

def float_split(total, n):                # the tempting way
    share = round(total / 100 / n, 2)
    return [round(share * 100) for _ in range(n)]

def allocate(total, n):                   # whole cents, extras to the first
    each, extra = divmod(total, n)
    return [each + 1] * extra + [each] * (n - extra)

rng = random.Random(2026)
for split in (float_split, allocate):
    failures = 0
    for _ in range(10_000):
        total = rng.randint(1, 1_000_000)  # up to $10,000.00, in cents
        n = rng.randint(1, 12)
        if sum(split(total, n)) != total:
            failures += 1
    print(f"{split.__name__:12} failed {failures} of 10000")

# Money Problems · q08-05 · Challenge: the Alabama paradox
# Largest remainder, with weights 1 : 3 : 3. Watch the first share as the pot grows.
# Challenge: find other weights where a bigger pot gives someone less.
# Bonus: write a split that rotates who gets the extra cent, month after month.

def allocate(total, weights):
    whole = sum(weights)
    shares, remainders = [], []
    for i, w in enumerate(weights):
        share, rem = divmod(total * w, whole)
        shares.append(share)
        remainders.append((-rem, i))
    for _, i in sorted(remainders)[:total - sum(shares)]:
        shares[i] += 1
    return shares

WEIGHTS = [1, 3, 3]
previous = None
for total in range(1, 9):
    shares = allocate(total, WEIGHTS)
    note = ""
    if previous and any(s < p for s, p in zip(shares, previous)):
        note = "  <- someone got less from a bigger pot"
    print(f"{total}¢ -> {shares}{note}")
    previous = shares

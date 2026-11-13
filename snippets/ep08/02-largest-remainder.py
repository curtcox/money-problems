# Money Problems · q08-02 · Largest remainder
# Split whole cents in proportion to weights. The parts always add up.
# Try other totals and weights, like allocate(100, [1, 1, 1, 1, 1, 1, 1]).

def allocate(total, weights):
    whole = sum(weights)
    shares, remainders = [], []
    for i, w in enumerate(weights):
        share, rem = divmod(total * w, whole)   # floor of each exact share
        shares.append(share)
        remainders.append((-rem, i))            # biggest remainder first, then position
    left_over = total - sum(shares)
    for _, i in sorted(remainders)[:left_over]:
        shares[i] += 1                          # one extra cent each
    return shares

def dollars(cents):
    return f"${cents // 100:,}.{cents % 100:02d}"

for total, weights in [(10_000, [1, 1, 1]),
                       (100_000, [1, 2, 3]),
                       (1_000, [333, 333, 334])]:
    parts = allocate(total, weights)
    print(dollars(total), weights, "->", [dollars(p) for p in parts],
          "sum", dollars(sum(parts)))

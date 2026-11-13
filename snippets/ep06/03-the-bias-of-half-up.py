# Money Problems · q06-03 · The bias of half-up
# Round every amount from $0.000 to $9.999 to cents, then add up the errors.
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

cent = Decimal("0.01")
amounts = [Decimal(n) / 1000 for n in range(10_000)]
ties = [a for a in amounts if a % cent == Decimal("0.005")]
print(len(amounts), "amounts, of which", len(ties), "are exact half-cent ties")

for name, mode in [("half-up", ROUND_HALF_UP), ("half-even", ROUND_HALF_EVEN)]:
    drift = sum(a.quantize(cent, mode) - a for a in amounts)
    tie_drift = sum(a.quantize(cent, mode) - a for a in ties)
    print(f"{name:9} total error {drift:+} (all from ties: {tie_drift:+})")

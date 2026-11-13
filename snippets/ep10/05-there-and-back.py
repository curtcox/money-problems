# Money Problems · q10-05 · Challenge: there and back again
# Convert dollars to euros and back, rounding to cents each way.
# Try other rates and amounts. Can you find a rate where nothing is lost?
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
rate = Decimal("0.8571")                   # euros per dollar (made up)
inverse = (1 / rate).quantize(Decimal("0.0001"), ROUND_HALF_UP)
print("rate:", rate, " inverse:", inverse, " rate * inverse:", rate * inverse)

for dollars in ["0.03", "19.99", "1000.00", "5000.00"]:
    usd = Decimal(dollars)
    eur = (usd * rate).quantize(CENT, ROUND_HALF_UP)
    back = (eur * inverse).quantize(CENT, ROUND_HALF_UP)
    print(f"${usd} -> €{eur} -> ${back}   change: {back - usd}")

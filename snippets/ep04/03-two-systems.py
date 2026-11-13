# Money Problems · q04-03 · Two systems, one cent apart
# The same 5% fee, computed by a float system and a Decimal system.
from decimal import Decimal, ROUND_HALF_UP

RATE = "0.05"
for price in ["0.30", "0.70", "1.00", "2.30", "2.50", "4.10"]:
    a = round(float(price) * float(RATE), 2)          # system A: floats
    b = (Decimal(price) * Decimal(RATE)).quantize(     # system B: decimals
        Decimal("0.01"), rounding=ROUND_HALF_UP)
    flag = "" if Decimal(str(a)) == b else "  <- break"
    print(f"${price}: float {a:.2f}  decimal {b}{flag}")

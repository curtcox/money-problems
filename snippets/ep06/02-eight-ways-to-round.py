# Money Problems · q06-02 · Eight ways to round
# Each row is one of Python's decimal rounding modes. Add your own amounts.
import decimal
from decimal import Decimal

amounts = ["2.341", "2.345", "2.355", "2.301", "-2.345"]
modes = ["ROUND_UP", "ROUND_DOWN", "ROUND_CEILING", "ROUND_FLOOR",
         "ROUND_HALF_UP", "ROUND_HALF_DOWN", "ROUND_HALF_EVEN", "ROUND_05UP"]

cent = Decimal("0.01")
print(f"{'':16}" + "".join(f"{a:>8}" for a in amounts))
for mode in modes:
    rounding = getattr(decimal, mode)
    row = [Decimal(a).quantize(cent, rounding) for a in amounts]
    print(f"{mode:16}" + "".join(f"{r:>8}" for r in row))

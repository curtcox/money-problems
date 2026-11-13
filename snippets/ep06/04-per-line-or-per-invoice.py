# Money Problems · q06-04 · Per line or per invoice
# The same receipt, the same tax rate, two places to round.
# Try other prices and rates.
from decimal import Decimal, ROUND_HALF_UP

cent = Decimal("0.01")
rate = Decimal("0.0825")
items = [Decimal("0.99"), Decimal("0.99"), Decimal("0.99")]

line_taxes = [(price * rate).quantize(cent, ROUND_HALF_UP) for price in items]
print("exact tax per line:", items[0] * rate)
print("rounded per line:  ", " + ".join(map(str, line_taxes)), "=", sum(line_taxes))

subtotal = sum(items)
print("exact tax on total:", subtotal * rate)
print("rounded on total:  ", (subtotal * rate).quantize(cent, ROUND_HALF_UP))

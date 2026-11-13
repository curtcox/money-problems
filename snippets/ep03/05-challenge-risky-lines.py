# Money Problems · q03-05 · Challenge: find the risky lines
# Five lines here can go wrong with money. Find them, then fix them.
# Hint: json.loads(text, parse_float=Decimal) and Decimal.quantize.
import json

text = '{"items": [0.29, 9.99, 19.99], "tax_rate": 0.0825, "paid": 32.77}'
order = json.loads(text)

subtotal = 0
for price in order["items"]:
    subtotal += price
tax = round(subtotal * order["tax_rate"], 2)
total = subtotal + tax
cents = int(total * 100)

print("subtotal", subtotal, " tax", tax, " total", total)
print("charging", cents, "cents")
print("paid in full" if order["paid"] == total else "balance due!")

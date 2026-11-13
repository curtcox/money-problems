# Money Problems · q09-04 · JSON without floats
# Read amounts as Decimal; write them as strings or whole minor units.
import json
from decimal import Decimal

text = '{"item": "coffee", "price": 4.35}'

as_float = json.loads(text)
print("float price x 100   =", as_float["price"] * 100)

as_decimal = json.loads(text, parse_float=Decimal)
print("Decimal price x 100 =", as_decimal["price"] * 100)

price = as_decimal["price"]
print(json.dumps({"price": str(price), "currency": "USD"}))
print(json.dumps({"price_minor": int(price * 100), "currency": "USD"}))

try:
    json.dumps({"price": price})
except TypeError as error:
    print("TypeError:", error)

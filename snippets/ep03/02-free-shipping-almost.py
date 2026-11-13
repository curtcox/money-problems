# Money Problems · q03-02 · Free shipping, almost
# These prices add up to exactly $50.00. Try them in another order.

cart = [16.99, 18.00, 15.01]
FREE_SHIPPING_AT = 50.00

subtotal = 0.0
for price in cart:
    subtotal += price
print("subtotal:", subtotal)
print(f"on screen: ${subtotal:.2f}")
if subtotal >= FREE_SHIPPING_AT:
    print("Free shipping!")
else:
    print(f"Add ${FREE_SHIPPING_AT - subtotal:.2f} more for free shipping.")

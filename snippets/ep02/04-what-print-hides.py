# Money Problems · q02-04 · What print hides
# print() shows the shortest decimal that leads back to the same double.

print("print(0.1)      ->", 0.1)
print("20 places       ->", f"{0.1:.20f}")
print("1.1 * 3         ->", 1.1 * 3)
print("3.3 == 1.1 * 3  ->", 3.3 == 1.1 * 3)

refund = 0.10 + 0.20 - 0.30          # should be exactly zero
print("refund          ->", refund)
balance = -refund                    # the same sliver, owed the other way
print("rounded         ->", round(balance, 2))
print("on a statement  ->", f"${balance:.2f}")

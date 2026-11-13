# Money Problems · q08-01 · A hundred dollars, three ways
# Three friends split a $100.00 bill. Do the shares add back up?

bill = 100.00
share = bill / 3
print("bill / 3       =", share)
each = round(share, 2)
print("each pays      =", each)
print("three shares   =", round(each * 3, 2))
print("missing        =", round(bill - each * 3, 2))

# The same split, counted in whole cents
each_cents, left_over = divmod(10_000, 3)
print("in cents:", each_cents, "each, and", left_over, "cent left over")

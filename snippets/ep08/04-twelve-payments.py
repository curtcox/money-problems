# Money Problems · q08-04 · Twelve payments
# $1,000.00 a year, paid monthly. Who pays the extra cents is a choice.

annual = 100_000                      # cents
naive = round(1000.00 / 12, 2)
print("float: 12 x", naive, "=", round(naive * 12, 2))

each, extra = divmod(annual, 12)
print("each", each, "with", extra, "cents left over")

last_pays = [each] * 11 + [each + extra]
first_pay = [each + 1] * extra + [each] * (12 - extra)
for name, plan in [("last month pays", last_pays), ("first months pay", first_pay)]:
    print(f"{name:17}", plan[:5], "...", plan[-2:], "sum", sum(plan))

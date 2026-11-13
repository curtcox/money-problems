# Money Problems · q08-03 · Spreading a discount
# A $5.00 coupon, shared across the lines of a receipt in proportion to price.

def allocate(total, weights):
    whole = sum(weights)
    shares, remainders = [], []
    for i, w in enumerate(weights):
        share, rem = divmod(total * w, whole)
        shares.append(share)
        remainders.append((-rem, i))
    for _, i in sorted(remainders)[:total - sum(shares)]:
        shares[i] += 1
    return shares

prices = [1999, 500, 1250]          # $19.99, $5.00, $12.50, in cents
coupon = 500                        # $5.00

naive = [round(coupon / 100 * p / sum(prices), 2) for p in prices]
print("rounded each line:", naive, "sum", round(sum(naive), 2))

shares = allocate(coupon, prices)
print("largest remainder:", shares, "sum", sum(shares))
for p, d in zip(prices, shares):
    print(f"  line {p:5d} - {d:3d} = {p - d:5d}")
print("receipt total:", sum(prices) - sum(shares), "=", sum(prices), "-", coupon)

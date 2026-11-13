# Money Problems · q07-01 · Where fractions of a penny come from
# One day's interest at 3.5% a year on a few balances. Try your own balance.
from decimal import Decimal, ROUND_DOWN

daily_rate = Decimal("0.035") / 365
for balance in ["1234.56", "250.00", "98765.43", "10.01"]:
    interest = Decimal(balance) * daily_rate
    whole_cents = interest.quantize(Decimal("0.01"), ROUND_DOWN)
    left_over = (interest - whole_cents) * 100
    print(f"${balance:>8}: interest {interest:.8f}  pay {whole_cents}  left {left_over:.4f}¢")

# Money Problems · q04-01 · Paid off, or not?
# A $1,000 loan in twelve payments: eleven of $83.33 and a last one of $83.37.

balance = 1000.00
payments = [83.33] * 11 + [83.37]
for month, payment in enumerate(payments, 1):
    balance -= payment
    if month >= 10:
        print(f"month {month:2}: balance ${balance:.2f}")

print("statement says:   ", f"${balance:.2f}")
print("balance == 0:     ", balance == 0)
print("what is stored:   ", balance)

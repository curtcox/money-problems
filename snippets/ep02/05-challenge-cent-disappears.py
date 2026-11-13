# Money Problems · q02-05 · Challenge: when a cent disappears
# Find the first power of two where adding one cent changes nothing.
# Then try other amounts: 0.001 (a mill), 1.00 (a dollar), 0.05 ...
AMOUNT = 0.01

power = 0
while 2.0 ** power + AMOUNT != 2.0 ** power:
    power += 1
print(f"2**{power} = ${2.0 ** power:,.0f}: adding {AMOUNT} does nothing")

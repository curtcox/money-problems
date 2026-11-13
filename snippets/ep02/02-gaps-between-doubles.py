# Money Problems · q02-02 · The gaps between doubles
# math.ulp(x) is the distance from x to the next double up.
import math

for dollars in [1, 1_000, 1_000_000, 1_000_000_000, 10**12, 10**15, 10**16]:
    print(f"${dollars:>22,}   gap {math.ulp(dollars):.3g}")

for power in [45, 46, 47]:
    x = 2.0 ** power
    print(f"2**{power} = ${x:,.0f}  gap {math.ulp(x)}  x + 0.01 == x: {x + 0.01 == x}")

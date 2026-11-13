# Money Problems · q02-03 · A house price in 32 bits
# struct can squeeze a number into a 32-bit float ("f") and read it back.
import math
import struct

def float32(x):
    return struct.unpack("f", struct.pack("f", x))[0]

for price in [1_234.56, 65_536.01, 131_072.01, 249_999.99, 1_000_000.01]:
    print(f"${price:>13,.2f}  stored as {float32(price):>16,}")

print("float32 gap at $131,072:", 2.0 ** (17 - 23))
print("float64 gap at $131,072:", math.ulp(131_072.0))

# Money Problems · q05-01 · Same bits everywhere
# The 64 bits of a double, in hexadecimal. Every language that uses
# IEEE 754 doubles stores exactly these bits for these numbers.
import struct

def bits(x):
    return struct.pack(">d", x).hex()

for name, x in [("0.1", 0.1), ("0.2", 0.2), ("0.1 + 0.2", 0.1 + 0.2), ("0.3", 0.3)]:
    print(f"{name:>9}  {bits(x)}")

# Money Problems · q02-01 · The bits of a double
# Try other amounts: 0.25, 19.99, 1234.56, -0.1 ...
import struct

def show(x):
    bits = format(struct.unpack(">Q", struct.pack(">d", x))[0], "064b")
    sign, exponent, fraction = bits[0], bits[1:12], bits[12:]
    print(f"{x!r}  hex {struct.pack('>d', x).hex()}  {float.hex(x)}")
    print("  sign", sign, " exponent", exponent, f"= {int(exponent, 2) - 1023:+d}")
    print("  fraction", fraction)

show(0.1)
show(0.25)

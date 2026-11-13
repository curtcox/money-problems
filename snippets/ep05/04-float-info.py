# Money Problems · q05-04 · What float really is
# Python's float is the machine's IEEE 754 double. sys.float_info describes it.
import sys

info = sys.float_info
print("significant bits (mant_dig):", info.mant_dig)
print("reliable decimal digits:    ", info.dig)
print("largest double:             ", info.max)
print("gap just above 1 (epsilon): ", info.epsilon)
print("radix (base):               ", info.radix)

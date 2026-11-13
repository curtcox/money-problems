# Money Problems · q06-05 · Challenge: the euro triangle
# The 1999 rules: Deutsche Mark to French franc goes through the euro.
# Challenge: how many whole amounts from 1 to 1000 DEM come out differently?
from decimal import Decimal, ROUND_HALF_UP

DEM = Decimal("1.95583")   # Deutsche Mark per euro, fixed in 1998
FRF = Decimal("6.55957")   # French francs per euro

def via_euro(dem):
    euro = (dem / DEM).quantize(Decimal("0.001"), ROUND_HALF_UP)  # at least 3 decimals
    return (euro * FRF).quantize(Decimal("0.01"), ROUND_HALF_UP)

def cross_rate(dem):       # not allowed by the rules
    return (dem * (FRF / DEM)).quantize(Decimal("0.01"), ROUND_HALF_UP)

amount = Decimal(100)
print("100 DEM via the euro:  ", via_euro(amount), "FRF")
print("100 DEM by cross rate: ", cross_rate(amount), "FRF")

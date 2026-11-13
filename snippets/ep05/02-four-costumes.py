# Money Problems · q05-02 · One value, four costumes
# One double, printed four common ways. Only the costume changes.

x = 0.1 + 0.2
print("shortest repr (Python, JavaScript, Java):", repr(x))
print("6 decimals    (C printf %f):             ", f"{x:.6f}")
print("15 digits     (spreadsheet display):     ", f"{x:.15g}")
print("17 digits     (C printf %.17g):          ", f"{x:.17g}")
print("is it 0.3?                               ", x == 0.3)

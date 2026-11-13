# Money Problems · q03-01 · A cent, a million times
# Add one cent over and over and watch the total drift from the truth.

total = 0.0
for count in range(1, 1_000_001):
    total += 0.01
    if count in (100, 1_000, 10_000, 100_000, 1_000_000):
        should_be = count / 100
        print(f"{count:>9,} cents  total {total!r:<20} off by {total - should_be:.1e}")

# Money Problems · q04-02 · The loop that skips zero
# "Pay ten cents until nothing is owed." The guard stops it after 13 steps;
# without the guard, this loop would never end.

owed = 1.00
steps = 0
while owed != 0 and steps < 13:
    owed -= 0.10
    steps += 1
    print(f"step {steps:2}: owed = {owed!r}")

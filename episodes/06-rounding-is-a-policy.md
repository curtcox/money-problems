# Episode 6 · Rounding is a policy

| | |
|---|---|
| Part | Living with it |
| Target length | about 15 min (segment estimates; set final timing from the narration audio) |
| Builds on | Episodes 1 and 2: stored doubles, the float line, ties to even |
| QR codes | q06-01 … q06-05 |

## Learning goals

By the end, the viewer can:

- explain why `round(2.675, 2)` returns 2.67 in Python;
- name the eight rounding modes in Python's `decimal` module and predict each on an example;
- explain why round-half-up drifts upward over many amounts and round-half-even doesn't;
- show that rounding per line and rounding the total can give different, equally valid answers;
- describe cash rounding and the euro conversion rules as examples of rounding written into policy and law.

## Script

### 6.1 Cold open · ≈ 0:46

**Visual.** [V6.1a] Black canvas. A price tag reading "$2.675" swings in. A `YELLOW`
arrow points at the final 5. [V6.1b] The q06-01 panel types out on the left; the console
prints `round(2.675, 2) = 2.67`. The 7 pulses `RED`. [V6.1c] The next three lines print
one by one: `1.0`, `0.12`, `0.38`. A small "?" hovers over each of the first two. [V6.1d]
The tag flips over; on its back, in tiny `BLUE` digits, the stored value
`2.67499999999999982236431605997495353221893310546875` scrolls past.

**On screen**

```python
for price in [2.675, 1.005, 0.125, 0.375]:
    print(f"round({price}, 2) = {round(price, 2)}")
```

```output
round(2.675, 2) = 2.67
round(1.005, 2) = 1.0
round(0.125, 2) = 0.12
round(0.375, 2) = 0.38
```

**QR q06-01** appears at [V6.1c], 8 seconds. Caption: "q06-01 · Why 2.675 rounds down".

> Round two dollars sixty-seven and a half cents to the nearest cent. At school you learned that a five rounds up, so the answer is two sixty-eight.
>
> Python says two sixty-seven. <break time="0.5s" /> A dollar and half a cent rounds to one dollar. Twelve and a half cents rounds down to twelve. And thirty-seven and a half cents rounds up to thirty-eight.
>
> Four amounts that each end in a five, and they don't even agree with each other. It looks like Python can't make up its mind.
>
> It can. Every one of these answers follows a precise rule. But there are two different rules tangled together here, and by the end of this video you'll be able to pull them apart. Along the way, we'll find that rounding isn't really arithmetic at all. It's a decision: someone has to choose how to round, and where. And sometimes that someone is a government.

### 6.2 Eight ways to round · ≈ 1:30

**Visual.** [V6.2a] A number line from 2.33 to 2.37 with cent ticks at 2.34, 2.35, 2.36.
Five `YELLOW` diamonds sit at 2.341, 2.345, 2.355, 2.301 (shown on an inset line near
2.30) and, on a mirrored line below zero, −2.345. [V6.2b] Code panel q06-02; the console
prints the header row and the table fills in one row at a time. For each row, the
diamonds slide along the number line to their rounded cent, leaving a short trail:
`ROUND_UP` pushes everything away from zero, `ROUND_DOWN` toward zero, `ROUND_CEILING`
right, `ROUND_FLOOR` left. [V6.2c] The three "half" rows: the 2.341 diamond moves to the
nearest cent in all three and greys out; the tie diamonds (2.345, 2.355, −2.345) are
outlined in `YELLOW` and each mode's tie-break arrow is drawn larger. [V6.2d] For
`ROUND_HALF_EVEN`, the ticks 2.34 and 2.36 are labelled "even" in `GREEN`; 2.345 slides
down to 2.34 and 2.355 slides up to 2.36. [V6.2e] `ROUND_05UP`: 2.301 first drops to
2.30, the last digit 0 lights up, and it bounces up to 2.31.

**On screen**

```python
cent = Decimal("0.01")
print(f"{'':16}" + "".join(f"{a:>8}" for a in amounts))
for mode in modes:
    rounding = getattr(decimal, mode)
    row = [Decimal(a).quantize(cent, rounding) for a in amounts]
    print(f"{mode:16}" + "".join(f"{r:>8}" for r in row))
```

```output
                   2.341   2.345   2.355   2.301  -2.345
ROUND_UP            2.35    2.35    2.36    2.31   -2.35
ROUND_DOWN          2.34    2.34    2.35    2.30   -2.34
ROUND_CEILING       2.35    2.35    2.36    2.31   -2.34
ROUND_FLOOR         2.34    2.34    2.35    2.30   -2.35
ROUND_HALF_UP       2.34    2.35    2.36    2.30   -2.35
ROUND_HALF_DOWN     2.34    2.34    2.35    2.30   -2.34
ROUND_HALF_EVEN     2.34    2.34    2.36    2.30   -2.34
ROUND_05UP          2.34    2.34    2.36    2.31   -2.34
```

**QR q06-02** appears at [V6.2b], 8 seconds. Caption: "q06-02 · Eight ways to round".

> Let's set floats aside for a moment and use Python's decimal module, which stores exactly the digits you give it. That way we can watch rounding by itself.
>
> Rounding to the cent means choosing one of two neighbouring cents. Python's decimal module offers eight different ways to choose, and the code in the corner applies all of them to the same five amounts.
>
> The first four ignore how close you are and only care about direction. Round up moves away from zero. Round down moves toward zero, which is the same as chopping off the extra digits: truncation. Ceiling always moves toward plus infinity, and floor toward minus infinity. For positive amounts, ceiling and up agree. For negative amounts, they don't, and the last column shows it.
>
> The next three are the ones people usually mean by rounding: go to the nearest cent. Two dollars, thirty-four and a tenth cents goes to two thirty-four, in all three. They only disagree when an amount sits exactly halfway, like two thirty-four and a half. Half up sends a tie away from zero. Half down sends it toward zero. And half even sends it to whichever neighbour has an even last digit. So two thirty-four and a half goes down to two thirty-four, and two thirty-five and a half goes up to two thirty-six.
>
> The eighth mode is a curiosity: zero five up. It truncates, unless that would leave a zero or a five in the last place, in which case it rounds away from zero instead. Two dollars, thirty and a tenth cents becomes two thirty-one.
>
> Eight rules, all reasonable, and they disagree in every column. None of them is "the correct one". Each is a choice.

### 6.3 Why round half to even · ≈ 1:12

**Visual.** [V6.3a] A strip of 10,000 tiny cells, one per amount from $0.000 to
$9.999, packed into a long band. Every tenth cell, the exact half-cent ties, is
outlined in `YELLOW`: "1000 ties". [V6.3b] Two balance-style meters, "half-up" and
"half-even", start at zero. As the strip scrolls, every non-tie cell nudges both meters
up or down by the same amount, and the needles wobble but stay centred. [V6.3c] At each
tie, half-up's needle ticks up by half a cent, every time; half-even's needle ticks down,
then up, then down, alternating. [V6.3d] The console prints the q06-03 output. Half-up's
meter ends at "+5.000" in `RED`; half-even's at "+0.000" in `GREEN`. [V6.3e] A caption:
"IEEE 754's default: round to nearest, ties to even."

**On screen**

```python
for name, mode in [("half-up", ROUND_HALF_UP), ("half-even", ROUND_HALF_EVEN)]:
    drift = sum(a.quantize(cent, mode) - a for a in amounts)
    tie_drift = sum(a.quantize(cent, mode) - a for a in ties)
    print(f"{name:9} total error {drift:+} (all from ties: {tie_drift:+})")
```

```output
10000 amounts, of which 1000 are exact half-cent ties
half-up   total error +5.000 (all from ties: +5.000)
half-even total error +0.000 (all from ties: +0.000)
```

**QR q06-03** appears at [V6.3d], 8 seconds. Caption: "q06-03 · The bias of half-up".

> Why would anyone prefer half even, the rule that rounds two thirty-four and a half down? Because of what happens to ties over many amounts.
>
> This code takes every amount from zero to nine dollars ninety-nine point nine, in steps of a tenth of a cent: ten thousand amounts. It rounds each one to the cent and adds up the errors.
>
> For most amounts, the two rules agree, and the errors cancel nicely: for every amount that rounds up by three tenths of a cent, there's another that rounds down by three tenths. But one amount in ten is an exact tie, and that's where they part ways. Half up rounds every tie upward, so every tie adds half a cent of error in the same direction. A thousand ties, five dollars of drift, all of it upward.
>
> Half even rounds half of the ties up and half of them down, so their errors cancel too. Total drift: zero.
>
> That's why it's the default for floating-point arithmetic, which you met in episode one when zero point one plus zero point two landed on a tie. It's also what Python's built-in round function does. It is often called banker's rounding, although whether bankers ever widely used it is a matter of debate. In practice, plenty of financial rules say half up. Which brings us back to the question of who gets to choose.

### 6.4 Two layers of rounding · ≈ 1:18

**Visual.** [V6.4a] The float line motif, zoomed near 2.675. The `YELLOW` diamond for
the true 2.675 sits exactly at the midpoint between the cent ticks 2.67 and 2.68 (drawn
far apart as large `GREY` ticks). Fine `BLUE` ticks are the doubles. [V6.4b] The diamond
snaps to the nearest `BLUE` tick, which is slightly left of the midpoint; a magnifier
shows the gap and the label "2.67499999999999982…". [V6.4c] From that `BLUE` tick, a
second arrow goes to the nearer cent tick: 2.67. Labels: "layer 1: typing 2.675 rounds to a
double", "layer 2: round() rounds that double to cents". [V6.4d] Split screen: 0.125's
diamond sits exactly on a `BLUE` tick ("stored exactly: a true tie"), and half-even sends
it to 0.12. [V6.4e] Last line of q06-01: `Decimal('2.675') half-up = 2.68` in `GREEN`.

**On screen**

```python
print("stored 2.675 =", Decimal(2.675))
print("stored 0.125 =", Decimal(0.125))
cent = Decimal("0.01")
print("Decimal('2.675') half-up =", Decimal("2.675").quantize(cent, ROUND_HALF_UP))
```

```output
stored 2.675 = 2.67499999999999982236431605997495353221893310546875
stored 0.125 = 0.125
Decimal('2.675') half-up = 2.68
```

> Now we can untangle the cold open. Python's round function rounds half to even. But that only explains two of the four answers.
>
> Twelve and a half cents is a quarter of a half: one eighth. A power of two in the denominator, so it's stored exactly. It really is a tie, and half even sends it to twelve. Thirty-seven and a half cents is three eighths, also exact, also a tie, and half even sends it to thirty-eight. So far, so consistent.
>
> But two point six seven five isn't stored exactly. When you typed it, the computer rounded it to the nearest double, and that double is a hair below the halfway point. Two point six seven four nine nine nine, and so on. So when round looks at it, it isn't looking at a tie at all. It's looking at a number slightly closer to two sixty-seven, and it rounds down. Any rounding rule would. The same thing happens to a dollar and half a cent.
>
> That's the second layer. Before your rounding rule ever runs, the float has already rounded your number once, to binary. The ties you meant may not be ties any more. And amounts that weren't ties can look like they are.
>
> The fix is to never let the float layer happen. Start from the digits you meant, as a string, in a decimal type. Decimal of the string two point six seven five, rounded half up to the cent, is two sixty-eight. Now there's only one layer of rounding, and it's the one you chose.

### 6.5 Per line or per invoice · ≈ 1:01

**Visual.** [V6.5a] The receipt motif: three lines, "Item 1 0.99", "Item 2 0.99",
"Item 3 0.99", subtotal 2.97, tax rate 8.25 %. [V6.5b] Left copy of the receipt: each line
grows a tax entry: 0.081675, which rounds to 0.08 in `BLUE`; three of them add to 0.24.
[V6.5c] Right copy: one tax entry on the subtotal: 0.245025, which rounds to 0.25.
[V6.5d] The two receipts side by side; the totals 0.24 and 0.25 glow, and a single penny
icon hovers between them, unsure which receipt it belongs to. [V6.5e] Both receipts get a
`GREEN` tick. A stamp: "Both correct. Pick one, and write it down."

**On screen**

```python
line_taxes = [(price * rate).quantize(cent, ROUND_HALF_UP) for price in items]
subtotal = sum(items)
print("rounded on total:  ", (subtotal * rate).quantize(cent, ROUND_HALF_UP))
```

```output
exact tax per line: 0.081675
rounded per line:   0.08 + 0.08 + 0.08 = 0.24
exact tax on total: 0.245025
rounded on total:   0.25
```

**QR q06-04** appears at [V6.5b], 8 seconds. Caption: "q06-04 · Per line or per invoice".

> So far we've asked how to round. Just as important is where.
>
> Here's a receipt: three items at ninety-nine cents each, with a sales tax of eight and a quarter percent. There are no floats anywhere in this code. Every number is an exact decimal. And yet there are two answers.
>
> If you work out the tax for each line, you get about eight point one seven cents. Round that to eight cents, three times, and the tax is twenty-four cents.
>
> If you add up the items first, and work out the tax on the total, you get about twenty-four and a half cents, which rounds to twenty-five.
>
> Which is right? Both. Each is a perfectly reasonable rule, applied exactly. The difference is a policy decision, not an error. Tax authorities, payment networks and accounting systems often specify which one to use, and sometimes it's up to you.
>
> But here's the trap. If your checkout page rounds per line and your invoicing system rounds the total, they'll disagree by a cent on some orders, and nobody will know which one is wrong, because neither is. So the rule has to be chosen once, written down, and used everywhere.

### 6.6 When there's no penny · ≈ 0:40

**Visual.** [V6.6a] A cash register display reading "$1.01", "$1.02", "$1.03" … "$1.10"
in a column. [V6.6b] A silver "5¢" coin icon replaces the penny icon, which fades out with a
small "2013" label. [V6.6c] Arrows map each total to the nearest five cents: 1.01 and 1.02
down to 1.00; 1.03 and 1.04 up to 1.05; 1.06 and 1.07 down to 1.05; 1.08 and 1.09 up to
1.10. [V6.6d] A card icon beside the register, with "$1.03 charged: $1.03" in `GREEN`.

> Sometimes the rounding rule comes from the coins themselves. In 2013, Canada stopped distributing pennies. Prices didn't change, and card payments are still charged to the cent. But when you pay in cash, the total is rounded to the nearest five cents. A dollar and one or two cents rounds down to a dollar. A dollar and three or four cents rounds up to a dollar and five.
>
> That's a rounding policy with its own increment, five cents instead of one, and it applies to one payment method but not another. The same basket of groceries can cost two different amounts, depending on how you pay, and both are correct.
>
> Several other countries have done something similar. If your software handles cash in any of them, rounding to the cent isn't even the right question.

### 6.7 Rounding written into law · ≈ 1:32

**Visual.** [V6.7a] A triangle of three currency labels: "DEM" (bottom left), "FRF" (bottom
right), "EUR" (top). The DEM–EUR edge is labelled "1.95583 per euro"; the FRF–EUR edge
"6.55957 per euro". [V6.7b] A list of rules types out beside it: "rates: 6 significant
figures", "never round or invert a rate", "national currency → national currency goes
through the euro", "the euro amount: at least 3 decimals", "results: nearest cent, halves
up". [V6.7c] Code panel q06-05 (`via_euro`). A gold "100 DEM" token travels up the left
edge to "51.129 EUR" (not shown in output; label it "≈ 51.129"), then down the right edge to
"335.38 FRF" in `GREEN`. [V6.7d] A dashed `RED` edge appears directly across the bottom,
labelled "cross rate (not allowed)". The token takes the shortcut and arrives at "335.39
FRF". [V6.7e] The two results side by side, one centime apart.

**On screen**

```python
def via_euro(dem):
    euro = (dem / DEM).quantize(Decimal("0.001"), ROUND_HALF_UP)  # at least 3 decimals
    return (euro * FRF).quantize(Decimal("0.01"), ROUND_HALF_UP)
def cross_rate(dem):       # not allowed by the rules
    return (dem * (FRF / DEM)).quantize(Decimal("0.01"), ROUND_HALF_UP)
```

```output
100 DEM via the euro:   335.38 FRF
100 DEM by cross rate:  335.39 FRF
```

> And sometimes the rounding rule is law.
>
> When the euro was introduced in 1999, eleven national currencies became fixed fractions of it. One euro was set at one point nine five five eight three Deutsche Mark, and at six point five five nine five seven French francs. For the next few years, banks and businesses had to convert amounts between these currencies constantly, and a European regulation spelled out exactly how.
>
> The rates have six significant figures, and you may not round them, or truncate them, or flip them upside down to make an inverse rate. To convert marks into francs, you must go through the euro: marks to euros, then euros to francs. The euro amount in the middle may be rounded, but to no fewer than three decimal places. And the final result is rounded to the nearest cent, or centime, with exact halves rounded up.
>
> The code follows those rules. A hundred marks becomes three hundred and thirty-five francs and thirty-eight centimes. Now take the obvious shortcut: divide the two rates to get a single mark-to-franc rate, and multiply. Three hundred and thirty-five francs, thirty-nine. One centime more, and against the rules.
>
> Why would lawmakers care about a centime? Because without one written rule, every bank would get slightly different answers, and every one of those differences would be a dispute. The point of the regulation wasn't to find the most accurate answer. It was to make sure everyone got the same one.

### 6.8 Recap and challenge · ≈ 1:08

**Visual.** [V6.8a] A recap column builds: "Rounding has a mode: up, down, ceiling, floor,
half-up, half-down, half-even, 05up" → "Half-up drifts; half-even doesn't" → "Floats round
first, so ties aren't ties" → "Where you round matters: per line ≠ per invoice" → "Write
the rule down; sometimes it's law". [V6.8b] The euro triangle returns with q06-05's code;
a counter labelled "amounts that differ, 1 to 1000 DEM" shows "?". [V6.8c] QR wall: q06-01
to q06-05 for 10 seconds. [V6.8d] Teaser: a gold penny is sliced into thin slivers, and
one sliver slides off into a jar labelled "?".

**QR q06-05** appears at [V6.8b], 10 seconds. Caption: "q06-05 · Challenge: the euro triangle".

> Let's take stock. Rounding isn't one operation. It's a family of rules, and Python's decimal module names eight of them. Half up is what most of us learned at school, but over many ties it drifts upward. Half even cancels that drift, which is why it's the default for floats and for Python's round. Floats add a second, hidden layer of rounding, so the ties you meant may not be ties any more; start from strings and decimals to avoid it. And where you round, per line or per invoice, can change the answer just as much as how. None of this is a fact of arithmetic. It's policy. Sometimes your team writes it, sometimes a payment network does, and sometimes it's the law.
>
> Here's a challenge. The code in the corner converts a hundred marks to francs both ways. Your job: loop over every whole amount from one to a thousand marks, and count how often the legal route and the shortcut disagree. Guess first. Is it a handful, or a lot?
>
> Next time: a film about three programmers who decided that the fractions of a penny left over by rounding should belong to them. What Office Space got right about money, and what it got wrong.

## Fact check before recording

- 6.3: "plenty of financial rules say half up" — e.g. the euro conversion rules in 6.7
  (halves rounded up); keep it general unless a further source is named.
- 6.8: the teaser's "three programmers" — confirm against the film (episode 7's fact check).

- 6.1, 6.4: `round(2.675, 2)` is 2.67 and `round(1.005, 2)` is 1.0 because the stored doubles
  are just below the halfway points; `round(0.125, 2)` is 0.12 and `round(0.375, 2)` is 0.38
  as exact ties rounded to even. All from q06-01's output.
- 6.2: the descriptions of the eight modes match Python's `decimal` documentation
  (`ROUND_05UP`: "Round away from zero if last digit after rounding towards zero would have
  been 0 or 5; otherwise round towards zero"). Confirm wording against
  docs.python.org/3/library/decimal.html.
- 6.3: Python's built-in `round()` uses round-half-to-even (Python 3; Python 2 rounded
  half away from zero). IEEE 754's default rounding attribute is roundTiesToEven.
- 6.3: "banker's rounding": the name is common, but its historical use by bankers is
  disputed; the script says so. Don't strengthen the claim.
- 6.5: "about eight point one seven cents" is 0.081675 dollars (8.1675 ¢); "about
  twenty-four and a half cents" is 0.245025.
- 6.5: "tax authorities ... often specify" — kept general on purpose. If a specific
  jurisdiction's rule is named on screen, cite it.
- 6.6: Canada: the Royal Canadian Mint stopped distributing pennies on 4 February 2013;
  the Government of Canada's guidance rounds cash totals (after tax) to the nearest five
  cents (1, 2 → 0; 3, 4 → 5; 6, 7 → 5; 8, 9 → 10); cheques and electronic payments are not
  rounded. Check canada.ca's "Phasing out the penny" page. "Several other countries"
  (for example Australia and New Zealand, which also round cash to 5 or 10 cents) —
  confirm before naming any on screen.
- 6.7: Council Regulation (EC) No 1103/97, Articles 4 and 5: rates as one euro in each
  national currency with six significant figures; not rounded or truncated when used;
  inverse rates not used; national-to-national conversion through the euro amount, which
  may be rounded to not less than three decimals; amounts rounded to the nearest cent,
  halves rounded up. Check the text on EUR-Lex. The irrevocable rates (DEM 1.95583,
  FRF 6.55957) were fixed by Council Regulation (EC) No 2866/98 on 31 December 1998;
  "eleven national currencies" from 1 January 1999 (Greece joined in 2001).
- 6.7: [V6.7c] label "≈ 51.129 EUR": 100 / 1.95583 rounded half up to three decimals is
  51.129 (checked in Python; not printed by the snippet, so it's a visual label only).
- 6.8 challenge answer (don't say it in narration): 162 of the amounts 1 to 1000 DEM
  differ between the two routes (checked in Python).

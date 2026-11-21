# Episode 3 · Where it bites

| | |
|---|---|
| Part | The problem |
| Target length | about 15 min (segment estimates; set final timing from the narration audio) |
| Builds on | Episodes 1–2: inexact cents, gaps between doubles, round to nearest |
| QR codes | q03-01 … q03-05 |

## Learning goals

By the end, the viewer can:

- name the situations where floating-point money errors are most likely: accumulation,
  comparisons and thresholds, conversion to cents, rates, order of addition, system
  boundaries, and extreme sizes;
- explain why `int(price * 100)` loses a cent for hundreds of everyday prices;
- explain why the same numbers can add up to different totals;
- spot the risky lines in a small piece of checkout code.

## Script

### 3.1 Cold open · ≈ 0:53

**Visual.** [V3.1a] A gold cent drops into a glass jar, then another, faster and faster,
while a counter climbs. [V3.1b] Code panel q03-01; the console prints one line at each
checkpoint: 100, 1,000, 10,000, 100,000, a million. Beside each line, the jar's label shows
the total. [V3.1c] The "off by" column lights up: `GREEN` for a moment at 100 (tiny), then the
digits creep left, column by column. The signs flip: plus, minus, plus, minus, plus, drawn as
a needle wobbling either side of a zero line, with each swing wider. [V3.1d] The final
total, `10000.000000171856`, enlarges; the tail glows `RED`.

**On screen**

```python
total = 0.0
for count in range(1, 1_000_001):
    total += 0.01
```

```output
      100 cents  total 1.0000000000000007   off by 6.7e-16
    1,000 cents  total 9.999999999999831    off by -1.7e-13
   10,000 cents  total 100.00000000001425   off by 1.4e-11
  100,000 cents  total 999.9999999992356    off by -7.6e-10
1,000,000 cents  total 10000.000000171856   off by 1.7e-07
```

**QR q03-01** appears at [V3.1b], 8 seconds. Caption: "q03-01 · A cent, a million times".

> Let's put a cent in a jar. And another. And keep going, a million times, keeping a running total in an ordinary Python float.
>
> After a hundred cents, the total should be one dollar. It's one dollar and less than a quadrillionth. After a thousand cents, it's a hair under ten dollars. After ten thousand, a hair over a hundred. And after a million cents, when we should have exactly ten thousand dollars, we have ten thousand dollars and about seventeen millionths of a cent.
>
> Watch the error column. It wobbles, high, then low, then high, but every swing is bigger than the last. Each single addition is as accurate as it can possibly be, but every one is rounded to the nearest double, and those roundings don't politely cancel out.
>
> In the last two episodes we saw what's inside a float. In this one, we go looking for trouble. Where, in real code, are these errors most likely to bite?

### 3.2 Accumulation · ≈ 1:00

**Visual.** [V3.2a] The float line returns. The running total is a `YELLOW` diamond hopping
right by one cent at a time; each hop lands between ticks and snaps to the nearest one. A
tiny `RED` sliver records each snap. [V3.2b] As the total grows, the camera zooms out and the
ticks spread apart (callback to episode 2); the slivers get bigger. [V3.2c] Four icons appear
in a row, each with a looping arrow: "running balance", "loop over line items", "daily
interest", "report summed row by row". Caption: "situation 1: accumulation".

> The first situation is the one we just saw: accumulation. Any time a program keeps a running total in a float, every step adds its own little rounding error.
>
> And there's a second effect, from the last episode. As the total gets bigger, the gaps between doubles get wider, so each addition can be off by more. Adding a cent to a dollar is very precise. Adding a cent to ten thousand dollars is less so. The total grows, and its precision shrinks.
>
> Where does this happen? A running balance updated with every transaction. A loop that adds up the items in an order. Interest calculated every day and added on. A report that sums a column, one row at a time. These are some of the most common lines of code anyone writes about money.
>
> Now, after a million additions we were off by less than a millionth of a dollar. Round to cents and it disappears. So on its own, accumulation is rarely the disaster. It's the seed. The disaster comes when that tiny error meets one of the next situations.

### 3.3 Comparisons and thresholds · ≈ 1:09

**Visual.** [V3.3a] A shopping cart icon with three tags: "$16.99", "$18.00", "$15.01", and a
banner: "Free shipping on orders of $50.00 or more". [V3.3b] Code panel q03-02; the console
prints `subtotal: 49.99999999999999`, then `on screen: $50.00` in `GREEN`. [V3.3c] The last
line prints, `Add $0.00 more for free shipping.`; the `$0.00` pulses `RED`. [V3.3d] The
float line near 50: a tick labelled "50.0" and the tick just left of it labelled
"49.99999999999999", with the subtotal diamond sitting on the left tick and a `RED` "<"
between them. [V3.3e] Other thresholds slide in as labels: "credit limit", "balance ≤ 0",
"payment == amount due", "over the reporting limit?".

**On screen**

```python
subtotal = 0.0
for price in cart:
    subtotal += price
print("subtotal:", subtotal)
print(f"on screen: ${subtotal:.2f}")
if subtotal >= FREE_SHIPPING_AT:
```

```output
subtotal: 49.99999999999999
on screen: $50.00
Add $0.00 more for free shipping.
```

**QR q03-02** appears at [V3.3b], 8 seconds. Caption: "q03-02 · Free shipping, almost".

> The second situation is comparison. Money is full of rules with a line in them. Free shipping at fifty dollars. A credit limit. A balance that must not go below zero. A payment that should equal the amount due.
>
> Here's a cart: sixteen ninety-nine, eighteen dollars, and fifteen oh one. That's exactly fifty dollars. Add them up in a float, and you get forty-nine point nine nine nine, and so on. Format it to two decimal places for the screen, and it shows fifty dollars. So the customer sees fifty dollars. But the comparison sees a number just below fifty, and the store cheerfully tells them to add zero dollars and zero cents more for free shipping.
>
> This is the most dangerous combination in the whole series. The error is far too small to see, and a comparison turns it into a yes-or-no answer that's simply wrong. A threshold doesn't care how close you were.
>
> And thresholds are exactly where money's rules live. Every equals equals, every greater-than-or-equal, every check against zero is a place where a sliver can flip the answer. Try the cart in a different order, by the way. Sometimes it comes out right, which makes this kind of bug very hard to reproduce.

### 3.4 Dollars to cents, the wrong way · ≈ 1:05

**Visual.** [V3.4a] A price tag "$0.29" enters a machine labelled "× 100", producing
"28.999999999999996", then a second machine labelled "int" which chops everything after the
point: "28". A cent rolls away. [V3.4b] Code panel q03-03; the console prints the five price
rows, with each `int` result in `RED`. [V3.4c] A 100 × 100 grid of tiny cells, one for every
amount from $0.00 to $99.99, fills in; 573 cells turn `RED`, in regular bands and stripes (draw the real pattern from q03-03; some rows, such as the $30s, have none). The count
line prints. [V3.4d] The `round()` line prints `0`: every red cell turns `GREEN`.

**On screen**

```python
for price in [0.29, 0.57, 1.15, 4.35, 19.99]:
    print(f"{price:>6}  * 100 = {price * 100!r:<20} int: {int(price * 100)}")
```

```output
  0.29  * 100 = 28.999999999999996   int: 28
  1.15  * 100 = 114.99999999999999   int: 114
 19.99  * 100 = 1998.9999999999998   int: 1998
573 of 10,000 amounts lose a cent with int()
0 of 10,000 amounts lose a cent with round()
```

**QR q03-03** appears at [V3.4b], 8 seconds. Caption: "q03-03 · Dollars to cents, the wrong way".

> The third situation is conversion. Lots of programs know they should count money in whole cents, so at some point they convert: take the dollar amount, multiply by a hundred, and turn it into an integer.
>
> Twenty-nine cents. Times a hundred is twenty-eight point nine nine nine, and so on, because twenty-nine cents was stored slightly low. And int doesn't round. It chops off everything after the point. Twenty-eight.
>
> A dollar fifteen becomes one hundred and fourteen. Nineteen ninety-nine becomes one thousand nine hundred and ninety-eight. The code is trying to do the right thing, and it loses a cent.
>
> How often? The code checks every amount from zero to ninety-nine dollars and ninety-nine cents. Five hundred and seventy-three of those ten thousand amounts come out a cent short. That's more than one in twenty. Not rare, not random-looking, and always in the same direction: down.
>
> Rounding instead of chopping fixes this particular conversion. Not one of the ten thousand amounts goes wrong with round. Keep that in mind, though: round fixes the conversion, not the float. Everything that happened to the number before you converted it is still there.

### 3.5 Multiplying by rates · ≈ 1:03

**Visual.** [V3.5a] A receipt (the receipt motif) with a subtotal, then lines appearing for
"tax 8.25%", "discount 15%", "interest 3.5% ÷ 365", "converted at 0.9187". Each product
shows a long tail of digits in `GREY`. [V3.5b] A number line from 1.00 to 1.01 with a `YELLOW`
diamond at the midpoint labelled "1.005": the true value is exactly halfway. Below it, the
stored double sits a hair to the left, and an arrow rounds it down to "1.0". Text beside it:
"round(1.005, 2) → 1.0". [V3.5c] Many diamonds land near midpoints; each one snaps the wrong
way when it sits on the wrong side, flashing `RED`.

**On screen**

```python
tax = round(subtotal * order["tax_rate"], 2)
```

> The fourth situation is multiplication by rates: sales tax, discounts, interest, exchange rates, commissions, fees. Multiply a price by a percentage, and the exact answer usually has more decimal places than a cent can hold, so it has to be rounded.
>
> That rounding is a decision about which way to go. And the decision depends on which side of the halfway point the answer falls. Here's the problem: when the exact answer is very close to half a cent, a float can't say which side it's on.
>
> Take one dollar and half a cent. Round it to cents and most of us expect a dollar and one cent. Python's round gives one dollar. That's not because round is broken. It's because the double nearest one point zero zero five is a hair below it, so as far as round can tell, it's nearer one dollar.
>
> Rates create these near-halfway answers all the time, and every one of them is a coin flip decided by representation error rather than by your rules. Episode six is all about rounding: the policies, the modes, and the trap of rounding a number that was already rounded once.

### 3.6 Same numbers, different order · ≈ 1:14

**Visual.** [V3.6a] Code panel q03-04: the `add_up` function. A deck of a thousand cards, each
a transaction amount, shuffles. [V3.6b] The console prints three totals from `add_up`: in
order, reversed, sorted. All three differ in their last digits, highlighted `RED`. [V3.6c] The
next three lines print `241354.0` in `GREEN`: `sum()`, `math.fsum`, exact cents. [V3.6d] A
diagram of a database query: a table split across four worker boxes, each summing its part,
then a final box adding the four partial sums. The partitions reshuffle and the final total's
last digits change. Caption: "order not guaranteed".

**On screen**

```python
def add_up(amounts):
    total = 0.0
    for amount in amounts:
        total += amount
    return total
```

```output
in order:    241353.99999999988
reversed:    241354.0000000001
sorted:      241354.00000000003
sum():       241354.0
math.fsum:   241354.0
exact cents: 241354.0
```

**QR q03-04** appears at [V3.6b], 8 seconds. Caption: "q03-04 · Same numbers, different order".

> The fifth situation is a strange one. In school, addition doesn't care about order. A plus B plus C is the same as C plus B plus A. With floats, it isn't, because every addition rounds, and what gets rounded depends on what's been added so far.
>
> Here are a thousand random transactions. Add them up the plain way, in order, and the total ends in nine nine nine eight eight. Reverse them and it ends in zero zero zero one. Sort them and you get yet another answer. Same numbers. Three different totals.
>
> Python's built-in sum gets it right here. Since Python three point twelve, sum quietly uses a cleverer method, called compensated summation, that keeps track of the bits each addition throws away. Math dot fsum goes further and gives the exactly rounded answer. But most code, in most languages, adds the plain way.
>
> And order is something you often don't control. A database adding up a column may split the work between several workers and combine the pieces in whatever order they finish. A distributed job does the same across machines. So the same report, run twice on the same data, can produce totals that differ in the last digits. Usually, rounding to cents hides it. Occasionally, it doesn't, and then nobody can explain why yesterday's number changed.

### 3.7 Crossing boundaries · ≈ 0:54

**Visual.** [V3.7a] A chain of system boxes: "web page (JavaScript)" → "JSON" → "API server" →
"CSV export" → "spreadsheet" → "data frame". A gold amount "$19.99" travels along the arrows.
[V3.7b] At each hop where the amount becomes a binary float, a small `BLUE` "float" badge
snaps onto it; the amount gains a faint grey tail of digits. [V3.7c] Zoom on the JSON hop:
the q03-05 line `order = json.loads(text)` with a badge "items become floats". Beside it,
`parse_float=Decimal` appears in `GREEN` as the alternative.

**On screen**

```python
order = json.loads(text)
```

> The sixth situation is crossing a boundary. Money rarely stays inside one program. It travels: from a web page to a server as JSON, from a database to a CSV file, from a CSV file into a spreadsheet or a data analysis library.
>
> And at each crossing, it can quietly turn into a float. Python's json dot loads reads a number with a decimal point as a float, unless you ask for something else. JavaScript's JSON parser turns every number into a double, because a double is its everyday kind of number. Spreadsheets store numbers as doubles. Data-frame libraries that read CSV files usually guess that a column of prices is a column of floats.
>
> So even if your own code is careful, the amount may have been a float for a while before it reached you, or may become one right after it leaves. A system is only as exact as the least exact place the money passes through.

### 3.8 Very big, very small · ≈ 0:39

**Visual.** [V3.8a] A split screen. Left, "very big": a total counter racing upward toward the
"gap > 1¢" marker from episode 2, and a 32-bit badge showing "gap > 1¢ at $131,072".
Right, "very small": a meter labelled "price per request: a few millionths of a dollar"
ticking, with a request counter spinning into the billions. [V3.8b] The two sides meet in the
middle at a single multiplication sign: "tiny price × huge count".

> The seventh situation is size. We saw in the last episode that big totals have coarse gaps, and that thirty-two-bit floats run out of cents at just over a hundred and thirty thousand dollars. Big aggregates, like a year of a large company's transactions, use up more of a double's digits than you might expect.
>
> The opposite end matters too. Plenty of things are priced in fractions of a cent: cloud computing by the second, messages, data transfer, requests to a web service. A price of a few millionths of a dollar, times billions of uses, is a multiplication of a very small inexact number by a very large one, followed by a rounding to cents that someone will see on an invoice.

### 3.9 Recap and challenge · ≈ 1:19

**Visual.** [V3.9a] A risk map: horizontal axis "how often it happens", vertical axis "how
visible the damage is". The seven situations appear as labelled dots: accumulation (often,
invisible), comparisons (often, very visible), conversion to cents (often, visible),
rates (often, visible), order (sometimes, invisible until it isn't), boundaries (very often,
invisible), size (rare, visible). A `RED` hotspot glows where comparisons, conversion and rates
cluster. [V3.9b] The challenge: q03-05's code panel with its output. As the narration names
each kind of risk, nothing is highlighted yet: finding the lines is the viewer's job.
[V3.9c] QR wall: q03-01 to q03-05 for 10 seconds. [V3.9d] Teaser: a statement reading "Balance:
$0.00" next to a status light glowing `RED`, "PAST DUE".

**On screen**

```python
subtotal = 0
for price in order["items"]:
    subtotal += price
tax = round(subtotal * order["tax_rate"], 2)
total = subtotal + tax
cents = int(total * 100)
```

```output
subtotal 30.269999999999996  tax 2.5  total 32.769999999999996
charging 3276 cents
balance due!
```

**QR q03-05** appears at [V3.9b], 10 seconds. Caption: "q03-05 · Challenge: find the risky lines".

> Let's take stock. Floating-point money goes wrong in seven kinds of places. Accumulation, where every step adds a little error. Comparisons and thresholds, where a sliver flips a yes into a no. Converting to cents with int, which chops instead of rounding. Multiplying by rates, where near-halfway answers round on a coin flip. Order of addition, which changes totals from run to run. Boundaries, where money silently becomes a float. And size: huge totals, thirty-two-bit floats, and tiny prices times enormous counts.
>
> Here's a challenge. The code in the corner is a tiny checkout. It reads an order from JSON, adds up three items, adds tax, converts to cents and checks the payment. The items are twenty-nine cents, nine ninety-nine and nineteen ninety-nine, so the subtotal should be thirty dollars and twenty-seven cents, and the total thirty-two seventy-seven. The customer paid exactly that. But the program charges three thousand two hundred and seventy-six cents, and says a balance is due.
>
> Five lines in it can go wrong with money. Find them all. Then fix them, using the hint in the comments, until it charges the right amount and agrees the order is paid.
>
> Next time: what all of this actually costs. Balances that won't close, loops that never end, systems that disagree by a cent, and a few real stories where small numbers caused large trouble.

## Fact check before recording

- 3.1: "about seventeen millionths of a cent": the final error is 1.7 × 10⁻⁷ dollars =
  1.7 × 10⁻⁵ cents (from q03-01's output).
- 3.4: "more than one in twenty": 573 / 10,000 = 5.73 %.
- 3.5: `round(1.005, 2)` returns `1.0` (shown as on-screen text, not from a snippet). Verify with
  `python3 -c "print(round(1.005, 2))"`.
- 3.5: the rate values on the receipt (8.25 %, 15 %, 3.5 % ÷ 365, 0.9187) are illustrative, not
  real rates; keep them generic on screen.
- 3.6: since Python 3.12, built-in `sum()` of floats uses compensated (Neumaier) summation;
  `math.fsum` returns the correctly rounded sum. Both behave the same in Pyodide's 3.14.
- 3.6: databases and distributed engines don't guarantee the order in which an aggregate such as
  `SUM` over a floating-point column is accumulated, so results can vary between runs or plans.
  Keep the claim general; don't name a product without checking its documentation.
- 3.7: Python's `json.loads` returns `float` for numbers with a fraction or exponent unless
  `parse_float` is given; JavaScript's `JSON.parse` produces Numbers (binary64); spreadsheets
  such as Excel store binary64; CSV readers in data-frame libraries (e.g. pandas `read_csv`)
  infer float64 for decimal columns by default.
- 3.8: "a few millionths of a dollar" per request is illustrative, not a quoted vendor price.

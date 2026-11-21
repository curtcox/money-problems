# Episode 4 · What goes wrong

| | |
|---|---|
| Part | The problem |
| Target length | about 15 min (segment estimates; set final timing from the narration audio) |
| Builds on | Episodes 1–3: why cents are approximate, the float line, where errors appear |
| QR codes | q04-01 … q04-05 |

## Learning goals

By the end, the viewer can:

- explain how a loan can print a balance of $0.00 and still not be paid off;
- say why `while balance != 0` is a dangerous loop condition for money;
- describe a reconciliation break, and why two correct-looking systems disagree by a cent;
- explain why truncation moves money in one direction, while rounding to nearest doesn't;
- explain why the same report can give different totals when the order of addition changes;
- retell two real stories in which numbers that couldn't be stored exactly did real damage.

## Script

### 4.1 Cold open · ≈ 0:52

**Visual.** [V4.1a] The receipt motif, restyled as a loan statement: "Loan amount
$1,000.00", then twelve payment lines scrolling past, eleven of $83.33 and one of $83.37.
[V4.1b] Code panel q04-01 on the left; the console prints the last three months. The
final line, `month 12: balance $-0.00`, appears; the minus sign glows `RED`. [V4.1c] A
green stamp "PAID IN FULL" swings down onto the statement and stops in mid-air, held by a
`RED` label: `balance == 0: False`. [V4.1d] The last console line prints the stored value,
`-1.2789769243681803e-13`; the float line zooms in on zero and shows a tick just to its
left, with a gold dot sitting on it.

**On screen**

```python
balance = 1000.00
payments = [83.33] * 11 + [83.37]
for month, payment in enumerate(payments, 1):
    balance -= payment
```

```output
month 10: balance $166.70
month 11: balance $83.37
month 12: balance $-0.00
statement says:    $-0.00
balance == 0:      False
what is stored:    -1.2789769243681803e-13
```

**QR q04-01** appears at [V4.1b], 8 seconds. Caption: "q04-01 · Paid off, or not?".

> Here's a loan of a thousand dollars, paid back in twelve instalments. Eleven payments of eighty-three thirty-three, and a final payment of eighty-three thirty-seven to make it come out even. Add them up on paper and you get exactly one thousand dollars.
>
> Run it, and look at the last statement line. Balance: minus zero dollars and zero cents. <break time="0.5s" /> Minus zero.
>
> Now ask the question the system actually cares about: is the balance zero? <break time="0.4s" /> False.
>
> What's left is about one ten-trillionth of a dollar, below zero. Nobody owes it, and nobody is owed it. It exists only because none of those payments could be stored exactly. But it's enough to keep the "paid in full" stamp from coming down.
>
> In the last episode, we found where these errors appear. In this one, we follow them downstream, and see what they break.

### 4.2 Ghost balances · ≈ 0:43

**Visual.** [V4.2a] A row of account cards, each with a balance. Most show `$0.00` in
`GREEN`. Three show `$-0.00` or `$0.00` with a faint `RED` halo. [V4.2b] A process
labelled "close account" runs down the row: it closes every green card with a satisfying
click, but bounces off the haloed ones with "balance ≠ 0". [V4.2c] The haloed cards get
envelopes: "Your statement: amount due $0.00", "Your statement: amount due $-0.00".
[V4.2d] A zoom into one haloed card reveals its stored balance as a tiny gold speck on the
float line, a few ticks away from zero.

> Call that leftover a ghost balance. It's too small to see, but not too small to matter, because software keeps asking questions about it.
>
> Is the account empty? Can we close it? Is the customer behind on their payments? Should we send a statement? Each of those is a comparison, and each comparison sees the ghost.
>
> So you get accounts that refuse to close. Statements that ask for zero dollars and zero cents. And the strangest one of all, minus zero, which is what you get when a tiny negative number is rounded to two places for display. The rounding throws away the size, but the sign survives.
>
> None of this loses anyone any money. But every one of these cases ends up in front of a person, who has to work out what happened, and then explain it to a customer who's convinced the bank can't count.

### 4.3 The loop that skips zero · ≈ 1:04

**Visual.** [V4.3a] Code panel q04-02. A vertical number line from 1 down to −0.3, with a
gold marker at 1.00. [V4.3b] Each step, the marker drops by a dime and the console prints
the line. From step 3, the printed values sprout trailing digits; the marker drifts a
hair to the right of each tenth mark (exaggerated, with a `YELLOW` bracket labelled "not
to scale"). [V4.3c] At step 10, the marker stops just above zero; a magnifier shows the gap
`1.3877787807814457e-16`. The loop's condition `owed != 0` flashes `GREEN`: "still true".
[V4.3d] Step 11: the marker jumps past zero to the negative side. The `0` mark on the
number line flashes `RED`; the marker keeps falling until the guard `steps < 13` catches
it. [V4.3e] The guard is struck out; the marker falls off the bottom of the screen.

**On screen**

```python
while owed != 0 and steps < 13:
    owed -= 0.10
    steps += 1
```

```output
step  9: owed = 0.10000000000000014
step 10: owed = 1.3877787807814457e-16
step 11: owed = -0.09999999999999987
```

**QR q04-02** appears at [V4.3c], 8 seconds. Caption: "q04-02 · The loop that skips zero".

> Comparisons don't only decide what to print. They decide what to do next.
>
> Here's a loop that says: keep paying ten cents until nothing is owed. We start at one dollar. Ten payments of a dime should bring us to exactly zero, and the loop should stop.
>
> Watch the printed balance. After three payments it reads zero point seven, then fourteen zeros and a one. The error from each dime is piling up. After ten payments, the balance isn't zero. It's about one ten-quadrillionth of a dollar, so "not equal to zero" is still true, and the loop goes around again.
>
> The eleventh payment overshoots, and now we owe minus ten cents. From here the balance only moves away from zero. Without the little guard that stops after thirteen steps, this loop would never end.
>
> In real systems, this pattern hides inside retry loops, payment schedules, and code that "settles up" until the difference is gone. The fix is simple: never ask a float whether it is exactly zero. But it's even better not to use floats for the balance in the first place.

### 4.4 Two systems, one cent apart · ≈ 1:09

**Visual.** [V4.4a] The ledger motif, split into two systems side by side: "System A
(floats)" in `BLUE`, "System B (decimals)" in `GREEN`. Both receive the same price list,
and both apply "5% fee". [V4.4b] Code panel q04-03; the console prints the six rows. The
`<- break` markers glow `RED`; the $1.00 row glows `GREEN`. [V4.4c] For the $0.30 row, a
close-up: thirty cents times five percent is one and a half cents, exactly on the
midpoint between one cent and two. System B's arrow goes up to 2¢. System A's arrow,
starting from a stored value a hair below the midpoint, goes down to 1¢. [V4.4d] The two
ledgers' totals differ by a cent; the balance scale tips. A ticket appears in a queue
labelled "Reconciliation exceptions", then another, then dozens.

**On screen**

```python
a = round(float(price) * float(RATE), 2)          # system A: floats
b = (Decimal(price) * Decimal(RATE)).quantize(     # system B: decimals
    Decimal("0.01"), rounding=ROUND_HALF_UP)
```

```output
$0.30: float 0.01  decimal 0.02  <- break
$0.70: float 0.03  decimal 0.04  <- break
$1.00: float 0.05  decimal 0.05
$2.30: float 0.11  decimal 0.12  <- break
$2.50: float 0.12  decimal 0.13  <- break
$4.10: float 0.20  decimal 0.21  <- break
```

**QR q04-03** appears at [V4.4b], 8 seconds. Caption: "q04-03 · Two systems, one cent apart".

> Money rarely lives in just one system. A payment processor, a billing platform, a general ledger, a bank: each one records the same transaction, and every night, someone checks that they all agree. That check is called reconciliation.
>
> Now imagine two of those systems compute the same five percent fee. System A uses floats and Python's round function. System B uses decimals and rounds halves up, the way you learned in school. Both are reasonable. Both pass their own tests.
>
> Five out of these six prices produce different fees. Thirty cents times five percent is exactly one and a half cents. System B rounds that up, to two. But System A never sees one and a half cents. It sees the nearest double to the result, and for these prices, either that double lands a hair below the midpoint, or it lands exactly on a midpoint and Python's round goes to the even neighbour. Either way, System A says one cent.
>
> Each difference is a single cent. But every one is a reconciliation break, and a break isn't settled by arithmetic. It's settled by a person, who opens a ticket, pulls the records from both systems, finds out why they differ, and decides which one is right. Multiply that by thousands of transactions a day, and the cost of a cent is suddenly measured in salaries.

### 4.5 Totals that don't foot · ≈ 0:56

**Visual.** [V4.5a] The receipt motif: five line items, each with a price and its own
rounded tax. Below, "Subtotal", "Tax", "Total". [V4.5b] A `YELLOW` adding-machine tape runs
down the tax column and prints a sum that is one cent away from the "Tax" line; the
mismatch glows `RED`. [V4.5c] A spreadsheet of a monthly report: columns for each region,
a "Total" column on the right. An accountant's tick-mark animation ("footing") runs down
each column and across each row; one cell refuses to tick. [V4.5d] A stamp: "Doesn't
foot". Then a text card: "Episode 6: where to round is a policy."

> Accountants have a word for checking that a column of numbers adds up to its total: footing. And they have a word for checking that the rows add up to the same grand total as the columns: cross-footing.
>
> Floating point makes reports that don't foot. Each line is rounded for display, but the total is computed from the unrounded values, or rounded in a different place. So the printed lines add up to one number, and the printed total says another, usually by a cent.
>
> To a customer, that's a receipt that doesn't add up. To an auditor, it's a reason to ask questions, because a report that doesn't foot is exactly what errors, and fraud, look like. The honest explanation, "it's floating point", is true, but it's not an answer anyone wants to sign.
>
> Part of this problem is about when and where to round, and we'll give that its own episode. But floats make it worse, because they hand you values that are already slightly off before you've rounded anything at all.

### 4.6 Truncation's one-way street · ≈ 1:13

**Visual.** [V4.6a] A gold cent sliced into hundredths of a cent; a row of 100,000 tiny
account icons, each producing a sliver of interest. [V4.6b] Two funnels: "truncate (round
down)" and "round to nearest". Slivers pass through. In the truncate funnel every sliver
loses its tail, and the tails all fall into a `RED` bin. In the round funnel, tails go
both ways: some slivers lose a little (`RED`), some gain a little (`GREEN`), and the two
bins stay level. [V4.6c] Code panel q04-04 and console. The three totals appear as bars:
"exact" in `GOLD`, "after truncating" visibly shorter, "after rounding" level with exact.
"short by 500.48" glows `RED`; "off by -0.46" glows `GREY`.

**On screen**

```python
for _ in range(100_000):
    balance = Decimal(random.randrange(1, 1_000_000)) / 100
    interest = balance * DAILY
    exact += interest
    truncated += interest.quantize(CENT, rounding=ROUND_DOWN)
    rounded += interest.quantize(CENT, rounding=ROUND_HALF_EVEN)
```

```output
exact interest:    68451.36
after truncating:  67950.88  short by 500.48
after rounding:    68451.82  off by -0.46
```

**QR q04-04** appears at [V4.6c], 8 seconds. Caption: "q04-04 · Truncation's one-way street".

> So far, the errors have been tiny and random. Some amounts are stored a little high, some a little low. Over many transactions, they tend to partly cancel.
>
> But one very common habit breaks that symmetry: truncation. Cutting off everything past the cent instead of rounding it. In episode three we saw the classic version, int of x times one hundred, which drops whatever is left over.
>
> This code computes one day's interest on a hundred thousand accounts, at five percent a year. To keep floating point out of the picture, it's all exact decimal arithmetic. The only difference between the two totals is how each day's interest is cut to cents.
>
> Rounding to nearest ends up within forty-six cents of the exact total. The errors go both ways, and they mostly cancel. Truncating comes up short by five hundred dollars and forty-eight cents. In one day. Every single cut went the same way, and all that money landed on the same side of the ledger.
>
> That's the difference between noise and bias. Noise annoys auditors. Bias moves money, from one party to another, systematically, and that's the kind of error that ends up in court. Hold on to this one, because in episode seven, a famous movie plot is built entirely on it.

### 4.7 The report you can't reproduce · ≈ 0:57

**Visual.** [V4.7a] Three identical stacks of 1,000 transaction cards, ordered three
ways: by time, largest first, smallest first. [V4.7b] Each stack feeds into an adding
machine. The three totals print side by side, from q04-05's output. The digits that
agree are `GREEN`; the differing tails are `RED`. [V4.7c] A server rack splits the cards
across eight workers, each adding its own share, then adds the partial sums; run twice,
the cards land on different workers and two different totals appear. [V4.7d] An auditor
icon holds up two printouts of the "same" report, with different totals.

**On screen**

```output
in time order:   263006.59000000014
largest first:   263006.59
smallest first:  263006.58999999985
```

> Here's an even stranger consequence. In ordinary arithmetic, the order in which you add things doesn't matter. Two plus three plus four is nine, whichever way you go.
>
> With floats, every single addition rounds its result to the nearest double. Change the order, and you change which intermediate results get rounded, and by how much. These are the same thousand transactions, added up three different ways, and they give three different totals.
>
> Why would anyone add things in a different order? Because databases don't promise an order for a sum. Because big systems split the work across many processors and combine the pieces in whatever order they finish. Run the same report twice, and you can get two answers.
>
> Here the difference is tiny, and rounding to cents hides it. But not always: whenever a total sits right next to a half cent, the order of addition decides which way it rounds. And when a regulator asks you to reproduce last quarter's numbers exactly, "it depends on the order the threads finished" is not the answer they're hoping for.

### 4.8 A stock index that sank · ≈ 0:58

**Visual.** [V4.8a] A simple line chart, starting in January 1982 at 1000. It slides
steadily downward month after month, with no drama in the market itself, reaching
"≈ 524.811" by November 1983. [V4.8b] Inset: a single update. The true new value has six
or more decimal places; the last digits beyond the third are sliced off and drop into a
`RED` bin. Counter: "thousands of updates a day". [V4.8c] The recalculated value appears
above: "≈ 1098.892". A vertical `GREEN` arrow jumps from the old line to the new value.
[V4.8d] A caption: "Truncation, not floating point. Same lesson."

> Let's finish with two real stories. They're not both about money, and they're not both about floating point, but they're both about a number that couldn't be stored exactly, and what happened when nobody watched the error grow.
>
> In 1982, the Vancouver Stock Exchange launched a new index, starting at one thousand. It was recalculated with every trade, thousands of times a day, and each time, the new value was cut off at three decimal places. Not rounded. Truncated.
>
> Every recalculation lost a little, always in the same direction. Within two years the index had sunk to about half its starting value, while the market it described had done nothing of the kind. When the error was found, the index was recalculated properly, and it jumped from around five hundred and twenty-five to nearly eleven hundred, overnight.
>
> That's truncation's one-way street again, at a stock exchange. No floating point required: just a value that couldn't be kept exactly, and a cut that always went the same way.

### 4.9 One tenth of a second · ≈ 0:52

**Visual.** [V4.9a] Restrained and quiet: no music sting, plain `GREY` and white. A
binary register of 24 boxes, holding the start of 1/10 in binary,
`0.000110011001100110011…`, with the bits past the last box greyed out and falling away.
[V4.9b] A clock counter ticks in tenths of a second; a tiny error accumulates with each
tick. Beside it: "about 100 hours of operation → about 0.34 seconds". [V4.9c] A plain
text card: "Dhahran, Saudi Arabia · 25 February 1991 · 28 soldiers killed". Hold for
three seconds in silence.

> The second story is not about money, and it's not funny. In 1991, during the Gulf War, a Patriot missile battery at Dhahran, in Saudi Arabia, failed to intercept an incoming Scud missile.
>
> The system counted time in tenths of a second, and stored one tenth in a fixed-point register that held only so many bits. As we saw in episode one, one tenth has no exact binary form, so every tick carried a tiny error. After about a hundred hours of continuous running, the clock had drifted by about a third of a second, enough for the system to look in the wrong place. <break time="0.6s" /> Twenty-eight soldiers were killed.
>
> The cause was the same fact we started this series with: one tenth can't be stored exactly in binary.

### 4.10 Recap and challenge · ≈ 1:03

**Visual.** [V4.10a] A recap column builds: "ghost balances" → "loops that skip zero" →
"reconciliation breaks" → "totals that don't foot" → "bias from truncation" → "reports you
can't reproduce". Each item gets a small icon from its segment. [V4.10b] The challenge:
q04-05's code; the three differing totals from 4.7 reappear and then, as an animated hint,
the amounts change to whole numbers of cents and the three totals collapse into one
`GREEN` number. [V4.10c] QR wall: q04-01 to q04-05 for 10 seconds. [V4.10d] Teaser: the line
`0.1 + 0.2` appears in a column of different fonts and editor colour schemes, each
followed by the same `0.30000000000000004`.

**On screen**

```python
def total(amounts):           # a plain running total, like most code and databases
    t = 0.0
    for a in amounts:
        t += a
    return t
```

**QR q04-05** appears at [V4.10b], 10 seconds. Caption: "q04-05 · Challenge: reconcile these".

> Let's take stock. A tiny error in a balance becomes a ghost that won't let an account close. Ask whether a float is exactly zero, and a loop can step right past it. Two sensible systems, rounding the same amounts, disagree by a cent, and every disagreement costs someone an afternoon. Reports don't foot. Truncation turns noise into bias, and bias moves real money. And a total can depend on nothing more than the order in which you added things up.
>
> Here's the challenge. The code in the corner adds the same thousand transactions in three different orders, and gets three different totals. Change it so that every amount is stored as a whole number of cents, and make all three reports agree, exactly. One small hint: Python's built-in sum function adds floats more carefully than this plain loop does, so for this experiment, keep the loop.
>
> Next time: is this just a Python problem? We'll ask eight languages and a database the same question, and get the same answer from every one of them. And we'll find out why.

## Fact check before recording

- 4.1–4.7: every number comes from the recorded output of q04-01 … q04-05. "About one
  ten-trillionth" is −1.28 × 10⁻¹³; "about one ten-quadrillionth" is 1.39 × 10⁻¹⁶.
- 4.4: explanation of the breaks. $0.30, $0.70, $2.30 and $4.10 × 0.05 give doubles just
  below the half cent; $2.50 × 0.05 = 0.125 exactly, a true tie that `round` sends to
  even (0.12). Confirm with `Decimal(float(p) * 0.05)` for each before recording.
- 4.7 and 4.10: since Python 3.12, `sum()` of floats uses compensated (Neumaier) summation
  and gives 263006.59 for all three orders; the snippet uses a plain loop for that
  reason. Check the "What's New in Python 3.12" entry for `sum()`.
- 4.8 Vancouver Stock Exchange index: launched January 1982 at 1000.000; recalculated
  about 3,000 times a day and truncated to three decimals; about 524.811 by November
  1983; recalculation gave about 1098.892. Check against the commonly cited Wall Street
  Journal (8 November 1983) and Toronto Star reports, or McCullough and Vinod (1999).
  Some sources give "about 520 after 22 months"; the narration says "about half" and
  "around five hundred and twenty-five" to stay within both.
- 4.9 Patriot missile, Dhahran, 25 February 1991: time counted in tenths of a second in a
  24-bit fixed-point register; about 100 hours of operation; drift about 0.34 seconds;
  28 US Army soldiers killed. Source: US GAO report GAO/IMTEC-92-26 (1992). Keep the
  tone factual and brief; no dramatic music or imagery.

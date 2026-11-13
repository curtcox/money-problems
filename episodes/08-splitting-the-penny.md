# Episode 8 · Splitting the penny

| | |
|---|---|
| Part | Living with it |
| Target length | about 14 min (segment estimates; set final timing from the narration audio) |
| Builds on | Episodes 1 and 6: amounts in whole cents, rounding as a choice |
| QR codes | q08-01 … q08-05 |

## Learning goals

By the end, the viewer can:

- explain why dividing an amount and rounding each share can lose or invent a cent;
- state the rule every split must obey: the parts add up exactly to the whole;
- split whole cents in proportion to any weights with the largest remainder method;
- spread a discount over receipt lines, and schedule installments, without a stray cent;
- recognise that deciding who gets the extra cent is a policy, and that even a sensible
  policy can produce paradoxes.

## Script

### 8.1 Cold open · ≈ 1:20

**Visual.** [V8.1a] Black canvas. A gold "$100.00" bill sits in the centre. Three
plain figures (simple circles with name tags "A", "B", "C", no faces) stand below it.
[V8.1b] The bill splits into three gold stacks labelled "$33.33" that slide to the
figures. [V8.1c] A gold penny remains where the bill was, spinning slowly, alone, with a
`RED` question mark above it. [V8.1d] Code panel q08-01 on the left; the console types out
the first four lines. `33.333333333333336` appears with its tail in `RED`; "three shares
= 99.99" and "missing = 0.01" glow `RED`. [V8.1e] The last line prints in `GREEN`: "in
cents: 3333 each, and 1 cent left over". The penny stops spinning and gets a `YELLOW`
label: "someone has to take it".

**On screen**

```python
bill = 100.00
share = bill / 3
print("bill / 3       =", share)
each = round(share, 2)
```

```output
bill / 3       = 33.333333333333336
each pays      = 33.33
three shares   = 99.99
missing        = 0.01
in cents: 3333 each, and 1 cent left over
```

**QR q08-01** appears at [V8.1d], 8 seconds. Caption: "q08-01 · A hundred dollars, three ways".

> Three friends share a one hundred dollar bill. Easy: everyone pays a third.
>
> Ask Python for a third of a hundred, and it gives you thirty-three point three, a long run of threes, and then a six at the end, because a third can't be stored exactly. So round it to cents: thirty-three dollars and thirty-three cents each.
>
> Now add the three shares back up. Ninety-nine ninety-nine. <break time="0.5s" /> A cent is missing. Nobody stole it, and no float error lost it. Even with perfect arithmetic, a hundred dollars does not divide into three equal amounts of whole cents. Count in cents and the problem is plain: three thousand three hundred and thirty-three cents each, and one cent left over.
>
> That last cent has to go somewhere. Someone pays thirty-three thirty-four. And the question of who, and how you decide, turns out to be one of the most interesting little problems in handling money.

### 8.2 The conservation law · ≈ 1:20

**Visual.** [V8.2a] The ledger motif: a T-account titled "Dinner", a "$100.00" credit on
one side. On the other side, three debits "$33.33" stack up; the balance scale above
tips and the gap, "$0.01", glows `RED`. [V8.2b] A fourth line, "$0.01 rounding", is added
by hand; the scale levels and turns `GREEN`. [V8.2c] The rule writes itself in large type:
"The parts must add up to the whole. Exactly." [V8.2d] Three small examples flash past,
each a whole splitting into parts: a payroll total into paychecks, a restaurant bill into
card payments, a tax total into receipt lines.

> Before we fix it, let's be clear about what we want. There's one rule that every split of money has to obey. The parts must add up to the whole. Exactly. Not to within a cent, and not on average.
>
> Think of it as a conservation law. A hundred dollars came in, so a hundred dollars must go out, split however you like. If the parts come to ninety-nine ninety-nine, a cent has vanished from the books. If they come to a hundred dollars and one cent, a cent has appeared from nowhere, and someone has been charged for it.
>
> Accountants have a name for books that obey the rule: they balance. And once a cent goes missing, somebody, eventually, will spend an afternoon looking for it.
>
> Notice that rounding each share separately can't promise this. Each share is rounded with no idea what happened to the others, so the little rounding errors are free to pile up in any direction. To keep the books balanced, the shares have to be decided together.

### 8.3 Largest remainder · ≈ 2:00

**Visual.** [V8.3a] Code panel q08-02 showing `allocate`. [V8.3b] Three bars, one per
person, each with the exact share drawn as a `YELLOW` outline: 3333 and one third cents.
The integer part of each bar fills `GOLD` (3333); the fractional thirds remain as thin
`YELLOW` slivers labelled "remainder". [V8.3c] The leftover pool, "1¢", appears as a
single penny. The slivers line up in a row sorted by size; ties are broken by position,
shown as small labels "1st", "2nd", "3rd". The penny drops onto the first bar, which
becomes 3334. [V8.3d] The console prints the first output line; "sum $100.00" glows
`GREEN`.

**On screen**

```python
def allocate(total, weights):
    whole = sum(weights)
    shares, remainders = [], []
    for i, w in enumerate(weights):
        share, rem = divmod(total * w, whole)   # floor of each exact share
        shares.append(share)
        remainders.append((-rem, i))            # biggest remainder first, then position
    left_over = total - sum(shares)
    for _, i in sorted(remainders)[:left_over]:
        shares[i] += 1                          # one extra cent each
    return shares
```

```output
$100.00 [1, 1, 1] -> ['$33.34', '$33.33', '$33.33'] sum $100.00
```

**QR q08-02** appears at [V8.3a], 8 seconds. Caption: "q08-02 · Largest remainder".

> Here's a method that always works. It's called largest remainder, and it fits in a dozen lines.
>
> First, work in whole cents, and describe the split with weights. An even three-way split is weights one, one, one.
>
> For each person, work out their exact share, and keep only the whole cents. Divmod does that in one step: it divides and gives you both the whole part and the remainder, with no floats anywhere. Ten thousand cents times one, divided by three, is three thousand three hundred and thirty-three, remainder one.
>
> Rounding everything down can only ever leave cents over, never take too many. So add up the whole parts, and see how many cents are left. Here, one.
>
> Now hand out the leftover cents, one each, to the people whose remainders were biggest: the ones who were rounded down the furthest. If remainders tie, as they do here, break the tie by position, so the answer is the same every time you run it.
>
> And the result: thirty-three thirty-four, thirty-three thirty-three, thirty-three thirty-three. Sum: exactly one hundred dollars. It can't come out any other way, because we handed out precisely the cents that were left over, and no more.

### 8.4 Weights and percentages · ≈ 1:20

**Visual.** [V8.4a] The bars from 8.3 morph into bars of lengths 1 : 2 : 3, labelled
"shares held". The total above reads "$1,000.00". [V8.4b] The second output line prints;
the three amounts land on the bars. The 1/6 bar shows a remainder sliver of four sixths,
the others smaller; one penny drops on the first bar. [V8.4c] The bars relabel as "33.3 %",
"33.3 %", "33.4 %" with weights 333, 333, 334, and a "$10.00" total; the third output line
prints. [V8.4d] Every "sum" in the console glows `GREEN` in turn.

**On screen**

```output
$1,000.00 [1, 2, 3] -> ['$166.67', '$333.33', '$500.00'] sum $1,000.00
$10.00 [333, 333, 334] -> ['$3.33', '$3.33', '$3.34'] sum $10.00
```

> Even splits are just the start. The same dozen lines handle any proportions.
>
> Suppose three partners own a business in the ratio one to two to three, and they share a thousand dollars of profit. Their exact shares are a sixth, two sixths and three sixths. Largest remainder gives one hundred sixty-six sixty-seven, three hundred thirty-three thirty-three, and exactly five hundred. Sum: a thousand dollars.
>
> Percentages work too. Write thirty-three point three percent, thirty-three point three, and thirty-three point four as the whole-number weights three hundred and thirty-three, three hundred and thirty-three and three hundred and thirty-four. Split ten dollars, and the shares are three thirty-three, three thirty-three and three thirty-four.
>
> The weights never need to be money, and they never need to be floats. Shares, hours worked, square metres of office space, or the prices on a receipt. Anything you can count.

### 8.5 Spreading a discount · ≈ 1:50

**Visual.** [V8.5a] The receipt motif: three lines, "Book $19.99", "Mug $5.00", "Lamp
$12.50", subtotal "$37.49". A gold coupon "−$5.00" slides onto the bottom. [V8.5b] Code
panel q08-03. The naive line prints; three discount tags 2.67, 0.67 and 1.67 attach to the
lines, and their sum "5.01" glows `RED`: one cent more than the coupon. [V8.5c] The
largest remainder line prints; the tags change to 2.66, 0.67, 1.67, and the sum glows
`GREEN`. The book's tag flicks from 2.67 down to 2.66 with a small `YELLOW` highlight.
[V8.5d] The three discounted lines print, then the receipt total. [V8.5e] Later: the Mug
is returned. Its line lifts off the receipt with "refund $4.33" attached, not "$5.00".

**On screen**

```python
prices = [1999, 500, 1250]          # $19.99, $5.00, $12.50, in cents
coupon = 500                        # $5.00
naive = [round(coupon / 100 * p / sum(prices), 2) for p in prices]
shares = allocate(coupon, prices)
```

```output
rounded each line: [2.67, 0.67, 1.67] sum 5.01
largest remainder: [266, 67, 167] sum 500
  line  1999 - 266 =  1733
  line   500 -  67 =   433
  line  1250 - 167 =  1083
receipt total: 3249 = 3749 - 500
```

**QR q08-03** appears at [V8.5b], 8 seconds. Caption: "q08-03 · Spreading a discount".

> Here's a split you might not recognise as one. A customer buys a book, a mug and a lamp, and uses a five dollar coupon. The total is easy: subtract five dollars. But many systems also need the discount on every line of the receipt, for tax, for accounting, and for returns.
>
> The tempting approach is to give each line its share of the five dollars, in proportion to its price, and round each one. Two sixty-seven, sixty-seven cents and a dollar sixty-seven. Add them up: five dollars and one cent. The lines now claim a bigger discount than the coupon gave.
>
> Largest remainder, with the prices as the weights, gives two sixty-six, sixty-seven and a dollar sixty-seven. Exactly five dollars. Look at the book. Rounded on its own, its share would be two sixty-seven. But its remainder was the smallest of the three, so when the leftover cents were handed out, it went without. Every line is within a cent of its exact share, and the lines add up.
>
> And this pays off later. If the customer returns the mug, you refund what they actually paid for it: five dollars minus its sixty-seven cent share of the coupon, four thirty-three. Not five dollars, which would hand back money they never paid. The split you store today is the refund you owe tomorrow, so store it.

### 8.6 Twelve payments · ≈ 1:30

**Visual.** [V8.6a] A calendar strip of twelve months. Above it, "$1,000.00 a year".
[V8.6b] Code panel q08-04; the float line prints, twelve gold "83.33" tags fall onto the
months, and "999.96" glows `RED`, with four pennies missing from a jar. [V8.6c] "each
8333 with 4 cents left over". Two alternative calendars build: in the first, the four
leftover pennies all drop onto December, which becomes 8337; in the second, one penny each
lands on January through April, which become 8334. [V8.6d] Both "sum 100000" lines glow
`GREEN`.

**On screen**

```python
each, extra = divmod(annual, 12)
last_pays = [each] * 11 + [each + extra]
first_pay = [each + 1] * extra + [each] * (12 - extra)
```

```output
float: 12 x 83.33 = 999.96
each 8333 with 4 cents left over
last month pays   [8333, 8333, 8333, 8333, 8333] ... [8333, 8337] sum 100000
first months pay  [8334, 8334, 8334, 8334, 8333] ... [8333, 8333] sum 100000
```

**QR q08-04** appears at [V8.6b], 8 seconds. Caption: "q08-04 · Twelve payments".

> Splits happen over time, too. An annual subscription of a thousand dollars, paid monthly. A loan, a rent, an insurance premium.
>
> Divide by twelve and round, and every payment is eighty-three thirty-three. Twelve of those come to nine hundred ninety-nine dollars and ninety-six cents. Four cents short, every year, for every customer.
>
> In whole cents, the division is honest about it: eight thousand three hundred and thirty-three cents a month, with four cents left over. And now there's a choice to make. You could put all four cents on the final payment: eleven months at eighty-three thirty-three, and one at eighty-three thirty-seven. Or you could spread them out, one extra cent on each of the first four months.
>
> Both add up to exactly a thousand dollars. Neither is wrong. Charging the extra early means you collect it sooner; charging it last means a customer who cancels early never pays it. Which one you choose is a business decision, and possibly a contractual one. What matters is that you make it on purpose, write it down, and apply it the same way every time.

### 8.7 Who gets the extra cent? · ≈ 1:20

**Visual.** [V8.7a] Three figures from 8.1 return. Over twelve months, a calendar
shows the leftover penny from each month's three-way split landing on figure A every
time; A's pile grows to twelve pennies, `RED`. [V8.7b] Rewind; now the penny rotates A, B,
C, A, B, C …; each pile ends with four pennies, `GREEN`. [V8.7c] Three labels appear over
the scene: "deterministic", "documented", "fair over time".

> Look at what our tie-break rule does over time. Split a monthly bill three ways, every month, and the leftover cent goes to the first person, every month. One cent a month is nothing. But if the first person is always the same customer, the same supplier, or the same department, a policy that looked neutral is quietly one-sided.
>
> There's no universally right answer, but there are good properties to aim for. The split should be deterministic: run it twice and get the same answer, so that it can be checked. It should be documented, so the person who asks why they paid a cent more can be told. And if the same parties are split again and again, it can be fair over time, for instance by rotating who takes the extra cent.
>
> All of these are choices about who gets a penny. Which should make you a little suspicious. Can a reasonable rule for handing out pennies ever behave unreasonably? <break time="0.5s" /> It can.

### 8.8 The Alabama paradox · ≈ 1:40

**Visual.** [V8.8a] Code panel q08-05 with `WEIGHTS = [1, 3, 3]`. Three bars of weights
1, 3, 3. [V8.8b] The console prints line by line, and pennies drop onto the bars to match:
1¢, 2¢, 3¢. At 3¢ each bar holds one penny. [V8.8c] At 4¢ the first bar's penny lifts off
and moves to another bar as one new penny arrives: [0, 2, 2]. The first bar flashes
`RED`; the annotation "<- someone got less from a bigger pot" types out. [V8.8d] For 3¢
and 4¢, the exact shares and remainders appear beside the bars: 3¢ gives 3/7, 9/7, 9/7
(remainders 3/7, 2/7, 2/7); 4¢ gives 4/7, 12/7, 12/7 (remainders 4/7, 5/7, 5/7). The
largest remainders are highlighted in `YELLOW`. [V8.8e] A simple map silhouette of the
state of Alabama (plain outline, no flag or seal), with "1880 census" and "299 seats → 8,
300 seats → 7".

**On screen**

```python
WEIGHTS = [1, 3, 3]
for total in range(1, 9):
    shares = allocate(total, WEIGHTS)
```

```output
3¢ -> [1, 1, 1]
4¢ -> [0, 2, 2]  <- someone got less from a bigger pot
5¢ -> [1, 2, 2]
```

**QR q08-05** appears at [V8.8b], 8 seconds. Caption: "q08-05 · Challenge: the Alabama paradox".

> Take three people with weights one, three and three, and split a small pot with largest remainder. Here are the results for one cent, two cents, three cents, and so on.
>
> At three cents, everyone gets one. Now add a cent to the pot. Four cents, and the first person gets <break time="0.4s" /> nothing. The pot grew, and their share shrank.
>
> Here's why. With three cents, the first person's exact share is three sevenths, all of it remainder, and that's the biggest remainder of the three, so they get a cent. With four cents, their exact share grows to four sevenths. But the other two have grown faster: from nine sevenths to twelve sevenths, which leaves each of them a remainder of five sevenths. Now the first person's remainder is the smallest. The leftover cents go elsewhere, and they drop to zero.
>
> This has a famous name. Largest remainder is the method Alexander Hamilton proposed for sharing out seats in the United States House of Representatives among the states. After the 1880 census, clerks working out the numbers found that if the House grew from two hundred and ninety-nine seats to three hundred, Alabama would lose a seat, falling from eight to seven. It became known as the Alabama paradox, and it's one reason the House eventually moved to a different method.
>
> For money, the paradox is usually harmless. But it's a good reminder that every allocation method is a policy with consequences, and some of them are surprising.

### 8.9 Recap and challenge · ≈ 1:20

**Visual.** [V8.9a] A recap column builds: "Rounding each share can lose or invent a cent"
→ "Parts must add up to the whole, exactly" → "Floor every share, give leftovers to the
largest remainders" → "Ties broken the same way every time" → "Who gets the extra cent is
policy". [V8.9b] The q08-05 code returns with its two challenge comments highlighted.
[V8.9c] QR wall: q08-01 to q08-05 for 10 seconds. [V8.9d] Teaser: a checklist card with
seven empty boxes; the first box ticks itself, labelled "count, don't measure".

**QR q08-05** appears at [V8.9b], 10 seconds. Caption: "q08-05 · Challenge: the Alabama paradox".

> Let's take stock. Dividing money and rounding each part independently can lose a cent or invent one, even with perfect arithmetic. The rule is that the parts add up to the whole, exactly. Largest remainder guarantees that: work in whole cents, floor every share, then hand the leftover cents to the largest remainders, breaking ties the same way every time. It works for even splits, weights, percentages, discounts across a receipt, and payments over time. And who gets the extra cent is a policy decision, which can be unfair over time, or even paradoxical.
>
> Here's a challenge, in two parts. The code in the corner shows the Alabama paradox with weights one, three, three. Find other weights where a bigger pot gives someone less. Then, for a bonus, write a split that rotates who gets the extra cent from one month to the next, and check that over a year everyone pays the same.
>
> Next time, we put everything together. Seven rules for handling money correctly, a tiny money type that enforces them, and a checklist you can take to your next code review.

## Fact check before recording

- 8.8: Hamilton's method is the largest remainder method; Alexander Hamilton proposed it
  for apportioning the House after the 1790 census (Washington vetoed the 1792
  apportionment bill, his first veto; the narration doesn't mention the veto). Confirm
  with a history of US apportionment (for example the US Census Bureau's apportionment
  history pages).
- 8.8: the Alabama paradox: after the 1880 census, the Census Office's chief clerk (C. W.
  Seaton) computed apportionments for House sizes from 275 to 350 and found that Alabama
  would get 8 seats with 299 and 7 with 300. "One reason the House eventually moved to a
  different method": the method was used (as the Vinton method) in the later 1800s and
  replaced in the early 1900s; check the wording against the same source.
- 8.6: whether charging leftover cents first or last is a "contractual" question is
  phrased as a possibility; no specific law is claimed.
- 8.5: the refund amount for a returned item follows the stored line discount; actual
  refund policies vary by business. Phrased as advice.
- All other numbers come from the q08 snippet output. q08-02 and q08-05's tie-break
  ("first by position") is what the code does, not a standard.

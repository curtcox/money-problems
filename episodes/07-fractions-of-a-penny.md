# Episode 7 · Fractions of a penny: what Office Space got right and wrong

| | |
|---|---|
| Part | Living with it |
| Target length | about 15 min (segment estimates; set final timing from the narration audio) |
| Builds on | Episode 6: truncation, round half up, where to round; episode 1: stored doubles |
| QR codes | q07-01 … q07-05 |

Commentary and criticism only: no film clips, stills, posters, logos, character
likenesses or music. Every visual below is our own diagram. See series-bible.md,
"Office Space".

## Learning goals

By the end, the viewer can:

- explain where fractions of a cent come from in real financial calculations;
- explain why skimming the remainders only accumulates under truncation, not round-to-nearest;
- describe how double-entry bookkeeping and reconciliation would expose a skimming account;
- recognise a unit or scale bug (dollars vs cents) as the most realistic part of the plot;
- show how floating point would make a remainder-skimming program take nearly whole cents.

## Script

### 7.1 Cold open · ≈ 1:10

**Visual.** [V7.1a] Black canvas. Title card in plain type: "Office Space (1999)".
No imagery from the film. [V7.1b] Three simple grey desk icons in a row, each with a
monitor. A thin gold stream of tiny penny slivers starts flowing from a large vault icon
labelled "transactions" toward a small jar labelled "our account". [V7.1c] A small caption
pops up beside the stream: "see: Superman III". [V7.1d] The stream suddenly thickens into a
torrent; the jar overflows. A `RED` decimal point bounces across the screen and lands in
the wrong place on a price tag.

> In 1999, Mike Judge's comedy Office Space gave a generation of programmers its favourite heist. Three fed-up employees at a software company called Initech decide to get even. Their plan is to slip a virus into the company's accounting system. Whenever a transaction leaves a fraction of a cent behind, the virus moves that fraction into an account they control. Nobody will miss it, they reason, because each slice is less than a penny. But there are millions of transactions, so the slices should add up.
>
> The characters even point out where they got the idea: Superman the Third did it first.
>
> And then, because it's a comedy, it goes wrong. The programmer who wrote the virus misplaces a decimal point, and after just a few days the account holds far too much money to explain.
>
> It's a great film, and it doesn't owe anyone a code review. But it's a story about rounding, money and a bug, which makes it the perfect case study for this series. So let's give it one anyway. What did Office Space get right, and what did it get wrong?

### 7.2 Where fractions of a penny come from · ≈ 1:40

**Visual.** [V7.2a] A bank passbook page with a balance of "$1,234.56" and a label "3.5 %
a year". [V7.2b] The balance is multiplied by 0.035 and divided by 365 on screen; the
result unrolls as a long `YELLOW` decimal: "0.11838247…". [V7.2c] A cent ruler (tick
marks every cent) appears under the result. The amount snaps down to 0.11 (`GREEN`, "pay")
and the leftover sliver, "0.8382¢", is cut off and lifted up in `GOLD`. [V7.2d] Code panel
q07-01; the console prints all four lines. The leftover column glows. The fourth row,
$10.01, pays nothing at all; its whole interest is a sliver.

**On screen**

```python
daily_rate = Decimal("0.035") / 365
for balance in ["1234.56", "250.00", "98765.43", "10.01"]:
    interest = Decimal(balance) * daily_rate
    whole_cents = interest.quantize(Decimal("0.01"), ROUND_DOWN)
    left_over = (interest - whole_cents) * 100
```

```output
$ 1234.56: interest 0.11838247  pay 0.11  left 0.8382¢
$  250.00: interest 0.02397260  pay 0.02  left 0.3973¢
$98765.43: interest 9.47065767  pay 9.47  left 0.0658¢
$   10.01: interest 0.00095986  pay 0.00  left 0.0960¢
```

**QR q07-01** appears at [V7.2d], 8 seconds. Caption: "q07-01 · Where fractions of a penny come from".

> First, the premise. Do fractions of a penny really exist? Absolutely, and floating point has nothing to do with it.
>
> Here's an example of our own; the film doesn't say which transactions it means. Take a savings account paying three and a half percent a year, with interest worked out daily. A balance of twelve hundred and thirty-four dollars, fifty-six cents earns three and a half percent, divided by three hundred and sixty-five, every day. That's about eleven point eight cents.
>
> But you can only pay whole cents. So the bank has to round, and whatever it does, there's a sliver left over. Here, if it pays eleven cents, the sliver is about eight tenths of a cent.
>
> This code uses Python's decimal type, so there's no binary error anywhere. Every balance leaves a fraction of a cent behind. And a balance of ten dollars and one cent earns less than a tenth of a cent a day. Its interest is nothing but sliver.
>
> So the film's premise is sound. Percentages, interest, currency conversion, fees, taxes: real financial arithmetic produces fractions of a cent all the time. As episode six showed, someone has to decide what happens to them.

### 7.3 The scheme as code · ≈ 1:30

**Visual.** [V7.3a] Code panel q07-02, highlighting the loop. [V7.3b] A conveyor belt of
account cards, each with a balance; at a cutting station labelled "truncate", each card's
interest is split: the whole cents slide right into a large `GREEN` bin "paid to people",
and the sliver drops into a small `GOLD` jar "hidden account". [V7.3c] The belt speeds up
until it's a blur; the counter reaches 100,000. [V7.3d] The console prints the four output
lines; "500.88" and "0.501 cents" are highlighted.

**On screen**

```python
for _ in range(N):
    balance = Decimal(random.randint(1, 5_000_000)) / 100   # $0.01 to $50,000
    interest = balance * daily_rate
    paid = interest.quantize(cent, ROUND_DOWN)             # truncate
    customers += paid
    hidden += interest - paid                              # the slice
```

```output
accounts:        100000
paid to people:  238869.60
hidden account:  500.88
average slice:   0.501 cents
```

**QR q07-02** appears at [V7.3d], 8 seconds. Caption: "q07-02 · The virus, in a few lines".

> The film never shows the virus's code, so here's our own version. It's only a few lines long.
>
> For a hundred thousand accounts with random balances up to fifty thousand dollars, work out a day's interest. Truncate it to the cent, which means always rounding down. Pay the customer that much. And put the slice, whatever was chopped off, into a hidden account.
>
> After one day, the customers have been paid about two hundred and thirty-nine thousand dollars between them. And the hidden account holds five hundred dollars and eighty-eight cents. The average slice is almost exactly half a cent.
>
> That makes sense. If the leftover fractions are spread evenly between nothing and a whole cent, their average is half a cent. Every account contributes about half a cent, every single day.

### 7.4 Right: tiny times enormous · ≈ 1:20

**Visual.** [V7.4a] A single gold sliver labelled "½¢". [V7.4b] It multiplies into a
grid that zooms out: 100,000 slivers become "$500 a day"; ten million become "about $50,000
a day". [V7.4c] A calendar flips: a week, a month, a year. [V7.4d] The jar from the cold open
returns; a label reads "the film: over $300,000 in a few days". A quick estimate line:
"$300,000 ÷ ½¢ ≈ 60 million slices".

> Here's the first thing the film gets right. Tiny amounts times enormous volume is real money.
>
> Half a cent from a hundred thousand accounts is about five hundred dollars a day. A bank with ten million accounts would be leaking about fifty thousand dollars a day, every day, and every individual customer would be short by less than a penny. No one would ever check their statement and notice.
>
> In the film, the account holds over three hundred thousand dollars after a few days. At half a cent a slice, that's around sixty million slices. That's a lot for a few days, which is exactly the point of the joke: the plan was supposed to be slow and invisible, and instead it's fast and enormous.
>
> So the arithmetic of the scheme holds up. Where it gets shakier is the assumption underneath it: that there's always a slice to take.

### 7.5 Wrong: round to nearest, and the slices cancel · ≈ 1:40

**Visual.** [V7.5a] The cent ruler again. Under truncation, every amount's arrow points
left, down to the cent below; the slivers all fall into the jar. [V7.5b] Switch to "half-up":
amounts in the lower half of each cent still go left and drop a sliver in the jar, but
amounts in the upper half now go right; to reach the cent above, the bank has to add a
sliver from the jar. Gold slivers flow both in and out. [V7.5c] Code panel q07-03; the
console prints both rows. Truncate: "keeps 500.88, gives 0.00, net 500.88" in `RED`. Half-up:
"keeps 125.18, gives 124.59, net 0.59" in `GREEN`. [V7.5d] The jar for half-up is nearly
empty; a tiny "0.59" rattles at the bottom.

**On screen**

```python
for name, mode in [("truncate", ROUND_DOWN), ("half-up", ROUND_HALF_UP)]:
    slices = [i - i.quantize(cent, mode) for i in interest]
    kept = sum((s for s in slices if s > 0), Decimal(0))
    given = -sum((s for s in slices if s < 0), Decimal(0))
```

```output
truncate  bank keeps  500.88  bank gives    0.00  net  500.88
half-up   bank keeps  125.18  bank gives  124.59  net    0.59
```

**QR q07-03** appears at [V7.5c], 8 seconds. Caption: "q07-03 · Round, don't truncate".

> Our virus only works because it truncates. Every interest payment is rounded down, so every slice is positive, and they all pile up on one side.
>
> But many financial systems don't truncate. They round to the nearest cent. And then something different happens. An amount like eleven point eight cents rounds up to twelve. The customer gets slightly more than the exact figure, and the slice is negative: the bank gives away a fraction of a cent.
>
> Run the same hundred thousand accounts with round half up. The amounts that round down leave about a hundred and twenty-five dollars in slices. The amounts that round up need about a hundred and twenty-four dollars and sixty cents of slices given back. Net: fifty-nine cents. For a hundred thousand accounts. That's essentially noise.
>
> So under round to nearest, there's no pile of free fractions waiting to be collected. A virus that collects only the positive slices isn't taking money that would otherwise vanish. It's taking money the books expect to balance against the negative ones. Which brings us to the second problem.

### 7.6 Wrong: fractions don't vanish · ≈ 1:40

**Visual.** [V7.6a] The ledger motif: a T-account with three rows, "interest expense",
"customers", "acct 1999". The balance scale sits above. [V7.6b] For one account, the full
interest is drawn out of "interest expense" as a gold bar; the bar splits, the whole cents
go to "customers" and the sliver to "acct 1999". The scale stays level. [V7.6c] The console
prints the q07-05 ledger; "books balance: True" in `GREEN`. [V7.6d] A magnifier moves down
the customer list, recomputing each account's interest the bank's own way; mismatched
accounts flash `RED`, one cent at a time. An arrow from every red flash points at
"acct 1999", whose balance glows `RED`.

**On screen**

```output
interest expense  -2461.0032041096
customers                2455.92
acct 1999           5.0832041096
books balance: True
```

> The film's premise is that fractions of a penny are a kind of dust. Too small to belong to anyone, so they might as well belong to you.
>
> Real accounting doesn't work that way. Banks and businesses keep their books by double entry: every amount that leaves one account must arrive in another, and the two sides must always add up to the same total. If the bank pays out interest, the full amount it owes is recorded as an expense, and every last fraction of it has to land somewhere.
>
> Here's what that looks like with a skimming account on a thousand customers. The interest expense is the full amount owed. The customers got the truncated amounts, and an account called nineteen ninety-nine got the rest. Add it all up, and the books balance perfectly.
>
> So balancing alone doesn't catch the virus. But it does force the slices to go to a real, named account, one that grows every single day for no business reason. And it means anyone can audit the arithmetic. Recompute each customer's interest the bank's way, compare it with what they were actually paid, and the shortfalls appear, a cent here, a cent there, all of them pointing at the same place.
>
> That's reconciliation: two independent calculations of the same thing, compared. It's dull, it runs every day, and it is exactly the kind of mundane detail that catches schemes like this.

### 7.7 Right: the decimal point mistake · ≈ 1:30

**Visual.** [V7.7a] Code panel q07-04, top half. The `skim` function, with two calls below
it: `skim(Decimal("0.01"))` labelled "meant" and `skim(Decimal("1"))` labelled "oops".
[V7.7b] The cent ruler zooms out to a dollar ruler; the cut moves from the cent tick to the
dollar tick, and the sliver being cut off grows from a hair to most of the bar. [V7.7c] The
console prints the first output line; "96 times as much" pulses `RED`. [V7.7d] A small
gallery of the same bug in the wild, as generic labels: "price in cents, read as dollars",
"amount in dollars, sent as cents", "yen treated as having cents".

**On screen**

```python
def skim(unit):
    return sum(i - i.quantize(unit, ROUND_DOWN) for i in interest)
meant = skim(Decimal("0.01"))      # keep fractions of a cent
oops = skim(Decimal("1"))          # keep fractions of a dollar
```

```output
meant: 50.01  oops: 4823.71  (96 times as much)
```

**QR q07-04** appears at [V7.7c], 8 seconds. Caption: "q07-04 · The decimal point mistake".

> Now for the part of the film that's more realistic than it has any right to be: the decimal point.
>
> The film doesn't explain exactly what went wrong, so here's one way it could happen. Our skimming function takes a unit, and keeps whatever is left below it. Meant to be a cent. Now change one constant: a one instead of zero point zero one. The function now keeps fractions of a dollar instead of fractions of a cent.
>
> On ten thousand accounts, the skim that was meant to collect fifty dollars collects four thousand eight hundred and twenty-three. Ninety-six times as much, from a single misplaced decimal point.
>
> And this is the most realistic part of the whole movie. Mixing up units, especially dollars and cents, is one of the most common money bugs there is. One system stores prices as whole cents, another reads them as dollars, and everything is suddenly a hundred times too big or too small. As we'll see in episode ten, it's the classic way that the standard fix, storing whole cents, goes wrong.

### 7.8 Where floats come in · ≈ 1:30

**Visual.** [V7.8a] Code panel q07-04, bottom loop. A price tag "$4.35" goes into a box
"× 100"; out comes a `BLUE` "434.99999999999994". [V7.8b] The cent ruler zoomed between 434
and 435: the value sits a hair left of 435. The "whole cents" cut falls at 434, and the
sliver handed to the jar is almost an entire cent: "0.999999999999943¢" in `RED`. [V7.8c]
The other two lines print: $1.15 and $0.29, each with a near-whole-cent slice. [V7.8d] A
side-by-side: "exact: slice 0¢" (`GREEN`) versus "float: slice ≈ 1¢" (`RED`).

**On screen**

```python
for dollars in [4.35, 1.15, 0.29]:
    cents = dollars * 100
    print(f"${dollars} is {cents!r} cents; float slice {cents - int(cents):.15f}¢")
```

```output
$4.35 is 434.99999999999994 cents; float slice 0.999999999999943¢
$1.15 is 114.99999999999999 cents; float slice 0.999999999999986¢
$0.29 is 28.999999999999996 cents; float slice 0.999999999999996¢
```

> So far, everything in this episode has used exact decimals. The film's scheme is about rounding, and nothing in it needs floating point. But this is a series about floats, so let's ask a question the film never does. What if the virus had used them?
>
> Take an amount of four dollars and thirty-five cents. It's a whole number of cents, so there's no fraction to skim. The slice should be zero. But in floating point, four point three five times one hundred is four hundred and thirty-four point nine nine nine, and so on. The whole-cents part is four hundred and thirty-four, and the slice handed to the virus is almost an entire cent.
>
> A dollar fifteen does the same. So does twenty-nine cents. Amounts that have no fraction at all suddenly appear to have nearly a whole cent of fraction, and a float-based virus would happily take it.
>
> That's not in the film; it's our addition. But it's the same int of x times one hundred mistake from episode three, and it has a sobering consequence. A program like this doesn't even need bad intentions. Any system that converts float dollars to cents by truncating is quietly moving whole cents, in one direction, on a few percent of its amounts.

### 7.9 Real salami slicing · ≈ 1:00

**Visual.** [V7.9a] A salami on a cutting board, sliced into paper-thin rounds, each
labelled "¢". [V7.9b] A stack of index cards labelled "penny-shaving stories", most of them
stamped "source?" in `GREY`. [V7.9c] A checklist builds: "rounding rule written down",
"reconciliation daily", "no unexplained accounts", "two people to change money code".

> Taking money in slices too thin to notice has a name: salami slicing. Security textbooks have used it as an example for decades, and stories about rogue programmers skimming rounding errors get retold constantly. Most of those stories are surprisingly hard to pin to a real, documented case, which may itself tell you something. The scheme is easy to imagine and hard to keep hidden.
>
> What actually stops it is unglamorous: a written rounding rule, so there's no free remainder to take; double entry, so the remainder lands somewhere visible; daily reconciliation, so a second calculation checks the first; and change control, so no single programmer can quietly edit the code that moves money.

### 7.10 Recap and challenge · ≈ 1:20

**Visual.** [V7.10a] Two columns build. "Right": "fractions of a cent are real", "tiny × huge
volume = real money", "a decimal point mistake is very believable". "Wrong": "round to
nearest leaves almost nothing to skim", "fractions don't vanish: double entry", "a daily
reconciliation would catch it". A third, `BLUE` column, "Our addition": "floats would skim
nearly whole cents". [V7.10b] The challenge: q07-05's code with the comment "Your check goes
here." highlighted in `YELLOW`. [V7.10c] QR wall: q07-01 to q07-05 for 10 seconds. [V7.10d]
Teaser: a hundred-dollar bill splits into three stacks, and one penny is left over,
spinning on the table.

**On screen**

```python
print("books balance:", sum(ledger.values()) == 0)
# Your check goes here.
```

**QR q07-05** appears at [V7.10b], 10 seconds. Caption: "q07-05 · Challenge: catch the virus".

> Let's take stock. Office Space got the important things right. Fractions of a cent are real, tiny amounts times enormous volumes add up to real money, and a misplaced decimal point is exactly the kind of bug that happens. Where it takes liberties is in imagining that the fractions are free for the taking. Under round to nearest, they mostly cancel. Under double entry, they have to land somewhere visible. And a daily reconciliation would find the account they land in. Floating point wasn't part of the plot, but it would have made things stranger, turning amounts with no fraction into nearly a whole cent of skim.
>
> Here's a challenge. The code in the corner runs the virus on a thousand accounts, and shows that the books balance. Your job is to write the check that catches it. Recompute each customer's interest the bank's way, rounded half up to the cent, compare it with what they were paid, and count the customers who came up short.
>
> Next time: splitting a hundred dollars three ways, and the penny that's always left over. Who should get it?

## Fact check before recording

- Film details (watch the film before recording): *Office Space* (1999), written and
  directed by Mike Judge; the company is Initech; the virus is uploaded into the
  company's accounting system and diverts fractions of a cent per transaction into an
  account the characters control; the characters explicitly compare the plan to
  *Superman III*; the programmer who wrote the virus (Michael Bolton) blames a misplaced
  decimal point, a "mundane detail"; the amount found in the account is commonly quoted as
  $305,326.13, after a few days. The script says "over three hundred thousand dollars" and
  "a few days"; confirm both, and confirm whose accounting system and whose money it is,
  before recording.
- *Superman III* (1983): Richard Pryor plays Gus Gorman, who diverts rounded-off fractions
  of cents from his employer's payroll. The script only says "Superman the Third did it
  first"; check that the film's characters reference it the way 7.1 says.
- Narration must stay a paraphrase; no line of dialogue is quoted. "Superman the Third" is
  written so the voice reads "III" correctly.
- 7.2: "about eleven point eight cents" is q07-01's 0.11838247; "about eight tenths of a
  cent" is 0.8382 ¢; $10.01 earns 0.00095986, "less than a tenth of a cent".
- 7.3: "about two hundred and thirty-nine thousand dollars" is 238,869.60.
- 7.4: back-of-the-envelope figures derived from q07-02's average slice (0.501 ¢): ten
  million accounts × ½ ¢ ≈ $50,000 a day; $305,326.13 ÷ $0.005 ≈ 61 million slices ("around
  sixty million").
- 7.5: "about a hundred and twenty-four dollars and sixty cents" is 124.59; "about a
  hundred and twenty-five dollars" is 125.18; net 0.59.
- 7.6: "a thousand customers" and the ledger values are q07-05's output. Challenge answer
  (don't say it): 508 of the 1,000 customers are short by one cent each, $5.08 in all
  (checked in Python).
- 7.7: q07-04 runs the skim on 10,000 accounts: 50.01 vs 4823.71, "96 times as much".
- 7.8: "a few percent of its amounts" — episode 3 / q03-03 counts 573 of the 10,000 amounts
  $0.00–$99.99 (5.73 %) that `int(x * 100)` gets a cent short (verified for the bible).
- 7.9: "Security textbooks have used it as an example for decades" and "hard to pin to a
  real, documented case" — kept general on purpose. If a specific case is named on
  screen, cite a court record or reputable news source.

# Episode 10 · When the fixes fail

| | |
|---|---|
| Part | Living with it |
| Target length | about 15 min (segment estimates; set final timing from the narration audio) |
| Builds on | Episodes 1–9, especially 9 (integer minor units and `Decimal`) |
| QR codes | q10-01 … q10-05 |

## Learning goals

By the end, the viewer can:

- explain why `Decimal(0.1)` is not one tenth, and how to build a decimal that is;
- say why a decimal type still rounds, and what its precision setting controls;
- spot integer-cents failures: unit mix-ups, 32-bit overflow and JavaScript's safe-integer limit;
- explain why "store cents" really means "store the currency's smallest unit", and why that unit varies;
- explain why converting money there and back doesn't return the original amount;
- say when floating point is the right tool for money-related work, and where to convert.

## Script

### 10.1 The fix that imported the bug · ≈ 1:30

**Visual.** [V10.1a] The checklist card from episode 9 slides in, its first two items
ticked in `GREEN`: "count in minor units", "Decimal for rates". [V10.1b] Code panel
q10-01. The line `from_float = Decimal(0.1)` is highlighted in `YELLOW`. The console prints
`Decimal(0.1)` with its full 55 digits; the tail after `0.10000000000000000` glows `RED`,
exactly as in episode 1's [V1.5c]. [V10.1c] `Decimal("0.1")` prints a clean `0.1` in
`GREEN`; `equal? False` appears in `RED`. [V10.1d] The two "three dimes" lines print. The
float-born version's tail glows `RED`; the text-born `0.3` is `GREEN`. [V10.1e] A second
code panel slides in from the right with the Java version and its output; the matching
55-digit line lines up exactly under the Python one.

**On screen**

```python
from_float = Decimal(0.1)        # the float's error comes along
from_text = Decimal("0.1")       # exactly one tenth
```

```output
Decimal(0.1)   = 0.1000000000000000055511151231257827021181583404541015625
Decimal("0.1") = 0.1
equal? False
three dimes, from floats: 0.3000000000000000166533453694
three dimes, from text:   0.3
```

```java
System.out.println(new BigDecimal(0.1));
System.out.println(new BigDecimal("0.1"));
System.out.println(BigDecimal.valueOf(0.1));
```

```text
0.1000000000000000055511151231257827021181583404541015625
0.1
0.1
```

**QR q10-01** appears at [V10.1c], 8 seconds. Caption: "q10-01 · The Decimal(0.1) trap".

> Last time, we built a checklist for doing money right. Count in whole minor units. Use decimals for rates. Round on purpose. This time, we're going to break the first few items on that list. Not because the advice is wrong, but because each fix has its own way of failing, and you should know what that looks like before it happens in production.
>
> Let's start with the most common one. You've learned that floats are bad and decimals are good, so you write Decimal of zero point one. <break time="0.5s" /> And you get our old friend from episode one: zero point one, sixteen zeros, and nearly forty digits of junk.
>
> What happened? Python read zero point one as a float first, long before Decimal saw it. By then, the dime was already gone. Decimal then did its job perfectly: it recorded that float exactly, error and all.
>
> Give it the string zero point one instead, and you get exactly one tenth. Three of those make exactly zero point three. Three of the float-born ones don't.
>
> Java has exactly the same trap. New BigDecimal of the double zero point one gives the same fifty-five digits. Pass a string, or use value of, and you get one tenth. The rule is the same everywhere: a decimal is only as exact as the digits you hand it.

### 10.2 Decimals still round · ≈ 1:40

**Visual.** [V10.2a] Code panel q10-02. The console prints `precision: 28 digits`. [V10.2b]
"1/3" appears in `YELLOW`, and the episode 1 pie chart of one third returns, now filled
with tenths, hundredths, thousandths … to twenty-eight decimal places. A tiny `RED` sliver
remains. [V10.2c] `1/3 * 3` prints `0.9999999999999999999999999999`; a ruler counts 28
nines. `equals 1? False` in `RED`. [V10.2d] A dial labelled "precision" turns from 28 down
to 6. The two six-digit lines print: `1234.57` in `GREEN`, then `12345.7` in `RED`, with a
`YELLOW` bracket showing that the true answer 12345.68 lost its last digit.

**On screen**

```python
third = Decimal(1) / Decimal(3)
print("1/3     =", third)
print("1/3 * 3 =", third * 3)
print("equals 1?", third * 3 == 1)
```

```output
precision: 28 digits
1/3     = 0.3333333333333333333333333333
1/3 * 3 = 0.9999999999999999999999999999
equals 1? False
with 6 digits: 1234.56 + 0.01 = 1234.57
with 6 digits: 12345.67 + 0.01 = 12345.7
```

**QR q10-02** appears at [V10.2a], 8 seconds. Caption: "q10-02 · One third, to 28 places".

> Here's the second surprise. Decimal fixes the dime, but it doesn't fix arithmetic. Remember the rule from episode one: base ten can only finish fractions built from twos and fives. One third has a three in it. So in decimal, just as on paper, it goes on forever.
>
> Python's decimal module keeps twenty-eight significant digits by default. One third becomes twenty-eight threes. Multiply by three and you get twenty-eight nines, which is not one. Decimal is still a finite number type. It simply rounds in base ten, which happens to be the base money is written in.
>
> That precision is a setting, and it can bite. Turn it down to six digits, and adding a cent to one thousand two hundred thirty-four dollars and fifty-six cents works fine. Add a cent to twelve thousand three hundred forty-five dollars and sixty-seven cents, and the answer needs seven digits. It gets rounded to twelve thousand three hundred forty-five point seven. Two cents appeared from nowhere, and nothing complained.
>
> Nobody sets the precision to six on purpose, of course. But somebody might set it in one place and forget it applies to the whole thread. So when you divide, or multiply by a rate, decide how many places you keep, and round there, on purpose, with quantize.

### 10.3 When types meet · ≈ 1:10

**Visual.** [V10.3a] Two tokens slide toward each other: a `GREEN` "Decimal 1.10" and a
`BLUE` "float 1.10". A `RED` barrier drops between them as the console prints the
`TypeError` line. [V10.3b] Split screen. Left, labelled "Python": the barrier. Right,
labelled "many other languages and libraries": the decimal token quietly turns `BLUE` and
merges with the float. A small `RED` warning icon blinks over the merged token.

**On screen**

```python
try:
    print(Decimal("1.10") + 1.10)
except TypeError as error:
    print("Decimal + float:", error)
```

```output
Decimal + float: unsupported operand type(s) for +: 'decimal.Decimal' and 'float'
```

> The last line of that snippet shows something Python gets right. Try adding a Decimal to a float, and Python refuses. Type error. It won't guess which kind of number you meant.
>
> That error is a gift. It means a float sneaking into your money code fails loudly, in testing, instead of silently, in production. Comparing a Decimal with a float is allowed, and compares the exact values, but arithmetic between them is not.
>
> Many languages and libraries are more forgiving, and forgiving is exactly what you don't want. If mixing the two quietly produces a float, then one stray float anywhere in a calculation turns the whole result back into the thing you were trying to avoid. When you choose a money library, check what it does here.

### 10.4 Integer cents, broken two ways · ≈ 1:50

**Visual.** [V10.4a] A price tag "$12.34" and a box labelled "store cents" outputs
"1234". [V10.4b] The *wrong-unit* bug: the tag "1234" enters a second box labelled "show
dollars" without dividing; the display reads "$1,234.00" in `RED`. A second tag "$12.34"
enters a box that multiplies by 100 twice; out comes "123400". [V10.4c] Code panel q10-03. A
32-cell row of bits fills from the right as the balance grows. The console prints the
largest 32-bit amount, `$21,474,836.47`, in `GOLD`. [V10.4d] A deposit of $2,000,000.00
lands on a $20,000,000.00 balance. The bit row overflows: the leftmost cell flips, and the
balance swings like an odometer to `-20,949,672.96 dollars` in `RED`. [V10.4e] The
JavaScript line: the float line motif returns at its far end, where the gap between ticks widens from one to two.
"9,007,199,254,740,991" and "…992" sit on neighbouring ticks; the next tick is "…994"; the
console shows that `safe + 1` and `safe + 2` both land on "…992".

**On screen**

```python
def as_int32(n):
    n = n & 0xFFFFFFFF                     # keep the low 32 bits
    return n - 2**32 if n >= 2**31 else n  # reinterpret as signed
```

```output
largest 32-bit amount: 2147483647 cents = $21,474,836.47
$20,000,000.00 + $2,000,000.00 = -20,949,672.96 dollars
JavaScript safe limit: 9,007,199,254,740,991 cents
next two whole numbers as floats: 9007199254740992.0 9007199254740992.0
```

**QR q10-03** appears at [V10.4d], 8 seconds. Caption: "q10-03 · When cents overflow".

> Integer cents are the backbone of doing money right. They add exactly, compare exactly, and never drift. But they have two failure modes of their own.
>
> The first is the one from Office Space: the decimal point mistake. Once some numbers in your system mean dollars and others mean cents, every boundary is a chance to forget which is which. Show cents as dollars and a twelve dollar charge becomes twelve hundred. Convert to cents twice, and you get the same hundredfold error from the other side. These bugs aren't subtle. They're off by a factor of a hundred. But they happen, because the number itself doesn't say what unit it's in.
>
> The second is size. Python's integers grow as large as they need to, so the code in the corner imitates a thirty-two-bit integer, the default in plenty of languages and databases. The biggest amount it can hold is about twenty-one and a half million dollars. Add two million to a twenty million dollar balance, and the bits run out. The value wraps around like an odometer, to minus twenty point nine million dollars.
>
> Sixty-four-bit integers push that limit to about ninety-two quadrillion dollars, which is plenty. But every ordinary JavaScript number is a double, and as we saw in episode five, whole numbers stop being exact at two to the fifty-third. In cents, that's about ninety trillion dollars. Past it, the next two whole numbers land on the same tick.

### 10.5 Minor units that don't fit · ≈ 1:40

**Visual.** [V10.5a] A table builds row by row from q10-04's output: currency code, digits
after the point, and "1234.5 in minor units". USD, JPY, KWD rows in `GOLD`; BTC and ETH rows
in `BLUE`, labelled "not ISO 4217". The ETH row's number keeps growing until it spills off
the table's right edge. [V10.5b] The JPY row: the "half" of 1234.5 glows `YELLOW` and then
falls off as `int` truncates it; a `RED` "½ yen dropped" label. [V10.5c] The wrong-exponent
line: "¥1000" is stored as 1000 but read with two decimal places; the display shrinks to
"10 JPY" in `RED`. [V10.5d] A 64-cell bit row fills completely; beside it, a gold coin
labelled "ETH" fills only to "18.446744073709551615".

**On screen**

```python
minor_digits = {"USD": 2, "JPY": 0, "KWD": 3, "BTC": 8, "ETH": 18}
amount = Decimal("1234.5")
for code, digits in minor_digits.items():
    units = int(amount * 10**digits)
    print(f"{code}: 1234.5 = {units:,} minor units")
```

```output
USD: 1234.5 = 123,450 minor units
JPY: 1234.5 = 1,234 minor units
KWD: 1234.5 = 1,234,500 minor units
BTC: 1234.5 = 123,450,000,000 minor units
ETH: 1234.5 = 1,234,500,000,000,000,000,000 minor units
Wrong exponent: 1000 JPY stored as cents shows as 10 JPY
uint64 limit in wei: 18446744073709551615
that is only 18.446744073709551615 ether
```

**QR q10-04** appears at [V10.5a], 8 seconds. Caption: "q10-04 · Minor units that don't fit".

> "Store cents" is really shorthand for "store the smallest unit of the currency." And that unit isn't always a hundredth.
>
> The US dollar has two digits after the point. The Japanese yen has none. The Kuwaiti dinar has three. So the same amount, one thousand two hundred thirty-four and a half, is a different whole number in each. And look at the yen row. There's no such thing as half a yen, so int quietly dropped it. Nothing warned us. Whether that half should be rounded, refused, or carried somewhere else is a policy, and the code just picked one.
>
> Hard-code two decimal places, and a thousand yen, stored correctly as a thousand, displays as ten. That's the decimal point mistake again, wearing a different currency.
>
> Cryptocurrencies stretch this further. A bitcoin divides into a hundred million satoshis. Ether divides into ten to the eighteenth wei. Now the smallest unit is so small that an unsigned sixty-four-bit integer, the same size that comfortably holds dollars in cents, holds only about eighteen and a half ether. Ethereum's own arithmetic uses two-hundred-fifty-six-bit integers.
>
> So an amount should always travel with its currency, and the number of digits should come from the currency, never from an assumption baked into the code.

### 10.6 There and back again · ≈ 1:40

**Visual.** [V10.6a] Two gold coins, "$" and "€", with arrows between them labelled with the
rate and its inverse from q10-05. [V10.6b] The product `rate * inverse: 0.99997857` appears;
a `YELLOW` bracket shows how far it falls short of 1. [V10.6c] The four round trips animate
in turn: each dollar amount flies to euros, snaps to the nearest cent (the float line
motif, ticks one cent apart), flies back and snaps again. $0.03 comes back as $0.04
(`GREEN`, +0.01); $19.99 comes back unchanged; $1000.00 and $5000.00 come back short
(`RED`, −0.02 and −0.11). [V10.6d] The euro changeover rule from episode 6 flashes up for a
moment: "never use inverse rates".

**On screen**

```python
for dollars in ["0.03", "19.99", "1000.00", "5000.00"]:
    usd = Decimal(dollars)
    eur = (usd * rate).quantize(CENT, ROUND_HALF_UP)
    back = (eur * inverse).quantize(CENT, ROUND_HALF_UP)
```

```output
rate: 0.8571  inverse: 1.1667  rate * inverse: 0.99997857
$0.03 -> €0.03 -> $0.04   change: 0.01
$19.99 -> €17.13 -> $19.99   change: 0.00
$1000.00 -> €857.10 -> $999.98   change: -0.02
$5000.00 -> €4285.50 -> $4999.89   change: -0.11
```

**QR q10-05** appears at [V10.6c], 8 seconds. Caption: "q10-05 · Challenge: there and back again".

> Even with perfect decimals, some money operations can't be undone. Currency conversion is the classic.
>
> Here's a made-up exchange rate of zero point eight five seven one euros per dollar, and its inverse, rounded to four places. Multiply them together and you don't get one. You get a little less. An inverse rate is rarely exactly the inverse.
>
> Now convert some amounts to euros and back, rounding to the cent each way. Three cents comes back as four. Nineteen ninety-nine survives. A thousand dollars comes back two cents short, and five thousand comes back eleven cents short. Small amounts are dominated by the rounding to cents; large amounts by the imprecise inverse rate.
>
> None of this is a bug. Each step was exact and rounded on purpose. It's simply a reminder that rounding throws information away, and you can't get it back. That's why the euro changeover rules from episode six forbade inverse rates, and why systems that convert currencies should store the original amount, the rate, and the result, not just the result.

### 10.7 Floats sneaking back in · ≈ 1:20

**Visual.** [V10.7a] A clean pipeline diagram: "CSV file" → "data frame" → "service" →
"JSON" → "browser" → "spreadsheet export" → "database". Every box starts `GREEN`.
[V10.7b] One by one, small `BLUE` float tokens slip in at the joints: a CSV reader guessing
"float64" for a price column, a JSON parser turning `"amount": 12.34` into a number, a
browser doing arithmetic on it, a spreadsheet re-saving it, an ORM mapping a column to
`FLOAT`. Each box they enter turns `BLUE`. [V10.7c] A single `RED` "TypeError" barrier
appears at one joint, in the Python service, stopping a token; the label reads "loud
failures are good failures".

> The last way the fixes fail is the sneakiest: the floats come back without anyone inviting them.
>
> You can write perfect money code, and still receive your prices from a CSV file, where a data library takes one look at a column of numbers with decimal points and decides they're floats. Or from a JSON API, where a parser does the same thing by default. Or from a browser, where every ordinary number is a double. Or from a spreadsheet, which stores doubles and shows you fifteen digits. Or from a database column someone declared as float years ago.
>
> Every one of those is a boundary from episode three, and every one needs a guard: read amounts as strings or as integer minor units, convert them to your money type once, at the edge, and reject anything that arrives as a float. In Python, mixing a stray float with a Decimal fails loudly, which is the outcome you want. Make your boundaries just as unforgiving.

### 10.8 When floats are fine · ≈ 1:30

**Visual.** [V10.8a] The screen splits in two. Left, under the heading "measuring" in
`BLUE`: a smooth curve of a forecast with a shaded uncertainty band, a scatter of
simulated price paths fanning out, a risk histogram. Right, under "counting" in `GOLD`: the
ledger motif, the receipt, a stack of pennies. [V10.8b] An arrow labelled "booking"
crosses from left to right. At the dividing line it passes through a small gate labelled
"round once, with a rule"; the `BLUE` value becomes a `GOLD` amount with exactly two
decimals. [V10.8c] The sentence "Floats are for measuring; money is counted." writes
itself across the middle.

> After ten episodes of warnings, here's something that might surprise you. Floating point is often exactly the right tool for work about money.
>
> A forecast of next year's revenue. A simulation of ten thousand possible price paths. A risk model, an option pricing formula, an average, a regression. None of these is a record of what happened. They're estimates, and their inputs are uncertain long before the fifteenth significant digit. Floats are fast, they're everywhere, and their tiny errors are dwarfed by the uncertainty in the question itself.
>
> The problem is never floating point on its own. It's floating point in a ledger. A ledger records what was actually paid, owed and moved, and it has to agree with other ledgers to the last cent, forever.
>
> So the boundary is the thing to design. When a model's output turns into a real booking, an invoice, a payment, an entry, that's the moment to round once, with a written rule, into integer minor units or a decimal, and never look back.
>
> Or, in one line: <break time="0.6s" /> floats are for measuring; money is counted.

### 10.9 The whole series, in one breath · ≈ 1:40

**Visual.** [V10.9a] The series' recurring motifs return, one per episode, each with its
episode number and a one-line caption, arranged in a ring around an empty centre: the cent grid with
four `GREEN` cells (1); the float line with spreading ticks (2); the risk map (3); the
ledger with its tipped scale (4); language names all printing the same digits (5); the
number line with eight rounding arrows (6); the sliced penny and hidden jar (7); three
stacks with one stray penny (8); the ticked checklist (9). [V10.9b] Episode 10's own motif,
the cracked decimal under "1/3", slides into the centre, and the ring tightens around it.

> Let's put the whole series together.
>
> In episode one, we found that a double can't hold ten cents: only four of the hundred cent values are stored exactly. In episode two, we opened a double and saw fifty-three bits and gaps that grow with size, until a balance can't hold its cents at all. Episode three mapped where the errors bite: running totals, comparisons, conversions to cents, rates, the order of addition, and every boundary between systems. Episode four counted the costs: ghost balances, reconciliation breaks, one-sided bias, and totals you can't reproduce.
>
> Episode five showed that nearly every mainstream language stores the same answers, though they print them differently, because they share the same standard and the same hardware. Episode six made rounding a decision instead of an accident. Episode seven took Office Space seriously, and found that the fractions were real, the scheme needed truncation, and double-entry bookkeeping would have caught it. Episode eight kept splits adding up to the whole, paradoxes and all. Episode nine wrote the checklist. And today, we watched each fix fail in its own way, and learned what to watch for.

### 10.10 Recap, challenge and farewell · ≈ 1:20

**Visual.** [V10.10a] A short recap column builds: "Decimal from strings, not floats" →
"Decimals still round: choose where" → "Integers overflow, and units get mixed up" →
"Minor units come from the currency" → "Conversions don't undo" → "Guard every boundary".
[V10.10b] The q10-05 code returns with its first comment highlighted: "Can you find a rate
where nothing is lost?" [V10.10c] QR wall: q10-01 to q10-05 for 10 seconds. [V10.10d] Final
shot: the gold dime from episode 1 returns, its dashed outline filling in solid `GOLD`
as the text `Decimal("0.10")` types beneath it. Fade to the credits card.

**QR q10-05** appears at [V10.10b], 10 seconds. Caption: "q10-05 · Challenge: there and back again".

> Let's take stock one last time. Build decimals from strings, never from floats. Remember that decimals still round, so decide where. Integer cents can overflow and can be mixed up with dollars. The size of the smallest unit comes from the currency, not from habit. Conversions can't be undone. And floats will try to sneak back in at every boundary, so guard them.
>
> Here's a final challenge. The code in the corner converts dollars to euros and back. Change the rate, the rounding, or the amounts. Can you find a rate where every round trip comes back exact? And if you can't, can you say why not?
>
> That's the end of Money Problems. If you remember one thing, let it be this: floats are for measuring; money is counted. Count it in whole units, round it on purpose, and make every part add up to the whole.
>
> Thanks for watching. <break time="0.5s" /> And may your ledgers always balance, to the very last cent.

## Fact check before recording

- 10.7: spreadsheets "store doubles and show you fifteen digits" — Excel stores IEEE 754
  doubles and displays at most 15 significant digits (Microsoft's "Floating-point arithmetic
  may give inaccurate results in Excel"); other spreadsheet programs may differ.
- 10.5: Ethereum's EVM uses 256-bit words; the script states this without claiming it was
  chosen because of wei.

- 10.1: Java's `new BigDecimal(0.1)` prints the full 55-digit value; `new BigDecimal("0.1")`
  and `BigDecimal.valueOf(0.1)` print `0.1`. Verified with OpenJDK 27.0.1 (`javac`/`java`).
  `valueOf` goes through `Double.toString`, so it gives the shortest repr, not the exact value.
- 10.2: Python `decimal` default context precision is 28 significant digits (q10-02 prints
  it). Context precision applies to arithmetic results, not to `Decimal("…")` construction.
  The context is per thread (`decimal.getcontext()` is thread-local; check contextvars
  behaviour for async code if mentioned further).
- 10.3: the `TypeError` message text is from CPython 3.15 natively; confirm Python Online
  (CPython 3.14.2 in Pyodide) prints the same message, since the output block quotes it.
  Comparisons between `Decimal` and `float` are exact (Python 3.2 and later).
- 10.3: "many other languages and libraries" convert silently — keep generic; don't name a
  specific library without checking its current behaviour.
- 10.4: 32-bit integers as a common default (e.g. `int` in C, Java and C#; SQL `INTEGER` in
  several databases). 64-bit cents limit: 2⁶³ − 1 cents ≈ $92.2 quadrillion.
  JavaScript `Number.MAX_SAFE_INTEGER` = 2⁵³ − 1 = 9,007,199,254,740,991.
- 10.5: ISO 4217 minor units: USD 2, JPY 0, KWD 3 (check the current ISO 4217 list).
  BTC and ETH are not ISO 4217 currencies. 1 BTC = 10⁸ satoshi; 1 ether = 10¹⁸ wei.
  The EVM uses 256-bit words and balances are 256-bit unsigned integers (check the
  Ethereum yellow paper or docs).
- 10.6: the rate 0.8571 is made up (stated in narration). Episode 6's euro changeover rule
  against inverse rates comes from Council Regulation (EC) No 1103/97; keep the wording
  in step with episode 6.
- 10.7: default float inference in common CSV readers (e.g. pandas `read_csv` → float64)
  and JSON parsers (JavaScript `JSON.parse`, Python `json.loads` without `parse_float`);
  narration keeps these generic.
- 10.9: the recap must match what episodes 1–9 actually say once they are final (episode
  numbers, "only four of the hundred cent values", the Office Space conclusions).

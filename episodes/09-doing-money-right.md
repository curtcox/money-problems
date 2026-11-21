# Episode 9 · Doing money right

| | |
|---|---|
| Part | Living with it |
| Target length | about 15 min (segment estimates; set final timing from the narration audio) |
| Builds on | Episodes 1–8, especially 6 (rounding) and 8 (allocation) |
| QR codes | q09-01 … q09-05 |

## Learning goals

By the end, the viewer can:

- store amounts as whole minor units, and format them without floats;
- build decimals from strings and round once, with a named rounding mode;
- keep a currency with every amount, and know that minor units differ by currency;
- read and write money in JSON without passing through a float;
- check money code with an invariant test: the parts add up to the whole;
- apply a seven-point checklist in code review.

## Script

### 9.1 Cold open · ≈ 0:45

**Visual.** [V9.1a] Black canvas. The jar of pennies from the trailer returns, and the
counter runs to "1,000,000 cents" again. [V9.1b] Code panel q09-01 on the left. Two
running totals tick up side by side: `as_float` in `BLUE`, `as_cents` in `GOLD`. [V9.1c]
The console prints. The float total's tail after `10000.` glows `RED`; the cents total,
`1000000`, glows `GREEN`; the formatted "$10,000.00" and "True" follow in `GREEN`.
[V9.1d] The two jars sit side by side: one labelled "measured", slightly overflowing with
a fine `RED` dust; one labelled "counted", filled exactly to a line.

**On screen**

```python
for _ in range(1_000_000):
    as_float += 0.01           # measure a cent
    as_cents += 1              # count a cent
```

```output
float total  = 10000.000000171856
cents total  = 1000000
as money     = $10,000.00
exactly $10,000.00? True
```

**QR q09-01** appears at [V9.1c], 8 seconds. Caption: "q09-01 · Counting cents".

> Remember this? Add one cent to a total, a million times. With floats, you get ten thousand dollars and a sliver.
>
> Now do it again, but this time, count cents instead. Add one to a whole number, a million times. The total is one million cents, exactly. Format it as dollars and cents, and it's ten thousand dollars, exactly. Ask whether it equals ten thousand dollars, and the answer is yes.
>
> That's the whole difference, really. The float version measures a cent: it adds a length that is very nearly one hundredth. The integer version counts a cent: it adds one. And counting never drifts.
>
> We've spent eight episodes on what goes wrong. This one is about doing it right. Seven rules, a tiny money type that enforces them, and a checklist you can take to your next code review.

### 9.2 Rule 1: count, don't measure · ≈ 0:54

**Visual.** [V9.2a] The checklist card appears with seven empty boxes; the first box's
text writes itself: "1. Count, don't measure: whole minor units". [V9.2b] A price tag
"$19.99" turns over to reveal "1999¢" on the back. Three more tags flip: "$0.10 → 10¢",
"$1.15 → 115¢", "$10,000.00 → 1000000¢". [V9.2c] The q09-01 formatting line enlarges:
`divmod(as_cents, 100)` splits "1000000" into "10000" and "00", which reassemble into
"$10,000.00", with no float anywhere along the way (a `GREEN` label: "no float"). [V9.2d] A
small inset contrasts `int(1.15 * 100)` → 114 (`RED`, from episode 3) with "115" typed
straight from the string "1.15" (`GREEN`).

**On screen**

```python
dollars, cents = divmod(as_cents, 100)
print(f"as money     = ${dollars:,}.{cents:02d}")
```

> Rule one: count, don't measure. Store amounts as whole numbers of the smallest unit of the currency: cents for dollars and euros, pence for pounds. Programmers call these minor units.
>
> A whole number of cents can't drift, and it can't sit between two values. Addition is exact, subtraction is exact, and equals equals means what it says. Nineteen ninety-nine is simply one thousand nine hundred and ninety-nine cents.
>
> You only turn it back into dollars at the very edge, when a person needs to read it. And even then, you don't need a float. Divmod by one hundred gives you the dollars and the cents as two whole numbers, and you print them with a dot in between.
>
> One warning. Getting into cents has to be done carefully too. Back in episode three, int of one point one five times one hundred gave us one hundred and fourteen. If an amount arrives as text, convert the text, not a float made from it. Which brings us to rule two.

### 9.3 Rule 2: decimals from strings · ≈ 1:04

**Visual.** [V9.3a] Checklist box 2 writes itself: "2. Decimal for rates, built from
strings". [V9.3b] Code panel q09-02. The first output line prints `0.3` in `GREEN`; the
float line from episode 1, `0.30000000000000004`, appears faded beside it for comparison.
[V9.3c] A tax rate tag "8.25 %" and an exchange rate tag "1.0837" float above the code,
with the label "not whole cents". [V9.3d] Two arrows lead into a `Decimal`: one from the
string `"1.005"` (`GREEN` path), one from the float `1.005` (`RED` path, passing through a
small float-line icon that nudges it down). The last two output lines print: `1.01` and
`1.00`.

**On screen**

```python
CENT = Decimal("0.01")
print("0.1 + 0.2       =", Decimal("0.1") + Decimal("0.2"))
print("from '1.005'    =", Decimal("1.005").quantize(CENT, rounding=ROUND_HALF_UP))
print("from 1.005      =", Decimal(1.005).quantize(CENT, rounding=ROUND_HALF_UP))
```

```output
0.1 + 0.2       = 0.3
from '1.005'    = 1.01
from 1.005      = 1.00
```

**QR q09-02** appears at [V9.3b], 8 seconds. Caption: "q09-02 · Decimal, done right".

> Whole cents are perfect for amounts. But money arithmetic also involves numbers that aren't whole cents: a tax rate of eight and a quarter percent, an interest rate, an exchange rate with four or five decimal places. For those, rule two: use a decimal type, and build it from strings.
>
> Python's Decimal stores numbers in base ten, digit for digit. So Decimal of the string zero point one, plus Decimal of the string zero point two, is exactly zero point three. The fives that broke binary are no problem in base ten.
>
> But notice the quotation marks. They matter enormously. Decimal of the string one point zero zero five is exactly one point zero zero five, and rounding it half up gives one dollar and one cent. Decimal of the float one point zero zero five, without quotes, is the float's value, faithfully copied, every digit of its error included. It's a little below one point zero zero five, so the same rounding gives one dollar.
>
> A decimal type only protects you if no float gets there first. Build decimals from strings, from integers, or from other decimals. Never from floats.

### 9.4 Rule 3: round once, on purpose · ≈ 1:00

**Visual.** [V9.4a] Checklist box 3: "3. Round once, at a defined point, with a named
mode". [V9.4b] The q09-02 tax lines: `2.50 x 0.05 = 0.1250` prints, with the trailing
`50` highlighted `YELLOW` and a small label "exact: no rounding yet". [V9.4c] The rounding
number line from episode 6 returns between 0.12 and 0.13, with 0.125 exactly in the
middle. Two arrows: "half up" to 0.13 and "half even" to 0.12, matching the two output
lines. [V9.4d] A pipeline of boxes: "price × quantity" → "× rate" → "round to cents" (one
`GOLD` box) → "store". A second pipeline with a rounding box after every step is crossed
out in `RED`.

**On screen**

```python
price = Decimal("2.50")
rate = Decimal("0.05")
tax = price * rate
print("half up         =", tax.quantize(CENT, rounding=ROUND_HALF_UP))
print("half even       =", tax.quantize(CENT, rounding=ROUND_HALF_EVEN))
```

```output
2.50 x 0.05     = 0.1250
half up         = 0.13
half even       = 0.12
```

> Rule three: round once, at a point you chose, with a mode you named.
>
> Multiplying these decimals doesn't round anything. Two fifty times five percent is exactly zero point one two five zero, an exact tie between twelve and thirteen cents. Now you round, deliberately, with quantize, telling it the precision you want, one cent, and the rule for ties. Half up gives thirteen cents. Half even gives twelve. As we saw in episode six, which one is right isn't a question for arithmetic. It's a question for your tax authority, your contract, or your accountant.
>
> Two habits make this reliable. First, always pass the rounding mode explicitly, even when the default happens to be what you want, so the next person can see the decision. Second, decide where rounding happens: per line or per invoice, per day or per month. Then round there, once. Rounding at every step of a calculation lets small errors pile up, and makes the result depend on how the code happened to be organised.

### 9.5 Rule 4: carry the currency · ≈ 0:57

**Visual.** [V9.5a] Checklist box 4: "4. Carry the currency; minor units differ". [V9.5b]
Three price tags side by side, each with a ruler underneath showing its minor-unit
digits: "USD 19.99" (two digits after the point), "JPY 1500" (none), "KWD 1.250" (three).
[V9.5c] A bare "1999" floats alone with a question mark: "$19.99? ¥1,999? 1.999 KWD?". The
question mark turns `RED`. [V9.5d] Two tags labelled "5 USD" and "5 JPY" bump into each
other with a `RED` spark; a label: "not the same 5".

> Rule four: an amount is a number and a currency, and you never let them separate.
>
> A bare one thousand nine hundred and ninety-nine is meaningless. Is it nineteen dollars ninety-nine? One thousand nine hundred and ninety-nine yen? Something else entirely?
>
> It matters more than you might expect, because currencies don't all have cents. The international currency standard, I S O forty-two seventeen, lists how many minor-unit digits each currency has. The US dollar has two. The Japanese yen has none: there's no such thing as a hundredth of a yen in everyday prices. The Kuwaiti dinar has three: a thousand fils to the dinar. So "multiply by one hundred" isn't a universal rule. It's a fact about some currencies.
>
> And of course, five dollars plus five yen isn't ten of anything. Code that adds amounts in different currencies has made a mistake, and the best time to find out is the moment it happens.

### 9.6 A tiny Money type · ≈ 1:25

**Visual.** [V9.6a] Code panel q09-03, scrolled to the class. Four `YELLOW` brackets label
the parts as the narration reaches them: "minor: int" (rule 1), "Decimal(text)" (rule 2),
"times(rate, rounding)" (rule 3), "currency" and the check in `__add__` (rule 4). [V9.6b]
The console prints the first three lines; each result glows `GREEN`. [V9.6c] The two
`ValueError` lines print in `RED`; beside the first, the string "1.005" is shown trying to
fit into a two-slot cents ruler, with its third digit hanging off the end.

**On screen**

```python
@dataclass(frozen=True)
class Money:
    minor: int
    currency: str

    def __add__(self, other):
        if other.currency != self.currency:
            raise ValueError(f"can't add {other.currency} to {self.currency}")
        return Money(self.minor + other.minor, self.currency)

    def times(self, rate, rounding=ROUND_HALF_EVEN):
        exact = self.minor * Decimal(rate)
        return Money(int(exact.to_integral_value(rounding)), self.currency)
```

```output
USD 20.00
JPY 1500 | KWD 1.250
USD 1.65
ValueError: 1.005 has too many decimals for USD
ValueError: can't add JPY to USD
```

**QR q09-03** appears at [V9.6a], 8 seconds. Caption: "q09-03 · A tiny Money type".

> Rules are easier to follow when the code won't let you break them. Here's a money type small enough to fit in a QR code, and it builds in all four rules so far.
>
> A Money is two things: a whole number of minor units, and a currency code. It's frozen, so nobody can change an amount behind your back.
>
> You create one from text, with Money dot of. It reads the text as a Decimal, shifts it by the currency's number of minor digits, and checks that the result is a whole number. Nineteen ninety-nine dollars becomes one thousand nine hundred and ninety-nine cents. Fifteen hundred yen stays fifteen hundred. One and a quarter dinars becomes one thousand two hundred and fifty fils, and prints as one point two five zero. But one point zero zero five dollars is refused. It has a fraction of a cent in it, and this type won't quietly round it for you.
>
> Adding checks the currencies first. Dollars plus dollars works. Dollars plus yen raises an error, right there, on the line with the mistake.
>
> And multiplying by a rate is the one place rounding happens. Times takes the rate as a string, does the multiplication exactly in Decimal, and rounds to a whole number of minor units using the mode you give it, half even unless you say otherwise. Nineteen ninety-nine at eight and a quarter percent comes to one dollar sixty-five.
>
> It's not a complete library. Real ones add allocation, formatting for different locales, and much more. But it shows the shape of the idea: make the right thing easy, and the wrong thing an error.

### 9.7 Rule 5: guard the boundaries · ≈ 1:20

**Visual.** [V9.7a] Checklist box 5: "5. Guard the boundaries". A box labelled "your
code" sits in the centre, `GREEN` inside. Around it, doors labelled "JSON", "database",
"browser", "spreadsheet", "CSV". [V9.7b] Code panel q09-04. Through the JSON door, the
amount "4.35" enters as a float and the console prints `434.99999999999994` in `RED`; it
enters again with `parse_float=Decimal` and prints `435.00` in `GREEN`. [V9.7c] On the way
out, the two `json.dumps` lines print: a string price and an integer `price_minor`. The
`TypeError` line prints in `YELLOW`, labelled "a helpful refusal". [V9.7d] The database
door opens on a column definition that reads `amount DECIMAL(19, 4)` in `GREEN`, next to a
crossed-out `amount FLOAT` in `RED`. [V9.7e] The browser door shows a price in a web page,
with the label "integers or a decimal library inside; formatting only at display".

**On screen**

```python
as_float = json.loads(text)
print("float price x 100   =", as_float["price"] * 100)
as_decimal = json.loads(text, parse_float=Decimal)
print("Decimal price x 100 =", as_decimal["price"] * 100)
```

```output
float price x 100   = 434.99999999999994
Decimal price x 100 = 435.00
{"price": "4.35", "currency": "USD"}
{"price_minor": 435, "currency": "USD"}
TypeError: Object of type Decimal is not JSON serializable
```

**QR q09-04** appears at [V9.7b], 8 seconds. Caption: "q09-04 · JSON without floats".

> Rule five: guard the boundaries. Your own code can be perfect, and a float can still sneak in through the door, every time money enters or leaves your program.
>
> JSON is the classic example. A number in JSON has no type of its own, and Python's json module turns anything with a decimal point into a float. A coffee priced at four thirty-five becomes four hundred and thirty-four point nine nine nine, and so on, cents. But pass parse float equals Decimal, and the same text becomes an exact decimal: four hundred and thirty-five cents.
>
> Going out, send amounts either as strings, or as whole minor units with the currency alongside. Python actually refuses to write a Decimal as a JSON number, which is a helpful refusal: it makes you choose.
>
> The same idea applies at every other door. In a database, store money in a decimal or numeric column with a fixed number of places, or in an integer column of minor units, never in a float or real column. In a JavaScript front end, every ordinary number is a double, so keep amounts as integers of minor units or use a decimal library, and format for display only at the very end. And when a spreadsheet or a CSV file comes in, read the amounts as text and convert them yourself, rather than letting a tool guess that they're floats.

### 9.8 Rules 6 and 7: allocate, and test · ≈ 1:14

**Visual.** [V9.8a] Checklist box 6: "6. Allocate, don't divide". The three-way split from
episode 8 replays in miniature: $100.00 → $33.34, $33.33, $33.33, with "sum $100.00" in
`GREEN`. [V9.8b] Checklist box 7: "7. Test the invariants". Code panel q09-05. A stream of
random receipts flies past, each splitting into parts and the parts snapping back
together. For `float_split`, many fail to fit, flashing `RED`; for `allocate`, every one
snaps into place. [V9.8c] The console prints the two result lines; `7431` in `RED`, `0` in
`GREEN`. [V9.8d] A short list of other invariants appears beside the console: "parts sum
to the whole", "debits equal credits", "parse then format gives back the text", "refunds
never exceed payments".

**On screen**

```python
def allocate(total, n):                   # whole cents, extras to the first
    each, extra = divmod(total, n)
    return [each + 1] * extra + [each] * (n - extra)
```

```output
float_split  failed 7431 of 10000
allocate     failed 0 of 10000
```

**QR q09-05** appears at [V9.8b], 8 seconds. Caption: "q09-05 · Challenge: test the invariant".

> Rule six you already know, from the last episode: allocate, don't divide. Whenever an amount is split, into shares, installments or receipt lines, decide the whole-cent parts together so that they add up exactly, and decide on purpose who gets the leftover cents.
>
> And rule seven is how you find out whether you've followed the first six: test the invariants. An invariant is something that must be true no matter what the inputs are. For a split, the parts must add up to the whole. For a ledger, debits must equal credits. Parsing an amount and formatting it again should give back the same text.
>
> The nice thing about invariants is that you don't have to work out the right answer for each test. You can throw thousands of random amounts at your code and simply check that the invariant holds. Here, ten thousand random totals, up to ten thousand dollars, each split among one to twelve people. The tempting float version, divide and round, fails seven thousand four hundred and thirty-one times. The whole-cent allocation fails zero times.
>
> Random inputs find the awkward amounts you'd never think to type: the ones that land near half a cent, or don't divide evenly. And if a test finds a failure, keep that amount as a permanent test, so the bug can never quietly return.

### 9.9 Recap and challenge · ≈ 1:01

**Visual.** [V9.9a] The checklist card fills the screen, all seven boxes ticked in
`GREEN`, and holds for at least 8 seconds:

1. Count, don't measure: store whole minor units.
2. Decimal for rates, built from strings, never from floats.
3. Round once, at a defined point, with a named mode.
4. Carry the currency; minor units differ.
5. Guard the boundaries: JSON, databases, browsers, files.
6. Allocate, don't divide.
7. Test the invariants.

[V9.9b] The q09-05 code returns, with the challenge comment highlighted. [V9.9c] QR wall:
q09-01 to q09-05 for 10 seconds. [V9.9d] Teaser: `Decimal(0.1)` types itself, and its
55-digit value unrolls across the screen; a crack runs through the word "Decimal".

> Here's the whole episode on one card. Count, don't measure: store whole minor units. Use a decimal type for rates, built from strings, never from floats. Round once, at a defined point, with a named mode. Carry the currency, because minor units differ. Guard the boundaries, where floats sneak back in. Allocate, don't divide. And test the invariants.
>
> Pause on this card, take a screenshot, and bring it to your next code review. Any line of money code that breaks one of these rules deserves a question.
>
> Here's the challenge. The code in the corner runs the invariant test. Add a test of your own, perhaps that formatting and parsing an amount gives back the same text. Or break the allocate function on purpose, and watch the test catch it.
>
> But be careful about feeling too safe. Next time, we look at the ways these very fixes still go wrong: decimals that import a float's error, integer cents that overflow, currencies that don't fit, and the places floats sneak back in. And, at last, when floats are exactly the right tool.

## Fact check before recording

- 9.5: ISO 4217 minor units: USD 2, JPY 0, KWD 3 (1 dinar = 1,000 fils). Check the
  current ISO 4217 list (maintained by SIX on behalf of ISO). "No such thing as a hundredth
  of a yen in everyday prices" is deliberately hedged: sub-yen amounts appear in some
  exchange rates and securities prices.
- 9.7: Python's `json.loads` turns JSON numbers with a fraction or exponent into `float`
  unless `parse_float` is given; `json.dumps` raises `TypeError` for `Decimal` (verified by
  q09-04's output on Python 3; confirm the message on Python 3.14 in Python Online).
- 9.7: database advice: SQL `DECIMAL`/`NUMERIC` are exact, `FLOAT`/`REAL`/`DOUBLE PRECISION`
  approximate (SQL standard). `DECIMAL(19, 4)` is shown as an example column type, not a
  universal recommendation; precision and scale should fit the currencies and rates used.
- 9.7: "in a JavaScript front end, every ordinary number is a double" (`Number` is IEEE 754
  binary64; `BigInt` exists for integers). No specific decimal library is named; if one is
  named on screen, check its current maintenance status.
- 9.6: q09-03 is illustrative, not a complete money library; the narration says so.
- 9.8: 7431 and 0 failures come from q09-05 with `random.Random(2026)`; Python's
  `randint` sequence for a fixed seed is stable across Python 3 versions, but confirm the
  output in Python Online before recording.

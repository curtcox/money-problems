# Episode 5 · Every language, the same answer

| | |
|---|---|
| Part | The problem |
| Target length | about 15 min (segment estimates; set final timing from the narration audio) |
| Builds on | Episodes 1–2: why one tenth can't be stored, the parts of a double |
| QR codes | q05-01 … q05-05 |

## Learning goals

By the end, the viewer can:

- explain why `0.1 + 0.2` gives the same result in nearly every mainstream language;
- describe, in a sentence, what IEEE 754 standardised and why it mattered;
- tell the difference between a value and the way a language chooses to print it;
- say where JavaScript's integers stop being exact, and why;
- name the decimal types available in their own language and database, and one trap
  (SQLite's `DECIMAL` column) where a decimal-looking type is not decimal at all.

## Script

### 5.1 Cold open · ≈ 1:02

**Visual.** [V5.1a] A grid of eight small code panels, one per language, each labelled
with the language's name in plain text (no logos): JavaScript, Java, C, Go, Rust, Ruby,
Swift, SQLite. They run one after another, left to right, top to bottom; under each, its
output types out. [V5.1b] Every `0.30000000000000004` lights up `RED` at the same moment,
and the trailing `4`s line up in a column. Every `false` (or `0`) lights up `RED` too.
[V5.1c] The C panel's first line, `0.300000`, gets a `YELLOW` question mark: "hiding?".
[V5.1d] A ninth panel slides in: Python, with q05-02's last line, `False`. All nine panels
shrink into a single row of identical tiles.

**On screen**

```javascript
console.log(0.1 + 0.2);
console.log(0.1 + 0.2 === 0.3);
```

```text
0.30000000000000004
false
```

```java
System.out.println(0.1 + 0.2);
System.out.println(0.1 + 0.2 == 0.3);
```

```text
0.30000000000000004
false
```

```c
double x = 0.1 + 0.2;
printf("%f\n", x);
printf("%.17g\n", x);
printf("%d\n", x == 0.3);
```

```text
0.300000
0.30000000000000004
0
```

```go
a, b := 0.1, 0.2
fmt.Println(a + b)
fmt.Println(a+b == 0.3)
```

```rust
let x: f64 = 0.1 + 0.2;
println!("{}", x);
println!("{}", x == 0.3);
```

```ruby
puts 0.1 + 0.2
puts 0.1 + 0.2 == 0.3
```

```swift
let x = 0.1 + 0.2
print(x)
print(x == 0.3)
```

```text
0.30000000000000004
false
```

(Go, Rust, Ruby and Swift each print the two lines above.)

```sql
SELECT 0.1 + 0.2;
SELECT 0.1 + 0.2 = 0.3;
```

```text
0.30000000000000004
0
```

> In the last four episodes, every example has been in Python. So it's fair to ask: is this just a Python problem? Maybe some other language gets ten cents plus twenty cents right.
>
> Let's ask. JavaScript: zero point three, fifteen zeros, and a four. And no, it's not equal to zero point three. Java: the same digits, the same no. Go, Rust, Ruby, Swift: the same, every one of them. Even the database: SQLite, asked to add zero point one and zero point two, gives the same digits, and says they aren't equal to zero point three.
>
> C is the odd one out, at first glance. Its usual way of printing says zero point three, followed by zeros. But ask C to show seventeen significant digits, and there's our old friend, the four. And the comparison? Zero, which in C means false.
>
> Eight languages and a database, built by different people, in different decades, for different purposes. And they all agree on this one strange answer, down to the last digit. That's not a coincidence, and it isn't eight copies of the same bug. It's a standard.

### 5.2 Same bits everywhere · ≈ 1:06

**Visual.** [V5.2a] Code panel q05-01 and console. Each hex string types out, then
expands into 64 binary boxes in three coloured groups: 1 sign bit (`GREY`), 11 exponent
bits (`YELLOW`), 52 fraction bits (`BLUE`), as built in episode 2. [V5.2b] The rows for
`0.1 + 0.2` and `0.3` line up one above the other. Every box matches except the last hex
digit: `4` against `3`. The final three bits glow `RED`. [V5.2c] The eight language tiles
from 5.1 fly in and each drops the same 64-box pattern into a shared slot, as if
inserting the same key into the same lock.

**On screen**

```python
def bits(x):
    return struct.pack(">d", x).hex()
```

```output
      0.1  3fb999999999999a
      0.2  3fc999999999999a
0.1 + 0.2  3fd3333333333334
      0.3  3fd3333333333333
```

**QR q05-01** appears at [V5.2a], 8 seconds. Caption: "q05-01 · Same bits everywhere".

> Here's what all of those languages have in common. When you write zero point one, each of them stores the same sixty-four bits, and we can look at them directly.
>
> This code takes a double and prints its raw bits, in hexadecimal, sixteen hex digits for sixty-four bits. Zero point one is three, f, b, and then a run of nines ending in an a. You'll recognise that repeating pattern: it's the endless zero, zero, one, one of one tenth, rounded off at the end, which is why the last digit is an a and not a nine.
>
> Now compare the sum of zero point one and zero point two with zero point three. Every hex digit is the same except the last one: a four for the sum, a three for zero point three. That's the one step on the float line we found in episode one. Two neighbouring doubles.
>
> JavaScript, Java, C, Go, Rust, Ruby, Swift, SQLite: all of them store these exact bits, add them with the exact same rules, and land on the exact same neighbour. They don't just get similar answers. They get identical bits.

### 5.3 Before the standard · ≈ 1:27

**Visual.** [V5.3a] A timeline from 1950 to 1990. Before 1985, a row of distinct
"machines" (plain labelled boxes, no logos): "IBM System/360: base 16", "DEC VAX: its own
formats", "Cray: its own formats", "others…". Each box has its own small register diagram
with different bit layouts. [V5.3b] The same calculation is fed to each machine; each
produces a slightly different final digit, coloured differently. A program moved from one
box to another changes its answer. [V5.3c] At 1980, a chip icon: "Intel 8087 coprocessor
implements a draft". At 1985: "IEEE 754 published". A name card: "William Kahan, principal
architect". At 1989: "Turing Award". [V5.3d] After 1985, the machines' register diagrams
all morph into the same 1-11-52 layout. A large stamp: "binary64".

> It wasn't always like this. Through the nineteen sixties and seventies, every computer maker had its own idea of what a floating-point number was. IBM's big machines worked in base sixteen. Digital Equipment's VAX had its own formats. Cray's supercomputers had theirs. They differed in how many bits went where, in how results were rounded, and in what happened when something went wrong, like dividing by zero.
>
> So the same program, with the same input, could print different answers on different machines. Moving numerical software from one computer to another meant re-checking all of it.
>
> In the late nineteen seventies, a committee of the Institute of Electrical and Electronics Engineers, the I triple E, set out to fix that. Its principal architect was William Kahan, a mathematician at Berkeley, who later received the Turing Award for this work. Intel built an early draft of the design into its 8087 maths coprocessor in 1980, and in 1985 the standard was published: IEEE 754.
>
> It pinned down everything: the formats, the rounding rules, the special values, and the promise that adding, subtracting, multiplying, dividing and taking a square root give the correctly rounded result. Today, every mainstream processor implements its sixty-four-bit format, binary64, in hardware. And nearly every mainstream language, when you write a number with a decimal point, hands it straight to that hardware.
>
> That's why the answers agree. The languages aren't doing arithmetic. The chip is.

### 5.4 What float really is · ≈ 0:45

**Visual.** [V5.4a] Code panel q05-04 and console. Each line of output connects with a
`YELLOW` line to the matching part of the 64-box diagram: `mant_dig 53` to the 52 fraction
boxes plus a ghost "implicit 1" box; `radix 2` to a large "base 2" label; `epsilon` to the
gap between 1 and the next tick on the float line. [V5.4b] `dig 15` appears with a short
caption: "15 decimal digits always survive a round trip through a double". [V5.4c] The
largest double appears and scrolls off the right edge as a very long number.

**On screen**

```python
info = sys.float_info
print("significant bits (mant_dig):", info.mant_dig)
print("reliable decimal digits:    ", info.dig)
```

```output
significant bits (mant_dig): 53
reliable decimal digits:     15
largest double:              1.7976931348623157e+308
gap just above 1 (epsilon):  2.220446049250313e-16
radix (base):                2
```

**QR q05-04** appears at [V5.4a], 8 seconds. Caption: "q05-04 · What float really is".

> You can ask Python directly what its float is. The sys module has a record called float info, and it describes the hardware's double.
>
> Fifty-three significant bits: the fifty-two that are stored, plus the leading one that's implied. Fifteen decimal digits that are always safe: any decimal number with fifteen significant digits survives the trip into a double and back. A radix, or base, of two. And epsilon, the gap between one and the very next double, about two times ten to the minus sixteen.
>
> Python didn't choose any of these numbers. They come from IEEE 754, and Python simply reports them. Ask the same question in C or in Rust, and you'll get the same fifty-three, the same fifteen, the same two.

### 5.5 One value, four costumes · ≈ 1:06

**Visual.** [V5.5a] A single gold dot on the float line: the double `0x3fd3333333333334`.
Four "costume" cards drop over it in turn, each labelled with who wears it: "shortest
repr: Python, JavaScript, Java", "6 decimals: C printf %f", "15 digits: spreadsheet
display", "17 digits: C printf %.17g". [V5.5b] Code panel q05-02; each output line appears
as its card lands. The two costumes that print `0.300000` and `0.3` are drawn as masks;
lifting a mask shows the same dot underneath, still one tick right of 0.3's double.
[V5.5c] The last line, `False`, glows `RED` under all four costumes at once.

**On screen**

```python
x = 0.1 + 0.2
print("shortest repr (Python, JavaScript, Java):", repr(x))
print("6 decimals    (C printf %f):             ", f"{x:.6f}")
print("15 digits     (spreadsheet display):     ", f"{x:.15g}")
print("17 digits     (C printf %.17g):          ", f"{x:.17g}")
```

```output
shortest repr (Python, JavaScript, Java): 0.30000000000000004
6 decimals    (C printf %f):              0.300000
15 digits     (spreadsheet display):      0.3
17 digits     (C printf %.17g):           0.30000000000000004
is it 0.3?                                False
```

**QR q05-02** appears at [V5.5b], 8 seconds. Caption: "q05-02 · One value, four costumes".

> So if every language stores the same bits, why did C print zero point three, followed by zeros?
>
> Because storing a number and printing it are two separate jobs. The value is fixed by the hardware. How it's shown is up to the language, and languages make different choices.
>
> Python, JavaScript and Java print the shortest decimal that leads back to exactly this double. That's honest: it shows the error as soon as the error makes a difference. C's printf, by default, shows six decimal places, and six places of this number round to zero point three, zero, zero, zero, zero, zero. Spreadsheets typically show at most fifteen significant digits, and fifteen digits of this number is simply zero point three. Ask for seventeen digits, and the four comes back.
>
> Four costumes, one value underneath. And whichever costume it's wearing, the comparison at the bottom still says false. Displays can hide the error. They can't remove it. That's worth remembering every time a spreadsheet or a report looks perfect: what you see may be a costume.

### 5.6 JavaScript's integer ceiling · ≈ 1:11

**Visual.** [V5.6a] The float line again, now far to the right, around 2⁵³. Below 2⁵³,
ticks fall on every whole number. At 2⁵³ the spacing doubles: ticks only on even numbers.
[V5.6b] Code panel q05-03; the five integers drop toward the line one by one. 2⁵³ − 1 and
2⁵³ land on ticks (`GREEN`). 2⁵³ + 1 falls between two ticks and snaps left to 2⁵³ (`RED`).
2⁵³ + 2 lands on a tick. 2⁵³ + 3 is a tie and snaps right to 2⁵³ + 4. [V5.6c] The cents
line: "$90,071,992,547,409.93" in `GOLD`, with `False` in `RED`.

**On screen**

```python
for n in [limit - 1, limit, limit + 1, limit + 2, limit + 3]:
    print(f"{n} as a double -> {float(n):.0f}")
```

```output
9007199254740991 as a double -> 9007199254740991
9007199254740992 as a double -> 9007199254740992
9007199254740993 as a double -> 9007199254740992
9007199254740994 as a double -> 9007199254740994
9007199254740995 as a double -> 9007199254740996
$90,071,992,547,409.93 in cents, as a double: False
```

```javascript
console.log(2 ** 53 + 1);
console.log(Number.MAX_SAFE_INTEGER);
```

```text
9007199254740992
9007199254740991
```

**QR q05-03** appears at [V5.6b], 8 seconds. Caption: "q05-03 · JavaScript's integer ceiling".

> One language deserves a closer look, because it runs in every browser and a huge amount of money passes through it: JavaScript.
>
> For most of its life, JavaScript had exactly one kind of number, and that number is a double. Even the whole numbers. And a double has fifty-three significant bits, so whole numbers are exact only up to two to the fifty-third, which is about nine quadrillion. Past that, the doubles are two apart, and odd numbers simply don't exist. Ask JavaScript for two to the fifty-third plus one, and it gives you back two to the fifty-third. That's why it has a constant called max safe integer: the largest whole number whose next neighbour is still exact.
>
> Python's own integers have no such limit, so this code uses float to show what a double would do. If you store an amount in cents, you're safe up to about ninety trillion dollars. Most of us are. But database IDs, account numbers and amounts in very small units can cross that line, and JavaScript will round them without a word. In 2020, the language added a second number type, BigInt, for exactly this reason.

### 5.7 Databases and spreadsheets · ≈ 1:35

**Visual.** [V5.7a] A database table icon with two columns: one labelled `FLOAT / REAL /
DOUBLE PRECISION` in `RED` ("approximate"), one labelled `DECIMAL / NUMERIC` in `GREEN`
("exact"). [V5.7b] The SQLite trap: a table `payments` with a column typed
`DECIMAL(10, 2)`. Two rows go in, 0.10 and 0.20. `SUM` prints `0.30000000000000004`; the
`GREEN` "exact" label peels off the column header and reveals `real` underneath. [V5.7c] A
spreadsheet cell with `=850*77.1`. Below it, the stored value `65534.99999999999` in
`BLUE`. The cell displays "100000" in `RED`, then a 2007 patch icon replaces it with
"65535" in `GREEN`.

**On screen**

```sql
CREATE TABLE payments (amount DECIMAL(10, 2));
INSERT INTO payments VALUES (0.10), (0.20);
SELECT SUM(amount) FROM payments;
SELECT typeof(amount) FROM payments LIMIT 1;
```

```text
0.30000000000000004
real
```

> Databases follow the same standard, with one helpful twist. The SQL language has two families of number types. FLOAT, REAL and DOUBLE PRECISION are approximate: they're doubles, or sometimes smaller floats. DECIMAL and NUMERIC are meant to be exact: you say how many digits, and how many of them come after the point.
>
> So you'd think declaring a column as DECIMAL ten comma two would be enough. In most databases, it is. But not in all of them. Here's SQLite, the database inside billions of phones and browsers. It accepts the DECIMAL declaration, and then stores the values as plain doubles anyway. Sum ten cents and twenty cents, and there's our four again. Ask what type it stored, and it says: real. Check what your database actually does with that word.
>
> Spreadsheets live on doubles too. Excel stores numbers as binary doubles and displays at most fifteen significant digits, which is one of those costumes from earlier. And in 2007, that costume famously slipped. Type eight hundred and fifty times seventy-seven point one into the newly released Excel 2007, and the cell displayed one hundred thousand. The right answer is sixty-five thousand, five hundred and thirty-five.
>
> The stored value was fine: the double just below sixty-five thousand five hundred and thirty-five, because seventy-seven point one can't be stored exactly. The bug was in the code that turned that double into text for the screen. Microsoft fixed it within weeks. But it's a perfect miniature of this whole series: the real value was slightly off, the display tried to hide that, and the hiding went wrong.

### 5.8 The exceptions · ≈ 1:28

**Visual.** [V5.8a] A wall of language names in `GREY`, all labelled "binary64 by default".
Some of them light up `GREEN` with a second label naming their decimal type: "C#:
decimal", "Java: BigDecimal", "Python: decimal, fractions", "Ruby: BigDecimal, Rational",
"SQL: DECIMAL, NUMERIC". [V5.8b] One name sits apart, glowing `GOLD`: "COBOL", with a
`PIC 9(7)V99` field drawn as nine digit boxes and an implied decimal point between the
seventh and eighth. [V5.8c] A short text card: "IEEE 754-2008: decimal formats ·
hardware: IBM POWER and IBM Z · C23: _Decimal64". [V5.8d] "JavaScript: no built-in
decimal (yet)" in `GREY`.

**On screen**

```java
System.out.println(new BigDecimal("0.1").add(new BigDecimal("0.2")));
```

```text
0.3
```

> So is every language stuck with this? No. Nearly every mainstream language has binary doubles as its default, but most also offer a second kind of number that works in base ten.
>
> C sharp has a built-in type called decimal: one hundred and twenty-eight bits, storing a whole number and a power of ten. Java has BigDecimal, and when you build it from the strings zero point one and zero point two, the sum is exactly zero point three. Python has the decimal module, and also fractions, for exact ratios. Ruby has BigDecimal and Rational. And SQL databases, SQLite aside, have DECIMAL and NUMERIC.
>
> And then there's COBOL, the language that much of the world's banking was built on. COBOL was designed for business, and its everyday numbers are decimal by default. A field declared as picture nine, seven, V, nine, nine holds seven digits, an implied decimal point, and exactly two digits of cents. No binary fractions involved. That's one reason the old mainframe ledgers rarely had this problem: they never asked binary hardware to hold a dime.
>
> The standard caught up, too. The 2008 revision of IEEE 754 added decimal floating-point formats, IBM builds them into the hardware of some of its server processors, and the latest C standard has decimal floating types. JavaScript still has no built-in decimal type, although a proposal to add one is under discussion.

### 5.9 Why binary is the default · ≈ 0:48

**Visual.** [V5.9a] Two figures side by side: a "scientist" icon measuring with a ruler and
a stopwatch, and an "accountant" icon counting coins. Above the scientist, "binary64:
fast, compact, in hardware"; above the accountant, "decimal: exact for prices, slower,
often in software". [V5.9b] The scientist's ruler reading "2.718281828…" and a stopwatch
reading "9.58 s"; neither cares whether the error is in base two or ten. The accountant's
dime does care. [V5.9c] Text: "Measure with floats. Count with integers and decimals."
fades in, then fades halfway out, held back for episode 10.

> Why did everyone choose binary, if decimal would have spared us all this?
>
> Because floating point was built for measuring. Distances, temperatures, forces, voltages, probabilities. Measurements already carry error. A ruler isn't exact, and a thermometer isn't exact, so a tiny rounding error in the last bit simply doesn't matter, and nobody cares whether that error is in base two or base ten. What scientists and engineers need is speed, range and predictable behaviour, and binary hardware delivers all three, cheaply.
>
> Money is different. Money isn't measured. It's counted. Nobody has nine point nine nine nine nine dimes. And counting needs exactness, in the base we count in. The languages didn't make a mistake. They picked the scientist's number. Our job is to notice when we're doing the accountant's work.

### 5.10 Recap and challenge · ≈ 1:07

**Visual.** [V5.10a] A recap column builds: "Same bits in every language" → "IEEE 754
since 1985, in the hardware" → "Printing is a costume" → "JavaScript: exact integers only
to 2⁵³" → "DECIMAL might not mean decimal" → "Most languages have a decimal type". [V5.10b]
The challenge: q05-05's code and output; the `Decimal` and `Fraction` lines glow
`GREEN`. A `YELLOW` sticky note: "Now try Decimal(0.1) without the quotes." [V5.10c] QR
wall: q05-01 to q05-05 for 10 seconds. [V5.10d] Teaser: `round(2.675, 2)` prints `2.67`;
eight arrows fan out from 2.675 on a number line, each labelled with a rounding mode.

**On screen**

```python
print("Decimal:  ", Decimal("0.1") + Decimal("0.2"),
      Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
```

```output
floats:    0.30000000000000004 False
Decimal:   0.3 True
Fraction:  3/10 True
```

**QR q05-05** appears at [V5.10b], 10 seconds. Caption: "q05-05 · Challenge: decimal arithmetic".

> Let's take stock. It isn't Python. Nearly every mainstream language stores the same sixty-four bits for zero point one, because they all hand their arithmetic to hardware built to the IEEE 754 standard. They differ only in how they print the result, and a tidy printout is a costume, not a cure. JavaScript's integers stop being exact at two to the fifty-third. A column called DECIMAL might quietly be a double. And most languages offer a real decimal type, if you ask for it.
>
> Here's the challenge. In the code in the corner, Python's decimal and fractions modules both say that one tenth plus two tenths equals three tenths. Now remove the quotes from Decimal of zero point one, and pass it the float instead. Predict what happens before you run it. It's the most common way to bring the bug right back into the fix, and we'll come back to it in the final episode.
>
> Next time: rounding. Why Python rounds two point six seven five down, why there are at least eight different ways to round, and why choosing one is a business decision, not a maths one.

## Fact check before recording

- 5.3: "every mainstream processor implements binary64 in hardware" means desktop, server and
  phone processors; some microcontrollers have only single-precision hardware or none.
- 5.8: "the old mainframe ledgers rarely had this problem" is a historical generalisation
  (COBOL's default `USAGE DISPLAY` and `COMP-3` packed decimal fields are decimal); keep it
  hedged, or cite a source on COBOL decimal arithmetic in banking.
- 5.3, 5.8, 5.10: "nearly every mainstream language": exceptions include COBOL (decimal by
  default) and Groovy, whose decimal literals are `BigDecimal` (`println(0.1 + 0.2)` prints 0.3).

- 5.1, 5.6, 5.7, 5.8: every non-Python sample was run on 12 November 2026 with exactly the
  code shown (complete programs wrap it in `main` etc.), and the outputs are what they
  printed. Toolchains: Node v26.13.1; OpenJDK 27.0.1; Apple clang 21.0.0; Go 1.27.4;
  rustc 1.94.0; Ruby 4.0.9; Apple Swift 6.4.2; SQLite 3.54.0. Re-run if newer versions
  are used for screen recordings.
- 5.1: C's `printf("%f")` prints `0.300000`; `%.17g` prints `0.30000000000000004` (above).
- 5.5: "Python, JavaScript and Java print the shortest decimal that round-trips". True for
  Python (3.1+) and JavaScript (ECMAScript Number::toString). Java's `Double.toString`
  has produced the shortest representation since JDK 19 (earlier versions sometimes
  printed extra digits, but not for this value). Check the JDK 19 release note.
- 5.5, 5.7: spreadsheets "show at most fifteen significant digits": Microsoft documents
  Excel's 15-digit precision limit ("Floating-point arithmetic may give inaccurate
  results in Excel"). Other spreadsheet programs vary.
- 5.3: pre-1985 formats (IBM System/360 hexadecimal floating point; DEC VAX F/D/G/H
  formats; Cray's own format); the IEEE 754 committee began in 1977; William Kahan as
  principal architect; Turing Award 1989 "for his fundamental contributions to numerical
  analysis", including floating point; Intel 8087 (1980) implemented a draft;
  IEEE 754-1985 published 1985. Check the ACM Turing Award citation and IEEE history.
- 5.6: BigInt standardised in ECMAScript 2020.
- 5.7: SQLite stores values declared `DECIMAL(10, 2)` with NUMERIC affinity, which keeps
  0.10 as a REAL (verified above, `typeof` = `real`); see sqlite.org/datatype3.html.
  "Billions of phones and browsers": SQLite's own site claims it is the most widely
  deployed database engine; keep the wording general.
- 5.7: Excel 2007 bug: `=850*77.1` displayed 100,000 instead of 65,535 (a display bug for
  a handful of values next to 65,535 and 65,536; the stored value was correct). Reported
  September 2007, fixed by a Microsoft update in October 2007. The product of the doubles
  is 65534.99999999999 (Python `850*77.1`). Check Microsoft's Excel team blog post of
  September 2007 and the fix date.
- 5.8: C# `decimal` is 128 bits: a 96-bit integer, a sign, and a scale of 0 to 28.
  COBOL `PIC 9(7)V99`: V is an implied decimal point; numeric `DISPLAY` and `COMP-3`
  (packed decimal) fields are decimal. IEEE 754-2008 defines decimal32/64/128; hardware
  decimal floating point on IBM POWER6 and later and on IBM z10 and later; C23 adds
  `_Decimal32/64/128` (conditionally supported). TC39 "Decimal" proposal: confirm its
  current stage before recording and adjust "under discussion" if it has advanced.
- 5.9: "9.58 s" on the stopwatch is decorative (the 100 m world record); drop it if it
  invites questions.

# Episode 2 · Inside a double

| | |
|---|---|
| Part | The problem |
| Target length | about 15 min (segment estimates; set final timing from the narration audio) |
| Builds on | Episode 1: binary fractions, 53 significant bits, the float line |
| QR codes | q02-01 … q02-05 |

## Learning goals

By the end, the viewer can:

- describe a double as a sign, an exponent and a 53-bit significand, and read `float.hex`;
- explain why the gaps between neighbouring doubles double at every power of two;
- estimate where a balance can no longer hold its cents, in 64-bit and in 32-bit floats;
- state the rounding rule every operation follows: round to nearest, ties to even;
- explain why `print` usually shows a tidy number, and when it doesn't.

## Script

### 2.1 Cold open · ≈ 0:38

**Visual.** [V2.1a] A simple house outline with a price tag: "$131,072.01". [V2.1b] The tag
is fed into a narrow box labelled "32-bit float"; out the other side comes "$131,072.015625".
The extra `5625` glows `RED`. [V2.1c] A second tag, "$1,000,000.01", goes through the same
box and comes out as "$1,000,000.0"; the lost cent tumbles off the tag as a small gold coin.
[V2.1d] The console shows the q02-03 lines for both prices. The two `RED` details pulse.

**On screen**

```output
$   131,072.01  stored as   131,072.015625
$ 1,000,000.01  stored as      1,000,000.0
```

> Here's a house, priced at one hundred and thirty-one thousand and seventy-two dollars and one cent. Store that price in a thirty-two-bit float, the smaller cousin of the numbers we met last time, and read it back. You get the same dollars, and one point five six two five cents.
>
> Try a million dollars and one cent. The cent is simply gone.
>
> In the last episode we saw that a computer can't store ten cents exactly, but it gets wonderfully close. Today we'll see that "close" depends on how big the number is. The bigger the amount, the coarser the grid a computer can use to store it, until one day there's no room left for the cents at all.
>
> To understand why, we need to open up a floating-point number and look inside.

### 2.2 Scientific notation, in binary · ≈ 1:39

**Visual.** [V2.2a] Decimal scientific notation first: "6.02 × 10²³" and "1.6 × 10⁻⁴",
with the digits labelled "significand" (`BLUE`) and the power labelled "exponent" (`YELLOW`).
A decimal point slides left and right as the exponent changes. [V2.2b] The same idea in
binary: "1.1001100… × 2⁻⁴". [V2.2c] A long strip of 64 boxes appears and splits into three
coloured groups: 1 box "sign" (`GREY`), 11 boxes "exponent" (`YELLOW`), 52 boxes "fraction"
(`BLUE`). [V2.2d] Code panel q02-01; the console prints the three lines for 0.1. The bits
fill the strip. The exponent `01111111011` morphs into "1019 − 1023 = −4". [V2.2e] A ghost box
appears to the left of the fraction, labelled "implicit 1", making "53 bits". [V2.2f] The last
four fraction bits, `1010`, glow `YELLOW`: the repeating pattern `1001` was rounded up to
`1010`. [V2.2g] The 0.25 lines print: fraction all zeros, exponent −2. Caption: "¼ = 1.0 × 2⁻²".

**On screen**

```python
def show(x):
    bits = format(struct.unpack(">Q", struct.pack(">d", x))[0], "064b")
    sign, exponent, fraction = bits[0], bits[1:12], bits[12:]
```

```output
0.1  hex 3fb999999999999a  0x1.999999999999ap-4
  sign 0  exponent 01111111011 = -4
  fraction 1001100110011001100110011001100110011001100110011010
```

**QR q02-01** appears at [V2.2d], 8 seconds. Caption: "q02-01 · The bits of a double".

> A double is scientific notation, done in binary.
>
> In decimal scientific notation, you write a number as a few significant digits, times ten to some power. The digits say what the number is. The power says where the decimal point goes. Slide the point left or right, and the same digits describe a tiny number or a huge one.
>
> A double does exactly that with twos. It's sixty-four bits, split into three parts. One bit for the sign: plus or minus. Eleven bits for the exponent: how far to slide the binary point. And fifty-two bits for the fraction: the significant digits.
>
> Let's look at zero point one. Its exponent bits, read as a number, are one thousand and nineteen. The format stores exponents with an offset of one thousand and twenty-three, so the real exponent is minus four. And the fraction bits are our old friend from the last episode: one, zero, zero, one, repeating.
>
> So zero point one is stored as one point something, times two to the minus four. One point six, times one sixteenth.
>
> You might have noticed that the fraction has only fifty-two bits, but I promised you fifty-three. Here's the trick. In binary scientific notation, the first significant digit is always a one, so there's no point storing it. It's implied. That free bit is why a double has fifty-three bits of precision.
>
> And look at the very end. The repeating pattern should continue one, zero, zero, one. Instead it ends one, zero, one, zero. That's the rounding we saw last time: the infinite tail was more than half a step, so the last bit was rounded up.
>
> Compare a quarter. It's exactly one times two to the minus two, so the fraction is fifty-two zeros. Nothing to round. Nothing lost.

### 2.3 A sliding window · ≈ 0:57

**Visual.** [V2.3a] The float line from episode 1, now from 1 to 2. Ticks are drawn as a
dense `BLUE` comb; a label reads "2⁵² doubles". [V2.3b] The line extends from 2 to 4. The
same number of ticks fills it, now twice as far apart; label "2⁵² doubles, gaps × 2". Then 4
to 8, 8 to 16: each interval has the same count and twice the gap. [V2.3c] A window frame
labelled "53 bits" slides along a long binary string representing a growing balance. The
whole-dollar bits enter from the left and push the cents bits out of the window on the right.
[V2.3d] A caption: "about 16 significant decimal digits, shared between dollars and cents".

> Here's the key consequence. The fifty-three bits of a double are a fixed number of significant digits. The exponent decides where they sit, but there are always the same number of them.
>
> So between one and two, there are two to the fifty-second doubles, evenly spaced. Between two and four there are exactly as many. But that interval is twice as long, so they're twice as far apart. Between four and eight, twice as far again. Every time a number doubles, the gaps between its neighbours double too.
>
> Think of the fifty-three bits as a window that slides along the number. A small amount has plenty of room for the fraction: the window covers lots of bits after the binary point. As the amount grows, the bits in front of the point need more and more of the window, and the fraction bits get pushed out the far end.
>
> In decimal terms, that's about fifteen or sixteen significant digits. They're shared between the dollars and the cents. The more digits the dollars need, the fewer are left for everything after the point.

### 2.4 The gap table · ≈ 0:39

**Visual.** [V2.4a] Code panel q02-02. The console prints the gap table one row at a time.
Beside each row a ruler segment shows the gap, drawn on a log scale; a `GREEN` reference
mark at the right shows "1¢". [V2.4b] The rows from $1 up to a trillion stay far left of the
cent mark. [V2.4c] The quadrillion row reaches "0.125": past the cent mark, `RED`, labelled
"an eighth of a dollar". The ten-quadrillion row shows "2": the ruler overshoots the frame.

**On screen**

```python
for dollars in [1, 1_000, 1_000_000, 1_000_000_000, 10**12, 10**15, 10**16]:
    print(f"${dollars:>22,}   gap {math.ulp(dollars):.3g}")
```

```output
$                     1   gap 2.22e-16
$             1,000,000   gap 1.16e-10
$     1,000,000,000,000   gap 0.000122
$ 1,000,000,000,000,000   gap 0.125
$10,000,000,000,000,000   gap 2
```

**QR q02-02** appears at [V2.4a], 8 seconds. Caption: "q02-02 · The gaps between doubles".

> We can measure those gaps directly. Python's math dot u l p, short for unit in the last place, gives the distance from a number to the next double up.
>
> At one dollar, the gap is about two times ten to the minus sixteen. Tiny. At a million dollars, it's about a ten-billionth of a dollar. At a trillion dollars, it's a little over a hundredth of a cent. Still fine for money.
>
> But keep going. At a quadrillion dollars, the gap between neighbouring doubles is an eighth of a dollar. There is no double for a quadrillion dollars and one cent. And at ten quadrillion, the gap is two whole dollars. The odd-numbered dollar amounts don't exist at all.

### 2.5 When a balance loses its cents · ≈ 1:09

**Visual.** [V2.5a] The last three lines of q02-02 print. Each becomes a float-line close-up
around its power of two, with the ticks labelled by their gap and a `GOLD` "+1¢" arrow
starting at the left tick. [V2.5b] At 2⁴⁵ the gap is smaller than a cent; the arrow lands
between ticks and snaps to the nearest one. [V2.5c] At 2⁴⁶ the gap is bigger than a cent;
the arrow lands past the halfway point and snaps up, to a tick a cent and a half away.
[V2.5d] At 2⁴⁷ the arrow lands short of halfway and snaps back to where it started. A
`RED` "x + 0.01 == x" stamp: True.

**On screen**

```output
2**45 = $35,184,372,088,832  gap 0.0078125  x + 0.01 == x: False
2**46 = $70,368,744,177,664  gap 0.015625  x + 0.01 == x: False
2**47 = $140,737,488,355,328  gap 0.03125  x + 0.01 == x: True
```

> So where exactly does money stop working? The gaps change at powers of two, so let's look there.
>
> At two to the forty-fifth, about thirty-five trillion dollars, the gap is under a cent: one hundred and twenty-eighth of a dollar. Cents are no longer exact, but different cent amounts still land on different doubles.
>
> At two to the forty-sixth, about seventy trillion dollars, the gap is one sixty-fourth of a dollar, a cent and a half. Now neighbouring cent amounts can land on the same double. Add a cent, and the result snaps to the nearest tick, which is a cent and a half away.
>
> And at two to the forty-seventh, about a hundred and forty trillion dollars, the gap is over three cents. Adding one cent doesn't even reach halfway to the next tick, so the sum rounds right back to where it started. The balance plus a cent equals the balance.
>
> You probably don't have seventy trillion dollars. But the window is the same wherever your numbers live. Count in a currency with very small units, or keep amounts in thousandths, or add up the transactions of a large bank for a year, and those sixteen digits get used up much sooner than you'd think. And as we're about to see, there's a much smaller float that runs out of room far, far earlier.

### 2.6 Thirty-two bits · ≈ 1:13

**Visual.** [V2.6a] The 64-box strip shrinks to 32 boxes: 1 sign, 8 exponent, 23 fraction,
plus the implicit 1 for "24 bits". [V2.6b] Code panel q02-03; the console prints the five
prices. The stored values line up beside the typed ones; the extra digits glow `RED`, and the
$1,000,000.01 row loses its cent. [V2.6c] A float line around $131,072: ticks spaced
"1/64 = $0.015625", with cent marks in `GOLD` falling between them. [V2.6d] Four small icons
labelled "graphics cards and ML pipelines", "some database REAL columns", "binary file
formats", "game economies", each with a "float32" tag.

**On screen**

```python
def float32(x):
    return struct.unpack("f", struct.pack("f", x))[0]
```

```output
$     1,234.56  stored as 1,234.56005859375
$    65,536.01  stored as   65,536.0078125
$   131,072.01  stored as   131,072.015625
$   249,999.99  stored as   249,999.984375
$ 1,000,000.01  stored as      1,000,000.0
float32 gap at $131,072: 0.015625
float64 gap at $131,072: 2.9103830456733704e-11
```

**QR q02-03** appears at [V2.6b], 8 seconds. Caption: "q02-03 · A house price in 32 bits".

> Doubles have a little sibling: the single-precision float, thirty-two bits in all. One sign bit, eight exponent bits and twenty-three fraction bits, so twenty-four bits of precision instead of fifty-three. Roughly seven significant decimal digits.
>
> Seven digits doesn't go far. The code in the corner squeezes prices through a thirty-two-bit float and reads them back. Twelve hundred dollars picks up some noise. At sixty-five thousand, even the cents come back wrong: one cent returns as about three quarters of a cent. And at one hundred and thirty-one thousand and seventy-two dollars, which is two to the seventeenth, the gap between neighbours reaches one sixty-fourth of a dollar. From there on, a thirty-two-bit float can't tell cents apart. By a million dollars, the gap is so wide the cent simply vanishes.
>
> For comparison, a double at the same price has a gap of about three hundredths of a billionth.
>
> You might think nobody would store money in a thirty-two-bit float. But they show up in surprising places: data pipelines built for graphics cards and machine learning, which favour them for speed, some database columns declared as real, binary file formats, game economies. Anywhere a number passes through one of those, the whole pipeline is only as precise as its narrowest pipe.

### 2.7 Round to nearest, ties to even · ≈ 1:07

**Visual.** [V2.7a] The float line with two ticks. Above it, an exact result is drawn as a
`YELLOW` diamond between them; an arrow snaps it to the nearer tick. [V2.7b] A label lists
the operations that obey this rule: "+ − × ÷ √". [V2.7c] The diamond moves to exactly halfway.
The two ticks show their last bits, `…0` and `…1`; the arrow snaps to the `…0` tick, labelled
"even". [V2.7d] The episode 1 picture returns briefly: stored 0.1 plus stored 0.2 landing on
a halfway point and snapping up to the even tick. [V2.7e] A stack of many small `RED` error
slivers, each at most half a gap, piles up into a visible bar: "each step is tiny; steps add up".

> Every arithmetic operation on doubles follows one simple promise. Addition, subtraction, multiplication, division and square root all give you the exact answer, rounded to the nearest double. As if the computer did the arithmetic perfectly, with infinitely many digits, and then rounded once at the end.
>
> When the exact answer falls precisely halfway between two doubles, the tie goes to the one whose last bit is zero: the even one. That's what happened with zero point one plus zero point two in the last episode. The exact sum fell on a halfway point, and the even neighbour happened to be the one above.
>
> Rounding to even sounds fussy, but there's a reason for it. If ties always went up, then over millions of operations the errors would drift upward. Sending half the ties up and half down keeps them balanced. We'll see the same idea used deliberately, for money, in episode six.
>
> So each single operation is as good as it can possibly be: its error is at most half a gap. The trouble is that a program doesn't do one operation. It does millions. And each one can add its own half-gap.

### 2.8 What print hides · ≈ 1:01

**Visual.** [V2.8a] Code panel q02-04, console beside it. `print(0.1)` prints `0.1`; then the
20-place version prints with the tail `555` in `RED`. [V2.8b] The float line around 0.1 shows
the tick's "catchment" region (from episode 1). "0.1" sits inside it as the shortest name.
[V2.8c] `1.1 * 3` prints `3.3000000000000003`; on the float line, the product lands one tick
right of the tick named "3.3", whose catchment doesn't contain it. [V2.8d] The refund lines:
a receipt shows +$0.10, +$0.20, −$0.30, total "5.551115123125783e-17". [V2.8e] The receipt
flips to a customer statement; the balance line reads "$-0.00", the minus sign circled in `RED`.

**On screen**

```python
refund = 0.10 + 0.20 - 0.30          # should be exactly zero
print("refund          ->", refund)
balance = -refund                    # the same sliver, owed the other way
print("rounded         ->", round(balance, 2))
print("on a statement  ->", f"${balance:.2f}")
```

```output
print(0.1)      -> 0.1
20 places       -> 0.10000000000000000555
1.1 * 3         -> 3.3000000000000003
3.3 == 1.1 * 3  -> False
refund          -> 5.551115123125783e-17
rounded         -> -0.0
on a statement  -> $-0.00
```

**QR q02-04** appears at [V2.8a], 8 seconds. Caption: "q02-04 · What print hides".

> We saw last time that print is polite. Let's look a little closer at how polite.
>
> Python prints the shortest decimal that leads back to exactly the same double. For zero point one, that's zero point one. Ask for twenty decimal places, and the truth peeks out: a string of zeros, then five, five, five.
>
> One point one times three lands one tick away from the double for three point three. Its shortest name has to be different, so print has no choice but to show you three point three, then fourteen zeros, then a three.
>
> And here's one that ends up on real statements. Ten cents plus twenty cents, minus thirty cents, should be nothing. It's actually a tiny positive sliver. Flip its sign, the way a balance owed in the other direction would, and round it to cents. You get zero, but a negative zero. Doubles keep a sign even on zero, and formatting faithfully prints it. Minus zero dollars and zero cents. Customers do notice that, and it's one of the friendlier ways these slivers show themselves.

### 2.9 Recap and challenge · ≈ 1:08

**Visual.** [V2.9a] A recap column builds: "64 bits = sign + exponent + 52 fraction bits (+1 implied)"
→ "same number of doubles between every power of two" → "gaps double as numbers double" →
"64-bit floats lose cents near $70 trillion; 32-bit near $131,072" → "every operation rounds
to nearest, ties to even" → "print shows the shortest name, not the value". [V2.9b] The
challenge: q02-05's code and output. [V2.9c] QR wall: q02-01 to q02-05 for 10 seconds.
[V2.9d] Teaser: a gold cent drops into a jar, a counter races to a million, and the total
display flickers in its last digits.

**On screen**

```python
AMOUNT = 0.01

power = 0
while 2.0 ** power + AMOUNT != 2.0 ** power:
    power += 1
print(f"2**{power} = ${2.0 ** power:,.0f}: adding {AMOUNT} does nothing")
```

```output
2**47 = $140,737,488,355,328: adding 0.01 does nothing
```

**QR q02-05** appears at [V2.9b], 10 seconds. Caption: "q02-05 · Challenge: when a cent disappears".

> Let's take stock. A double is a sign, an exponent and fifty-three significant bits: scientific notation in base two. The bits are a sliding window, so every doubling of a number doubles the gap to its neighbours. A sixty-four-bit double loses its grip on cents around seventy trillion dollars; a thirty-two-bit float, around a hundred and thirty-one thousand. Every operation rounds to the nearest double, with ties going to even. And print shows you the shortest name of a number, not the number itself.
>
> Here's a challenge. The code in the corner looks for the first power of two where adding a cent changes nothing, and finds two to the forty-seventh. Change the amount. Try a thousandth of a dollar. Try a whole dollar. Try five cents. Before you run each one, predict the power of two you'll get. Hint: the answer depends on when the amount is no more than half a gap.
>
> Next time, we leave the inside of a double and go looking for trouble: the everyday situations where these tiny errors are most likely to turn into wrong answers.

## Fact check before recording

- 2.5: at 2⁴⁶, adding 0.01 gives 2⁴⁶ + 1/64 (a cent and a half): verify with
  `python3 -c "x=2.0**46; print(x+0.01-x)"` (prints 0.015625).
- 2.3: there are 2⁵² doubles in [1, 2) and in [2, 4); a double carries 15–17 significant
  decimal digits (15 always survive a decimal → double → decimal round trip; 17 identify any double).
- 2.6: IEEE 754 single precision is 1 sign bit, 8 exponent bits, 23 fraction bits (24 bits of
  precision, about 7 decimal digits). "Some database columns declared as real": e.g. PostgreSQL's
  `real` is a 4-byte float; confirm for any database named on screen. The "where float32
  lurks" list is illustrative; don't name specific products without checking.
- 2.6: "about three hundredths of a billionth" = 2.91 × 10⁻¹¹ (from q02-03's output).
- 2.7: IEEE 754 requires +, −, ×, ÷ and square root to be correctly rounded; the default
  rounding mode is round to nearest, ties to even.
- 2.8: Python prints the shortest repr that round-trips since Python 3.1 (and 2.7).
- 2.8: `round(-5.55e-17, 2)` is `-0.0` and formats as `-0.00`, as q02-04 prints. Whether a
  particular billing system shows "-0.00" depends on its formatting code; keep the claim general.

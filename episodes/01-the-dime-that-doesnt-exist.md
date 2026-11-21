# Episode 1 · The dime that doesn't exist

| | |
|---|---|
| Part | The problem |
| Target length | about 14 min (segment estimates; set final timing from the narration audio) |
| Builds on | Reading a few lines of Python; fractions from school |
| QR codes | q01-01 … q01-05 |

## Learning goals

By the end, the viewer can:

- say which fractions have a finite decimal expansion, and which have a finite binary one;
- convert a fraction to binary by repeated doubling;
- explain why the double nearest one tenth is not one tenth, and roughly how far off it is;
- name the only four cent values from $0.00 to $0.99 that a double stores exactly;
- explain why `0.1 + 0.2` prints `0.30000000000000004` while `0.25 + 0.50` prints `0.75`.

## Script

### 1.1 Cold open · ≈ 0:52

**Visual.** [V1.1a] Black canvas. A gold dime icon labelled "10¢" and a gold coin
labelled "20¢" slide together; a plus sign appears between them. [V1.1b] The coins
dissolve into code: the q01-01 panel types out on the left. The console on the right
prints `a + b        = 0.30000000000000004`. The final `4` pulses `RED`. [V1.1c] The second
line prints `a + b == 0.30: False`; the word False glows `RED`. [V1.1d] Below, the
quarter-and-half lines print `0.75` and `True` in `GREEN`. Hold. [V1.1e] The dime icon
returns, alone, and a faint dashed outline replaces it, as if it had been erased.

**On screen**

```python
a = 0.10
b = 0.20
print("a + b        =", a + b)
print("a + b == 0.30:", a + b == 0.30)
```

```output
a + b        = 0.30000000000000004
a + b == 0.30: False
0.25 + 0.50 = 0.75
0.25 + 0.50 == 0.75: True
```

**QR q01-01** appears at [V1.1c], 8 seconds. Caption: "q01-01 · Ten cents plus twenty cents".

> Ten cents plus twenty cents. You know the answer, and so does every cash register you have ever used. But ask Python, and it says: zero point three, then fifteen zeros, then a four. Ask whether that equals thirty cents, and it says: no.
>
> Now try a quarter plus fifty cents. Seventy-five cents, exactly. And yes, they're equal.
>
> So the computer isn't simply bad at adding. Some amounts behave perfectly, and others don't. And by the end of this video, you'll be able to look at a price and predict which kind it is.
>
> Here's the surprising part. The trouble didn't happen when we added. It happened earlier, on the very first line, when we wrote ten cents. <break time="0.6s" /> Because your computer cannot store ten cents. Not approximately-badly. Not with a bug. It's simply impossible, in the kind of number Python uses by default. The dime doesn't exist.

### 1.2 A number you can't write down · ≈ 1:09

**Visual.** [V1.2a] "1/3" appears in `YELLOW`. An arrow leads to "0.3", then "0.33", then
"0.333", each new digit appearing with a soft click, trailing into "0.3333333…".
[V1.2b] A pie chart of one third; beneath it, three decimal place-value boxes labelled
"tenths", "hundredths", "thousandths". The pie is filled using 3 tenths, then 3
hundredths, then 3 thousandths; each time a tiny `RED` sliver of the third remains
unfilled, smaller and smaller, never gone. [V1.2c] Two columns appear. Left, `GREEN`,
"ends": 1/2 = 0.5, 1/4 = 0.25, 1/5 = 0.2, 1/8 = 0.125, 1/20 = 0.05. Right, `RED`, "repeats
forever": 1/3, 1/6, 1/7, 1/9, 1/12. [V1.2d] Each denominator is factored: 2, 2×2, 5,
2×2×2, 2×2×5 on the left; 3, 2×3, 7, 3×3, 2×2×3 on the right. The 3s and the 7 glow
`RED`. [V1.2e] The rule types itself: "Base ten can only finish fractions whose
denominators are built from 2s and 5s, because 10 = 2 × 5."

> Let's start with a number that everyone already knows you can't write down exactly. One third.
>
> In decimal, one third is zero point three three three, and so on, forever. You can write as many threes as you like, and you'll always be just a little short. Three tenths is short of a third. Thirty-three hundredths is still short. Every digit shrinks the gap, but no digit closes it.
>
> That's not because one third is a strange number. It's because of the place values we chose. Decimal digits count tenths, hundredths, thousandths: pieces made by cutting things into ten, and then ten again. One third asks you to cut something into three, and you cannot build a third out of tenths, however many you use.
>
> So which fractions do come out even? One half, one quarter, one fifth, one eighth, one twentieth. Factor their denominators and you only ever find twos and fives. And that's no coincidence: ten is two times five. Any fraction whose denominator is built only from twos and fives can be written with a finite number of decimal digits. Anything with a three, or a seven, or any other prime in the denominator, repeats forever.
>
> Hold on to that rule. We're about to apply it to a different base.

### 1.3 Counting in halves · ≈ 0:56

**Visual.** [V1.3a] A row of decimal place-value boxes (ones, tenths, hundredths)
morphs into binary place-value boxes: "1", "½", "¼", "⅛", "1/16", "1/32". [V1.3b] A bar
of length one sits above the boxes. Lighting the "½" box fills half the bar in `BLUE`;
lighting "¼" adds a quarter; the bar reads "0.11 in binary = ¾". [V1.3c] Examples
appear and fill their bars: 0.1₂ = ½, 0.01₂ = ¼, 0.011₂ = ⅜, 0.101₂ = ⅝. [V1.3d] The rule
from 1.2 returns with "ten" crossed out and replaced by "two": "Base two can only finish
fractions whose denominators are powers of 2." [V1.3e] The two columns from [V1.2c]
return, re-sorted: 1/2, 1/4, 1/8 stay `GREEN`; 1/5 and 1/20 slide over to the `RED`
column. A gold "1/10" label drops into the `RED` column with a thud.

> Computers don't count in tens. They count in twos. A binary number has a ones place, and then, after the point, a halves place, a quarters place, an eighths place, a sixteenths place. Each place is half the one before.
>
> So zero point one, in binary, means one half. Zero point zero one means one quarter. Zero point zero one one is a quarter plus an eighth: three eighths.
>
> Now apply the same rule as before. Decimal could only finish fractions built from twos and fives, because ten is two times five. Binary is built from two alone. So binary can only finish fractions whose denominators are powers of two: halves, quarters, eighths, sixteenths, and so on.
>
> One fifth? That has a five in the denominator. In binary, it repeats forever. One twentieth? Repeats forever. And one tenth, ten cents, a dime, which is one over two times five? <break time="0.6s" /> It has a five in it. In binary, one tenth is our one third. It never ends.

### 1.4 Long division by doubling · ≈ 1:07

**Visual.** [V1.4a] Code panel with q01-02's `binary_digits` function. [V1.4b] A table
with columns "value", "× 2", "bit", "keep". Row by row, starting at 1/10: 1/10 doubles to
2/10 (bit 0), 2/10 → 4/10 (0), 4/10 → 8/10 (0), 8/10 → 16/10 (1, keep 6/10), 6/10 → 12/10
(1, keep 2/10), 2/10 → 4/10 (0) … Each bit drops into a growing binary string at the top:
`0.00011…`. [V1.4c] When "keep 2/10" appears for the second time, the earlier row with
2/10 lights up in `YELLOW` and a looping arrow connects them. The bits `0011` are boxed
and the box starts stamping copies of itself along the string: `0.0 0011 0011 0011 …`.
[V1.4d] The console shows the q01-02 output. The `1/4` and `3/8` lines end in zeros, in
`GREEN`; the `1/10` and `1/5` lines repeat `0011`, in `RED`.

**On screen**

```python
def binary_digits(x, count):
    bits = ""
    for _ in range(count):
        x = x * 2
        bit = int(x)          # 1 if the doubled value reached a whole one
        bits += str(bit)
        x = x - bit           # keep only the fraction
    return bits
```

```output
1/4  = 0.01000000
3/8  = 0.01100000
1/10 = 0.00011001100110011001100110011001
1/5  = 0.00110011001100110011001100110011
```

**QR q01-02** appears at [V1.4d], 8 seconds. Caption: "q01-02 · Ten cents in binary".

> Let's watch it happen. There's a neat way to find the binary digits of any fraction, and it only needs doubling.
>
> Take your fraction and double it. If the result reached one or more, the next binary digit is a one, and you throw away the whole part. If it didn't, the next digit is a zero. Then repeat with whatever is left.
>
> Start with one tenth. Double it: two tenths. Less than one, so the first digit is zero. Double again: four tenths, another zero. Eight tenths, zero. Sixteen tenths: that's over one, so a one, and we keep the six tenths left over. Twelve tenths: another one, keep two tenths.
>
> And now look. Two tenths is a number we've already seen. From here, the doubling will walk exactly the same path again: four tenths, eight tenths, six tenths, two tenths. Round and round, forever. The digits zero, zero, one, one repeat without end.
>
> That's the code in the corner. It does exactly this doubling, using Python's Fraction type so the arithmetic is exact. A quarter and three eighths finish after a few digits, then nothing but zeros. One tenth and one fifth never finish.

### 1.5 Where the computer stops · ≈ 1:09

**Visual.** [V1.5a] The endless string `0.0001100110011…` scrolls right. A ruler
labelled "53 significant bits" slides along it, starting at the first `1`. Everything
past the ruler's end greys out and falls away. [V1.5b] At the cut, the kept bits end
`…1001` and the discarded tail is more than half, so they round up: a carry turns them
into `…1010`. A `BLUE` label: "rounded up". [V1.5c] Code panel q01-03; the console prints `Decimal(0.1)` with its
55 digits after the point. The first `1` is `YELLOW`; the long tail after
`0.10000000000000000` is `RED`. [V1.5d] The Fraction line appears; the denominator morphs
into `2^55`. [V1.5e] The error line: a tiny magnifier hovers over "5.551115123125783e-18",
and the label "about five and a half quintillionths of a dollar" appears beneath it.

**On screen**

```python
print("Decimal(0.1)  =", Decimal(0.1))
print("Fraction(0.1) =", stored)
print("denominator is 2**55:", stored.denominator == 2**55)
```

```output
Decimal(0.1)  = 0.1000000000000000055511151231257827021181583404541015625
Fraction(0.1) = 3602879701896397/36028797018963968
denominator is 2**55: True
stored - 1/10 = 1/180143985094819840
              ≈ 5.551115123125783e-18
```

**QR q01-03** appears at [V1.5c], 8 seconds. Caption: "q01-03 · What the computer really stores".

> A computer can't store infinitely many digits, so it stops. Python's floats, which programmers call doubles, keep fifty-three significant binary digits, counted from the first one. Everything after that is rounded off.
>
> So when you type zero point one, Python quietly finds the closest number it can build from those fifty-three bits, and stores that instead.
>
> How close is it? We can ask. Decimal of zero point one prints the stored value exactly, every digit. It starts off looking perfect: zero point one, then sixteen zeros. And then the junk appears: five, five, five, one, one, one, and on for another thirty-odd digits.
>
> Fraction shows the same number another way: a whole number over two to the fifty-fifth. That's the giveaway. Every double is secretly a fraction whose denominator is a power of two, which is exactly the kind of fraction that one tenth can never be.
>
> The stored value is too big by about five and a half quintillionths of a dollar. That's absurdly small. You will never see it on a bank statement. But it's not zero, and computers are very good at doing things a billion times.

### 1.6 The cent grid · ≈ 1:14

**Visual.** [V1.6a] A 10 × 10 grid of cells labelled $0.00 to $0.99 builds row by row
(the cent grid motif). All cells start `GREY`. [V1.6b] Code panel q01-04 on the left. As
the loop runs, the cells are tested in order; each fails and gets a tiny arrow, up in
`BLUE` or down in `RED`, except $0.00, $0.25, $0.50 and $0.75, which glow `GREEN`.
[V1.6c] The console prints `exact: [0, 25, 50, 75]` and the count line. The four green
cells pulse; "4 of 100" appears large. [V1.6d] The four green cells show their binary:
0.0, 0.01, 0.1, 0.11, with "¼ ½ ¾" labels. [V1.6e] The cells for 0.10, 0.20, 0.30 and 0.70
enlarge in turn as the last four output lines print; the arrows on 0.10 and 0.20 point up,
on 0.30 and 0.70 down.

**On screen**

```python
for cents in range(100):
    true_value = Fraction(cents, 100)
    stored = Fraction(cents / 100)       # the exact value of the double
    if stored == true_value:
        exact.append(cents)
```

```output
exact: [0, 25, 50, 75]
4 of 100 cent values are stored exactly
0.10 is stored above by 5.6e-18
0.20 is stored above by 1.1e-17
0.30 is stored below by 1.1e-17
0.70 is stored below by 4.4e-17
```

**QR q01-04** appears at [V1.6c], 8 seconds. Caption: "q01-04 · Which cents are exact?".

> So ten cents doesn't exist. What about the other cent values?
>
> Here's every amount from zero dollars to ninety-nine cents, laid out as a grid. The code tests each one: it compares the double that Python actually stores with the true fraction, cents over one hundred.
>
> And the answer is stark. Of the hundred possible cent values, exactly four are stored exactly. Zero. A quarter. A half. Three quarters. Every other amount, from one cent up to ninety-nine, is an approximation.
>
> You can predict that with the rule from earlier. A cent value is some number over one hundred, and one hundred is two times two times five times five. To lose those fives, the numerator has to cancel them, which means it must be a multiple of twenty-five. Zero, twenty-five, fifty, seventy-five. That's all of them.
>
> And the errors don't all lean the same way. Ten cents and twenty cents are stored slightly too high. Thirty cents and seventy cents are stored slightly too low. Each one is simply whichever neighbour happened to be nearest. Remember that, because it means errors can pile up, or partly cancel, depending on which amounts you happen to be adding.

### 1.7 Why 0.1 + 0.2 misses · ≈ 1:12

**Visual.** [V1.7a] The float line motif: a horizontal line, heavily zoomed, with three
tick marks near 0.3, evenly spaced. The middle region is labelled "0.3" with a `YELLOW`
diamond for the true value. The tick just left of the diamond is labelled "the double
for 0.3"; the next tick right is labelled "next double up". [V1.7b] Above, two short
`BLUE` bars, "stored 0.1" and "stored 0.2", each a hair longer than its true value, with
the excess shown as a thin `RED` tip. [V1.7c] The bars join end to end. Their right end
lands exactly halfway between the two ticks; a `YELLOW` bracket shows the two equal
distances. [V1.7d] An arrow snaps the sum to the right-hand tick. A label: "a tie: round
to even". [V1.7e] The two ticks are labelled with the values Python prints for them:
`0.3` on the left, `0.30000000000000004` on the right. A `RED` "≠" appears between the
sum and the tick for 0.3. [V1.7f] Contrast: 0.25 and 0.50 as `GREEN` bars with no red tips
join exactly at 0.75, which sits on a tick.

> Now we can see what went wrong in the very first example.
>
> Here's a close-up of the number line near zero point three. These tick marks are the only values a double can hold around here. The true zero point three falls between two of them. Python stores the nearer one, just below, and that's what you get when you type zero point three.
>
> Now add the stored versions of ten cents and twenty cents. Both of them are a little too big, so their sum is a little too big as well. In fact, it lands exactly halfway between the double for zero point three and the next double up.
>
> When a result falls exactly between two doubles, the rule is to pick the one whose last bit is even, and here that happens to be the upper one. We'll meet that rule properly in the next episode.
>
> So the sum and the number you typed land on two different, neighbouring tick marks. They differ by one step on this line, about fifty-five quintillionths. Python prints the upper one as zero point three followed by fifteen zeros and a four, and equals equals, quite correctly, says they are different numbers.
>
> And a quarter plus a half? Both are stored exactly, so there's no error to add up. The sum lands right on a tick, the tick for seventy-five cents.

### 1.8 Why you rarely see it · ≈ 1:07

**Visual.** [V1.8a] The console prints `0.1` for `print(0.1)` (on screen as a bare line, not
from a snippet). Beside it, the long `Decimal(0.1)` value from q01-03 slides in for
comparison; a `YELLOW` bracket shows that printing chose the shortest digits that lead
back to the same tick on the float line. [V1.8b] On the float line, the tick for 0.1 has a
small "catchment" region around it; "0.1" is the shortest decimal inside that region.
[V1.8c] For the disclosure, "synthetic voice" appears under the narration line.

> If every one of these amounts is wrong, why doesn't Python print zero point one as fifty-five digits of junk?
>
> Because print is polite. It prints the shortest decimal that would lead back to exactly the same double. Zero point one is the shortest number whose nearest double is this one, so that's what you see. The error is still there. Print simply doesn't mention it, until an addition or a multiplication pushes the result onto a different tick, one whose shortest name is longer. That's what happened with zero point three, then fifteen zeros and a four.
>
> So the errors are usually invisible. That's what makes them dangerous. A total can look perfect on the screen, and still fail a comparison, or round the wrong way, or drift over a million additions. That's what the rest of this series is about.
>
> One more thing worth mentioning, while we're talking about things that aren't quite what they seem. The voice you're listening to is synthetic: text-to-speech built from a model of Curt Cox's voice. It reads names from code as ordinary English words, so some of them may sound different from the way programmers say them.

### 1.9 Recap and challenge · ≈ 1:05

**Visual.** [V1.9a] A recap column builds: "Decimal finishes fractions built from 2s and 5s"
→ "Binary finishes only powers of 2" → "1/10 repeats forever in binary" → "A double keeps 53
bits" → "Only 4 of 100 cent values are exact". [V1.9b] The challenge: q01-05's code and
its output, `8 of 1000 are exact`, with the eight values glowing `GREEN` on a thin strip of
1,000 cells. [V1.9c] QR wall: q01-01 to q01-05 for 10 seconds. [V1.9d] Teaser: the float
line slides right and its ticks spread apart, one gap at a time, until a label reads
"gap > 1¢".

**On screen**

```python
STEPS = 1000
exact = [n for n in range(STEPS) if Fraction(n / STEPS) == Fraction(n, STEPS)]
print(len(exact), "of", STEPS, "are exact:", exact[:10])
```

```output
8 of 1000 are exact: [0, 125, 250, 375, 500, 625, 750, 875]
```

**QR q01-05** appears at [V1.9b], 10 seconds. Caption: "q01-05 · Challenge: other denominators".

> Let's take stock. In decimal, only fractions built from twos and fives come out even. In binary, only powers of two do. One tenth has a five in it, so in binary it repeats forever, and a double, which keeps fifty-three bits, has to round it off. Of the hundred cent values, only four survive that rounding exactly. Every other price you have ever typed into a program was stored as a very close approximation.
>
> Here's a challenge. Some systems price things in thousandths of a dollar. The code in the corner counts how many of those thousand amounts are exact. There are eight: the multiples of one eighth. Before you change the number of steps, predict the answer. Try three. Try sixty-four. Try one thousand and twenty-four. Try a hundred thousand. If you can predict every one, you've understood this episode.
>
> Next time, we open up a double and look inside: the sign, the exponent and the fifty-three bits. And we'll find out why the gaps between doubles grow as numbers get bigger, until one day, a balance can't even hold its cents.

## Fact check before recording

- 1.7: the exact sum of the stored 0.1 and 0.2 lies exactly halfway between the double for
  0.3 and the next double up, and round-half-to-even selects the upper one; the two
  doubles differ by one unit in the last place, 2⁻⁵⁴ ≈ 5.55 × 10⁻¹⁷ ("about fifty-five
  quintillionths"). Verified with:
  `python3 -c "from fractions import Fraction as F; s=F(0.1)+F(0.2); print(s-F(0.3)==F(0.1+0.2)-s)"`
  (prints True) and `math.ulp(0.3)`.
- 1.5: "zero point one, then sixteen zeros" — `Decimal(0.1)` is 0.1, sixteen zeros, then
  55511…; matches q01-03's output.
- 1.8: `print(0.1)` shows `0.1` (shortest round-trip repr, Python 3.1 and later).
- 1.8: confirm the narration voice before generating, and keep the disclosure wording
  in step with README.md, "How this series was made".

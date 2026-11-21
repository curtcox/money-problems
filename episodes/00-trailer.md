# Episode 0 · Trailer: Ten cents that don't exist

| | |
|---|---|
| Track | – |
| Target length | about 1.5 min |
| Builds on | Nothing |
| QR codes | q00-01 |

## Script

### 0.1 Four surprises · ≈ 0:38

**Visual.** [V0.1a] Black canvas. A console panel types the first line of q00-01 and
its result appears: `0.30000000000000004`. The trailing `4` pulses `RED`. [V0.1b] Hard
cut: a gold cent icon drops into a jar, then again and again, faster, until a counter
reads "1,000,000 cents". The console prints `10000.000000171856`; the tail after
`10000.` glows `RED`. [V0.1c] Hard cut: a price tag reading "$1.15" slides into a box
labelled "× 100, keep the whole part"; out comes "114¢". A single penny rolls off the
right edge of the frame. [V0.1d] Hard cut: `round(2.675, 2)`; the console prints `2.67`.
A small question mark sits over the 7.

**On screen**

```output
0.10 + 0.20         = 0.30000000000000004
a million cents     = 10000.000000171856
int(1.15 * 100)     = 114
round(2.675, 2)     = 2.67
```

**QR q00-01** appears at [V0.1d], 8 seconds. Caption: "q00-01 · Four surprises".

> Ten cents plus twenty cents. <break time="0.5s" /> Zero point three, then fifteen zeros, then a four.
>
> Add one cent to a total, a million times. You should have exactly ten thousand dollars. You have ten thousand dollars and a sliver.
>
> Turn a dollar fifteen into cents, the way a lot of real code does it, and you get one hundred and fourteen. <break time="0.4s" /> A cent just walked away.
>
> And round two point six seven five to two places. <break time="0.4s" /> Two point six seven.
>
> None of these is a bug in Python. You would get the same answers in JavaScript, Java, C, and almost everywhere else. Scan the code in the corner and try them yourself.

### 0.2 The series · ≈ 0:39

**Visual.** [V0.2a] The title "Money Problems" writes itself, with the subtitle "why
floating point can't count your cents". [V0.2b] A fast montage of the series' recurring
visuals, each with its episode number: the cent grid lighting four green cells (1), a
number line whose ticks spread apart as it slides right (2), a risk map with a red
hotspot (3), a ledger whose balance scale tips by one cent (4), a row of language names
all printing the same digits (5), a number line with eight rounding arrows (6), a penny
sliced into thin slivers dropping into a hidden jar (7), a $100 bill splitting into three
stacks with one stray penny (8), a checklist ticking itself (9), and a decimal sign
cracking under a "1/3" (10). [V0.2c] End card: "Episode 1 · The dime that doesn't exist".

> In this series, we'll find out why. Why your computer cannot store ten cents, and what it stores instead. Where that tiny error turns into real money, and what it costs when it does. Why nearly every programming language gives the same strange answers.
>
> Then we'll get practical. How rounding really works, and why it's a policy rather than a fact of arithmetic. What the movie Office Space got right, and wrong, about fractions of a penny. How to split a bill so that it always adds up. And how to handle money correctly, including the ways the usual fixes still go wrong.
>
> It starts with one small coin, and one simple question. <break time="0.5s" /> Why doesn't ten cents exist?

## Fact check before recording

- 0.1: "the same answers in JavaScript, Java, C": `0.1 + 0.2` prints 0.30000000000000004
  in JavaScript and Java (C needs `%.17g`; episode 5 shows each). The analogous
  operations give the same results: `Math.trunc(1.15 * 100)` is 114 and
  `(2.675).toFixed(2)` is "2.67" in JavaScript. Verified with Node.

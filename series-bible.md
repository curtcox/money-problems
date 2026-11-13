# Series bible

The plan for **Money Problems**: what each episode teaches, the visuals that recur, the
house style, and the facts the scripts rest on. Scripts follow the format in
[README.md](README.md), "Reading a script".

## The arc

Part 1, **The problem** (episodes 1–5): why a computer can't store ten cents, how a
double is built, where the error shows up, what it costs, and why every mainstream
language behaves the same way.

Part 2, **Living with it** (episodes 6–10): rounding as a deliberate policy, the
fractions-of-a-penny scheme from *Office Space*, splitting money so it always adds up,
how to do money right, and how the standard fixes still go wrong.

The one sentence the whole series earns: **floats are for measuring; money is counted.**
Episode 10 says it out loud; earlier episodes set it up without stating it.

## Recurring visuals

Build these once (as reusable Manim helpers) and reuse them across episodes, so the
viewer recognises them.

1. **The cent grid.** A 10 × 10 grid of the hundred cent values $0.00 to $0.99. Exact
   values glow `GREEN` (only 0.00, 0.25, 0.50 and 0.75). Every other cell carries a tiny
   arrow, up (`BLUE`) when the stored double is above the true value and down (`RED`)
   when it is below. Introduced in episode 1; returns in 2, 3 and 10.
2. **The float line.** A horizontal number line whose tick marks are the representable
   doubles. The true value is a `YELLOW` diamond; an arrow snaps it to the nearest tick.
   Zooming in reveals ever-finer ticks; sliding right makes them spread apart. Introduced
   in episode 1 (segment 1.7), developed in episode 2.
3. **The ledger.** A two-column T-account (debits, credits) with a balance-scale icon above
   it. When the columns differ by a cent, the scale tips and the difference glows `RED`.
   Used in episodes 4, 7, 8 and 9.
4. **The receipt.** A paper receipt strip with line items, subtotal, tax and total, in a
   monospaced font. Used wherever line items and totals disagree (3, 4, 6, 8).
5. **The penny.** A plain stylised coin marked "1¢" (no real coin design, no national
   symbols). A penny cut into slices stands for "fractions of a cent" (6, 7, 8).
6. **Code and console.** Code panel (monokai `Code` mobject, left) and console panel
   (right or below) showing the exact printed output. The console types out line by line.

Colour roles: `BLUE` stored values, `YELLOW` pointer and true values, `GREEN` exact or
correct, `RED` error or lost money, `GOLD` money itself, `GREY` scaffolding.

## House style for scripts

- Follow episode 1 exactly for structure: title line, the published-video line left out
  until published, the metadata table, **Learning goals**, `## Script`, segments
  `### N.M Title · ≈ m:ss`, then `## Fact check before recording`.
- 8–11 segments; 1,600–2,100 narrated words (about 11–15 minutes at 145 words per
  minute); five QR codes. The last segment is always "Recap and challenge", ends with a
  QR wall [Vn.xc] and a one-line teaser for the next episode (episode 10, the finale, ends
  with a series recap and a farewell instead).
- Every segment has a **Visual.** paragraph with shot ids `[Vn.ma]`, `[Vn.mb]` ….
  Visuals carry the explanation: describe exactly what moves, what is highlighted, and
  what the numbers on screen are.
- Narration: warm, curious, plain words, second person. Short sentences. No symbols:
  write "zero point one", "two to the fifty-third", "times", "equals equals" only when
  the code itself matters. Spell out ambiguous numbers. Describe long decimals instead of
  reading them. Read Python in words ("Decimal of the string zero point one").
- Every number the narration states either comes from a snippet's recorded output or is
  listed under **Fact check before recording**. Don't round a number the snippet prints
  unless you say "about".
- Never claim something is true of "all" languages, banks or regulations unless it is;
  prefer "most", "typically", "in Python". Real incidents, films, laws and prices are
  stated carefully and listed in the fact check.
- `**On screen**` blocks: ` ```python ` excerpts must be lines from one snippet of the same
  episode (the checker enforces this; drop comments or reorder only by cutting whole
  lines). ` ```output ` blocks must be lines the episode's snippets print. Other languages
  use their own fence (` ```javascript `, ` ```java `, ` ```c `, ` ```sql ` …) and aren't
  checked, so verify them by hand (episode 5).
- QR cue format: `**QR q03-02** appears at [V3.4b], 8 seconds. Caption: "q03-02 · Title".`
  The caption title must equal the snippet's header title.

## Snippet rules

- One file per QR code: `snippets/epNN/MM-slug.py`, first line
  `# Money Problems · qNN-MM · Title`. The second and third lines may be comments that tell
  the viewer what to try. Keep the title short (it is also the on-screen caption).
- Python standard library only (`decimal`, `fractions`, `math`, `struct`, `json`, `random`
  with a fixed seed …). No `numpy`, no network, no `input()`, no files, no `sqlite3`.
- Deterministic output: seed any randomness, never print sets of strings, ids, times or
  platform details.
- Short: under about 25 lines of code and 1,500 bytes, under 1 second natively, at most
  about 25 lines of output. Python Online stops an Auto-run after 5 seconds and Pyodide
  is slower than native Python.
- Print labelled results (`print("0.1 + 0.2 =", 0.1 + 0.2)`) so the console reads well on
  screen. Align columns with format specs where a table helps.
- Each episode's last snippet is a challenge: it runs as written and prints something,
  and comments say what to change.
- Since Python 3.12, built-in `sum()` of floats uses compensated summation, so it hides
  order-of-addition effects. Use an explicit `total += x` loop to show them.
- Decimal arithmetic still rounds to the context's 28 significant digits; quantize
  intermediate amounts before summing many of them.
- After writing or changing a snippet: `python3 tools/check_snippets.py --record epNN`,
  read the `.out` file, then use only those numbers in the script.

## Office Space

Episode 7 discusses the 1999 film *Office Space* (written and directed by Mike Judge) and
its explicit nod to *Superman III* (1983). Commentary and criticism only:

- No film clips, stills, posters, logos, character likenesses or soundtrack. Visuals are
  our own diagrams (pennies, ledgers, code).
- Name the film and characters factually. Paraphrase the plot; quote at most a few words.
- Thumbnail and title may name the film in text; no film imagery.

## Episode briefs

The briefs below are the plan each script follows. Numbers marked ✓ were verified by
running Python 3; others go in that episode's fact check.

### 0 · Trailer: Ten cents that don't exist (≈ 1.5 min, 1 QR)

Rapid cold open over four one-liners (q00-01): `0.1 + 0.2` (0.30000000000000004 ✓),
adding one cent a million times (10000.000000171856 ✓), `int(1.15 * 100)` (114 ✓),
`round(2.675, 2)` (2.67 ✓). Then the promise: why, where, what it costs, why every
language does it, *Office Space*, and how to do it right. Episode list as a quick
montage of the motifs.

### 1 · The dime that doesn't exist

Goal: the viewer can explain why 1/10 has no finite binary expansion, and that only four
of the hundred cent values are stored exactly.

Segments: cold open on 0.1 + 0.2 · one third in decimal (which fractions terminate in base
ten: denominators built from 2s and 5s) · binary place values (halves, quarters, eighths;
only denominators that are powers of two terminate) · long division of 1/10 in binary by
doubling (0.0 0011 0011 0011 …) · chopping at 53 significant bits: stored value of 0.1 is
0.1000000000000000055511151231257827021181583404541015625 ✓ = 3602879701896397 / 2⁵⁵ ✓
· the cent grid: exact cents are 0, 25, 50, 75 ✓ · why 0.1 + 0.2 lands one tick above
0.3's double (float line) · why printing usually hides it, plus the synthetic-voice
disclosure · recap and challenge (thousandths: 8 of 1,000 are exact ✓, the multiples of
0.125).

Snippets: q01-01 Ten cents plus twenty cents · q01-02 Ten cents in binary · q01-03 What
the computer really stores · q01-04 Which cents are exact? · q01-05 Challenge: other
denominators.

### 2 · Inside a double

Goal: the viewer can describe a double as sign, exponent and 53-bit significand, explain
why the gaps between doubles grow with magnitude, and say when a balance loses its cents.

Segments: cold open: a $131,072.01 house price stored in a 32-bit float becomes
131072.015625 ✓ · scientific notation in binary: 1 sign bit, 11 exponent bits, 52 stored
fraction bits plus an implicit leading 1; 0.1 is `0x3fb999999999999a`, `float.hex` gives
`0x1.999999999999ap-4` ✓ · same number of doubles in every doubling interval (2⁵² between
1 and 2, and between 2 and 4, twice as far apart) · the gap table, `math.ulp`: 1 → 2.2e-16,
one million → 1.16e-10, one trillion → 0.000122, one quadrillion → 0.125, ten
quadrillion → 2.0 ✓ · past 2⁴⁶ dollars (70,368,744,177,664) the gap is 1/64, more than a
cent; at 2⁴⁷ (140,737,488,355,328) adding a cent does nothing ✓ · single precision:
24 bits, the gap passes a cent at $131,072 (2¹⁷) ✓ (where float32 lurks: GPU and ML
pipelines, some database `REAL` columns, file formats) · every operation rounds to
nearest, ties to even; + − × ÷ and √ are correctly rounded · why printing is polite:
shortest round-trip repr (Python since 3.1), `f"{0.1:.20f}"`, `1.1 * 3` →
3.3000000000000003 · negative zero on a statement: a tiny negative residue rounded to
cents prints "-0.00" · recap and challenge: find the smallest power of two where adding a
cent changes nothing.

Snippets: q02-01 The bits of a double · q02-02 The gaps between doubles · q02-03 A house
price in 32 bits · q02-04 What print hides · q02-05 Challenge: when a cent disappears.

### 3 · Where it bites

Goal: the viewer can name the situations where float money errors are most likely and
spot them in code review.

Segments: cold open: adding a cent a million times gives 10000.000000171856 ✓ ·
accumulation (running totals, loops, row-by-row sums; error grows with the count) ·
equality and thresholds (`==`, `<=`, credit limits, free-shipping thresholds; find a cart
whose prices should total exactly $50.00 but whose float sum is just below) · converting
to integer cents with `int(x * 100)`: 573 of the 10,000 amounts $0.00–$99.99 come out a
cent short ✓, e.g. 0.29 → 28 ✓, 1.15 → 114 ✓ · multiplying by rates: tax, discounts,
interest, currency conversion; results near half a cent round the wrong way
(`round(1.005, 2)` is 1.0 ✓) · order of addition: the same amounts summed in a different
order give different totals (databases and parallel or distributed sums don't promise an
order) · crossing boundaries: JSON numbers, JavaScript front ends, CSV files read into
data frames, spreadsheets, APIs (`json.loads` gives floats unless `parse_float=Decimal`)
· very large and very small: huge totals, float32 columns, sub-cent unit prices times
large counts (cloud metering, per-message and per-request pricing) · recap: a risk map
(how often × how visible) and challenge.

Snippets: q03-01 A cent, a million times · q03-02 Free shipping, almost · q03-03 Dollars to
cents, the wrong way · q03-04 Same numbers, different order · q03-05 Challenge: find the
risky line.

### 4 · What goes wrong

Goal: the viewer can describe the concrete failures float money causes and why each one
costs real time or money.

Segments: cold open: a loan schedule prints a final balance of $0.00, but `balance == 0`
is False · ghost balances (tiny residues and negative zero; accounts that can't close,
statements for $0.00) · loops and branches (`while balance != 0` steps right past zero;
bounded demo) · reconciliation breaks (a float system and a Decimal system disagree by a
cent on amounts like 1.005; every break is a person investigating) · totals that don't
foot (lines vs total, report columns, auditors) · systematic bias (truncation always
moves money one way; sets up episode 7) · results that can't be reproduced (order-
dependent sums give different answers on different runs) · real stories: the Vancouver
Stock Exchange index (1982–83: recalculated thousands of times a day and truncated to
three decimals; it drifted from 1000 to about 524.811 before a recalculation put it near
1098.892 — a truncation story, not a floating-point one, and the script says so); the
Patriot missile failure at Dhahran, 25 February 1991 (time counted in tenths of a second
in a 24-bit fixed-point register; after about 100 hours the clock error was about 0.34
seconds; 28 soldiers died; not money, but the same "one tenth can't be stored" root;
handle respectfully, briefly) · recap and challenge.

Snippets: q04-01 Paid off, or not? · q04-02 The loop that skips zero · q04-03 Two systems,
one cent apart · q04-04 Truncation's one-way street · q04-05 Challenge: reconcile these.

### 5 · Every language, the same answer

Goal: the viewer understands that this is IEEE 754 arithmetic, not a bug in their
language, and knows which languages and databases offer decimal types.

Segments: cold open: `0.1 + 0.2` in Python, JavaScript, Java, C, Go, Rust, Ruby, Swift and
SQLite (verify each with the installed toolchain; C's `printf("%f")` shows 0.300000,
`%.17g` shows 0.30000000000000004) · same bits: 0.1 + 0.2 is `0x3fd3333333333334`, 0.3 is
`0x3fd3333333333333` (verify) · history: before IEEE 754-1985 manufacturers had their own
formats (IBM hexadecimal floating point, DEC VAX, Cray) and results differed between
machines; William Kahan led the design (Turing Award 1989); the Intel 8087 (1980)
implemented the draft; today every mainstream CPU does binary64 in hardware · different
makeup: the same double printed as shortest repr, 6 decimals, 15 significant digits
(spreadsheet display) and 17 significant digits · JavaScript has one number type until
BigInt (ES2020): integers above 2⁵³ lose precision, 2⁵³ + 1 becomes 2⁵³ · databases and
spreadsheets: SQL `FLOAT`/`REAL`/`DOUBLE PRECISION` are approximate, `DECIMAL`/`NUMERIC`
exact; Excel stores binary64 and shows 15 significant digits; the Excel 2007 display bug
(`=850*77.1` showed 100,000 instead of 65,535; the product is 65534.99999999999 ✓; fixed
by Microsoft in 2007) · the exceptions: COBOL's decimal fixed point (`PIC 9(7)V99`, packed
decimal), C# `decimal` (128-bit, base ten), Java `BigDecimal`, Python `decimal` and
`fractions`, Ruby `BigDecimal` and `Rational`, SQL `DECIMAL`; IEEE 754-2008 decimal
formats with hardware support on IBM POWER and z; C23 decimal floating types; JavaScript
has no built-in decimal (a proposal exists; check its stage) · why binary is the default
(speed, hardware, science measures rather than counts) · recap and challenge.

Snippets: q05-01 Same bits everywhere · q05-02 One value, four costumes · q05-03
JavaScript's integer ceiling · q05-04 What float really is (`sys.float_info`) · q05-05
Challenge: decimal arithmetic.

### 6 · Rounding is a policy

Goal: the viewer can choose a rounding mode deliberately, explain why `round(2.675, 2)`
is 2.67, and knows that where you round changes the answer.

Segments: cold open: `round(2.675, 2)` is 2.67 ✓ because the double is
2.67499999999999982236431605997495353221893310546875 ✓ · the modes, on a number line:
up, down, ceiling, floor, half-up, half-down, half-even, 05up (Python's `decimal`
names) · why half-even: half-up biases ties upward; simulate · two layers of rounding:
float already rounded the decimal you typed, so ties aren't ties (`round(0.125, 2)` is
0.12 because 0.125 is an exact tie and goes to even ✓; `round(0.375, 2)` is 0.38 ✓) ·
where to round: per line vs per invoice (three items at $0.99 with 8.25 % tax: per-line
tax totals $0.24, invoice-level $0.25 ✓; neither is wrong, the rule is) · cash rounding:
Canada stopped distributing the penny in 2013; cash totals round to the nearest five
cents, electronic payments don't · a rule written into law: the euro changeover
(Council Regulation (EC) No 1103/97): conversion rates with six significant figures,
never rounded or inverted, conversions between national currencies through the euro
(intermediate amount to at least three decimals), results rounded to the nearest cent
with halves rounded up. 100 DEM → FRF through the euro gives 335.38, a direct cross rate
gives 335.39 ✓ (rates 1.95583 DEM and 6.55957 FRF per euro) · recap and challenge.

Snippets: q06-01 Why 2.675 rounds down · q06-02 Eight ways to round · q06-03 The bias of
half-up · q06-04 Per line or per invoice · q06-05 Challenge: the euro triangle.

### 7 · Fractions of a penny: what Office Space got right and wrong

Goal: the viewer can separate the real arithmetic in the "fractions of a penny" scheme
from the movie logic, and sees where floating point would have made it stranger.

Segments: cold open: the setup, paraphrased (three programmers, a virus that moves
fractions of a cent per transaction into their account, the explicit *Superman III*
reference, a misplaced decimal point, far too much money far too fast) · where fractions
of a penny really come from (interest accrual: balance × annual rate ÷ 365 is rarely a
whole number of cents) · the scheme as code: truncate, keep the remainder · right: tiny
amounts × enormous volume is real money (back-of-the-envelope volume) · wrong: with
round-to-nearest the residues average to zero; only truncation leaves a one-sided pile ·
wrong: fractions don't vanish; double-entry bookkeeping makes every cent land in some
account, and reconciliation would find the skimming account · right: the decimal point
mistake is the most realistic part; scale and unit bugs (dollars vs cents, ×100) are
classic · where floats come in, which the film didn't need: `4.35 * 100` is
434.99999999999994 ✓, so a float version of the virus would see "0.99999999999994 of a
cent" · real salami slicing: the term; most penny-shaving legends are hard to verify ·
recap and challenge: write the reconciliation check that catches the virus.

Snippets: q07-01 Where fractions of a penny come from · q07-02 The virus, in a few lines ·
q07-03 Round, don't truncate · q07-04 The decimal point mistake · q07-05 Challenge: catch
the virus.

Fact check: the film's year, writer/director, the amount in the account (commonly
quoted as $305,326.13) and how long it took, the *Superman III* reference and its
character (Gus Gorman, played by Richard Pryor). Watch the film before recording.

### 8 · Splitting the penny

Goal: the viewer can split an amount into parts that always add up to the whole, and
knows the choices (who gets the extra cent) are policy.

Segments: cold open: $100 three ways is 33.33 × 3 = 99.99 ✓; float division gives
33.333333333333336 ✓ · the conservation law: parts must sum exactly to the whole ·
largest remainder: floor every share, hand the leftover cents to the largest remainders,
break ties deterministically · weighted splits (shares 1 : 2 : 3, percentages) ·
spreading a discount across line items so the lines still sum (and refunds of one item
later) · installments: $1,000 over 12 months (83.33 × 11 + 83.37, or 83.34 × 4 + 83.33 ×
8) · paradoxes: with weights 1 : 3 : 3, splitting 3 cents gives [1, 1, 1] but 4 cents
gives [0, 2, 2] ✓: the first person loses a cent when the pot grows; the Alabama paradox
(US House apportionment after the 1880 census) · recap and challenge: rotate who gets
the extra cent month to month.

Snippets: q08-01 A hundred dollars, three ways · q08-02 Largest remainder · q08-03
Spreading a discount · q08-04 Twelve payments · q08-05 Challenge: the Alabama paradox.

### 9 · Doing money right

Goal: the viewer leaves with a checklist they can apply on Monday.

Segments: cold open: the million-cent loop again with integers: exactly 1,000,000 cents
= $10,000.00 · rule 1: count, don't measure: integer minor units · rule 2: `Decimal` for
rates and from strings, with `quantize` and an explicit rounding mode · rule 3: round at
defined points with a defined mode · rule 4: carry the currency; minor units differ (ISO
4217: USD 2, JPY 0, KWD 3) · a small `Money` type that enforces 1–4 · rule 5: guard the
boundaries: JSON as strings or integer minor units (`parse_float=Decimal`), database
`DECIMAL`/`NUMERIC` not `FLOAT`/`REAL`, JavaScript front ends with integers or a decimal
library, `Intl.NumberFormat` for display only · rule 6: allocate, don't divide · rule 7:
test the invariants (sum of parts equals the whole, round trips) with random amounts ·
recap: the checklist card.

Snippets: q09-01 Counting cents · q09-02 Decimal, done right · q09-03 A tiny Money type ·
q09-04 JSON without floats · q09-05 Challenge: test the invariant.

### 10 · When the fixes fail

Goal: the viewer can spot the ways integer cents and decimals still go wrong, and knows
when floats are the right tool.

Segments: cold open: `Decimal(0.1)` imports the float's error, 55 digits of it ✓ ·
decimals are still finite: 1/3 to 28 digits, times 3 is 0.9999999999999999999999999999 ✓;
precision contexts · mixing types: Python raises `TypeError` for `Decimal + float` (good);
Java's `new BigDecimal(0.1)` has the same trap as `Decimal(0.1)` · integer cents: unit
mix-ups (×100, the *Office Space* callback); 32-bit overflow at 2,147,483,647 cents =
$21,474,836.47 ✓; JavaScript's safe-integer limit is 9,007,199,254,740,991 cents, about
$90 trillion ✓ · minor units that don't fit: JPY has none, KWD has three, bitcoin's
satoshi is 10⁻⁸, ether's wei is 10⁻¹⁸, so an unsigned 64-bit integer holds only about
18.45 ether in wei ✓ (Ethereum uses 256-bit integers) · exchange rates: inverse rates
aren't inverses; a round trip doesn't return the original amount · floats sneaking back
in (CSV readers that infer float columns, JSON in JavaScript, spreadsheet exports, ORMs
mapping to float, `sum` starting from a float) · when floats are fine: forecasts, risk
models, statistics, pricing models: anything that measures or estimates rather than
records; convert at the boundary between model and ledger · series recap: "floats are for
measuring; money is counted" · farewell and QR wall.

Snippets: q10-01 The Decimal(0.1) trap · q10-02 One third, to 28 places · q10-03 When
cents overflow · q10-04 Minor units that don't fit · q10-05 Challenge: there and back again.

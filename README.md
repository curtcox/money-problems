# Money Problems

Scripts for an explanatory video series about why floating-point numbers are the wrong
way to store money. It's built in the style of narrated math-explainer videos: one calm
narrator, a dark canvas, intuition before syntax, and every idea shown moving. Narration
is generated with ElevenLabs and graphics are built with Manim Community. QR codes open
the exact Python on screen in [Python Online](https://python.hashbin.page/), where
viewers can run it and change it.

This series is independent and isn't affiliated with 3Blue1Brown, Manim Community or any
film studio. Don't use 3Blue1Brown's name, logo or "pi creature" characters, or any film
footage, stills, posters or logos, in titles, thumbnails or graphics (see
[series-bible.md](series-bible.md), "Office Space").

## Audience

Working developers: people who write code for a living or for fun, have probably seen
`0.1 + 0.2` print something odd, and have never been shown why. No binary arithmetic is
assumed; every idea is built from scratch, visually. Each episode stands on its own but
builds on the ones before it.

## Episodes

| # | Title | Part | Target | QR codes |
|---|---|---|---|---|
| 0 | [Trailer: Ten cents that don't exist](episodes/00-trailer.md) | – | 1.5 min | 1 |
| 1 | [The dime that doesn't exist](episodes/01-the-dime-that-doesnt-exist.md) | The problem | 14 min | 5 |
| 2 | [Inside a double](episodes/02-inside-a-double.md) | The problem | 15 min | 5 |
| 3 | [Where it bites](episodes/03-where-it-bites.md) | The problem | 15 min | 5 |
| 4 | [What goes wrong](episodes/04-what-goes-wrong.md) | The problem | 15 min | 5 |
| 5 | [Every language, the same answer](episodes/05-every-language-the-same-answer.md) | The problem | 15 min | 5 |
| 6 | [Rounding is a policy](episodes/06-rounding-is-a-policy.md) | Living with it | 15 min | 5 |
| 7 | [Fractions of a penny: what Office Space got right and wrong](episodes/07-fractions-of-a-penny.md) | Living with it | 15 min | 5 |
| 8 | [Splitting the penny](episodes/08-splitting-the-penny.md) | Living with it | 14 min | 5 |
| 9 | [Doing money right](episodes/09-doing-money-right.md) | Living with it | 15 min | 5 |
| 10 | [When the fixes fail](episodes/10-when-the-fixes-fail.md) | Living with it | 15 min | 5 |

Topics that earned their own episode beyond the core questions: the anatomy of a
double (2), rounding modes and rounding rules (6), allocation (8), and the ways the
standard fixes go wrong (10). The plan, the recurring visuals, and the facts each
episode rests on are in [series-bible.md](series-bible.md).

## Reading a script

Each episode is a sequence of numbered segments (`### 3.4 Title · ≈ 1:30`). Inside a segment:

- **Visual.** paragraphs describe what the animator builds. Bracketed ids (`[V3.4a]`)
  name individual shots for the edit.
- **On screen** code blocks show code exactly as it should appear on screen.
  ` ```python ` blocks are always excerpts of the episode's QR snippets, so viewers can scan
  and find the same lines. ` ```output ` blocks are excerpts of what those snippets print.
  Code in other languages (episode 5) is on screen only; it has no QR code.
- **QR qNN-MM** lines say when to show a QR code and for how long.
- Lines starting with `>` are **narration**, the only text sent to ElevenLabs.
- Each episode ends with **Fact check before recording**: claims that the snippets don't
  prove, with where to confirm them.

Durations are estimates at 145 words per minute plus held visual beats.
`node tools/extract-narration.mjs` reports the narrated word count per segment.

## Voice and narration

- One narrator throughout: warm, curious, unhurried, speaking to one viewer ("you").
  The ManimOnline series used Curt Cox's own ElevenLabs voice ("Curt Cox 2"); confirm
  the voice before generating. Don't clone or imitate any other presenter or any actor.
- Narration is written to be spoken: code is read in plain words ("int of x times one
  hundred"), numbers are spelled out when they would be ambiguous, and symbols never
  appear. Long decimals are described, not read digit by digit ("zero point three, then
  fifteen zeros, then a four").
- `<break time="0.8s" />` marks a deliberate pause (honoured by ElevenLabs v2, Turbo and
  Flash models; use `--strip-breaks` for others and add the silence in the edit).
- Generate each segment separately so visual timing can be adjusted per segment.
- Load [`pronunciations.pls`](pronunciations.pls) as an ElevenLabs pronunciation
  dictionary. It uses alias rules, which work on every model.

## Visual language

See [series-bible.md](series-bible.md) for the recurring motifs (the cent grid, the
float line, the ledger, the receipt). In short:

- **Canvas.** Manim's default near-black background, 16:9 at 1920×1080, 60 fps.
- **Colour roles.** `BLUE` for values as the computer stores them, `YELLOW` for whatever
  the narration is pointing at, `GREEN` for exact or correct, `RED` for errors and lost
  money, `GOLD` for money itself (coins, cents, totals), `GREY` for scaffolding.
- **Code panels.** Manim's `Code` mobject (monokai) on the left third, never more than
  about 14 lines; the line being discussed gets a yellow `SurroundingRectangle`. Program
  output appears in a console panel below or beside it, exactly as the snippet prints it.

## QR codes

Every QR code is a HashBin link: `https://python.hashbin.page/#<CID>`. Opening it loads
the snippet into Python Online and runs it. The CID is computed from the snippet's bytes,
so **the URLs in [`qr-links.md`](qr-links.md) are already final**, but they only resolve
after the payloads are uploaded. Each row also has a self-contained fallback link
(`?compressed=…`) that works with no upload; use it in video descriptions next to the
QR URL.

On screen:

- Bottom-right corner, at least 22 % of the frame height (about 240 px at 1080p), black
  on white with the full quiet zone. Never put a QR code over moving content.
- Hold each code for at least 6 seconds, with a caption above it: the QR id and the
  snippet title (for example "q03-02 · Free shipping, almost").
- Each episode ends with a "QR wall" of all its codes for 10 seconds, and every episode
  description lists the same URLs in order.

Workflow:

1. Edit snippets in `snippets/epNN/`. Each starts with the header line
   `# Money Problems · qNN-MM · Title`, which is where the manifest gets its titles. Then:
   ```bash
   python3 tools/check_snippets.py
   ```
   It runs every snippet, compares the output with the recorded `.out` file, and checks
   that every code and output block in the scripts is an excerpt of a snippet. After an
   intentional change, read the new output and record it with `--record`.
2. Regenerate the links (changing a single byte of a snippet changes its CID and QR code):
   ```bash
   node tools/qr-links.mjs --upload
   ```
   This writes `qr-manifest.json`, `qr-links.json`, `qr-links.md`, and exactly the files to
   upload to `build/hashbin-upload/`. Each file is the document Python Online's own
   **Save to HashBin** button stores for that snippet (Auto-run on, no Program input).
3. Drop the folder's contents on https://hashbin.org/upload, choose one long retention
   period for all of them (an expired payload breaks a printed QR code), and upload. Don't
   open and re-save the files: HashBin computes each CID from the raw bytes.
4. Confirm that everything resolves:
   ```bash
   node tools/qr-links.mjs --check
   ```
5. Open a few links on a phone, from a screen, to confirm they scan and run. The native
   check doesn't prove behaviour in Pyodide; the snippets avoid anything that differs.

## Production pipeline

1. **Narration.** `node tools/extract-narration.mjs` writes one text file per segment and a
   `cues.csv` cue sheet to `build/narration/`. Generate each segment's audio with
   ElevenLabs. (ManimOnline's `narrate.py` can be adapted to do this in one step.)
2. **Graphics.** Build Manim Community scenes from the **Visual** notes, one Scene per
   segment, timed to the measured narration. Where a shot reproduces a snippet, start
   from the snippet's code and output so the screen matches what the QR code opens.
3. **Publishing.** Each description ends with the episode's QR URLs (and fallbacks) and
   the disclosure block below.

## How this series was made

```text
How this series was made
Animation: Manim Community, from Python code in the series repository.
Scripts and code samples: Claude Opus 5.5, an AI model by Anthropic.
Direction: Curt Cox.
Narration: ElevenLabs text-to-speech, from a model of Curt Cox's voice.
Source: https://github.com/curtcox/money-problems

Text-to-speech reads names from code as ordinary English words, so the words you hear
may be pronounced differently than programmers would say them.
```

Episode 1, segment 1.8 says the same thing in narration. Keep the three in agreement.

## Files

- `episodes/` – the scripts.
- `series-bible.md` – the series plan, recurring visuals, house style and per-episode briefs.
- `snippets/epNN/` – one Python file per QR code, with its recorded output (`.out`).
- `qr-manifest.json`, `qr-links.json`, `qr-links.md` – generated ids, titles, CIDs and URLs.
- `pronunciations.pls` – ElevenLabs pronunciation dictionary.
- `tools/` – snippet checks, link generation and narration extraction.
  `tools/vendor/` holds lz-string 1.5.0 (MIT) for the fallback links.

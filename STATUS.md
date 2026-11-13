# Status

What has been done, what remains, and who did what. Agents: read this first and update it
before you finish (see [AGENTS.md](AGENTS.md), "Leaving the repo tidy").

Last updated: 2026-11-13.

## Where things stand

Pre-production writing is complete in draft: all eleven scripts and all 51 QR snippets
exist, and `tools/check_snippets.py` passes with 0 problems. Nothing downstream has
started: no fact-check items are confirmed, no HashBin payloads are uploaded, no narration
audio is generated, and no Manim code exists in the repository. There is no record yet of
the director reviewing the scripts.

## Episodes

Columns follow the pipeline in README.md. "Open" is the number of unconfirmed items in the
episode's **Fact check before recording** list (recount with the command in AGENTS.md).

| # | Episode | Script | Snippets | Open fact checks | Words | QR uploaded | Narration | Graphics | Edit | Published |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | Trailer | Draft | 1 ✓ | 1 | 229 | – | – | – | – | – |
| 1 | The dime that doesn't exist | Draft | 5 ✓ | 4 | 1,719 | – | – | – | – | – |
| 2 | Inside a double | Draft | 5 ✓ | 7 | 1,725 | – | – | – | – | – |
| 3 | Where it bites | Draft | 5 ✓ | 8 | 1,664 | – | – | – | – | – |
| 4 | What goes wrong | Draft | 5 ✓ | 5 | 1,740 | – | – | – | – | – |
| 5 | Every language, the same answer | Draft | 5 ✓ | 13 | 1,922 | – | – | – | – | – |
| 6 | Rounding is a policy | Draft | 5 ✓ | 12 | 1,716 | – | – | – | – | – |
| 7 | Fractions of a penny | Draft | 5 ✓ | 11 | 1,774 | – | – | – | – | – |
| 8 | Splitting the penny | Draft | 5 ✓ | 5 | 1,671 | – | – | – | – | – |
| 9 | Doing money right | Draft | 5 ✓ | 6 | 1,736 | – | – | – | – | – |
| 10 | When the fixes fail | Draft | 5 ✓ | 11 | 1,885 | – | – | – | – | – |

Script states: **Draft** (written, passes the checker) → **Reviewed** (director has read
and approved it) → **Locked** (fact checks closed, snippets frozen for QR upload).
Snippets ✓ means they run natively and match their recorded output; it does not mean they
have been tried in Python Online.

## Remaining

Roughly in pipeline order. Items marked *(director)* need Curt Cox's decision or account
access; an agent can prepare them but not finish them.

### Scripts

- [ ] Director review of each script; mark **Reviewed** in the table. *(director)*
- [ ] Close the 83 open fact-check items (counts per episode above). Most can be settled
      by running code or citing a primary source; some need the director:
  - [ ] Episode 5: run `0.1 + 0.2` with each installed toolchain (JavaScript, Java, C, Go,
        Rust, Ruby, Swift, SQLite) and confirm the on-screen output; check the TC39
        Decimal proposal's current stage.
  - [ ] Episode 7: watch *Office Space* and confirm film details (amount, timeline,
        characters, *Superman III* reference). *(director)*
  - [ ] Episodes 9 and 10: confirm error-message text and seeded output on Python 3.14
        in Python Online.
  - [ ] Historical and legal claims in episodes 4, 6 and 8 (Vancouver Stock Exchange,
        Patriot missile, Canadian penny, EU Regulation 1103/97, Alabama paradox).
- [ ] Lock each script once its fact checks are closed.

### Code samples and QR codes

- [ ] Open every fallback link in [qr-links.md](qr-links.md) in Python Online and confirm
      each snippet runs within the 5-second Auto-run limit and prints its `.out` exactly.
- [ ] Freeze snippets (after scripts are locked), then
      `node tools/qr-links.mjs --upload` and upload `build/hashbin-upload/` to
      hashbin.org with one long retention period. *(director: account and retention choice)*
- [ ] `node tools/qr-links.mjs --check` until every row is stored (it is rate-limited;
      be patient). As of 2026-11-13 the check reported payloads MISSING.
- [ ] Scan a few QR codes from a screen with a phone.

### Narration

- [ ] Confirm the ElevenLabs voice ("Curt Cox 2" was used for ManimOnline). *(director)*
- [ ] Load `pronunciations.pls` into ElevenLabs; listen for mispronounced code names and
      extend the dictionary.
- [ ] Generate audio per segment from `build/narration/` (`node tools/extract-narration.mjs`).
      Decide where the audio files live (not in this repository unless the director says so).
- [ ] Set final segment timings from the audio; update the "≈ m:ss" estimates.

### Graphics

- [ ] Decide where Manim code lives (this repository or a separate one) and record it here.
- [ ] Build the recurring visuals once as reusable helpers: cent grid, float line,
      ledger, receipt, penny, code-and-console panels (series bible, "Recurring visuals").
- [ ] Build each episode's scenes from its **Visual.** notes, one Scene per segment,
      timed to the narration, with QR codes per README "QR codes".

### Publishing

- [ ] Edit, thumbnails (no film imagery, no 3Blue1Brown branding), descriptions with QR
      URLs, fallback links and the disclosure block.
- [ ] After each episode is published, add its published-video line under the title, as
      the house style describes, and mark it Published here.

### Housekeeping

- [ ] Snippet size limit disagrees: series bible says under about 1,500 bytes,
      `check_snippets.py` enforces 2,000 (`MAX_BYTES`). Pick one.

## Decisions

Record decisions that later work depends on, with the date.

- 2026-11-12: Series structure fixed at trailer + ten episodes in two parts (The problem,
  Living with it); five QR codes per episode, one for the trailer.
- 2026-11-12: QR codes point at python.hashbin.page via HashBin CIDs, with lz-string
  fallback links in descriptions.

## Work log

Newest first. One line per session: date, who, what changed, what was left unfinished.

- 2026-11-13 · Claude · Added AGENTS.md, CLAUDE.md and this file to orient agents and
  track work. Ran the snippet checker (0 problems), regenerated links (no change) and
  narration counts. HashBin `--check` was rate-limited partway; payloads it reached were
  MISSING.
- 2026-11-12 · Claude, directed by Curt Cox · Wrote the series bible, all eleven scripts,
  51 snippets with recorded output, the tools, the pronunciation dictionary and the
  generated QR link files (commit 161bf60).

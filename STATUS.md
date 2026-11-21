# Status

What has been done, what remains, and who did what. Agents: read this first and update it
before you finish (see [AGENTS.md](AGENTS.md), "Leaving the repo tidy").

Last updated: 2026-11-20.

## Where things stand

Pre-production writing is complete in draft: all eleven scripts and all 51 QR snippets
exist, and `tools/check_snippets.py` passes with 0 problems. Graphics are built in draft:
`production/` holds Manim Community scenes for the trailer and all ten episodes, one Scene
per segment. Narration audio exists for every segment (ElevenLabs, "Curt Cox 2"), and every
episode renders and stitches at 480p15 with its soundtrack (`render.py N -ql`), each beat
placed by the audio's character timings. All 51 QR cards decode at 1080p (`check_qr.py`)
and every card stays up at least 8 s (`check_holds.py`). Not yet done: listening for
mispronunciations, 1080p renders, fact checks, HashBin upload, and director review of
scripts and scenes.

## Episodes

Columns follow the pipeline in README.md. "Open" is the number of unconfirmed items in the
episode's **Fact check before recording** list (recount with the command in AGENTS.md).

| # | Episode | Script | Snippets | Open fact checks | Words | QR uploaded | Narration | Graphics | Edit | Published |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | Trailer | Draft | 1 ✓ | 1 | 229 | – | ✓ | Draft | – | – |
| 1 | The dime that doesn't exist | Draft | 5 ✓ | 4 | 1,719 | – | ✓ | Draft | – | – |
| 2 | Inside a double | Draft | 5 ✓ | 7 | 1,725 | – | ✓ | Draft | – | – |
| 3 | Where it bites | Draft | 5 ✓ | 8 | 1,664 | – | ✓ | Draft | – | – |
| 4 | What goes wrong | Draft | 5 ✓ | 5 | 1,740 | – | ✓ | Draft | – | – |
| 5 | Every language, the same answer | Draft | 5 ✓ | 13 | 1,922 | – | ✓ | Draft | – | – |
| 6 | Rounding is a policy | Draft | 5 ✓ | 12 | 1,716 | – | ✓ | Draft | – | – |
| 7 | Fractions of a penny | Draft | 5 ✓ | 11 | 1,774 | – | ✓ | Draft | – | – |
| 8 | Splitting the penny | Draft | 5 ✓ | 5 | 1,671 | – | ✓ | Draft | – | – |
| 9 | Doing money right | Draft | 5 ✓ | 6 | 1,736 | – | ✓ | Draft | – | – |
| 10 | When the fixes fail | Draft | 5 ✓ | 11 | 1,885 | – | ✓ | Draft | – | – |

Script states: **Draft** (written, passes the checker) → **Reviewed** (director has read
and approved it) → **Locked** (fact checks closed, snippets frozen for QR upload).
Snippets ✓ means they run natively and match their recorded output; it does not mean they
have been tried in Python Online. Graphics **Draft** means every segment renders and was
reviewed on 480p contact sheets; it becomes **Final** after a 1080p render timed to the real
narration has been watched end to end.

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

- [x] Voice "Curt Cox 2" confirmed by the director (2026-11-20).
- [x] Audio generated for all 95 segments (`python3 tools/narrate.py N`, about 101,500
      characters) into `build/narration/audio/` (gitignored), with `durations.json`.
      `narrate.py` applies `pronunciations.pls` itself and skips unchanged segments, so a
      script edit regenerates only the segments it touches.
- [x] Segment timings in the scripts' headings set from the narrated renders.
- [ ] Listen for mispronounced code names and other slips; extend `pronunciations.pls` and
      re-run `narrate.py` for the affected segments. *(director: by ear)*

### Graphics

- [x] Manim code lives in this repository, `production/` (decision below).
- [x] Recurring visuals built once in `production/common.py`: cent grid, float line,
      ledger, receipt, penny, code and console panels (`motifs.py` is a contact sheet).
- [x] Each episode's scenes built from its **Visual.** notes, one Scene per segment, with
      QR cards and closing walls; all render at 480p15. `check_qr.py` decodes all 51 cards.
- [ ] Director review of the 480p renders (`build/episodes/epNN-480p15.mp4`). Departures
      from the Visual notes are listed in production/README.md, "Episode notes".
- [ ] Render each episode at 1080p (`render.py N`; hours per episode), watch it end to end,
      check that beats land on their phrases, then run `check_holds.py N 1080p60` and
      `check_qr.py --wall N`. (At 480p with narration, every card already holds 8 s.)
- [ ] Thumbnails (no film imagery, no 3Blue1Brown branding).

### Publishing

- [x] `tools/descriptions.py` writes each description (summary, chapters, QR URLs, the
      disclosure block) to `build/youtube/`; when fallback links would pass YouTube's 5,000
      characters they go to a pinned-comment file instead (episodes 3, 4, 6–10).
- [ ] Final edit and upload. *(director)*
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
- 2026-11-20: Manim scenes live in this repository under `production/`, following the
  ManimOnline video series' pipeline (render.py, narrate.py, credits card). No TeX: all
  text is `Text`. The disclosure now credits Claude with animation code and production
  tooling too (README and the credits card; segment 1.8's narration names no roles).

## Work log

Newest first. One line per session: date, who, what changed, what was left unfinished.

- 2026-11-20 · Claude, directed by Curt Cox · Generated narration for all 95 segments and
  re-rendered every episode at 480p15 with its soundtrack (trailer 1.4 min, episodes 9.3 to
  11.7 min). Fixed phrase matching across paragraph breaks, added `check_holds.py` and
  lengthened the 2.4, 5.5 and 9.1 QR holds to 8 s. Script headings now carry the measured
  segment lengths. Left: listening pass, 1080p renders, director review.
- 2026-11-20 · Claude · Built the production pipeline (production/common.py, render.py,
  credits.py, check_qr.py; tools/narrate.py, make_qr_svgs.py, descriptions.py) and Manim
  scenes for the trailer and all ten episodes; all render at 480p15 and all QR cards
  decode. Corrected the V1.5b note (0.1's kept bits end …1001 and round up to …1010) and
  the 6.5 fact-check wording (8.17¢). Reviewed every episode on contact sheets; fixed an
  overlapping label in 6.3 and a 7.1 icon that resembled a car badge. Left: narration audio,
  1080p renders, director review.
- 2026-11-13 · Claude · Added AGENTS.md, CLAUDE.md and this file to orient agents and
  track work. Ran the snippet checker (0 problems), regenerated links (no change) and
  narration counts. HashBin `--check` was rate-limited partway; payloads it reached were
  MISSING.
- 2026-11-12 · Claude, directed by Curt Cox · Wrote the series bible, all eleven scripts,
  51 snippets with recorded output, the tools, the pronunciation dictionary and the
  generated QR link files (commit 161bf60).

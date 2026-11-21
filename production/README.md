# Production graphics

Manim Community scenes for the series, one file per episode (`epNN.py`) and one Scene class
per script segment (`Segment_1_5` is segment 1.5, `Segment_4_10` is 4.10). Shot ids in
comments (`[V1.5b]`) match the **Visual.** notes in `../episodes/`. The trailer (`ep00.py`) is
the template; `motifs.py` is a contact sheet of the recurring visuals.

## Requirements

- Manim Community 0.22 (`manim --version`) and ffmpeg.
- **No TeX.** This machine has no `latex`, so never use `MathTex`, `Tex`, or a bare
  `Integer`/`DecimalNumber` (they call TeX). Use `Text` and `common.number(...)` for counters.
  Fractions and symbols are plain characters: `1/10`, `½`, `×`, `≈`, `2⁵³`.
- Fonts: Avenir Next for text and Menlo for code (both ship with macOS; override with
  `SERIES_FONT` / `SERIES_MONO`).
- QR matrices: `production/qr-matrices.json` (committed) comes from
  `python3 tools/make_qr_svgs.py`, which needs `segno`. Regenerate it whenever a snippet
  changes, after `node tools/qr-links.mjs`.
- QR decoding check only: a Python with `opencv-python-headless`.

## Rendering

```bash
python3 production/render.py 1 -ql          # quick 480p15 review of episode 1, stitched
python3 production/render.py 1 -ql 1.5 1.6  # only these segments (not stitched)
python3 production/render.py 1              # 1080p60 production render
python3 production/render.py 1 --stitch     # stitch segment videos already on disk again
```

Segment videos land in `build/media/videos/epNN/<quality>/`; the stitched episode, with the
credits card (`credits.py`) at the end, is `build/episodes/epNN-<quality>.mp4`. Set
`SEGMENT_LABELS=1` to burn the segment id and clock into the top-left corner for review.
To look at a render quickly, make a contact sheet:

```bash
ffmpeg -v error -y -i build/episodes/ep01-480p15.mp4 -vf "fps=1/4,scale=427:240,tile=5x8" -frames:v 1 sheet.png
```

## Timing

`common.Segment` sets each scene's length from its narration: words at 145 per minute plus
`<break/>` pauses, read from the episode script. Place beats with `self.at('phrase')`, which
waits until the narration starts saying that phrase (it raises if the phrase isn't in the
segment's narration), and end with `self.finish()`. `self.hold_until(fraction)` is the coarse
alternative.

After `tools/narrate.py` has generated audio, `build/narration/durations.json` holds the
measured lengths and each segment's sidecar holds ElevenLabs' character timings, so rendering
again fits every beat to the real voice without code changes. Pronunciation aliases are
applied to the spoken text, so don't pick an `at` phrase containing an aliased word (see
`pronunciations.pls`: JSON, SQL, IEEE, COBOL, ISO …).

## Conventions

- **Colour roles** (`common.py`): `STORED` blue, `FOCUS` yellow, `EXACT` green, `ERROR` red,
  `MONEY` gold, `SCAFFOLD` grey.
- **Recurring visuals** come from `common.py`, never redrawn per episode: `CentGrid`
  (`cent_grid`), `FloatLine`, `ledger` + `tip_scale`, `receipt`, `penny`/`coin`/`sliced_penny`,
  `jar`, `price_tag`, `code_panel` + `line_highlight`, and `Console` (`output_console`).
- **On-screen code and output come from the snippet files**: `snippet_lines`, `snippet_find`,
  `snippet_output`, `output_line`, `output_console`. Never type a snippet's code or output into
  a scene by hand; then the screen always matches what the QR code opens. Values the scripts
  compute but no snippet prints may be computed in the scene with Python (say so in a comment).
- **Monospaced text** is `MonoLine` (`code_text`): it keeps columns, and `line.part('4')`
  picks glyphs to colour. `Console.type_line(i)` types a line out; start from
  `console.background` on screen. Animating glyphs adds them to the scene on their own, so
  before transforming a typed console as a whole, `self.remove(*console.body.family_members_with_points())`
  and `self.add(console)` (or re-add the line), or a stale copy stays behind.
- **QR codes**: `qr_card(id)` bottom-right at 25 % of frame height, shown at the shot the
  script names and held at least 8 seconds, never over moving content (keep the bottom-right
  3.5 × 3 units clear while a card is up). Never `Indicate`, recolour or fade a QR code
  partially; point at it with a `SurroundingRectangle`. The last segment ends with
  `qr_wall(episode_qr_ids(N))` held 10 seconds (`self.finish(extra=...)` if the narration ends
  sooner), then the teaser `end_card`.
- `python3 production/check_holds.py N` measures how long each QR card stays up in episode
  N's rendered segments (480p15 by default) and fails any under 8 s. Hold a card with
  `card_shown = self.renderer.time` after showing it and `self.wait_since(card_shown, 8.2)`
  before removing it, so faster narration can't cut it short.
- `python production/check_qr.py` renders every card at 1080p and decodes it;
  `check_qr.py --wall N` decodes episode N's closing wall from its 1080p render.
- Keep text inside the frame (`fit`), at least 18 pt at 1080p equivalent (font_size ≥ 18),
  and never let two pieces of text overlap.
- No film imagery, logos, or real coin and banknote designs: coins are plain gold discs.

## Episode notes

Where a scene departs from its script's **Visual.** notes, or shows a value no snippet
prints. Values computed in a scene say so in a comment; schematic drawings are labelled
"not to scale" on screen. Every episode also adds small moving beats where the narration
runs on with no shot, so no stretch is static text.

- **1** Code panels sit above their consoles (too wide side by side at 18 pt). 1.5 animates
  the real carry (`…1001` → `…1010`); the script's note was corrected to match. 1.7's
  stored-value bars are not to scale but keep the true 1 : 2 ratio of the two errors.
- **2** `FloatLine.nearest` now breaks ties to even (2.7). 2.4's ten-quadrillion bar just
  overshoots the frame on its log scale. QR cards are removed in one cut, never faded.
- **3** 3.2's ticks are schematic, with the real `math.ulp` gaps printed beside them. 3.5's
  receipt uses $19.99 (a q03-03 price) at the script's rates. 3.8's 3,000,000,000 requests
  stand for "billions"; the invoice shows "$ ?" rather than a made-up price. 3.9 shows
  q03-05 lines 7–18 so all five risky lines are visible.
- **4** 4.1's long statement scrolls on a fixed strip. 4.4's reconciliation ledger shows the
  $0.30 transaction only (0.01 against 0.02). 4.5's receipt uses q03-05 and q04-03 prices at
  8.25 %, chosen so the line taxes miss the tax line by one cent (asserted in the scene).
  4.7's two worker runs use seeds 1 and 5. 4.8's four index updates are illustrative.
  4.9 is a plain clock-drift diagram, no weapons imagery. 4.10's hint shows the exact
  total, 26300659 cents, as the script asks; that gives the challenge away (director's call).
- **5** Other languages' code and output are parsed from the script's fenced blocks. 5.3's
  pre-1985 machines show "0.30000000000000?" rather than invented final digits. 5.4's
  largest double scrolls across the frame on purpose.
- **6** 6.3's 10,000-cent band is an overview image plus a scrolling zoom window. 6.4 builds
  the 0.125 half before 2.675's, in narration order. 6.2 shows q06-02 lines 12–15 while its
  card is up.
- **7** Film content is text only ("Office Space (1999)", "see: Superman III"). 7.7's ruler
  "zooms out" by relabelling rather than a camera move. 7.8 draws 434.97 so the gap from 435
  is visible (the real gap is far too small to draw).
- **8** The $100 bill is a plain green rectangle. 8.3 and 8.4 magnify the last cent, not to
  scale. 8.8's console shows the 1¢–5¢ rows; the Alabama outline is approximate.
- **9** A seven-box checklist card runs through the episode. 9.3 and 9.5 follow narration
  order where it differs from the shot order. 9.6 shows q09-03's class in two halves.
- **10** 10.2's last sliver is drawn as a labelled edge (it is far thinner than a pixel).
  10.5's ether stack is 18 coins plus a partial one. 10.9's recap ring is rectangular so
  nine tiles fit without overlapping.

# Agent guide

Start here if you are an AI agent (or a new collaborator) working in this repository.
It tells you what the project is, where things live, which rules are enforced, and how to
leave the repository in a state the next agent can pick up.

## What this is

**Money Problems** is an eleven-part narrated video series (a trailer plus ten
episodes, about 15 minutes each) on why floating-point numbers are the wrong way to store
money. The repository holds the *pre-production* material: scripts, runnable Python
samples, QR-code links, a pronunciation dictionary, and the tools that keep them
consistent. Narration is generated with ElevenLabs; graphics will be built with Manim
Community. Curt Cox directs; Claude writes scripts and code samples.

## Read in this order

1. [STATUS.md](STATUS.md) – what is done, what remains, and the work log. **Read before
   starting; update before finishing** (see "Leaving the repo tidy" below).
2. [README.md](README.md) – audience, script format ("Reading a script"), voice, visual
   language, QR workflow, production pipeline, disclosure text.
3. [series-bible.md](series-bible.md) – the arc, recurring visuals, house style, snippet
   rules, *Office Space* limits, and a brief per episode. Scripts must follow it.
4. The episode you are touching, in [episodes/](episodes/), including its
   **Fact check before recording** list at the end.

## Map

| Path | What it is | Edit by hand? |
|---|---|---|
| `episodes/NN-slug.md` | Scripts: segments, **Visual.** notes, on-screen code, QR cues, `>` narration, fact check | Yes |
| `snippets/epNN/MM-slug.py` | One runnable Python sample per QR code | Yes |
| `snippets/epNN/MM-slug.out` | Recorded output of that sample | No – `check_snippets.py --record` |
| `qr-manifest.json`, `qr-links.json`, `qr-links.md` | QR ids, titles, CIDs, URLs, fallback links | No – `tools/qr-links.mjs` |
| `pronunciations.pls` | ElevenLabs pronunciation dictionary (alias rules) | Yes |
| `tools/check_snippets.py` | Runs snippets, checks scripts against them | Yes |
| `tools/qr-links.mjs` | Generates links; `--upload` stages payloads, `--check` asks HashBin | Yes |
| `tools/extract-narration.mjs` | Writes per-segment narration text and `cues.csv` | Yes |
| `tools/narrate.py` | Generates ElevenLabs audio per segment (spends credits: director's go-ahead) | Yes |
| `tools/make_qr_svgs.py` | QR images and `production/qr-matrices.json` (needs `segno`) | Yes |
| `tools/descriptions.py` | Video descriptions to `build/youtube/` | Yes |
| `production/common.py` | Shared Manim helpers: timing, QR cards, recurring visuals | Yes, carefully: every episode uses it |
| `production/epNN.py` | One Manim Scene per script segment | Yes |
| `production/render.py`, `check_qr.py`, `check_holds.py`, `credits.py` | Render and stitch, QR decode and hold-time checks, credits card | Yes |
| `production/qr-matrices.json` | QR module grids | No – `tools/make_qr_svgs.py` |
| `tools/vendor/` | lz-string 1.5.0 (MIT), vendored | No |
| `build/` | Generated, git-ignored (`narration/`, `hashbin-upload/`) | No |

## Commands

Requirements: Python 3 (standard library only) and Node.js (no npm packages).

```bash
python3 tools/check_snippets.py                 # must report 0 problems before you commit
python3 tools/check_snippets.py --record ep03   # after an intentional snippet change; then read the .out
node tools/qr-links.mjs                         # after any snippet change; commit the regenerated files
node tools/extract-narration.mjs                # word counts and minutes per episode
python3 production/render.py 3 -ql              # quick review render of episode 3 (see production/README.md)
python3 tools/descriptions.py                   # video descriptions, after rendering
```

Production needs Manim Community 0.22 and ffmpeg but no TeX: never use `MathTex`/`Tex`.

`node tools/qr-links.mjs --check` queries the HashBin service and is rate-limited; run it
only when you need upload status, not as a routine check.

## Rules that are easy to break

- **Scenes read snippets.** Production scenes draw on-screen code and output from the
  snippet files, so a snippet change shows up in the video; re-render the episode and run
  `python3 tools/make_qr_svgs.py` (the QR code changes too).
- **Snippets and scripts move together.** Every ` ```python ` block in a script must be
  lines from one of that episode's snippets, and every ` ```output ` block lines from the
  recorded output. Every number the narration states comes from a snippet's `.out` or is
  listed in the episode's fact check. The checker enforces the first two; you enforce the
  third.
- **A snippet's bytes are its QR code.** Changing one byte changes its CID and URL. After
  editing a snippet: `--record` that episode, read the new output, update any script text
  that quotes it, run `node tools/qr-links.mjs`, and commit all of it together. Once QR
  codes have been uploaded or rendered into video (see STATUS.md), don't change a snippet
  without the director's say-so.
- **Snippet header** is exactly `# Money Problems · qNN-MM · Title`; the QR caption in the
  script must use the same title.
- **Snippet limits:** standard library only, deterministic, no input/files/network, short
  (see the series bible). Python Online runs CPython 3.14 in Pyodide; a native pass is
  necessary but not sufficient.
- **Narration** is only the `>` lines, written to be spoken: no symbols, numbers spelled
  out when ambiguous, long decimals described. `<break time="…" />` is the only markup.
- **Disclosure text** must agree in three places: README "How this series was made",
  episode 1 segment 1.8, and each published video description.
- **No impersonation or borrowed imagery.** Don't use 3Blue1Brown's name, logo or
  characters; no film clips, stills or posters (episode 7 is commentary only); don't clone
  or imitate any voice other than the director's own.
- **Claims are careful.** Prefer "most", "typically", "in Python" over "all". Real
  incidents, laws, films and prices go in the fact check until confirmed.

## Fact-check convention

Each episode ends with **Fact check before recording**. An item is open until someone
confirms it. When you confirm one, keep the item and append
` ✓ Confirmed YYYY-MM-DD: <source or command>.` to it. If the claim was wrong, fix the
script (and snippet if needed) and say so in the same note. Recount open items for
STATUS.md with:

```bash
for f in episodes/*.md; do printf '%s ' "$f"; awk '/^## Fact check/{p=1;next} p&&/^- /&&!/✓ Confirmed/{c++} END{print c+0}' "$f"; done
```

## Leaving the repo tidy

Before you finish a piece of work:

1. `python3 tools/check_snippets.py` reports 0 problems, and `node tools/qr-links.mjs`
   leaves `git status` unchanged (or you commit what it changed).
2. Update [STATUS.md](STATUS.md): move items between *Remaining* and *Done*, update the
   episode table, and add one dated line to the work log saying what changed and what you
   left unfinished.
3. Don't commit `build/` or anything outside the repository's purpose. Commit only when
   asked.

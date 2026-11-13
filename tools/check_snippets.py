"""Run every QR snippet and check the episode scripts against it.

Usage:
    python3 tools/check_snippets.py            check everything
    python3 tools/check_snippets.py --record   (re)write each snippet's expected .out file
    python3 tools/check_snippets.py ep03 q05   only snippets whose path or id contains a filter;
                                               episode checks run only for "epNN" filters

What it checks:

1. Each snippet in snippets/epNN/*.py starts with the header line
   "# Money Problems · qNN-MM · Title", where NN matches its folder.
2. Each snippet runs with `python3 -I` in under DEADLINE seconds (python.hashbin.page
   stops an Auto-run after five seconds, and Pyodide is slower than native Python) and
   prints exactly what its recorded .out file says. Tracebacks count as output, so a
   snippet that is *meant* to fail records its error.
3. Every **QR qNN-MM** cue in an episode names an existing snippet, and every snippet is
   cued by its episode at least once.
4. Every ```python block in an episode is an excerpt of one of that episode's snippets:
   each non-blank line (ignoring leading/trailing spaces) appears in the same snippet.
   Code in other languages (```javascript, ```java, ```c ...) is not checked.
5. Every ```output block in an episode is an excerpt of that episode's recorded
   output: each non-blank line appears in one snippet's .out file.

A native pass is necessary but not sufficient: python.hashbin.page runs CPython 3.14 in
Pyodide. Open the links in a browser as well (see README.md, "QR codes").
"""
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNIPPETS = ROOT / 'snippets'
EPISODES = ROOT / 'episodes'
DEADLINE = 3.0       # seconds, native; leaves room for Pyodide inside the site's 5 s limit
MAX_BYTES = 2000     # keeps QR payloads and on-screen code small
MAX_OUTPUT_LINES = 40
HEADER = re.compile(r'^# Money Problems · (q(\d\d)-\d\d) · (.+)$')


def snippet_files(filters):
    files = sorted(SNIPPETS.glob('ep*/*.py'))
    if filters:
        files = [f for f in files if any(x in str(f.relative_to(ROOT)) or x in f.read_text().split('\n', 1)[0] for x in filters)]
    return files


def run(path):
    started = time.time()
    try:
        proc = subprocess.run([sys.executable, '-I', path.name], cwd=path.parent, capture_output=True,
                              text=True, timeout=DEADLINE * 3)
    except subprocess.TimeoutExpired:
        return None, DEADLINE * 3
    # Tracebacks name the file; keep only its base name so output is machine-independent.
    output = proc.stdout + proc.stderr.replace(str(path.parent) + '/', '')
    return output, time.time() - started


def episode_text(number):
    found = list(EPISODES.glob(f'{number:02d}-*.md'))
    return found[0].read_text() if found else None


def blocks(markdown, language):
    return re.findall(r'^```' + language + r'\n(.*?)^```', markdown, flags=re.S | re.M)


def main(argv):
    record = '--record' in argv
    filters = [a for a in argv if not a.startswith('--')]
    problems = []
    snippets = {}  # id -> (path, source lines, output lines)
    for path in snippet_files(filters):
        rel = path.relative_to(ROOT)
        source = path.read_text()
        header = HEADER.match(source.split('\n', 1)[0])
        if not header:
            problems.append(f'{rel}: first line must be "# Money Problems · qNN-MM · Title"')
            continue
        qid, ep, title = header.groups()
        if path.parent.name != f'ep{ep}':
            problems.append(f'{rel}: {qid} is in the wrong folder')
        if len(source.encode()) > MAX_BYTES:
            problems.append(f'{rel}: {len(source.encode())} bytes; keep snippets under {MAX_BYTES}')
        output, elapsed = run(path)
        expected = path.with_suffix('.out')
        if output is None:
            problems.append(f'{rel}: did not finish')
            output = ''
        elif elapsed > DEADLINE:
            problems.append(f'{rel}: took {elapsed:.1f} s natively; keep it under {DEADLINE} s')
        if output.count('\n') > MAX_OUTPUT_LINES:
            problems.append(f'{rel}: prints {output.count(chr(10))} lines; keep it under {MAX_OUTPUT_LINES}')
        if record:
            expected.write_text(output)
        elif not expected.exists():
            problems.append(f'{rel}: no recorded output; run with --record after checking it by eye')
        elif expected.read_text() != output:
            problems.append(f'{rel}: output differs from {expected.name}')
        snippets[qid] = (path, {l.strip() for l in source.splitlines() if l.strip()},
                         {l.strip() for l in output.splitlines() if l.strip()})
        print(f"{'ok  ' if not any(str(rel) in p for p in problems) else 'FAIL'} {qid} {rel} ({elapsed:.2f} s)")

    # With filters, check only the episodes named by an "epNN" filter.
    episodes = None if not filters else {int(f[2:]) for f in filters if re.fullmatch(r'ep\d\d', f)}
    if episodes is None or episodes:
        problems += check_episodes(snippets, episodes)
    for p in problems:
        print('  - ' + p)
    print(f'\n{len(snippets)} snippet(s), {len(problems)} problem(s)')
    return 1 if problems else 0


def check_episodes(snippets, only=None):
    problems = []
    by_episode = {}
    for qid, info in snippets.items():
        by_episode.setdefault(int(qid[1:3]), {})[qid] = info
    for md in sorted(EPISODES.glob('*.md')):
        number = int(md.name[:2])
        if only is not None and number not in only:
            continue
        text = md.read_text()
        mine = by_episode.get(number, {})
        cued = set(re.findall(r'\*\*QR (q\d\d-\d\d)\*\*', text))
        for qid in sorted(cued - set(snippets)):
            problems.append(f'{md.name}: cues {qid}, which has no snippet')
        for qid in sorted(set(mine) - cued):
            problems.append(f'{md.name}: never cues its snippet {qid}')
        for n, block in enumerate(blocks(text, 'python'), 1):
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not any(all(l in src for l in lines) for _, src, _ in mine.values()):
                missing = [l for l in lines if not any(l in src for _, src, _ in mine.values())]
                problems.append(f'{md.name}: python block {n} is not an excerpt of one snippet'
                                + (f' (e.g. {missing[0]!r})' if missing else ''))
        for n, block in enumerate(blocks(text, 'output'), 1):
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            missing = [l for l in lines if not any(l in out for _, _, out in mine.values())]
            if missing:
                problems.append(f'{md.name}: output block {n} has a line no snippet prints: {missing[0]!r}')
    return problems


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Write each episode's video description: summary, chapters, QR links and the disclosure.

    python3 tools/descriptions.py            # every episode
    python3 tools/descriptions.py 3 4        # only these

Output (gitignored, regenerate any time): build/youtube/epNN.txt. Chapter times come from the
rendered segment videos (build/media/videos/epNN/1080p60/, else 480p15) when they exist, so
render first; otherwise they fall back to the narration estimate and the file says so. The
disclosure block is copied from README.md, "How this series was made", so the description
always agrees with it. YouTube limits a description to 5,000 characters: when the fallback links
would push it over, they go to build/youtube/epNN-pinned-comment.txt for the video's pinned
comment instead, and the description says so.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'production'))
WORDS_PER_MINUTE = 145
TAIL_SECONDS = 0.8
LIMIT = 5000


def episode_file(episode):
    return sorted((ROOT / 'episodes').glob(f'{episode:02d}-*.md'))[0]


def disclosure():
    readme = (ROOT / 'README.md').read_text()
    block = readme.split('## How this series was made', 1)[1]
    return re.search(r'```text\n(.*?)```', block, re.S).group(1).strip()


def segments(text):
    """[(segment id, title, narration)] in order."""
    found = []
    for match in re.finditer(r'^### (\d+\.\d+) (.+?) · ≈ [\d:]+\n(.*?)(?=^### |^## |\Z)', text, re.M | re.S):
        narration = ' '.join(l[1:].strip() for l in match.group(3).splitlines() if l.startswith('>'))
        found.append((match.group(1), match.group(2).strip(), narration))
    return found


def estimate(narration):
    pauses = sum(float(s) for s in re.findall(r'<break time="([\d.]+)s"\s*/>', narration))
    return len(re.sub(r'<[^>]+>', ' ', narration).split()) / WORDS_PER_MINUTE * 60 + pauses + TAIL_SECONDS


def measured(episode, segment):
    name = 'Segment_' + segment.replace('.', '_')
    for quality in ('1080p60', '720p30', '480p15'):
        video = ROOT / 'build' / 'media' / 'videos' / f'ep{episode:02d}' / quality / f'{name}.mp4'
        if video.exists():
            return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
                                         'csv=p=0', str(video)], capture_output=True, text=True, check=True).stdout)
    return None


def clock(seconds):
    seconds = int(round(seconds))
    return f'{seconds // 60}:{seconds % 60:02d}'


def summary(text):
    """The episode's learning goals as one paragraph."""
    goals = re.search(r'## Learning goals\n\nBy the end, the viewer can:\n\n(.*?)\n\n', text, re.S)
    if not goals:
        return ''
    items = [re.sub(r'`([^`]*)`', r'\1', g.strip().removeprefix('- ').rstrip(';.'))
             for g in goals.group(1).split('\n- ')]
    return 'In this video you will learn to ' + '; '.join(items) + '.'


def describe(episode, links):
    text = episode_file(episode).read_text()
    title = re.match(r'# Episode \d+ · (.+)', text).group(1).strip()
    parts = [title, '']
    if summary(text):
        parts += [summary(text), '']
    t, estimated = 0.0, False
    chapters = []
    for sid, name, narration in segments(text):
        chapters.append(f'{clock(t)} {name}')
        length = measured(episode, sid)
        if length is None:
            length, estimated = estimate(narration), True
        t += length
    parts += ['Chapters' + (' (estimated: render the episode for exact times)' if estimated else ''), *chapters, '']
    rows = [r for r in links if r['episode'] == episode]
    parts += ['Run the code from the video in your browser (Python Online):']
    for r in rows:
        parts.append(f"{r['id']} · {r['title']}: {r['url']}")
    fallbacks = ['If a link above does not open, these carry the code itself:']
    fallbacks += [f"{r['id']}: {r['fallback']}" for r in rows]
    full = '\n'.join(parts + [''] + fallbacks + ['', disclosure()]) + '\n'
    if len(full) <= LIMIT:
        return full, None
    short = '\n'.join(parts + ['', 'Backup links that carry the code itself are in the pinned comment.', '',
                                disclosure()]) + '\n'
    return short, '\n'.join(fallbacks) + '\n'


def main(argv):
    links = json.loads((ROOT / 'qr-links.json').read_text())
    episodes = [int(a) for a in argv] or sorted(int(p.name[:2]) for p in (ROOT / 'episodes').glob('[0-9][0-9]-*.md'))
    out = ROOT / 'build' / 'youtube'
    out.mkdir(parents=True, exist_ok=True)
    for episode in episodes:
        description, comment = describe(episode, links)
        path = out / f'ep{episode:02d}.txt'
        path.write_text(description)
        pinned = out / f'ep{episode:02d}-pinned-comment.txt'
        if comment:
            pinned.write_text(comment)
        elif pinned.exists():
            pinned.unlink()
        warning = f'  OVER {LIMIT}' if len(description) > LIMIT else ''
        note = ' (fallback links moved to the pinned comment)' if comment else ''
        print(f'{path.relative_to(ROOT)}: {len(description)} characters{warning}{note}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

"""Measure how long each QR card stays on screen in an episode's rendered segments.

    python3 production/check_holds.py 3            # episode 3, 480p15 renders
    python3 production/check_holds.py 3 1080p60

A card sits in the bottom-right corner (common.qr_card), black on white, so the corner
is mostly white while one is up. The script samples that corner four times a second
with ffmpeg and reports each stretch it was showing a card. A stretch shorter than
8 seconds fails (README asks for at least 6; the series holds 8). The closing wall is
centred and is not measured here; check it with check_qr.py --wall.
Standard library only; needs ffmpeg.
"""
import re
import subprocess
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
MINIMUM = 8.0
RATE = 4                      # samples per second
# Split at mid-grey: at 480p a module is about 2.4 pixels and compression blurs many of them.
_NOT_LIGHT = bytes(range(129))          # deleting these leaves the pixels above 128
_NOT_DARK = bytes(range(128, 256))      # deleting these leaves the pixels below 128
_NOT_WHITE = bytes(range(211))          # pure white: QR backgrounds, not gold or grey


def segment_names(episode):
    source = (PRODUCTION / f'ep{episode:02d}.py').read_text()
    return re.findall(r'^class (Segment_\d+_\d+)\(Segment\b', source, re.M)


def stretches(video):
    """[(start, end)] seconds during which the bottom-right corner shows a QR card."""
    probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                            'stream=width,height', '-of', 'csv=p=0', str(video)],
                           capture_output=True, text=True, check=True).stdout.strip()
    width, height = map(int, probe.split(','))
    side = int(height * 0.22)                       # inside the 25 %-high card
    x, y = width - side - int(height * 0.06), height - side - int(height * 0.06)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-vf',
                          f'fps={RATE},crop={side}:{side}:{x}:{y},format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    size = side * side
    found, start = [], None
    frames = len(raw) // size
    for k in range(frames):
        frame = raw[k * size:(k + 1) * size]
        light = len(frame.translate(None, _NOT_LIGHT)) / size
        dark = len(frame.translate(None, _NOT_DARK)) / size
        white = len(frame.translate(None, _NOT_WHITE)) / size
        # A QR code is about half light, half dark, and its light is pure white.
        showing = light > 0.3 and dark > 0.3 and white > 0.15
        t = k / RATE
        if showing and start is None:
            start = t
        elif not showing and start is not None:
            found.append((start, t))
            start = None
    if start is not None:
        found.append((start, frames / RATE))
    return found


def main(argv):
    episode = int(argv[0])
    quality = argv[1] if len(argv) > 1 else '480p15'
    videos = ROOT / 'build' / 'media' / 'videos' / f'ep{episode:02d}' / quality
    failures = 0
    for name in segment_names(episode):
        video = videos / f'{name}.mp4'
        if not video.exists():
            print(f'{name}: not rendered')
            continue
        for start, end in stretches(video):
            # Blips under a second are something white passing the corner, not a card.
            if end - start < 1.0:
                continue
            ok = end - start >= MINIMUM
            failures += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {name} card {start:6.1f}–{end:6.1f} s ({end - start:4.1f} s)")
    print(f'\n{failures} card(s) shorter than {MINIMUM:.0f} s')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

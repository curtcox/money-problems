"""Shared building blocks for the Money Problems production scenes (Manim Community).

Each segment of an episode script is one Scene class (`Segment_1_5` is segment 1.5). A
segment's length comes from its narration: the word count at 145 words per minute plus any
<break/> pauses, or the measured audio length once tools/narrate.py has written
build/narration/durations.json. Beats are placed with Segment.at('phrase') (when the
narration starts saying a phrase) or Segment.hold_until(fraction), so re-timing to the real
audio is a matter of rendering again.

The recurring visuals from series-bible.md live here so every episode draws them the same
way: the cent grid, the float line, the ledger, the receipt, the penny, and the code and
console panels. No TeX is needed: every label is Text, and fractions use plain characters.

Render through production/render.py, or directly from the repository root:
    manim -ql production/ep01.py Segment_1_1
Set SEGMENT_LABELS=1 to burn the segment id and clock into a corner for review.
"""
import json
import math
import os
import re
import textwrap
from fractions import Fraction
from pathlib import Path

from manim import *

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
WORDS_PER_MINUTE = 145
TAIL_SECONDS = 0.8          # breathing room after the last sentence

# Colour roles (README "Visual language", series bible "Recurring visuals").
STORED = BLUE               # values as the computer stores them
FOCUS = YELLOW              # whatever the narration points at; true values
EXACT = GREEN               # exact or correct
ERROR = RED                 # errors and lost money
MONEY = GOLD                # coins, cents, totals
SCAFFOLD = GREY_B           # axes, labels, frames
DIM = GREY_D
PAPER = '#f2eee3'           # receipt paper
INK = '#2b2b2b'             # receipt ink
PANEL = '#1e1f1c'           # code and console backgrounds (monokai)

QR_HEIGHT = 2.0             # 25 % of the 8-unit frame (README asks for at least 22 %)

# One sans-serif face for every Text (Avenir Next ships with macOS; set SERIES_FONT
# elsewhere) and Menlo for code, output, receipts and ledgers.
FONT = os.environ.get('SERIES_FONT', 'Avenir Next')
MONO = os.environ.get('SERIES_MONO', 'Menlo')
Text.set_default(font=FONT)
MarkupText.set_default(font=FONT)


# ---------------------------------------------------------------- timing

def _episode_file(episode):
    matches = sorted((ROOT / 'episodes').glob(f'{episode:02d}-*.md'))
    if not matches:
        raise FileNotFoundError(f'No script for episode {episode}')
    return matches[0]


def narration_text(episode, segment):
    """Narration lines (blockquotes) of one '### <segment> Title' section, joined."""
    lines, inside = [], False
    for line in _episode_file(episode).read_text().splitlines():
        heading = re.match(r'^### (\d+\.\d+)\s', line)
        if heading:
            inside = heading.group(1) == segment
            continue
        if line.startswith('## '):
            inside = False
        if inside and line.startswith('>'):
            lines.append(line.lstrip('>').strip())
    return ' '.join(l for l in lines if l)


def narration_seconds(episode, segment):
    measured = ROOT / 'build' / 'narration' / 'durations.json'
    if measured.exists():
        durations = json.loads(measured.read_text())
        key = f'{episode:02d}.{segment.split(".")[1]}'
        if key in durations:
            return float(durations[key])
    text = narration_text(episode, segment)
    pauses = sum(float(s) for s in re.findall(r'<break time="([\d.]+)s"\s*/>', text))
    words = len(re.sub(r'<[^>]+>', ' ', text).split())
    return words / WORDS_PER_MINUTE * 60 + pauses


def _timeline(episode, segment):
    """(word, estimated start second) for each narrated word, pauses included."""
    words, clock = [], 0.0
    for token in re.split(r'(<break time="[\d.]+s"\s*/>)', narration_text(episode, segment)):
        pause = re.match(r'<break time="([\d.]+)s"', token)
        if pause:
            clock += float(pause.group(1))
            continue
        for word in re.sub(r'<[^>]+>', ' ', token).split():
            words.append((word, clock))
            clock += 60 / WORDS_PER_MINUTE
    return words, clock


def phrase_seconds(episode, segment, phrase, occurrence=0):
    """When the narration starts saying a phrase: from ElevenLabs' character timings (saved by
    tools/narrate.py) when they exist, else from its word position at the estimated rate,
    scaled to the measured segment length if there is one. Matching ignores case and runs of
    whitespace. After narration the spoken text has the pronunciation aliases applied, so pick
    phrases without aliased words (JSON, SQL, IEEE ...)."""
    sidecar = ROOT / 'build' / 'narration' / 'audio' / f'ep{episode:02d}' / f'{segment}.json'
    alignment = json.loads(sidecar.read_text()).get('alignment') if sidecar.exists() else None
    needle = ' '.join(phrase.lower().split())
    if alignment and alignment.get('starts'):
        # Collapse runs of whitespace (paragraph breaks arrive as "\n\n"), keeping each
        # kept character's index into the timings.
        spoken, index = '', []
        for i, ch in enumerate(''.join(alignment['characters']).lower()):
            if ch.isspace():
                if spoken.endswith(' '):
                    continue
                ch = ' '
            spoken += ch
            index.append(i)
        start = -1
        for _ in range(occurrence + 1):
            start = spoken.find(needle, start + 1)
            if start < 0:
                raise ValueError(f'{segment}: narration never says {phrase!r}')
        return alignment['starts'][index[start]]
    words, estimated = _timeline(episode, segment)
    joined, offsets = '', []
    for i, (word, _) in enumerate(words):
        offsets.append(len(joined))
        joined += word.lower() + ' '
    start = -1
    for _ in range(occurrence + 1):
        start = joined.find(needle, start + 1)
        if start < 0:
            raise ValueError(f'{segment}: narration never says {phrase!r}')
    index = max(i for i, o in enumerate(offsets) if o <= start)
    return words[index][1] * narration_seconds(episode, segment) / max(estimated, 1e-6)


class Segment(Scene):
    """A scene whose length follows its segment's narration."""

    EPISODE = 0
    SEGMENT = '0.0'

    def setup(self):
        self.target = narration_seconds(self.EPISODE, self.SEGMENT) + TAIL_SECONDS
        if os.environ.get('SEGMENT_LABELS'):
            label = Text(f'{self.SEGMENT}', font_size=18, color=DIM).to_corner(UL, buff=0.15)
            clock = number(0, decimals=1, font_size=18, color=DIM).next_to(label, RIGHT)
            clock.add_updater(lambda m: m.set_value(self.renderer.time))
            self.add_foreground_mobjects(label, clock)
        super().setup()

    def hold_until(self, fraction):
        """Wait until the given fraction of the narration has been spoken."""
        remaining = fraction * self.target - self.renderer.time
        if remaining > 1 / 30:
            self.wait(remaining)

    def at(self, phrase, occurrence=0, lead=0.0):
        """Wait until the narration starts saying phrase (lead seconds earlier, if given)."""
        remaining = phrase_seconds(self.EPISODE, self.SEGMENT, phrase, occurrence) - lead - self.renderer.time
        if remaining > 1 / 30:
            self.wait(remaining)

    def wait_since(self, since, seconds):
        """Wait until `seconds` have passed since renderer time `since` (for example, so a QR
        card shown at `since` stays up at least 8 seconds before it is removed)."""
        remaining = since + seconds - self.renderer.time
        if remaining > 1 / 30:
            self.wait(remaining)

    def finish(self, extra=0.0):
        """Hold until the narration ends (plus extra seconds, for a held QR wall)."""
        self.hold_until(1.0)
        if extra > 0:
            self.wait(extra)


# ---------------------------------------------------------------- QR codes

_QR = json.loads((PRODUCTION / 'qr-matrices.json').read_text())


def qr_code(qr_id, height=QR_HEIGHT):
    """A scannable QR code as vector rectangles, black on white with its quiet zone."""
    rows = _QR[qr_id]['rows']
    quiet = 4
    module = height / (len(rows) + 2 * quiet)
    backing = Square(side_length=height).set_fill(WHITE, 1).set_stroke(width=0)
    top_left = backing.get_corner(UL) + (RIGHT + DOWN) * quiet * module
    modules = VGroup()
    for r, row in enumerate(rows):
        for match in re.finditer(r'1+', row):
            run = match.end() - match.start()
            # A hair of overlap hides anti-aliasing seams between neighbouring modules.
            rect = Rectangle(width=run * module * 1.01, height=module * 1.04)
            rect.set_fill(BLACK, 1).set_stroke(width=0)
            rect.move_to(top_left + RIGHT * (match.start() + run / 2) * module + DOWN * (r + 0.5) * module)
            modules.add(rect)
    return VGroup(backing, modules)


def qr_title(qr_id):
    return _QR[qr_id]['title']


def wrapped_text(words, max_width, font_size=20, skip=0, **kwargs):
    """Text no wider than max_width: wraps once at the comma or space nearest the middle
    (ignoring the first `skip` characters) before falling back to shrinking."""
    text = Text(words, font_size=font_size, **kwargs)
    if text.width <= max_width:
        return text
    breaks = [i for i, ch in enumerate(words) if ch in ', ' and i > skip]
    cut = min(breaks, key=lambda i: abs(i - len(words) / 2)) if breaks else len(words) // 2
    text = Text(words[:cut + 1].rstrip() + '\n' + words[cut + 1:].strip(), font_size=font_size,
                line_spacing=0.8, **kwargs)
    return text.scale_to_fit_width(max_width) if text.width > max_width else text


def qr_card(qr_id, height=QR_HEIGHT, corner=DR):
    """QR code with its caption ("q03-02 · Free shipping, almost") above it, in a corner.
    Show it for at least 8 seconds and never over moving content."""
    code = qr_code(qr_id, height)
    caption = wrapped_text(f'{qr_id} · {qr_title(qr_id)}', 4.2, font_size=20, skip=len(qr_id) + 3)
    caption.next_to(code, UP, buff=0.12)
    caption.align_to(code, RIGHT if corner[0] > 0 else LEFT)
    card = VGroup(BackgroundRectangle(caption, fill_opacity=0.85, buff=0.06), caption, code)
    return card.to_corner(corner, buff=0.3)


def episode_qr_ids(episode):
    return sorted(k for k in _QR if k.startswith(f'q{episode:02d}-'))


def qr_wall(qr_ids, height=2.0):
    """All of an episode's codes, captions underneath, for the closing wall (rows of three).
    Hold it for 10 seconds."""
    cards = VGroup()
    for qr_id in qr_ids:
        code = qr_code(qr_id, height)
        caption = Text(qr_id, font_size=22).next_to(code, DOWN, buff=0.15)
        title = wrapped_text(qr_title(qr_id), height + 0.6, font_size=18, color=SCAFFOLD).next_to(caption, DOWN, buff=0.08)
        cards.add(VGroup(code, caption, title))
    if len(cards) <= 4:
        cards.arrange(RIGHT, buff=0.6, aligned_edge=UP)
    else:
        rows = [VGroup(*cards[i:i + 3]).arrange(RIGHT, buff=0.9, aligned_edge=UP) for i in range(0, len(cards), 3)]
        VGroup(*rows).arrange(DOWN, buff=0.35)
        cards.move_to(ORIGIN)
    if cards.width > 13.2:
        cards.scale_to_fit_width(13.2)
    if cards.height > 7.0:
        cards.scale_to_fit_height(7.0)
    return cards


# ---------------------------------------------------------------- snippets, code and console

def snippet_path(path):
    return ROOT / 'snippets' / path


def snippet_source(path):
    """Source of a QR snippet ('ep01/01-ten-plus-twenty.py'), so on-screen code always
    matches what the QR code opens."""
    return snippet_path(path).read_text()


def snippet_lines(path, first, last):
    """Lines first..last (1-based, inclusive) of a snippet, dedented, for an excerpt panel."""
    lines = snippet_source(path).splitlines()[first - 1:last]
    return textwrap.dedent('\n'.join(lines))


def snippet_find(path, *needles):
    """The snippet lines that contain each needle, in order: an excerpt that can't drift."""
    lines = snippet_source(path).splitlines()
    picked = []
    for needle in needles:
        found = [l for l in lines if needle in l]
        if not found:
            raise ValueError(f'{path}: no line contains {needle!r}')
        picked.append(found[0])
    return textwrap.dedent('\n'.join(picked))


def snippet_output(path):
    """The recorded output lines of a snippet (its .out file), exactly as Python prints them."""
    return snippet_path(path).with_suffix('.out').read_text().rstrip('\n').split('\n')


def output_line(path, needle):
    """The first recorded output line of a snippet that contains needle."""
    for line in snippet_output(path):
        if needle in line:
            return line
    raise ValueError(f'{path}: no output line contains {needle!r}')


def code_panel(source, font_size=24, line_numbers=False):
    """Syntax-highlighted code on a dark rounded panel (Manim's Code mobject, monokai).
    Keep it to about 14 lines; `code.code_lines[i]` is line i for highlighting."""
    return Code(code_string=source.strip('\n'), language='python', formatter_style='monokai',
                add_line_numbers=line_numbers, background='rectangle',
                background_config={'fill_color': PANEL, 'stroke_color': GREY_D, 'stroke_width': 1},
                paragraph_config={'font_size': font_size, 'font': MONO})


def line_highlight(code, index, color=FOCUS):
    """A yellow box around line `index` (0-based) of a code_panel, the panel's full width."""
    lines = code.code_lines
    target = lines[index]
    box = SurroundingRectangle(target, color=color, buff=0.04, corner_radius=0.05)
    if len(lines) > 1:
        # Never taller than the line pitch, so it doesn't cover its neighbours.
        pitch = abs(lines[0].get_y() - lines[-1].get_y()) / (len(lines) - 1)
        if box.height > pitch:
            box.stretch_to_fit_height(pitch)
    return box.stretch_to_fit_width(code.background.width - 0.2).move_to(
        [code.background.get_x(), target.get_y(), 0])


_BLOCK = '█'   # fills its monospace cell, so lines that start with it share a column grid
_ADVANCE = {}


def _advance(font, font_size):
    """Distance between neighbouring character cells, measured from two block glyphs (one
    block's ink is a little wider than its cell, so its width alone drifts along a line)."""
    key = (font, font_size)
    if key not in _ADVANCE:
        pair = Text(_BLOCK * 2, font=font, font_size=font_size)
        _ADVANCE[key] = pair[1].get_left()[0] - pair[0].get_left()[0]
    return _ADVANCE[key]


class MonoLine(VGroup):
    """One line of monospaced text whose glyphs keep their columns, leading spaces included.

    `line.glyphs` holds the visible characters (Text has none for spaces); `line.part('4')`
    returns the glyphs of a substring, for colouring a digit or a word. Lines of one font size
    share a column grid once their anchors line up (`stack_lines`, Console and receipt do
    this). Invisible marker points travel with the line, so anchors survive any shift or scale."""

    def __init__(self, source, font_size=24, color=GREY_A, font=None, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        text = Text(_BLOCK + source, font=font or MONO, font_size=font_size, color=color)
        block = text[0]
        left = block.get_left()
        advance = _advance(font or MONO, font_size)
        self.markers = VGroup(VectorizedPoint(left), VectorizedPoint(left + RIGHT * advance),
                              VectorizedPoint(left + UP * block.height / 2))
        self.glyphs = VGroup(*text[1:])
        self.blank = not len(self.glyphs)
        if self.blank:
            self.glyphs.add(VectorizedPoint(block.get_center()))
        self.add(self.markers, self.glyphs)

    @property
    def cell(self):
        return float(np.linalg.norm(self.markers[1].get_center() - self.markers[0].get_center()))

    @property
    def line_height(self):
        return 2 * float(np.linalg.norm(self.markers[2].get_center() - self.markers[0].get_center()))

    def anchor(self):
        """Left edge of column 0, at mid-height of the line."""
        return self.markers[0].get_center()

    def set_anchor(self, point):
        return self.shift(np.array(point, dtype=float) - self.anchor())

    def column_point(self, column):
        """Left edge of a column (0-based), at mid-height."""
        return self.anchor() + RIGHT * self.cell * column

    def part(self, needle, occurrence=0):
        start = -1
        for _ in range(occurrence + 1):
            start = self.source.index(needle, start + 1)
        return self.chars(start, start + len(needle))

    def chars(self, start, end=None):
        end = len(self.source) if end is None else end
        index = len(re.sub(r'\s', '', self.source[:start]))
        count = len(re.sub(r'\s', '', self.source[start:end]))
        return VGroup(*self.glyphs[index:index + count])


def mono_line(source, font_size=24, color=GREY_A):
    return MonoLine(source, font_size=font_size, color=color)


def stack_lines(lines, spacing=1.45):
    """Stack MonoLines top to bottom on a shared column grid (line pitch = spacing × cap height)."""
    if not lines:
        return VGroup()
    pitch = lines[0].line_height * spacing
    origin = lines[0].anchor()
    for i, line in enumerate(lines):
        line.set_anchor(origin + DOWN * pitch * i)
    return VGroup(*lines)


class Console(VGroup):
    """The console panel: program output exactly as printed, in a dark rounded box.

    `console.lines[i]` is a MonoLine; `console.part(i, 'needle')` picks glyphs to colour.
    `rows` reserves space for more lines than are given, and `width` fixes the box width, so
    a console can be built empty-looking and typed into. `console.type_line(i)` is the
    type-out animation; start with `console.background` on screen and type each line."""

    def __init__(self, lines, font_size=22, width=None, rows=None, title=None, color=GREY_A, **kwargs):
        super().__init__(**kwargs)
        self.lines = [MonoLine(l, font_size=font_size, color=color) for l in lines]
        sample = MonoLine('M', font_size=font_size)
        stack_lines(self.lines)
        body = VGroup(*self.lines)
        pitch = sample.line_height * 1.45
        rows = max(rows or len(lines), len(lines), 1)
        longest = max([len(l) for l in lines] + [8])
        inner_w = width - 0.5 if width else longest * sample.cell + 0.1
        inner_h = pitch * (rows - 1) + sample.line_height
        self.background = RoundedRectangle(width=inner_w + 0.5, height=inner_h + 0.5, corner_radius=0.12)
        self.background.set_fill(PANEL, 1).set_stroke(GREY_D, 1)
        if self.lines:
            first = self.lines[0]
            target = self.background.get_corner(UL) + RIGHT * 0.25 + DOWN * (0.25 + first.line_height / 2)
            body.shift(target - first.anchor())
        self.body = body
        self.add(self.background, body)
        if title:
            self.title = Text(title, font_size=18, color=SCAFFOLD).next_to(self.background, UP, buff=0.08,
                                                                           aligned_edge=LEFT)
            self.add(self.title)

    def part(self, index, needle, occurrence=0):
        return self.lines[index].part(needle, occurrence)

    def type_line(self, index, run_time=None):
        """Type line `index` out, character by character."""
        glyphs = self.lines[index].glyphs
        n = len(glyphs)
        run_time = run_time or max(0.3, min(1.6, n * 0.035))
        return LaggedStart(*[FadeIn(g, run_time=0.05) for g in glyphs], lag_ratio=1.0, run_time=run_time)

    def type_all(self, run_time_per_line=None):
        return Succession(*[self.type_line(i, run_time_per_line) for i in range(len(self.lines))])


def console(lines, **kwargs):
    return Console(lines, **kwargs)


def output_console(path, needles=None, **kwargs):
    """A Console of a snippet's recorded output (all of it, or the lines containing needles)."""
    lines = snippet_output(path) if needles is None else [output_line(path, n) for n in needles]
    return Console(lines, **kwargs)


def code_text(source, font_size=26, color=GREY_A):
    """A single line of code or output in the code font, without a panel."""
    return MonoLine(source, font_size=font_size, color=color)


def number(value, decimals=0, font_size=36, color=WHITE, commas=False, **kwargs):
    """A counter that can animate (`.animate.set_value(n)`, ChangeDecimalToValue), drawn with
    Text: Manim's Integer and DecimalNumber use TeX unless given mob_class=Text, and this
    machine has no TeX. Never use MathTex, Tex or a bare DecimalNumber in production."""
    return DecimalNumber(value, num_decimal_places=decimals, mob_class=Text, font_size=font_size, color=color,
                         group_with_commas=commas, **kwargs)


def fit(mob, width=13.0):
    """Shrink a mobject that would run off the frame."""
    return mob.scale_to_fit_width(width) if mob.width > width else mob


# ---------------------------------------------------------------- the cent grid

def stored_direction(cents, denominator=100):
    """+1 if the double nearest cents/denominator is above it, -1 below, 0 exact."""
    exact = Fraction(cents, denominator)
    stored = Fraction(float(f'{cents / denominator:.10f}'))
    return (stored > exact) - (stored < exact)


class CentGrid(VGroup):
    """The cent grid: the hundred values $0.00 to $0.99 in a 10 × 10 grid (row = dimes,
    column = pennies). Exact cells (0.00, 0.25, 0.50, 0.75) glow GREEN; every other cell
    carries a small arrow, BLUE up when the stored double is above the true value, RED
    down when it is below. `grid.cells[c]`, `grid.labels[c]`, `grid.arrows[c]` (None for
    exact cells), `grid.exact` (the four exact cells)."""

    def __init__(self, cell=0.62, font_size=16, show_arrows=True, **kwargs):
        super().__init__(**kwargs)
        self.cells, self.labels, self.arrows = [], [], []
        squares, labels, arrows = VGroup(), VGroup(), VGroup()
        for c in range(100):
            row, col = divmod(c, 10)
            square = Square(cell).set_stroke(GREY_D, 1).set_fill(BLACK, 0)
            square.move_to(RIGHT * col * cell + DOWN * row * cell)
            label = Text(f'.{c:02d}', font=MONO, font_size=font_size, color=GREY_B).move_to(square)
            direction = stored_direction(c)
            arrow = None
            if direction:
                arrow = Arrow(ORIGIN, UP * cell * 0.32 * direction, buff=0, stroke_width=3,
                              max_tip_length_to_length_ratio=0.45, color=STORED if direction > 0 else ERROR)
                arrow.move_to(square.get_corner(UR) + LEFT * cell * 0.16 + DOWN * cell * 0.28)
                label.shift(LEFT * cell * 0.1)
                arrows.add(arrow)
            self.cells.append(square)
            self.labels.append(label)
            self.arrows.append(arrow)
            squares.add(square)
            labels.add(label)
        self.squares, self.label_group, self.arrow_group = squares, labels, arrows
        self.add(squares, labels, arrows)
        self.exact = VGroup(*[self.cells[c] for c in (0, 25, 50, 75)])
        self.center()
        if not show_arrows:
            # Centred with the arrows so arrow_group stays in place for adding later.
            self.remove(arrows)

    def light_exact(self):
        """Animations that make the four exact cells glow green."""
        return [cell.animate.set_fill(EXACT, 0.55).set_stroke(EXACT, 3) for cell in self.exact]


def cent_grid(**kwargs):
    return CentGrid(**kwargs)


# ---------------------------------------------------------------- the float line

def doubles_between(lo, hi, limit=400):
    """Every double from lo to hi inclusive (floats), at most `limit` of them."""
    x = float(lo)
    if Fraction(x) < Fraction(lo):
        x = math.nextafter(x, math.inf)
    out = []
    while Fraction(x) <= Fraction(hi) and len(out) < limit:
        out.append(x)
        x = math.nextafter(x, math.inf)
    return out


class FloatLine(VGroup):
    """The float line: a number line from lo to hi whose tick marks are the representable
    doubles in that window (pass exact values as Fractions or decimal strings). Use
    `line.point(value)` for positions, `line.diamond(value)` for a YELLOW true-value marker
    and `line.snap(value)` for the arrow from a true value to its nearest double. For views
    too wide to draw every double, pass `ticks=` your own list of tick values."""

    def __init__(self, lo, hi, width=11.0, ticks=None, tick_height=0.35, color=STORED,
                 labels=None, label_size=18, **kwargs):
        super().__init__(**kwargs)
        self.lo, self.hi = Fraction(lo), Fraction(hi)
        self.width_units = width
        self.axis = Line(LEFT * width / 2, RIGHT * width / 2, color=SCAFFOLD, stroke_width=2)
        values = ticks if ticks is not None else doubles_between(self.lo, self.hi)
        self.tick_values = list(values)
        self.ticks = VGroup(*[Line(DOWN * tick_height / 2, UP * tick_height / 2, color=color, stroke_width=3)
                              .move_to(self.point(v)) for v in self.tick_values])
        self.add(self.axis, self.ticks)
        self.labels = VGroup()
        for value, text in (labels or {}).items():
            label = Text(text, font=MONO, font_size=label_size, color=SCAFFOLD)
            label.next_to(self.point(value), DOWN, buff=tick_height / 2 + 0.15)
            self.labels.add(label)
        self.add(self.labels)

    def point(self, value):
        fraction = (Fraction(value) - self.lo) / (self.hi - self.lo)
        return self.axis.get_start() + (self.axis.get_end() - self.axis.get_start()) * float(fraction)

    def nearest(self, value):
        """The tick a correctly rounded operation lands on: nearest, ties to the even significand."""
        def even(t):
            mantissa, _ = math.frexp(float(t))
            return int(mantissa * 2 ** 53) % 2
        return min(self.tick_values, key=lambda t: (abs(Fraction(t) - Fraction(value)), even(t)))

    def diamond(self, value, size=0.22, color=FOCUS):
        d = Square(size).rotate(PI / 4).set_fill(color, 1).set_stroke(width=0)
        return d.move_to(self.point(value) + UP * 0.45)

    def snap(self, value, color=FOCUS):
        start = self.point(value) + UP * 0.32
        end = self.point(self.nearest(value)) + UP * 0.2
        return CurvedArrow(start, end, color=color, angle=-PI / 3, stroke_width=3, tip_length=0.15) \
            if abs(start[0] - end[0]) > 0.05 else Arrow(start + UP * 0.2, end, buff=0, color=color)


# ---------------------------------------------------------------- money objects

def coin(label='1¢', radius=0.5, color=MONEY, font_size=None):
    """A plain stylised coin: no real design, no national symbols."""
    body = Circle(radius=radius).set_fill(color, 1).set_stroke(interpolate_color(ManimColor(color), BLACK, 0.35), radius * 8)
    rim = Circle(radius=radius * 0.82).set_stroke(interpolate_color(ManimColor(color), WHITE, 0.3), radius * 2.5)
    text = Text(label, font_size=font_size or radius * 56, color=interpolate_color(ManimColor(color), BLACK, 0.7),
                weight=BOLD).move_to(body)
    if text.width > radius * 1.5:
        text.scale_to_fit_width(radius * 1.5)
    return VGroup(body, rim, text)


def penny(radius=0.5):
    """The penny: a gold coin marked 1¢."""
    return coin('1¢', radius)


def sliced_penny(slices=8, radius=0.8, gap=0.0):
    """A penny cut into equal wedges (fractions of a cent); returns the wedges."""
    wedges = VGroup()
    dark = interpolate_color(ManimColor(MONEY), BLACK, 0.35)
    for i in range(slices):
        wedge = Sector(radius=radius, angle=TAU / slices, start_angle=PI / 2 - (i + 1) * TAU / slices)
        wedge.set_fill(MONEY, 1).set_stroke(dark, 2)
        if gap:
            mid = PI / 2 - (i + 0.5) * TAU / slices
            wedge.shift(np.array([math.cos(mid), math.sin(mid), 0]) * gap)
        wedges.add(wedge)
    return wedges


def jar(width=1.6, height=2.0, color=GREY_B):
    """A simple glass jar outline (for coins dropping in)."""
    body = RoundedRectangle(width=width, height=height, corner_radius=0.25).set_stroke(color, 3).set_fill(BLUE_E, 0.12)
    lip = RoundedRectangle(width=width * 0.8, height=0.22, corner_radius=0.06).set_stroke(color, 3)
    lip.next_to(body, UP, buff=-0.05)
    return VGroup(body, lip)


def price_tag(text, color=MONEY, font_size=30):
    label = Text(text, font_size=font_size, color=BLACK, weight=BOLD)
    tag = RoundedRectangle(width=label.width + 0.7, height=label.height + 0.4, corner_radius=0.08)
    tag.set_fill(color, 1).set_stroke(width=0)
    hole = Circle(radius=0.06).set_fill(BLACK, 1).set_stroke(width=0).move_to(tag.get_left() + RIGHT * 0.2)
    label.move_to(tag).shift(RIGHT * 0.1)
    return VGroup(tag, hole, label)


def receipt(rows, width=4.6, font_size=20, title=None, rules=()):
    """The receipt: a paper strip of line items in a monospaced font.

    rows: list of (label, amount) strings; ('-', '') draws a dashed rule. The amount column
    is right-aligned. `rules` lists row indexes to draw a rule above. Returns a VGroup with
    `.paper`, `.rows` (a list of VGroups of label and amount MonoLines, None for rules)."""
    sample = MonoLine('M', font_size=font_size)
    columns = int((width - 0.5) / sample.cell)
    lines, kinds = [], []
    if title:
        lines.append(MonoLine(title.center(columns).rstrip(), font_size=font_size, color=INK))
        kinds.append('title')
    for label, amount in rows:
        if label == '-':
            lines.append(MonoLine('-' * columns, font_size=font_size, color=GREY))
            kinds.append('rule')
        else:
            lines.append(MonoLine(label + amount.rjust(columns - len(label)), font_size=font_size, color=INK))
            kinds.append('row')
    stack_lines(lines, spacing=1.6)
    body = VGroup(*lines)
    pitch = sample.line_height * 1.6
    height = pitch * len(lines) + 0.6
    paper = _receipt_paper(width, height)
    body.move_to(paper).shift(UP * 0.08)
    body.align_to(paper, LEFT).shift(RIGHT * 0.25)
    group = VGroup(paper, body)
    group.paper = paper
    group.lines = lines
    group.rows = [line if kind == 'row' else None for line, kind in zip(lines, kinds) if kind != 'title']
    return group


def _receipt_paper(width, height, teeth=14):
    top = [LEFT * width / 2 + UP * height / 2, RIGHT * width / 2 + UP * height / 2]
    bottom = []
    step = width / teeth
    for i in range(teeth + 1):
        x = width / 2 - i * step
        y = -height / 2 - (0.12 if i % 2 else 0)
        bottom.append(np.array([x, y, 0]))
    points = [top[0], top[1], np.array([width / 2, -height / 2, 0])] + bottom[1:] + [np.array([-width / 2, -height / 2, 0])]
    return Polygon(*points).set_fill(PAPER, 1).set_stroke(width=0)


# ---------------------------------------------------------------- the ledger

def balance_scale(width=2.4, color=GREY_B):
    """A balance-scale icon: VGroup(stand, beam). Tip it with `tip_scale(scale, angle)`
    (positive angle: left pan down)."""
    post = Line(DOWN * 0.9, UP * 0.6, color=color, stroke_width=5)
    base = Line(LEFT * 0.5, RIGHT * 0.5, color=color, stroke_width=6).move_to(post.get_start())
    pivot = post.get_end()
    bar = Line(pivot + LEFT * width / 2, pivot + RIGHT * width / 2, color=color, stroke_width=5)
    pans = VGroup()
    for side in (LEFT, RIGHT):
        hang = pivot + side * width / 2
        string_l = Line(hang, hang + DOWN * 0.55 + LEFT * 0.3, color=color, stroke_width=2)
        string_r = Line(hang, hang + DOWN * 0.55 + RIGHT * 0.3, color=color, stroke_width=2)
        pan = Arc(radius=0.35, start_angle=PI, angle=PI, color=color, stroke_width=4).move_to(hang + DOWN * 0.68)
        pans.add(VGroup(string_l, string_r, pan))
    beam = VGroup(bar, pans, Dot(pivot, radius=0.07, color=color))
    group = VGroup(VGroup(post, base), beam)
    group.beam = beam
    return group


def tip_scale(scale, angle, **kwargs):
    """Animation: tip a balance_scale's beam by angle (radians) about its pivot."""
    return Rotate(scale.beam, angle, about_point=scale.beam[2].get_center(), **kwargs)


def ledger(debits, credits, totals=None, font_size=22, width=7.0, headings=('Debits', 'Credits'),
           with_scale=True):
    """The ledger: a T-account with debits on the left and credits on the right, and a
    balance scale above it.

    debits/credits: lists of amount strings, or (label, amount) pairs; amounts are
    right-aligned. totals: optional (left, right) strings drawn in GOLD under a rule.
    Attributes: `.left`/`.right` (lists of MonoLines), `.totals` (VGroup of rule and the two
    total MonoLines, `.totals.left`/`.totals.right`; empty without totals), `.headings`,
    `.frame`, `.balance` (the balance scale, None without). To reveal totals later, `book.totals.set_opacity(0)`
    first, then `.animate.set_opacity(1)`. Tip the scale with tip_scale(book.balance, angle)."""
    half = width / 2
    rows = max(len(debits), len(credits), 1)
    pitch = 0.5
    top = Line(LEFT * half, RIGHT * half, color=GREY_B, stroke_width=4)
    stem_height = 0.45 + pitch * rows + (0.75 if totals else 0.2)
    stem = Line(ORIGIN, DOWN * stem_height, color=GREY_B, stroke_width=4)
    heads = VGroup(Text(headings[0], font_size=24, color=SCAFFOLD).move_to(LEFT * half / 2 + UP * 0.3),
                   Text(headings[1], font_size=24, color=SCAFFOLD).move_to(RIGHT * half / 2 + UP * 0.3))
    group = VGroup(top, stem, heads)
    cols = int((half - 0.5) / MonoLine('M', font_size=font_size).cell)

    def line_at(text, side, y, color):
        line = MonoLine(text, font_size=font_size, color=color)
        return line.set_anchor([-half + 0.25 if side < 0 else 0.25, y, 0])

    def column(entries, side):
        lines = []
        for k, entry in enumerate(entries):
            label, amount = entry if isinstance(entry, tuple) else ('', entry)
            lines.append(line_at(label + amount.rjust(cols - len(label)), side, -0.45 - pitch * k, WHITE))
        return lines

    group.left, group.right = column(debits, -1), column(credits, 1)
    group.add(*group.left, *group.right)
    group.totals = VGroup()
    if totals:
        y = -0.45 - pitch * rows
        rule = VGroup(Line([-half + 0.25, y + 0.2, 0], [-0.25, y + 0.2, 0], color=GREY_B),
                      Line([0.25, y + 0.2, 0], [half - 0.25, y + 0.2, 0], color=GREY_B))
        left = line_at(totals[0].rjust(cols), -1, y - 0.12, MONEY)
        right = line_at(totals[1].rjust(cols), 1, y - 0.12, MONEY)
        group.totals = VGroup(rule, left, right)
        group.totals.left, group.totals.right = left, right
        group.add(group.totals)
    group.frame, group.headings = VGroup(top, stem), heads
    group.balance = None
    if with_scale:
        group.balance = balance_scale().scale(0.8).next_to(heads, UP, buff=0.35)
        group.add(group.balance)
    return group


# ---------------------------------------------------------------- small pieces

def label_box(text, color=SCAFFOLD, font_size=24, fill=None, pad=0.25):
    """A rounded box with a label, for diagrams (pipelines, systems, checklist items)."""
    label = Text(text, font_size=font_size)
    box = RoundedRectangle(width=label.width + 2 * pad, height=label.height + 2 * pad * 0.8, corner_radius=0.12)
    box.set_stroke(color, 2)
    if fill:
        box.set_fill(fill, 0.25)
    label.move_to(box)
    return VGroup(box, label)


def checkmark(color=EXACT, size=0.4):
    return VMobject(color=color, stroke_width=6).set_points_as_corners(
        [LEFT * size * 0.5, DOWN * size * 0.4 + LEFT * size * 0.1, UP * size * 0.5 + RIGHT * size * 0.6])


def crossmark(color=ERROR, size=0.4):
    return VGroup(Line(UL * size / 2, DR * size / 2, color=color, stroke_width=6),
                  Line(UR * size / 2, DL * size / 2, color=color, stroke_width=6))


def caption(text, font_size=28, color=WHITE, width=12.5):
    """A one- or two-line caption, kept inside the frame."""
    return fit(Text(text, font_size=font_size, color=color), width)


def end_card(episode_text, title_text):
    """The teaser card: 'Episode 2 · Inside a double'."""
    top = Text(episode_text, font_size=30, color=SCAFFOLD)
    title = Text(title_text, font_size=48)
    return VGroup(top, title).arrange(DOWN, buff=0.3)


def title_card(title, subtitle=None):
    head = Text(title, font_size=72, weight=BOLD)
    if not subtitle:
        return VGroup(head)
    sub = Text(subtitle, font_size=30, color=SCAFFOLD)
    return VGroup(head, sub).arrange(DOWN, buff=0.35)

"""Episode 5 · Every language, the same answer. One Scene per script segment.

    python3 production/render.py 5 [-ql] [segment ...]

Shot ids in comments ([V5.1a] ...) refer to episodes/05-every-language-the-same-answer.md.
On-screen Python and its output come from snippets/ep05/. Code in other languages, and what
it printed, has no snippet: it is read from the script's ```javascript, ```java, ```c ...
blocks and their ```text outputs, so the screen always matches the script.
"""
import decimal
import re
import struct
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa: E402,F403

P1 = 'ep05/01-same-bits.py'
P2 = 'ep05/02-four-costumes.py'
P3 = 'ep05/03-integer-ceiling.py'
P4 = 'ep05/04-float-info.py'
P5 = 'ep05/05-challenge-decimal.py'
SCRIPT = sorted((ROOT / 'episodes').glob('05-*.md'))[0]


# ---------------------------------------------------------------- helpers

def script_blocks(segment):
    """Fenced blocks of one segment of the script, as (language, text) in order."""
    blocks, inside, fence, buf = [], False, None, []
    for line in SCRIPT.read_text().splitlines():
        heading = re.match(r'^### (\d+\.\d+)\s', line)
        if heading:
            inside = heading.group(1) == segment
            continue
        if line.startswith('## '):
            inside = False
        if not inside:
            continue
        if fence is None:
            m = re.match(r'^```(\w+)\s*$', line)
            if m:
                fence, buf = m.group(1), []
        elif line.startswith('```'):
            blocks.append((fence, '\n'.join(buf)))
            fence = None
        else:
            buf.append(line)
    return blocks


def other_code(segment, language, occurrence=0):
    """(code, output lines) of a non-Python sample in the script: its fenced block and the
    first ```text block after it (Go, Rust, Ruby and Swift share one output block)."""
    blocks = script_blocks(segment)
    found = [i for i, (lang, _) in enumerate(blocks) if lang == language]
    i = found[occurrence]
    output = next(text for lang, text in blocks[i + 1:] if lang == 'text')
    return blocks[i][1], output.split('\n')


def other_panel(source, language, font_size=22):
    """code_panel for another language (same look: monokai on the dark panel)."""
    return Code(code_string=source.strip('\n'), language=language, formatter_style='monokai',
                add_line_numbers=False, background='rectangle',
                background_config={'fill_color': PANEL, 'stroke_color': GREY_D, 'stroke_width': 1},
                paragraph_config={'font_size': font_size, 'font': MONO})


def type_out(line, run_time=None):
    glyphs = line.glyphs
    run_time = run_time or max(0.3, min(1.6, len(glyphs) * 0.035))
    return LaggedStart(*[FadeIn(g, run_time=0.05) for g in glyphs], lag_ratio=1.0, run_time=run_time)


def typed(scene, line, run_time=None, *also):
    """Type a MonoLine out, then keep it on screen as one mobject (so it can move later)."""
    scene.play(type_out(line, run_time), *also)
    scene.remove(*line.glyphs)
    scene.add(line)


def wipe(scene, *keep, run_time=0.6):
    gone = [m for m in scene.mobjects if m not in keep]
    if gone:
        scene.play(*[FadeOut(m) for m in gone], run_time=run_time)
        scene.remove(*gone)


def value_of(line):
    """The printed value at the end of a labelled output line ('label: value')."""
    return line.split(':', 1)[1].strip() if ':' in line else line.split()[-1]


GROUP_COLOURS = (GREY_B, FOCUS, STORED)     # sign, exponent, fraction (as in episode 2)


def bit_row(hexstr, cell=0.17, gap=0.12):
    """The 64 boxes of a double: 1 sign, 11 exponent and 52 fraction bits, filled where the
    bit is 1. `row.boxes[i]` is bit i (0 = sign); `row.groups` the three groups."""
    bits = f'{int(hexstr, 16):064b}'
    boxes, x = VGroup(), 0.0
    for i, b in enumerate(bits):
        if i in (1, 12):
            x += gap
        colour = GROUP_COLOURS[0 if i == 0 else 1 if i < 12 else 2]
        sq = Square(cell * 0.8).set_stroke(colour, 1.5).set_fill(colour, 0.85 if b == '1' else 0)
        boxes.add(sq.move_to(RIGHT * x))
        x += cell
    boxes.center()
    row = VGroup(boxes)
    row.boxes, row.bits, row.hex = boxes, bits, hexstr
    row.groups = VGroup(boxes[0:1], boxes[1:12], boxes[12:64])
    return row


def hex_labels(row, font_size=20):
    labels = VGroup()
    for k, ch in enumerate(row.hex):
        nibble = row.boxes[4 * k:4 * k + 4]
        labels.add(Text(ch, font=MONO, font_size=font_size, color=GREY_A).next_to(nibble, DOWN, buff=0.12))
    return labels


def register(layout, width, height=0.3, hex_digits=False):
    """A register diagram: bars for sign, exponent and fraction in proportion to layout."""
    total = sum(layout)
    parts, x = VGroup(), -width / 2
    for k, bits in enumerate(layout):
        w = width * bits / total
        bar = Rectangle(width=w, height=height).set_fill(GROUP_COLOURS[k], 0.8).set_stroke(BLACK, 1)
        parts.add(bar.move_to(RIGHT * (x + w / 2)))
        x += w
    if hex_digits:   # base 16: the fraction is a row of hex digits
        frac = parts[2]
        for j in range(1, layout[2] // 4):
            px = frac.get_left()[0] + frac.width * j / (layout[2] // 4)
            parts.add(Line([px, -height / 2, 0], [px, height / 2, 0], color=BLACK, stroke_width=1.5))
    return parts


def chip_icon(size=0.9, label=None, font_size=18):
    """A plain processor chip: a square with pins (no logos)."""
    body = RoundedRectangle(width=size, height=size, corner_radius=0.08).set_fill(GREY_E, 1).set_stroke(GREY_B, 2)
    pins = VGroup()
    for t in np.linspace(-0.3, 0.3, 4) * size:
        for side in (UP, DOWN, LEFT, RIGHT):
            along = RIGHT if side[1] else UP
            start = side * size / 2 + along * t
            pins.add(Line(start, start + side * size * 0.14, color=GREY_B, stroke_width=3))
    group = VGroup(pins, body)
    if label:
        text = Text(label, font_size=font_size, color=WHITE).move_to(body)
        if text.width > size * 0.9:
            body.stretch_to_fit_width(text.width + 0.3)
            pins.stretch_to_fit_width(text.width + 0.3 + size * 0.28)
        group.add(text)
    return group


def bracket(mob, direction=DOWN, buff=0.1, color=SCAFFOLD):
    """A square bracket along one side of a mobject (no TeX)."""
    if direction[1]:
        a, b = mob.get_corner(direction + LEFT), mob.get_corner(direction + RIGHT)
    else:
        a, b = mob.get_corner(direction + UP), mob.get_corner(direction + DOWN)
    a, b = a + direction * buff, b + direction * buff
    tick = direction * 0.12
    return VMobject(color=color, stroke_width=3).set_points_as_corners([a - tick * 0, a + tick, b + tick, b - tick * 0])


def mini_tile(name, content=None, width=1.35, height=1.45):
    """The small identical tile each language becomes at the end of 5.1 (and returns in 5.2)."""
    frame = RoundedRectangle(width=width, height=height, corner_radius=0.1).set_fill(PANEL, 1).set_stroke(GREY_D, 1.5)
    label = Text(name, font_size=18, color=GREY_A).next_to(frame.get_top(), DOWN, buff=0.12)
    if content is None:
        content = Text('4', font=MONO, font_size=44, color=ERROR)
    content.move_to(frame).shift(DOWN * 0.18)
    tile = VGroup(frame, label, content)
    tile.frame, tile.label, tile.content = frame, label, content
    return tile


def lang_tile(name, lines, width=3.3, height=1.72):
    """One cold-open panel: the language's name and its output, typed in later."""
    bg = RoundedRectangle(width=width, height=height, corner_radius=0.12).set_fill(PANEL, 1).set_stroke(GREY_D, 1.5)
    label = Text(name, font_size=20, color=SCAFFOLD)
    label.move_to(bg.get_corner(UL) + RIGHT * 0.18 + DOWN * 0.26, aligned_edge=LEFT)
    out = [MonoLine(l, font_size=18) for l in lines]
    stack_lines(out)
    VGroup(*out).shift(bg.get_corner(UL) + RIGHT * 0.2 + DOWN * 0.68 - out[0].anchor())
    ask = Text('?', font_size=30, color=DIM).move_to(bg).shift(DOWN * 0.2)
    tile = VGroup(bg, label, *out)
    tile.bg, tile.label, tile.lines, tile.ask = bg, label, out, ask
    return tile


def mask_shape(width=4.2, height=1.25, color=FOCUS):
    """A costume drawn as a mask: an opaque panel with two eye holes."""
    face = RoundedRectangle(width=width, height=height, corner_radius=height / 2).set_fill(PANEL, 1).set_stroke(color, 3)
    eyes = VGroup(*[Ellipse(width=0.13 * width, height=0.2 * height).set_fill(BLACK, 1).set_stroke(color, 2)
                    .move_to(face.get_center() + RIGHT * dx + UP * 0.22 * height) for dx in (-0.33 * width, 0.33 * width)])
    return VGroup(face, eyes)


def person(color=GREY_B, coat=GREY_D):
    """A plain figure (no likeness): head and shoulders."""
    head = Circle(radius=0.38).set_fill(color, 1).set_stroke(width=0)
    body = RoundedRectangle(width=1.5, height=1.5, corner_radius=0.45).set_fill(coat, 1).set_stroke(color, 2)
    body.next_to(head, DOWN, buff=0.08)
    return VGroup(body, head)


# ---------------------------------------------------------------- 5.1

GRID = [('JavaScript', 'javascript'), ('Java', 'java'), ('Go', 'go'), ('Rust', 'rust'),
        ('Ruby', 'ruby'), ('Swift', 'swift'), ('SQLite', 'sql'), ('C', 'c')]
SPOT = DOWN * 2.15                      # where the running sample's code is shown


class Segment_5_1(Segment):
    """Cold open: eight languages and a database print the same digits."""
    EPISODE, SEGMENT = 5, '5.1'

    def construct(self):
        # The grid follows the narration's order (C is discussed last), left to right.
        tiles = {}
        for name, lang in GRID:
            code, out = other_code('5.1', lang)
            tile = lang_tile(name, out)
            tile.code, tile.lang = code, lang
            tiles[name] = tile
        grid = VGroup(*tiles.values()).arrange_in_grid(rows=2, cols=4, buff=(0.15, 0.25)).to_edge(UP, buff=0.3)
        for t in tiles.values():
            t.ask.move_to(t.bg).shift(DOWN * 0.2)

        # Opening question: is it only Python?
        python = Text('Python', font_size=56, weight=BOLD)
        mark = Text('?', font_size=72, color=FOCUS).next_to(python, RIGHT, buff=0.25)
        self.play(FadeIn(python, shift=UP * 0.3))
        self.at('is this just a Python problem?')
        self.play(FadeIn(mark, scale=1.6))

        # [V5.1a] eight panels, one per language, names in plain text
        self.at('Maybe some other language')
        self.play(FadeOut(VGroup(python, mark), shift=DOWN * 0.5))
        self.play(LaggedStart(*[FadeIn(VGroup(t.bg, t.label, t.ask), scale=0.9) for t in tiles.values()],
                              lag_ratio=0.12), run_time=1.6)

        state = {'panel': None, 'tile': None}

        def start(name, run_time=0.5):
            tile = tiles[name]
            panel = other_panel(tile.code, tile.lang, 22).move_to(SPOT)
            anims = [FadeIn(panel, scale=0.5, target_position=tile.bg.get_center()),
                     tile.bg.animate.set_stroke(FOCUS, 3), FadeOut(tile.ask)]
            if state['panel'] is not None:
                anims += [FadeOut(state['panel']), state['tile'].bg.animate.set_stroke(GREY_D, 1.5)]
            self.play(*anims, run_time=run_time)
            state['panel'], state['tile'] = panel, tile
            return tile, panel

        # [V5.1a] the samples run one after another, their output typing out
        self.at("Let's ask. JavaScript")
        js, _ = start('JavaScript')
        typed(self, js.lines[0], 0.8)
        self.at("And no, it's not equal")
        typed(self, js.lines[1], 0.4)
        self.at('Java: the same digits')
        java, _ = start('Java')
        typed(self, java.lines[0], 0.7)
        typed(self, java.lines[1], 0.3)
        self.at('Go, Rust')
        for name in ('Go', 'Rust', 'Ruby', 'Swift'):
            tile, _ = start(name, run_time=0.3)
            self.play(type_out(tile.lines[0], 0.45))
            self.play(type_out(tile.lines[1], 0.2))
            self.remove(*tile.lines[0].glyphs, *tile.lines[1].glyphs)
            self.add(tile.lines[0], tile.lines[1])
        self.at('Even the database')
        sqlite, _ = start('SQLite')
        self.at('gives the same digits')
        typed(self, sqlite.lines[0], 0.8)
        self.at("says they aren't equal")
        typed(self, sqlite.lines[1], 0.3)

        # C: six places hide the four; seventeen digits bring it back
        self.at('C is the odd one out')
        c, cpanel = start('C')
        self.at('Its usual way of printing')
        box = line_highlight(cpanel, 1)
        self.play(Create(box), run_time=0.4)
        typed(self, c.lines[0], 0.5)
        # [V5.1c] a yellow question mark: hiding?
        ask = Text('?', font_size=30, color=FOCUS).next_to(c.lines[0].glyphs, RIGHT, buff=0.25)
        hiding = Text('hiding?', font_size=18, color=FOCUS).next_to(ask, RIGHT, buff=0.12)
        self.play(FadeIn(ask, scale=1.8), FadeIn(hiding, shift=LEFT * 0.2))
        self.at('seventeen significant digits')
        self.play(box.animate.move_to([box.get_x(), line_highlight(cpanel, 2).get_y(), 0]), run_time=0.4)
        typed(self, c.lines[1], 0.8)
        self.at('And the comparison? Zero')
        self.play(box.animate.move_to([box.get_x(), line_highlight(cpanel, 3).get_y(), 0]), run_time=0.4)
        typed(self, c.lines[2], 0.3)

        # [V5.1b] the panels line up as a table: the trailing 4s fall into one column
        self.at('Eight languages and a database')
        self.play(FadeOut(cpanel), FadeOut(box), c.bg.animate.set_stroke(GREY_D, 1.5), run_time=0.5)
        name_x, value_x, pitch, top = -1.8, -1.4, 0.56, 3.3
        answer_x = value_x + 19 * MonoLine('M', font_size=22).cell + 0.6
        rows, moves = [], []
        for k, (name, _) in enumerate(GRID):
            t = tiles[name]
            y = top - pitch * k
            src_value = t.lines[1] if name == 'C' else t.lines[0]
            label = Text(name, font_size=22, color=GREY_A).move_to([name_x, y, 0], aligned_edge=RIGHT)
            value = MonoLine(src_value.source, font_size=22).set_anchor([value_x, y, 0])
            answer = MonoLine(t.lines[-1].source, font_size=22).set_anchor([answer_x, y, 0])
            rows.append(VGroup(label, value, answer))
            moves += [ReplacementTransform(t.label, label), ReplacementTransform(src_value, value),
                      ReplacementTransform(t.lines[-1], answer), FadeOut(t.bg)]
        moves += [FadeOut(tiles['C'].lines[0]), FadeOut(ask), FadeOut(hiding)]
        self.play(*moves, run_time=1.6)
        self.at('down to the last digit')
        fours = VGroup(*[r[1].glyphs[-1] for r in rows])
        self.play(*[r[1].animate.set_color(ERROR) for r in rows], *[r[2].animate.set_color(ERROR) for r in rows],
                  run_time=0.6)
        column = SurroundingRectangle(fours, color=ERROR, buff=0.08)
        self.play(Create(column), *[f.animate.scale(1.3) for f in fours], run_time=0.6)
        self.play(*[f.animate.scale(1 / 1.3) for f in fours], run_time=0.3)

        # [V5.1d] a ninth panel slides in: Python, with q05-02's answers
        self.at("That's not a coincidence")
        y = top - pitch * len(GRID)
        py_value = value_of(output_line(P2, 'shortest repr'))
        py_answer = value_of(output_line(P2, 'is it 0.3?'))
        py = VGroup(Text('Python', font_size=22, color=GREY_A).move_to([name_x, y, 0], aligned_edge=RIGHT),
                    MonoLine(py_value, font_size=22, color=ERROR).set_anchor([value_x, y, 0]),
                    MonoLine(py_answer, font_size=22, color=ERROR).set_anchor([answer_x, y, 0]))
        self.play(FadeIn(py, shift=LEFT * 3), column.animate.stretch_to_fit_height(
            column.height + pitch, about_edge=UP), run_time=0.9)
        rows.append(py)

        # All nine shrink into a single row of identical tiles
        self.at('eight copies of the same bug')
        minis = VGroup(*[mini_tile(n) for n, _ in GRID], mini_tile('Python')).arrange(RIGHT, buff=0.1)
        minis.move_to(ORIGIN)
        self.play(FadeOut(column), *[ReplacementTransform(r, m) for r, m in zip(rows, minis)], run_time=1.4)
        self.finish()


# ---------------------------------------------------------------- 5.2

class Segment_5_2(Segment):
    """Same bits everywhere (q05-01)."""
    EPISODE, SEGMENT = 5, '5.2'

    def construct(self):
        # [V5.2a] code panel and console; QR q05-01
        code = code_panel(snippet_find(P1, 'def bits', 'return struct'), font_size=24).to_corner(UL, buff=0.4)
        out = output_console(P1, font_size=24).next_to(code, DOWN, buff=0.4, aligned_edge=LEFT)
        card = qr_card('q05-01')
        self.play(FadeIn(code), FadeIn(out.background), FadeIn(card, shift=UP * 0.2))
        self.at('This code takes a')
        box = line_highlight(code, 1)
        self.play(Create(box))
        for line in out.lines:
            typed(self, line, 0.5)

        # [V5.2a] the hex for 0.1 expands into 64 boxes: sign, exponent, fraction
        self.at('Zero point one is three')
        self.play(FadeOut(card), FadeOut(code), FadeOut(box), run_time=0.5)
        self.play(out.animate.scale(0.85).to_edge(UP, buff=0.25).set_x(0), run_time=0.7)
        hexes = [l.source.split()[-1] for l in out.lines]
        row_x = 0.7
        tenth = bit_row(hexes[0]).move_to([row_x, 0.4, 0])
        tenth_hex = hex_labels(tenth)
        src = out.lines[0].part(hexes[0])
        self.play(TransformFromCopy(src, tenth_hex), run_time=0.9)
        self.play(LaggedStart(*[GrowFromCenter(b) for b in tenth.boxes], lag_ratio=0.02), run_time=1.2)
        groups = VGroup(Text('sign', font_size=18, color=GREY_B), Text('exponent', font_size=18, color=FOCUS),
                        Text('fraction', font_size=18, color=STORED))
        for label, g in zip(groups, tenth.groups):
            label.next_to(g, UP, buff=0.15)
        groups[0].align_to(tenth.groups[0], LEFT)
        name = Text('0.1', font_size=22).next_to(tenth.boxes, LEFT, buff=0.35)
        self.play(FadeIn(groups), FadeIn(name), run_time=0.6)

        # the repeating pattern of one tenth, rounded off at the end: 9 becomes a
        self.at('recognise that repeating pattern')
        nines = SurroundingRectangle(VGroup(tenth.boxes[12:60], tenth_hex[3:15]), color=FOCUS, buff=0.06)
        nines_label = Text('the repeating pattern of one tenth', font_size=20, color=FOCUS)
        nines_label.next_to(nines, DOWN, buff=0.15)
        self.play(Create(nines), FadeIn(nines_label))
        self.at('the last digit is an a')
        last = SurroundingRectangle(VGroup(tenth.boxes[60:64], tenth_hex[15]), color=ERROR, buff=0.06)
        last_label = Text('rounded: 9 → a', font_size=20, color=ERROR).next_to(last, DOWN, buff=0.15)
        last_label.align_to(last, RIGHT)
        nines_label.generate_target().align_to(nines, LEFT)
        self.play(Create(last), FadeIn(last_label), MoveToTarget(nines_label))

        # [V5.2b] the sum and 0.3, one above the other
        self.at('Now compare the sum')
        self.play(FadeOut(VGroup(tenth, tenth_hex, name, nines, nines_label, last, last_label)), run_time=0.5)
        rows = []
        for k, (index, y) in enumerate(((2, 0.5), (3, -1.15))):
            row = bit_row(hexes[index]).move_to([row_x, y, 0])
            labels = hex_labels(row)
            tag = Text(out.lines[index].source.rsplit(' ', 1)[0].strip(), font_size=22).next_to(row.boxes, LEFT, buff=0.35)
            rows.append((row, labels, tag))
            self.play(TransformFromCopy(out.lines[index].part(hexes[index]), labels), FadeIn(tag), run_time=0.7)
            self.play(LaggedStart(*[GrowFromCenter(b) for b in row.boxes], lag_ratio=0.015), run_time=0.9)
        groups.generate_target()
        for label, g in zip(groups.target, rows[0][0].groups):
            label.next_to(g, UP, buff=0.15)
        groups.target[0].align_to(rows[0][0].groups[0], LEFT)
        self.play(MoveToTarget(groups), run_time=0.4)

        self.at('Every hex digit is the same')
        (a, a_hex, _), (b, b_hex, _) = rows
        self.play(LaggedStart(*[AnimationGroup(a_hex[k].animate.set_color(EXACT), b_hex[k].animate.set_color(EXACT))
                                for k in range(15)], lag_ratio=0.15), run_time=1.6)
        self.at('a four for the sum')
        self.play(a_hex[15].animate.set_color(ERROR).scale(1.4), b_hex[15].animate.set_color(ERROR).scale(1.4))
        # the final three bits glow red
        glow = [box.animate.set_stroke(ERROR, 4).set_fill(ERROR, 0.9 if bit == '1' else 0.15)
                for row in (a, b) for box, bit in zip(row.boxes[61:], row.bits[61:])]
        self.play(*glow, run_time=0.6)

        # one step on the float line: two neighbouring doubles
        self.at('one step on the')
        line = FloatLine('0.29999999999999993', '0.30000000000000016', width=9.0,
                         labels={0.3: '0.3', 0.1 + 0.2: '0.1 + 0.2'}).move_to([row_x, -2.95, 0])
        self.play(Create(line.axis), FadeIn(line.ticks), FadeIn(line.labels))
        step = CurvedArrow(line.point(0.3) + UP * 0.3, line.point(0.1 + 0.2) + UP * 0.3, angle=-PI / 2.5,
                           color=FOCUS, stroke_width=3, tip_length=0.15)
        self.play(Create(step))
        self.at('Two neighbouring doubles')
        self.play(*[Indicate(t, color=FOCUS, scale_factor=1.5) for t in line.ticks
                    if line.tick_values.index(line.nearest(0.3)) <= list(line.ticks).index(t)
                    <= line.tick_values.index(line.nearest(0.1 + 0.2))])

        # [V5.2c] eight language tiles drop the same 64-box pattern into one slot
        self.at('JavaScript, Java, C')
        wipe(self, run_time=0.5)
        key = bit_row(hexes[2]).move_to([0, -1.0, 0])
        slot = RoundedRectangle(width=key.width + 0.5, height=0.6, corner_radius=0.12).move_to(key)
        slot.set_stroke(GREY_B, 3).set_fill(PANEL, 1)
        ghost = key.copy().set_opacity(0.18)
        slot_label = Text('binary64', font=MONO, font_size=22, color=SCAFFOLD).next_to(slot, DOWN, buff=0.2)
        names = [n for n, _ in GRID[:-1]]
        names.insert(2, 'C')      # the order the narration names them
        minis = VGroup(*[mini_tile(n, key.copy().scale_to_fit_width(1.1)) for n in names]).arrange(RIGHT, buff=0.18)
        minis.to_edge(UP, buff=0.6)
        self.play(FadeIn(slot), FadeIn(ghost), FadeIn(slot_label),
                  LaggedStart(*[FadeIn(m, shift=DOWN * 0.6) for m in minis], lag_ratio=0.12), run_time=1.8)
        self.at('all of them store these exact bits')
        for m in minis:
            stripe = m.content
            self.play(stripe.animate.become(key.copy()), run_time=0.45, rate_func=rate_functions.ease_in_quad)
            self.play(slot.animate.set_stroke(EXACT, 4), run_time=0.15)
            self.play(slot.animate.set_stroke(GREY_B, 3), run_time=0.15)
        self.at('They get identical bits')
        tick = checkmark(size=0.6).next_to(slot_label, RIGHT, buff=0.3)
        self.play(slot.animate.set_stroke(EXACT, 4), Create(tick))
        self.finish()


# ---------------------------------------------------------------- 5.3

YEAR0, YEAR1 = 1950, 1990


class Segment_5_3(Segment):
    """Before the standard: every maker had its own floating point, until IEEE 754."""
    EPISODE, SEGMENT = 5, '5.3'

    def construct(self):
        # [V5.3a] a timeline from 1950 to 1990
        axis_y, x0, x1 = -3.15, -6.2, 6.2

        def year_x(year):
            return x0 + (x1 - x0) * (year - YEAR0) / (YEAR1 - YEAR0)

        axis = Line([x0, axis_y, 0], [x1, axis_y, 0], color=SCAFFOLD, stroke_width=3)
        decades = VGroup()
        for year in range(YEAR0, YEAR1 + 1, 10):
            tick = Line(DOWN * 0.12, UP * 0.12, color=SCAFFOLD, stroke_width=3).move_to([year_x(year), axis_y, 0])
            decades.add(tick, Text(str(year), font_size=20, color=SCAFFOLD).next_to(tick, DOWN, buff=0.1))
        self.play(Create(axis), FadeIn(decades), run_time=1.0)

        # the machines, each with its own register layout (proportions only; no figures drawn)
        specs = [('IBM System/360', 'base 16', (1, 7, 56), True),
                 ('DEC VAX', 'its own formats', (1, 8, 55), False),
                 ('Cray', 'its own formats', (1, 15, 48), False),
                 ('others…', None, (1, 9, 38), False)]
        machines = VGroup()
        for title, sub, layout, hexd in specs:
            box = RoundedRectangle(width=3.0, height=1.9, corner_radius=0.12).set_fill(PANEL, 1).set_stroke(GREY_B, 2)
            head = Text(title, font_size=22).move_to(box.get_top() + DOWN * 0.35)
            parts = VGroup(box, head)
            if sub:
                parts.add(Text(sub, font_size=20, color=SCAFFOLD).next_to(head, DOWN, buff=0.12))
            reg = register(layout, 2.5, hex_digits=hexd).move_to(box.get_bottom() + UP * 0.42)
            parts.add(reg)
            parts.box, parts.reg = box, reg
            machines.add(parts)
        machines.arrange(RIGHT, buff=0.22).move_to(UP * 1.45)

        self.at('Through the nineteen sixties and seventies')
        era = Line([year_x(1960), axis_y + 0.2, 0], [year_x(1980), axis_y + 0.2, 0], color=ERROR, stroke_width=8)
        self.play(Create(era))
        for m, phrase in zip(machines, ('big machines worked in base sixteen', "Digital Equipment's",
                                        "Cray's supercomputers", 'They differed in how many bits')):
            self.at(phrase)
            self.play(FadeIn(m, shift=DOWN * 0.3), run_time=0.6)
        self.play(LaggedStart(*[Indicate(m.reg, color=FOCUS, scale_factor=1.15) for m in machines], lag_ratio=0.2))

        # [V5.3b] the same calculation fed to every machine; the last digit differs
        self.at('So the same program')
        program = label_box('0.1 + 0.2', color=FOCUS, font_size=24).move_to(UP * 3.45)
        self.play(FadeIn(program, shift=DOWN * 0.2))
        copies = [program.copy() for _ in machines]
        self.play(*[c.animate.move_to(m.box).scale(0.3).set_opacity(0) for c, m in zip(copies, machines)],
                  run_time=0.9)
        self.remove(*copies)
        colours = [STORED, MONEY, TEAL, PURPLE]
        results = VGroup()
        for m, colour in zip(machines, colours):
            digits = MonoLine('0.30000000000000', font_size=18)
            last = Square(0.27).set_fill(colour, 1).set_stroke(width=0)
            mark = Text('?', font=MONO, font_size=18, color=BLACK).move_to(last)
            last_digit = VGroup(last, mark).next_to(digits.glyphs, RIGHT, buff=0.05)
            result = VGroup(digits, last_digit).next_to(m.box, DOWN, buff=0.3)
            result.last = last_digit
            results.add(result)
        self.at('could print different answers')
        self.play(LaggedStart(*[FadeIn(r, shift=DOWN * 0.2) for r in results], lag_ratio=0.25), run_time=1.2)
        self.at('Moving numerical software')
        hop = label_box('program', font_size=20, color=FOCUS).next_to(machines[0].box, UP, buff=0.12)
        self.play(FadeOut(program), FadeIn(hop))
        for k in range(1, 4):
            self.play(hop.animate.next_to(machines[k].box, UP, buff=0.12), run_time=0.5)
            self.play(Indicate(results[k].last, color=colours[k], scale_factor=1.5), run_time=0.4)

        # [V5.3c] the standard: Kahan, Turing Award, the 8087, IEEE 754
        self.at('In the late nineteen seventies')
        self.play(FadeOut(results), FadeOut(hop), machines.animate.scale(0.8).to_edge(UP, buff=0.2), run_time=0.9)

        def drop_marker(year, source):
            dot = Dot(source.get_bottom() + DOWN * 0.1, radius=0.09, color=FOCUS)
            self.play(FadeIn(dot), run_time=0.2)
            self.play(dot.animate.move_to([year_x(year), axis_y, 0]), run_time=0.7)
            return dot

        col = {1980: -4.5, 1985: 0.0, 1989: 4.5}
        years = {y: Text(str(y), font_size=24, color=FOCUS).move_to([x, 1.05, 0]) for y, x in col.items()}
        self.at('Its principal architect')
        kahan = Text('William Kahan,\nprincipal architect', font_size=20, line_spacing=0.8)
        name_card = VGroup(SurroundingRectangle(kahan, color=GREY_B, buff=0.18, corner_radius=0.1), kahan)
        name_card.move_to([col[1985], -1.0, 0])
        self.play(FadeIn(name_card, shift=UP * 0.2))
        self.at('received the Turing Award')
        turing = Text('Turing Award', font_size=24).move_to([col[1989], 0.25, 0])
        self.play(FadeIn(years[1989]), FadeIn(turing, shift=UP * 0.2))
        dot89 = drop_marker(1989, turing)
        self.at('Intel built an early draft')
        chip = chip_icon(0.8).move_to([col[1980], 0.25, 0])
        intel = Text('Intel 8087 coprocessor\nimplements a draft', font_size=20, line_spacing=0.8).next_to(chip, DOWN, buff=0.3)
        self.play(FadeIn(years[1980]), FadeIn(chip, scale=0.6), FadeIn(intel, shift=UP * 0.2))
        dot80 = drop_marker(1980, intel)
        self.at('in 1985 the standard was published')
        published = Text('IEEE 754 published', font_size=26, weight=BOLD).move_to([col[1985], 0.25, 0])
        self.play(FadeIn(years[1985]), FadeIn(published, scale=1.2))
        dot85 = drop_marker(1985, name_card)
        after = Line([year_x(1985), axis_y + 0.2, 0], [year_x(YEAR1), axis_y + 0.2, 0], color=EXACT, stroke_width=8)
        self.play(Create(after), era.animate.put_start_and_end_on(era.get_start(), [year_x(1985), axis_y + 0.2, 0]))

        # [V5.3d] it pinned down everything: every register becomes 1-11-52
        self.at('It pinned down everything')
        events = VGroup(*years.values(), name_card, turing, chip, intel, published)
        self.play(FadeOut(events), run_time=0.6)
        promises = VGroup(*[label_box(t, font_size=24, color=EXACT) for t in
                            ('the formats', 'the rounding rules', 'the special values',
                             'correctly rounded  +  −  ×  ÷  √')])
        promises.arrange_in_grid(rows=2, cols=2, buff=(0.5, 0.4)).move_to(DOWN * 0.55)
        self.at('the formats')
        self.play(*[Transform(m.reg, register((1, 11, 52), m.reg.width).move_to(m.reg)) for m in machines],
                  FadeIn(promises[0], shift=UP * 0.2), run_time=1.2)
        self.at('the rounding rules')
        self.play(FadeIn(promises[1], shift=UP * 0.2))
        self.at('the special values')
        self.play(FadeIn(promises[2], shift=UP * 0.2))
        self.at('and the promise')
        self.play(FadeIn(promises[3], shift=UP * 0.2))

        self.at('Today, every mainstream processor')
        self.play(FadeOut(promises), run_time=0.5)
        word = Text('binary64', font=MONO, font_size=80, color=STORED, weight=BOLD)
        stamp = VGroup(SurroundingRectangle(word, color=STORED, buff=0.3, corner_radius=0.15, stroke_width=8), word)
        stamp.rotate(-8 * DEGREES).move_to(DOWN * 0.55)
        self.play(FadeIn(stamp, scale=2.2), run_time=0.5, rate_func=rate_functions.ease_in_quad)
        self.play(Indicate(VGroup(*[m.reg for m in machines]), color=STORED, scale_factor=1.05))

        # The languages hand their arithmetic to the chip
        self.at("That's why the answers agree")
        wipe(self, run_time=0.6)
        chip = chip_icon(1.8, 'binary64', font_size=26)
        names = [n for n, _ in GRID] + ['Python']
        ring = VGroup(*[Text(n, font_size=24, color=GREY_A) for n in names])
        for k, t in enumerate(ring):
            angle = PI / 2 - k * TAU / len(ring)
            t.move_to(np.array([4.6 * math.cos(angle), 3.0 * math.sin(angle), 0]))
        self.play(FadeIn(chip, scale=0.7), LaggedStart(*[FadeIn(t) for t in ring], lag_ratio=0.08), run_time=1.4)
        self.at("The languages aren't doing arithmetic")
        arrows = VGroup(*[Arrow(t.get_center(), ORIGIN, buff=0, color=SCAFFOLD, stroke_width=3)
                          .put_start_and_end_on(t.get_center() + (ORIGIN - t.get_center()) * 0.22,
                                                (t.get_center()) * 0.36) for t in ring])
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.06), run_time=1.2)
        self.at('The chip is')
        self.play(chip[1].animate.set_stroke(STORED, 5), chip[0].animate.set_color(STORED),
                  *[a.animate.set_color(STORED) for a in arrows], run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 5.4

class Segment_5_4(Segment):
    """What float really is (q05-04): sys.float_info describes the hardware's double."""
    EPISODE, SEGMENT = 5, '5.4'

    def construct(self):
        # [V5.4a] code panel, console and QR q05-04
        code = code_panel(snippet_find(P4, 'info = sys', 'info.mant_dig', 'info.dig'), font_size=22)
        code.to_corner(UL, buff=0.35)
        out = output_console(P4, font_size=20).next_to(code, DOWN, buff=0.35, aligned_edge=LEFT)
        card = qr_card('q05-04')
        self.play(FadeIn(code), FadeIn(out.background), FadeIn(card, shift=UP * 0.2))
        self.at('a record called')
        for line in out.lines:
            typed(self, line, 0.55)

        # the output lines spread out, each to the part of the double it describes
        self.at('Fifty-three significant bits')
        lines = out.lines
        row = bit_row('0' * 16).move_to([0.55, 1.45, 0])
        self.play(FadeOut(card), FadeOut(code), FadeOut(out.background),
                  lines[0].animate.set_anchor([-6.6, 3.45, 0]), lines[1].animate.set_anchor([-6.6, 0.1, 0]),
                  lines[4].animate.set_anchor([-6.6, -1.35, 0]), lines[3].animate.set_anchor([-6.6, -3.45, 0]),
                  lines[2].animate.set_opacity(0), run_time=1.0)
        self.play(LaggedStart(*[GrowFromCenter(b) for b in row.boxes], lag_ratio=0.01), run_time=0.9)
        ghost = DashedVMobject(Square(row.boxes[0].width).set_stroke(STORED, 2), num_dashes=8)
        ghost.next_to(row.groups[2], UP, buff=0.18).align_to(row.groups[2], LEFT)
        implicit = Text('implicit 1', font_size=18, color=STORED).next_to(ghost, RIGHT, buff=0.15)
        stored = Text('52 stored', font_size=20, color=STORED).next_to(row.groups[2], DOWN, buff=0.15)
        frac_bracket = bracket(VGroup(row.groups[2], ghost), UP, buff=0.12, color=FOCUS)
        fifty3 = lines[0].part(value_of(lines[0].source))
        link0 = Line(fifty3.get_bottom() + DOWN * 0.08, frac_bracket.get_top() + LEFT * 2.5, color=FOCUS, stroke_width=3)
        self.play(row.groups[2].animate.set_fill(STORED, 0.35), FadeIn(stored))
        self.at('plus the leading one')
        self.play(Create(ghost), FadeIn(implicit), Create(frac_bracket), Create(link0), fifty3.animate.set_color(FOCUS))

        # [V5.4b] 15 digits survive a round trip
        self.at('Fifteen')
        fifteen = lines[1].part(value_of(lines[1].source))
        note = Text('15 decimal digits always survive a round trip through a double', font_size=22, color=FOCUS)
        note.next_to(lines[1], DOWN, buff=0.35).align_to(lines[1], LEFT).shift(RIGHT * 0.4)
        link1 = Line(fifteen.get_bottom() + DOWN * 0.06, [fifteen.get_x(), note.get_top()[1] + 0.06, 0],
                     color=FOCUS, stroke_width=3)
        self.play(fifteen.animate.set_color(FOCUS), Create(link1), FadeIn(note, shift=RIGHT * 0.3))

        # radix 2: a large "base 2"
        self.at('A radix, or base')
        two = lines[4].part(value_of(lines[4].source))
        base = Text('base 2', font_size=48, weight=BOLD, color=FOCUS).move_to([0.4, -1.35, 0])
        link4 = Line(two.get_right() + RIGHT * 0.1, base.get_left() + LEFT * 0.12, color=FOCUS, stroke_width=3)
        self.play(two.animate.set_color(FOCUS), Create(link4), FadeIn(base, scale=0.6))

        # epsilon: the gap between 1 and the next tick on the float line
        self.at('And epsilon')
        eps = float(value_of(lines[3].source))
        ticks = [1 - eps, 1 - eps / 2, 1.0, 1 + eps, 1 + 2 * eps]   # doubles near 1, from the printed epsilon
        fl = FloatLine(Fraction(1) - Fraction(eps) * Fraction(5, 4), Fraction(1) + Fraction(eps) * Fraction(9, 4),
                       width=4.2, ticks=ticks).move_to([4.5, -2.3, 0])
        one = Text('1', font=MONO, font_size=20, color=SCAFFOLD).next_to(fl.point(1.0), UP, buff=0.3)
        fl.labels.add(one)
        gap = bracket(Line(fl.point(1.0), fl.point(1 + eps)), DOWN, buff=0.3, color=FOCUS)
        eps_text = lines[3].part(value_of(lines[3].source))
        link3 = Line(eps_text.get_right() + RIGHT * 0.1, gap.get_bottom() + DOWN * 0.04,
                     color=FOCUS, stroke_width=3)
        self.play(Create(fl.axis), FadeIn(fl.ticks), FadeIn(fl.labels), run_time=0.7)
        self.play(eps_text.animate.set_color(FOCUS), Create(gap), Create(link3))
        self.play(Indicate(fl.ticks[3], color=FOCUS, scale_factor=1.6))

        # [V5.4c] the largest double, written out in full, scrolls past
        self.at("Python didn't choose")
        keep = [lines[0], lines[1], lines[4], lines[3]]
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep],
                  VGroup(*keep).animate.set_opacity(0.35), run_time=0.6)
        big = lines[2].copy().set_opacity(1).set_anchor([-6.6, 2.1, 0])
        lines[2].set_anchor([-6.6, 2.1, 0])
        self.play(FadeIn(big, shift=RIGHT * 0.3), *[l.animate.shift(DOWN * 0.0) for l in keep], run_time=0.5)
        # every digit of the largest double (computed from the printed value: an exact integer)
        full = str(int(float(value_of(lines[2].source))))
        streak = MonoLine(full, font_size=30, color=MONEY).set_anchor([-6.6, 1.3, 0])
        count = Text(f'{len(full)} digits', font_size=22, color=SCAFFOLD).next_to(big.glyphs, RIGHT, buff=0.5)
        self.play(FadeIn(streak, shift=LEFT), FadeIn(count))
        self.play(streak.animate.shift(LEFT * (streak.width - 6)), run_time=6, rate_func=linear)
        self.play(FadeOut(streak), FadeOut(count), run_time=0.4)

        # Ask C or Rust: the same 53, 15, 2
        self.at('Ask the same question in C')
        same = [value_of(lines[i].source) for i in (0, 1, 4)]
        boards = VGroup()
        for lang in ('C', 'Rust'):
            head = Text(lang, font_size=26)
            vals = VGroup(*[code_text(v, font_size=30, color=FOCUS) for v in same]).arrange(RIGHT, buff=0.6)
            board = VGroup(head, vals).arrange(DOWN, buff=0.25)
            frame = SurroundingRectangle(board, color=GREY_D, buff=0.3, corner_radius=0.12).set_fill(PANEL, 1)
            boards.add(VGroup(frame, board))
        boards.arrange(RIGHT, buff=1.2).move_to(UP * 1.75)
        self.play(FadeOut(big), *[l.animate.set_opacity(1) for l in keep])
        self.play(FadeIn(boards[0], shift=UP * 0.3))
        self.play(FadeIn(boards[1], shift=UP * 0.3))
        self.finish()


# ---------------------------------------------------------------- 5.5

class Segment_5_5(Segment):
    """One value, four costumes (q05-02)."""
    EPISODE, SEGMENT = 5, '5.5'

    def construct(self):
        # [V5.5a] a gold dot on the float line: the double 0x3fd3333333333334
        line = FloatLine('0.29999999999999993', '0.30000000000000016', width=11.0,
                         labels={0.3: '0.3', 0.1 + 0.2: '0.1 + 0.2'}).move_to(UP * 2.55)
        value = 0.1 + 0.2
        dot = Dot(line.point(value), radius=0.13, color=MONEY)
        bits = '0x' + output_line(P1, '0.1 + 0.2').split()[-1]
        bits_label = code_text(bits, font_size=22, color=STORED).next_to(dot, UP, buff=0.35)
        self.play(Create(line.axis), FadeIn(line.ticks), FadeIn(line.labels))
        self.play(FadeIn(dot, scale=2), FadeIn(bits_label, shift=DOWN * 0.2))

        # [V5.5b] code panel q05-02 and QR
        self.at('Because storing a number')
        code = code_panel(snippet_lines(P2, 4, 9), font_size=18).to_edge(LEFT, buff=0.3).set_y(0.45)
        out = Console(snippet_output(P2), font_size=18, width=code.background.width)
        out.next_to(code, DOWN, buff=0.25, aligned_edge=LEFT)
        card = qr_card('q05-02')
        self.play(FadeIn(code), FadeIn(out.background), FadeIn(card, shift=UP * 0.2), FadeOut(bits_label))
        card_shown = self.renderer.time
        self.at('The value is fixed by the hardware')
        self.play(Indicate(dot, color=MONEY, scale_factor=1.6))
        self.at("How it's shown")
        self.wait_since(card_shown, 8.2)
        self.remove(card)

        # four costumes, each lands on the dot as its output line prints
        outs = snippet_output(P2)
        badges = VGroup()
        cards = []
        for k in range(4):
            label, printed = outs[k].split(':', 1)
            m = re.match(r'(.*?)\s*\((.*)\)', label)
            text = Text(f'{m.group(1).strip()}\n{m.group(2)}', font_size=18, color=SCAFFOLD, line_spacing=0.7)
            shown = MonoLine(printed.strip(), font_size=22, color=WHITE)
            if k in (1, 2):    # the two costumes that hide the four are masks
                shell = mask_shape(4.4, 1.3)
                text.move_to(shell[0]).shift(UP * 0.22)
            else:
                shell = VGroup(RoundedRectangle(width=4.4, height=1.3, corner_radius=0.15).set_fill(PANEL, 1)
                               .set_stroke(STORED, 3))
                text.move_to(shell[0]).shift(UP * 0.22)
            shown.move_to(shell[0]).shift(DOWN * 0.27)
            costume = VGroup(shell, text, shown)
            costume.move_to(dot.get_center() + UP * 0.35)
            cards.append(costume)
            badge = label_box(m.group(1).strip(), font_size=18, color=STORED if k in (0, 3) else FOCUS)
            badge.move_to([5.1, 1.25 - 0.6 * k, 0])
            badges.add(badge)
        tick_step = None

        def land(k):
            c = cards[k]
            start = c.copy().shift(UP * 2.0).set_opacity(0)
            self.play(FadeIn(c, shift=DOWN * 2.0), run_time=0.6, rate_func=rate_functions.ease_in_quad)
            typed(self, out.lines[k], 0.7)
            return start

        def stow(k):
            self.play(ReplacementTransform(cards[k], badges[k]), run_time=0.7)

        self.at('Python, JavaScript and Java print the shortest')
        land(0)
        self.at("That's honest")
        stow(0)
        self.at("C's printf, by default")
        land(1)
        # lifting the mask: the same dot, still one tick right of 0.3's double
        self.at('six places of this number round')
        self.play(cards[1].animate.shift(UP * 0.75).rotate(6 * DEGREES), run_time=0.6)
        step = CurvedArrow(line.point(0.3) + UP * 0.28, line.point(value) + UP * 0.28, angle=-PI / 2.2,
                           color=FOCUS, stroke_width=3, tip_length=0.14)
        self.play(Create(step), Indicate(dot, color=MONEY, scale_factor=1.6))
        stow(1)
        self.at('Spreadsheets typically show')
        land(2)
        self.at('is simply zero point three')
        self.play(cards[2].animate.shift(UP * 0.75).rotate(-6 * DEGREES), run_time=0.6)
        self.play(Indicate(dot, color=MONEY, scale_factor=1.6), Indicate(step, color=FOCUS))
        stow(2)
        self.at('Ask for seventeen digits')
        land(3)
        self.play(out.lines[3].glyphs[-1].animate.set_color(ERROR), cards[3][2].glyphs[-1].animate.set_color(ERROR))
        stow(3)

        # [V5.5c] four costumes, one value underneath: False under all four
        self.at('Four costumes, one value underneath')
        ghosts = [b.copy() for b in badges]
        self.play(LaggedStart(*[g.animate.move_to(dot).scale(0.2).set_opacity(0) for g in ghosts], lag_ratio=0.2),
                  run_time=1.4)
        self.remove(*ghosts)
        self.play(Indicate(dot, color=MONEY, scale_factor=1.8))
        self.at('the comparison at the bottom')
        typed(self, out.lines[4], 0.6)
        false = out.lines[4].part(value_of(out.lines[4].source))
        self.play(false.animate.set_color(ERROR).scale(1.4), run_time=0.5)
        self.play(false.animate.scale(1 / 1.4), Indicate(VGroup(*[o.glyphs for o in out.lines[:4]]), color=FOCUS,
                                                           scale_factor=1.02), run_time=0.6)
        self.at("They can't remove it")
        self.play(Flash(dot, color=MONEY, line_length=0.3))
        self.at('what you see may be a costume')
        self.play(*[Indicate(b, color=FOCUS) for b in badges])
        self.finish()


# ---------------------------------------------------------------- 5.6

LIMIT = 2 ** 53     # JavaScript's integer ceiling, as in q05-03


def pow_label(n):
    """'2⁵³', '2⁵³ − 1', '2⁵³ + 2' ... for a whole number near 2**53."""
    d = n - LIMIT
    return '2⁵³' if d == 0 else f'2⁵³{"+" if d > 0 else "−"}{abs(d)}'


class Segment_5_6(Segment):
    """JavaScript's integer ceiling (q05-03)."""
    EPISODE, SEGMENT = 5, '5.6'

    def construct(self):
        title = Text('JavaScript', font_size=48, weight=BOLD)
        window = RoundedRectangle(width=6, height=3.4, corner_radius=0.15).set_stroke(GREY_B, 2)
        bar = Line(window.get_corner(UL) + DOWN * 0.45, window.get_corner(UR) + DOWN * 0.45, color=GREY_B)
        dots = VGroup(*[Circle(0.07).set_fill(c, 1).set_stroke(width=0) for c in (ERROR, MONEY, EXACT)])
        dots.arrange(RIGHT, buff=0.12).move_to(window.get_corner(UL) + RIGHT * 0.5 + DOWN * 0.22)
        browser = VGroup(window, bar, dots)
        title.move_to(window).shift(DOWN * 0.2)
        self.play(Create(browser), run_time=0.8)
        self.at('a huge amount of money')
        flow = [penny(0.22).move_to(window.get_left() + LEFT * 1.2 + DOWN * (0.6 - 0.3 * (i % 3))) for i in range(6)]
        self.play(LaggedStart(*[c.animate.shift(RIGHT * 8.4) for c in flow], lag_ratio=0.18), run_time=2.0,
                  rate_func=linear)
        self.remove(*flow)
        self.at('JavaScript.')
        self.play(Write(title), run_time=0.8)

        # one kind of number, and it is a double
        self.at('exactly one kind of number')
        number_box = label_box('Number', font_size=30, color=STORED).move_to(DOWN * 0.3)
        self.play(FadeOut(browser), title.animate.scale(0.6).to_corner(UL, buff=0.35), FadeIn(number_box, scale=0.8))
        self.at('that number is a')
        stripe = bit_row('0' * 16).move_to(DOWN * 0.3)
        self.play(ReplacementTransform(number_box, stripe), run_time=0.9)
        self.at('Even the whole numbers')
        self.play(Indicate(stripe, color=STORED))

        # [V5.6a] the float line far to the right, around 2⁵³
        self.at('fifty-three significant bits')
        lo, hi = LIMIT - 5, LIMIT + 7
        doubles = doubles_between(lo, hi)
        line = FloatLine(lo, hi, width=12.4, ticks=doubles, tick_height=0.4).move_to(UP * 1.85)
        for n in range(LIMIT - 4, LIMIT + 7, 2):
            line.labels.add(Text(pow_label(n), font_size=20, color=SCAFFOLD).next_to(line.point(n), DOWN, buff=0.35))
        self.play(FadeOut(stripe), Create(line.axis), run_time=0.6)
        below = [t for t, v in zip(line.ticks, line.tick_values) if v < LIMIT]
        above = [t for t, v in zip(line.ticks, line.tick_values) if v >= LIMIT]
        self.play(LaggedStart(*[GrowFromCenter(t) for t in below], lag_ratio=0.15), FadeIn(line.labels), run_time=1.0)
        self.at('which is about nine quadrillion')
        ceiling = DashedLine(line.point(LIMIT) + DOWN * 0.35, line.point(LIMIT) + UP * 1.0, color=FOCUS)
        every = Text('every whole number', font_size=20, color=EXACT).move_to(
            (line.point(lo) + line.point(LIMIT)) / 2 + UP * 0.75)
        self.play(Create(ceiling), FadeIn(every))
        self.at('Past that, the doubles are two apart')
        self.play(LaggedStart(*[GrowFromCenter(t) for t in above], lag_ratio=0.2), run_time=0.9)
        evens = Text('two apart', font_size=20, color=ERROR).move_to(
            (line.point(LIMIT) + line.point(hi)) / 2 + UP * 0.75)
        self.play(FadeIn(evens))
        self.at("odd numbers simply don't exist")
        missing = VGroup(*[crossmark(size=0.22).move_to(line.point(n)) for n in range(LIMIT + 1, hi, 2)])
        self.play(LaggedStart(*[FadeIn(x, scale=1.5) for x in missing], lag_ratio=0.2))

        # JavaScript itself: 2 ** 53 + 1, and MAX_SAFE_INTEGER
        self.at('Ask JavaScript for two to the fifty-third plus one')
        js_code, js_out = other_code('5.6', 'javascript')
        panel = other_panel(js_code, 'javascript', 22)
        console = Console(js_out, font_size=22)
        VGroup(panel, console).arrange(RIGHT, buff=0.4, aligned_edge=UP).move_to(DOWN * 1.6)
        self.play(FadeIn(panel), FadeIn(console.background))
        typed(self, console.lines[0], 0.7)
        self.play(Indicate(line.ticks[line.tick_values.index(LIMIT)], color=FOCUS, scale_factor=1.6))
        self.at('max safe integer')
        typed(self, console.lines[1], 0.7)
        flag = Triangle().scale(0.12).rotate(PI).set_fill(EXACT, 1).set_stroke(width=0)
        flag.move_to(line.point(LIMIT - 1) + UP * 0.45)
        self.play(FadeIn(flag, shift=DOWN * 0.3), console.lines[1].animate.set_color(EXACT))
        self.at('the largest whole number whose next neighbour')
        self.play(Indicate(line.ticks[line.tick_values.index(LIMIT)], color=EXACT, scale_factor=1.5))

        # [V5.6b] q05-03: five integers drop toward the line
        self.at("Python's own integers")
        self.play(FadeOut(VGroup(panel, console, every, evens, flag, ceiling)), run_time=0.5)
        code = code_panel(snippet_find(P3, 'for n in', 'as a double'), font_size=20).to_edge(LEFT, buff=0.3).set_y(0.55)
        out = Console(snippet_output(P3)[1:], font_size=20).next_to(code, DOWN, buff=0.25, aligned_edge=LEFT)
        card = qr_card('q05-03')
        self.play(FadeIn(code), FadeIn(out.background), FadeIn(card, shift=UP * 0.2))
        for k, n in enumerate(range(LIMIT - 1, LIMIT + 4)):
            stored = float(n)                      # what a double holds, as the snippet prints
            diamond = line.diamond(n)
            tag = Text(pow_label(n), font_size=20, color=FOCUS).next_to(diamond, UP, buff=0.12)
            piece = VGroup(diamond, tag).shift(UP * 1.0)
            self.play(FadeIn(piece, shift=DOWN * 0.3), run_time=0.3)
            self.play(piece.animate.shift(DOWN * 1.0), type_out(out.lines[k], 0.6), run_time=0.6)
            self.remove(*out.lines[k].glyphs)
            self.add(out.lines[k])
            if int(stored) == n:
                self.play(diamond.animate.set_color(EXACT), tag.animate.set_color(EXACT), run_time=0.3)
            else:
                snap = line.snap(n, color=ERROR)
                self.play(Create(snap), diamond.animate.set_color(ERROR), tag.animate.set_color(ERROR), run_time=0.4)
                self.play(diamond.animate.move_to(line.point(stored) + UP * 0.45), run_time=0.4)
                printed = out.lines[k]
                self.play(printed.chars(printed.source.index('-> ') + 3).animate.set_color(ERROR),
                          FadeOut(snap), run_time=0.3)
        # [V5.6c] the cents line: $90,071,992,547,409.93, and False
        self.at('If you store an amount in cents')
        cents = out.lines[5]
        typed(self, cents, 0.9)
        amount = cents.source.split(' ')[0]
        self.play(cents.part(amount).animate.set_color(MONEY), cents.part('False').animate.set_color(ERROR))
        self.at('Most of us are')
        self.play(FadeOut(card))
        self.at('But database IDs')
        risks = VGroup(*[label_box(t, font_size=20, color=FOCUS) for t in
                         ('database IDs', 'account numbers', 'amounts in very small units')])
        risks.arrange(DOWN, buff=0.2, aligned_edge=RIGHT).to_edge(RIGHT, buff=0.35).set_y(-1.3)
        self.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.3) for r in risks], lag_ratio=0.4), run_time=1.6)
        self.at('round them without a word')
        self.play(*[r[0].animate.set_stroke(ERROR, 3) for r in risks])
        self.at('In 2020')
        big = label_box('BigInt · 2020', font_size=24, color=EXACT, fill=EXACT).next_to(risks, DOWN, buff=0.35)
        big.align_to(risks, RIGHT)
        self.play(FadeIn(big, scale=0.8))
        self.finish()


# ---------------------------------------------------------------- 5.7

class Segment_5_7(Segment):
    """Databases and spreadsheets: DECIMAL that isn't, and the Excel 2007 display bug."""
    EPISODE, SEGMENT = 5, '5.7'

    def construct(self):
        # [V5.7a] a table with two families of number types
        width, head_h, row_h = 5.8, 0.9, 0.55
        cols = VGroup()
        for k, (heading, tag, colour, sign) in enumerate((
                ('FLOAT / REAL / DOUBLE PRECISION', 'approximate', ERROR, '≈'),
                ('DECIMAL / NUMERIC', 'exact', EXACT, '='))):
            head = Rectangle(width=width, height=head_h).set_fill(PANEL, 1).set_stroke(GREY_B, 2)
            name = Text(heading, font_size=22, color=colour).move_to(head)
            body = VGroup(*[Rectangle(width=width, height=row_h).set_stroke(GREY_D, 1.5) for _ in range(3)])
            body.arrange(DOWN, buff=0).next_to(head, DOWN, buff=0)
            marks = VGroup(*[Text(sign, font_size=30, color=colour).move_to(r) for r in body])
            label = Text(tag, font_size=22, color=colour).next_to(body, DOWN, buff=0.25)
            col = VGroup(head, name, body, marks, label)
            col.head, col.name, col.body, col.marks, col.label = head, name, body, marks, label
            cols.add(col)
        cols.arrange(RIGHT, buff=0).move_to(UP * 0.3)
        self.play(*[Create(c.head) for c in cols], *[Create(c.body) for c in cols], run_time=1.5)
        self.at('two families of number types')
        self.play(Circumscribe(VGroup(cols[0].head, cols[1].head), color=GREY_A, fade_out=True))
        self.at('are approximate')
        self.play(FadeIn(cols[0].name), FadeIn(cols[0].label, shift=UP * 0.2),
                  LaggedStart(*[FadeIn(m, shift=RIGHT * 0.3) for m in cols[0].marks], lag_ratio=0.2))
        self.at('meant to be exact')
        self.play(FadeIn(cols[1].name), FadeIn(cols[1].label, shift=UP * 0.2),
                  LaggedStart(*[FadeIn(m, shift=RIGHT * 0.3) for m in cols[1].marks], lag_ratio=0.2))
        self.at('how many digits')
        self.play(Indicate(cols[1].name, color=EXACT))

        # [V5.7b] the SQLite trap
        self.at("So you'd think")
        self.play(FadeOut(cols, shift=UP * 0.4), run_time=0.6)
        sql, sql_out = other_code('5.7', 'sql')
        panel = other_panel(sql, 'sql', 20).to_corner(UL, buff=0.35)
        console = Console(sql_out, font_size=22, rows=2).next_to(panel, RIGHT, buff=0.35, aligned_edge=UP)
        self.play(FadeIn(panel), FadeIn(console.background))
        box = line_highlight(panel, 0)
        self.play(Create(box))
        # the payments table, typed as in the CREATE statement
        decl = re.search(r'\((\w+) (DECIMAL\([^)]*\))\)', sql)
        values = re.findall(r'\(([\d.]+)\)', sql.split('\n')[1])
        cell_w = 3.6
        header = Rectangle(width=cell_w, height=0.95).set_fill(PANEL, 1).set_stroke(GREY_B, 2)
        col_name = Text(decl.group(1), font_size=22, font=MONO).move_to(header).shift(UP * 0.2)
        col_type = Text(decl.group(2), font_size=20, font=MONO, color=SCAFFOLD).move_to(header).shift(DOWN * 0.2)
        table_name = Text('payments', font_size=22, color=SCAFFOLD).next_to(header, UP, buff=0.15, aligned_edge=LEFT)
        cells = VGroup(*[Rectangle(width=cell_w, height=0.6).set_stroke(GREY_D, 1.5) for _ in values])
        cells.arrange(DOWN, buff=0).next_to(header, DOWN, buff=0)
        table = VGroup(table_name, header, col_name, col_type, cells).move_to([-3.6, -1.4, 0])
        self.at('In most databases, it is')
        self.play(FadeIn(table, shift=UP * 0.2))
        sticker = label_box('exact', font_size=22, color=EXACT, fill=EXACT).next_to(header, RIGHT, buff=0.25)
        sticker.rotate(-10 * DEGREES)
        self.play(FadeIn(sticker, scale=1.6))
        self.at('the database inside billions')
        self.play(Indicate(VGroup(panel.code_lines[0]), color=FOCUS))
        self.at('It accepts the')
        self.play(box.animate.move_to([box.get_x(), line_highlight(panel, 1).get_y(), 0]))
        shown = VGroup()
        for cell, v in zip(cells, values):
            t = code_text(v, font_size=22, color=WHITE).move_to(cell)
            shown.add(t)
            self.play(FadeIn(t, shift=DOWN * 0.5), run_time=0.4)
        self.at('Sum ten cents')
        self.play(box.animate.move_to([box.get_x(), line_highlight(panel, 2).get_y(), 0]))
        typed(self, console.lines[0], 0.8)
        self.play(console.lines[0].glyphs[-1].animate.set_color(ERROR).scale(1.5), run_time=0.4)
        self.play(console.lines[0].glyphs[-1].animate.scale(1 / 1.5), run_time=0.3)
        self.at('Ask what type it stored')
        self.play(box.animate.move_to([box.get_x(), line_highlight(panel, 3).get_y(), 0]))
        typed(self, console.lines[1], 0.5)
        # the "exact" label peels off and shows what is underneath
        under = Text(console.lines[1].source, font=MONO, font_size=24, color=ERROR).move_to(sticker)
        self.play(FadeIn(under), sticker.animate.rotate(-50 * DEGREES, about_point=sticker.get_corner(DL))
                  .shift(DOWN * 1.2 + RIGHT * 0.6).set_opacity(0), run_time=1.0)
        self.play(Indicate(under, color=ERROR), console.lines[1].animate.set_color(ERROR))
        self.at('Check what your database actually does')
        ring = SurroundingRectangle(VGroup(col_type, under), color=FOCUS, buff=0.1)
        self.play(Create(ring))

        # [V5.7c] the spreadsheet: =850*77.1
        self.at('Spreadsheets live on')
        wipe(self)
        formula = '=850*77.1'
        product = 850 * 77.1                     # the double the cell holds (Python)
        stored_text = repr(product)               # 65534.99999999999
        exact = Fraction(850) * Fraction('77.1')  # the true product, 65535
        shown15 = f'{product:.15g}'               # 15 significant digits, as the fixed display shows
        cw, ch, rh = 2.0, 0.62, 0.5
        letters = VGroup(*[Text(c, font_size=18, color=SCAFFOLD) for c in 'ABC'])
        grid_cells = VGroup(*[Rectangle(width=cw, height=ch).set_stroke(GREY_D, 1.5) for _ in range(9)])
        grid_cells.arrange_in_grid(rows=3, cols=3, buff=0)
        heads = VGroup(*[Rectangle(width=cw, height=rh).set_fill(GREY_E, 1).set_stroke(GREY_D, 1.5) for _ in range(3)])
        heads.arrange(RIGHT, buff=0).next_to(grid_cells, UP, buff=0)
        for l, h in zip(letters, heads):
            l.move_to(h)
        fbar = Rectangle(width=3 * cw, height=0.6).set_stroke(GREY_B, 1.5).next_to(heads, UP, buff=0.2)
        fx = Text('fx', font_size=20, color=SCAFFOLD).move_to(fbar.get_left() + RIGHT * 0.3)
        ftext = code_text(formula, font_size=24, color=WHITE).next_to(fx, RIGHT, buff=0.3)
        sheet = VGroup(fbar, fx, heads, letters, grid_cells).move_to([-3.4, 1.6, 0])
        ftext.next_to(fx, RIGHT, buff=0.3)
        target = grid_cells[4]
        select = SurroundingRectangle(target, color=FOCUS, buff=0, stroke_width=4)
        self.play(FadeIn(sheet), run_time=0.7)
        self.play(Create(select), FadeIn(ftext, shift=RIGHT * 0.2))
        self.at('Excel stores numbers')
        stored = VGroup(Text('stored', font_size=20, color=SCAFFOLD), code_text(stored_text, font_size=26, color=STORED))
        stored.arrange(RIGHT, buff=0.3).next_to(sheet, RIGHT, buff=0.6).set_y(target.get_y())
        self.play(TransformFromCopy(ftext, stored[1]), FadeIn(stored[0]), run_time=1.0)
        self.at('one of those costumes from earlier')
        mask = mask_shape(1.7, 0.5).scale(0.9).next_to(stored, UP, buff=0.35)
        self.play(FadeIn(mask, shift=DOWN * 0.3))
        self.at('the cell displayed one hundred thousand')
        wrong = code_text('100000', font_size=26, color=ERROR).move_to(target)
        self.play(FadeOut(mask), FadeIn(wrong, scale=1.5))
        self.play(Indicate(wrong, color=ERROR))
        self.at('The right answer is')
        right = VGroup(Text('right answer', font_size=20, color=SCAFFOLD), code_text(str(exact), font_size=26, color=EXACT))
        right.arrange(RIGHT, buff=0.3).next_to(stored, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(FadeIn(right, shift=UP * 0.2))
        self.at('The stored value was fine')
        tick = checkmark(size=0.35).next_to(stored, RIGHT, buff=0.25)
        self.play(Create(tick), Indicate(stored[1], color=STORED))
        self.at('into text for the screen')
        hop = CurvedArrow(stored[0].get_left() + LEFT * 0.1 + UP * 0.2, target.get_right() + RIGHT * 0.05 + UP * 0.2,
                          angle=PI / 2, color=ERROR, stroke_width=3, tip_length=0.15)
        hop_label = Text('double → text', font_size=20, color=ERROR).next_to(stored, UP, buff=0.25).align_to(stored, LEFT)
        self.play(Create(hop), FadeIn(hop_label))
        self.at('Microsoft fixed it')
        patch = VGroup(RoundedRectangle(width=1.5, height=0.5, corner_radius=0.2).set_fill(MONEY, 1).set_stroke(width=0),
                       Text('2007 patch', font_size=18, color=BLACK)).move_to(target.get_bottom() + DOWN * 1.4)
        patch[1].move_to(patch[0])
        self.play(FadeIn(patch, shift=UP * 0.3))
        fixed = code_text(shown15, font_size=26, color=EXACT).move_to(target)
        self.play(patch.animate.move_to(target).set_opacity(0.0), ReplacementTransform(wrong, fixed), run_time=0.9)
        self.play(FadeOut(hop), FadeOut(hop_label))
        self.at('perfect miniature')
        steps = VGroup(label_box('the value was slightly off', font_size=22, color=STORED),
                       label_box('the display tried to hide it', font_size=22, color=FOCUS),
                       label_box('the hiding went wrong', font_size=22, color=ERROR)).arrange(RIGHT, buff=0.55)
        fit(steps, 13.2).move_to(DOWN * 2.6)
        arrows = VGroup(*[Arrow(steps[i].get_right(), steps[i + 1].get_left(), buff=0.08, color=SCAFFOLD,
                                stroke_width=3) for i in range(2)])
        for phrase, k in (('the real value was slightly off', 0), ('the display tried to hide', 1),
                          ('the hiding went wrong', 2)):
            self.at(phrase)
            anims = [FadeIn(steps[k], shift=UP * 0.2)]
            if k:
                anims.append(GrowArrow(arrows[k - 1]))
            self.play(*anims, run_time=0.5)
        self.finish()


# ---------------------------------------------------------------- 5.8

class Segment_5_8(Segment):
    """The exceptions: decimal types, COBOL, and decimal floating point."""
    EPISODE, SEGMENT = 5, '5.8'

    def construct(self):
        # [V5.8a] a wall of languages, binary64 by default
        names = ['JavaScript', 'Java', 'C', 'Go', 'Rust', 'Ruby', 'Swift', 'Python', 'C#', 'SQL']
        cells = VGroup(*[Rectangle(width=2.6, height=1.0).set_opacity(0) for _ in names])
        cells.arrange_in_grid(rows=2, cols=5, buff=(0.0, 0.15)).move_to(UP * 2.3)
        wall = {}
        for n, cell in zip(names, cells):
            wall[n] = Text(n, font_size=26, color=GREY_B).move_to(cell).shift(UP * 0.18)
        heading = Text('binary64 by default', font_size=22, color=SCAFFOLD).to_edge(UP, buff=0.15)
        self.play(FadeIn(heading), LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in wall.values()], lag_ratio=0.08),
                  run_time=1.4)

        def light(name, label):
            sub = Text(label, font_size=18, color=EXACT).next_to(wall[name], DOWN, buff=0.1)
            self.play(wall[name].animate.set_color(EXACT), FadeOut(stripes[name]), FadeIn(sub, shift=UP * 0.1),
                      run_time=0.5)
            return sub

        stripe = bit_row(output_line(P1, '0.1 ').split()[-1])
        stripes = {n: stripe.copy().scale_to_fit_width(1.7).next_to(t, DOWN, buff=0.16) for n, t in wall.items()}
        self.at('Nearly every mainstream language has')
        self.play(LaggedStart(*[GrowFromEdge(st, LEFT) for st in stripes.values()], lag_ratio=0.08), run_time=1.4)
        middle = DOWN * 0.3
        self.at('most also offer a second kind')
        self.play(*[Indicate(t, color=GREY_A, scale_factor=1.08) for t in wall.values()])

        # C#: 128 bits, a whole number and a power of ten
        self.at('C sharp has a built-in type')
        light('C#', 'decimal')
        self.at('one hundred and twenty-eight bits')
        whole = Rectangle(width=5.4, height=0.6).set_fill(STORED, 0.6).set_stroke(BLACK, 1)
        power = Rectangle(width=2.8, height=0.6).set_fill(FOCUS, 0.6).set_stroke(BLACK, 1)
        bar = VGroup(whole, power).arrange(RIGHT, buff=0).move_to(middle)
        bar_labels = VGroup(Text('a whole number', font_size=20).move_to(whole),
                            Text('a power of ten', font_size=20, color=BLACK).move_to(power))
        size = Text('128 bits', font_size=20, color=SCAFFOLD).next_to(bar, UP, buff=0.15)
        self.play(GrowFromEdge(bar, LEFT), FadeIn(bar_labels), FadeIn(size), run_time=0.9)

        # Java: BigDecimal from strings gives exactly 0.3
        self.at('Java has')
        java_sub = light('Java', 'BigDecimal')
        code, out = other_code('5.8', 'java')
        panel = other_panel(code, 'java', 18)
        console = Console(out, font_size=22)
        VGroup(panel, console).arrange(RIGHT, buff=0.3).move_to(middle)
        self.play(FadeOut(VGroup(bar, bar_labels, size)), FadeIn(panel), FadeIn(console.background))
        self.at('the sum is exactly zero point three')
        typed(self, console.lines[0], 0.4)
        self.play(console.lines[0].animate.set_color(EXACT).scale(1.3))
        self.at('Python has the')
        light('Python', 'decimal, fractions')
        self.at('Ruby has')
        light('Ruby', 'BigDecimal, Rational')
        self.at('aside, have')
        light('SQL', 'DECIMAL, NUMERIC')

        # [V5.8b] COBOL, apart, in gold: PIC 9(7)V99
        self.at("And then there's")
        self.play(FadeOut(panel), FadeOut(console), run_time=0.5)
        cobol = Text('COBOL', font_size=44, weight=BOLD, color=MONEY).move_to([-4.6, -0.2, 0])
        by_default = Text('decimal by default', font_size=20, color=MONEY).next_to(cobol, DOWN, buff=0.15)
        self.play(FadeIn(cobol, shift=UP * 0.3))
        self.at('designed for business')
        self.play(FadeIn(by_default), Flash(cobol, color=MONEY, line_length=0.3, flash_radius=1.4))
        self.at('A field declared as picture')
        pic = code_text('PIC 9(7)V99', font_size=32, color=MONEY).move_to([1.6, -0.2, 0])
        boxes = VGroup(*[Square(0.62).set_stroke(MONEY, 2) for _ in range(9)]).arrange(RIGHT, buff=0.08)
        boxes[7:].shift(RIGHT * 0.32)
        boxes.move_to([1.6, -1.55, 0])
        point = Dot(radius=0.07, color=MONEY).move_to(
            (boxes[6].get_corner(DR) + boxes[7].get_corner(DL)) / 2 + UP * 0.08)
        self.play(FadeIn(pic, shift=DOWN * 0.2))
        self.play(LaggedStart(*[GrowFromCenter(b) for b in boxes], lag_ratio=0.08), run_time=0.9)
        self.at('holds seven digits')
        seven = bracket(boxes[:7], DOWN, buff=0.12, color=MONEY)
        seven_l = Text('seven digits', font_size=20, color=MONEY).next_to(seven, DOWN, buff=0.1)
        self.play(Create(seven), FadeIn(seven_l))
        self.at('an implied')
        self.play(FadeIn(point, scale=3))
        self.at('two digits of cents')
        two = bracket(boxes[7:], DOWN, buff=0.12, color=MONEY)
        two_l = Text('cents', font_size=20, color=MONEY).next_to(two, DOWN, buff=0.1)
        self.play(Create(two), FadeIn(two_l))
        self.at('to hold a dime')
        dime = coin('10¢', 0.4).move_to(boxes.get_top() + UP * 1.0 + RIGHT * 2.0)
        self.play(FadeIn(dime, scale=0.5), run_time=0.3)
        self.play(dime.animate.move_to(boxes[7:]).scale(0.4).set_opacity(0), run_time=0.6)
        digits = VGroup(*[Text(ch, font=MONO, font_size=30, color=EXACT).move_to(b)
                          for ch, b in zip('0000000' + '10', boxes)])   # ten cents, from the narration
        self.play(LaggedStart(*[FadeIn(d, scale=1.4) for d in digits], lag_ratio=0.06), run_time=0.8)

        # [V5.8c] the standard caught up
        self.at('The standard caught up')
        self.play(FadeOut(VGroup(cobol, by_default, pic, boxes, point, seven, seven_l, two, two_l, digits)), run_time=0.6)
        notes = VGroup(*[Text(t, font_size=26) for t in
                         ('IEEE 754-2008: decimal formats', 'hardware: IBM POWER and IBM Z', 'C23: _Decimal64')])
        notes.arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(DOWN * 0.9)
        card = SurroundingRectangle(notes, color=GREY_B, buff=0.35, corner_radius=0.15)
        self.at('The 2008 revision')
        self.play(Create(card), FadeIn(notes[0], shift=RIGHT * 0.3))
        self.at('builds them into the hardware')
        self.play(FadeIn(notes[1], shift=RIGHT * 0.3))
        self.at('the latest C standard')
        self.play(FadeIn(notes[2], shift=RIGHT * 0.3))

        # [V5.8d] JavaScript: no built-in decimal (yet)
        self.at('JavaScript still has no built-in')
        js = Text('JavaScript: no built-in decimal (yet)', font_size=24, color=GREY_B).next_to(card, DOWN, buff=0.4)
        self.play(Indicate(wall['JavaScript'], color=GREY_A), FadeIn(js, shift=UP * 0.2))
        self.at('a proposal to add one')
        self.play(Circumscribe(js, color=GREY_B, fade_out=True))
        self.finish()


# ---------------------------------------------------------------- 5.9

class Segment_5_9(Segment):
    """Why binary is the default: scientists measure, accountants count."""
    EPISODE, SEGMENT = 5, '5.9'

    def construct(self):
        # [V5.9a] two figures side by side
        sci = person(GREY_B, '#3a4a5a').scale(1.3).move_to([-2.8, -0.4, 0])
        acc = person(GREY_B, '#5a4a2a').scale(1.3).move_to([3.6, -0.4, 0])
        sci_label = wrapped_text('binary64: fast, compact, in hardware', 5.6, font_size=24, color=STORED)
        acc_label = wrapped_text('decimal: exact for prices, slower, often in software', 5.6, font_size=24, color=EXACT)
        sci_label.next_to(sci, UP, buff=1.0).set_x(-3.5)
        acc_label.next_to(acc, UP, buff=1.0).align_to(sci_label, UP).set_x(3.6)
        divider = DashedLine(UP * 3.6, DOWN * 3.0, color=GREY_D)
        self.play(FadeIn(sci, shift=UP * 0.3), FadeIn(acc, shift=UP * 0.3), Create(divider))

        self.at('built for measuring')
        self.play(FadeIn(sci_label, shift=DOWN * 0.2))
        # [V5.9b] a ruler and a stopwatch
        ruler = Rectangle(width=2.0, height=0.35).set_fill('#c9a66b', 1).set_stroke(width=0)
        marks = VGroup(*[Line(UP * 0.0, DOWN * (0.15 if i % 2 else 0.08), color=BLACK, stroke_width=2)
                         .move_to(ruler.get_corner(UL) + RIGHT * (0.1 + i * 0.2) + DOWN * 0.06) for i in range(10)])
        ruler = VGroup(ruler, marks).rotate(20 * DEGREES).next_to(sci, LEFT, buff=-0.3).shift(DOWN * 0.3)
        watch = VGroup(Circle(0.45).set_stroke(GREY_A, 4), Line(ORIGIN, UP * 0.32, color=FOCUS, stroke_width=3),
                       Rectangle(width=0.16, height=0.14).set_fill(GREY_A, 1).set_stroke(width=0).shift(UP * 0.55))
        watch.next_to(sci, RIGHT, buff=-0.2).shift(DOWN * 0.2)
        self.at('Distances')
        words = VGroup(*[Text(w, font_size=20, color=SCAFFOLD) for w in
                         ('distances', 'temperatures', 'forces', 'voltages', 'probabilities')])
        words.arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to([-6.0, -0.7, 0]).to_edge(LEFT, buff=0.3)
        self.play(FadeIn(ruler, shift=RIGHT * 0.2), FadeIn(watch, shift=LEFT * 0.2),
                  LaggedStart(*[FadeIn(w, shift=RIGHT * 0.2) for w in words], lag_ratio=0.35), run_time=2.2)
        reading = code_text('2.718281828…', font_size=22, color=STORED).next_to(sci, DOWN, buff=0.3).shift(LEFT * 0.5)
        lap = code_text('9.58 s', font_size=22, color=STORED).next_to(reading, RIGHT, buff=0.4)
        self.at("A ruler isn't exact")
        self.play(FadeIn(reading, shift=UP * 0.2), Rotate(watch[1], -TAU, about_point=watch[0].get_center()), run_time=1.0)
        self.play(FadeIn(lap, shift=UP * 0.2))
        self.at('base two or base ten')
        shrug = VGroup(Text('base 2', font_size=20, color=SCAFFOLD), Text('base 10', font_size=20, color=SCAFFOLD))
        shrug.arrange(RIGHT, buff=0.3).next_to(VGroup(reading, lap), DOWN, buff=0.25)
        self.play(FadeIn(shrug))
        self.play(shrug.animate.set_opacity(0.4))
        self.at('speed, range and predictable behaviour')
        self.play(Indicate(sci_label, color=STORED, scale_factor=1.05))

        # The accountant counts
        self.at('Money is different')
        self.play(FadeIn(acc_label, shift=DOWN * 0.2))
        self.at("It's counted")
        stack = VGroup()
        for i in range(4):
            p = penny(0.3).move_to(acc.get_right() + RIGHT * 0.7 + UP * 1.2)
            self.play(p.animate.move_to(acc.get_corner(DR) + RIGHT * 0.7 + UP * (0.25 + 0.14 * i)).stretch(0.45, 1),
                      run_time=0.25)
            stack.add(p)
        self.at('Nobody has nine point nine')
        dime = coin('10¢', 0.42).next_to(acc, DOWN, buff=0.35)
        odd = code_text('9.9999 dimes', font_size=22, color=ERROR).next_to(dime, LEFT, buff=0.4)
        strike = Line(odd.get_left(), odd.get_right(), color=ERROR, stroke_width=4)
        self.play(FadeIn(dime, scale=0.5), FadeIn(odd))
        self.play(Create(strike))
        self.at('counting needs exactness')
        tick = checkmark(size=0.4).next_to(dime, RIGHT, buff=0.3)
        self.play(Create(tick), Indicate(dime, color=MONEY))
        self.at("picked the scientist's number")
        self.play(sci[0].animate.set_stroke(STORED, 5), Indicate(sci_label, color=STORED, scale_factor=1.05))

        # [V5.9c] the rule, held back for episode 10
        self.at('Our job is to notice')
        self.play(acc[0].animate.set_stroke(EXACT, 5), run_time=0.5)
        rule = Text('Measure with floats. Count with integers and decimals.', font_size=30, weight=BOLD)
        fit(rule, 13).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(rule, shift=UP * 0.2), run_time=0.8)
        self.wait(1.0)
        self.play(rule.animate.set_opacity(0.45), run_time=1.0)
        self.finish()


# ---------------------------------------------------------------- 5.10

class Segment_5_10(Segment):
    """Recap and challenge (q05-05), the QR wall, and the teaser for episode 6."""
    EPISODE, SEGMENT = 5, '5.10'

    def construct(self):
        # [V5.10a] the recap column
        items = ['Same bits in every language', 'IEEE 754 since 1985, in the hardware', 'Printing is a costume',
                 'JavaScript: exact integers only to 2⁵³', 'DECIMAL might not mean decimal',
                 'Most languages have a decimal type']
        phrases = ['Nearly every mainstream language stores', 'because they all hand their arithmetic',
                   'They differ only in how they print', "JavaScript's integers stop",
                   'A column called', 'And most languages offer']
        rows = VGroup()
        for t in items:
            box = Square(0.36).set_stroke(SCAFFOLD, 2)
            text = Text(t, font_size=30)
            rows.add(VGroup(box, text).arrange(RIGHT, buff=0.35))
        rows.arrange(DOWN, buff=0.42, aligned_edge=LEFT).move_to(ORIGIN)
        title = Text("Let's take stock", font_size=26, color=SCAFFOLD).next_to(rows, UP, buff=0.45).align_to(rows, LEFT)
        self.play(FadeIn(title))
        self.at("It isn't Python")
        self.play(Indicate(title, color=FOCUS))
        for row, phrase in zip(rows, phrases):
            self.at(phrase)
            tick = checkmark(size=0.32).move_to(row[0])
            self.play(FadeIn(row, shift=RIGHT * 0.4), run_time=0.5)
            self.play(Create(tick), run_time=0.35)
            row.add(tick)

        # [V5.10b] the challenge: q05-05, with a sticky note; QR held over 10 seconds
        self.at("Here's the challenge")
        wipe(self, run_time=0.5)
        code = code_panel(snippet_lines(P5, 7, 11), font_size=18).to_corner(UL, buff=0.35)
        out = output_console(P5, font_size=22).next_to(code, DOWN, buff=0.35, aligned_edge=LEFT)
        card = qr_card('q05-05')
        self.play(FadeIn(code), FadeIn(out.background), FadeIn(card, shift=UP * 0.2))
        for line in out.lines:
            typed(self, line, 0.6)
        self.at('both say that one tenth plus two tenths')
        self.play(out.lines[1].animate.set_color(EXACT), out.lines[2].animate.set_color(EXACT),
                  Create(line_highlight(code, 1, EXACT)), Create(line_highlight(code, 3, EXACT)))
        self.at('Now remove the quotes')
        note_text = wrapped_text('Now try Decimal(0.1) without the quotes.', 2.9, font_size=24, color=BLACK)
        note = VGroup(Square(3.3).set_fill(FOCUS, 1).set_stroke(width=0).stretch_to_fit_height(2.2), note_text)
        note_text.move_to(note[0])
        note.rotate(4 * DEGREES).move_to([4.9, 2.5, 0])
        self.play(FadeIn(note, shift=DOWN * 0.3, scale=1.1))
        quotes = code.code_lines[2]
        ring = SurroundingRectangle(quotes, color=FOCUS, buff=0.05)
        self.play(Create(ring))

        # [V5.10c] the QR wall: q05-01 to q05-05, held 10 seconds
        self.at('Predict what happens')
        wipe(self, run_time=0.5)
        wall = qr_wall(episode_qr_ids(5))
        self.play(FadeIn(wall), run_time=0.6)

        # [V5.10d] teaser: round(2.675, 2) and eight ways to round
        self.at('Next time')
        wipe(self, run_time=0.5)
        call = code_text('round(2.675, 2)', font_size=36, color=WHITE)
        answer = code_text(repr(round(2.675, 2)), font_size=36, color=STORED)   # Python: 2.67
        arrow = Text('→', font_size=36, color=SCAFFOLD)
        top = VGroup(call, arrow, answer).arrange(RIGHT, buff=0.4).to_edge(UP, buff=0.4)
        self.play(FadeIn(call))
        self.at('two point six seven five down')
        self.play(FadeIn(arrow), FadeIn(answer, shift=LEFT * 0.2))
        # the eight rounding modes of Python's decimal module, each applied to 2.675
        modes = sorted(n for n in dir(decimal) if n.startswith('ROUND_'))
        lo_x, hi_x, axis_y = -2.6, 2.6, 0.35
        axis = Line([lo_x, axis_y, 0], [hi_x, axis_y, 0], color=SCAFFOLD, stroke_width=3)
        ends = VGroup(*[Line(DOWN * 0.15, UP * 0.15, color=SCAFFOLD, stroke_width=3).move_to([x, axis_y, 0])
                        for x in (lo_x, hi_x)])
        end_labels = VGroup(code_text('2.67', font_size=22, color=SCAFFOLD).next_to(ends[0], LEFT, buff=0.2),
                            code_text('2.68', font_size=22, color=SCAFFOLD).next_to(ends[1], RIGHT, buff=0.2))
        mid = Dot([0, axis_y, 0], radius=0.09, color=FOCUS)
        mid_label = code_text('2.675', font_size=22, color=FOCUS).next_to(mid, UP, buff=0.75)
        self.play(Create(axis), FadeIn(ends), FadeIn(end_labels), FadeIn(mid), FadeIn(mid_label))
        self.at('eight different ways to round')
        colours = [STORED, EXACT, FOCUS, ERROR, MONEY, TEAL, PURPLE, GREY_B]
        sides = {-1: [], 1: []}
        for name in modes:
            result = decimal.Decimal('2.675').quantize(decimal.Decimal('0.01'), rounding=getattr(decimal, name))
            sides[1 if result > decimal.Decimal('2.675') else -1].append(name)
        fans = VGroup()
        for side, names in sides.items():
            for j, name in enumerate(names):
                level = [1.25, 0.65, -0.65, -1.25][j % 4] + (0.0 if len(names) <= 4 else 0)
                tip = np.array([(hi_x if side > 0 else lo_x) + side * 0.2, axis_y + level, 0])
                colour = colours[len(fans) % len(colours)]
                a = Arrow([0, axis_y, 0] + np.array([side * 0.15, level * 0.15, 0]), tip, buff=0.05, color=colour,
                          stroke_width=3, max_tip_length_to_length_ratio=0.08)
                label = Text(name[6:].lower().replace('_', ' '), font_size=20, color=colour)
                label.next_to(tip, RIGHT if side > 0 else LEFT, buff=0.12)
                fans.add(VGroup(a, label))
        self.play(LaggedStart(*[AnimationGroup(GrowArrow(f[0]), FadeIn(f[1])) for f in fans], lag_ratio=0.25),
                  run_time=2.4)
        self.at('a business decision')
        teaser = end_card('Episode 6', 'Rounding is a policy').to_edge(DOWN, buff=0.35)
        self.play(FadeIn(teaser, shift=UP * 0.2))
        self.finish()

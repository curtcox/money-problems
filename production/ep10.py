"""Episode 10 · When the fixes fail. One Scene per script segment.

    python3 production/render.py 10 [-ql] [segment ...]

Shot ids in comments ([V10.1a] ...) refer to episodes/10-when-the-fixes-fail.md. Python code
and console lines come from snippets/ep10/ (q10-01 ... q10-05) and, for the series recap,
from earlier episodes' snippets. The Java example in 10.1 has no snippet: its code and
printed output are read from the script's own "On screen" blocks.
"""
import ast
import random
import re
import sys
from decimal import Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa: E402,F403

TRAP = 'ep10/01-decimal-trap.py'
THIRD = 'ep10/02-one-third.py'
OVERFLOW = 'ep10/03-cents-overflow.py'
UNITS = 'ep10/04-minor-units.py'
TRIP = 'ep10/05-there-and-back.py'

QR_SECONDS = 8.0


# ---------------------------------------------------------------- local helpers

def script_block(segment, lang, index=0):
    """A fenced block from this episode's script ('java', 'text' ...), for on-screen text
    that has no snippet of its own (the Java example in 10.1)."""
    text = next((ROOT / 'episodes').glob('10-*.md')).read_text()
    section = re.search(rf'^### {re.escape(segment)} .*?(?=^### |^## )', text, re.S | re.M).group(0)
    blocks = re.findall(rf'^```{lang}\n(.*?)^```', section, re.S | re.M)
    return blocks[index].rstrip('\n')


def java_panel(source, font_size=20):
    """code_panel's look, for Java."""
    return Code(code_string=source.strip('\n'), language='java', formatter_style='monokai',
                add_line_numbers=False, background='rectangle',
                background_config={'fill_color': PANEL, 'stroke_color': GREY_D, 'stroke_width': 1},
                paragraph_config={'font_size': font_size, 'font': MONO})


def show_qr(scene, qr_id, **kwargs):
    """Fade a QR card in and remember when, so drop_qr can keep it up long enough."""
    card = qr_card(qr_id, **kwargs)
    scene.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)
    card.shown_at = scene.renderer.time
    return card


def drop_qr(scene, card, seconds=QR_SECONDS):
    """Fade a QR card out, never sooner than `seconds` after it appeared."""
    remaining = card.shown_at + seconds - scene.renderer.time
    if remaining > 1 / 30:
        scene.wait(remaining)
    scene.play(FadeOut(card), run_time=0.5)


def token(text, color, font_size=26, mono=True):
    """A rounded chip carrying a value: 'Decimal 1.10', 'float64' ..."""
    label = Text(text, font=MONO if mono else FONT, font_size=font_size, color=color)
    box = RoundedRectangle(width=label.width + 0.45, height=label.height + 0.36, corner_radius=0.12)
    box.set_stroke(color, 3).set_fill(color, 0.15)
    label.move_to(box)
    group = VGroup(box, label)
    group.box, group.label = box, label
    return group


def recolor_token(chip, color):
    return [chip.box.animate.set_stroke(color, 3).set_fill(color, 0.15), chip.label.animate.set_color(color)]


def barrier(height=1.8, label=None, font_size=22):
    """The red wall a TypeError puts between two kinds of number."""
    wall = RoundedRectangle(width=0.26, height=height, corner_radius=0.06).set_fill(ERROR, 1).set_stroke(width=0)
    stripes = VGroup(*[Line(LEFT * 0.13, RIGHT * 0.13, stroke_width=4, color=BLACK).rotate(PI / 5)
                       .move_to(wall.get_top() + DOWN * (0.25 + 0.3 * k)) for k in range(int((height - 0.2) / 0.3))])
    group = VGroup(wall, stripes)
    if label:
        group.add(Text(label, font_size=font_size, color=ERROR).next_to(wall, UP, buff=0.12))
    return group


def warning_icon(size=0.55):
    tri = Triangle().set_stroke(ERROR, 4).set_fill(ERROR, 0.2).scale_to_fit_height(size)
    mark = Text('!', font_size=int(size * 50), color=ERROR, weight=BOLD).move_to(tri).shift(DOWN * size * 0.1)
    return VGroup(tri, mark)


class BitRow(VGroup):
    """A row of bit cells, most significant on the left; `show(value)` fills the ones."""

    def __init__(self, bits, cell=0.28, buff=0.03, color=STORED, sign_color=None, **kwargs):
        super().__init__(**kwargs)
        self.bits, self.on_color, self.sign_color = bits, color, sign_color
        self.cells = VGroup(*[Square(cell).set_stroke(GREY_D, 1.5).set_fill(BLACK, 0) for _ in range(bits)])
        self.cells.arrange(RIGHT, buff=buff)
        self.add(self.cells)

    def show(self, value):
        value &= (1 << self.bits) - 1
        for i, cell in enumerate(self.cells):
            on = (value >> (self.bits - 1 - i)) & 1
            color = self.sign_color if (i == 0 and self.sign_color) else self.on_color
            cell.set_fill(color if on else BLACK, 0.9 if on else 0)
        return self


def as_int32(n):
    """The snippet's own 32-bit wrap (q10-03), recomputed here to drive the odometer."""
    n = n & 0xFFFFFFFF
    return n - 2**32 if n >= 2**31 else n


def checklist_card(items, font_size=30, heading='Checklist · episode 9'):
    rows = VGroup()
    for text in items:
        box = Square(0.42).set_stroke(SCAFFOLD, 3)
        rows.add(VGroup(box, Text(text, font_size=font_size)).arrange(RIGHT, buff=0.3))
    rows.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
    head = Text(heading, font_size=24, color=SCAFFOLD)
    body = VGroup(head, rows).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
    frame = RoundedRectangle(width=body.width + 1.0, height=body.height + 0.8, corner_radius=0.2)
    frame.set_stroke(GREY_B, 2).set_fill(PANEL, 1).move_to(body)
    card = VGroup(frame, body)
    card.rows = rows
    card.ticks = VGroup(*[checkmark(size=0.42).move_to(r[0]).shift(UP * 0.04 + RIGHT * 0.04) for r in rows])
    return card


def wedge(center, radius, f0, f1, color, opacity=0.9):
    """The part of a pie from fraction f0 to f1 of the circle, clockwise from twelve o'clock."""
    sector = Sector(radius=radius, start_angle=PI / 2 - TAU * f1, angle=TAU * (f1 - f0))
    return sector.set_fill(color, opacity).set_stroke(width=0).shift(center)


def dial_angle(value, hi=30):
    return (225 - 270 * value / hi) * DEGREES


def precision_dial(center, radius=1.0, start=28):
    """A dial labelled 'precision' whose needle and readout follow `dial.tracker`."""
    tracker = ValueTracker(start)
    rim = Arc(radius=radius, start_angle=dial_angle(30), angle=dial_angle(0) - dial_angle(30),
              color=SCAFFOLD, stroke_width=4).shift(center)
    ticks = VGroup()
    for v in range(0, 31, 2):
        d = np.array([math.cos(dial_angle(v)), math.sin(dial_angle(v)), 0])
        ticks.add(Line(center + d * radius * 0.86, center + d * radius, color=SCAFFOLD, stroke_width=2))
    marks = VGroup()
    for v in (6, 28):
        d = np.array([math.cos(dial_angle(v)), math.sin(dial_angle(v)), 0])
        marks.add(Text(str(v), font_size=20, color=SCAFFOLD).move_to(center + d * (radius + 0.3)))
    needle = Line(center, center + UP * radius * 0.75, color=FOCUS, stroke_width=5)

    def aim(m):
        a = dial_angle(tracker.get_value())
        m.put_start_and_end_on(center, center + np.array([math.cos(a), math.sin(a), 0]) * radius * 0.75)
    needle.add_updater(aim)
    hub = Dot(center, radius=0.08, color=FOCUS)
    readout = number(start, font_size=34, color=FOCUS).move_to(center + DOWN * radius * 0.45)
    readout.add_updater(lambda m: m.set_value(round(tracker.get_value())).move_to(center + DOWN * radius * 0.45))
    label = Text('precision', font_size=24, color=SCAFFOLD).next_to(rim, DOWN, buff=0.2)
    group = VGroup(rim, ticks, marks, needle, hub, readout, label)
    group.tracker = tracker
    return group


# ---------------------------------------------------------------- 10.1

class Segment_10_1(Segment):
    """The fix that imported the bug (q10-01)."""
    EPISODE, SEGMENT = 10, '10.1'

    def construct(self):
        # [V10.1a] the checklist card from episode 9 slides in; its first two items tick
        card = checklist_card(['count in minor units', 'Decimal for rates', 'round on purpose'], font_size=40)
        card.move_to(ORIGIN)
        self.play(FadeIn(card, shift=RIGHT * 3), run_time=1.0)
        self.at('Count in whole minor units')
        self.play(Create(card.ticks[0]), card.rows[0][0].animate.set_stroke(EXACT, 3), run_time=0.6)
        self.at('Use decimals for rates')
        self.play(Create(card.ticks[1]), card.rows[1][0].animate.set_stroke(EXACT, 3), run_time=0.6)
        self.at('Round on purpose')
        self.play(Indicate(card.rows[2][1], color=FOCUS, scale_factor=1.08), run_time=0.8)
        self.at('break the first few items')
        top, bottom = card.rows[0], card.rows[1]
        left = min(top.get_left()[0], bottom.get_left()[0]) - 0.3
        right = max(top.get_right()[0], bottom.get_right()[0]) + 0.3
        y0, y1 = top.get_top()[1] + 0.15, bottom.get_bottom()[1] - 0.15
        xs = np.linspace(left, right, 6)
        ys = [y0, y1 + 0.5, y0 - 0.3, y1, y0 - 0.2, y1 + 0.3]
        crack = VMobject(color=ERROR, stroke_width=6).set_points_as_corners([[x, y, 0] for x, y in zip(xs, ys)])
        self.play(Create(crack), card.ticks[:2].animate.set_color(ERROR), run_time=1.0)
        self.at('each fix has its own way of failing')
        self.play(Wiggle(VGroup(card, card.ticks[:2], crack), scale_value=1.04, rotation_angle=0.02), run_time=1.2)

        # [V10.1b] code panel q10-01: Decimal(0.1) prints its 55 digits, the tail glows red
        self.at("Let's start with the most common one")
        self.play(FadeOut(VGroup(card, card.ticks[:2], crack), shift=LEFT * 3), run_time=0.7)
        code = code_panel(snippet_lines(TRAP, 5, 6), font_size=20).to_edge(UP, buff=0.35)
        out = output_console(TRAP, font_size=20).next_to(code, DOWN, buff=0.3)
        fit(out, 13.4)
        out.set_x(0)
        code.align_to(out, LEFT)
        lines = out.lines
        self.play(FadeIn(code, shift=DOWN * 0.2), FadeIn(out.background))
        self.at('so you write Decimal of zero point one')
        mark = line_highlight(code, 0)
        self.play(Create(mark), run_time=0.6)
        self.at('And you get our old friend')
        self.play(out.type_line(0, run_time=1.6))
        first = lines[0]
        value_at = first.source.index('= ') + 2
        self.at('sixteen zeros')
        zeros = first.chars(value_at + 3, value_at + 19)
        self.play(zeros.animate.set_color(FOCUS), run_time=0.5)
        self.at('nearly forty digits of junk')
        tail = first.chars(value_at + len('0.10000000000000000'))
        self.play(zeros.animate.set_color(GREY_A), tail.animate.set_color(ERROR), run_time=0.8)

        # What happened: the dime becomes a float before Decimal ever sees it
        self.at('What happened?')
        row_y = -2.3
        f_box = label_box('float', color=STORED, font_size=28).move_to([-2.4, row_y, 0])
        d_box = label_box('Decimal', color=EXACT, font_size=28).move_to([1.4, row_y, 0])
        a1 = Arrow([-5.0, row_y, 0], f_box.get_left(), buff=0.15, color=SCAFFOLD, stroke_width=3)
        a2 = Arrow(f_box.get_right(), d_box.get_left(), buff=0.15, color=SCAFFOLD, stroke_width=3)
        dime = coin('0.1', 0.42).move_to([-5.7, row_y, 0])
        self.play(FadeIn(f_box), FadeIn(d_box), Create(a1), Create(a2), FadeIn(dime, scale=0.6), run_time=0.9)
        self.at('Python read zero point one as a float first')
        self.play(dime.animate.move_to(f_box), run_time=1.0)
        self.play(FadeOut(dime, scale=0.4), f_box[0].animate.set_fill(STORED, 0.35), run_time=0.5)
        self.at('the dime was already gone')
        ghost = DashedVMobject(Circle(radius=0.42, color=MONEY), num_dashes=24).move_to([-5.7, row_y, 0])
        chip = Square(0.32).set_fill(STORED, 1).set_stroke(width=0).move_to(f_box)
        self.play(FadeIn(ghost), chip.animate.move_to(d_box.get_left() + RIGHT * 0.1), run_time=1.0)
        self.play(chip.animate.move_to(d_box).scale(0.2).set_opacity(0), run_time=0.4)
        self.remove(chip)
        self.at('Decimal then did its job perfectly')
        tick = checkmark(size=0.35).next_to(d_box, RIGHT, buff=0.25)
        self.play(Create(tick), d_box[0].animate.set_fill(EXACT, 0.25), run_time=0.6)
        self.at('error and all')
        self.play(Indicate(tail, color=ERROR, scale_factor=1.05), run_time=0.8)

        # [V10.1c] Decimal("0.1"): a clean 0.1 in green; equal? False in red; QR q10-01
        self.at('Give it the string zero point one instead')
        self.play(Transform(mark, line_highlight(code, 1)), run_time=0.5)
        text_chip = token('"0.1"', EXACT, font_size=24).move_to([-5.7, row_y, 0])
        self.play(FadeOut(ghost), FadeIn(text_chip, scale=0.7), run_time=0.4)
        self.play(text_chip.animate.move_to(d_box.get_top() + UP * 0.45), path_arc=-PI / 2.5, run_time=1.0)
        lines[1].part('0.1', occurrence=1).set_color(EXACT)
        card_q = show_qr(self, 'q10-01')
        self.play(out.type_line(1, run_time=0.6))
        self.at('and you get exactly one tenth')
        lines[2].part('False').set_color(ERROR)
        self.play(out.type_line(2, run_time=0.5))

        # [V10.1d] three dimes: the text-born 0.3 is green, the float-born tail red
        self.at('Three of those make exactly zero point three')
        lines[4].part('0.3').set_color(EXACT)
        self.play(out.type_line(4, run_time=0.9))
        self.at("Three of the float-born ones don't")
        born = lines[3]
        born.chars(born.source.index('0.3000000000000000') + len('0.3000000000000000')).set_color(ERROR)
        self.play(out.type_line(3, run_time=1.0))

        # [V10.1e] the Java version slides in; its 55-digit line sits right under Python's
        self.at('Java has exactly the same trap')
        drop_qr(self, card_q)
        self.play(FadeOut(VGroup(code, mark, f_box, d_box, a1, a2, chip, tick, text_chip)), run_time=0.6)
        self.play(out.animate.to_edge(UP, buff=0.55), run_time=0.8)
        py_label = Text('Python', font_size=22, color=SCAFFOLD).next_to(out.background, UP, buff=0.08, aligned_edge=LEFT)
        java = java_panel(script_block('10.1', 'java'), font_size=20)
        java.next_to(out, DOWN, buff=0.35).align_to(out, LEFT)
        java_label = Text('Java', font_size=22, color=SCAFFOLD).next_to(java, RIGHT, buff=0.3, aligned_edge=UP)
        printed = Console(script_block('10.1', 'text').splitlines(), font_size=20)
        printed.scale(lines[0].cell / printed.lines[0].cell)    # same column width as the Python console
        printed.next_to(java, DOWN, buff=0.3)
        # Line the Java value up under the Python value, column for column (first digit on first digit).
        printed.shift(RIGHT * (lines[0].chars(value_at, value_at + 1)[0].get_left()[0]
                               - printed.lines[0].glyphs[0].get_left()[0]))
        jl = printed.lines
        jtail = jl[0].chars(len('0.10000000000000000'))
        jtail.set_color(ERROR)
        java.shift(RIGHT * 14)
        self.play(FadeIn(py_label), java.animate.shift(LEFT * 14), run_time=1.0)
        self.play(FadeIn(java_label), FadeIn(printed.background), run_time=0.4)
        self.at('gives the same fifty-five digits')
        jmark = line_highlight(java, 0)
        self.play(Create(jmark), printed.type_line(0, run_time=1.4))
        # Same digits, same columns: two boxes of exactly the same width, one above the other.
        guides = VGroup(SurroundingRectangle(lines[0].chars(value_at), color=FOCUS, buff=0.05),
                        SurroundingRectangle(jl[0].glyphs, color=FOCUS, buff=0.05))
        self.play(Create(guides), run_time=0.8)
        self.at('Pass a string')
        jl[1].glyphs.set_color(EXACT)
        jl[2].glyphs.set_color(EXACT)
        self.play(Transform(jmark, line_highlight(java, 1)), printed.type_line(1, run_time=0.4))
        self.at('or use value of')
        self.play(Transform(jmark, line_highlight(java, 2)), printed.type_line(2, run_time=0.4))
        self.at('The rule is the same everywhere')
        rule = caption('A decimal is only as exact as the digits you hand it.', font_size=30, color=FOCUS)
        rule.to_edge(DOWN, buff=0.35)
        self.play(FadeOut(guides), Write(rule), run_time=1.6)
        self.finish()


# ---------------------------------------------------------------- 10.2

class Segment_10_2(Segment):
    """Decimals still round (q10-02)."""
    EPISODE, SEGMENT = 10, '10.2'

    def construct(self):
        # [V10.2a] code panel q10-02; the console prints the precision; QR q10-02
        code = code_panel(snippet_lines(THIRD, 6, 9), font_size=20).to_corner(UL, buff=0.4)
        out = Console(snippet_output(THIRD)[:6], font_size=20)   # the TypeError line belongs to 10.3
        out.next_to(code, DOWN, buff=0.3, aligned_edge=LEFT)
        lines = out.lines
        self.play(FadeIn(code, shift=DOWN * 0.2), FadeIn(out.background))
        card_q = show_qr(self, 'q10-02')
        self.play(out.type_line(0, run_time=0.8))

        # [V10.2b] 1/3 and the episode 1 pie, filled with tenths, hundredths ... to 28 places
        center, radius = np.array([3.0, 1.55, 0]), 1.25
        self.at('Remember the rule from episode one')
        third = Text('1/3', font_size=44, color=FOCUS).move_to([1.85, 3.35, 0])
        rule = Text('10 = 2 × 5', font_size=28, color=SCAFFOLD).move_to([4.6, 3.35, 0])
        pie = Circle(radius=radius).set_stroke(GREY_B, 2).move_to(center)
        target = wedge(center, radius, 0, Fraction(1, 3), FOCUS, 0).set_stroke(FOCUS, 3)
        self.play(FadeIn(third), Create(pie), run_time=0.8)
        self.at('built from twos and fives')
        self.play(FadeIn(rule, shift=DOWN * 0.2), run_time=0.6)
        self.at('One third has a three in it')
        cross = crossmark(size=0.4).next_to(rule, RIGHT, buff=0.2)
        self.play(third[2].animate.set_color(ERROR), Create(target), FadeIn(cross), run_time=0.8)
        self.at('it goes on forever')
        digits = MonoLine(output_line(THIRD, '1/3     =').split('= ')[1], font_size=20, color=FOCUS)
        digits.move_to([4.0, -0.35, 0])
        legend = VGroup()
        colours = [STORED, TEAL, EXACT, PURPLE]
        names = ['tenths', 'hundredths', 'thousandths', '… 28 places']
        filled, previous = VGroup(), Fraction(0)
        self.add(digits.glyphs[:2])        # "0."
        for k in range(28):
            current = Fraction(int('3' * (k + 1)), 10 ** (k + 1))
            # Past the fifth place the pieces are far thinner than a pixel; only the digits go on.
            piece = wedge(center, radius, previous, current, colours[min(k, 3)]) if k < 5 else VGroup()
            previous = current
            filled.add(piece)
            if k < 3:
                entry = VGroup(Square(0.25).set_fill(colours[k], 0.9).set_stroke(width=0),
                               Text(names[k], font_size=20, color=SCAFFOLD)).arrange(RIGHT, buff=0.15)
                legend.add(entry)
                entry.move_to([5.6, 2.6 - 0.45 * k, 0]).align_to([4.55, 0, 0], LEFT)
                self.play(FadeIn(piece), FadeIn(entry), FadeIn(digits.glyphs[2 + k]), run_time=0.7)
            else:
                self.add(piece)
                self.play(FadeIn(digits.glyphs[2 + k]), run_time=0.12)
        entry = VGroup(Square(0.25).set_fill(colours[3], 0.9).set_stroke(width=0),
                       Text(names[3], font_size=20, color=SCAFFOLD)).arrange(RIGHT, buff=0.15)
        entry.next_to(legend, DOWN, buff=0.2, aligned_edge=LEFT)
        legend.add(entry)
        # What 28 threes leave over: 1/3 - 0.333...3 (computed above); far too thin to draw, so mark it.
        edge = Line(center, center + radius * np.array([math.cos(PI / 2 - TAU / 3), math.sin(PI / 2 - TAU / 3), 0]),
                    color=ERROR, stroke_width=5)
        sliver = Text('a sliver is always left', font_size=20, color=ERROR).move_to([3.0, 0.05, 0])
        self.play(FadeIn(entry), Create(edge), FadeIn(sliver), run_time=0.8)

        # [V10.2c] 28 threes, then 28 nines, counted with a ruler; equals 1? False
        self.at("Python's decimal module keeps")
        drop_qr(self, card_q)
        self.play(lines[0].part('28').animate.set_color(FOCUS), run_time=0.4)
        self.at('One third becomes twenty-eight threes')
        self.play(FadeOut(digits.glyphs, target_position=lines[1].glyphs.get_center()), out.type_line(1, run_time=1.2))
        self.at('Multiply by three')
        self.play(out.type_line(2, run_time=1.2))
        nines = [g for g, ch in zip(lines[2].glyphs, lines[2].source.replace(' ', '')) if ch == '9']
        ruler = VGroup(*[Line(UP * 0.07, DOWN * 0.07, color=FOCUS, stroke_width=2).next_to(g, DOWN, buff=0.04)
                         for g in nines])
        count = number(0, font_size=24, color=FOCUS)
        count.next_to(lines[2].glyphs, RIGHT, buff=0.3)
        self.add(count)
        self.play(LaggedStart(*[Create(t) for t in ruler], lag_ratio=0.6),
                  count.animate.set_value(len(nines)), run_time=1.6, rate_func=linear)
        self.at('which is not one')
        lines[3].part('False').set_color(ERROR)
        self.play(out.type_line(3, run_time=0.5))
        self.at('It simply rounds in base ten')
        self.play(Indicate(VGroup(edge, sliver), color=ERROR, scale_factor=1.05), run_time=0.9)

        # [V10.2d] the precision dial turns from 28 down to 6; two six-digit sums
        self.at('That precision is a setting')
        self.play(FadeOut(VGroup(third, rule, cross, pie, target, filled, legend, edge, sliver, ruler, count)), run_time=0.6)
        dial = precision_dial(np.array([4.0, 1.6, 0]), radius=1.15)
        self.play(FadeIn(dial), run_time=0.6)
        self.at('Turn it down to six digits')
        self.play(dial.tracker.animate.set_value(6), run_time=1.6)
        for part in dial:
            part.clear_updaters()
        lines[4].part('1234.57').set_color(EXACT)
        self.play(out.type_line(4, run_time=1.0))
        self.at('Add a cent to twelve thousand')
        printed = output_line(THIRD, '12345.67 +').split('= ')[1]
        lines[5].part(printed, occurrence=0).set_color(ERROR)
        self.play(out.type_line(5, run_time=1.0))
        self.at('the answer needs seven digits')
        with localcontext() as ctx:            # the true sum, at the default 28 digits
            ctx.prec = 28
            true_sum = Decimal('12345.67') + Decimal('0.01')
        truth = MonoLine(str(true_sum), font_size=36, color=FOCUS).move_to([4.0, -1.2, 0])
        caption_true = Text('true answer', font_size=20, color=SCAFFOLD).next_to(truth, UP, buff=0.15)
        bracket = Brace(truth.glyphs, DOWN, buff=0.08, color=FOCUS)
        seven = Text(f'{len(str(true_sum).replace(".", ""))} digits', font_size=20, color=FOCUS).next_to(bracket, DOWN, buff=0.1)
        self.play(FadeIn(truth), FadeIn(caption_true), run_time=0.5)
        self.play(GrowFromCenter(bracket), FadeIn(seven), run_time=0.6)
        self.at('It gets rounded to')
        last = truth.glyphs[-1]
        strike = Line(last.get_corner(DL), last.get_corner(UR), color=ERROR, stroke_width=4)
        self.play(Create(strike), last.animate.set_color(ERROR), run_time=0.6)
        self.at('Two cents appeared from nowhere')
        gained = Decimal(printed) - true_sum    # 12345.7 - 12345.68
        cents = VGroup(penny(0.3), penny(0.3)).arrange(RIGHT, buff=0.15).move_to([3.4, -3.3, 0])
        plus = Text(f'+{gained}', font_size=28, color=ERROR).next_to(cents, RIGHT, buff=0.3)
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.6, scale=0.5) for c in cents], lag_ratio=0.4),
                  FadeIn(plus), run_time=0.9)
        self.at('and nothing complained')
        self.play(Wiggle(VGroup(cents, plus)), run_time=0.8)

        # The setting is per thread: one change reaches every calculation that follows
        self.at('Nobody sets the precision')
        self.play(FadeOut(VGroup(truth, caption_true, bracket, seven, strike, cents, plus)), run_time=0.5)
        self.play(dial.animate.scale(0.7).move_to([2.5, 1.9, 0]), run_time=0.6)
        self.at('forget it applies to the whole thread')
        jobs = VGroup(*[label_box(t, font_size=22) for t in ('totals', 'tax', 'interest', 'refunds')])
        jobs.arrange(DOWN, buff=0.3).move_to([5.6, 0.6, 0])
        wires = VGroup(*[Line(dial.get_right() + RIGHT * 0.1, j.get_left(), color=ERROR, stroke_width=2) for j in jobs])
        sixes = VGroup(*[Text('6', font_size=22, color=ERROR).next_to(j, RIGHT, buff=0.15) for j in jobs])
        self.play(LaggedStart(*[AnimationGroup(Create(w), FadeIn(j), FadeIn(s)) for w, j, s in zip(wires, jobs, sixes)],
                              lag_ratio=0.3), run_time=1.6)
        self.at('decide how many places you keep')
        plan = label_box('round there, on purpose: quantize', color=EXACT, font_size=26, fill=EXACT)
        plan.move_to([3.6, -2.6, 0])
        self.play(FadeIn(plan, shift=UP * 0.2), run_time=0.7)
        self.at('with quantize')
        self.play(Indicate(plan, color=EXACT, scale_factor=1.06), run_time=0.8)
        self.finish()


# ---------------------------------------------------------------- 10.3

class Segment_10_3(Segment):
    """When types meet (q10-02, last lines)."""
    EPISODE, SEGMENT = 10, '10.3'

    def construct(self):
        # [V10.3a] Decimal 1.10 and float 1.10 slide together; a red barrier drops; TypeError
        code = code_panel(snippet_lines(THIRD, 15, 18), font_size=20).to_edge(UP, buff=0.3)
        out = output_console(THIRD, ['Decimal + float'], font_size=18).to_edge(DOWN, buff=0.45)
        y = -0.3
        dec = token('Decimal 1.10', EXACT).move_to([-5.0, y, 0])
        flo = token('float 1.10', STORED).move_to([5.0, y, 0])
        self.play(FadeIn(code, shift=DOWN * 0.2), FadeIn(out.background), FadeIn(dec), FadeIn(flo))
        self.at('Try adding a Decimal to a float')
        plus = Text('+', font_size=48, color=FOCUS).move_to([0, y, 0])
        self.play(dec.animate.move_to([-2.0, y, 0]), flo.animate.move_to([2.0, y, 0]), FadeIn(plus), run_time=1.4)
        self.at('and Python refuses')
        wall = barrier(1.9, label='TypeError').move_to([0, y + 0.2, 0])
        wall.shift(UP * 5)
        self.play(FadeOut(plus), wall.animate.shift(DOWN * 5), run_time=0.6, rate_func=rate_functions.ease_in_quad)
        self.play(dec.animate.shift(LEFT * 0.5), flo.animate.shift(RIGHT * 0.5), out.type_line(0, run_time=1.6),
                  run_time=1.6)
        self.at('Type error.')
        self.play(Indicate(wall[2], color=ERROR, scale_factor=1.2), run_time=0.6)

        # A gift: loud in testing, not silent in production; comparing is allowed
        self.at('That error is a gift')
        loud = VGroup(checkmark(size=0.32), Text('fails loudly, in testing', font_size=24, color=EXACT)).arrange(RIGHT, buff=0.2)
        quiet = VGroup(crossmark(size=0.3), Text('not silently, in production', font_size=24, color=ERROR)).arrange(RIGHT, buff=0.2)
        loud.move_to([-3.6, -1.35, 0])
        quiet.move_to([3.4, -1.35, 0])
        self.play(FadeIn(loud, shift=UP * 0.2), run_time=0.6)
        self.at('instead of silently')
        self.play(FadeIn(quiet, shift=UP * 0.2), run_time=0.6)
        self.at('Comparing a Decimal with a float is allowed')
        same = Text('==', font=MONO, font_size=30, color=EXACT).next_to(dec, RIGHT, buff=0.15)
        self.play(FadeIn(same), run_time=0.3)
        self.play(same.animate.next_to(flo, LEFT, buff=0.15), path_arc=-PI * 0.7, run_time=1.2)
        ok = checkmark(size=0.3).next_to(same, UP, buff=0.1)
        self.play(Create(ok), run_time=0.4)
        self.at('but arithmetic between them is not')
        add = Text('+', font=MONO, font_size=34, color=ERROR).next_to(dec, RIGHT, buff=0.15)
        self.play(FadeIn(add), run_time=0.2)
        self.play(add.animate.next_to(wall, LEFT, buff=0.05), run_time=0.5, rate_func=rate_functions.ease_in_quad)
        self.play(add.animate.next_to(dec, RIGHT, buff=0.15), run_time=0.5, rate_func=rate_functions.ease_out_bounce)

        # [V10.3b] split screen: Python's barrier, and elsewhere a quiet merge into float
        self.at('Many languages and libraries are more forgiving')
        self.play(FadeOut(VGroup(code, out.background, out.lines[0], loud, quiet, same, ok, add)), run_time=0.6)
        left_group = VGroup(dec, flo, wall)
        divider = DashedLine(UP * 3.2, DOWN * 3.6, color=GREY_D)
        h_left = Text('Python', font_size=28, color=SCAFFOLD).move_to([-3.55, 3.3, 0])
        h_right = Text('many other languages and libraries', font_size=26, color=SCAFFOLD).move_to([3.55, 3.3, 0])
        fit(h_right, 6.6)
        small_dec = token('Decimal 1.10', EXACT, font_size=22).move_to([-5.2, 1.2, 0])
        small_flo = token('float 1.10', STORED, font_size=22).move_to([-1.9, 1.2, 0])
        small_wall = barrier(1.4, label='TypeError', font_size=20).move_to([-3.5, 1.35, 0])
        self.play(ReplacementTransform(left_group, VGroup(small_dec, small_flo, small_wall)),
                  Create(divider), FadeIn(h_left), FadeIn(h_right), run_time=1.0)
        r_dec = token('Decimal 1.10', EXACT, font_size=22).move_to([2.0, 1.2, 0])
        r_flo = token('float 1.10', STORED, font_size=22).move_to([5.3, 1.2, 0])
        self.play(FadeIn(r_dec), FadeIn(r_flo), run_time=0.5)
        self.at('and forgiving is exactly')
        merged = token('float', STORED, font_size=22).move_to([3.65, 1.2, 0])
        self.play(*recolor_token(r_dec, STORED), run_time=0.6)
        self.play(r_dec.animate.move_to(merged), r_flo.animate.move_to(merged), run_time=0.8)
        self.play(FadeOut(VGroup(r_dec, r_flo)), FadeIn(merged), run_time=0.3)
        warn = warning_icon().next_to(merged, UP, buff=0.2)
        self.play(FadeIn(warn), run_time=0.3)
        for _ in range(2):
            self.play(warn.animate.set_opacity(0.15), run_time=0.3)
            self.play(warn.animate.set_opacity(1), run_time=0.3)

        # One stray float turns the whole calculation back into a float
        self.at('one stray float anywhere')
        chain = VGroup(*[token(t, EXACT, font_size=20) for t in ('Decimal', 'float', 'Decimal')])
        chain.arrange(RIGHT, buff=0.35).move_to([3.6, -1.2, 0])
        for chip, colour in zip(chain, (EXACT, STORED, EXACT)):
            chip.box.set_stroke(colour, 3).set_fill(colour, 0.15)
            chip.label.set_color(colour)
        pluses = VGroup(*[Text('+', font_size=24, color=SCAFFOLD).move_to((a.get_right() + b.get_left()) / 2)
                          for a, b in zip(chain[:-1], chain[1:])])
        self.play(FadeIn(chain, lag_ratio=0.2), FadeIn(pluses), run_time=0.9)
        self.at('turns the whole result back')
        self.play(LaggedStart(*[AnimationGroup(*recolor_token(c, STORED)) for c in chain], lag_ratio=0.3), run_time=1.2)
        result = token('float', STORED, font_size=22).next_to(chain, DOWN, buff=0.5)
        arrow = Arrow(chain.get_bottom(), result.get_top(), buff=0.08, color=STORED, stroke_width=3)
        self.play(GrowArrow(arrow), FadeIn(result), run_time=0.6)
        left_note = Text('mixing stops here', font_size=22, color=ERROR).next_to(small_wall, DOWN, buff=0.4)
        self.play(FadeIn(left_note), run_time=0.5)
        self.at('When you choose a money library')
        note = caption('Check what your money library does when the two meet.', font_size=28, color=FOCUS)
        note.to_edge(DOWN, buff=0.4)
        self.play(Write(note), run_time=1.4)
        self.finish()


# ---------------------------------------------------------------- 10.4

class Segment_10_4(Segment):
    """Integer cents, broken two ways (q10-03)."""
    EPISODE, SEGMENT = 10, '10.4'

    def construct(self):
        # [V10.4a] a price tag goes into "store cents" and comes out as 1234
        tag = price_tag('$12.34').move_to([-5.0, 2.2, 0])
        store = label_box('store cents', font_size=26).move_to([-1.2, 2.2, 0])
        cents = 1234                           # $12.34 in cents
        stored = Text(str(cents), font=MONO, font_size=34, color=MONEY).move_to([2.3, 2.2, 0])
        self.play(FadeIn(tag), FadeIn(store), run_time=0.6)
        self.play(tag.animate.move_to(store).scale(0.4).set_opacity(0), run_time=0.9)
        self.play(FadeIn(stored, shift=RIGHT * 0.5), run_time=0.5)
        self.at('They add exactly')
        good = VGroup(*[VGroup(checkmark(size=0.28), Text(t, font_size=22, color=EXACT)).arrange(RIGHT, buff=0.15)
                        for t in ('add exactly', 'compare exactly', 'never drift')]).arrange(RIGHT, buff=0.6)
        good.move_to([0, 1.1, 0])
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.2) for g in good], lag_ratio=0.4), run_time=1.4)
        self.at('two failure modes of their own')
        self.play(FadeOut(good), run_time=0.4)

        # [V10.4b] the wrong-unit bugs: cents shown as dollars, dollars converted twice
        self.at('the decimal point mistake')
        self.play(Indicate(stored, color=FOCUS), run_time=0.7)
        self.at('Show cents as dollars')
        show = label_box('show dollars', font_size=26).move_to([-1.2, 0.4, 0])
        shown = Text(f'${cents:,.2f}', font=MONO, font_size=34, color=ERROR).move_to([2.6, 0.4, 0])  # 1234 read as dollars
        moving = stored.copy()
        self.play(FadeIn(show), run_time=0.4)
        self.play(moving.animate.move_to(show).scale(0.4).set_opacity(0), run_time=0.8)
        self.play(FadeIn(shown, shift=RIGHT * 0.5), run_time=0.5)
        self.at('Convert to cents twice')
        tag2 = price_tag('$12.34').move_to([-5.0, -1.6, 0])
        x1 = label_box('× 100', font_size=26).move_to([-2.4, -1.6, 0])
        mid = Text(str(cents), font=MONO, font_size=28, color=MONEY).move_to([-0.6, -1.6, 0])
        x2 = label_box('× 100', font_size=26).move_to([1.2, -1.6, 0])
        twice = Text(str(cents * 100), font=MONO, font_size=34, color=ERROR).move_to([3.6, -1.6, 0])  # 1234 × 100
        self.play(FadeIn(tag2), FadeIn(x1), FadeIn(x2), run_time=0.5)
        self.play(tag2.animate.move_to(x1).scale(0.4).set_opacity(0), run_time=0.7)
        self.play(FadeIn(mid, shift=RIGHT * 0.3), run_time=0.4)
        self.play(mid.animate.move_to(x2).scale(0.4).set_opacity(0), run_time=0.7)
        self.play(FadeIn(twice, shift=RIGHT * 0.5), run_time=0.5)
        self.at('off by a factor of a hundred')
        badges = VGroup(Text('× 100 too big', font_size=22, color=ERROR).next_to(shown, DOWN, buff=0.15),
                        Text('× 100 too big', font_size=22, color=ERROR).next_to(twice, DOWN, buff=0.15))
        self.play(FadeIn(badges, shift=UP * 0.2), run_time=0.6)
        self.at("doesn't say what unit")
        self.play(FadeOut(VGroup(tag, store, show, shown, x1, x2, twice, badges, moving, mid, tag2)), run_time=0.5)
        self.play(stored.animate.move_to([0, 0.4, 0]).scale(1.8), run_time=0.7)
        maybe = VGroup(Text('¢ ?', font_size=36, color=FOCUS).next_to(stored, LEFT, buff=0.6),
                       Text('$ ?', font_size=36, color=FOCUS).next_to(stored, RIGHT, buff=0.6))
        self.play(FadeIn(maybe[0], shift=RIGHT * 0.3), run_time=0.4)
        self.play(FadeIn(maybe[1], shift=LEFT * 0.3), run_time=0.4)
        self.play(Wiggle(maybe), run_time=0.8)

        # [V10.4c] code panel q10-03; a 32-bit row fills from the right up to the largest amount
        self.at('The second is size')
        self.play(FadeOut(VGroup(stored, maybe)), run_time=0.4)
        code = code_panel(snippet_lines(OVERFLOW, 4, 6), font_size=20).to_corner(UL, buff=0.35)
        out = output_console(OVERFLOW, font_size=18, width=12.6).next_to(code, DOWN, buff=0.25, aligned_edge=LEFT)
        lines = out.lines
        self.play(FadeIn(code, shift=DOWN * 0.2), FadeIn(out.background), run_time=0.7)
        self.at('imitates a thirty-two-bit integer')
        bits = BitRow(32, cell=0.28, sign_color=ERROR).move_to([0, 0, 0])
        bits.next_to(out, DOWN, buff=0.45).align_to(out, LEFT)
        bit_label = Text('32-bit signed integer', font_size=20, color=SCAFFOLD).next_to(bits, RIGHT, buff=0.25)
        sign = Text('sign', font_size=18, color=SCAFFOLD).next_to(bits.cells[0], DOWN, buff=0.08)
        self.play(FadeIn(bits), FadeIn(bit_label), FadeIn(sign), run_time=0.6)
        self.at('The biggest amount it can hold')
        grow = ValueTracker(0)
        odo = number(0, decimals=2, font_size=40, color=MONEY, commas=True)
        odo.move_to([-3.2, -2.1, 0])
        unit = Text('dollars', font_size=30, color=SCAFFOLD)
        unit.add_updater(lambda m: m.next_to(odo, RIGHT, buff=0.25, aligned_edge=DOWN))
        bits.add_updater(lambda m: m.show(int(2 ** grow.get_value()) - 1))
        odo.add_updater(lambda m: m.set_value((int(2 ** grow.get_value()) - 1) / 100))
        self.add(odo, unit)
        self.play(grow.animate.set_value(31), run_time=2.4, rate_func=linear)
        bits.clear_updaters()
        odo.clear_updaters()
        biggest = 2**31 - 1
        lines[0].part(f'${biggest / 100:,.2f}').set_color(MONEY)
        self.play(out.type_line(0, run_time=1.2))

        # [V10.4d] $2,000,000.00 lands on $20,000,000.00: the sign bit flips, the odometer wraps
        self.at('Add two million to a twenty million')
        card_q = show_qr(self, 'q10-03')
        balance, deposit = 2_000_000_000, 200_000_000      # the snippet's cents
        raw = ValueTracker(balance)
        bits.show(balance)
        odo.set_value(balance / 100)
        drop = price_tag(f'+${deposit / 100:,.2f}', font_size=26).move_to([0.8, -3.2, 0])
        self.play(FadeIn(drop, shift=DOWN * 0.4), run_time=0.5)
        self.play(drop.animate.move_to(odo).scale(0.3).set_opacity(0), run_time=0.7)

        def paint(m):
            m.set_value(as_int32(int(raw.get_value())) / 100)
            m.set_color(ERROR if m.get_value() < 0 else MONEY)
        bits.add_updater(lambda m: m.show(int(raw.get_value())))
        odo.add_updater(paint)
        self.at('and the bits run out')
        self.play(raw.animate.set_value(balance + deposit), run_time=3.0, rate_func=linear)
        bits.clear_updaters()
        odo.clear_updaters()
        self.at('to minus twenty point nine million')
        wrapped = output_line(OVERFLOW, '$2,000,000.00 =').split('= ')[1].split()[0]
        lines[1].part(wrapped).set_color(ERROR)
        self.play(out.type_line(1, run_time=1.2), Indicate(odo, color=ERROR, scale_factor=1.1))

        # Sixty-four bits: about 92 quadrillion dollars
        self.at('Sixty-four-bit integers push')
        drop_qr(self, card_q)
        wide = BitRow(64, cell=0.135, buff=0.016).move_to(bits).align_to(bits, LEFT)
        wide.show(2**63 - 1)
        wide.cells[0].set_fill(BLACK, 0)
        quad = round((2**63 - 1) / 100 / 1e15)   # 2⁶³ − 1 cents in quadrillions of dollars
        wide_label = Text(f'64 bits: about ${quad} quadrillion', font_size=22, color=EXACT)
        wide_label.next_to(wide, DOWN, buff=0.25).align_to(wide, LEFT)
        self.play(FadeOut(VGroup(odo, unit, sign)), ReplacementTransform(bits, wide),
                  ReplacementTransform(bit_label, wide_label), run_time=1.0)

        # [V10.4e] JavaScript: the far end of the float line, where the gaps grow from 1 to 2
        self.at('But every ordinary JavaScript number')
        safe = 2**53 - 1
        ticks = doubles_between(safe - 2, safe + 5)    # every double in that window
        line = FloatLine(safe - 2, safe + 5, width=11.0, ticks=ticks).move_to([-0.4, -2.0, 0])
        self.play(FadeOut(VGroup(wide, wide_label)), run_time=0.4)
        self.play(Create(line.axis), LaggedStart(*[Create(t) for t in line.ticks], lag_ratio=0.15), run_time=1.2)
        names = VGroup(
            Text(f'{safe:,}', font=MONO, font_size=20, color=SCAFFOLD).next_to(line.point(safe), DOWN, buff=0.35)
            .align_to(line.point(safe) + RIGHT * 0.25, RIGHT),
            Text(f'…{(safe + 1) % 1000}', font=MONO, font_size=20, color=SCAFFOLD).next_to(line.point(safe + 1), DOWN, buff=0.35),
            Text(f'…{(safe + 3) % 1000}', font=MONO, font_size=20, color=SCAFFOLD).next_to(line.point(safe + 3), DOWN, buff=0.35))
        self.play(FadeIn(names, lag_ratio=0.3), run_time=0.9)
        gaps = VGroup(
            Text('gap 1', font_size=20, color=STORED).move_to((line.point(safe - 1) + line.point(safe)) / 2 + UP * 0.45),
            Text('gap 2', font_size=20, color=STORED).move_to((line.point(safe + 1) + line.point(safe + 3)) / 2 + UP * 0.45))
        self.play(FadeIn(gaps), run_time=0.5)
        self.at('whole numbers stop being exact')
        lines[2].part(f'{safe:,}').set_color(FOCUS)
        self.play(out.type_line(2, run_time=1.0))
        self.at("In cents, that's about")
        trillions = round(safe / 100 / 1e12)          # 2⁵³ − 1 cents in trillions of dollars
        about = Text(f'≈ ${trillions} trillion', font_size=28, color=MONEY).next_to(names[0], DOWN, buff=0.25)
        self.play(FadeIn(about, shift=UP * 0.2), run_time=0.6)
        self.at('Past it, the next two whole numbers')
        self.play(FadeOut(gaps), run_time=0.3)
        marks = VGroup()
        for value, text in ((safe + 1, 'safe + 1'), (safe + 2, 'safe + 2')):
            d = line.diamond(value)
            label = Text(text, font_size=20, color=FOCUS).next_to(d, UP, buff=0.15)
            marks.add(VGroup(d, label))
        marks[0][1].shift(LEFT * 0.35)
        marks[1][1].shift(RIGHT * 0.35)
        self.play(FadeIn(marks, lag_ratio=0.4), run_time=0.8)
        self.at('land on the same tick')
        self.play(Create(line.snap(safe + 2)), Indicate(line.ticks[line.tick_values.index(float(safe + 1))],
                                                            color=FOCUS, scale_factor=1.6), run_time=1.0)
        self.play(out.type_line(3, run_time=1.2))
        self.finish()


# ---------------------------------------------------------------- 10.5

class Segment_10_5(Segment):
    """Minor units that don't fit (q10-04)."""
    EPISODE, SEGMENT = 10, '10.5'

    def construct(self):
        # [V10.5a] a table of minor units builds from q10-04's output; QR q10-04
        digits = ast.literal_eval(snippet_find(UNITS, 'minor_digits =').split('=', 1)[1].strip())
        units = {}
        for line in snippet_output(UNITS):
            m = re.match(r'(\w+): (1234\.5) = ([\d,]+) minor units', line)
            if m:
                units[m.group(1)] = (m.group(2), m.group(3))
        x_code, x_digits, x_units = -5.7, -3.75, -2.4
        head_y, pitch = 3.25, 0.62
        heads = VGroup(Text('currency', font_size=22, color=SCAFFOLD).move_to([x_code, head_y, 0]),
                       Text('digits', font_size=22, color=SCAFFOLD).move_to([x_digits, head_y, 0]),
                       Text('1234.5 in minor units', font_size=22, color=SCAFFOLD).move_to([0, head_y, 0]))
        heads[2].align_to([x_units, 0, 0], LEFT)
        frame = RoundedRectangle(width=9.6, height=3.85, corner_radius=0.15).set_stroke(GREY_D, 2)
        frame.move_to([-1.85, 1.5, 0])
        rule = Line([-6.5, head_y - 0.3, 0], [2.8, head_y - 0.3, 0], color=GREY_D)
        self.play(Create(frame), FadeIn(heads), Create(rule), run_time=0.8)
        card_q = show_qr(self, 'q10-04')
        row_mobs = {}

        def add_row(k, code, colour, grow=False):
            y = head_y - 0.75 - pitch * k
            name = Text(code, font=MONO, font_size=26, color=colour).move_to([x_code, y, 0])
            count = Text(str(digits[code]), font=MONO, font_size=26, color=colour).move_to([x_digits, y, 0])
            amount, minor = units[code]
            start = MonoLine(amount, font_size=24, color=FOCUS).set_anchor([x_units, y, 0])
            value = MonoLine(minor, font_size=24, color=colour).set_anchor([x_units, y, 0])
            self.play(FadeIn(name, shift=RIGHT * 0.3), FadeIn(count), FadeIn(start), run_time=0.5)
            if grow:
                self.play(FadeOut(start), run_time=0.2)
                self.play(LaggedStart(*[FadeIn(g, run_time=0.1) for g in value.glyphs], lag_ratio=1.0),
                          run_time=2.4, rate_func=rate_functions.ease_in_quad)
            else:
                self.play(FadeTransform(start, value), run_time=0.7)
            row_mobs[code] = VGroup(name, count, value)
            return row_mobs[code]

        self.at('The US dollar has two digits')
        add_row(0, 'USD', MONEY)
        self.at('The Japanese yen has none')
        add_row(1, 'JPY', MONEY)
        self.at('The Kuwaiti dinar has three')
        add_row(2, 'KWD', MONEY)

        # [V10.5b] the yen row: the half glows yellow, then falls off as int truncates it
        self.at('And look at the yen row')
        drop_qr(self, card_q)
        jpy = row_mobs['JPY']
        ring = SurroundingRectangle(jpy, color=FOCUS, buff=0.1)
        self.play(Create(ring), run_time=0.5)
        amount = MonoLine(units['JPY'][0], font_size=48, color=WHITE).move_to([-3.2, -1.6, 0])
        half = amount.part('.5')
        call = Text('int( )', font=MONO, font_size=30, color=SCAFFOLD).next_to(amount, LEFT, buff=0.5)
        self.play(FadeIn(amount), FadeIn(call), run_time=0.5)
        self.at("There's no such thing as half a yen")
        self.play(half.animate.set_color(FOCUS).scale(1.2), run_time=0.5)
        self.at('so int quietly dropped it')
        self.play(half.animate.shift(DOWN * 1.6).rotate(-0.6).set_opacity(0), run_time=1.0,
                  rate_func=rate_functions.ease_in_quad)
        dropped = Text('½ yen dropped', font_size=28, color=ERROR).next_to(amount, RIGHT, buff=0.6)
        self.play(FadeIn(dropped, shift=LEFT * 0.2), run_time=0.5)
        self.at('Whether that half should be rounded')
        choices = VGroup(*[label_box(t, font_size=24) for t in ('round', 'refuse', 'carry', 'truncate')])
        choices.arrange(RIGHT, buff=0.35).move_to([2.6, -3.1, 0])
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in choices], lag_ratio=0.25), run_time=1.2)
        self.at('the code just picked one')
        self.play(choices[3][0].animate.set_stroke(ERROR, 3), choices[3][1].animate.set_color(ERROR),
                  Indicate(choices[3], color=ERROR, scale_factor=1.1), run_time=0.8)

        # [V10.5c] the wrong exponent: 1000 yen read with two decimal places shows as 10
        self.at('Hard-code two decimal places')
        self.play(FadeOut(VGroup(ring, amount, call, dropped, choices)), run_time=0.5)
        wrong = output_line(UNITS, 'Wrong exponent')
        m = re.search(r'(\d+) JPY stored as cents shows as (\d+) JPY', wrong)
        yen, shown = m.group(1), m.group(2)
        tag = price_tag(f'¥{yen}', font_size=28).move_to([-5.3, -1.5, 0])
        kept = Text(f'stored: {yen}', font=MONO, font_size=28, color=MONEY).move_to([-2.0, -1.5, 0])
        reader = label_box('read with 2 decimals', font_size=24).move_to([1.6, -1.5, 0])
        result = Text(f'{shown} JPY', font=MONO, font_size=40, color=ERROR).move_to([4.9, -1.5, 0])
        self.play(FadeIn(tag), run_time=0.4)
        self.play(TransformFromCopy(tag, kept), run_time=0.7)
        self.play(FadeIn(reader), run_time=0.4)
        self.at('displays as ten')
        self.play(FadeTransform(kept.copy(), result), run_time=0.8)
        self.play(result.animate.scale(0.7), run_time=0.6)
        line = Console([wrong], font_size=20).move_to([0, -3.1, 0])
        line.lines[0].part(f'{shown} JPY', occurrence=0).set_color(ERROR)
        self.play(FadeIn(line.background), line.type_line(0, run_time=1.2))

        # BTC and ETH join the table; the ETH number spills past its edge
        self.at('Cryptocurrencies stretch this further')
        self.play(FadeOut(VGroup(tag, kept, reader, result, line.background, line.lines[0])), run_time=0.5)
        self.at('A bitcoin divides')
        add_row(3, 'BTC', STORED)
        self.at('Ether divides')
        eth = add_row(4, 'ETH', STORED, grow=True)
        btc = row_mobs['BTC']
        brace = Brace(VGroup(btc, eth), RIGHT, color=STORED)
        brace.set_x(eth[2].get_right()[0] + 0.2 + brace.width / 2)
        iso = Text('not ISO 4217', font_size=22, color=STORED).next_to(brace, RIGHT, buff=0.15)
        self.play(GrowFromCenter(brace), FadeIn(iso), run_time=0.6)

        # [V10.5d] a 64-bit row fills completely: it holds only about 18.45 ether in wei
        self.at('an unsigned sixty-four-bit integer')
        bits = BitRow(64, cell=0.135, buff=0.016).move_to([-1.9, -1.15, 0])
        bit_label = Text('64 bits, all ones', font_size=22, color=SCAFFOLD).next_to(bits, RIGHT, buff=0.3)
        self.play(FadeIn(bits), FadeIn(bit_label), run_time=0.4)
        self.play(LaggedStart(*[c.animate.set_fill(STORED, 0.9) for c in reversed(bits.cells)], lag_ratio=0.08),
                  run_time=1.6)
        limit_lines = [output_line(UNITS, 'uint64 limit'), output_line(UNITS, 'that is only')]
        ether = re.search(r'only ([\d.]+) ether', limit_lines[1]).group(1)
        whole, frac = int(Decimal(ether)), float(Decimal(ether) % 1)
        legend = VGroup(coin('ETH', 0.42), Text('= 1 ether', font_size=22, color=MONEY)).arrange(RIGHT, buff=0.2)
        legend.move_to([-5.4, -2.25, 0])
        coins = VGroup(*[coin('1', 0.17)[:2] for _ in range(whole)]).arrange(RIGHT, buff=0.08)
        # the last coin, filled only to the fraction left over (0.4467... of an ether)
        part = VGroup(Circle(radius=0.17).set_stroke(MONEY, 2),
                      Sector(radius=0.17, start_angle=PI / 2 - TAU * frac, angle=TAU * frac).set_fill(MONEY, 1).set_stroke(width=0))
        stack = VGroup(*coins, part).arrange(RIGHT, buff=0.08).next_to(legend, RIGHT, buff=0.4)
        stack.set_y(-2.25)
        self.play(FadeIn(legend), run_time=0.4)
        self.at('holds only about eighteen and a half ether')
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.3) for c in stack], lag_ratio=0.25), run_time=2.0)
        limit = Console(limit_lines, font_size=20).move_to([-1.5, -3.3, 0])
        limit.lines[1].part(ether).set_color(MONEY)
        self.play(FadeIn(limit.background), limit.type_line(0, run_time=0.8))
        self.play(limit.type_line(1, run_time=0.8))
        self.at("Ethereum's own arithmetic uses")
        wider = VGroup(*[BitRow(64, cell=0.033, buff=0.004) for _ in range(4)]).arrange(RIGHT, buff=0.02)
        wider.match_width(bits).move_to(bits)
        for r in wider:
            r.show(0)
        wider[3].show(2**64 - 1)
        wide_label = Text('256 bits', font_size=22, color=EXACT).move_to(bit_label, aligned_edge=LEFT)
        self.play(ReplacementTransform(bits, wider[3]), FadeIn(wider[:3]), ReplacementTransform(bit_label, wide_label),
                  run_time=1.2)

        # An amount travels with its currency; the digits come from the currency
        self.at('So an amount should always travel')
        self.play(FadeOut(VGroup(wider, wide_label, legend, stack, limit.background, *limit.lines)), run_time=0.5)
        pairs = VGroup()
        for code in ('USD', 'JPY', 'KWD'):
            amt = price_tag('1234.5', font_size=24)
            cur = label_box(code, color=MONEY, font_size=24)
            link = Line(LEFT * 0.25, RIGHT * 0.25, color=MONEY, stroke_width=4)
            pairs.add(VGroup(amt, link, cur).arrange(RIGHT, buff=0.05))
        pairs.arrange(RIGHT, buff=0.7).move_to([0, -1.5, 0])
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in pairs], lag_ratio=0.3), run_time=1.2)
        self.at('the number of digits should come from the currency')
        notes = VGroup(*[Text(f'{digits[code]} digits', font_size=22, color=EXACT).next_to(p[2], DOWN, buff=0.45)
                         for code, p in zip(('USD', 'JPY', 'KWD'), pairs)])
        arrows = VGroup(*[Arrow(p[2].get_bottom(), n.get_top(), buff=0.06, color=EXACT, stroke_width=3)
                          for p, n in zip(pairs, notes)])
        self.play(LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(n)) for a, n in zip(arrows, notes)], lag_ratio=0.3),
                  run_time=1.2)
        self.finish()


# ---------------------------------------------------------------- 10.6

CENT = Decimal('0.01')


def cent_line(center, prefix, x, y=-2.65):
    """The float line motif with ticks one cent apart, around `center`."""
    ticks = [center - CENT, center, center + CENT]
    line = FloatLine(center - Decimal('0.015'), center + Decimal('0.015'), width=4.2, ticks=ticks,
                     tick_height=0.3, color=MONEY).move_to([x, y, 0])
    labels = VGroup(*[Text(f'{prefix}{t}', font=MONO, font_size=18, color=SCAFFOLD)
                      .next_to(line.point(t), DOWN, buff=0.22) for t in ticks])
    group = VGroup(line, labels)
    group.line, group.labels = line, labels
    return group


class Segment_10_6(Segment):
    """There and back again (q10-05)."""
    EPISODE, SEGMENT = 10, '10.6'

    def construct(self):
        found = re.search(r'rate: ([\d.]+)\s+inverse: ([\d.]+)\s+rate \* inverse: ([\d.]+)', snippet_output(TRIP)[0])
        rate, inverse, product = (Decimal(g) for g in found.groups())

        # [V10.6a] two gold coins, $ and €, with the rate and its inverse on the arrows
        usd_coin = coin('$', 0.55).move_to([-3.0, 2.55, 0])
        eur_coin = coin('€', 0.55).move_to([3.0, 2.55, 0])
        self.play(FadeIn(usd_coin, scale=0.6), FadeIn(eur_coin, scale=0.6), run_time=0.8)
        self.at('made-up exchange rate')
        there = CurvedArrow(usd_coin.get_right() + UP * 0.2, eur_coin.get_left() + UP * 0.2, angle=-PI / 7, color=MONEY)
        back = CurvedArrow(eur_coin.get_left() + DOWN * 0.2, usd_coin.get_right() + DOWN * 0.2, angle=-PI / 7, color=MONEY)
        rate_label = Text(f'rate × {rate}', font_size=24, color=MONEY).next_to(there, UP, buff=0.08)
        inv_label = Text(f'inverse × {inverse}', font_size=24, color=MONEY).next_to(back, DOWN, buff=0.08)
        self.play(Create(there), FadeIn(rate_label), run_time=0.9)
        self.at('and its inverse')
        self.play(Create(back), FadeIn(inv_label), run_time=0.9)

        # [V10.6b] rate * inverse falls short of 1, by a bracketed gap
        out = output_console(TRIP, font_size=22)
        out.to_edge(LEFT, buff=0.5).set_y(1.2 - out.background.height / 2)
        lines = out.lines
        self.at('Multiply them together')
        lines[0].part(str(product)).set_color(FOCUS)
        self.play(FadeIn(out.background), run_time=0.3)
        self.play(out.type_line(0, run_time=1.2))
        lo, hi = Decimal('0.9999'), Decimal('1')
        axis = Line([-5.0, -2.4, 0], [5.0, -2.4, 0], color=SCAFFOLD, stroke_width=2)

        def at_x(v):
            return -5.0 + 10.0 * float((v - lo) / (hi - lo))
        ends = VGroup(*[Line(UP * 0.15, DOWN * 0.15, color=SCAFFOLD, stroke_width=3).move_to([at_x(v), -2.4, 0]) for v in (lo, hi)])
        end_labels = VGroup(Text(str(lo), font=MONO, font_size=20, color=SCAFFOLD).next_to(ends[0], DOWN, buff=0.15),
                            Text('1', font=MONO, font_size=24, color=FOCUS).next_to(ends[1], DOWN, buff=0.15))
        dot = Dot([at_x(product), -2.4, 0], radius=0.1, color=STORED)
        dot_label = Text(str(product), font=MONO, font_size=20, color=STORED).next_to(dot, DOWN, buff=0.2)
        self.play(Create(axis), FadeIn(ends), FadeIn(end_labels), run_time=0.6)
        self.play(FadeIn(dot, scale=0.5), FadeIn(dot_label), run_time=0.5)
        self.at('You get a little less')
        brace = BraceBetweenPoints(dot.get_center() + UP * 0.12, ends[1].get_top() + UP * 0.02, direction=UP, color=FOCUS)
        short = Text(f'short by {hi - product}', font_size=22, color=FOCUS).next_to(brace, UP, buff=0.1)
        self.play(GrowFromCenter(brace), FadeIn(short), run_time=0.7)
        self.at('An inverse rate is rarely')
        self.play(Indicate(VGroup(brace, short), color=FOCUS, scale_factor=1.06), run_time=0.8)

        # [V10.6c] four round trips, each amount snapping to the nearest cent both ways; QR q10-05
        self.at('Now convert some amounts')
        self.play(FadeOut(VGroup(axis, ends, end_labels, dot, dot_label, brace, short)), run_time=0.4)
        card_q = show_qr(self, 'q10-05')
        trips = []
        for dollars in ('0.03', '19.99', '1000.00', '5000.00'):     # the snippet's amounts
            usd = Decimal(dollars)
            exact_eur = usd * rate
            eur = exact_eur.quantize(CENT, ROUND_HALF_UP)
            exact_back = eur * inverse
            trips.append((usd, exact_eur, eur, exact_back, exact_back.quantize(CENT, ROUND_HALF_UP)))
        left = right = heads = None
        phrases = ['Now convert some amounts', 'Nineteen ninety-nine survives', 'A thousand dollars comes back',
                   'and five thousand comes back']
        exact_r, current = None, []
        for k, (usd, exact_eur, eur, exact_back, back_usd) in enumerate(trips):
            self.at(phrases[k])
            quick = 0.6 if k else 1.0
            new_left, new_right = cent_line(eur, '€', -4.2), cent_line(back_usd, '$', 0.9)
            new_heads = VGroup(Text(f'${usd} × {rate}', font=MONO, font_size=20, color=WHITE),
                               Text(f'€{eur} × {inverse}', font=MONO, font_size=20, color=WHITE))
            new_heads[0].next_to(new_left, DOWN, buff=0.2)
            new_heads[1].next_to(new_right, DOWN, buff=0.2)
            olds = [m for m in (left, right, heads) if m is not None]
            self.play(*[FadeOut(m) for m in olds + current], FadeIn(new_left), FadeIn(new_heads[0]), run_time=0.4 * quick)
            left, right, heads = new_left, new_right, new_heads
            d1 = left.line.diamond(exact_eur)
            e1 = MonoLine(str(exact_eur), font_size=18, color=FOCUS).next_to(d1, UP, buff=0.08)
            s1 = left.line.snap(exact_eur)
            self.play(FadeIn(d1, shift=DOWN * 0.3), FadeIn(e1), run_time=0.4 * quick)
            self.play(Create(s1), left.labels[1].animate.set_color(MONEY), run_time=0.5 * quick)
            self.play(FadeIn(right), FadeIn(heads[1]), run_time=0.4 * quick)
            d2 = right.line.diamond(exact_back)
            e2 = MonoLine(str(exact_back), font_size=18, color=FOCUS).next_to(d2, UP, buff=0.08)
            s2 = right.line.snap(exact_back)
            self.play(FadeIn(d2, shift=DOWN * 0.3), FadeIn(e2), run_time=0.4 * quick)
            change = back_usd - usd
            colour = EXACT if change > 0 else ERROR if change < 0 else WHITE
            self.play(Create(s2), right.labels[1].animate.set_color(colour), run_time=0.5 * quick)
            line = lines[k + 1]
            at = line.source.rindex(f'${back_usd}')         # the returned amount, after the second arrow
            line.chars(at, at + len(f'${back_usd}')).set_color(colour)
            line.part(f'change: {change}').set_color(colour)
            self.play(out.type_line(k + 1, run_time=0.7 * quick))
            current = [d1, e1, s1, d2, e2, s2]
            exact_r = e2
        self.at('Small amounts are dominated')
        self.play(Indicate(lines[1].part('change: 0.01'), color=EXACT), run_time=0.7)
        self.at('large amounts by the imprecise inverse rate')
        self.play(Indicate(inv_label, color=ERROR), Indicate(lines[4].part('change: -0.11'), color=ERROR), run_time=0.9)

        # Rounding throws information away: the extra digits fall off
        self.at('None of this is a bug')
        drop_qr(self, card_q)
        self.at('rounding throws information away')
        text = exact_r.source
        lost = exact_r.chars(text.index('.') + 3)
        self.play(lost.animate.set_color(ERROR), run_time=0.4)
        self.play(lost.animate.shift(DOWN * 0.8).set_opacity(0), run_time=0.9, rate_func=rate_functions.ease_in_quad)

        # [V10.6d] episode 6's euro changeover rule flashes up; store all three
        self.at('the euro changeover rules')
        self.play(FadeOut(VGroup(left, right, heads, *current)), run_time=0.4)
        rule = label_box('Euro changeover rule (episode 6): never use inverse rates', color=ERROR, font_size=26)
        rule.move_to([0, -2.5, 0])
        self.play(FadeIn(rule, scale=1.1), run_time=0.4)
        self.play(Indicate(rule, color=ERROR, scale_factor=1.05), run_time=0.8)
        self.at('store the original amount')
        self.play(FadeOut(rule), run_time=0.3)
        keep = VGroup(*[VGroup(checkmark(size=0.3), label_box(t, color=EXACT, font_size=24)).arrange(RIGHT, buff=0.15)
                        for t in ('original amount', 'rate', 'result')]).arrange(RIGHT, buff=0.6)
        keep.move_to([-0.3, -2.5, 0])
        self.play(LaggedStart(*[FadeIn(k, shift=UP * 0.2) for k in keep], lag_ratio=0.35), run_time=1.3)
        self.at('not just the result')
        only = VGroup(crossmark(size=0.28), Text('just the result', font_size=24, color=ERROR)).arrange(RIGHT, buff=0.15)
        only.next_to(keep, DOWN, buff=0.35)
        self.play(FadeIn(only, shift=UP * 0.2), run_time=0.5)
        self.finish()


# ---------------------------------------------------------------- 10.7

class Segment_10_7(Segment):
    """Floats sneaking back in."""
    EPISODE, SEGMENT = 10, '10.7'

    def construct(self):
        # [V10.7a] a clean pipeline, every box green
        def node(text):
            return label_box(text, color=EXACT, font_size=26, fill=EXACT)
        top = VGroup(*[node(t) for t in ('CSV file', 'data frame', 'service', 'JSON')])
        for box, x in zip(top, (-5.2, -1.75, 1.75, 5.2)):
            box.move_to([x, 1.3, 0])
        bottom = VGroup(*[node(t) for t in ('browser', 'spreadsheet export', 'database')])
        for box, x in zip(bottom, (4.6, 0.3, -4.4)):
            box.move_to([x, -1.5, 0])
        arrows = [Arrow(a.get_right(), b.get_left(), buff=0.12, color=SCAFFOLD, stroke_width=3) for a, b in zip(top[:-1], top[1:])]
        arrows.append(Arrow(top[3].get_bottom(), bottom[0].get_top(), buff=0.12, color=SCAFFOLD, stroke_width=3))
        arrows += [Arrow(a.get_left(), b.get_right(), buff=0.12, color=SCAFFOLD, stroke_width=3)
                   for a, b in zip(bottom[:-1], bottom[1:])]
        arrows = VGroup(*arrows)
        boxes = [*top, *bottom]
        title = Text('Where floats sneak back in', font_size=30, color=SCAFFOLD).to_edge(UP, buff=0.35)
        self.play(FadeIn(title), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(b, scale=0.9) for b in boxes], lag_ratio=0.15),
                  LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.15), run_time=2.0)

        def turn(box, colour):
            return [box[0].animate.set_stroke(colour, 2).set_fill(colour, 0.25)]

        def slip(chip, box, start):
            chip.move_to(start)
            self.play(FadeIn(chip, scale=0.7), run_time=0.4)
            self.play(chip.animate.move_to(box).scale(0.3).set_opacity(0), *turn(box, STORED), run_time=0.9)
            self.remove(chip)

        # [V10.7b] float tokens slip in at the joints; each box they enter turns blue
        self.at('where a data library takes one look')
        slip(token('float64', STORED, font_size=22), top[1], arrows[0].get_center() + UP * 0.75)
        self.at('where a parser does the same thing')
        raw = Text('"amount": 12.34', font=MONO, font_size=22, color=EXACT).move_to(top[3].get_top() + UP * 0.6 + LEFT * 0.4)
        self.play(FadeIn(raw), run_time=0.4)
        number_chip = token('12.34', STORED, font_size=22).move_to(raw)
        self.play(FadeTransform(raw, number_chip), run_time=0.6)
        self.play(number_chip.animate.move_to(top[3]).scale(0.3).set_opacity(0), *turn(top[3], STORED), run_time=0.9)
        self.remove(number_chip)
        self.at('Or from a browser')
        slip(token('double', STORED, font_size=22), bottom[0], arrows[3].get_center() + LEFT * 1.3)
        self.at('Or from a spreadsheet')
        slip(token('double', STORED, font_size=22), bottom[1], arrows[4].get_center() + DOWN * 0.95)
        self.at('Or from a database column')
        slip(token('FLOAT', STORED, font_size=22), bottom[2], arrows[5].get_center() + DOWN * 0.95)

        # Every joint is a boundary, and every boundary gets a guard
        self.at('Every one of those is a boundary')
        self.play(LaggedStart(*[Indicate(a, color=FOCUS, scale_factor=1.1) for a in arrows], lag_ratio=0.15), run_time=1.4)
        self.at('every one needs a guard')
        guards = VGroup()
        for a in arrows:
            direction = a.get_end() - a.get_start()
            gate = Rectangle(width=0.14, height=0.62).set_fill(EXACT, 1).set_stroke(width=0)
            gate.rotate(math.atan2(direction[1], direction[0])).move_to(a.get_center())
            guards.add(gate)
        self.play(LaggedStart(*[FadeIn(g, scale=1.6) for g in guards], lag_ratio=0.15), run_time=1.2)
        self.at('read amounts as strings')
        how = Text('read as strings or integer minor units; convert once, at the edge', font_size=24, color=EXACT)
        fit(how, 12.5).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(how, shift=UP * 0.2), run_time=0.6)
        self.at('convert them to your money type once')
        self.play(LaggedStart(*[AnimationGroup(*turn(b, EXACT)) for b in boxes], lag_ratio=0.12), run_time=1.4)
        self.at('reject anything that arrives as a float')
        bounce = token('float', STORED, font_size=20).move_to(guards[0].get_center() + LEFT * 0.0 + UP * 0.75)
        self.play(FadeIn(bounce), run_time=0.3)
        self.play(bounce.animate.move_to(guards[0].get_center() + UP * 0.3), run_time=0.4, rate_func=rate_functions.ease_in_quad)
        self.play(bounce.animate.shift(UP * 0.6).set_opacity(0), run_time=0.5)

        # [V10.7c] in the Python service, a red TypeError barrier stops a token: loud is good
        self.at('In Python, mixing a stray float')
        joint = guards[1]
        wall = barrier(1.0, label='TypeError', font_size=22).move_to(joint)
        wall[2].next_to(wall[0], UP, buff=0.1)
        self.play(FadeOut(joint), FadeIn(wall, shift=DOWN * 0.3), run_time=0.5)
        stray = Square(0.26).set_fill(STORED, 1).set_stroke(width=0).move_to(top[1].get_right() + RIGHT * 0.15)
        self.play(FadeIn(stray), run_time=0.2)
        self.play(stray.animate.next_to(wall[0], LEFT, buff=0.02), run_time=0.5, rate_func=rate_functions.ease_in_quad)
        self.play(stray.animate.shift(LEFT * 0.25), run_time=0.4, rate_func=rate_functions.ease_out_bounce)
        good = Text('loud failures are good failures', font_size=28, color=FOCUS).move_to([-1.2, -0.05, 0])
        self.play(Write(good), run_time=1.2)
        self.at('Make your boundaries just as unforgiving')
        walls = VGroup(*[g.copy().set_fill(ERROR, 1) for g in guards if g is not joint])
        self.play(*[Transform(g, w) for g, w in zip([g for g in guards if g is not joint], walls)], run_time=0.8)
        self.play(LaggedStart(*[Indicate(g, color=ERROR, scale_factor=1.4) for g in guards if g is not joint],
                              lag_ratio=0.1), run_time=1.2)
        self.finish()


# ---------------------------------------------------------------- 10.8

def chart_frame(x0, x1, y0, y1):
    return VGroup(Line([x0, y0, 0], [x1, y0, 0], color=GREY_D, stroke_width=2),
                  Line([x0, y0, 0], [x0, y1, 0], color=GREY_D, stroke_width=2))


class Segment_10_8(Segment):
    """When floats are fine."""
    EPISODE, SEGMENT = 10, '10.8'

    def construct(self):
        # Illustrative curves only: a seeded random walk, computed here (no figures are quoted).
        rng = random.Random(10)
        steps = 60

        def walk():
            price, path = 100.0, [100.0]
            for _ in range(steps):
                price *= math.exp(rng.gauss(0.0005, 0.012))
                path.append(price)
            return path
        paths = [walk() for _ in range(14)]
        finals = [walk()[-1] for _ in range(400)]
        model_value = sum(finals) / len(finals)            # a model's float output

        # [V10.8a] the split screen: measuring (blue) and counting (gold)
        divider = DashedLine(UP * 3.2, DOWN * 3.8, color=GREY_D)
        h_measure = Text('measuring', font_size=34, color=STORED).move_to([-3.6, 3.5, 0])
        h_count = Text('counting', font_size=34, color=MONEY).move_to([3.6, 3.5, 0])
        self.play(Create(divider), FadeIn(h_measure), FadeIn(h_count), run_time=0.9)

        # forecast with its uncertainty band
        self.at("A forecast of next year's revenue")
        fx0, fx1, fy0, fy1 = -6.5, -0.7, 1.3, 2.95
        f_axes = chart_frame(fx0, fx1, fy0, fy1)

        def fpt(t, v):
            return np.array([fx0 + 0.2 + (fx1 - fx0 - 0.4) * t, fy0 + 0.1 + (fy1 - fy0 - 0.2) * v, 0])
        ts = np.linspace(0, 1, 40)
        mid = [0.25 + 0.45 * t + 0.05 * math.sin(7 * t) for t in ts]
        spread = [0.03 + 0.22 * t for t in ts]
        band = Polygon(*[fpt(t, m + s) for t, m, s in zip(ts, mid, spread)],
                       *[fpt(t, m - s) for t, m, s in reversed(list(zip(ts, mid, spread)))])
        band.set_fill(STORED, 0.25).set_stroke(width=0)
        curve = VMobject(color=STORED, stroke_width=4).set_points_smoothly([fpt(t, m) for t, m in zip(ts, mid)])
        f_label = Text('forecast', font_size=20, color=SCAFFOLD).move_to([fx0 + 0.75, fy1 - 0.1, 0])
        self.play(Create(f_axes), FadeIn(f_label), run_time=0.4)
        self.play(Create(curve), FadeIn(band), run_time=1.2)

        # simulated price paths fanning out
        self.at('A simulation of ten thousand possible price paths')
        px0, px1, py0, py1 = -6.5, -0.7, -0.95, 0.95
        lo_p = min(min(p) for p in paths)
        hi_p = max(max(p) for p in paths)

        def ppt(i, v):
            return np.array([px0 + 0.2 + (px1 - px0 - 0.4) * i / steps,
                             py0 + 0.1 + (py1 - py0 - 0.2) * (v - lo_p) / (hi_p - lo_p), 0])
        sims = VGroup(*[VMobject(stroke_width=2).set_stroke(STORED, 2, 0.7).set_points_as_corners(
            [ppt(i, v) for i, v in enumerate(p)]) for p in paths])
        p_axes = chart_frame(px0, px1, py0, py1)
        p_label = Text('price paths', font_size=20, color=SCAFFOLD).move_to([px0 + 0.85, py1 - 0.05, 0])
        self.play(Create(p_axes), FadeIn(p_label), run_time=0.3)
        self.play(LaggedStart(*[Create(s) for s in sims], lag_ratio=0.12), run_time=2.0)

        # a risk histogram of where 400 simulated paths end
        self.at('A risk model')
        hx0, hx1, hy0, hy1 = -6.5, -0.7, -3.55, -1.35
        lo_f, hi_f, bins = min(finals), max(finals), 14
        counts = [0] * bins
        for f in finals:
            counts[min(int((f - lo_f) / (hi_f - lo_f) * bins), bins - 1)] += 1
        bar_w = (hx1 - hx0 - 0.4) / bins
        bars = VGroup(*[Rectangle(width=bar_w * 0.85, height=max(0.02, (hy1 - hy0 - 0.45) * c / max(counts)))
                        .set_fill(STORED, 0.8).set_stroke(width=0)
                        .move_to([hx0 + 0.2 + bar_w * (k + 0.5), hy0, 0], aligned_edge=DOWN)
                        for k, c in enumerate(counts)])
        h_axes = chart_frame(hx0, hx1, hy0, hy1)
        h_label = Text('risk', font_size=20, color=SCAFFOLD).move_to([hx0 + 0.4, hy1 - 0.05, 0])
        self.play(Create(h_axes), FadeIn(h_label), run_time=0.3)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.08), run_time=1.2)
        self.at('their tiny errors are dwarfed')
        self.play(band.animate.set_fill(STORED, 0.45), run_time=0.5)
        self.play(band.animate.set_fill(STORED, 0.25), run_time=0.5)

        # the ledger, the receipt and a stack of pennies
        self.at("It's floating point in a ledger")
        amounts = ['19.99', '0.03']                        # two of q10-05's amounts
        total = str(sum(Decimal(a) for a in amounts))
        book = ledger(amounts, [total], totals=(total, total), width=4.8, font_size=20)
        book.move_to([3.6, 1.2, 0]).align_to([0, 3.05, 0], UP)
        self.play(FadeIn(book), run_time=0.8)
        self.at('A ledger records what was actually paid')
        slip = receipt([('Item', amounts[0]), ('Item', amounts[1]), ('-', ''), ('Total', total)],
                       width=3.0, font_size=18, title='RECEIPT')
        slip.move_to([2.3, -2.45, 0])
        self.play(FadeIn(slip, shift=UP * 0.3), run_time=0.7)
        self.at('to the last cent')
        pile = VGroup(*[penny(0.36).shift(UP * 0.13 * k) for k in range(7)]).move_to([5.4, -2.4, 0])
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.4) for p in pile], lag_ratio=0.25), run_time=1.2)

        # [V10.8b] booking: a blue model value crosses the line, rounded once, into a gold amount
        self.at('So the boundary is the thing to design')
        self.play(FadeOut(VGroup(sims, p_axes, p_label, bars, h_axes, h_label, slip, pile, book)), run_time=0.6)
        forecast = VGroup(f_axes, f_label, curve, band)
        self.play(forecast.animate.move_to([-3.6, -2.2, 0]), run_time=0.8)
        value = Text(repr(model_value), font=MONO, font_size=26, color=STORED).move_to([-3.8, 0.5, 0])
        source = Text('model output', font_size=20, color=SCAFFOLD).next_to(value, UP, buff=0.15)
        posts = VGroup(*[Line(UP * 0.55, DOWN * 0.55, color=FOCUS, stroke_width=6).move_to([dx, 0.5, 0]) for dx in (-0.12, 0.12)])
        gate_label = Text('round once, with a rule', font_size=22, color=FOCUS).next_to(posts, DOWN, buff=0.15)
        gate_label = VGroup(BackgroundRectangle(gate_label, fill_opacity=1, buff=0.08), gate_label)
        self.play(FadeIn(value), FadeIn(source), FadeIn(posts), FadeIn(gate_label), run_time=0.7)
        self.at("When a model's output turns into a real booking")
        arrow = Arrow([-1.6, 1.25, 0], [1.6, 1.25, 0], buff=0, color=SCAFFOLD, stroke_width=3)
        booking = Text('booking', font_size=22, color=SCAFFOLD).next_to(arrow, UP, buff=0.08)
        self.play(GrowArrow(arrow), FadeIn(booking), run_time=0.6)
        rounded = Decimal(repr(model_value)).quantize(CENT, ROUND_HALF_UP)
        amount = Text(f'${rounded}', font=MONO, font_size=34, color=MONEY).move_to([3.6, 0.5, 0])
        moving = value.copy()
        self.play(moving.animate.move_to(posts).scale(0.5), run_time=0.8)
        self.play(ReplacementTransform(moving, amount), run_time=0.8)
        self.at('round once, with a written rule')
        self.play(Indicate(gate_label[1], color=FOCUS, scale_factor=1.08), run_time=0.7)
        self.at('into integer minor units or a decimal')
        entry = ledger([('Booked', str(rounded))], [], width=6.0, font_size=20, with_scale=False)
        entry.move_to([3.6, -2.0, 0])
        self.play(FadeIn(entry.frame), FadeIn(entry.headings), run_time=0.4)
        self.play(TransformFromCopy(amount, entry.left[0]), run_time=0.9)
        self.at('and never look back')
        self.play(Indicate(amount, color=MONEY, scale_factor=1.1), run_time=0.7)

        # [V10.8c] the sentence writes itself across the middle
        self.at('floats are for measuring')
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.4)
        line = Text('Floats are for measuring; money is counted.', font_size=46,
                    t2c={'measuring': STORED, 'counted': MONEY})
        fit(line, 12.6)
        self.play(Write(line), run_time=2.2)
        self.finish()


# ---------------------------------------------------------------- 10.9

def ring_tile(number_, content, words, width=2.7, height=2.1):
    """One tile of the series ring: a frame, its episode number, a motif and a caption."""
    frame = RoundedRectangle(width=width, height=height, corner_radius=0.12).set_stroke(GREY_D, 2).set_fill(BLACK, 0.8)
    badge = Text(str(number_), font_size=22, color=SCAFFOLD).move_to(frame.get_corner(UL) + RIGHT * 0.22 + DOWN * 0.2)
    words = Text(words, font_size=18, color=GREY_A).move_to(frame.get_bottom() + UP * 0.25)
    room_w, room_h = width * 0.8, height - 0.95
    content.scale_to_fit_height(room_h) if content.height / room_h > content.width / room_w else content.scale_to_fit_width(room_w)
    content.move_to(frame.get_center() + UP * 0.08)
    group = VGroup(frame, badge, words, content)
    group.content = content
    return group


def ring_slot(width=2.7, height=2.1):
    return DashedVMobject(RoundedRectangle(width=width, height=height, corner_radius=0.12).set_stroke(GREY_D, 2), num_dashes=40)


class Segment_10_9(Segment):
    """The whole series, in one breath."""
    EPISODE, SEGMENT = 10, '10.9'

    def construct(self):
        # [V10.9a] a ring of motifs, one per episode, around an empty centre
        spots = [(-4.65, 2.85), (-1.55, 2.85), (1.55, 2.85), (4.65, 2.85), (5.5, 0.0),
                 (3.1, -2.85), (0.0, -2.85), (-3.1, -2.85), (-5.5, 0.0)]
        slots = VGroup(*[ring_slot().move_to([x, y, 0]) for x, y in spots])
        self.play(LaggedStart(*[Create(s) for s in slots], lag_ratio=0.08), run_time=1.6)
        tiles = []

        def place(k, content, words):
            t = ring_tile(k, content, words).move_to(slots[k - 1])
            self.play(FadeOut(slots[k - 1]), FadeIn(t, scale=0.92), run_time=0.5)
            tiles.append(t)
            return t

        # 1 · the cent grid lights its four exact cells
        self.at('In episode one')
        grid = cent_grid(cell=0.3, font_size=7)
        place(1, grid, 'only 4 of 100 exact')
        self.at('only four of the hundred')
        self.play(*grid.light_exact(), run_time=0.8)

        # 2 · the float line: gaps grow with size (a toy float, two significant bits after the first)
        self.at('In episode two')
        toy = sorted({m / 4 * 2.0 ** e for e in range(-1, 2) for m in (4, 5, 6, 7)} | {4.0})
        fl = FloatLine(0.5, 4, width=4.4, ticks=toy, tick_height=0.5)
        fl.ticks.set_opacity(0)
        place(2, fl, 'gaps grow with size')
        self.at('gaps that grow with size')
        self.play(LaggedStart(*[t.animate.set_opacity(1) for t in fl.ticks], lag_ratio=0.2), run_time=1.2)

        # 3 · the risk map with its red hotspot
        self.at('Episode three mapped')
        axes = VGroup(Arrow(ORIGIN, RIGHT * 2.6, buff=0, color=SCAFFOLD, stroke_width=3),
                      Arrow(ORIGIN, UP * 1.8, buff=0, color=SCAFFOLD, stroke_width=3))
        hot = VGroup(*[Circle(radius=r).set_fill(ERROR, o).set_stroke(width=0) for r, o in ((0.5, 0.2), (0.32, 0.4), (0.16, 0.9))])
        hot.move_to(RIGHT * 1.9 + UP * 1.1)
        dots = VGroup(*[Dot(RIGHT * x + UP * y, radius=0.05, color=GREY_B) for x, y in ((0.5, 0.4), (1.0, 0.7), (0.7, 1.3), (1.4, 0.3))])
        risk = VGroup(axes, dots, hot)
        place(3, risk, 'where it bites')
        self.play(Indicate(hot, color=ERROR, scale_factor=1.3), run_time=0.7)

        # 4 · the ledger whose scale tips by a couple of cents (q10-05's $1000.00 -> $999.98)
        self.at('Episode four counted')
        book = ledger(['1000.00'], ['999.98'], width=4.0, font_size=20)
        place(4, book, 'what it costs')
        self.play(tip_scale(book.balance, 0.2), book.right[0].animate.set_color(ERROR), run_time=0.8)

        # 5 · language names, all printing the same digits (q05-02's output)
        self.at('Episode five showed')
        shared = output_line('ep05/02-four-costumes.py', 'shortest repr')
        found = re.match(r'shortest repr \(([^)]*)\):\s*(\S+)', shared)
        langs = VGroup()
        for name in found.group(1).split(', '):
            langs.add(VGroup(Text(name, font_size=26, color=SCAFFOLD), MonoLine(found.group(2), font_size=24, color=STORED)))
        for row in langs:
            row[1].next_to(row[0], RIGHT, buff=0.3)
        langs.arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        right_edge = max(r[0].get_right()[0] for r in langs)
        for row in langs:
            row[1].set_anchor([right_edge + 0.3, row[0].get_y(), 0])
        for row in langs:
            row[1].glyphs.set_opacity(0)
        place(5, langs, 'same answers')
        self.play(LaggedStart(*[r[1].glyphs.animate.set_opacity(1) for r in langs], lag_ratio=0.35), run_time=1.0)

        # 6 · a value between two neighbours, with eight rounding arrows
        self.at('Episode six made rounding')
        axis = Line(LEFT * 2, RIGHT * 2, color=SCAFFOLD, stroke_width=2)
        ends = VGroup(*[Line(DOWN * 0.15, UP * 0.15, color=SCAFFOLD, stroke_width=3).move_to(x * RIGHT) for x in (-1.6, 1.6)])
        point = Dot(RIGHT * 0.2, color=FOCUS, radius=0.09)
        colours = [STORED, EXACT, FOCUS, ERROR, MONEY, TEAL, PURPLE, GREY_B]
        fan = VGroup()
        for k in range(8):
            side = ends[k % 2].get_center()
            lift = (0.25 + 0.22 * (k // 2)) * (1 if k < 4 else -1)
            fan.add(Arrow(point.get_center() + UP * lift * 0.4, side + UP * lift, buff=0.05, color=colours[k],
                          stroke_width=3, max_tip_length_to_length_ratio=0.12))
        fan.set_opacity(0)
        rounding = VGroup(axis, ends, fan, point)
        place(6, rounding, 'round on purpose')
        self.play(LaggedStart(*[a.animate.set_opacity(1) for a in fan], lag_ratio=0.15), run_time=1.0)

        # 7 · the sliced penny, slivers dropping into a hidden jar
        self.at('Episode seven took')
        slices = sliced_penny(10, 0.7)
        hidden = jar(0.9, 0.8, color=GREY_D)
        seven = VGroup(slices, hidden).arrange(RIGHT, buff=0.5)
        place(7, seven, 'real fractions')
        self.play(LaggedStart(*[s.animate.move_to(hidden[0]).scale(0.2).set_opacity(0) for s in slices[:4]],
                              lag_ratio=0.3), run_time=1.0)

        # 8 · a bill splits into three stacks and one stray penny (q08-01's "each pays")
        self.at('Episode eight kept')
        each = output_line('ep08/01-three-ways.py', 'each pays').split('=')[1].strip()
        bill = RoundedRectangle(width=2.2, height=1.0, corner_radius=0.08).set_fill('#2f6b3a', 1).set_stroke(EXACT, 2)
        stacks = VGroup(*[VGroup(*[RoundedRectangle(width=0.7, height=0.14, corner_radius=0.03).set_fill('#2f6b3a', 1)
                                   .set_stroke(EXACT, 1).shift(UP * 0.1 * i) for i in range(5)]) for _ in range(3)])
        stacks.arrange(RIGHT, buff=0.3)
        tags = VGroup(*[Text(each, font_size=18, color=MONEY).next_to(s, DOWN, buff=0.08) for s in stacks])
        stray = penny(0.16).next_to(stacks, RIGHT, buff=0.25)
        split = VGroup(stacks, tags, stray)
        bill.move_to(stacks)
        placeholder = VGroup(bill, split.copy().set_opacity(0))
        t8 = place(8, placeholder, 'parts add up')
        split.match_height(t8.content[1]).move_to(t8.content[1])
        self.play(ReplacementTransform(bill, split[0]), FadeIn(split[1]), FadeIn(split[2], shift=RIGHT * 0.2), run_time=0.9)

        # 9 · the checklist ticks itself
        self.at('Episode nine wrote the checklist')
        items = VGroup(*[Text(t, font_size=22) for t in ('count in minor units', 'Decimal for rates', 'round on purpose')])
        items.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        boxes = VGroup(*[Square(0.28).set_stroke(SCAFFOLD, 2).next_to(i, LEFT, buff=0.2) for i in items])
        ticks = VGroup(*[checkmark(size=0.3).move_to(b) for b in boxes]).set_opacity(0)
        place(9, VGroup(items, boxes, ticks), 'the checklist')
        self.play(LaggedStart(*[t.animate.set_opacity(1) for t in ticks], lag_ratio=0.4), run_time=0.9)

        # [V10.9b] episode 10's motif, a cracked decimal under 1/3, slides into the centre
        self.at('And today')
        third = Text('1/3', font_size=48, color=FOCUS)
        sign = token('Decimal', STORED, font_size=40).next_to(third, DOWN, buff=0.35)
        label = Text('10 · when the fixes fail', font_size=24, color=SCAFFOLD).next_to(sign, DOWN, buff=0.35)
        centre = VGroup(third, sign, label).move_to(ORIGIN)
        centre.shift(DOWN * 6)
        self.play(centre.animate.shift(UP * 6), run_time=1.0)
        self.at('we watched each fix fail')
        crack = VMobject(color=ERROR, stroke_width=5).set_points_as_corners(
            [sign.get_top() + LEFT * 0.15, sign.get_center() + RIGHT * 0.25, sign.get_center() + LEFT * 0.15 + DOWN * 0.12,
             sign.get_bottom() + RIGHT * 0.1])
        self.play(Create(crack), *recolor_token(sign, ERROR), run_time=0.8)
        self.at('and learned what to watch for')
        self.play(*[t.animate.shift(-0.07 * np.array([t.get_x(), t.get_y(), 0])) for t in tiles], run_time=1.2)
        self.finish()


# ---------------------------------------------------------------- 10.10

class Segment_10_10(Segment):
    """Recap, challenge and farewell (q10-05, then the wall)."""
    EPISODE, SEGMENT = 10, '10.10'

    def construct(self):
        # [V10.10a] the recap column builds, one lesson per line
        heading = Text('This episode', font_size=28, color=SCAFFOLD).move_to([-1.0, 3.45, 0])
        self.play(FadeIn(heading), run_time=0.5)
        sign_bits = BitRow(8, cell=0.13, buff=0.015, sign_color=ERROR).show(0b01111111)
        icons = [token('"0.1"', EXACT, font_size=22), Text('1/3', font_size=30, color=FOCUS), sign_bits,
                 token('JPY 0', MONEY, font_size=20),
                 VGroup(coin('$', 0.22), Text('⇄', font_size=26, color=MONEY), coin('€', 0.22)).arrange(RIGHT, buff=0.08),
                 barrier(0.6)]
        lessons = ['Decimal from strings, not floats', 'Decimals still round: choose where',
                   'Integers overflow, and units get mixed up', 'Minor units come from the currency',
                   "Conversions don't undo", 'Guard every boundary']
        phrases = ['Build decimals from strings', 'Remember that decimals still round', 'Integer cents can overflow',
                   'The size of the smallest unit', "Conversions can't be undone", 'And floats will try to sneak']
        rows = VGroup()
        for k, (icon, words, phrase) in enumerate(zip(icons, lessons, phrases)):
            y = 2.55 - 1.0 * k
            icon.move_to([-4.9, y, 0])
            text = Text(words, font_size=30).move_to([0, y, 0]).align_to([-3.8, 0, 0], LEFT)
            self.at(phrase)
            self.play(FadeIn(icon, scale=0.6), FadeIn(text, shift=LEFT * 0.4), run_time=0.7)
            if icon is sign_bits:
                sign_bits.show(0b10000000)
                self.play(Indicate(sign_bits.cells[0], color=ERROR, scale_factor=1.5), run_time=0.5)
            rows.add(VGroup(icon, text))

        # [V10.10b] the q10-05 code returns, its challenge comment highlighted; QR q10-05
        self.at("Here's a final challenge")
        self.play(FadeOut(VGroup(heading, rows)), run_time=0.6)
        code = code_panel(snippet_find(TRIP, '# Money Problems', '# Convert', '# Try other', 'rate = Decimal', 'inverse = (1'),
                          font_size=20).to_corner(UL, buff=0.4)
        mark = line_highlight(code, 2)
        self.play(FadeIn(code, shift=DOWN * 0.2), run_time=0.6)
        card_q = show_qr(self, 'q10-05')
        self.play(Create(mark), run_time=0.6)
        loop_y = -2.2
        a, b = coin('$', 0.5).move_to([-4.8, loop_y, 0]), coin('€', 0.5).move_to([-0.8, loop_y, 0])
        go = CurvedArrow(a.get_top() + UP * 0.1, b.get_top() + UP * 0.1, angle=-PI / 3, color=MONEY)
        come = CurvedArrow(b.get_bottom() + DOWN * 0.1, a.get_bottom() + DOWN * 0.1, angle=-PI / 3, color=MONEY)
        self.play(FadeIn(a), FadeIn(b), Create(go), Create(come), run_time=0.8)
        self.at('Change the rate')
        self.play(Transform(mark, line_highlight(code, 3)), run_time=0.5)
        runner = Dot(go.get_start(), radius=0.1, color=FOCUS)
        self.add(runner)
        self.play(MoveAlongPath(runner, go), run_time=1.0, rate_func=linear)
        self.play(MoveAlongPath(runner, come), run_time=1.0, rate_func=linear)
        self.at('Can you find a rate')
        self.play(Transform(mark, line_highlight(code, 2)), MoveAlongPath(runner, go), run_time=1.0, rate_func=linear)
        self.play(MoveAlongPath(runner, come), run_time=1.0, rate_func=linear)
        self.at("can you say why not?")
        question = Text('?', font_size=72, color=FOCUS).move_to([-2.8, loop_y, 0])
        self.play(FadeIn(question, scale=0.5), FadeOut(runner), run_time=0.6)

        # [V10.10c] the QR wall: q10-01 to q10-05, held for at least 10 seconds
        self.at("That's the end of Money Problems")
        drop_qr(self, card_q, seconds=10)
        self.play(FadeOut(VGroup(code, mark, a, b, go, come, question)), run_time=0.5)
        wall = qr_wall(episode_qr_ids(10))
        self.play(FadeIn(wall), run_time=0.8)
        wall_from = self.renderer.time

        # [V10.10d] the gold dime from episode 1 returns, filling in as Decimal("0.10") types beneath
        self.at('Thanks for watching')
        if self.renderer.time - wall_from < 10:
            self.wait(10 - (self.renderer.time - wall_from))
        self.play(FadeOut(wall), run_time=0.6)
        outline = DashedVMobject(Circle(radius=1.1, color=MONEY, stroke_width=4), num_dashes=36).move_to(UP * 0.7)
        dime = coin('10¢', 1.1).move_to(outline)
        text = code_text('Decimal("0.10")', font_size=40, color=EXACT).next_to(dime, DOWN, buff=0.6)
        self.play(FadeIn(outline), run_time=0.6)
        self.play(FadeIn(dime, scale=0.85), FadeOut(outline),
                  LaggedStart(*[FadeIn(g, run_time=0.08) for g in text.glyphs], lag_ratio=1.0), run_time=1.8)
        self.finish()
        self.play(FadeOut(VGroup(dime, text)), run_time=0.8)

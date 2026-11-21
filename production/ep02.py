"""Episode 2 · Inside a double. One Scene per script segment.

    python3 production/render.py 2 [-ql] [segment ...]

Shot ids in comments ([V2.1a] ...) refer to episodes/02-inside-a-double.md. Code and console
text come from the q02-01 ... q02-05 snippets and their recorded output; values that no snippet
prints (bit patterns of window amounts, float32 neighbours, running totals) are computed here
with Python and marked as such.
"""
import math
import random
import struct
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa: E402,F403

BITS = 'ep02/01-bits-of-a-double.py'
GAPS = 'ep02/02-gaps-between-doubles.py'
PRICES = 'ep02/03-house-price-32-bits.py'
PRINTS = 'ep02/04-what-print-hides.py'
CHALLENGE = 'ep02/05-challenge-cent-disappears.py'
EP01_SUM = 'ep01/01-ten-plus-twenty.py'
EP03_CENTS = 'ep03/01-a-cent-a-million-times.py'


# ---------------------------------------------------------------- local helpers

def rich(parts, font_size=36, color=WHITE):
    """A line of Text pieces with superscripts, without TeX. Each part is a string, a
    (text, colour) pair, or ('^', text, colour) for a raised, smaller exponent."""
    pieces, kinds = VGroup(), []
    for part in parts:
        if isinstance(part, str):
            part = (part, None)
        if part[0] == '^':
            pieces.add(Text(part[1], font_size=font_size * 0.6, color=(part[2] if len(part) > 2 else None) or color))
            kinds.append('^')
        else:
            pieces.add(Text(part[0].strip(), font_size=font_size, color=part[1] or color))
            kinds.append(part[0])
    ref = Text('0', font_size=font_size)
    x = 0.0
    for piece, kind in zip(pieces, kinds):
        gap = 0.04 if kind == '^' else (0.16 * font_size / 36 if kind.startswith(' ') else 0.05)
        piece.move_to([x + gap + piece.width / 2, 0, 0])
        if kind == '^':
            piece.align_to([0, ref.height * 0.45, 0], DOWN)
        else:
            piece.align_to([0, -ref.height / 2, 0], DOWN)
        x = piece.get_right()[0] + (0.16 * font_size / 36 if kind != '^' and kind.endswith(' ') else 0)
    pieces.center()
    return pieces


def house(width=2.4, color=GREY_A):
    body = Rectangle(width=width, height=width * 0.68).set_stroke(color, 4)
    roof = Polygon(body.get_corner(UL) + LEFT * 0.25, body.get_corner(UR) + RIGHT * 0.25,
                   body.get_top() + UP * width * 0.42).set_stroke(color, 4)
    door = Rectangle(width=width * 0.2, height=width * 0.36).set_stroke(color, 3)
    door.align_to(body, DOWN).shift(LEFT * width * 0.2)
    window = Square(width * 0.2).set_stroke(color, 3).move_to(body).shift(RIGHT * width * 0.22 + UP * width * 0.04)
    return VGroup(body, roof, door, window)


def price_pair(needle):
    """(typed, stored) price strings from a q02-03 output line, e.g. ('131,072.01', '131,072.015625')."""
    typed, stored = output_line(PRICES, needle).split('stored as')
    return typed.replace('$', '').strip(), stored.strip()


def common_prefix(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return a[:n]


def spaced_console(lines, font_size=18, pitch=0.6, **kwargs):
    """A Console whose rows are `pitch` apart (room for a ruler segment beside each row)."""
    con = Console(lines, font_size=font_size, **kwargs)
    top_left = con.background.get_corner(UL)
    first = con.lines[0].anchor()
    for i, line in enumerate(con.lines):
        line.set_anchor(first + DOWN * pitch * i)
    height = pitch * (len(lines) - 1) + con.lines[0].line_height + 0.5
    con.background.stretch_to_fit_height(height)
    con.background.move_to(top_left, aligned_edge=UL)
    return con


def bit_boxes(n, cell):
    boxes = VGroup(*[Square(cell * 0.86).set_stroke(GREY_B, 1.5) for _ in range(n)])
    return boxes.arrange(RIGHT, buff=cell * 0.14)


def split_boxes(boxes, sizes, gap):
    """A copy of a row of boxes with a gap between the groups, centred where the row was."""
    target = boxes.copy()
    start = 0
    for k, size in enumerate(sizes):
        VGroup(*target[start:start + size]).shift(RIGHT * gap * k)
        start += size
    return target.move_to(boxes)


def groups_of(boxes, sizes):
    out, start = [], 0
    for size in sizes:
        out.append(VGroup(*boxes[start:start + size]))
        start += size
    return out


def colour_group(group, color, opacity=0.25):
    return group.animate.set_stroke(color, 2).set_fill(color, opacity)


def bit_texts(bits, boxes, font_size=18, color=WHITE):
    return VGroup(*[Text(b, font=MONO, font_size=font_size, color=color).move_to(box)
                    for b, box in zip(bits, boxes)])


def digit_slots(n, width=0.52, height=0.7, buff=0.08):
    return VGroup(*[RoundedRectangle(width=width, height=height, corner_radius=0.06).set_stroke(GREY_B, 2)
                    for _ in range(n)]).arrange(RIGHT, buff=buff)


def fill_slots(slots, gold, blue, red=0):
    """Animations colouring the first `gold` slots MONEY (dollar digits), the next `blue`
    STORED (digits after the point), the next `red` ERROR, and the rest empty."""
    anims = []
    for i, slot in enumerate(slots):
        if i < gold:
            color, opacity = MONEY, 0.75
        elif i < gold + blue:
            color, opacity = STORED, 0.6
        elif i < gold + blue + red:
            color, opacity = ERROR, 0.6
        else:
            color, opacity = GREY_B, 0.0
        anims.append(slot.animate.set_fill(color, opacity).set_stroke(color, 2))
    return anims


def stamp(text, color=ERROR, font_size=30):
    label = Text(text, font=MONO, font_size=font_size, color=color, weight=BOLD)
    box = SurroundingRectangle(label, buff=0.2, color=color, stroke_width=5, corner_radius=0.08)
    return VGroup(box, label).rotate(8 * DEGREES)


def tumble(mob, shift, turns=3, run_time=1.4):
    return AnimationGroup(Rotate(mob, -turns * PI), mob.animate.shift(shift).set_opacity(0),
                          run_time=run_time, rate_func=rate_functions.ease_in_quad)


def snap_to(line, value, target, color=FOCUS, angle=-PI / 3):
    """Arrow from a true value (above the line) to a chosen tick: for ties, where
    FloatLine.snap would pick the first neighbour rather than the even one."""
    start = line.point(value) + UP * 0.32
    end = line.point(target) + UP * 0.2
    return CurvedArrow(start, end, color=color, angle=angle, stroke_width=3, tip_length=0.15)


def cent_arc(line, start, cents=1, label=True):
    """GOLD '+1¢' arc from a tick to the true sum, above the line."""
    a = line.point(start) + UP * 0.28
    b = line.point(Fraction(start) + Fraction(cents, 100)) + UP * 0.62
    arc = CurvedArrow(a, b, angle=-PI / 2, color=MONEY, stroke_width=4, tip_length=0.18)
    if not label:
        return VGroup(arc)
    text = Text(f'+{cents}¢', font_size=24, color=MONEY).next_to(arc, UP, buff=0.08)
    return VGroup(arc, text)


def gpu_icon():
    board = RoundedRectangle(width=1.6, height=0.9, corner_radius=0.08).set_stroke(GREY_A, 3).set_fill(GREY_E, 1)
    fans = VGroup(*[Circle(radius=0.28).set_stroke(GREY_A, 2) for _ in range(2)]).arrange(RIGHT, buff=0.2).move_to(board)
    blades = VGroup(*[Line(f.get_center() + UP * 0.22, f.get_center() + DOWN * 0.22, color=GREY_B).rotate(a)
                      for f in fans for a in (0, PI / 3, 2 * PI / 3)])
    pins = VGroup(*[Rectangle(width=0.08, height=0.14).set_fill(MONEY, 1).set_stroke(width=0) for _ in range(9)])
    pins.arrange(RIGHT, buff=0.06).next_to(board, DOWN, buff=0.0)
    return VGroup(board, fans, blades, pins)


def database_icon():
    w, h = 1.2, 1.0
    top = Ellipse(width=w, height=0.32).set_stroke(GREY_A, 3).set_fill(GREY_E, 1).shift(UP * h / 2)
    sides = VGroup(Line(LEFT * w / 2 + UP * h / 2, LEFT * w / 2 + DOWN * h / 2),
                   Line(RIGHT * w / 2 + UP * h / 2, RIGHT * w / 2 + DOWN * h / 2)).set_stroke(GREY_A, 3)
    rings = VGroup(*[Arc(radius=1, start_angle=PI, angle=PI).stretch_to_fit_width(w).stretch_to_fit_height(0.16)
                     .move_to(DOWN * y + DOWN * 0.08).set_stroke(GREY_A, 3) for y in (h / 2, 0, -h / 6)])
    rings[2].set_opacity(0)
    return VGroup(sides, rings[:2], top)


def file_icon():
    w, h, fold = 1.0, 1.3, 0.3
    body = Polygon([-w / 2, h / 2, 0], [w / 2 - fold, h / 2, 0], [w / 2, h / 2 - fold, 0], [w / 2, -h / 2, 0],
                   [-w / 2, -h / 2, 0]).set_stroke(GREY_A, 3).set_fill(GREY_E, 1)
    corner = VMobject().set_points_as_corners([[w / 2 - fold, h / 2, 0], [w / 2 - fold, h / 2 - fold, 0],
                                              [w / 2, h / 2 - fold, 0]]).set_stroke(GREY_A, 3)
    rows = VGroup(*[Line(LEFT * 0.3, RIGHT * 0.3, color=GREY_B, stroke_width=3).shift(DOWN * 0.18 * k)
                    for k in range(4)]).move_to(body).shift(DOWN * 0.12)
    return VGroup(body, corner, rows)


def coin_stack():
    discs = VGroup()
    dark = interpolate_color(ManimColor(MONEY), BLACK, 0.35)
    for k in range(3):
        disc = Ellipse(width=1.2, height=0.42).set_fill(MONEY, 1).set_stroke(dark, 3).shift(UP * 0.2 * k)
        discs.add(disc)
    return discs.move_to(ORIGIN)


def float32(x):
    """Round a Python float to the nearest 32-bit float (as q02-03 does)."""
    return struct.unpack('f', struct.pack('f', x))[0]


def float32_neighbours(lo, hi):
    """Every 32-bit float from lo to hi (computed here with numpy, for the float line)."""
    x = np.float32(float(lo))
    if Fraction(float(x)) < Fraction(lo):
        x = np.nextafter(x, np.float32(np.inf))
    out = []
    while Fraction(float(x)) <= Fraction(hi):
        out.append(float(x))
        x = np.nextafter(x, np.float32(np.inf))
    return out


def last_bit(x):
    return struct.unpack('>Q', struct.pack('>d', x))[0] & 1


# ---------------------------------------------------------------- 2.1

class Segment_2_1(Segment):
    """Cold open: a house price in a 32-bit float (q02-03's output)."""
    EPISODE, SEGMENT = 2, '2.1'

    def construct(self):
        typed1, stored1 = price_pair('131,072.01')
        typed2, stored2 = price_pair('1,000,000.01')

        # [V2.1a] a house with its price tag
        home = house(2.3).move_to(LEFT * 4.8 + UP * 1.4)
        tag1 = price_tag('$' + typed1).next_to(home, DOWN, buff=0.45)
        string = Line(home.get_bottom(), tag1[1].get_center(), color=GREY_B, stroke_width=2)
        self.play(Create(home), run_time=1.4)
        self.play(Create(string), FadeIn(tag1, shift=DOWN * 0.3))

        # [V2.1b] the tag goes through a narrow "32-bit float" box
        self.at('Store that price')
        box = Rectangle(width=1.3, height=2.0).set_stroke(STORED, 4).set_fill(STORED, 0.1).move_to(LEFT * 0.6 + UP * 0.2)
        box_label = Text('32-bit float', font_size=26, color=STORED).next_to(box, UP, buff=0.2)
        self.play(Create(box), FadeIn(box_label, shift=DOWN * 0.2))
        self.play(FadeOut(string), tag1.animate.move_to(box).scale(0.25).set_opacity(0), run_time=1.2)
        self.remove(tag1)
        for _ in range(2):        # the box squeezes the price into 32 bits
            self.play(box.animate.set_fill(STORED, 0.4).stretch(0.9, 0), rate_func=there_and_back, run_time=1.0)
        self.at('read it back')
        out1 = price_tag('$' + stored1, color=STORED)
        out1.next_to(box, RIGHT, buff=0.5)
        start1 = out1.copy().scale(0.25).move_to(box).set_opacity(0)
        self.play(Transform(start1, out1), run_time=1.0)
        self.remove(start1)
        self.add(out1)
        keep1 = len(common_prefix(typed1, stored1))
        extra1 = out1[2][1 + keep1:]                  # the digits past the typed price ("5625")
        self.at('You get the same dollars')
        self.play(extra1.animate.set_color(ERROR).scale(1.35), run_time=0.5)
        self.play(extra1.animate.scale(1 / 1.35), run_time=0.4)

        # [V2.1c] a million dollars and one cent: the cent tumbles off as a coin
        self.at('Try a million dollars')
        self.play(FadeOut(home), out1.animate.scale(0.8).move_to(RIGHT * 3.6 + UP * 2.9), run_time=0.8)
        tag2 = price_tag('$' + typed2).move_to(LEFT * 4.6 + UP * 0.2)
        self.play(FadeIn(tag2, shift=RIGHT * 0.5), run_time=0.6)
        self.play(tag2.animate.move_to(box).scale(0.25).set_opacity(0), run_time=1.0)
        self.remove(tag2)
        out2 = price_tag('$' + stored2, color=STORED).next_to(box, RIGHT, buff=0.5)
        start2 = out2.copy().scale(0.25).move_to(box).set_opacity(0)
        lost = penny(0.26).next_to(out2, RIGHT, buff=0.1)
        self.play(Transform(start2, out2), FadeIn(lost), run_time=1.0)
        self.remove(start2)
        self.add(out2)
        self.at('The cent is simply gone')
        self.play(tumble(lost, DOWN * 3.2 + RIGHT * 1.2, turns=4, run_time=1.4))
        self.remove(lost)

        # [V2.1d] the console shows both q02-03 lines; the two red details pulse
        out = output_console(PRICES, ['131,072.01', '1,000,000.01'], font_size=24).move_to(DOWN * 2.35)
        self.play(FadeIn(out.background), run_time=0.4)
        self.play(out.type_line(0, run_time=0.9))
        self.play(out.type_line(1, run_time=0.9))
        line0, line1 = out.lines
        start = line0.source.index(stored1) + keep1
        red0 = line0.chars(start, line0.source.index(stored1) + len(stored1))
        cent = line1.source.index(typed2) + len(typed2) - 1
        red1 = line1.chars(cent, cent + 1)         # the typed cent that never arrives
        self.play(red0.animate.set_color(ERROR), red1.animate.set_color(ERROR), run_time=0.4)
        for _ in range(2):
            self.play(red0.animate.scale(1.4), red1.animate.scale(1.6), run_time=0.35)
            self.play(red0.animate.scale(1 / 1.4), red1.animate.scale(1 / 1.6), run_time=0.35)

        # "Close" depends on how big the number is: a comb of ticks that spreads to the right
        self.at('In the last episode')
        self.play(FadeOut(VGroup(box, box_label, out1, out2)), out.animate.scale(0.8).to_edge(UP, buff=0.4))
        y = -0.6
        stretch = ValueTracker(0.0)

        def positions():
            xs, x = [], -6.2
            while x <= 6.2:
                xs.append(x)
                x += 0.12 * 2 ** (stretch.get_value() * (x + 6.2) * 0.62)
            return xs

        axis = Line(LEFT * 6.4 + UP * y, RIGHT * 6.4 + UP * y, color=SCAFFOLD, stroke_width=2)
        comb = always_redraw(lambda: VGroup(*[Line(UP * (y - 0.2) + RIGHT * x, UP * (y + 0.2) + RIGHT * x,
                                                   color=STORED, stroke_width=2.5) for x in positions()]))
        self.play(Create(axis), FadeIn(comb), run_time=0.8)
        dime_x = -5.0 + 0.05
        diamond = Square(0.2).rotate(PI / 4).set_fill(FOCUS, 1).set_stroke(width=0).move_to([dime_x, y + 0.5, 0])
        dime = Text('10¢', font_size=26, color=FOCUS).next_to(diamond, UP, buff=0.12)
        self.at('wonderfully close')
        self.play(FadeIn(diamond, shift=DOWN * 0.2), FadeIn(dime))
        near = min(positions(), key=lambda x: abs(x - dime_x))
        hop = Arrow(diamond.get_bottom(), [near, y + 0.22, 0], buff=0.02, color=FOCUS, stroke_width=3,
                    max_tip_length_to_length_ratio=0.5)
        self.play(GrowArrow(hop), run_time=0.5)
        self.at('depends on how big')
        small = Text('small amounts', font_size=24, color=SCAFFOLD).move_to([-4.6, y - 0.75, 0])
        big = Text('big amounts', font_size=24, color=SCAFFOLD).move_to([4.6, y - 0.75, 0])
        self.play(FadeOut(VGroup(diamond, dime, hop)), FadeIn(small), FadeIn(big))
        self.at('The bigger the amount')
        self.play(stretch.animate.set_value(1.0), run_time=3.0)
        comb.clear_updaters()
        self.at('no room left for the cents')
        ticks = positions()
        dots = VGroup()
        for k in range(42):
            x = -6.15 + 0.3 * k
            d = Dot([x, y - 0.32, 0], radius=0.045, color=MONEY)
            right = min([t for t in ticks if t >= x] or [6.4])
            left = max([t for t in ticks if t <= x] or [-6.4])
            d.lonely = right - left > 0.6          # several cents share one gap between ticks
            dots.add(d)
        lonely = VGroup(*[d for d in dots if d.lonely])
        small.generate_target().shift(DOWN * 0.15)
        big.generate_target().shift(DOWN * 0.15)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.03), MoveToTarget(small),
                  MoveToTarget(big), run_time=1.4)
        self.play(lonely.animate.set_color(ERROR), run_time=0.5)
        self.play(LaggedStart(*[d.animate.shift(DOWN * 1.2).set_opacity(0) for d in lonely], lag_ratio=0.05),
                  run_time=1.2)

        # Open up a floating-point number
        self.at('To understand why')
        self.play(FadeOut(VGroup(axis, comb, dots, small, big, out)), run_time=0.6)
        crate = Rectangle(width=6.0, height=1.5).set_stroke(STORED, 4).set_fill(STORED, 0.08).shift(DOWN * 0.8)
        name = Text('a floating-point number', font_size=32).move_to(crate)
        lid = Rectangle(width=6.3, height=0.24).set_stroke(STORED, 4).set_fill(STORED, 0.3).next_to(crate, UP, buff=0)
        self.play(FadeIn(crate), FadeIn(lid), Write(name), run_time=1.0)
        self.play(lid.animate.rotate(-0.35).shift(UP * 0.9 + RIGHT * 4.2).set_opacity(0), run_time=0.8)
        inside = bit_boxes(64, 0.19).move_to(UP * 1.8)
        sign, exponent, fraction = groups_of(inside, (1, 11, 52))
        sign.set_stroke(GREY_B, 2)
        exponent.set_stroke(FOCUS, 2)
        fraction.set_stroke(STORED, 2)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 1.0, target_position=crate.get_center()) for b in inside],
                              lag_ratio=0.02), run_time=1.6)
        self.finish()


# ---------------------------------------------------------------- 2.2

def sci(significand, base, exponent, font_size=56, sig_color=STORED, exp_color=FOCUS):
    return rich([(significand, sig_color), (' × ' + base, WHITE), ('^', exponent, exp_color)], font_size=font_size)


class Segment_2_2(Segment):
    """Scientific notation, in binary (q02-01)."""
    EPISODE, SEGMENT = 2, '2.2'

    def construct(self):
        # [V2.2a] decimal scientific notation, labelled
        big = sci('6.02', '10', '23')
        tiny = sci('1.6', '10', '−4')
        pair = VGroup(big, tiny).arrange(RIGHT, buff=2.2).move_to(UP * 2.3)
        self.play(FadeIn(big, shift=UP * 0.2), FadeIn(tiny, shift=UP * 0.2))
        self.at('a few significant digits')
        sig_label = Text('significand', font_size=26, color=STORED).next_to(big[0], DOWN, buff=0.3)
        exp_label = Text('exponent', font_size=26, color=FOCUS).next_to(big[2], UP, buff=0.2)
        self.play(FadeIn(sig_label, shift=UP * 0.2), Indicate(big[0], color=STORED, scale_factor=1.15))
        self.play(FadeIn(exp_label, shift=DOWN * 0.2), Indicate(big[2], color=FOCUS, scale_factor=1.3))

        # The decimal point slides as the exponent changes
        self.at('The power says where the decimal point goes')
        digits_src = '000602000'
        digits = VGroup(*[Text(d, font=MONO, font_size=48, color=STORED if 3 <= i <= 5 else GREY_B)
                          for i, d in enumerate(digits_src)]).arrange(RIGHT, buff=0.32).move_to(DOWN * 0.9 + LEFT * 2.2)
        pos = ValueTracker(3.0)        # the point sits after digit 3: 6.02 × 10^0

        def boundary(i):
            i = min(max(i, 0), len(digits) - 2)
            return (digits[i].get_right()[0] + digits[i + 1].get_left()[0]) / 2

        def point_x():
            v = pos.get_value()
            i = math.floor(v)
            return interpolate(boundary(i), boundary(i + 1), v - i)

        dot = always_redraw(lambda: Dot([point_x(), digits.get_bottom()[1] + 0.06, 0], radius=0.09, color=FOCUS))
        readout = rich([('= 6.02 × 10', WHITE)], font_size=40).next_to(digits, RIGHT, buff=0.6)
        power = number(0, font_size=28, color=FOCUS)
        power.add_updater(lambda m: m.set_value(round(pos.get_value()) - 3).next_to(readout, UR, buff=0.04)
                          .shift(DOWN * 0.18))
        self.play(FadeIn(digits), FadeIn(dot), FadeIn(readout), FadeIn(power))
        self.at('Slide the point left or right')
        self.play(pos.animate.set_value(7.0), run_time=1.6)
        self.play(pos.animate.set_value(0.0), run_time=2.0)
        self.play(pos.animate.set_value(3.0), run_time=1.2)

        # [V2.2b] the same idea in binary
        self.at('A double does exactly that with twos')
        binary = sci('1.1001100…', '2', '−4').move_to(UP * 0.4)
        sig_b = Text('significand', font_size=26, color=STORED).next_to(binary[0], DOWN, buff=0.3)
        exp_b = Text('exponent', font_size=26, color=FOCUS).next_to(binary[2], UP, buff=0.2)
        power.clear_updaters()
        self.play(FadeOut(VGroup(pair, sig_label, exp_label, digits, readout, power)), FadeOut(dot),
                  FadeIn(binary, shift=UP * 0.3), FadeIn(sig_b), FadeIn(exp_b))

        # [V2.2c] 64 boxes split into sign, exponent and fraction
        self.at("It's sixty-four bits")
        cell = 0.19
        strip = bit_boxes(64, cell).move_to(UP * 3.25)
        label64 = Text('64 bits', font_size=24, color=SCAFFOLD).next_to(strip, DOWN, buff=0.15)
        self.play(LaggedStart(*[FadeIn(b, scale=0.5) for b in strip], lag_ratio=0.02), FadeIn(label64), run_time=1.5)
        sizes = (1, 11, 52)
        self.at('One bit for the sign')
        self.play(Transform(strip, split_boxes(strip, sizes, 0.34)), FadeOut(label64))
        sign, exponent, fraction = groups_of(strip, sizes)
        sign_label = Text('sign', font_size=22, color=GREY_B).next_to(sign, UP, buff=0.1)
        self.play(colour_group(sign, GREY_B, 0.3), FadeIn(sign_label))
        self.at('Eleven bits for the exponent')
        exp_label = Text('exponent · 11', font_size=22, color=FOCUS).next_to(exponent, UP, buff=0.1)
        self.play(colour_group(exponent, FOCUS, 0.15), FadeIn(exp_label))
        self.at('And fifty-two bits for the fraction')
        frac_label = Text('fraction · 52', font_size=22, color=STORED).next_to(fraction, UP, buff=0.1)
        self.play(colour_group(fraction, STORED, 0.15), FadeIn(frac_label))

        # [V2.2d] code panel q02-01; the console prints 0.1; the bits fill the strip
        self.at("Let's look at zero point one")
        code = code_panel(snippet_lines(BITS, 5, 7), font_size=18).to_edge(LEFT, buff=0.45).set_y(1.45)
        cons = output_console(BITS, font_size=18)
        top3 = Console([l.source for l in cons.lines[:3]], font_size=18)
        top3.to_edge(LEFT, buff=0.45).align_to(UP * 0.45, UP)
        quarter = Console([l.source for l in cons.lines[3:]], font_size=18).move_to(top3)
        card = qr_card('q02-01')
        self.play(FadeOut(VGroup(binary, sig_b, exp_b)), FadeIn(code), FadeIn(top3.background),
                  FadeIn(card, shift=UP * 0.2))
        self.play(top3.type_line(0, run_time=1.2))
        words1 = top3.lines[1].source.split()
        sign_bits, exp_bits = words1[1], words1[3]
        frac_bits = top3.lines[2].source.split()[1]
        self.play(top3.type_line(1, run_time=1.0))
        self.play(top3.type_line(2, run_time=1.4))
        bits = bit_texts(sign_bits + exp_bits + frac_bits, strip)
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.15) for b in bits], lag_ratio=0.02), run_time=1.6)

        # The exponent bits morph into 1019 − 1023 = −4 (values computed from the printed bits)
        self.at('read as a number')
        biased = int(exp_bits, 2)
        sum_text = Text(f'{biased} − 1023 = {biased - 1023:+d}'.replace('-', '−').replace('+', ''),
                        font_size=34, color=FOCUS)
        sum_text.to_edge(LEFT, buff=0.6).set_y(-1.7)
        glyphs = sum_text[:len(str(biased))]
        source = top3.lines[1].part(exp_bits).copy()
        self.play(ReplacementTransform(source, glyphs), run_time=1.2)
        self.at('offset of one thousand and twenty-three')
        offset = sum_text[len(str(biased)):len(str(biased)) + 5]
        self.play(FadeIn(offset, shift=LEFT * 0.2))
        self.at('so the real exponent')
        self.play(FadeIn(sum_text[len(str(biased)) + 5:], shift=LEFT * 0.2))

        # One, zero, zero, one, repeating
        self.at('our old friend')
        unders = VGroup()
        for g in range(13):
            seg = VGroup(*fraction[4 * g:4 * g + 4])
            unders.add(Line(seg.get_corner(DL) + DOWN * 0.06 + RIGHT * 0.02, seg.get_corner(DR) + DOWN * 0.06 + LEFT * 0.02,
                            color=FOCUS if g % 2 == 0 else STORED, stroke_width=4))
        self.play(LaggedStart(*[Create(u) for u in unders], lag_ratio=0.12), run_time=1.8)

        # One point something, times two to the minus four
        self.at('So zero point one is stored as')
        hexbox = SurroundingRectangle(top3.lines[0].part(top3.lines[0].source.split()[-1]), color=FOCUS, buff=0.06)
        self.play(Create(hexbox))
        stored_as = rich(['0.1 ≈ 1.6 × 2', ('^', '−4', FOCUS), ' = 1.6 × 1/16'], font_size=34)
        stored_as.to_edge(LEFT, buff=0.6).set_y(-2.7)
        self.play(FadeIn(stored_as, shift=UP * 0.2))
        self.at('One point six, times one sixteenth')
        self.play(Indicate(stored_as, color=FOCUS, scale_factor=1.06))

        # [V2.2e] the implicit leading 1
        self.at('You might have noticed')
        self.remove(card)
        self.play(FadeOut(hexbox))
        ghost = DashedVMobject(Square(cell * 0.86), num_dashes=12).set_stroke(GREY_A, 2)
        ghost.next_to(fraction, LEFT, buff=0.06)
        ghost_one = Text('1', font=MONO, font_size=18, color=GREY_A).move_to(ghost)
        implicit = Text('implicit 1', font_size=22, color=GREY_A).next_to(ghost, DOWN, buff=0.25)
        self.at("Here's the trick")
        self.play(Create(ghost), FadeIn(implicit, shift=UP * 0.1))
        self.at('the first significant digit is always a one')
        lead = sci('1.1001100…', '2', '−4', font_size=44).move_to([4.2, -2.2, 0])
        lead_box = SurroundingRectangle(lead[0][0], color=FOCUS, buff=0.08)
        self.play(FadeIn(lead, shift=UP * 0.2))
        self.play(Create(lead_box))
        self.at("It's implied")
        self.play(ReplacementTransform(lead[0][0].copy(), ghost_one), run_time=1.0)
        self.at('That free bit')
        bits53 = Text('1 + 52 = 53 bits', font_size=22, color=STORED).move_to(frac_label)
        self.play(Transform(frac_label, bits53))

        # [V2.2f] the last four fraction bits were rounded up: 1001 became 1010
        self.at('And look at the very end')
        last4 = VGroup(*fraction[-4:])
        self.play(last4.animate.set_fill(FOCUS, 0.55).set_stroke(FOCUS, 3), unders[-1].animate.set_color(ERROR))
        should = Text('should be 1001…', font=MONO, font_size=20, color=GREY_B)
        became = Text('rounded up: 1010', font=MONO, font_size=20, color=FOCUS)
        note = VGroup(should, became).arrange(RIGHT, buff=0.4)
        note.next_to(fraction, DOWN, buff=0.25).align_to(fraction, RIGHT)
        self.at('should continue one, zero, zero, one')
        self.play(FadeIn(should, shift=UP * 0.1))
        self.at('Instead it ends')
        self.play(FadeIn(became, shift=UP * 0.1))
        self.play(Indicate(VGroup(*bits[-4:]), color=FOCUS, scale_factor=1.4))

        # [V2.2g] a quarter: fraction all zeros, exponent −2
        self.at('Compare a quarter')
        self.play(FadeOut(top3.body), FadeOut(unders), FadeOut(note), FadeOut(lead), FadeOut(lead_box),
                  last4.animate.set_fill(STORED, 0.15).set_stroke(STORED, 2))
        self.play(quarter.type_line(0, run_time=1.0))
        self.play(quarter.type_line(1, run_time=0.8), quarter.type_line(2, run_time=1.2))
        w = quarter.lines[1].source.split()
        q_bits = w[1] + w[3] + quarter.lines[2].source.split()[1]
        new_bits = bit_texts(q_bits, strip)
        q_biased = int(w[3], 2)
        q_sum = Text(f'{q_biased} − 1023 = {q_biased - 1023:+d}'.replace('-', '−').replace('+', ''),
                     font_size=34, color=FOCUS).move_to(sum_text, aligned_edge=LEFT)
        caption_q = rich(['¼ = 1.0 × 2', ('^', '−2', FOCUS)], font_size=40).to_edge(LEFT, buff=0.6).set_y(-2.7)
        self.play(Transform(bits, new_bits), Transform(sum_text, q_sum), FadeOut(stored_as),
                  FadeIn(caption_q, shift=UP * 0.2), run_time=1.2)
        self.at('fifty-two zeros')
        self.play(fraction.animate.set_stroke(EXACT, 3).set_fill(EXACT, 0.2), run_time=0.8)
        self.at('Nothing lost')
        tick = checkmark(size=0.5).next_to(caption_q, RIGHT, buff=0.4)
        self.play(Create(tick))
        self.finish()


# ---------------------------------------------------------------- 2.3

POWERS = ['1', '2', '4', '8', '16']


def window_amount_bits(amount, top=46, bottom=-56):
    """Bits of an exact decimal amount from 2**top down to 2**bottom, and the position of its
    leading bit (computed here: the 53-bit window starts there)."""
    value = Fraction(Decimal(amount))
    lead = math.floor(math.log2(value))
    bits = {}
    for p in range(top, bottom - 1, -1):
        bits[p] = int(value / Fraction(2) ** p) % 2
    return bits, lead


class Segment_2_3(Segment):
    """A sliding window: the same number of doubles in every doubling."""
    EPISODE, SEGMENT = 2, '2.3'

    def construct(self):
        # 53 bits; the exponent only moves the point
        self.at("Here's the key consequence")
        row = bit_boxes(53, 0.21).move_to(UP * 0.6)
        row.set_stroke(STORED, 2).set_fill(STORED, 0.25)
        brace = Brace(row, DOWN, buff=0.12, color=SCAFFOLD)
        label = Text('53 significant bits', font_size=26, color=STORED).next_to(brace, DOWN, buff=0.12)
        self.play(LaggedStart(*[FadeIn(b, scale=0.5) for b in row], lag_ratio=0.02), run_time=1.4)
        self.play(GrowFromCenter(brace), FadeIn(label))
        self.at('The exponent decides where they sit')
        where = ValueTracker(0)
        pointer = always_redraw(lambda: Triangle(color=FOCUS).set_fill(FOCUS, 1).scale(0.12).rotate(PI)
                                .move_to(row[0].get_corner(UR) + RIGHT * 0.21 * where.get_value() + UP * 0.25 + RIGHT * 0.02))
        point_label = Text('binary point', font_size=22, color=FOCUS)
        point_label.add_updater(lambda m: m.next_to(pointer, UP, buff=0.1))
        self.play(FadeIn(pointer), FadeIn(point_label))
        self.play(where.animate.set_value(30), run_time=1.6)
        self.play(where.animate.set_value(8), run_time=1.2)
        self.at('always the same number of them')
        self.play(Indicate(label, color=STORED))
        point_label.clear_updaters()

        # [V2.3a] the float line from 1 to 2: a dense comb, 2⁵² doubles
        self.at('So between one and two')
        self.play(FadeOut(VGroup(row, brace, label, pointer, point_label)))
        y, left, width, n = -0.2, -6.2, 12.4, 64
        hi = ValueTracker(2.0)
        shown = [1]

        def x_of(v):
            return left + width * (v - 1) / (hi.get_value() - 1)

        def tick(v):
            return Line([x_of(v), y - 0.22, 0], [x_of(v), y + 0.22, 0], color=STORED, stroke_width=2)

        def interval_ticks(j):
            a = 2 ** j
            return VGroup(*[tick(a + a * i / n) for i in range(n)])

        axis = always_redraw(lambda: Line([left, y, 0], [left + width, y, 0], color=SCAFFOLD, stroke_width=2))
        comb = always_redraw(lambda: VGroup(*[interval_ticks(j) for j in range(shown[0])]))

        def power_labels():
            group = VGroup()
            for k, text in enumerate(POWERS):
                v = 2 ** k
                if v <= hi.get_value() + 1e-9:
                    group.add(Text(text, font=MONO, font_size=24, color=SCAFFOLD).move_to([x_of(v), y - 0.55, 0]))
            return group

        labels = always_redraw(power_labels)

        def braces():
            group = VGroup()
            for j in range(shown[0]):
                a, b = 2 ** j, 2 ** (j + 1)
                br = Brace(Line([x_of(a), 0, 0], [x_of(b), 0, 0]), UP, buff=0, color=SCAFFOLD)
                br.stretch_to_fit_height(0.2).move_to([(x_of(a) + x_of(b)) / 2, y + 0.42, 0])
                tag = rich(['2', ('^', '52', STORED)], font_size=30).next_to(br, UP, buff=0.08)
                group.add(VGroup(br, tag))
            return group

        tops = always_redraw(braces)
        first = interval_ticks(0)
        self.play(FadeIn(axis), LaggedStart(*[Create(t) for t in first], lag_ratio=0.02), run_time=1.5)
        self.remove(*first)
        self.add(comb)
        self.play(FadeIn(labels), FadeIn(tops))
        caption = rich(['2', ('^', '52', STORED), ' doubles, evenly spaced'], font_size=36).move_to(UP * 2.6)
        self.play(FadeIn(caption, shift=DOWN * 0.2))

        # [V2.3b] each doubling: the same count, twice the gap
        def reveal(j, text_parts, cue):
            self.at(cue)
            self.play(hi.animate.set_value(2 ** (j + 1)), run_time=1.3)
            fresh = interval_ticks(j)
            self.play(LaggedStart(*[Create(t) for t in fresh], lag_ratio=0.015), run_time=1.3)
            self.remove(*fresh)
            shown[0] = j + 1
            new_caption = rich(text_parts, font_size=36).move_to(caption)
            self.play(Transform(caption, new_caption), run_time=0.6)

        reveal(1, ['2', ('^', '52', STORED), ' doubles, gaps × 2'], 'Between two and four')
        self.at('twice as far apart')
        g1 = Line([x_of(1), y - 0.9, 0], [x_of(1 + 1 / n), y - 0.9, 0])
        g2 = Line([x_of(2), y - 0.9, 0], [x_of(2 + 2 / n), y - 0.9, 0])
        gap_marks = VGroup(*[Brace(g, DOWN, buff=0, color=FOCUS) for g in (g1, g2)])
        gap_words = VGroup(Text('gap', font_size=22, color=FOCUS).next_to(gap_marks[0], DOWN, buff=0.08),
                           Text('gap × 2', font_size=22, color=FOCUS).next_to(gap_marks[1], DOWN, buff=0.08))
        self.play(FadeIn(gap_marks), FadeIn(gap_words))
        self.play(FadeOut(gap_marks), FadeOut(gap_words), run_time=0.5)
        reveal(2, ['2', ('^', '52', STORED), ' doubles, gaps × 4'], 'Between four and eight')
        reveal(3, ['every doubling: same count, gaps × 2'], 'Every time a number doubles')

        # [V2.3c] a 53-bit window slides along a growing balance
        self.at('Think of the fifty-three bits')
        for m in (axis, comb, labels, tops):
            m.clear_updaters()
        self.play(FadeOut(VGroup(axis, comb, labels, tops, caption)))
        cell, gap, top, bottom = 0.116, 0.16, 46, -56
        x0 = -(cell * (top - bottom + 1) + gap) / 2
        wy = -0.1

        def col_x(p):
            c = top - p
            return x0 + cell * c + cell / 2 + (gap if p < 0 else 0)

        def cells(amount):
            bits, lead = window_amount_bits(amount, top, bottom)
            group = VGroup()
            for p in range(top, bottom - 1, -1):
                sq = Rectangle(width=cell * 0.78, height=0.5).move_to([col_x(p), wy, 0])
                b = bits[p]
                if p > lead:
                    sq.set_stroke(GREY_D, 1, opacity=0.0).set_fill(BLACK, 0)
                elif p >= lead - 52:
                    color = MONEY if p >= 0 else STORED
                    sq.set_stroke(color, 1.5).set_fill(color, 0.95 if b else 0.12)
                else:
                    sq.set_stroke(GREY_D, 1).set_fill(GREY_C, 0.55 if b else 0.05)
                group.add(sq)
            frame = Rectangle(width=cell * 53 + 0.08 + (gap if lead - 52 < 0 <= lead else 0), height=cell * 2.2)
            frame.stretch_to_fit_height(0.72).set_stroke(FOCUS, 3)
            frame.move_to([(col_x(lead) + col_x(lead - 52)) / 2, wy, 0])
            return group, frame

        amounts = ['0.10', '1234.56', '1000000.01', f'{2 ** 46}.01']   # 2**46 as in q02-02's output
        boxes, frame = cells(amounts[0])
        frame_label = Text('53 bits', font_size=24, color=FOCUS).next_to(frame, DOWN, buff=0.15)
        point = Dot([x0 + cell * (top + 1) + gap / 2, wy - 0.22, 0], radius=0.06, color=WHITE)
        dollars = Text('dollars', font_size=26, color=MONEY).move_to([-3.2, wy + 0.85, 0])
        cents = Text('cents and below', font_size=26, color=STORED).move_to([3.2, wy + 0.85, 0])
        divider = DashedLine([point.get_x(), wy + 1.15, 0], [point.get_x(), wy - 0.38, 0], color=GREY_B)
        amount = Text('$' + f'{Decimal(amounts[0]):,}', font_size=40, color=MONEY).move_to(UP * 2.3)
        more = Text('…', font_size=30, color=GREY_B).next_to(boxes, RIGHT, buff=0.1)
        self.play(FadeIn(boxes), FadeIn(point), Create(divider), FadeIn(dollars), FadeIn(cents), FadeIn(amount),
                  FadeIn(more), run_time=1.0)
        self.play(Create(frame), FadeIn(frame_label))
        self.at('A small amount has plenty of room')
        inside = VGroup(*[b for b, p in zip(boxes, range(top, bottom - 1, -1)) if p < 0])
        self.play(Indicate(inside, color=STORED, scale_factor=1.05), run_time=1.2)
        self.at('As the amount grows')
        for a in amounts[1:]:
            new_boxes, new_frame = cells(a)
            new_amount = Text('$' + f'{Decimal(a):,}', font_size=40, color=MONEY).move_to(amount)
            self.play(Transform(boxes, new_boxes), Transform(frame, new_frame), Transform(amount, new_amount),
                      frame_label.animate.next_to(new_frame, DOWN, buff=0.15), run_time=1.4)
            self.wait(0.6)
        self.at('pushed out the far end')
        _, lead = window_amount_bits(amounts[-1], top, bottom)
        lost = VGroup(*[b for b, p in zip(boxes, range(top, bottom - 1, -1)) if p < lead - 52])
        self.play(lost.animate.set_stroke(ERROR, 1.5), run_time=0.6)
        self.play(lost.animate.shift(RIGHT * 0.6).set_opacity(0.15), run_time=0.9)

        # [V2.3d] in decimal: about 16 digits shared between dollars and cents
        self.at('In decimal terms')
        self.play(FadeOut(VGroup(boxes, frame, frame_label, point, divider, dollars, cents, amount, more, lost)))
        caption = fit(Text('about 16 significant decimal digits, shared between dollars and cents', font_size=32), 12.8)
        caption.move_to(UP * 2.5)
        slots = digit_slots(16).move_to(UP * 0.1)
        self.play(FadeIn(caption, shift=DOWN * 0.2), LaggedStart(*[Create(s) for s in slots], lag_ratio=0.05))

        def show(dollar_digits, cent_digits, label_text):
            digits = VGroup()
            for i, d in enumerate(dollar_digits + cent_digits):
                if i < len(slots):
                    digits.add(Text(d, font=MONO, font_size=30, color=BLACK).move_to(slots[i]))
            n = len(dollar_digits)
            dot = Dot(radius=0.07, color=FOCUS).move_to(
                slots[min(n, 15)].get_corner(DL if n < 16 else DR) + (LEFT if n < 16 else RIGHT) * 0.04 + UP * 0.08)
            label = Text(label_text, font_size=30, color=MONEY).next_to(slots, DOWN, buff=0.5)
            fit_cents = max(0, min(len(cent_digits), 16 - n))
            spill = VGroup()
            if fit_cents < len(cent_digits):
                spill = Text(cent_digits[fit_cents:], font=MONO, font_size=30, color=ERROR).next_to(slots, RIGHT, buff=0.3)
                spill.add(crossmark(size=0.45).move_to(spill))
            return digits, dot, label, fit_cents, spill

        cases = [('1234', '56', '$1,234.56'), ('70368744177664', '01', '$70,368,744,177,664.01'),
                 ('1000000000000000', '01', '$1,000,000,000,000,000.01')]
        current = None
        cues = ["They're shared between", None, 'The more digits the dollars need']
        for (d, c, text), cue in zip(cases, cues):
            if cue:
                self.at(cue)
            digits, dot, label, fit_cents, spill = show(d, c, text)
            anims = fill_slots(slots, len(d), fit_cents)
            if current is None:
                self.play(*anims, FadeIn(digits), FadeIn(dot), FadeIn(label), run_time=1.0)
            else:
                self.play(*anims, ReplacementTransform(current[0], digits), ReplacementTransform(current[1], dot),
                          ReplacementTransform(current[2], label), FadeOut(current[3]), run_time=1.0)
            if len(spill):
                self.play(FadeIn(spill, shift=LEFT * 0.2))
            current = (digits, dot, label, spill)
            self.wait(1.2)
        self.finish()


# ---------------------------------------------------------------- 2.4

class Segment_2_4(Segment):
    """The gap table (q02-02): math.ulp from a dollar to ten quadrillion."""
    EPISODE, SEGMENT = 2, '2.4'

    def construct(self):
        # [V2.4a] code panel q02-02, an empty console, the QR card
        code = code_panel(snippet_lines(GAPS, 5, 6), font_size=18).to_edge(UP, buff=0.3)
        rows = snippet_output(GAPS)[:7]
        con = spaced_console(rows, font_size=18, pitch=0.6).to_edge(LEFT, buff=0.4)
        con.align_to(code.get_bottom() + DOWN * 0.3, UP)
        card = qr_card('q02-02')
        self.play(FadeIn(code), FadeIn(con.background), FadeIn(card, shift=UP * 0.2))
        card_shown = self.renderer.time
        self.at('unit in the last place')
        self.play(Indicate(code.code_lines[1], color=FOCUS, scale_factor=1.03))
        self.at('gives the distance')
        demo_axis = Line([0.8, 0.6, 0], [6.6, 0.6, 0], color=SCAFFOLD, stroke_width=2)
        here, there = 2.0, 5.0
        demo_ticks = VGroup(*[Line([x, 0.35, 0], [x, 0.85, 0], color=STORED, stroke_width=4) for x in (here, there)])
        demo_names = VGroup(Text('a number', font_size=22, color=STORED).next_to(demo_ticks[0], DOWN, buff=0.15),
                            Text('the next double up', font_size=22, color=STORED).next_to(demo_ticks[1], DOWN, buff=0.15))
        demo_brace = Brace(Line([here, 0, 0], [there, 0, 0]), UP, buff=0, color=FOCUS).move_to([(here + there) / 2, 1.05, 0])
        demo_label = code_text('math.ulp(x)', font_size=24, color=FOCUS).next_to(demo_brace, UP, buff=0.1)
        demo = VGroup(demo_axis, demo_ticks, demo_names, demo_brace, demo_label)
        self.play(Create(demo_axis), FadeIn(demo_ticks[0]), FadeIn(demo_names[0]))
        self.play(FadeIn(demo_ticks[1], shift=LEFT * 0.6), FadeIn(demo_names[1]))
        self.play(GrowFromCenter(demo_brace), FadeIn(demo_label))

        # The log-scale ruler and the 1¢ reference mark
        self.at('At one dollar')
        self.wait_since(card_shown, 8.2)
        self.remove(card)
        self.play(FadeOut(demo), run_time=0.5)
        lo_log, cent_x, x0 = -16.0, 6.3, 0.1
        k = (cent_x - x0) / (-2 - lo_log)

        def x_at(gap):
            return x0 + (math.log10(gap) - lo_log) * k

        row_y = [con.lines[i].anchor()[1] for i in range(7)]
        top_y, bottom_y = row_y[0] + 0.4, row_y[-1] - 0.35
        base = Line([x0, top_y, 0], [x0, bottom_y, 0], color=GREY_D, stroke_width=2)
        cent_line = DashedLine([cent_x, top_y, 0], [cent_x, bottom_y, 0], color=EXACT, stroke_width=3)
        cent_label = Text('1¢', font_size=26, color=EXACT).next_to(cent_line, UP, buff=0.08)
        scale_label = Text('gap, log scale', font_size=20, color=SCAFFOLD).next_to(base, UP, buff=0.1).align_to(base, LEFT)
        self.play(Create(base), Create(cent_line), FadeIn(cent_label), FadeIn(scale_label))

        bars = VGroup()

        def show_row(i, color=STORED, run_time=0.8):
            gap = float(rows[i].split('gap')[1])
            end = x_at(gap)
            bar = Line([x0, row_y[i], 0], [end, row_y[i], 0], color=color, stroke_width=9)
            self.play(con.type_line(i, run_time=0.8))
            self.play(Create(bar), run_time=run_time)
            bars.add(bar)
            return bar

        show_row(0)
        self.at('At a million dollars')
        show_row(1, run_time=0.5)
        show_row(2, run_time=0.5)
        self.at('At a trillion dollars')
        show_row(3, run_time=0.5)
        show_row(4, run_time=0.5)
        self.at('Still fine for money')
        fine = VGroup(*[con.lines[i] for i in range(5)])
        self.play(cent_line.animate.set_stroke(width=6), fine.animate.set_color(EXACT), run_time=0.6)
        self.play(cent_line.animate.set_stroke(width=3), fine.animate.set_color(GREY_A), run_time=0.6)

        # [V2.4c] a quadrillion: past the cent mark, an eighth of a dollar
        self.at('At a quadrillion dollars')
        bar5 = show_row(5, color=ERROR, run_time=1.0)
        eighth = Text('an eighth of a dollar', font_size=22, color=ERROR)
        eighth.next_to(bar5, DOWN, buff=0.1).align_to([cent_x - 0.15, 0, 0], RIGHT)
        self.play(FadeIn(eighth, shift=UP * 0.1), con.lines[5].part('0.125').animate.set_color(ERROR))
        self.at('And at ten quadrillion')
        self.play(con.type_line(6, run_time=0.8))
        bar6 = Arrow([x0, row_y[6], 0], [x_at(2.0) + 0.6, row_y[6], 0], buff=0, color=ERROR, stroke_width=9,
                     max_tip_length_to_length_ratio=0.03)
        self.play(GrowArrow(bar6), con.lines[6].part('gap 2').animate.set_color(ERROR), run_time=1.2)

        # The odd-numbered dollar amounts don't exist (math.ulp(1e16) == 2, computed)
        self.at('The odd-numbered dollar amounts')
        step = 1.3
        line_y = -2.75
        axis = Line([-5.8, line_y, 0], [5.8, line_y, 0], color=SCAFFOLD, stroke_width=2)
        marks, names = VGroup(), VGroup()
        for d in range(9):
            x = -5.2 + d * step
            if float(10 ** 16 + d) == 10 ** 16 + d:
                marks.add(Line([x, line_y - 0.22, 0], [x, line_y + 0.22, 0], color=STORED, stroke_width=4))
            else:
                marks.add(crossmark(size=0.3).move_to([x, line_y, 0]))
            names.add(Text(f'+{d}', font=MONO, font_size=20, color=SCAFFOLD).move_to([x, line_y - 0.45, 0]))
        what = Text('dollars past ten quadrillion', font_size=22, color=SCAFFOLD).next_to(axis, UP, buff=0.35)
        self.play(Create(axis), FadeIn(names), FadeIn(what))
        self.play(LaggedStart(*[FadeIn(m, scale=0.5) for m in marks], lag_ratio=0.15), run_time=1.6)
        self.finish()


# ---------------------------------------------------------------- 2.5

class Segment_2_5(Segment):
    """When a balance loses its cents: 2⁴⁵, 2⁴⁶, 2⁴⁷ (q02-02's last three lines)."""
    EPISODE, SEGMENT = 2, '2.5'

    def construct(self):
        con = output_console(GAPS, ['2**45', '2**46', '2**47'], font_size=20).to_edge(UP, buff=0.35)
        self.play(FadeIn(con.background))
        y = -0.4
        powers = VGroup(*[rich(['2', ('^', str(p), FOCUS)], font_size=64) for p in (45, 46, 47)]).arrange(RIGHT, buff=1.6)
        powers.move_to(DOWN * 0.4)
        self.at('The gaps change at powers of two')
        self.play(LaggedStart(*[FadeIn(pw, shift=UP * 0.3) for pw in powers], lag_ratio=0.4), run_time=1.6)

        def close_up(p):
            x = Fraction(2 ** p)
            line = FloatLine(x - Fraction(1, 100), x + Fraction(7, 100), width=12).shift(UP * y)
            marks, names = VGroup(), VGroup()
            for c in range(-1, 8):
                v = x + Fraction(c, 100)
                marks.add(Line(line.point(v) + DOWN * 0.18, line.point(v) + DOWN * 0.34, color=MONEY, stroke_width=3))
                if c == 0:
                    name = rich(['2', ('^', str(p))], font_size=30, color=SCAFFOLD)
                else:
                    name = Text(f'{c:+d}¢'.replace('-', '−'), font_size=20, color=MONEY)
                names.add(name.next_to(marks[-1], DOWN, buff=0.1))
            return x, line, VGroup(marks, names)

        def gap_brace(line, x, gap_text, words):
            gap = Fraction(math.ulp(float(x)))                    # equals the gap q02-02 prints
            br = Brace(Line(line.point(x), line.point(x + gap)), DOWN, buff=0, color=FOCUS)
            br.move_to([(line.point(x)[0] + line.point(x + gap)[0]) / 2, y - 1.5, 0])
            text = Text(f'gap {gap_text} = 1/{gap.denominator} of a dollar{words}', font_size=24, color=FOCUS)
            text.next_to(br, DOWN, buff=0.1)
            if text.get_left()[0] < -6.9:
                text.align_to([-6.9, 0, 0], LEFT)
            return VGroup(br, text), gap

        focus = None

        def focus_line(i):
            nonlocal focus
            box = SurroundingRectangle(con.lines[i], color=FOCUS, buff=0.06)
            if focus is None:
                self.play(Create(box), run_time=0.4)
            else:
                self.play(Transform(focus, box), run_time=0.4)
                box = focus
            focus = box

        def gap_text(i):
            return con.lines[i].source.split('gap ')[1].split()[0]

        # [V2.5a]/[V2.5b] 2⁴⁵: the gap is under a cent; cents land on different doubles
        self.at('At two to the forty-fifth')
        self.play(FadeOut(powers), con.type_line(0, run_time=1.2))
        focus_line(0)
        x, line, cents = close_up(45)
        self.play(Create(line.axis), LaggedStart(*[Create(t) for t in line.ticks], lag_ratio=0.05),
                  FadeIn(cents), run_time=1.4)
        self.at('the gap is under a cent')
        brace, gap = gap_brace(line, x, gap_text(0), '')
        self.play(FadeIn(brace, shift=UP * 0.1), con.lines[0].part(gap_text(0)).animate.set_color(FOCUS))
        self.at('Cents are no longer exact')
        arc = cent_arc(line, x)
        one = x + Fraction(1, 100)
        d1 = line.diamond(one)
        self.play(Create(arc[0]), FadeIn(arc[1]), run_time=0.8)
        self.play(FadeIn(d1, shift=DOWN * 0.2))
        s1 = line.snap(one)
        self.play(Create(s1))
        self.at('different cent amounts still land on different doubles')
        two = x + Fraction(2, 100)
        d2 = line.diamond(two)
        s2 = line.snap(two)
        self.play(FadeIn(d2, shift=DOWN * 0.2))
        self.play(Create(s2))
        hit = VGroup(*[t for t in line.ticks if Fraction(line.tick_values[list(line.ticks).index(t)]) in
                       (Fraction(line.nearest(one)), Fraction(line.nearest(two)))])
        self.play(hit.animate.set_color(EXACT).set_stroke(width=6), run_time=0.6)
        scene45 = VGroup(line, cents, brace, arc, d1, s1, d2, s2)

        # [V2.5c] 2⁴⁶: the gap passes a cent; +1¢ snaps up a cent and a half
        self.at('At two to the forty-sixth')
        self.play(FadeOut(scene45), con.type_line(1, run_time=1.2))
        focus_line(1)
        x, line, cents = close_up(46)
        self.play(Create(line.axis), LaggedStart(*[Create(t) for t in line.ticks], lag_ratio=0.05),
                  FadeIn(cents), run_time=1.2)
        self.at('the gap is one sixty-fourth')
        brace, gap = gap_brace(line, x, gap_text(1), ', a cent and a half')
        self.play(FadeIn(brace, shift=UP * 0.1), con.lines[1].part(gap_text(1)).animate.set_color(FOCUS))
        self.at('Now neighbouring cent amounts')
        one, two = x + Fraction(1, 100), x + Fraction(2, 100)
        d1, d2 = line.diamond(one), line.diamond(two)
        s1, s2 = line.snap(one), line.snap(two)
        self.play(FadeIn(d1, shift=DOWN * 0.2), FadeIn(d2, shift=DOWN * 0.2))
        self.play(Create(s1), Create(s2))
        same = [t for t, v in zip(line.ticks, line.tick_values) if Fraction(v) == Fraction(line.nearest(one))]
        self.play(VGroup(*same).animate.set_color(ERROR).set_stroke(width=6), run_time=0.6)
        self.at('Add a cent, and the result snaps')
        arc = cent_arc(line, x)
        self.play(Create(arc[0]), FadeIn(arc[1]), run_time=0.8)
        assert Fraction(2.0 ** 46 + 0.01) == Fraction(line.nearest(one))      # the fact-check value, 2**46 + 1/64
        self.play(Indicate(s1, color=ERROR, scale_factor=1.2))
        scene46 = VGroup(line, cents, brace, arc, d1, s1, d2, s2)

        # [V2.5d] 2⁴⁷: +1¢ falls short of halfway and snaps back; x + 0.01 == x
        self.at('And at two to the forty-seventh')
        self.play(FadeOut(scene46), con.type_line(2, run_time=1.2))
        focus_line(2)
        x, line, cents = close_up(47)
        self.play(Create(line.axis), LaggedStart(*[Create(t) for t in line.ticks], lag_ratio=0.05),
                  FadeIn(cents), run_time=1.2)
        self.at('the gap is over three cents')
        brace, gap = gap_brace(line, x, gap_text(2), '')
        self.play(FadeIn(brace, shift=UP * 0.1), con.lines[2].part(gap_text(2)).animate.set_color(FOCUS))
        self.at("Adding one cent doesn't even reach halfway")
        half = DashedLine(line.point(x + gap / 2) + DOWN * 0.3, line.point(x + gap / 2) + UP * 1.3, color=GREY_B)
        half_label = Text('halfway', font_size=20, color=GREY_B).next_to(half, UP, buff=0.08)
        arc = cent_arc(line, x)
        one = x + Fraction(1, 100)
        d1 = line.diamond(one)
        self.play(Create(half), FadeIn(half_label))
        self.play(Create(arc[0]), FadeIn(arc[1]), run_time=0.8)
        self.play(FadeIn(d1, shift=DOWN * 0.2))
        self.at('rounds right back to where it started')
        assert 2.0 ** 47 + 0.01 == 2.0 ** 47
        s1 = line.snap(one)
        self.play(Create(s1))
        self.at('The balance plus a cent equals the balance')
        claim = con.lines[2].source[con.lines[2].source.index('x + 0.01'):]
        mark = stamp(claim).move_to(RIGHT * 3.6 + DOWN * 3.0)
        self.play(FadeIn(mark, scale=1.6), con.lines[2].part('True').animate.set_color(ERROR), run_time=0.5)
        scene47 = VGroup(line, cents, brace, arc, d1, s1, half, half_label, mark)

        # The same window wherever the numbers live: sixteen digits get used up
        self.at("You probably don't have seventy trillion dollars")
        self.play(FadeOut(scene47), FadeOut(focus))
        slots = digit_slots(16).move_to(UP * 0.4)
        bar_label = Text('about 16 digits', font_size=26, color=SCAFFOLD).next_to(slots, UP, buff=0.25)
        self.play(LaggedStart(*[Create(s) for s in slots], lag_ratio=0.04), FadeIn(bar_label))
        self.play(*fill_slots(slots, 4, 12))
        reasons = ['a currency with very small units', 'amounts kept in thousandths', "a large bank's year of transactions"]
        cues = ['Count in a currency', 'or keep amounts in thousandths', 'or add up the transactions']
        fills = [(8, 8), (11, 5), (14, 2)]
        shown = VGroup()
        for text, cue, (g, b) in zip(reasons, cues, fills):
            self.at(cue)
            item = Text(text, font_size=26, color=MONEY)
            item.next_to(shown if len(shown) else slots, DOWN, buff=0.3 if len(shown) else 0.6)
            item.set_x(0)
            self.play(FadeIn(item, shift=UP * 0.15), *fill_slots(slots, g, b), run_time=0.8)
            shown.add(item)
        self.at('get used up much sooner')
        self.play(*fill_slots(slots, 16, 0), run_time=0.8)
        self.at('a much smaller float')
        small = digit_slots(7).move_to(slots, aligned_edge=LEFT)
        small_label = Text('32-bit float: about 7 digits', font_size=26, color=STORED).next_to(small, UP, buff=0.25)
        small_label.align_to(small, LEFT)
        small.move_to(slots)
        small_label.next_to(small, UP, buff=0.25)
        self.play(FadeOut(shown), ReplacementTransform(slots, small), Transform(bar_label, small_label), run_time=1.2)
        self.play(*fill_slots(small, 7, 0), run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 2.6

class Segment_2_6(Segment):
    """Thirty-two bits (q02-03): a house price in a 32-bit float."""
    EPISODE, SEGMENT = 2, '2.6'

    def construct(self):
        # [V2.6a] the 64-box strip shrinks to 32: 1 + 8 + 23, plus the implicit 1
        wide = split_boxes(bit_boxes(64, 0.19), (1, 11, 52), 0.34).move_to(UP * 2.2)
        for g, c in zip(groups_of(wide, (1, 11, 52)), (GREY_B, FOCUS, STORED)):
            g.set_stroke(c, 2).set_fill(c, 0.2)
        wide_label = Text('64-bit double · 53 bits of precision', font_size=24, color=SCAFFOLD).next_to(wide, UP, buff=0.15)
        self.play(FadeIn(wide), FadeIn(wide_label))
        self.at('thirty-two bits in all')
        narrow = split_boxes(bit_boxes(32, 0.3), (1, 8, 23), 0.45).move_to(DOWN * 0.1)
        sign, exponent, fraction = groups_of(narrow, (1, 8, 23))
        for g, c in zip((sign, exponent, fraction), (GREY_B, FOCUS, STORED)):
            g.set_stroke(c, 2).set_fill(c, 0.2)
        self.play(*[ReplacementTransform(a.copy(), b) for a, b in zip(groups_of(wide, (1, 11, 52)), (sign, exponent, fraction))],
                  run_time=1.6)
        self.at('One sign bit')
        names = VGroup(Text('sign', font_size=22, color=GREY_B).next_to(sign, UP, buff=0.12),
                       Text('exponent · 8', font_size=22, color=FOCUS).next_to(exponent, UP, buff=0.12),
                       Text('fraction · 23', font_size=22, color=STORED).next_to(fraction, UP, buff=0.12))
        self.play(LaggedStart(*[FadeIn(nm, shift=DOWN * 0.1) for nm in names], lag_ratio=0.5), run_time=1.6)
        self.at('so twenty-four bits of precision')
        ghost = DashedVMobject(Square(0.3 * 0.86), num_dashes=12).set_stroke(GREY_A, 2).next_to(fraction, LEFT, buff=0.08)
        one = Text('1', font=MONO, font_size=20, color=GREY_A).move_to(ghost)
        brace = Brace(VGroup(ghost, fraction), DOWN, buff=0.12, color=STORED)
        bits24 = Text('implicit 1 + 23 = 24 bits', font_size=24, color=STORED).next_to(brace, DOWN, buff=0.1)
        self.play(Create(ghost), FadeIn(one), GrowFromCenter(brace), FadeIn(bits24))
        self.at('Roughly seven significant decimal digits')
        slots = digit_slots(16, width=0.42, height=0.56).move_to(DOWN * 2.6)
        self.play(FadeIn(slots))
        seven = digit_slots(7, width=0.42, height=0.56).move_to(slots, aligned_edge=LEFT)
        seven_label = Text('about 7 decimal digits', font_size=26, color=STORED).next_to(seven, RIGHT, buff=0.4)
        self.play(ReplacementTransform(slots, seven), FadeIn(seven_label, shift=LEFT * 0.2), run_time=1.0)
        self.play(*fill_slots(seven, 7, 0), run_time=0.5)
        slots = seven

        # [V2.6b] code panel q02-03; the console prints the five prices
        self.at('The code in the corner')
        code = code_panel(snippet_lines(PRICES, 6, 7), font_size=20).to_corner(UL, buff=0.35)
        con = output_console(PRICES, font_size=20).next_to(code, DOWN, buff=0.3, aligned_edge=LEFT)
        card = qr_card('q02-03')
        self.play(FadeOut(VGroup(wide, wide_label, sign, exponent, fraction, names, ghost, one, brace, bits24,
                                 slots, seven_label)), run_time=0.6)
        self.play(FadeIn(code), FadeIn(con.background), FadeIn(card, shift=UP * 0.2))

        def type_price(i):
            line = con.lines[i]
            typed, stored = line.source.split('stored as')
            typed = typed.replace('$', '').strip()
            stored = stored.strip()
            self.play(con.type_line(i, run_time=1.0))
            keep = len(common_prefix(typed, stored))
            start = line.source.index(stored, line.source.index('stored as'))
            if keep < len(stored):
                self.play(line.chars(start + keep, start + len(stored)).animate.set_color(ERROR), run_time=0.5)
            return line, typed, stored

        self.at('Twelve hundred dollars')
        type_price(0)
        self.at('At sixty-five thousand')
        type_price(1)
        self.at('one cent returns as')
        line1 = con.lines[1]
        s = line1.source.index('stored as')
        self.play(Indicate(line1.chars(s + 10), color=ERROR, scale_factor=1.15))
        self.at('And at one hundred and thirty-one thousand')
        type_price(2)

        # [V2.6c] a float line around $131,072: float32 ticks 1/64 apart, cents between them
        self.at('the gap between neighbours reaches')
        self.remove(card)
        base = Fraction(131072)
        lo, hi = base - Fraction(1, 100), base + Fraction(7, 100)
        ticks = float32_neighbours(lo, hi)                     # computed: the float32 values in view
        line = FloatLine(lo, hi, width=12, ticks=ticks).move_to(DOWN * 2.3)
        marks, labels = VGroup(), VGroup()
        for c in range(-1, 8):
            v = base + Fraction(c, 100)
            marks.add(Line(line.point(v) + DOWN * 0.18, line.point(v) + DOWN * 0.34, color=MONEY, stroke_width=3))
            text = '$131,072' if c == 0 else f'{c:+d}¢'.replace('-', '−')
            labels.add(Text(text, font_size=20, color=SCAFFOLD if c == 0 else MONEY).next_to(marks[-1], DOWN, buff=0.08))
        f32_gap = output_line(PRICES, 'float32 gap').split(': ')[1]
        gap = Fraction(float(f32_gap))
        br = Brace(Line(line.point(base), line.point(base + gap)), UP, buff=0.25, color=FOCUS)
        gap_label = Text(f'1/{gap.denominator} = ${f32_gap}', font_size=24, color=FOCUS).next_to(br, UP, buff=0.08)
        self.play(Create(line.axis), LaggedStart(*[Create(t) for t in line.ticks], lag_ratio=0.1), run_time=1.2)
        self.play(FadeIn(marks), FadeIn(labels), GrowFromCenter(br), FadeIn(gap_label))

        self.at("From there on, a thirty-two-bit float can't tell cents apart")
        self.play(FadeOut(br), FadeOut(gap_label), run_time=0.4)
        a, b = base + Fraction(1, 100), base + Fraction(2, 100)
        da, db = line.diamond(a), line.diamond(b)
        assert float32(131072.01) == float32(131072.02)        # computed: both cents land on one float32
        self.play(FadeIn(da, shift=DOWN * 0.2), FadeIn(db, shift=DOWN * 0.2))
        self.play(Create(line.snap(a)), Create(line.snap(b)))
        type_price(3)

        # The million-dollar row loses its cent
        self.at('By a million dollars')
        line4, typed4, stored4 = type_price(4)
        cent = line4.source.index(typed4) + len(typed4) - 1
        lost_digit = line4.chars(cent, cent + 1)
        self.play(lost_digit.animate.set_color(ERROR).scale(1.4), run_time=0.4)
        coin_ = penny(0.22).move_to(lost_digit.get_center() + UP * 0.05)
        self.play(FadeIn(coin_, scale=0.5), lost_digit.animate.scale(1 / 1.4).set_opacity(0.35), run_time=0.4)
        self.play(tumble(coin_, RIGHT * 5.0 + DOWN * 0.6, turns=4, run_time=1.5))
        self.remove(coin_)

        # For comparison, a double's ticks at the same price are too close to draw apart
        self.at('For comparison')
        self.play(con.type_line(5, run_time=0.9))
        self.play(con.type_line(6, run_time=1.2))
        band = Rectangle(width=line.axis.get_length(), height=0.16).set_fill(STORED, 0.6).set_stroke(width=0)
        band.move_to(line.axis).shift(UP * 0.0)
        band_label = Text('float64 ticks', font_size=22, color=STORED).next_to(band, RIGHT, buff=0.1)
        band_label.next_to(line.axis, UP, buff=0.9).align_to(line.axis, RIGHT)
        f64 = con.lines[6].part(con.lines[6].source.split(': ')[1])
        self.play(FadeIn(band), FadeIn(band_label), f64.animate.set_color(STORED))

        # [V2.6d] where float32 hides
        self.at('You might think nobody')
        self.play(FadeOut(Group(*self.mobjects)))
        icons = [gpu_icon(), database_icon(), file_icon(), coin_stack()]
        names = ['graphics cards and ML pipelines', 'some database REAL columns', 'binary file formats', 'game economies']
        cues = ['data pipelines built for graphics cards', 'some database columns', 'binary file formats', 'game economies']
        tiles = VGroup()
        for k, (icon, nm) in enumerate(zip(icons, names)):
            icon.scale_to_fit_height(min(icon.height, 1.1)).move_to([-4.95 + 3.3 * k, 1.9, 0])
            label = wrapped_text(nm, 2.9, font_size=24).next_to(icon, DOWN, buff=0.3)
            label.set_y(0.75)
            tag = price_tag('float32', color=STORED, font_size=22).next_to(label, DOWN, buff=0.3)
            tag.set_y(-0.15)
            tiles.add(VGroup(icon, label, tag))
        for tile, cue in zip(tiles, cues):
            self.at(cue)
            self.play(FadeIn(tile[0], shift=UP * 0.2), FadeIn(tile[1]), run_time=0.6)
            self.play(FadeIn(tile[2], shift=DOWN * 0.2), run_time=0.4)

        # The whole pipeline is only as precise as its narrowest pipe
        self.at('Anywhere a number passes through')
        py = -2.4
        pipes = VGroup(Rectangle(width=4.0, height=1.2).move_to([-4.2, py, 0]),
                       Rectangle(width=2.6, height=0.36).move_to([-0.9, py, 0]),
                       Rectangle(width=4.0, height=1.2).move_to([2.4, py, 0]))
        pipes.set_stroke(GREY_B, 3).set_fill(GREY_E, 0.6)
        pipes[1].set_stroke(STORED, 3)
        narrow_tag = Text('float32', font_size=20, color=STORED).next_to(pipes[1], UP, buff=0.12)
        self.play(FadeIn(pipes), FadeIn(narrow_tag))
        rows_y = [py + 0.4, py + 0.2, py, py - 0.2, py - 0.4]
        drops = VGroup(*[Dot([-5.9 + 0.5 * i, ry, 0], radius=0.06, color=MONEY) for ry in rows_y for i in range(6)])
        self.play(FadeIn(drops), run_time=0.4)
        through = VGroup(*[d for d in drops if abs(d.get_y() - py) < 0.05])
        blocked = VGroup(*[d for d in drops if abs(d.get_y() - py) >= 0.05])
        self.play(through.animate.shift(RIGHT * 7.6), blocked.animate.shift(RIGHT * 2.1).set_opacity(0.0),
                  run_time=2.4, rate_func=linear)
        self.at('narrowest pipe')
        self.play(pipes[1].animate.set_stroke(ERROR, 5), narrow_tag.animate.set_color(ERROR))
        self.finish()


# ---------------------------------------------------------------- 2.7

class Segment_2_7(Segment):
    """Round to nearest, ties to even."""
    EPISODE, SEGMENT = 2, '2.7'

    def construct(self):
        # [V2.7a] two ticks; an exact result snaps to the nearer one
        line = FloatLine(0, 1, width=10, ticks=[0.2, 0.8], tick_height=0.5).shift(DOWN * 0.4)
        names = VGroup(*[Text('double', font_size=22, color=STORED).next_to(line.point(v), DOWN, buff=0.4)
                         for v in (0.2, 0.8)])
        self.play(Create(line.axis), Create(line.ticks), FadeIn(names))

        # [V2.7b] the operations that keep the promise
        self.at('Addition, subtraction')
        ops = Text('+   −   ×   ÷   √', font_size=60, color=WHITE).move_to(UP * 2.7)
        self.play(LaggedStart(*[FadeIn(g, shift=DOWN * 0.3) for g in ops], lag_ratio=0.35), run_time=2.2)
        self.at('the exact answer, rounded to the nearest double')
        d = line.diamond(Fraction(38, 100))
        exact = Text('exact answer', font_size=24, color=FOCUS)
        exact.add_updater(lambda m: m.next_to(d, UP, buff=0.15))
        self.play(FadeIn(d, shift=DOWN * 0.2), FadeIn(exact))
        arrow = line.snap(Fraction(38, 100))
        self.play(Create(arrow))
        self.at('As if the computer did the arithmetic perfectly')
        self.play(FadeOut(arrow), d.animate.move_to(line.point(Fraction(66, 100)) + UP * 0.45), run_time=1.2)
        arrow = line.snap(Fraction(66, 100))
        self.play(Create(arrow))
        self.at('rounded once at the end')
        once = Text('rounded once', font_size=24, color=FOCUS).next_to(line.point(0.8), DOWN, buff=1.0)
        self.play(FadeIn(once, shift=UP * 0.1), Indicate(line.ticks[1], color=FOCUS))

        # [V2.7c] exactly halfway: the tie goes to the even neighbour
        self.at('When the exact answer falls precisely halfway')
        self.play(FadeOut(arrow), FadeOut(once), d.animate.move_to(line.point(Fraction(1, 2)) + UP * 0.45), run_time=1.2)
        half = DashedLine(line.point(0.5) + DOWN * 0.4, line.point(0.5) + UP * 0.25, color=GREY_B)
        bits = VGroup(Text('…1', font=MONO, font_size=30, color=STORED).next_to(line.point(0.2), UP, buff=0.4),
                      Text('…0', font=MONO, font_size=30, color=STORED).next_to(line.point(0.8), UP, buff=0.4))
        self.play(Create(half), FadeIn(bits))
        self.at('the tie goes to the one whose last bit is zero')
        tie = snap_to(line, Fraction(1, 2), 0.8)
        even = Text('even', font_size=26, color=EXACT).next_to(names[1], DOWN, buff=0.15)
        self.play(Create(tie))
        self.play(FadeIn(even, shift=UP * 0.1), bits[1].animate.set_color(EXACT))

        # [V2.7d] episode 1's picture: stored 0.1 + stored 0.2 lands halfway and snaps to the even tick
        self.at('zero point one plus zero point two')
        exact.clear_updaters()
        self.play(FadeOut(VGroup(line, names, d, exact, half, bits, tie, even)), ops.animate.scale(0.6).to_edge(UP, buff=0.3))
        lo, hi = Fraction('0.29999999999999993'), Fraction('0.30000000000000016')
        real = FloatLine(lo, hi, width=11, tick_height=0.5).shift(DOWN * 0.4)
        total = Fraction(0.1) + Fraction(0.2)                       # computed: the exact sum of the stored values
        below, above = 0.3, 0.1 + 0.2
        assert total == (Fraction(below) + Fraction(above)) / 2    # exactly halfway
        sum_repr = output_line(EP01_SUM, 'a + b        =').split('= ')[1]
        tick_names = VGroup(
            Text(f'0.3   …{last_bit(below)}', font=MONO, font_size=22, color=STORED).next_to(real.point(below), DOWN, buff=0.4),
            Text(f'{sum_repr}   …{last_bit(above)}', font=MONO, font_size=22, color=STORED).next_to(real.point(above), DOWN, buff=0.4))
        if tick_names[1].get_left()[0] < tick_names[0].get_right()[0] + 0.3:
            tick_names[1].next_to(real.point(above), DOWN, buff=1.0)
        self.play(Create(real.axis), Create(real.ticks), FadeIn(tick_names))
        self.at('The exact sum fell on a halfway point')
        d2 = real.diamond(total)
        label = Text('stored 0.1 + stored 0.2, exactly', font_size=24, color=FOCUS).next_to(d2, UP, buff=0.2)
        self.play(FadeIn(d2, shift=DOWN * 0.2), FadeIn(label))
        self.at('the even neighbour happened to be the one above')
        up = snap_to(real, total, above)
        even2 = Text('even', font_size=26, color=EXACT).next_to(tick_names[1], DOWN, buff=0.15)
        self.play(Create(up))
        self.play(FadeIn(even2, shift=UP * 0.1))

        # Why ties go to even: errors that drift versus errors that cancel (computed, illustrative)
        self.at('Rounding to even sounds fussy')
        self.play(FadeOut(VGroup(real, tick_names, d2, label, up, even2)))
        rng = random.Random(6)
        steps = 60
        always_up, to_even = [0.0], [0.0]
        for _ in range(steps):
            always_up.append(always_up[-1] + 0.5)
            to_even.append(to_even[-1] + (0.5 if rng.random() < 0.5 else -0.5))
        plots = VGroup()
        for k, (series, title, color) in enumerate(((always_up, 'ties always up', ERROR), (to_even, 'ties to even', EXACT))):
            origin = np.array([-6.0 + 6.6 * k, -2.2, 0])
            zero = Line(origin, origin + RIGHT * 5.4, color=SCAFFOLD, stroke_width=2)
            up_axis = Line(origin + DOWN * 0.9, origin + UP * 3.4, color=SCAFFOLD, stroke_width=2)
            points = [origin + RIGHT * 5.4 * i / steps + UP * v * 3.2 / (0.5 * steps) for i, v in enumerate(series)]
            path = VMobject(color=color, stroke_width=4).set_points_as_corners(points)
            name = Text(title, font_size=26, color=color).next_to(up_axis, UP, buff=0.15).align_to(up_axis, LEFT)
            err = Text('total error', font_size=20, color=SCAFFOLD).rotate(PI / 2).next_to(up_axis, LEFT, buff=0.1)
            ops_label = Text('operations →', font_size=20, color=SCAFFOLD).next_to(zero, DOWN, buff=0.1).align_to(zero, RIGHT)
            plots.add(VGroup(zero, up_axis, name, err, ops_label, path))
        self.play(*[FadeIn(VGroup(*p[:5])) for p in plots], ops.animate.set_opacity(0))
        self.at('If ties always went up')
        self.play(Create(plots[0][5]), run_time=2.5, rate_func=linear)
        self.at('Sending half the ties up')
        self.play(Create(plots[1][5]), run_time=2.5, rate_func=linear)
        self.at('episode six')
        later = Text('Episode 6 · Rounding is a policy', font_size=24, color=SCAFFOLD).move_to(DOWN * 3.55)
        self.play(FadeIn(later, shift=UP * 0.2))

        # [V2.7e] each error is at most half a gap; the slivers pile up into a bar
        self.at('So each single operation')
        self.play(FadeOut(VGroup(plots, later)))
        gap_w = 0.6
        ruler = VGroup(Line(LEFT * gap_w / 2, RIGHT * gap_w / 2, color=SCAFFOLD, stroke_width=2),
                       Line(UP * 0.25, DOWN * 0.25, color=STORED, stroke_width=4).shift(LEFT * gap_w / 2),
                       Line(UP * 0.25, DOWN * 0.25, color=STORED, stroke_width=4).shift(RIGHT * gap_w / 2),
                       DashedLine(UP * 0.18, DOWN * 0.18, color=GREY_B)).move_to(UP * 2.2 + LEFT * 4.6)
        gap_name = Text('one gap', font_size=22, color=STORED).next_to(ruler, UP, buff=0.15)
        half_name = Text('error ≤ ½ gap', font_size=22, color=ERROR).next_to(ruler, RIGHT, buff=0.4)
        self.play(FadeIn(ruler), FadeIn(gap_name))
        rng = random.Random(2)
        widths = [gap_w / 2 * rng.uniform(0.25, 1.0) for _ in range(48)]
        first = Rectangle(width=widths[0], height=0.3).set_fill(ERROR, 0.9).set_stroke(BLACK, 1)
        first.move_to(ruler[1].get_center() + RIGHT * widths[0] / 2 + DOWN * 0.45)
        self.at('at most half a gap')
        self.play(FadeIn(first), FadeIn(half_name))
        self.at("doesn't do one operation")
        bar_y, x = -0.6, -6.0
        slivers = VGroup()
        for w in widths:
            s = Rectangle(width=w, height=0.42).set_fill(ERROR, 0.9).set_stroke(BLACK, 1.5)
            s.move_to([x + w / 2, bar_y, 0])
            x += w
            slivers.add(s)
        self.play(ReplacementTransform(first, slivers[0]), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.6) for s in slivers[1:6]], lag_ratio=0.6), run_time=2.0)
        self.at('It does millions')
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.6) for s in slivers[6:]], lag_ratio=0.25), run_time=2.4)
        brace = Brace(slivers, DOWN, buff=0.15, color=ERROR)
        caption = Text('each step is tiny; steps add up', font_size=32, color=WHITE).next_to(brace, DOWN, buff=0.3)
        self.at('its own half-gap')
        self.play(GrowFromCenter(brace), FadeIn(caption, shift=UP * 0.2))
        self.finish()


# ---------------------------------------------------------------- 2.8

def catchment(line, value, color=FOCUS):
    """The band of real numbers whose nearest double is `value` (half a gap either side)."""
    below = math.nextafter(value, -math.inf)
    above = math.nextafter(value, math.inf)
    left = line.point((Fraction(below) + Fraction(value)) / 2)
    right = line.point((Fraction(value) + Fraction(above)) / 2)
    band = Rectangle(width=right[0] - left[0], height=0.44).set_fill(color, 0.18).set_stroke(color, 1.5)
    return band.move_to((left + right) / 2)


class Segment_2_8(Segment):
    """What print hides (q02-04)."""
    EPISODE, SEGMENT = 2, '2.8'

    def construct(self):
        # [V2.8a] code panel q02-04, console beside it
        code = code_panel(snippet_lines(PRINTS, 4, 7), font_size=18).to_corner(UL, buff=0.3)
        first = Console(snippet_output(PRINTS)[:4], font_size=18).next_to(code, DOWN, buff=0.25, aligned_edge=LEFT)
        card = qr_card('q02-04')
        self.play(FadeIn(code), FadeIn(first.background), FadeIn(card, shift=UP * 0.2))

        # [V2.8b] the float line around 0.1: its catchment, and 0.1 as the shortest name inside it
        self.at('Python prints the shortest decimal')
        ulp = Fraction(math.ulp(0.1))
        line = FloatLine(Fraction(0.1) - ulp * 5 / 2, Fraction(0.1) + ulp * 5 / 2, width=9.0, tick_height=0.4)
        line.move_to([-2.0, -1.15, 0])
        band = catchment(line, 0.1)
        stored_name = Text('stored 0.1', font_size=20, color=STORED).next_to(line.point(0.1), DOWN, buff=0.36)
        self.play(Create(line.axis), Create(line.ticks), FadeIn(stored_name))
        self.play(FadeIn(band))
        self.at("For zero point one, that's zero point one")
        self.play(first.type_line(0, run_time=0.8))
        name = line.diamond(Fraction(1, 10))
        name_label = Text('0.1', font=MONO, font_size=26, color=FOCUS).next_to(name, UP, buff=0.12)
        shortest = Text('shortest name in here', font_size=20, color=FOCUS).next_to(name_label, RIGHT, buff=0.25)
        self.play(FadeIn(name, shift=DOWN * 0.2), FadeIn(name_label), FadeIn(shortest))
        self.at('Ask for twenty decimal places')
        self.play(first.type_line(1, run_time=1.2))
        self.at('then five, five, five')
        self.play(first.lines[1].part('555').animate.set_color(ERROR).scale(1.2), run_time=0.5)
        self.play(first.lines[1].part('555').animate.scale(1 / 1.2), run_time=0.3)

        # [V2.8c] 1.1 * 3 lands one tick right of 3.3, outside its catchment
        self.at('One point one times three')
        self.remove(card)
        self.play(FadeOut(VGroup(line, band, stored_name, name, name_label, shortest)))
        product = 1.1 * 3                                     # computed; prints as q02-04 shows
        assert product == math.nextafter(3.3, math.inf)
        ulp3 = Fraction(math.ulp(3.3))
        line3 = FloatLine(Fraction(3.3) - ulp3 * 3 / 2, Fraction(3.3) + ulp3 * 5 / 2, width=11.5, tick_height=0.4)
        line3.move_to([0, -1.6, 0])
        band3 = catchment(line3, 3.3)
        name33 = Text('3.3', font=MONO, font_size=24, color=EXACT).next_to(line3.point(3.3), DOWN, buff=0.36)
        self.play(Create(line3.axis), Create(line3.ticks), FadeIn(band3), FadeIn(name33))
        exact = Fraction(1.1) * 3                             # computed: the exact product of the stored 1.1
        d = line3.diamond(exact)
        d_label = Text('1.1 × 3, exactly', font_size=22, color=FOCUS).next_to(d, UP, buff=0.15)
        self.play(first.type_line(2, run_time=1.0), FadeIn(d, shift=DOWN * 0.2), FadeIn(d_label))
        snap3 = line3.snap(exact)
        self.play(Create(snap3))
        self.at('Its shortest name has to be different')
        long_name = Text(output_line(PRINTS, '1.1 * 3').split('-> ')[1], font=MONO, font_size=24, color=ERROR)
        long_name.next_to(line3.point(product), DOWN, buff=0.36)
        self.play(FadeIn(long_name, shift=UP * 0.1), first.lines[2].part('3.3000000000000003').animate.set_color(ERROR))
        self.play(first.type_line(3, run_time=0.9))
        self.play(first.lines[3].part('False').animate.set_color(ERROR))

        # [V2.8d] the refund: +0.10 +0.20 −0.30 is a tiny positive sliver
        self.at("And here's one that ends up")
        code2 = code_panel(snippet_lines(PRINTS, 9, 13), font_size=18).to_corner(UL, buff=0.3)
        second = Console(snippet_output(PRINTS)[4:], font_size=18).next_to(code2, DOWN, buff=0.25, aligned_edge=LEFT)
        self.play(FadeOut(VGroup(line3, band3, name33, d, d_label, long_name, first, snap3)),
                  FadeTransform(code, code2), FadeIn(second.background))
        refund = output_line(PRINTS, 'refund').split('-> ')[1]
        rows = [('Ten cents', '+$0.10'), ('Twenty cents', '+$0.20'), ('Thirty cents', '-$0.30'), ('-', ''),
                ('Total', refund)]
        slip = receipt(rows, width=4.9, font_size=18, title='REFUND').move_to([4.4, -0.6, 0])
        self.at('Ten cents plus twenty cents')
        self.play(FadeIn(slip.paper), FadeIn(slip.lines[0]))
        self.play(LaggedStart(*[FadeIn(l) for l in slip.lines[1:5]], lag_ratio=0.4), run_time=1.4)
        self.at("It's actually a tiny positive sliver")
        self.play(FadeIn(slip.lines[5]), second.type_line(0, run_time=1.0))
        total_value = slip.lines[5].part(refund)
        self.play(total_value.animate.set_color(ERROR), second.lines[0].part(refund).animate.set_color(ERROR))

        # [V2.8e] the receipt flips to a statement; the balance reads $-0.00
        self.at('Flip its sign')
        self.play(second.type_line(1, run_time=0.8))
        statement_value = output_line(PRINTS, 'on a statement').split('-> ')[1]
        statement = receipt([('Balance', statement_value)], width=4.9, font_size=18, title='STATEMENT')
        statement.move_to(slip)
        self.play(slip.animate.stretch(0.02, 0), run_time=0.4)
        self.remove(slip)
        statement.stretch(0.02, 0)
        self.add(statement)
        self.play(statement.animate.stretch(50, 0), run_time=0.4)
        self.at('You get zero, but a negative zero')
        self.play(second.lines[1].part('-0.0').animate.set_color(ERROR))
        self.at('formatting faithfully prints it')
        self.play(second.type_line(2, run_time=0.9))
        minus = statement.rows[0].part('-')
        ring = Circle(radius=0.22, color=ERROR, stroke_width=4).move_to(minus)
        self.at('Minus zero dollars and zero cents')
        printed = second.lines[2].source.index('$-') + 1
        self.play(Create(ring), minus.animate.set_color(ERROR), second.lines[2].chars(printed, printed + 1).animate.set_color(ERROR))
        self.at('Customers do notice that')
        puzzled = Text('?', font_size=60, color=FOCUS).next_to(statement, UP, buff=0.3).align_to(ring, RIGHT)
        self.play(FadeIn(puzzled, shift=DOWN * 0.3), Wiggle(VGroup(statement, ring), scale_value=1.05), run_time=1.2)
        self.play(ring.animate.scale(1.25).move_to(minus), run_time=0.4)
        self.play(ring.animate.scale(0.8).move_to(minus), run_time=0.4)
        self.finish()


# ---------------------------------------------------------------- 2.9

def recap_icon(k):
    """A small moving picture for each recap line."""
    if k == 0:
        boxes = bit_boxes(12, 0.13)
        s, e, f = groups_of(boxes, (1, 3, 8))
        s.set_stroke(GREY_B, 2)
        e.set_stroke(FOCUS, 2)
        f.set_stroke(STORED, 2)
        return boxes, lambda: Transform(boxes, split_boxes(boxes, (1, 3, 8), 0.12))
    if k == 1:
        axis = Line(LEFT * 0.8, RIGHT * 0.8, color=SCAFFOLD, stroke_width=2)
        ticks = VGroup(*[Line(DOWN * 0.12, UP * 0.12, color=STORED, stroke_width=2).move_to(RIGHT * x)
                         for x in [-0.8 + 0.1 * i for i in range(6)] + [-0.2 + 0.2 * i for i in range(6)]])
        group = VGroup(axis, ticks)
        return group, lambda: Indicate(ticks, color=STORED, scale_factor=1.1)
    if k == 2:
        axis = Line(LEFT * 0.8, RIGHT * 0.8, color=SCAFFOLD, stroke_width=2)
        ticks = VGroup(*[Line(DOWN * 0.12, UP * 0.12, color=STORED, stroke_width=2).move_to(RIGHT * (-0.8 + 0.08 * i))
                         for i in range(6)])
        group = VGroup(axis, ticks)

        def spread():
            target = ticks.copy()
            left = axis.get_left()
            for i, t in enumerate(target):
                t.move_to(left + RIGHT * 0.08 * (2 ** (i * 0.75) - 1) * 1.3)
            return Transform(ticks, target)
        return group, spread
    if k == 3:
        cent = penny(0.26)
        cross = crossmark(size=0.5)
        group = VGroup(cent, cross.set_opacity(0))
        return group, lambda: AnimationGroup(cent.animate.set_opacity(0.3), cross.animate.set_opacity(1))
    if k == 4:
        axis = Line(LEFT * 0.8, RIGHT * 0.8, color=SCAFFOLD, stroke_width=2)
        ticks = VGroup(*[Line(DOWN * 0.12, UP * 0.12, color=STORED, stroke_width=3).move_to(RIGHT * x) for x in (-0.6, 0.6)])
        d = Square(0.14).rotate(PI / 4).set_fill(FOCUS, 1).set_stroke(width=0).move_to(UP * 0.3 + RIGHT * 0.25)
        group = VGroup(axis, ticks, d)
        return group, lambda: d.animate.move_to(ticks[1].get_top() + UP * 0.1)
    short = Text('0.1', font=MONO, font_size=22, color=FOCUS)
    tail = Text('…555', font=MONO, font_size=22, color=ERROR).next_to(short, RIGHT, buff=0.05)
    group = VGroup(short, tail.set_opacity(0))
    return group, lambda: tail.animate.set_opacity(1)


class Segment_2_9(Segment):
    """Recap and challenge (q02-05), the QR wall and the episode 3 teaser."""
    EPISODE, SEGMENT = 2, '2.9'

    def construct(self):
        # [V2.9a] the recap column builds
        items = ['64 bits = sign + exponent + 52 fraction bits (+1 implied)',
                 'same number of doubles between every power of two',
                 'gaps double as numbers double',
                 '64-bit floats lose cents near $70 trillion; 32-bit near $131,072',
                 'every operation rounds to nearest, ties to even',
                 'print shows the shortest name, not the value']
        cues = ['A double is a sign', 'The bits are a sliding window', 'every doubling of a number',
                'loses its grip on cents', 'Every operation rounds', 'And print shows you']
        rows = VGroup()
        for k, (text, cue) in enumerate(zip(items, cues)):
            y = 3.05 - 1.2 * k
            icon, act = recap_icon(k)
            icon.move_to([-5.6, y, 0])
            words = fit(Text(text, font_size=26), 10.8).move_to([0, y, 0]).align_to([-4.4, 0, 0], LEFT)
            self.at(cue)
            self.play(FadeIn(icon, shift=RIGHT * 0.2), FadeIn(words, shift=RIGHT * 0.2), run_time=0.6)
            self.play(act(), run_time=0.8)
            rows.add(VGroup(icon, words))

        # [V2.9b] the challenge: q02-05's code and output, and its QR card
        self.at("Here's a challenge")
        self.play(FadeOut(rows))
        code = code_panel(snippet_lines(CHALLENGE, 4, 9), font_size=18).to_corner(UL, buff=0.3)
        out = output_console(CHALLENGE, font_size=18).next_to(code, DOWN, buff=0.25, aligned_edge=LEFT)
        card = qr_card('q02-05')
        self.play(FadeIn(code), FadeIn(out.background), FadeIn(card, shift=UP * 0.2))
        self.play(Create(line_highlight(code, 0)))
        self.at('finds two to the forty-seventh')
        self.play(out.type_line(0, run_time=1.4))
        self.play(out.lines[0].part('2**47').animate.set_color(FOCUS))
        tries = []
        hint = snippet_source(CHALLENGE).splitlines()[2]          # "# Then try other amounts: 0.001 (a mill), ..."
        for value in ('0.001', '1.00', '0.05'):
            assert value in hint
            row = MonoLine(f'AMOUNT = {value:<6}  →  2**?', font_size=22, color=GREY_A)
            row.part('?').set_color(FOCUS)
            tries.append(row)
        stack = stack_lines(tries, spacing=2.2)
        stack.next_to(out, DOWN, buff=0.45).align_to(out, LEFT).shift(RIGHT * 0.25)
        for row, cue in zip(tries, ('Try a thousandth of a dollar', 'Try a whole dollar', 'Try five cents')):
            self.at(cue)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.at('predict the power of two')
        self.play(LaggedStart(*[Indicate(r.part('?'), color=FOCUS, scale_factor=1.6) for r in tries], lag_ratio=0.3))

        # [V2.9c] the QR wall, held 10 seconds
        self.at('Hint:')
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)
        wall = qr_wall(episode_qr_ids(2))
        self.add(wall)
        start = self.renderer.time
        self.wait(10)

        # [V2.9d] teaser: cents drop into a jar, the count races to a million, the total flickers
        self.at('Next time')
        self.remove(wall)
        assert self.renderer.time - start >= 9.99
        card = end_card('Episode 3', 'Where it bites').to_edge(UP, buff=0.5)
        pot = jar(1.8, 2.0).move_to(LEFT * 3.6 + DOWN * 1.2)
        count = number(0, font_size=40, color=MONEY, commas=True)
        unit = Text('cents', font_size=30, color=MONEY)
        total_name = Text('total', font_size=30, color=SCAFFOLD)
        self.play(FadeIn(card, shift=DOWN * 0.2), FadeIn(pot))
        # Running totals computed here: add 0.01 a million times, as q03-01 does.
        checkpoints = sorted({int(round(10 ** (i / 5))) for i in range(31)})
        totals, total = {}, 0.0
        marks = set(checkpoints)
        for n in range(1, 1_000_001):
            total += 0.01
            if n in marks:
                totals[n] = repr(total)
        assert totals[1_000_000] in output_line(EP03_CENTS, '1,000,000 cents')
        shown = code_text(totals[1], font_size=34, color=WHITE)

        def place():
            count.move_to([0.6, -0.6, 0], aligned_edge=LEFT)
            unit.next_to(count, RIGHT, buff=0.2, aligned_edge=DOWN)
            total_name.move_to([0.6, -1.6, 0], aligned_edge=LEFT)
            shown.next_to(total_name, RIGHT, buff=0.3)

        place()
        self.add(count, unit, total_name, shown)
        pile = VGroup()
        for i, n in enumerate(checkpoints):
            cent = penny(0.22).move_to(pot.get_top() + UP * 1.0)
            spot = pot[0].get_bottom() + UP * (0.28 + 0.07 * min(len(pile), 14)) + RIGHT * 0.3 * ((len(pile) % 3) - 1)
            self.play(cent.animate.move_to(spot), run_time=max(0.08, 0.45 * 0.8 ** i), rate_func=rate_functions.ease_in_quad)
            if len(pile) < 15:
                pile.add(cent)
            else:
                self.remove(cent)
            count.set_value(n)
            self.remove(shown)
            shown = code_text(totals[n], font_size=34, color=WHITE)
            place()
            self.add(shown)
        tail = shown.chars(len('10000.0000001'))
        self.play(tail.animate.set_color(ERROR), run_time=0.4)
        self.finish(extra=3.0)

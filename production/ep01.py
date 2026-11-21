"""Episode 1 · The dime that doesn't exist. One Scene per script segment.

    python3 production/render.py 1 [-ql] [segment ...]

Shot ids in comments ([V1.1a] ...) refer to episodes/01-the-dime-that-doesnt-exist.md. Code
panels and console lines come from snippets/ep01/ (q01-01 ... q01-05); values no snippet prints
(binary digits, gaps, positions on the float line) are computed below with Fraction and math.
"""
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa: E402,F403

Q1 = 'ep01/01-ten-plus-twenty.py'
Q2 = 'ep01/02-ten-cents-in-binary.py'
Q3 = 'ep01/03-what-is-stored.py'
Q4 = 'ep01/04-which-cents-are-exact.py'
Q5 = 'ep01/05-challenge-denominators.py'


# ---------------------------------------------------------------- local helpers

def label(text, font_size=24, color=WHITE, **kwargs):
    """Plain Text without ligatures, so text_part can index its glyphs."""
    return Text(text, font_size=font_size, color=color, disable_ligatures=True, **kwargs)


def text_part(text, source, needle, occurrence=0):
    """Glyphs of `needle` inside a Text built from `source`. With ligatures disabled, Text keeps
    a blank glyph for every space (but not for newlines); otherwise it drops all whitespace."""
    start = -1
    for _ in range(occurrence + 1):
        start = source.index(needle, start + 1)
    if len(text) == len(source.replace('\n', '')):
        first, count = len(source[:start].replace('\n', '')), len(needle.replace('\n', ''))
    else:
        first, count = len(re.sub(r'\s', '', source[:start])), len(re.sub(r'\s', '', needle))
    return VGroup(*text[first:first + count])


def type_code(code, run_time=2.0):
    """Type a code_panel's lines out, glyph by glyph (show code.background first)."""
    lines = [line for line in code.code_lines if len(line)]
    per = run_time / max(1, len(lines))
    return Succession(*[LaggedStart(*[FadeIn(g, run_time=0.05) for g in line], lag_ratio=1.0, run_time=per)
                        for line in lines])


def pulse(scene, mob, color=None, factor=1.4, run_time=0.35):
    """Grow, colour and settle back: the 'pulses RED' / 'glows' beat."""
    grow = mob.animate.scale(factor)
    if color is not None:
        grow = grow.set_color(color)
    scene.play(grow, run_time=run_time)
    scene.play(mob.animate.scale(1 / factor), run_time=run_time)


def thud(scene, mob):
    """A landing bump with two little impact strokes."""
    marks = VGroup(*[Line(ORIGIN, side * 0.3 + DOWN * 0.1, color=GREY_B, stroke_width=3)
                     .next_to(mob, side, buff=0.08) for side in (LEFT, RIGHT)])
    scene.play(mob.animate.shift(DOWN * 0.12), FadeIn(marks), run_time=0.12, rate_func=rate_functions.ease_in_quad)
    scene.play(mob.animate.shift(UP * 0.12), FadeOut(marks), run_time=0.25)


def binary_digits(x, count):
    """The same doubling as q01-02, computed here for the drawings (exact, with Fraction)."""
    bits = ''
    for _ in range(count):
        x = x * 2
        bit = int(x)
        bits += str(bit)
        x = x - bit
    return bits


def magnifier(radius=0.45):
    glass = Circle(radius=radius, color=FOCUS, stroke_width=5).set_fill(FOCUS, 0.08)
    handle = Line(ORIGIN, (DR * 0.55), color=FOCUS, stroke_width=8)
    handle.move_to(glass.get_center() + DR * (radius * 0.707 + 0.2))
    return VGroup(glass, handle)


def place_boxes(names, size=1.15, font_size=26, point_after=1, gap=0.18, label_above=True):
    """Place-value boxes with their names and a decimal point after box `point_after`."""
    boxes = VGroup(*[Square(size).set_stroke(SCAFFOLD, 2) for _ in names])
    boxes.arrange(RIGHT, buff=gap)
    if point_after:
        for b in boxes[point_after:]:
            b.shift(RIGHT * 0.35)
    names_g = VGroup(*[label(n, font_size=font_size, color=SCAFFOLD).next_to(b, UP if label_above else DOWN, buff=0.15)
                       for n, b in zip(names, boxes)])
    dot = Dot(radius=0.08, color=WHITE)
    if point_after:
        dot.move_to((boxes[point_after - 1].get_corner(DR) + boxes[point_after].get_corner(DL)) / 2 + UP * 0.12)
    else:
        dot.set_opacity(0)
    group = VGroup(boxes, names_g, dot)
    group.boxes, group.names, group.dot = boxes, names_g, dot
    return group


def unit_bar(width, height=0.4, color=SCAFFOLD):
    return Rectangle(width=width, height=height).set_stroke(color, 2)


def fill_piece(bar, start, length, color=STORED, opacity=0.85):
    """A filled rectangle covering [start, start+length] (fractions of the bar)."""
    w = bar.width * float(length)
    piece = Rectangle(width=max(w, 0.001), height=bar.height).set_fill(color, opacity).set_stroke(width=0)
    piece.move_to(bar.get_left() + RIGHT * (bar.width * float(start) + w / 2))
    return piece


# ---------------------------------------------------------------- 1.1

class Segment_1_1(Segment):
    """Cold open: 0.10 + 0.20 (q01-01)."""
    EPISODE, SEGMENT = 1, '1.1'

    def construct(self):
        # [V1.1a] a dime and a 20-cent coin slide together; a plus sign appears
        dime, twenty = coin('10¢', 0.9), coin('20¢', 0.9)
        dime.move_to(LEFT * 7.5)
        twenty.move_to(RIGHT * 7.5)
        self.play(dime.animate.move_to(LEFT * 1.6), twenty.animate.move_to(RIGHT * 1.6), run_time=1.4,
                  rate_func=rate_functions.ease_out_cubic)
        plus = Text('+', font_size=80)
        self.play(FadeIn(plus, scale=0.4), run_time=0.5)
        self.at('You know the answer')
        coins = VGroup(dime, plus, twenty)
        equals = Text('=', font_size=80)
        thirty = coin('30¢', 0.9)
        self.play(coins.animate.shift(LEFT * 2.2))
        VGroup(equals, thirty).arrange(RIGHT, buff=0.6).next_to(coins, RIGHT, buff=0.6)
        self.play(FadeIn(equals), FadeIn(thirty, scale=0.6))

        # [V1.1b] the coins dissolve into code; the console prints the first line
        self.at('But ask Python')
        code = code_panel(snippet_lines(Q1, 4, 10), font_size=24).to_corner(UL, buff=0.35)
        out = output_console(Q1, font_size=26)
        out.next_to(code, DOWN, buff=0.3, aligned_edge=LEFT)
        coins.add(equals, thirty)
        self.play(coins.animate.scale(0.25).move_to(code.get_center()).set_opacity(0), FadeIn(code.background),
                  run_time=0.9)
        self.remove(coins)
        self.play(type_code(code, run_time=1.6))
        self.play(FadeIn(out.background), run_time=0.4)
        self.at('zero point three, then fifteen zeros')
        self.play(out.type_line(0, run_time=1.4))
        self.at('then a four')
        pulse(self, out.part(0, '4'), ERROR, factor=1.8)

        # [V1.1c] the comparison prints False; the QR code
        self.at('Ask whether that equals thirty cents')
        card = qr_card('q01-01')
        self.play(FadeIn(card, shift=UP * 0.2), out.type_line(1, run_time=1.0))
        self.at('it says: no')
        pulse(self, out.part(1, 'False'), ERROR, factor=1.5)

        # [V1.1d] the quarter and the half: 0.75 and True in green
        self.at('Now try a quarter')
        self.play(out.type_line(2, run_time=1.0))
        self.at('Seventy-five cents, exactly')
        pulse(self, out.part(2, '0.75'), EXACT, factor=1.3)
        self.at('And yes, they')
        self.play(out.type_line(3, run_time=1.0))
        pulse(self, out.part(3, 'True'), EXACT, factor=1.4)

        # Two kinds of amount: a cross for the first pair, a tick for the second
        self.at('So the computer isn')
        self.play(FadeOut(card))
        self.at('Some amounts behave perfectly')
        top = VGroup(out.lines[0], out.lines[1])
        bottom = VGroup(out.lines[2], out.lines[3])
        cross = crossmark(size=0.45).next_to(out.background, RIGHT, buff=0.35).set_y(top.get_y())
        tick = checkmark(size=0.45).next_to(out.background, RIGHT, buff=0.35).set_y(bottom.get_y())
        self.play(Create(tick), run_time=0.5)
        self.play(Create(cross), run_time=0.5)

        # Predict which kind a price is: four price tags, each with a question mark
        self.at('predict which kind it is')
        tags = VGroup(*[price_tag(t, font_size=28) for t in ('$0.10', '$0.25', '$0.30', '$0.75')])
        tags.arrange_in_grid(rows=2, cols=2, buff=(0.5, 0.9)).move_to([4.7, -1.75, 0])
        marks = VGroup(*[Text('?', font_size=34, color=FOCUS).next_to(t, UP, buff=0.1) for t in tags])
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.3) for t in tags], lag_ratio=0.25), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(m, scale=0.5) for m in marks], lag_ratio=0.2), run_time=0.8)
        self.play(LaggedStart(*[Wiggle(m) for m in marks], lag_ratio=0.15), run_time=1.0)

        # The trouble is not the addition but the first line
        self.at('surprising part')
        self.play(FadeOut(VGroup(tags, marks, tick, cross)))
        self.at('happen when we added')
        box = line_highlight(code, 2, color=ERROR)
        self.play(Create(box))
        self.at('It happened earlier')
        new_box = line_highlight(code, 0)
        self.play(Transform(box, new_box))
        self.at('when we wrote ten cents')
        ten = code.code_lines[0][2:]
        pulse(self, ten, FOCUS, factor=1.5, run_time=0.4)

        # [V1.1e] the dime returns alone and is erased, leaving a dashed outline
        self.at('Because your computer cannot store ten cents')
        self.play(FadeOut(VGroup(code, out, box)))
        dime = coin('10¢', 1.3)
        self.play(FadeIn(dime, scale=0.6))
        self.at('simply impossible')
        outline = DashedVMobject(Circle(radius=1.3, color=MONEY, stroke_width=3), num_dashes=36).move_to(dime)
        self.play(FadeOut(dime, scale=0.9), FadeIn(outline), run_time=2.0)
        self.at('The dime')
        self.play(outline.animate.set_stroke(opacity=0.45), run_time=1.0)
        self.finish()


# ---------------------------------------------------------------- 1.2

class Segment_1_2(Segment):
    """A number you can't write down: one third in decimal, and which fractions finish."""
    EPISODE, SEGMENT = 1, '1.2'

    def construct(self):
        # [V1.2a] 1/3 and its decimal digits, one at a time
        third = label('1/3', font_size=64, color=FOCUS)
        start_third = third.copy().scale(1.6)
        self.play(FadeIn(start_third, scale=0.7), run_time=0.8)
        self.at('One third.')
        third.move_to([-5.2, 2.9, 0])
        self.play(ReplacementTransform(start_third, third))
        arrow = Arrow(third.get_right(), third.get_right() + RIGHT * 1.4, buff=0.2, color=SCAFFOLD)
        digits = MonoLine('0.3333333…', font_size=56, color=WHITE)
        digits.set_anchor(arrow.get_end() + RIGHT * 0.35)
        self.play(GrowArrow(arrow), run_time=0.5)
        self.at('zero point three three three')
        self.play(FadeIn(digits.glyphs[:3], shift=LEFT * 0.1), run_time=0.4)
        for k in (3, 4):
            self.play(FadeIn(digits.glyphs[k], scale=1.4), run_time=0.35)
        self.at('and so on, forever')
        self.play(LaggedStart(*[FadeIn(g, scale=1.3) for g in digits.glyphs[5:]], lag_ratio=0.5), run_time=1.6)

        # [V1.2b] a pie of one third, filled with 3 tenths, 3 hundredths, 3 thousandths
        self.at('You can write as many')
        centre = np.array([-3.4, -0.25, 0])
        radius = 1.55
        disc = Circle(radius=radius).set_stroke(GREY_D, 2).move_to(centre)
        third_slice = Sector(radius=radius, angle=TAU / 3, start_angle=PI / 2 - TAU / 3).move_to(centre, aligned_edge=ORIGIN)
        third_slice.shift(centre - third_slice.get_arc_center())
        third_slice.set_fill(opacity=0).set_stroke(FOCUS, 3)
        boxes = place_boxes(['tenths', 'hundredths', 'thousandths'], size=0.95, font_size=22, point_after=0,
                            gap=1.15, label_above=False)
        boxes.next_to(disc, DOWN, buff=0.45)
        boxes.names.next_to(boxes.boxes, DOWN, buff=0.12)
        for n, b in zip(boxes.names, boxes.boxes):
            n.set_x(b.get_x())
        self.play(Create(disc), Create(third_slice), FadeIn(boxes), run_time=1.0)

        def wedge(start, angle, color):
            w = Sector(radius=radius, angle=angle, start_angle=start).set_fill(color, 0.85)
            w.set_stroke(color, 2)
            return w.shift(centre - w.get_arc_center())

        filled = None
        gap_label = None
        threes = VGroup()
        for k, phrase in enumerate(('Three tenths is short', 'Thirty-three hundredths', 'Every digit shrinks')):
            if phrase:
                self.at(phrase)
            value = Fraction(int('3' * (k + 1)), 10 ** (k + 1))      # 0.3, 0.33, 0.333
            angle = float(value) * TAU
            new_fill = wedge(PI / 2 - angle, angle, STORED)
            sliver = wedge(PI / 2 - TAU / 3, TAU / 3 - angle, ERROR)
            three = MonoLine('3', font_size=44, color=STORED)
            three.move_to(boxes.boxes[k])
            gap = Fraction(1, 3) - value                             # 1/30, 1/300, 1/3000
            new_gap = VGroup(label('short by', font_size=26, color=SCAFFOLD),
                             label(f'{gap.numerator}/{gap.denominator}', font_size=36, color=ERROR))
            new_gap.arrange(DOWN, buff=0.15).move_to([0.6, 0.2, 0])
            threes.add(three)
            anims = [FadeIn(three, shift=DOWN * 0.6)]
            if filled is None:
                filled = VGroup(new_fill, sliver)
                anims += [FadeIn(filled), FadeIn(new_gap)]
                gap_label = new_gap
            else:
                anims += [Transform(filled, VGroup(new_fill, sliver)), Transform(gap_label, new_gap)]
            self.play(*anims, run_time=0.8)
        self.at('no digit closes it')
        self.play(Indicate(filled[1], color=ERROR, scale_factor=1.15), Indicate(gap_label[1], color=ERROR))

        # Place values: a whole cut into ten, and one tenth cut into ten again
        self.at('the place values we chose')
        self.play(LaggedStart(*[Indicate(n, color=FOCUS) for n in boxes.names], lag_ratio=0.3), run_time=1.4)
        self.at('Decimal digits count tenths')
        self.play(FadeOut(VGroup(disc, third_slice, filled, gap_label, boxes, threes)))
        strip = unit_bar(11, 0.55).move_to(UP * 0.9)
        zero_one = VGroup(label('0', 22, SCAFFOLD).next_to(strip, LEFT, buff=0.15),
                          label('1', 22, SCAFFOLD).next_to(strip, RIGHT, buff=0.15))
        self.play(Create(strip), FadeIn(zero_one))
        self.at('pieces made by cutting')
        cuts = VGroup(*[Line(strip.get_bottom() + UP * 0, strip.get_top(), color=SCAFFOLD, stroke_width=2)
                        .set_x(strip.get_left()[0] + strip.width * i / 10) for i in range(1, 10)])
        tenths = label('tenths', 22, SCAFFOLD).next_to(strip, UP, buff=0.15).align_to(strip, LEFT)
        self.play(LaggedStart(*[Create(c) for c in cuts], lag_ratio=0.12), FadeIn(tenths), run_time=1.2)
        self.at('then ten again')
        piece = fill_piece(strip, Fraction(3, 10), Fraction(1, 10), color=GREY_D, opacity=0.6)
        zoom = unit_bar(11, 0.55).move_to(DOWN * 1.4)
        zoom_cuts = VGroup(*[Line(zoom.get_bottom(), zoom.get_top(), color=SCAFFOLD, stroke_width=2)
                             .set_x(zoom.get_left()[0] + zoom.width * i / 10) for i in range(1, 10)])
        guides = VGroup(DashedLine(piece.get_corner(DL), zoom.get_corner(UL), color=GREY_D),
                        DashedLine(piece.get_corner(DR), zoom.get_corner(UR), color=GREY_D))
        ends = VGroup(label('0.3', 22, SCAFFOLD).next_to(zoom, LEFT, buff=0.15),
                      label('0.4', 22, SCAFFOLD).next_to(zoom, RIGHT, buff=0.15))
        hundredths = label('hundredths', 22, SCAFFOLD).next_to(zoom, DOWN, buff=0.15).align_to(zoom, LEFT)
        self.play(FadeIn(piece), Create(guides), TransformFromCopy(piece, zoom), run_time=0.7)
        self.play(LaggedStart(*[Create(c) for c in zoom_cuts], lag_ratio=0.12), FadeIn(ends), FadeIn(hundredths),
                  run_time=0.8)

        # One third falls between the marks, at every level
        self.at('One third asks you to cut')
        thirds = VGroup(*[Line(strip.get_bottom() + DOWN * 0.15, strip.get_top() + UP * 0.15, color=FOCUS, stroke_width=4)
                          .set_x(strip.get_left()[0] + strip.width * k / 3) for k in (1, 2)])
        third_tag = label('1/3', 26, FOCUS).next_to(thirds[0], UP, buff=0.1)
        self.play(Create(thirds), FadeIn(third_tag), run_time=0.8)
        self.at('you cannot build a third')
        x = (Fraction(1, 3) - Fraction(3, 10)) * 10                # where 1/3 falls inside 0.3 .. 0.4
        mark = Line(zoom.get_bottom() + DOWN * 0.15, zoom.get_top() + UP * 0.15, color=FOCUS, stroke_width=4)
        mark.set_x(zoom.get_left()[0] + zoom.width * float(x))
        between = fill_piece(zoom, Fraction(3, 10), Fraction(1, 10), color=ERROR, opacity=0.45)
        self.play(TransformFromCopy(thirds[0], mark), run_time=0.8)
        self.play(FadeIn(between), Indicate(mark, color=FOCUS))

        # [V1.2c] two columns: fractions that end, and fractions that repeat forever
        self.at('So which fractions do come out even')
        self.play(FadeOut(VGroup(strip, zero_one, cuts, tenths, piece, zoom, zoom_cuts, guides, ends, hundredths,
                                 thirds, third_tag, mark, between)),
                  VGroup(third, arrow, digits).animate.scale(0.6).to_corner(UL, buff=0.35))
        heads = VGroup(label('ends', 34, EXACT).move_to([-4.2, 2.8, 0]),
                       label('repeats forever', 34, ERROR).move_to([3.0, 2.8, 0]))
        rule_line = Line(UP * 3.1, DOWN * 1.2, color=GREY_D).set_x(-0.4)
        self.play(FadeIn(heads), Create(rule_line))
        left = ['1/2 = 0.5', '1/4 = 0.25', '1/5 = 0.2', '1/8 = 0.125', '1/20 = 0.05']
        right = ['1/3', '1/6', '1/7', '1/9', '1/12']
        left_f = ['2', '2×2', '5', '2×2×2', '2×2×5']
        right_f = ['3', '2×3', '7', '3×3', '2×2×3']
        ys = [2.05 - 0.7 * i for i in range(5)]
        lrows = VGroup(*[label(t, 34).move_to([-6.2, y, 0], aligned_edge=LEFT) for t, y in zip(left, ys)])
        rrows = VGroup(*[label(t, 34).move_to([0.8, y, 0], aligned_edge=LEFT) for t, y in zip(right, ys)])
        lfac = VGroup(*[label(t, 34, SCAFFOLD).move_to([-2.6, y, 0], aligned_edge=LEFT) for t, y in zip(left_f, ys)])
        rfac = VGroup(*[label(t, 34, SCAFFOLD).move_to([3.6, y, 0], aligned_edge=LEFT) for t, y in zip(right_f, ys)])
        for row, phrase in zip(lrows, ('One half', 'one quarter', 'one fifth', 'one eighth', 'one twentieth')):
            self.at(phrase)
            self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.3) for r in rrows], lag_ratio=0.15), run_time=0.6)

        # [V1.2d] factor the denominators
        self.at('Factor their denominators')
        self.play(LaggedStart(*[FadeIn(f, shift=LEFT * 0.2) for f in [*lfac, *rfac]], lag_ratio=0.1), run_time=1.6)
        self.at('only ever find twos and fives')
        self.play(*[f.animate.set_color(EXACT) for f in lfac], run_time=0.6)

        # [V1.2e] the rule types itself
        self.at('ten is two times five')
        rule = rule_ten()
        rule.move_to(DOWN * 2.6)
        self.play(AddTextLetterByLetter(rule, run_time=3.0))
        self.at('Anything with a three')
        bad = VGroup(*[g for f, src in zip(rfac, right_f) for g, ch in zip(f, src.replace('×', 'x')) if ch in '37'])
        self.play(bad.animate.set_color(ERROR).scale(1.35), run_time=0.5)
        self.play(bad.animate.scale(1 / 1.35), run_time=0.4)
        self.play(LaggedStart(*[r.animate.set_color(ERROR) for r in rrows], lag_ratio=0.1),
                  LaggedStart(*[r.animate.set_color(EXACT) for r in lrows], lag_ratio=0.1), run_time=1.0)
        self.at('Hold on to that rule')
        frame = SurroundingRectangle(rule, color=FOCUS, buff=0.18, corner_radius=0.1)
        self.play(Create(frame))
        self.finish()


RULE_TEN = 'Base ten can only finish fractions whose denominators\nare built from 2s and 5s, because 10 = 2 × 5.'
RULE_TWO = 'Base two can only finish fractions whose denominators\nare powers of 2.'


def rule_ten():
    return label(RULE_TEN, font_size=30, line_spacing=0.9)


def rule_two():
    return label(RULE_TWO, font_size=30, line_spacing=0.9)


# ---------------------------------------------------------------- 1.3

BINARY_PLACES = ['1', '½', '¼', '⅛', '1/16', '1/32']


class Segment_1_3(Segment):
    """Counting in halves: binary place values, and which fractions binary can finish."""
    EPISODE, SEGMENT = 1, '1.3'

    def construct(self):
        # [V1.3a] decimal place-value boxes morph into binary ones
        decimal = place_boxes(['ones', 'tenths', 'hundredths'], size=1.1, font_size=24, point_after=1, gap=0.5)
        decimal.move_to(DOWN * 0.2)
        self.play(FadeIn(decimal, shift=UP * 0.2))
        self.at('They count in twos')
        binary = place_boxes(BINARY_PLACES, size=1.1, font_size=30, point_after=1, gap=0.22)
        binary.move_to(DOWN * 0.2)
        self.play(ReplacementTransform(decimal, binary), run_time=1.2)
        for k, phrase in enumerate(('a ones place', 'a halves place', 'a quarters place', 'an eighths place',
                                    'a sixteenths place')):
            self.at(phrase)
            self.play(Indicate(binary.names[k], color=FOCUS, scale_factor=1.3),
                      binary.boxes[k].animate.set_stroke(FOCUS, 3), run_time=0.5)
            self.play(binary.boxes[k].animate.set_stroke(SCAFFOLD, 2), run_time=0.2)

        # [V1.3b] a bar of length one: light ½, then ¼: 0.11 in binary = ¾
        self.at('Each place is half the one before')
        bar = unit_bar(8.0, 0.45).move_to(UP * 2.85)
        ends = VGroup(label('0', 22, SCAFFOLD).next_to(bar, LEFT, buff=0.15),
                      label('1', 22, SCAFFOLD).next_to(bar, RIGHT, buff=0.15))
        self.play(binary.animate.move_to(UP * 1.2), Create(bar), FadeIn(ends), run_time=0.7)
        state = {'digits': VGroup(), 'fill': VGroup(), 'lit': []}

        def show(bits, run_time=0.8):
            """Write bits (ones digit first) into the boxes, light the 1s and fill the bar."""
            digits = VGroup(*[MonoLine(b, font_size=40, color=STORED if b == '1' else GREY_B).move_to(binary.boxes[i])
                              for i, b in enumerate(bits)])
            fill, start = VGroup(), Fraction(0)
            for i, b in enumerate(bits):
                if b == '1' and i > 0:
                    fill.add(fill_piece(bar, start, Fraction(1, 2 ** i)))
                    start += Fraction(1, 2 ** i)
            anims = [FadeIn(digits, shift=DOWN * 0.3), LaggedStart(*[GrowFromEdge(p, LEFT) for p in fill], lag_ratio=0.6)]
            if len(state['digits']):
                anims += [FadeOut(state['digits']), FadeOut(state['fill'])]
            anims += [binary.boxes[i].animate.set_fill(STORED, 0.2 if b == '1' and i else 0) for i, b in enumerate(bits)]
            anims += [b.animate.set_fill(opacity=0) for b in binary.boxes[len(bits):]]
            self.play(*anims, run_time=run_time)
            state['digits'], state['fill'] = digits, fill
            return digits, fill

        show('01', run_time=0.6)
        show('011', run_time=0.6)
        three_q = label('0.11 in binary = ¾', 26, STORED).next_to(bar, UP, buff=0.12)
        self.play(FadeIn(three_q, shift=DOWN * 0.1), run_time=0.4)

        # [V1.3c] examples fill their bars: ½, ¼, ⅜, ⅝
        examples = [('So zero point one, in binary', '01', '0.1₂ = ½'),
                    ('Zero point zero one means', '001', '0.01₂ = ¼'),
                    ('Zero point zero one one', '0011', '0.011₂ = ⅜'),
                    ('Now apply the same rule', '0101', '0.101₂ = ⅝')]
        slots = [np.array([x, y, 0]) for y in (-1.15, -2.55) for x in (-3.4, 3.4)]
        records = VGroup()
        for k, ((phrase, bits, text), slot) in enumerate(zip(examples, slots)):
            self.at(phrase)
            if k == 1:
                self.play(FadeOut(three_q), run_time=0.3)
            digits, fill = show(bits)
            mini = unit_bar(2.6, 0.32).move_to(slot + RIGHT * 1.35)
            mini_fill = VGroup(*[fill_piece(mini, (p.get_left()[0] - bar.get_left()[0]) / bar.width,
                                            p.width / bar.width) for p in fill])
            tag = label(text, 30).move_to(slot + LEFT * 1.25)
            record = VGroup(tag, mini, mini_fill)
            self.play(TransformFromCopy(fill, mini_fill), FadeIn(mini), FadeIn(tag, shift=DOWN * 0.2), run_time=0.8)
            records.add(record)

        # [V1.3d] the rule returns: ten crossed out, two written in
        self.at('Decimal could only finish')
        self.play(FadeOut(VGroup(binary, bar, ends, state['digits'], state['fill'], records)))
        rule = rule_ten().move_to(UP * 2.6)
        self.play(FadeIn(rule, shift=DOWN * 0.2))
        base10 = VGroup(label('base ten', 26, SCAFFOLD), label('10 = 2 × 5', 48)).arrange(DOWN, buff=0.25)
        base2 = VGroup(label('base two', 26, SCAFFOLD), label('2 = 2', 48, STORED)).arrange(DOWN, buff=0.25)
        base10.move_to([-3.2, -0.4, 0])
        base2.move_to([3.2, -0.4, 0])
        self.play(FadeIn(base10, shift=UP * 0.2))
        self.at('Binary is built from two alone')
        self.play(FadeIn(base2, shift=UP * 0.2), Indicate(text_part(base10[1], '10 = 2 × 5', '5'), color=ERROR))
        ten = text_part(rule, RULE_TEN, 'ten')
        strike = Line(ten.get_left() + LEFT * 0.05, ten.get_right() + RIGHT * 0.05, color=ERROR, stroke_width=5)
        two = label('two', 30, STORED).next_to(ten, UP, buff=0.12)
        self.play(Create(strike), run_time=0.4)
        self.play(FadeIn(two, shift=DOWN * 0.2), run_time=0.5)
        self.at('So binary can only finish')
        new_rule = rule_two().move_to(UP * 2.6)
        text_part(new_rule, RULE_TWO, 'two').set_color(STORED)
        self.play(FadeOut(VGroup(strike, two)), TransformMatchingShapes(rule, new_rule), run_time=1.4)
        self.play(Circumscribe(base2, color=STORED), run_time=1.0)
        rule = new_rule

        # [V1.3e] the columns return, re-sorted for base two
        self.at('halves, quarters, eighths')
        heads = VGroup(label('ends in binary', 32, EXACT).move_to([-3.3, 1.45, 0]),
                       label('repeats forever', 32, ERROR).move_to([3.0, 1.45, 0]))
        divider = Line(UP * 1.75, DOWN * 3.5, color=GREY_D).set_x(-0.4)
        pitch = 0.56
        ys = [0.8 - pitch * i for i in range(8)]
        lefts = {t: label(t, 30, EXACT).move_to([-4.3, y, 0], aligned_edge=LEFT)
                 for t, y in zip(['1/2', '1/4', '1/5', '1/8', '1/20'], ys)}
        lefts['1/5'].set_color(WHITE)
        lefts['1/20'].set_color(WHITE)
        rights = [label(t, 30, ERROR).move_to([2.4, y, 0], aligned_edge=LEFT)
                  for t, y in zip(['1/3', '1/6', '1/7', '1/9', '1/12'], ys)]
        self.play(FadeOut(base10), FadeOut(base2), run_time=0.4)
        self.play(FadeIn(heads), Create(divider),
                  LaggedStart(*[FadeIn(m) for m in [*lefts.values(), *rights]], lag_ratio=0.06), run_time=1.4)
        self.at('One fifth?')
        self.play(Indicate(lefts['1/5'], color=ERROR))
        self.at('That has a five')
        self.play(lefts['1/5'].animate.move_to([2.4, ys[5], 0], aligned_edge=LEFT).set_color(ERROR),
                  lefts['1/8'].animate.set_y(ys[2]), lefts['1/20'].animate.set_y(ys[3]), run_time=1.0)
        self.at('One twentieth?')
        self.play(lefts['1/20'].animate.move_to([2.4, ys[6], 0], aligned_edge=LEFT).set_color(ERROR), run_time=1.0)
        self.at('And one tenth')
        tenth = label('1/10', 34, MONEY).move_to([2.4, 3.6, 0], aligned_edge=LEFT)
        tenth.set_x(2.4 + tenth.width / 2)
        self.play(FadeOut(rule, shift=UP * 0.3), FadeIn(tenth, shift=DOWN * 0.3))
        self.at('It has a five in it')
        self.play(tenth.animate.move_to([2.4, ys[7], 0], aligned_edge=LEFT), run_time=0.6,
                  rate_func=rate_functions.ease_in_quad)
        thud(self, tenth)

        # one tenth in binary is our one third in decimal
        self.at('one tenth is our one third')
        bits_1_10 = output_line(Q2, '1/10').split('= ')[1][:15] + '…'      # from q01-02's output
        pair = VGroup(MonoLine('1/3  = 0.3333333…', font_size=26, color=FOCUS),
                      MonoLine('1/10 = ' + bits_1_10, font_size=26, color=MONEY))
        notes = VGroup(label('in decimal', 22, SCAFFOLD), label('in binary', 22, SCAFFOLD))
        for note, line, y in zip(notes, pair, (-1.45, -2.6)):
            note.move_to([-6.4, y, 0], aligned_edge=LEFT)
            line.set_anchor([-6.4, y - 0.45, 0])
        self.play(FadeIn(pair[0]), FadeIn(notes[0]))
        self.play(FadeIn(pair[1]), FadeIn(notes[1]))
        self.at('It never ends')
        self.play(Indicate(pair[1].glyphs[-1], color=ERROR, scale_factor=1.6), Indicate(pair[0].glyphs[-1], color=ERROR,
                                                                                       scale_factor=1.6))
        self.finish()


# ---------------------------------------------------------------- 1.4

class Segment_1_4(Segment):
    """Long division by doubling (q01-02)."""
    EPISODE, SEGMENT = 1, '1.4'

    def construct(self):
        # [V1.4a] the binary_digits function
        code = code_panel(snippet_lines(Q2, 5, 12), font_size=20).to_edge(UP, buff=0.4)
        self.play(FadeIn(code.background))
        self.play(type_code(code, run_time=2.4))
        # The method as a little loop under the code: double, take the bit, keep the fraction
        steps = VGroup(label_box('double it', font_size=28), label_box('whole part → next bit', font_size=28),
                       label_box('keep the fraction', font_size=28)).arrange(RIGHT, buff=0.9).move_to(DOWN * 1.4)
        links = VGroup(*[Arrow(steps[i].get_right(), steps[i + 1].get_left(), buff=0.12, color=SCAFFOLD)
                         for i in range(2)])
        again = CurvedArrow(steps[2].get_bottom() + DOWN * 0.1, steps[0].get_bottom() + DOWN * 0.1, angle=-PI / 4,
                            color=SCAFFOLD, stroke_width=3)
        again_tag = label('repeat', 24, SCAFFOLD).next_to(again, DOWN, buff=0.08)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in (steps[0], links[0], steps[1], links[1], steps[2])],
                              lag_ratio=0.3), run_time=1.6)

        def light(i):
            return [steps[j][0].animate.set_stroke(FOCUS if j == i else SCAFFOLD, 3 if j == i else 2) for j in range(3)]
        self.at('Take your fraction and double it')
        box = line_highlight(code, 3)
        self.play(Create(box), *light(0))
        self.at('the next binary digit is a one')
        self.play(Transform(box, line_highlight(code, 4)), *light(1))
        self.play(Transform(box, line_highlight(code, 5)), run_time=0.6)
        self.at('throw away the whole part')
        self.play(Transform(box, line_highlight(code, 6)), *light(2))
        self.at('the next digit is a zero')
        self.play(Indicate(steps[1], color=FOCUS, scale_factor=1.08))
        self.at('Then repeat')
        self.play(Transform(box, line_highlight(code, 2)), Create(again), FadeIn(again_tag), *light(-1))

        # [V1.4b] the doubling table for 1/10
        self.at('Start with one tenth')
        self.play(FadeOut(VGroup(code, box, steps, links, again, again_tag)))
        xs = [-4.8, -1.8, 1.0, 3.8]
        heads = VGroup(*[label(t, 30, SCAFFOLD).move_to([x, 2.3, 0]) for t, x in zip(('value', '× 2', 'bit', 'keep'), xs)])
        under = Line([-6.1, 1.95, 0], [5.1, 1.95, 0], color=GREY_D)
        ys = [1.45 - 0.68 * i for i in range(6)]
        # Rows computed exactly with Fraction (the doubling of q01-02), shown in tenths.
        rows, x = [], Fraction(1, 10)
        for _ in range(6):
            doubled = x * 2
            bit = int(doubled)
            rows.append((x, doubled, bit, doubled - bit))
            x = doubled - bit
        tenths = lambda f: f'{f * 10}/10'
        cells = []
        for (value, doubled, bit, keep), y in zip(rows, ys):
            cells.append(VGroup(label(tenths(value), 36).move_to([xs[0], y, 0]),
                                label(tenths(doubled), 36, FOCUS if doubled >= 1 else WHITE).move_to([xs[1], y, 0]),
                                label(str(bit), 36, STORED).move_to([xs[2], y, 0]),
                                label(tenths(keep), 36).move_to([xs[3], y, 0])))
        bits = ''.join(str(r[2]) for r in rows)
        string = MonoLine('0.' + bits, font_size=44, color=STORED).set_anchor([-1.6, 3.3, 0])
        string.glyphs[:2].set_color(WHITE)
        self.play(FadeIn(heads), Create(under), FadeIn(string.glyphs[:2]), FadeIn(cells[0][0]))
        beats = ['two tenths. Less than one', 'four tenths, another zero', 'Eight tenths, zero',
                 'Sixteen tenths', 'Twelve tenths']
        for i, phrase in enumerate(beats):
            self.at(phrase)
            if i:
                self.play(FadeIn(cells[i][0], shift=DOWN * 0.2), run_time=0.3)
            self.play(FadeIn(cells[i][1], shift=RIGHT * 0.3), run_time=0.4)
            self.play(FadeIn(cells[i][2], scale=1.5), FadeIn(cells[i][3], shift=RIGHT * 0.3), run_time=0.4)
            self.play(TransformFromCopy(cells[i][2], string.glyphs[2 + i]), run_time=0.4)

        # [V1.4c] 2/10 again: the earlier row lights up and a loop connects them
        self.at('Two tenths is a number')
        self.play(cells[0][3].animate.set_color(FOCUS), cells[4][3].animate.set_color(FOCUS),
                  cells[1].animate.set_color(FOCUS))
        loop = CurvedArrow(cells[4][3].get_right() + RIGHT * 0.15, cells[0][3].get_right() + RIGHT * 0.15,
                           angle=PI * 0.75, color=FOCUS, stroke_width=4, tip_length=0.2)
        self.play(Create(loop), run_time=0.9)
        self.at('the same path again')
        self.play(FadeIn(cells[5][0], shift=DOWN * 0.2), run_time=0.3)
        self.play(FadeIn(cells[5][1:]), TransformFromCopy(cells[5][2], string.glyphs[7]), run_time=0.6)
        for i, phrase in zip((1, 2, 3, 4), ('four tenths, eight tenths', 'eight tenths, six', 'six tenths, two',
                                            'two tenths. Round')):
            self.at(phrase)
            self.play(Indicate(cells[i][0], color=FOCUS, scale_factor=1.3), run_time=0.5)
        self.at('Round and round')
        spaced = MonoLine('0.0 0011 0011 0011 …', font_size=44, color=STORED)
        spaced.set_anchor(string.anchor() + LEFT * 2.2)
        spaced.glyphs[:3].set_color(WHITE)
        first = spaced.chars(4, 8)
        self.play(FadeOut(string.glyphs[7]), TransformMatchingShapes(string.glyphs[:3], spaced.glyphs[:3]),
                  ReplacementTransform(string.glyphs[3:7], first), run_time=0.8)
        stamp = SurroundingRectangle(first, color=FOCUS, buff=0.08, corner_radius=0.06)
        self.play(Create(stamp))
        self.at('The digits zero, zero, one, one')
        for k, start in enumerate((9, 14)):
            copy = VGroup(stamp, first).copy()
            target = spaced.chars(start, start + 4)
            self.play(copy.animate.shift(target.get_center() - first.get_center()), run_time=0.5)
            pulse(self, copy[1], None, factor=1.15, run_time=0.15)
        self.play(FadeIn(spaced.glyphs[-1]))

        # [V1.4d] the console: 1/4 and 3/8 end in zeros; 1/10 and 1/5 repeat
        self.at('the code in the corner')
        self.play(FadeOut(Group(*self.mobjects)))
        code = code_panel(snippet_lines(Q2, 5, 12), font_size=20).to_corner(UL, buff=0.35)
        out = output_console(Q2, font_size=24).next_to(code, DOWN, buff=0.35, aligned_edge=LEFT)
        card = qr_card('q01-02')
        self.play(FadeIn(code), FadeIn(card, shift=UP * 0.2))
        self.play(FadeIn(out.background), run_time=0.4)
        self.at('using Python')
        for i in range(4):
            self.play(out.type_line(i, run_time=0.8))
        self.at('A quarter and three eighths')
        greens = [out.lines[i].chars(out.lines[i].source.index(head) + len(head))
                  for i, head in ((0, '0.01'), (1, '0.011'))]
        self.play(*[g.animate.set_color(EXACT) for g in greens])
        self.at('One tenth and one fifth never finish')
        reds = [out.lines[i].chars(out.lines[i].source.index('= 0.') + 4) for i in (2, 3)]
        self.play(*[r.animate.set_color(ERROR) for r in reds])
        self.finish()


# ---------------------------------------------------------------- 1.5

class Segment_1_5(Segment):
    """Where the computer stops: 53 bits, rounding, and what 0.1 really is (q01-03)."""
    EPISODE, SEGMENT = 1, '1.5'

    def construct(self):
        # [V1.5a] the endless string scrolls out; a 53-bit ruler slides along it
        bits = binary_digits(Fraction(1, 10), 62)              # computed: the doubling of 1/10
        line = MonoLine('0.' + bits + '…', font_size=24, color=WHITE).set_anchor([-6.75, 0.6, 0])
        self.play(LaggedStart(*[FadeIn(g, shift=LEFT * 0.2) for g in line.glyphs], lag_ratio=0.6), run_time=3.0)
        first = 2 + bits.index('1')                             # column of the first 1
        kept_end = first + 53                                   # one past the last kept bit
        # MonoLine.cell runs a little wide for long lines, so measure the glyphs themselves.
        g = line.glyphs
        pitch = (g[kept_end - 1].get_x() - g[first].get_x()) / 52
        left_x, right_x = g[first].get_x() - pitch / 2, g[kept_end - 1].get_x() + pitch / 2
        ruler_w = right_x - left_x
        ruler = VGroup(Rectangle(width=ruler_w, height=0.62).set_fill(FOCUS, 0.12).set_stroke(FOCUS, 2))
        for k in range(0, 54, 4):
            ruler.add(Line(DOWN * 0.31, DOWN * (0.31 - (0.14 if k % 8 else 0.22)), color=FOCUS, stroke_width=2)
                      .shift(LEFT * ruler_w / 2 + RIGHT * pitch * k))
        ruler_label = label('53 significant bits', 26, FOCUS)
        ruler_label.add_updater(lambda m: m.next_to(ruler, UP, buff=0.12))
        ruler.move_to([line.column_point(0)[0] - ruler_w / 2 - 0.5, line.anchor()[1], 0])
        self.add(ruler, ruler_label)
        self.at('keep fifty-three significant')
        self.play(ruler.animate.set_x((left_x + right_x) / 2), run_time=2.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(Indicate(line.chars(first, first + 1), color=FOCUS, scale_factor=1.8), run_time=0.7)
        self.at('Everything after that is rounded off')
        tail = line.chars(kept_end)
        self.play(tail.animate.set_color(GREY_D), run_time=0.4)
        self.play(LaggedStart(*[g.animate.shift(DOWN * 2.6 + RIGHT * 0.3).rotate(-PI / 3).set_opacity(0)
                                for g in tail], lag_ratio=0.12), run_time=1.0, rate_func=rate_functions.ease_in_quad)
        self.remove(tail)

        # [V1.5b] the last kept bits round up (the discarded tail is more than half)
        kept = bits[first - 2:kept_end - 2]
        rounded = format(int(kept, 2) + 1, '053b')              # tail starts 1001..., more than half: round up
        assert int(bits[kept_end - 2:], 2) > 0 and bits[kept_end - 2] == '1'
        changed = next(i for i in range(53) if kept[i] != rounded[i])
        old = line.chars(first + changed, kept_end)
        new = MonoLine(rounded[changed:], font_size=24, color=STORED)
        for glyph, place in zip(new.glyphs, old):
            glyph.move_to(place)
        up = label('rounded up', 26, STORED).next_to(new, DOWN, buff=0.45).align_to(new, RIGHT)
        why = label('the cut-off tail was more than half', 22, SCAFFOLD).next_to(up, DOWN, buff=0.1).align_to(up, RIGHT)
        self.play(old.animate.set_color(FOCUS).shift(UP * 0.15), run_time=0.4)
        self.play(ReplacementTransform(old, new.glyphs), FadeIn(up, shift=UP * 0.2), FadeIn(why), run_time=0.8)

        # What Python stores for 0.1: the rounded 53 bits
        self.at('So when you type zero point one')
        stored = VGroup(*line.chars(first, first + changed), *new.glyphs)
        self.play(stored.animate.set_color(STORED), run_time=0.8)
        note = label('what Python stores for 0.1', 26, STORED).move_to([0.5, -1.7, 0])
        typed = label('you typed 0.1', 26, FOCUS).move_to([-4.5, -2.9, 0])
        snap = Arrow(typed.get_right(), note.get_left() + DOWN * 0.05, buff=0.2, color=FOCUS)
        self.play(FadeIn(typed))
        self.play(GrowArrow(snap), FadeIn(note, shift=RIGHT * 0.2))

        # [V1.5c] q01-03: Decimal(0.1) prints the stored value, every digit
        self.at('How close is it')
        self.play(FadeOut(Group(*self.mobjects)))
        ruler_label.clear_updaters()
        out = output_console(Q3, font_size=20).to_edge(UP, buff=0.35)
        code = code_panel(snippet_lines(Q3, 6, 13), font_size=20).next_to(out, DOWN, buff=0.3).to_edge(LEFT, buff=0.35)
        card = qr_card('q01-03')
        self.play(FadeIn(out.background), FadeIn(code.background), FadeIn(card, shift=UP * 0.2))
        self.play(type_code(code, run_time=1.8))
        self.at('prints the stored value exactly')
        self.play(out.type_line(0, run_time=2.0))
        decimal = out.lines[0]
        start = decimal.source.index('= 0.') + 2
        self.at('It starts off looking perfect')
        self.play(decimal.chars(start + 2, start + 3).animate.set_color(FOCUS).scale(1.4), run_time=0.4)
        self.play(decimal.chars(start + 2, start + 3).animate.scale(1 / 1.4), run_time=0.3)
        self.at('And then the junk appears')
        junk = decimal.chars(start + 19)                        # after 0.1 and sixteen zeros
        self.play(junk.animate.set_color(ERROR), run_time=0.8)
        self.play(LaggedStart(*[Indicate(g, color=ERROR, scale_factor=1.4) for g in junk], lag_ratio=0.05),
                  run_time=2.0)

        # [V1.5d] the Fraction line; its denominator becomes 2⁵⁵
        self.at('Fraction shows the same number')
        self.play(FadeOut(code), FadeOut(card), out.type_line(1, run_time=1.2))
        numer, denom = output_line(Q3, 'Fraction(0.1)').split('= ')[1].split('/')
        big = VGroup(MonoLine(numer, font_size=34, color=STORED), MonoLine('/', font_size=34),
                     MonoLine(denom, font_size=34, color=STORED)).arrange(RIGHT, buff=0.2).move_to(DOWN * 0.1)
        self.play(TransformFromCopy(out.lines[1].part(numer), big[0].glyphs),
                  TransformFromCopy(out.lines[1].part('/'), big[1].glyphs),
                  TransformFromCopy(out.lines[1].part(denom), big[2].glyphs), run_time=1.0)
        self.at('two to the fifty-fifth')
        power = label('2⁵⁵', 48, FOCUS).move_to(big[2]).align_to(big[2], LEFT)
        self.play(ReplacementTransform(big[2].glyphs, power), run_time=0.8)
        self.play(VGroup(big[0], big[1], power).animate.arrange(RIGHT, buff=0.25, aligned_edge=DOWN).move_to(DOWN * 0.1),
                  run_time=0.6)
        self.at('the giveaway')
        self.play(out.type_line(2, run_time=0.8))
        self.play(out.part(2, 'True').animate.set_color(EXACT), run_time=0.4)
        self.at('Every double is secretly')
        rule = label('every double = a whole number / a power of 2', 30).move_to(DOWN * 1.5)
        self.play(FadeIn(rule, shift=UP * 0.2))
        self.at('one tenth can never be')
        tenth = label('1/10 = 1/(2 × 5)', 30, ERROR).next_to(rule, DOWN, buff=0.45)
        no = crossmark(size=0.4).next_to(tenth, RIGHT, buff=0.3)
        self.play(FadeIn(tenth), Create(no))

        # [V1.5e] the error line under a magnifier
        self.at('The stored value is too big')
        self.play(FadeOut(VGroup(big[0], big[1], power, rule, tenth, no)))
        self.play(out.type_line(3, run_time=0.9))
        self.play(out.type_line(4, run_time=0.9))
        tiny = out.lines[4].part(output_line(Q3, '≈').split('≈ ')[1])
        lens = magnifier(0.5).move_to(tiny.get_center() + LEFT * 2.5 + DOWN * 0.6)
        self.play(FadeIn(lens))
        self.play(lens.animate.shift(tiny[0].get_center() - lens[0].get_center()), run_time=1.0)
        self.play(lens.animate.shift(tiny[-1].get_center() - tiny[0].get_center()), run_time=1.2,
                  rate_func=rate_functions.there_and_back_with_pause)
        words = label('about five and a half quintillionths of a dollar', 30, FOCUS)
        words.next_to(out, DOWN, buff=1.0)
        self.play(tiny.animate.set_color(FOCUS), FadeIn(words, shift=UP * 0.2))
        self.at('absurdly small')
        self.play(FadeOut(lens))
        self.at('computers are very good')
        times = label('×', 40, MONEY)
        count = number(1, font_size=40, color=MONEY, commas=True)
        times_group = VGroup(times, count).arrange(RIGHT, buff=0.2).next_to(words, DOWN, buff=0.7)
        final_w = times.width + 0.2 + number(1_000_000_000, font_size=40, commas=True).width
        times.set_x(-final_w / 2 + times.width / 2)          # centred for the final value
        count.add_updater(lambda m: m.next_to(times, RIGHT, buff=0.2))
        count.update()
        self.play(FadeIn(times_group))
        self.at('a billion times')
        self.play(ChangeDecimalToValue(count, 1_000_000_000), run_time=1.8, rate_func=rate_functions.ease_in_expo)
        count.clear_updaters()
        self.finish()


# ---------------------------------------------------------------- 1.6

class Segment_1_6(Segment):
    """The cent grid: which of the hundred cent values are exact (q01-04)."""
    EPISODE, SEGMENT = 1, '1.6'

    def construct(self):
        # The erased dime from 1.1, then: what about the other amounts?
        ghost = DashedVMobject(Circle(radius=1.3, color=MONEY, stroke_width=3), num_dashes=36).set_stroke(opacity=0.45)
        ghost_tag = label('10¢', 48, MONEY).set_opacity(0.45)
        self.play(FadeIn(ghost), FadeIn(ghost_tag))
        self.at('What about the other cent values')
        others = VGroup(*[label(t, 34, SCAFFOLD) for t in ('1¢', '25¢', '37¢', '50¢', '99¢')])
        for t, angle in zip(others, np.linspace(PI * 0.9, PI * 0.1, 5)):
            t.move_to(np.array([math.cos(angle), math.sin(angle), 0]) * 2.6 + DOWN * 0.4)
        self.play(LaggedStart(*[FadeIn(t, scale=0.6) for t in others], lag_ratio=0.2), run_time=1.2)

        # [V1.6a] the cent grid builds row by row, all grey
        self.at("Here's every amount")
        self.play(FadeOut(VGroup(ghost, ghost_tag, others)), run_time=0.5)
        # show_arrows=False would leave the arrows uncentred (common.CentGrid centres only what it
        # holds), so keep them in the grid and hide them until the test reaches each cell.
        grid = CentGrid(cell=0.66, font_size=18)
        grid.arrow_group.set_opacity(0)
        rows = [VGroup(*[VGroup(grid.cells[r * 10 + c], grid.labels[r * 10 + c]) for c in range(10)]) for r in range(10)]
        self.play(LaggedStart(*[FadeIn(r, shift=DOWN * 0.15) for r in rows], lag_ratio=0.3), run_time=2.5)

        # [V1.6b] the q01-04 loop tests every cell in order
        self.at('The code tests each one')
        code = code_panel(snippet_lines(Q4, 5, 10), font_size=18).to_edge(UP, buff=0.3)
        small = 4.85 / grid.height
        self.play(grid.animate.scale(small).next_to(code, DOWN, buff=0.3), FadeIn(code, shift=DOWN * 0.2))
        box = line_highlight(code, 4)
        scan = SurroundingRectangle(rows[0], color=FOCUS, buff=0.03)
        self.play(Create(box), Create(scan))
        arrows_by_cell = grid.arrows
        for r in range(10):
            if r:
                self.play(scan.animate.move_to(rows[r]), run_time=0.15)
            anims = []
            for c in range(10):
                n = r * 10 + c
                if arrows_by_cell[n] is None:
                    anims.append(grid.cells[n].animate.set_fill(EXACT, 0.55).set_stroke(EXACT, 3))
                else:
                    anims.append(arrows_by_cell[n].animate.set_opacity(1))
            self.play(LaggedStart(*anims, lag_ratio=0.3), run_time=0.55)
        self.play(FadeOut(scan), FadeOut(box))

        # [V1.6c] exact: [0, 25, 50, 75]; four of a hundred
        self.at('Of the hundred possible')
        out = output_console(Q4, font_size=18, rows=6)
        self.play(FadeOut(code), grid.animate.scale(1 / small).to_edge(LEFT, buff=0.35).set_y(0))
        out.to_corner(UR, buff=0.35)
        card = qr_card('q01-04')
        self.play(FadeIn(out.background), FadeIn(card, shift=UP * 0.2))
        self.play(out.type_line(0, run_time=1.0))
        self.play(out.type_line(1, run_time=1.2))
        big = label('4 of 100', 72, EXACT).move_to([3.55, 0.25, 0])
        self.at('Zero. A quarter')
        self.play(FadeIn(big, scale=0.6), run_time=0.3)
        for n, phrase in zip((0, 25, 50, 75), (None, 'A quarter.', 'A half.', 'Three quarters.')):
            if phrase:
                self.at(phrase)
            pulse(self, VGroup(grid.cells[n], grid.labels[n]), None, factor=1.35, run_time=0.18)

        # [V1.6d] the rule predicts it: the four exact cells in binary
        self.at('You can predict that')
        self.play(FadeOut(card), FadeOut(out), FadeOut(big))
        self.at('A cent value is some number')
        over = VGroup(label('a cent value', 26, SCAFFOLD), label('cents / 100', 44)).arrange(DOWN, buff=0.2)
        over.move_to([3.4, -0.6, 0])
        self.play(FadeIn(over, shift=UP * 0.2))
        self.at('one hundred is two times two')
        factors = label('100 = 2 × 2 × 5 × 5', 40).move_to([3.4, -2.45, 0])
        self.play(Write(factors), run_time=1.4)
        self.at('To lose those fives')
        fives = text_part(factors, '100 = 2 × 2 × 5 × 5', '5 × 5')
        self.play(fives.animate.set_color(ERROR))
        self.at('a multiple of twenty-five')
        rule = label('so the cents must be a multiple of 25', 28, FOCUS).next_to(factors, DOWN, buff=0.3)
        self.play(FadeIn(rule, shift=UP * 0.2))
        self.at('Zero, twenty-five, fifty')
        callouts = VGroup()
        grid_right = grid.squares.get_right()[0]
        for n, text in zip((0, 25, 50, 75), ('.00  →  0.0', '.25  →  0.01  = ¼', '.50  →  0.1  = ½', '.75  →  0.11  = ¾')):
            y = grid.cells[n].get_y()
            tag = label(text, 30, EXACT).move_to([grid_right + 0.75, y, 0], aligned_edge=LEFT)
            link = Arrow([grid_right + 0.05, y, 0], [grid_right + 0.7, y, 0], buff=0, color=EXACT, stroke_width=3,
                         max_tip_length_to_length_ratio=0.35)
            callouts.add(VGroup(link, tag))
        head = label('in binary', 24, SCAFFOLD).next_to(callouts[0][1], UP, buff=0.2).align_to(callouts[0][1], LEFT)
        self.play(FadeOut(over), run_time=0.3)
        self.play(FadeIn(head), LaggedStart(*[AnimationGroup(Create(c[0]), FadeIn(c[1], shift=RIGHT * 0.2))
                                              for c in callouts], lag_ratio=0.35), run_time=2.0)

        # [V1.6e] 0.10 and 0.20 are stored high, 0.30 and 0.70 low
        self.at('And the errors')
        self.play(FadeOut(VGroup(callouts, head, factors, rule)))
        out = output_console(Q4, needles=['0.10 is', '0.20 is', '0.30 is', '0.70 is'], font_size=18)
        out.to_corner(UR, buff=0.35)
        self.play(FadeIn(out.background))
        zooms = VGroup()
        for i, (n, phrase) in enumerate(zip((10, 20, 30, 70), ('Ten cents and twenty', 'twenty cents are stored',
                                                               'Thirty cents and seventy', 'seventy cents are stored'))):
            self.at(phrase)
            piece = VGroup(grid.cells[n], grid.labels[n], grid.arrows[n]).copy()
            target = piece.copy().scale(2.0).move_to([1.4 + 1.6 * i, -1.0, 0])
            self.play(out.type_line(i, run_time=0.9), Transform(piece, target), grid.cells[n].animate.set_stroke(FOCUS, 3),
                      run_time=0.9)
            zooms.add(piece)
        self.at('whichever neighbour')
        self.play(LaggedStart(*[Indicate(z[2], scale_factor=1.6, color=z[2].get_color()) for z in zooms],
                              lag_ratio=0.25), run_time=1.6)

        # Errors pile up or partly cancel
        self.at('errors can pile up')
        up = lambda: Arrow(DOWN * 0.35, UP * 0.35, buff=0, color=STORED, stroke_width=5)
        down = lambda: Arrow(UP * 0.35, DOWN * 0.35, buff=0, color=ERROR, stroke_width=5)
        pile = VGroup(up(), label('+', 30), up(), label('pile up', 26, SCAFFOLD)).arrange(RIGHT, buff=0.2)
        pile.move_to([0.6, -2.45, 0], aligned_edge=LEFT)
        self.play(FadeIn(pile, shift=UP * 0.2))
        self.at('or partly cancel')
        cancel = VGroup(up(), label('+', 30), down(), label('partly cancel', 26, SCAFFOLD)).arrange(RIGHT, buff=0.2)
        cancel.move_to([0.6, -3.35, 0], aligned_edge=LEFT)
        self.play(FadeIn(cancel, shift=UP * 0.2))
        self.finish()


# ---------------------------------------------------------------- 1.7

def neighbours(x, below=1, above=1):
    """Doubles around x (a float): `below` before it, x itself, `above` after it."""
    out = [x]
    for _ in range(below):
        out.insert(0, math.nextafter(out[0], -math.inf))
    for _ in range(above):
        out.append(math.nextafter(out[-1], math.inf))
    return out


def schematic_bar(length, tip, color, text, font_size=24):
    """A value as a bar (not to scale), with a thin RED tip for the excess when tip > 0."""
    body = Rectangle(width=length, height=0.32).set_fill(color, 0.85).set_stroke(width=0)
    group = VGroup(body)
    if tip:
        cap = Rectangle(width=tip, height=0.32).set_fill(ERROR, 1).set_stroke(width=0).next_to(body, RIGHT, buff=0)
        group.add(cap)
    name = label(text, font_size, color).next_to(group, LEFT, buff=0.2)
    group.name = name
    return group


class Segment_1_7(Segment):
    """Why 0.1 + 0.2 misses: the float line near 0.3."""
    EPISODE, SEGMENT = 1, '1.7'

    def construct(self):
        # [V1.7a] the float line near 0.3: three doubles, the true 0.3 between two of them
        d_lo, d03, d_hi = neighbours(0.3)                     # computed: the doubles around 0.3
        step = Fraction(d_hi) - Fraction(d03)
        fl = FloatLine(Fraction(d_lo) - step * Fraction(2, 5), Fraction(d_hi) + step * Fraction(2, 5),
                       width=11.0, ticks=[d_lo, d03, d_hi], tick_height=0.45).move_to(DOWN * 0.7)
        title = label('close-up of the number line near 0.3', 26, SCAFFOLD).to_edge(UP, buff=0.35)
        first = output_console(Q1, needles=['a + b        =', 'a + b == 0.30'], font_size=30).move_to(UP * 0.6)
        first.part(1, 'False').set_color(ERROR)
        self.play(FadeIn(first, shift=DOWN * 0.2))
        self.play(Indicate(first.part(0, '4'), color=ERROR, scale_factor=1.6))
        self.at('a close-up of the number line')
        self.play(FadeOut(first), Create(fl.axis), FadeIn(title))
        self.at('These tick marks')
        self.play(LaggedStart(*[GrowFromCenter(t) for t in fl.ticks], lag_ratio=0.3), run_time=1.2)
        self.at('The true zero point three')
        diamond = fl.diamond(Fraction(3, 10))
        true_tag = label('true 0.3', 24, FOCUS).next_to(diamond, UP, buff=0.12)
        self.play(FadeIn(diamond, shift=DOWN * 0.3), FadeIn(true_tag))
        self.at('Python stores the nearer one')
        name_lo = label('the double for 0.3', 24, STORED).next_to(fl.point(d03), DOWN, buff=1.25)
        name_hi = label('next double up', 24, STORED).next_to(fl.point(d_hi), DOWN, buff=1.25)
        name_hi.align_to(name_lo, UP)
        snap = fl.snap(Fraction(3, 10))
        self.play(Create(snap))
        self.play(FadeIn(name_lo, shift=UP * 0.2), Indicate(fl.ticks[1], color=FOCUS))
        self.play(FadeIn(name_hi, shift=UP * 0.2))
        self.play(FadeOut(snap))

        # [V1.7b] stored 0.1 and stored 0.2 as bars, each with a thin red excess
        self.at('Now add the stored versions')
        # Not to scale: 2 units per 0.1. The red tips are exaggerated but keep the true 1:2 ratio
        # of the two excesses (5.6e-18 and 1.1e-17 in q01-04's output).
        excess = [Fraction(v) - Fraction(t) for v, t in ((0.1, '0.1'), (0.2, '0.2'))]
        tips = [0.12, 0.12 * float(excess[1] / excess[0])]
        b1 = schematic_bar(2.0, tips[0], STORED, 'stored 0.1').move_to([-2.6, 2.6, 0], aligned_edge=LEFT)
        b2 = schematic_bar(4.0, tips[1], STORED, 'stored 0.2').move_to([-2.6, 1.85, 0], aligned_edge=LEFT)
        b1.name.next_to(b1, LEFT, buff=0.2)
        b2.name.next_to(b2, LEFT, buff=0.2)
        scale_note = label('bars not to scale', 20, SCAFFOLD).to_corner(UR, buff=0.35)
        self.play(FadeOut(title), FadeIn(scale_note), GrowFromEdge(b1, LEFT), FadeIn(b1.name), run_time=0.8)
        self.play(GrowFromEdge(b2, LEFT), FadeIn(b2.name), run_time=0.8)
        self.at('Both of them are a little too big')
        self.play(Indicate(b1[1], color=ERROR, scale_factor=2.0), Indicate(b2[1], color=ERROR, scale_factor=1.6))
        self.at('their sum is a little too big')
        self.play(Indicate(VGroup(b1[1], b2[1]), color=ERROR, scale_factor=1.6))

        # [V1.7c] the bars join; the sum lands exactly halfway between two doubles
        self.at('In fact, it lands exactly halfway')
        total = Fraction(0.1) + Fraction(0.2)                 # exact sum of the two stored values
        x_sum = fl.point(total)[0]
        joined_w = b1.width + b2.width
        self.play(FadeOut(b1.name), FadeOut(b2.name),
                  b1.animate.move_to([x_sum - joined_w, 0.9, 0], aligned_edge=LEFT),
                  b2.animate.move_to([x_sum - b2.width, 0.9, 0], aligned_edge=LEFT), run_time=1.2)
        sum_name = label('stored 0.1 + stored 0.2', 24, STORED).next_to(VGroup(b1, b2), UP, buff=0.15)
        drop = DashedLine([x_sum, 0.72, 0], fl.point(total) + UP * 0.05, color=STORED)
        dot = Dot(fl.point(total), radius=0.1, color=STORED)
        self.play(FadeIn(sum_name), Create(drop), FadeIn(dot, scale=0.5))
        brace_l = BraceBetweenPoints(fl.point(d03), fl.point(total), direction=DOWN, color=FOCUS)
        brace_r = BraceBetweenPoints(fl.point(total), fl.point(d_hi), direction=DOWN, color=FOCUS)
        for b in (brace_l, brace_r):
            b.shift(DOWN * 0.15)
        halfway = label('exactly halfway', 24, FOCUS).next_to(VGroup(brace_l, brace_r), DOWN, buff=0.05)
        halfway.set_z_index(3)
        self.play(GrowFromCenter(brace_l), GrowFromCenter(brace_r), FadeIn(halfway))

        # [V1.7d] a tie: round to even, up to the next double
        self.at('the rule is to pick the one')
        self.play(FadeOut(VGroup(brace_l, brace_r, halfway)))
        tie = CurvedArrow(fl.point(total) + UP * 0.25, fl.point(d_hi) + UP * 0.3, angle=-PI / 2.5, color=FOCUS,
                          stroke_width=4, tip_length=0.18)
        tie_tag = label('a tie: round to even', 26, FOCUS).next_to(tie, UP, buff=0.15).align_to(tie, LEFT).shift(RIGHT * 0.4)
        self.play(Create(tie), FadeIn(tie_tag))
        self.at('happens to be the upper one')
        self.play(dot.animate.move_to(fl.point(d_hi)), run_time=0.8)
        self.play(Indicate(fl.ticks[2], color=FOCUS))

        # [V1.7e] the values Python prints for the two ticks; a red ≠ between them
        self.at('So the sum and the number you typed')
        self.play(FadeOut(VGroup(tie, tie_tag, drop, b1, b2, sum_name)))
        printed_hi = output_line(Q1, 'a + b        =').split('= ')[1]          # 0.30000000000000004
        py_lo = MonoLine(repr(d03), font_size=24, color=WHITE)                   # computed: repr of the double
        py_hi = MonoLine(printed_hi, font_size=24, color=WHITE)
        py_lo.next_to(name_lo, DOWN, buff=0.2)
        py_hi.next_to(name_hi, DOWN, buff=0.2)
        typed_tag = label('you typed', 22, SCAFFOLD).next_to(py_lo, DOWN, buff=0.1)
        sum_tag = label('the sum', 22, SCAFFOLD).next_to(py_hi, DOWN, buff=0.1)
        self.play(FadeIn(py_lo, shift=UP * 0.2), FadeIn(typed_tag))
        self.play(FadeIn(py_hi, shift=UP * 0.2), FadeIn(sum_tag))
        neq = label('≠', 64, ERROR).move_to([(py_lo.get_right()[0] + py_hi.get_left()[0]) / 2, py_hi.get_y(), 0])
        self.play(FadeIn(neq, scale=0.5))
        self.at('They differ by one step')
        gap = BraceBetweenPoints(fl.point(d03) + UP * 0.75, fl.point(d_hi) + UP * 0.75, direction=UP, color=FOCUS)
        ulp = math.ulp(0.3)                                    # computed: one step here, 2⁻⁵⁴
        mant, expo = f'{ulp:.2e}'.split('e')
        sup = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')
        gap_tag = label(f'one step ≈ {mant} × 10{str(int(expo)).translate(sup)}', 28, FOCUS).next_to(gap, UP, buff=0.12)
        self.play(FadeOut(true_tag), GrowFromCenter(gap), FadeIn(gap_tag))
        self.at('Python prints the upper one')
        pulse(self, py_hi.part('4'), ERROR, factor=1.6)
        self.at('equals equals')
        verdict = Console([output_line(Q1, '== 0.30')], font_size=24).to_edge(UP, buff=0.4)
        verdict.lines[0].part('False').set_color(ERROR)
        self.play(FadeOut(scale_note), FadeIn(verdict, shift=DOWN * 0.2))

        # [V1.7f] contrast: 0.25 + 0.50 lands right on the tick for 0.75
        self.at('And a quarter plus a half')
        self.play(FadeOut(Group(*self.mobjects)))
        e_lo, e75, e_hi = neighbours(0.75)
        estep = Fraction(e_hi) - Fraction(e75)
        fl2 = FloatLine(Fraction(e_lo) - estep * Fraction(2, 5), Fraction(e_hi) + estep * Fraction(2, 5),
                        width=11.0, ticks=[e_lo, e75, e_hi], tick_height=0.45).move_to(DOWN * 0.7)
        name75 = label('the double for 0.75', 24, EXACT).next_to(fl2.point(e75), DOWN, buff=0.5)
        title2 = label('close-up near 0.75', 26, SCAFFOLD).to_edge(UP, buff=0.35)
        self.play(FadeIn(title2), Create(fl2.axis), LaggedStart(*[GrowFromCenter(t) for t in fl2.ticks], lag_ratio=0.3),
                  FadeIn(name75), run_time=1.2)
        self.at('Both are stored exactly')
        g1 = schematic_bar(2.0, 0, EXACT, 'stored 0.25').move_to([-2.6, 2.6, 0], aligned_edge=LEFT)
        g2 = schematic_bar(4.0, 0, EXACT, 'stored 0.50').move_to([-2.6, 1.85, 0], aligned_edge=LEFT)
        g1.name.next_to(g1, LEFT, buff=0.2)
        g2.name.next_to(g2, LEFT, buff=0.2)
        self.play(GrowFromEdge(g1, LEFT), FadeIn(g1.name), GrowFromEdge(g2, LEFT), FadeIn(g2.name), run_time=1.0)
        self.at('The sum lands right on a tick')
        x75 = fl2.point(Fraction(0.25) + Fraction(0.5))[0]
        self.play(FadeOut(g1.name), FadeOut(g2.name),
                  g1.animate.move_to([x75 - 6.0, 0.9, 0], aligned_edge=LEFT),
                  g2.animate.move_to([x75 - 4.0, 0.9, 0], aligned_edge=LEFT), run_time=1.0)
        drop2 = DashedLine([x75, 0.72, 0], fl2.point(e75) + UP * 0.05, color=EXACT)
        dot2 = Dot(fl2.point(e75), radius=0.1, color=EXACT)
        self.play(Create(drop2), FadeIn(dot2, scale=0.5))
        tick = checkmark(size=0.45).next_to(name75, RIGHT, buff=0.3)
        self.play(Create(tick), Indicate(fl2.ticks[1], color=EXACT))
        self.finish()


# ---------------------------------------------------------------- 1.8

class Segment_1_8(Segment):
    """Why you rarely see it: print shows the shortest digits; the disclosure."""
    EPISODE, SEGMENT = 1, '1.8'

    def construct(self):
        # [V1.8a] print(0.1) shows 0.1; Decimal(0.1) shows every digit
        call = code_text('print(0.1)', font_size=34, color=WHITE)
        shown = Console([repr(0.1)], font_size=34, width=3.0)          # computed: what print(0.1) shows
        VGroup(call, shown).arrange(RIGHT, buff=0.8).to_edge(UP, buff=0.5).to_edge(LEFT, buff=0.5)
        self.play(FadeIn(call))
        self.play(FadeIn(shown.background))
        self.play(shown.type_line(0, run_time=0.4))
        self.at('fifty-five digits of junk')
        exact = output_line(Q3, 'Decimal(0.1)').split('= ')[1]          # from q01-03's output
        full = MonoLine(exact, font_size=24, color=SCAFFOLD)
        full.set_anchor([shown.lines[0].anchor()[0], 1.3, 0])
        if full.get_right()[0] > 6.8:
            full.shift(LEFT * (full.get_right()[0] - 6.8))
        full_tag = label('Decimal(0.1): the stored value, every digit', 22, SCAFFOLD).next_to(full, UP, buff=0.15)
        full_tag.align_to(full, LEFT)
        self.play(FadeIn(full, shift=LEFT * 1.0), FadeIn(full_tag), run_time=1.0)
        self.at('It prints the shortest decimal')
        head = full.chars(0, 3)
        self.play(head.animate.set_color(FOCUS), shown.lines[0].glyphs.animate.set_color(FOCUS))
        brace = BraceBetweenPoints(head.get_corner(DL) + DOWN * 0.08, head.get_corner(DR) + DOWN * 0.08,
                                   direction=DOWN, color=FOCUS)
        brace_tag = label('the shortest digits that lead back to the same double', 24, FOCUS)
        brace_tag.next_to(brace, DOWN, buff=0.1).align_to(brace, LEFT)
        self.play(GrowFromCenter(brace), FadeIn(brace_tag))

        # [V1.8b] the float line near 0.1: every value in this tick's catchment rounds to it
        self.at('Zero point one is the shortest number')
        p_lo, p1, p_hi = neighbours(0.1)
        pstep = Fraction(p_hi) - Fraction(p1)
        fl = FloatLine(Fraction(p_lo) - pstep * Fraction(2, 5), Fraction(p_hi) + pstep * Fraction(2, 5), width=11.0,
                       ticks=[p_lo, p1, p_hi], tick_height=0.45).move_to(DOWN * 2.1)
        left_edge = fl.point((Fraction(p_lo) + Fraction(p1)) / 2)
        right_edge = fl.point((Fraction(p1) + Fraction(p_hi)) / 2)
        basin = Rectangle(width=right_edge[0] - left_edge[0], height=0.8).set_fill(FOCUS, 0.15).set_stroke(FOCUS, 1)
        basin.move_to((left_edge + right_edge) / 2)
        basin_tag = label('rounds to this double', 22, FOCUS).next_to(basin, DOWN, buff=0.12)
        self.play(Create(fl.axis), LaggedStart(*[GrowFromCenter(t) for t in fl.ticks], lag_ratio=0.3), run_time=1.0)
        self.play(FadeIn(basin), FadeIn(basin_tag))
        diamond = fl.diamond(Fraction(1, 10))
        d_tag = label('0.1', 26, FOCUS).next_to(diamond, UP, buff=0.1)
        self.play(FadeIn(diamond, shift=DOWN * 0.3), FadeIn(d_tag))
        self.play(Indicate(fl.ticks[1], color=FOCUS))

        # An addition lands on a different tick, whose shortest name is longer
        self.at('The error is still there')
        self.play(FadeOut(VGroup(brace, brace_tag)), full.chars(3).animate.set_color(ERROR))
        self.at('pushes the result onto a different tick')
        self.play(FadeOut(VGroup(fl, basin, basin_tag, diamond, d_tag)))
        d_lo, d03, d_hi = neighbours(0.3)
        step = Fraction(d_hi) - Fraction(d03)
        fl3 = FloatLine(Fraction(d03) - step * Fraction(4, 5), Fraction(d_hi) + step * Fraction(4, 5), width=11.0,
                        ticks=[d03, d_hi], tick_height=0.45).move_to(DOWN * 2.1)
        basins, names = VGroup(), VGroup()
        printed_hi = output_line(Q1, 'a + b        =').split('= ')[1]
        for v, name in ((d03, repr(d03)), (d_hi, printed_hi)):
            lo = fl3.point(Fraction(v) - step / 2)
            hi = fl3.point(Fraction(v) + step / 2)
            b = Rectangle(width=hi[0] - lo[0] - 0.06, height=0.8).set_fill(FOCUS, 0.12).set_stroke(FOCUS, 1)
            basins.add(b.move_to((lo + hi) / 2))
            names.add(MonoLine(name, font_size=24, color=STORED).next_to(fl3.point(v), DOWN, buff=0.55))
        self.play(Create(fl3.axis), FadeIn(fl3.ticks), FadeIn(basins), FadeIn(names))
        dot = Dot(fl3.point(d03), radius=0.1, color=STORED)
        self.play(FadeIn(dot))
        self.play(dot.animate.move_to(fl3.point(d_hi)), run_time=1.0, rate_func=rate_functions.ease_in_out_back)
        self.at('zero point three, then fifteen zeros')
        pulse(self, names[1].part('4'), ERROR, factor=1.6)

        # The errors are invisible: a total that looks perfect, and what can still go wrong
        self.at('So the errors are usually invisible')
        self.play(FadeOut(Group(*self.mobjects)))
        screen = RoundedRectangle(width=5.0, height=1.6, corner_radius=0.15).set_stroke(GREY_B, 2).set_fill(PANEL, 1)
        screen.move_to(UP * 2.0)
        total = MonoLine(f'Total  ${0.1 + 0.2:.2f}', font_size=40, color=WHITE).move_to(screen)  # computed: formatted sum
        self.play(FadeIn(screen), FadeIn(total))
        self.play(Create(checkmark(size=0.5).next_to(screen, RIGHT, buff=0.3)))
        self.at('makes them dangerous')
        under = MonoLine(printed_hi, font_size=28, color=ERROR).next_to(screen, DOWN, buff=0.35)
        under_tag = label('what it holds', 22, SCAFFOLD).next_to(under, DOWN, buff=0.1)
        self.play(FadeIn(under, shift=DOWN * 0.3), FadeIn(under_tag))
        risks = VGroup()
        for text in ('fail a comparison', 'round the wrong way', 'drift over a million additions'):
            box = label_box(text, color=ERROR, font_size=26)
            risks.add(box)
        risks.arrange(RIGHT, buff=0.35).move_to(DOWN * 1.6)
        fit(risks, 13.0)
        for box, phrase in zip(risks, ('still fail a comparison', 'round the wrong way', 'drift over a million')):
            self.at(phrase)
            self.play(FadeIn(box, shift=UP * 0.3), run_time=0.5)
        self.at('the rest of this series')
        self.play(LaggedStart(*[Indicate(b, color=ERROR, scale_factor=1.08) for b in risks], lag_ratio=0.2), run_time=1.2)

        # [V1.8c] the disclosure: a waveform, and "synthetic voice" under it
        self.at('One more thing worth mentioning')
        self.play(FadeOut(Group(*self.mobjects)))
        bars = VGroup(*[Rectangle(width=0.12, height=0.3).set_fill(STORED, 0.9).set_stroke(width=0) for _ in range(41)])
        bars.arrange(RIGHT, buff=0.1).move_to(UP * 0.6)
        clock = ValueTracker(0)

        def wave(group):
            t = clock.get_value()
            for i, bar in enumerate(group):
                h = 0.25 + 1.4 * abs(math.sin(0.9 * t + i * 0.45) * math.sin(0.37 * t + i * 0.21)) \
                    * math.exp(-((i - 20) / 14) ** 2)
                bar.stretch_to_fit_height(h).set_y(0.6)
        bars.add_updater(wave)
        clock.add_updater(lambda m, dt: m.increment_value(dt * 4))
        self.add(clock, bars)
        self.play(FadeIn(bars), run_time=0.8)
        self.at('The voice you')
        words = label('synthetic voice', 40, WHITE).next_to(bars, DOWN, buff=1.0)
        self.play(FadeIn(words, shift=UP * 0.2))
        self.finish()


# ---------------------------------------------------------------- 1.9

class Segment_1_9(Segment):
    """Recap and challenge (q01-05), the QR wall, and the teaser for episode 2."""
    EPISODE, SEGMENT = 1, '1.9'

    def construct(self):
        # [V1.9a] the recap column builds, each item with a little picture on the right
        items = ['Decimal finishes fractions built from 2s and 5s', 'Binary finishes only powers of 2',
                 '1/10 repeats forever in binary', 'A double keeps 53 bits', 'Only 4 of 100 cent values are exact']
        rows = VGroup(*[label(t, 32) for t in items]).arrange(DOWN, buff=0.62, aligned_edge=LEFT)
        rows.to_edge(LEFT, buff=0.6).shift(UP * 0.2)
        arrows = VGroup(*[Arrow(UP * 0.18, DOWN * 0.18, buff=0, color=GREY_D, stroke_width=3,
                                max_tip_length_to_length_ratio=0.4).next_to(rows[i], DOWN, buff=0.08).align_to(rows, LEFT)
                          .shift(RIGHT * 0.2) for i in range(4)])
        slot = np.array([4.3, 0.2, 0])

        pics = [
            label('10 = 2 × 5', 44, EXACT),
            VGroup(*[label(t, 34, STORED) for t in ('½', '¼', '⅛', '1/16')]).arrange(RIGHT, buff=0.45),
            MonoLine('0.0 0011 0011 …', font_size=34, color=ERROR),
            None,
            None,
        ]
        ruler = VGroup(Rectangle(width=4.2, height=0.5).set_fill(FOCUS, 0.12).set_stroke(FOCUS, 2),
                       label('53 bits', 28, FOCUS))
        ruler[1].next_to(ruler[0], UP, buff=0.12)
        pics[3] = ruler
        mini = CentGrid(cell=0.36, font_size=10, show_arrows=True)
        mini.remove(mini.label_group)
        pics[4] = mini
        for p in pics:
            p.move_to(slot)
        phrases = ['In decimal, only fractions', 'In binary, only powers', 'One tenth has a five',
                   'which keeps fifty-three bits', 'Of the hundred cent values']
        current = None
        for i, (row, pic, phrase) in enumerate(zip(rows, pics, phrases)):
            self.at(phrase)
            anims = [FadeIn(row, shift=RIGHT * 0.3)]
            if i:
                anims.append(GrowArrow(arrows[i - 1]))
            if current is not None:
                anims.append(FadeOut(current, shift=UP * 0.3))
            anims.append(FadeIn(pic, shift=UP * 0.3))
            self.play(*anims, run_time=0.7)
            current = pic
            if i == 2:
                self.play(Indicate(pic.chars(4, 8), color=ERROR), Indicate(pic.chars(9, 13), color=ERROR))
            if i == 3:
                self.play(ruler[0].animate.stretch(1.06, 0), rate_func=there_and_back, run_time=0.6)
            if i == 4:
                self.play(*mini.light_exact(), run_time=0.8)
        self.at('Every other price')
        self.play(Indicate(rows[4], color=EXACT, scale_factor=1.05))

        # [V1.9b] the challenge: q01-05 and a strip of 1,000 cells with eight exact
        self.at("Here's a challenge")
        self.play(FadeOut(Group(*self.mobjects)))
        code = code_panel(snippet_lines(Q5, 6, 8), font_size=18).to_edge(UP, buff=0.35)
        out = output_console(Q5, font_size=20).next_to(code, DOWN, buff=0.3).align_to(code, LEFT)
        card = qr_card('q01-05')
        self.play(FadeIn(code), FadeIn(card, shift=UP * 0.2))
        self.at('thousandths of a dollar')
        strip = Rectangle(width=13.0, height=0.42).set_stroke(GREY_B, 1.5).move_to(UP * 0.25)
        steps = 1000
        cell_w = strip.width / steps
        marks = VGroup(*[Line(UP * 0.21, DOWN * 0.21, color=GREY_D, stroke_width=1)
                         .move_to(strip.get_left() + RIGHT * cell_w * k) for k in range(10, steps, 10)])
        strip_tag = label('1,000 cells: $0.000 to $0.999', 22, SCAFFOLD).next_to(strip, UP, buff=0.12).align_to(strip, LEFT)
        self.play(Create(strip), LaggedStart(*[Create(m) for m in marks], lag_ratio=0.01), FadeIn(strip_tag), run_time=1.5)
        self.at('counts how many')
        self.play(FadeIn(out.background), run_time=0.3)
        self.play(out.type_line(0, run_time=1.6))
        exact = [int(n) for n in re.findall(r'\d+', output_line(Q5, 'are exact').split(':')[1])]
        lights = VGroup()
        for n in exact:
            cell = Rectangle(width=max(cell_w, 0.07), height=0.42).set_fill(EXACT, 1).set_stroke(EXACT, 2)
            lights.add(cell.move_to(strip.get_left() + RIGHT * cell_w * (n + 0.5)))
        scanner = Line(UP * 0.35, DOWN * 0.35, color=FOCUS, stroke_width=3).move_to(strip.get_left())
        self.at('There are eight')
        self.add(scanner)
        self.play(scanner.animate.move_to(strip.get_right()),
                  LaggedStart(*[FadeIn(l, scale=2.0) for l in lights], lag_ratio=1.0), run_time=1.5,
                  rate_func=linear)
        self.remove(scanner)
        self.at('the multiples of one eighth')
        eighths = VGroup(*[label(f'{Fraction(n, steps).numerator}/{Fraction(n, steps).denominator}' if n else '0', 22, EXACT)
                           .next_to(l, DOWN, buff=0.12) for n, l in zip(exact, lights)])
        self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.15) for e in eighths], lag_ratio=0.15), run_time=1.2)

        # Predict: try other numbers of steps
        self.at('predict the answer')
        tries = VGroup()
        for n, phrase in zip(('3', '64', '1024', '100000'), ('Try three', 'Try sixty-four',
                                                           'Try one thousand', 'Try a hundred thousand')):
            chip = label_box(f'STEPS = {n}   →   ?', color=FOCUS, font_size=24)
            tries.add(chip)
        tries.arrange_in_grid(rows=2, cols=2, buff=(0.35, 0.3)).move_to([-2.9, -2.55, 0])
        for chip, phrase in zip(tries, ('Try three', 'Try sixty-four', 'Try one thousand', 'Try a hundred thousand')):
            self.at(phrase)
            self.play(FadeIn(chip, shift=UP * 0.2), run_time=0.4)

        # [V1.9c] the QR wall: every code in this episode, ten seconds
        self.at('If you can predict every one')
        wall = qr_wall(episode_qr_ids(1))
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
        self.play(FadeIn(wall), run_time=0.5)
        self.wait(10)
        self.play(FadeOut(wall), run_time=0.5)

        # [V1.9d] teaser: the float line slides right and its gaps grow, until a gap is more than a cent
        axis = Line(LEFT * 6.4, RIGHT * 6.4, color=SCAFFOLD, stroke_width=2).move_to(UP * 0.6)
        xs = [-6.4 + 0.2 * i for i in range(65)]
        ticks = VGroup(*[Line(DOWN * 0.22, UP * 0.22, color=STORED, stroke_width=3).move_to([x, 0.6, 0]) for x in xs])
        bigger = label('larger numbers  →', 24, SCAFFOLD).next_to(axis, DOWN, buff=0.45).align_to(axis, RIGHT)
        self.play(Create(axis), FadeIn(ticks), FadeIn(bigger), run_time=0.8)
        self.at('why the gaps between doubles grow')
        for _ in range(5):
            self.play(ticks.animate.stretch(2.0, 0, about_point=axis.get_left()), run_time=0.7)
            gone = [t for t in ticks if t.get_x() > 6.5]
            if gone:
                ticks.remove(*gone)
                self.remove(*gone)
        gap = BraceBetweenPoints(ticks[0].get_top() + UP * 0.1, ticks[1].get_top() + UP * 0.1, direction=UP, color=ERROR)
        gap_tag = label('gap > 1¢', 34, ERROR).next_to(gap, UP, buff=0.12)
        self.at("a balance can")
        self.play(GrowFromCenter(gap), FadeIn(gap_tag, shift=DOWN * 0.2))
        card = end_card('Episode 2', 'Inside a double').move_to(DOWN * 2.2)
        self.play(FadeIn(card, shift=UP * 0.2))
        self.finish(extra=3.0)

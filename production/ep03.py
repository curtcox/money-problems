"""Episode 3 · Where it bites. One Scene per script segment.

    python3 production/render.py 3 [-ql] [segment ...]

Shot ids in comments ([V3.1a] ...) refer to episodes/03-where-it-bites.md. On-screen code and
console lines come from snippets/ep03/; figures that no snippet prints are computed here with
Python, and each one says so in a comment.
"""
import itertools
import math
import os
import random
import sys
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa: E402,F403

P1 = 'ep03/01-a-cent-a-million-times.py'
P2 = 'ep03/02-free-shipping-almost.py'
P3 = 'ep03/03-dollars-to-cents.py'
P4 = 'ep03/04-same-numbers-different-order.py'
P5 = 'ep03/05-challenge-risky-lines.py'


# ---------------------------------------------------------------- local helpers

if os.environ.get('LATE_CHECK'):
    # Review aid: report beats whose animations overran the phrase they wait for.
    _plain_at = Segment.at

    def _checked_at(self, phrase, occurrence=0, lead=0.0):
        late = self.renderer.time - (phrase_seconds(self.EPISODE, self.SEGMENT, phrase, occurrence) - lead)
        if late > 0.4:
            print(f'LATE {self.SEGMENT} {phrase!r} by {late:.1f}s', file=sys.stderr)
        _plain_at(self, phrase, occurrence, lead)

    Segment.at = _checked_at


def show_qr(scene, qr_id):
    """Fade a QR card in and remember when, so hide_qr can honour the minimum hold."""
    card = qr_card(qr_id)
    scene.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)
    card.shown_at = scene.renderer.time
    return card


def hide_qr(scene, card, hold=8.0):
    """Fade a QR card out, first waiting until it has been fully visible for `hold` seconds."""
    remaining = hold - (scene.renderer.time - card.shown_at)
    if remaining > 0:
        scene.wait(remaining)
    scene.play(FadeOut(card), run_time=0.5)


def value_after(line, key):
    """The first whitespace-delimited field after key in a printed output line."""
    return line.split(key, 1)[1].split()[0]


def tail_from(line, start):
    """Glyphs of a MonoLine from source index start to the end of its last field."""
    return line.chars(start, len(line.source.rstrip()))


def looping_arrow(radius=0.32, color=FOCUS):
    arc = Arc(radius=radius, start_angle=PI * 0.6, angle=-TAU * 0.8, color=color, stroke_width=4)
    arc.add_tip(tip_length=0.14, tip_width=0.14)
    return arc


def card_icon(width, height):
    return RoundedRectangle(width=width, height=height, corner_radius=0.08).set_stroke(SCAFFOLD, 3)


def balance_icon():
    book = card_icon(1.5, 1.1)
    bars = VGroup(*[Line(LEFT * 0.5, RIGHT * 0.5, color=GREY_C, stroke_width=3) for _ in range(3)])
    bars.arrange(DOWN, buff=0.18).move_to(book).shift(LEFT * 0.12)
    up = Arrow(DOWN * 0.3, UP * 0.3, buff=0, color=EXACT, stroke_width=4).next_to(bars, RIGHT, buff=0.1)
    return VGroup(book, bars, up)


def items_icon():
    paper = receipt([('-', ''), ('-', ''), ('-', ''), ('-', '')], width=1.2, font_size=18)
    return paper


def calendar_icon():
    page = card_icon(1.5, 1.2)
    top = Rectangle(width=1.5, height=0.25).set_fill(ERROR, 0.8).set_stroke(width=0).align_to(page, UP)
    cells = VGroup(*[Square(0.13).set_stroke(GREY_C, 1) for _ in range(21)])
    cells.arrange_in_grid(rows=3, cols=7, buff=0.05).move_to(page).shift(DOWN * 0.12)
    return VGroup(page, top, cells)


def report_icon():
    page = card_icon(1.3, 1.3)
    rows = VGroup(*[Line(LEFT * 0.45, RIGHT * 0.45, color=GREY_C, stroke_width=2) for _ in range(5)])
    rows.arrange(DOWN, buff=0.14).move_to(page).shift(UP * 0.08)
    column = Rectangle(width=0.3, height=0.85).set_fill(FOCUS, 0.25).set_stroke(width=0).move_to(rows).shift(RIGHT * 0.25)
    total = Line(LEFT * 0.45, RIGHT * 0.45, color=MONEY, stroke_width=4).next_to(rows, DOWN, buff=0.1)
    return VGroup(page, column, rows, total)


def cart_icon():
    color = SCAFFOLD
    basket = Polygon([-1.3, 0.55, 0], [1.3, 0.55, 0], [1.0, -0.55, 0], [-1.0, -0.55, 0]).set_stroke(color, 5)
    handle = Line([-1.3, 0.55, 0], [-1.75, 1.05, 0], color=color, stroke_width=5)
    grip = Line([-1.75, 1.05, 0], [-2.1, 1.05, 0], color=color, stroke_width=5)
    wheels = VGroup(*[Circle(radius=0.17).set_stroke(color, 5).move_to([x, -0.85, 0]) for x in (-0.7, 0.7)])
    return VGroup(basket, handle, grip, wheels)


def status_light(color=ERROR):
    glow = VGroup(*[Circle(radius=r).set_fill(color, o).set_stroke(width=0) for r, o in ((0.5, 0.15), (0.38, 0.3))])
    lamp = Circle(radius=0.26).set_fill(color, 1).set_stroke(WHITE, 2)
    return VGroup(glow, lamp)


# ---------------------------------------------------------------- 3.1

class Segment_3_1(Segment):
    """Cold open: a cent, a million times (q03-01)."""
    EPISODE, SEGMENT = 3, '3.1'

    def construct(self):
        lines = snippet_output(P1)

        # [V3.1a] a gold cent drops into a jar, then another, faster and faster; a counter climbs
        pot = jar(2.2, 2.4).move_to(LEFT * 2.2 + DOWN * 0.4)
        count = number(0, font_size=56, color=MONEY, commas=True).next_to(pot, RIGHT, buff=1.2)
        unit = Text('cent', font_size=40, color=MONEY)
        unit.add_updater(lambda m: m.next_to(count, RIGHT, buff=0.25, aligned_edge=DOWN))
        self.play(FadeIn(pot), FadeIn(count), FadeIn(unit), run_time=0.5)
        pile = VGroup()

        def drop(value, run_time):
            cent = penny(0.3).move_to(pot.get_top() + UP * 1.3)
            layer, slot = divmod(len(pile), 3)
            spot = pot[0].get_bottom() + UP * (0.35 + 0.17 * layer) + RIGHT * 0.55 * (slot - 1)
            self.play(cent.animate.move_to(spot), run_time=run_time, rate_func=rate_functions.ease_in_quad)
            if len(pile) < 24:
                pile.add(cent)
            else:
                self.remove(cent)
            count.set_value(value)
            if value == 2:
                unit.become(Text('cents', font_size=40, color=MONEY))

        drop(1, 0.8)
        self.at('And another')
        drop(2, 0.6)
        self.at('And keep going')
        shown = [3, 4, 5, 6, 7, 8, 10, 12, 15, 18, 22, 27, 33, 40, 48, 57, 67, 78, 89, 100]
        for k, value in enumerate(shown):
            drop(value, max(0.12, 0.55 - 0.03 * k))
        self.add(pile)

        # [V3.1b] code panel q03-01; the console prints one line at each checkpoint, the jar's
        # label shows the total
        self.at('After a hundred cents')
        code = code_panel(snippet_lines(P1, 4, 6), font_size=22).to_corner(UL, buff=0.4)
        out = output_console(P1, font_size=18)
        out.to_edge(LEFT, buff=0.5).set_y(1.2 - out.height / 2)
        money = VGroup(pot, pile, count, unit)
        self.play(money.animate.scale(0.5).move_to(RIGHT * 3.0 + UP * 2.9), FadeIn(code), FadeIn(out.background))
        card = show_qr(self, 'q03-01')

        label = None

        def checkpoint(i, cents):
            nonlocal label
            anims = [out.type_line(i)]
            # The jar's label: the total field of this line of q03-01's output.
            new = code_text('total ' + value_after(lines[i], 'total '), font_size=20, color=MONEY)
            new.next_to(money, DOWN, buff=0.25).align_to(money, LEFT)
            anims.append(FadeIn(new) if label is None else ReplacementTransform(label, new))
            self.play(ChangeDecimalToValue(count, cents, run_time=0.6, rate_func=rate_functions.ease_in_quad))
            self.play(*anims, run_time=0.8)
            label = new

        self.at('the total should be one dollar')
        checkpoint(0, 100)
        self.at('After a thousand cents')
        checkpoint(1, 1_000)
        self.at('After ten thousand')
        checkpoint(2, 10_000)
        checkpoint(3, 100_000)
        self.at('And after a million cents')
        checkpoint(4, 1_000_000)
        final = out.lines[4]
        total_text = value_after(lines[4], 'total ')
        start = final.source.index(total_text)
        self.at('and about seventeen millionths')
        tail = final.chars(start + total_text.index('.') + 1, start + len(total_text))
        self.play(tail.animate.set_color(ERROR), run_time=0.6)
        hide_qr(self, card)

        # [V3.1c] the "off by" column lights up; a needle wobbles either side of zero, wider each time
        self.at('Watch the error column', lead=0.9)
        self.play(FadeOut(VGroup(code, money, label)), out.animate.to_edge(UP, buff=0.4), run_time=0.7)
        tail.set_color(GREY_A)
        values = [value_after(l, 'off by ') for l in lines]
        parts = [out.lines[i].part(v) for i, v in enumerate(values)]
        pivot = LEFT * 3.4 + DOWN * 3.5
        zero = DashedLine(pivot, pivot + UP * 3.2, color=SCAFFOLD, dash_length=0.12)
        zero_label = Text('0', font_size=26, color=SCAFFOLD).next_to(zero, UP, buff=0.1)
        signs = VGroup(Text('+', font_size=40, color=STORED).move_to(pivot + RIGHT * 2.2 + UP * 2.6),
                       Text('−', font_size=40, color=ERROR).move_to(pivot + LEFT * 2.2 + UP * 2.6))
        needle = Line(pivot, pivot + UP * 2.8, color=FOCUS, stroke_width=7)
        hub = Dot(pivot, radius=0.1, color=FOCUS)
        caption_off = Text('off by', font_size=26, color=SCAFFOLD).move_to(RIGHT * 0.6 + DOWN * 1.2)
        self.play(FadeIn(zero), FadeIn(zero_label), FadeIn(signs), Create(needle), FadeIn(hub), FadeIn(caption_off),
                  run_time=0.6)
        readout = None
        angle_now = 0.0
        ghosts = VGroup()
        self.add(ghosts)
        for i, value in enumerate(values):
            if i == 1:
                self.at('It wobbles')
            number_value = Decimal(value)        # the off-by figure printed by q03-01
            # The same figure written out in full, so its digits creep left from line to line.
            spelled = ('+' if number_value > 0 else '−') + format(abs(number_value), 'f')
            row = code_text(spelled, font_size=30, color=STORED if number_value > 0 else ERROR)
            row.set_anchor(caption_off.get_left() + DOWN * 0.7)
            # Swing angle grows with the size of the error (log scale), sign from the output.
            target = (12 + (math.log10(abs(float(number_value))) + 16) * 7) * DEGREES
            target = -target if number_value > 0 else target
            ghost = needle.copy().set_stroke(DIM, 4)
            ghosts.add(ghost)
            flash = EXACT if i == 0 else FOCUS
            anims = [Rotate(needle, target - angle_now, about_point=pivot),
                     parts[i].animate.set_color(flash)]
            anims.append(FadeIn(row) if readout is None else ReplacementTransform(readout, row))
            self.play(*anims, run_time=0.9)
            if i == 0:
                self.play(parts[0].animate.set_color(GREY_A), run_time=0.4)
            angle_now = target
            readout = row
            if i >= 1:
                self.wait(0.6)

        # [V3.1d] the final total enlarges; the tail glows red
        self.at('those roundings')
        big = code_text(total_text, font_size=64, color=WHITE).move_to(UP * 0.3)
        source = final.part(total_text).copy()
        self.play(FadeOut(VGroup(zero, zero_label, signs, needle, hub, ghosts, readout, caption_off)),
                  out.animate.set_opacity(0.25), run_time=0.6)
        self.play(ReplacementTransform(source, big.glyphs), run_time=1.0)
        big_tail = big.chars(total_text.index('.') + 1)
        self.play(big_tail.animate.set_color(ERROR), run_time=0.6)
        glow = SurroundingRectangle(big_tail, color=ERROR, buff=0.12, corner_radius=0.1)
        self.play(Create(glow))
        self.at('we go looking for trouble')
        title = Text('Where it bites', font_size=60, weight=BOLD).next_to(big, DOWN, buff=1.0)
        self.play(FadeOut(out), Write(title), run_time=1.4)
        self.finish()


# ---------------------------------------------------------------- 3.2

class Segment_3_2(Segment):
    """Situation 1: accumulation."""
    EPISODE, SEGMENT = 3, '3.2'

    def construct(self):
        # [V3.2a] the float line; the running total hops right a cent at a time and snaps to a tick
        heading = Text('situation 1: accumulation', font_size=34, color=FOCUS).to_edge(UP, buff=0.4)
        y = 0.5
        left, right = -6.2, 6.2
        hop = 1.45                                  # one cent, drawn this wide
        axis = Line([left, y, 0], [right, y, 0], color=SCAFFOLD, stroke_width=2)

        def tick_row(gap):
            xs = np.arange(left + 0.3, right, gap)
            return VGroup(*[Line(DOWN * 0.18, UP * 0.18, color=STORED, stroke_width=3).move_to([x, y, 0]) for x in xs])

        ticks = tick_row(0.32)
        # Real gaps between doubles, computed here with math.ulp (the line itself is not to scale).
        near = Text('total near $1', font_size=26, color=SCAFFOLD).move_to([left + 1.7, y + 1.5, 0])
        gap_text = Text(f'gap between doubles: {math.ulp(1.0):.1e}', font_size=24, color=STORED)
        gap_text.next_to(near, RIGHT, buff=0.8)
        note = Text('ticks not to scale', font_size=18, color=DIM).to_corner(DR, buff=0.4)
        tally_label = Text('rounding errors so far', font_size=24, color=SCAFFOLD).move_to([left + 1.6, -1.6, 0])
        tally = VGroup()
        tally_x = [left + 3.6]
        diamond = Square(0.24).rotate(PI / 4).set_fill(FOCUS, 1).set_stroke(width=0).move_to([left + 0.3, y + 0.42, 0])
        self.play(FadeIn(heading), Create(axis), FadeIn(ticks, lag_ratio=0.02), FadeIn(near), FadeIn(gap_text),
                  FadeIn(note), run_time=1.2)
        self.play(FadeIn(diamond, shift=DOWN * 0.3), FadeIn(tally_label), run_time=0.5)

        def hops(n, gap, step_time):
            for _ in range(n):
                stored = diamond.get_x()
                true = stored + hop
                base = ticks[0].get_x()
                snapped = base + round((true - base) / gap) * gap
                plus = Text('+1¢', font_size=22, color=MONEY).move_to([stored + hop / 2, y + 0.95, 0])
                self.play(diamond.animate(path_arc=-PI / 2).move_to([true, y + 0.42, 0]), FadeIn(plus),
                          run_time=step_time * 0.45)
                sliver = Line([true, y, 0], [snapped, y, 0], color=ERROR, stroke_width=10)
                self.play(diamond.animate.move_to([snapped, y + 0.42, 0]), Create(sliver), FadeOut(plus),
                          run_time=step_time * 0.3)
                width = max(abs(snapped - true), 0.04)
                bar = Rectangle(width=width, height=0.4).set_fill(ERROR, 1).set_stroke(width=0)
                bar.move_to([tally_x[0] + width / 2, -1.6, 0])
                tally_x[0] += width + 0.04
                self.play(ReplacementTransform(sliver, bar), run_time=step_time * 0.25)
                tally.add(bar)

        hops(6, 0.32, 1.6)

        # [V3.2b] zoom out: the ticks spread apart and the slivers get bigger
        self.at('As the total gets bigger')
        wide = tick_row(1.1)
        near_big = Text('total near $10,000', font_size=26, color=SCAFFOLD).move_to(near, aligned_edge=LEFT)
        gap_big = Text(f'gap between doubles: {math.ulp(10000.0):.1e}', font_size=24, color=STORED)
        gap_big.move_to(gap_text, aligned_edge=LEFT).next_to(near_big, RIGHT, buff=0.8)
        self.play(Transform(ticks, wide), diamond.animate.move_to([left + 0.3, y + 0.42, 0]),
                  ReplacementTransform(near, near_big), ReplacementTransform(gap_text, gap_big), run_time=2.0)
        self.at('so each addition can be off')
        hops(1, 1.1, 2.0)
        self.at('Adding a cent to a dollar')
        small = VGroup(*tally[:6])
        self.play(Indicate(small, color=FOCUS, scale_factor=1.3), run_time=1.0)
        self.at('Adding a cent to ten thousand')
        self.play(Indicate(VGroup(*tally[6:]), color=ERROR, scale_factor=1.2), run_time=1.0)
        hops(2, 1.1, 2.0)

        # [V3.2c] four icons, each with a looping arrow
        self.at('Where does this happen?')
        self.play(FadeOut(VGroup(axis, ticks, diamond, near_big, gap_big, tally, tally_label, note)), run_time=0.6)
        icons = [balance_icon(), items_icon(), calendar_icon(), report_icon()]
        names = ['running balance', 'loop over\nline items', 'daily interest', 'report summed\nrow by row']
        slots = VGroup(*[Rectangle(width=3.1, height=3.0).set_opacity(0) for _ in icons]).arrange(RIGHT, buff=0.25)
        slots.move_to(DOWN * 0.1)
        tiles = []
        cues = ['A running balance', 'A loop that adds', 'Interest calculated', 'A report that sums']
        for icon, name, slot, cue in zip(icons, names, slots, cues):
            self.at(cue)
            icon.scale_to_fit_height(1.8).move_to(slot).shift(UP * 0.4)
            loop = looping_arrow(0.38).next_to(icon, UR, buff=-0.05)
            text = Text(name, font_size=26, line_spacing=0.8).next_to(icon, DOWN, buff=0.4)
            self.play(FadeIn(icon, shift=UP * 0.2), FadeIn(text), Create(loop), run_time=0.6)
            self.play(Rotate(loop, -TAU, about_point=loop.get_center()), run_time=1.0)
            tiles.append(VGroup(icon, loop, text))
        self.play(*[Rotate(t[1], -TAU, about_point=t[1].get_center()) for t in tiles], run_time=1.2)

        # A million additions: off by less than a millionth, gone once rounded to cents
        self.at('Now, after a million')
        self.play(FadeOut(VGroup(*tiles)), run_time=0.6)
        line = output_line(P1, '1,000,000 cents')
        out = Console([line], font_size=22).move_to(UP * 1.2)
        self.play(FadeIn(out.background))
        self.play(out.type_line(0))
        off = value_after(line, 'off by ')
        self.play(out.part(0, off).animate.set_color(ERROR))
        self.at('Round to cents')
        total = value_after(line, 'total ')
        before = code_text(total, font_size=40).move_to(LEFT * 3.0 + DOWN * 1.0)
        before.chars(total.index('.') + 1).set_color(ERROR)
        rounded = code_text(f'{float(total):.2f}', font_size=40, color=EXACT)   # rounded here with Python
        arrow = Arrow(LEFT * 0.4, RIGHT * 0.9, color=SCAFFOLD).next_to(before, RIGHT, buff=0.3)
        rounded.next_to(arrow, RIGHT, buff=0.3)
        self.play(FadeIn(before))
        self.play(GrowArrow(arrow), TransformFromCopy(before.chars(0, total.index('.') + 3), rounded.glyphs),
                  before.chars(total.index('.') + 3).animate.set_opacity(0.2), run_time=1.2)

        # The seed: the tiny error meets one of the next situations
        self.at("It's the seed")
        seed = Dot(radius=0.14, color=ERROR).move_to(LEFT * 2.0 + DOWN * 2.6)
        seed_label = Text('the seed', font_size=30, color=ERROR).next_to(seed, LEFT, buff=0.3)
        self.play(FadeOut(VGroup(out, before, arrow, rounded)), FadeIn(seed, scale=3), FadeIn(seed_label))
        self.play(seed.animate.move_to(UP * 0.0 + LEFT * 2.0), seed_label.animate.next_to(UP * 0.0 + LEFT * 2.0, LEFT, buff=0.4),
                  run_time=1.0)
        self.at('meets one of the next situations')
        fence = DashedLine(UP * 1.4, DOWN * 1.4, color=FOCUS, dash_length=0.15).move_to(RIGHT * 1.8)
        fence_label = Text('the next situations', font_size=30, color=FOCUS).next_to(fence, RIGHT, buff=0.3)
        self.play(FadeIn(fence, shift=LEFT * 2), FadeIn(fence_label, shift=LEFT * 2))
        self.play(seed.animate.move_to(fence.get_center() + LEFT * 0.25), run_time=0.8)
        self.play(Flash(seed, color=ERROR, flash_radius=0.4))
        self.finish()


# ---------------------------------------------------------------- 3.3

class Segment_3_3(Segment):
    """Situation 2: comparisons and thresholds (q03-02)."""
    EPISODE, SEGMENT = 3, '3.3'

    def construct(self):
        heading = Text('situation 2: comparisons', font_size=34, color=FOCUS).to_edge(UP, buff=0.4)
        self.play(FadeIn(heading))

        # A rule with a line in it: an amount slides up to a threshold
        self.at('rules with a line')
        track = Line(LEFT * 5.5, RIGHT * 5.5, color=SCAFFOLD, stroke_width=3).shift(DOWN * 0.2)
        fence = DashedLine(UP * 1.0, DOWN * 1.0, color=FOCUS, dash_length=0.12).move_to(track).shift(RIGHT * 1.5)
        no = Text('no', font_size=28, color=ERROR).move_to(LEFT * 2.0 + UP * 0.6)
        yes = Text('yes', font_size=28, color=EXACT).move_to(RIGHT * 3.5 + UP * 0.6)
        dot = Dot(radius=0.14, color=MONEY).move_to(track.get_start())
        self.play(Create(track), FadeIn(fence), FadeIn(no), FadeIn(yes), FadeIn(dot), run_time=0.8)
        self.play(dot.animate.move_to(fence.get_center() + LEFT * 0.4), run_time=1.6, rate_func=rate_functions.ease_out_quad)
        rule = None
        for cue, text in (('Free shipping at fifty', 'free shipping at $50.00'), ('A credit limit', 'a credit limit'),
                          ('A balance that must', "a balance that can't go below $0.00"),
                          ('A payment that should', 'a payment that must equal the amount due')):
            self.at(cue)
            new = Text(text, font_size=28).move_to(DOWN * 1.6)
            self.play(FadeIn(new, shift=UP * 0.2) if rule is None else ReplacementTransform(rule, new),
                      dot.animate.shift(RIGHT * 0.25 if rule is None else RIGHT * 0.0), run_time=0.6)
            rule = new
        self.play(dot.animate.move_to(fence.get_center() + RIGHT * 0.4).set_color(EXACT), run_time=0.8)

        # [V3.3a] a cart with three tags and the free-shipping banner
        self.at("Here's a cart")
        self.play(FadeOut(VGroup(track, fence, no, yes, dot, rule)), FadeOut(heading), run_time=0.5)
        banner = label_box('Free shipping on orders of $50.00 or more', color=EXACT, font_size=28, fill=EXACT)
        banner.to_edge(UP, buff=0.35)
        cart = cart_icon().scale(0.8).move_to(LEFT * 4.6 + UP * 0.9)
        # The cart's prices, as q03-02 lists them.
        prices = snippet_find(P2, 'cart =').split('[')[1].rstrip(']').split(', ')
        tags = VGroup(*[price_tag(f'${float(p):.2f}', font_size=24).rotate(0.12 * (k - 1)) for k, p in enumerate(prices)])
        tags.arrange(RIGHT, buff=0.12).next_to(cart, UP, buff=0.15)
        self.play(FadeIn(banner, shift=DOWN * 0.2), FadeIn(cart), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.6) for t in tags], lag_ratio=0.5), run_time=1.0)
        self.at("That's exactly fifty dollars")
        exact = sum(Decimal(p) for p in prices)                 # exact decimal sum, computed here
        equals = Text(f'= ${exact:.2f} exactly', font_size=28, color=EXACT).next_to(cart, DOWN, buff=0.45)
        self.play(Write(equals), run_time=0.8)

        # [V3.3b] code panel q03-02; the console prints the subtotal, then $50.00 in green
        self.at('Add them up in a float')
        code = code_panel(snippet_lines(P2, 7, 12), font_size=20).to_edge(LEFT, buff=0.4).to_edge(DOWN, buff=0.4)
        out = output_console(P2, font_size=22).next_to(banner, DOWN, buff=0.6).to_edge(RIGHT, buff=0.4)
        self.play(VGroup(cart, tags, equals).animate.scale(0.75).move_to(LEFT * 4.6 + UP * 1.6), run_time=0.6)
        self.play(FadeIn(code), FadeIn(out.background), run_time=0.6)
        card = show_qr(self, 'q03-02')
        loop_box = line_highlight(code, 2)
        self.play(Create(loop_box), run_time=0.4)
        self.at('forty-nine point nine')
        self.play(out.type_line(0, run_time=1.2))
        self.at('Format it to two decimal places')
        self.play(out.type_line(1, run_time=0.9))
        self.at('and it shows fifty dollars')
        self.play(out.lines[1].part('$50.00').animate.set_color(EXACT).scale(1.25), run_time=0.5)
        self.play(out.lines[1].part('$50.00').animate.scale(1 / 1.25), run_time=0.4)
        self.at('But the comparison sees')
        box = line_highlight(code, 5)
        self.play(Create(box))
        self.play(out.lines[0].part(value_after(snippet_output(P2)[0], 'subtotal: ')).animate.set_color(ERROR))

        # [V3.3c] the last line prints; $0.00 pulses red
        self.at('cheerfully tells them')
        self.play(out.type_line(2, run_time=1.0))
        zero = out.lines[2].part('$0.00')
        self.play(zero.animate.set_color(ERROR).scale(1.4), run_time=0.4)
        self.play(zero.animate.scale(1 / 1.4), run_time=0.4)
        self.play(zero.animate.scale(1.4), run_time=0.4)
        self.play(zero.animate.scale(1 / 1.4), run_time=0.4)

        # [V3.3d] the float line near 50: the subtotal sits on the tick just left of 50.0
        self.at('This is the most dangerous')
        hide_qr(self, card)
        self.play(FadeOut(VGroup(code, box, loop_box, out, cart, tags, equals, banner)), run_time=0.6)
        subtotal = float(value_after(snippet_output(P2)[0], 'subtotal: '))
        ulp = Fraction(math.ulp(subtotal))         # the gap between doubles here, from math.ulp
        line = FloatLine(Fraction(50) - ulp * Fraction(5, 2), Fraction(50) + ulp * Fraction(5, 2), width=12.0)
        line.move_to(UP * 0.6)
        below = code_text(repr(subtotal), font_size=24, color=SCAFFOLD)
        below.next_to(line.point(subtotal), DOWN, buff=0.4).align_to(line.point(subtotal) + RIGHT * 0.8, RIGHT)
        at50 = code_text(repr(50.0), font_size=24, color=SCAFFOLD).next_to(line.point(50), DOWN, buff=0.4)
        line.labels.add(below, at50)
        line.add(below, at50)
        threshold = DashedLine(line.point(50) + DOWN * 0.6, line.point(50) + UP * 1.6, color=EXACT, dash_length=0.1)
        free = Text('free shipping from here', font_size=22, color=EXACT).next_to(threshold, UP, buff=0.1)
        self.play(Create(line.axis), LaggedStart(*[Create(t) for t in line.ticks], lag_ratio=0.15),
                  FadeIn(line.labels), run_time=1.2)
        self.play(Create(threshold), FadeIn(free))
        diamond = line.diamond(subtotal)
        who = Text('subtotal', font_size=22, color=FOCUS).next_to(diamond, UP, buff=0.15)
        self.play(FadeIn(diamond, shift=DOWN * 0.4), FadeIn(who))
        less = Text('<', font_size=56, color=ERROR).move_to((line.point(subtotal) + line.point(50)) / 2 + UP * 0.45)
        self.play(FadeIn(less, scale=1.6))
        self.at("A threshold doesn't care")
        # The comparison and the miss, evaluated here with Python.
        test = code_text(f'{subtotal!r} >= 50.0  →  {subtotal >= 50.0}', font_size=28).move_to(DOWN * 1.6)
        test.part(str(subtotal >= 50.0)).set_color(ERROR)
        missed = Text(f'missed by {50.0 - subtotal:.1e}', font_size=24, color=ERROR).next_to(test, DOWN, buff=0.35)
        self.play(FadeIn(test, shift=UP * 0.2))
        self.play(FadeIn(missed), Wiggle(less))
        line_group = VGroup(line, threshold, free, diamond, who, less)

        # [V3.3e] other thresholds slide in as labels
        self.at('And thresholds are exactly')
        self.play(FadeOut(VGroup(test, missed)), line_group.animate.scale(0.85).to_edge(UP, buff=0.5), run_time=0.8)
        names = ['credit limit', 'balance ≤ 0', 'payment == amount due', 'over the reporting limit?']
        labels = VGroup(*[label_box(n, color=FOCUS, font_size=26) for n in names])
        labels.arrange_in_grid(rows=2, cols=2, buff=(0.8, 0.5)).move_to(DOWN * 1.5)
        for k, cue in enumerate(['Every equals equals', 'every greater-than', 'every check against zero',
                                 'a sliver can flip']):
            self.at(cue)
            self.play(FadeIn(labels[k], shift=LEFT * 3), run_time=0.6)

        # Try the cart in a different order: every order, added up here with Python
        self.at('Try the cart in a different order')
        self.play(FadeOut(labels, shift=LEFT * 3), run_time=0.6)
        rows = VGroup()
        ticks_ok = []
        for order in itertools.permutations(prices):
            total = 0.0
            for p in order:
                total += float(p)
            text = code_text(' + '.join(order) + f'  =  {total!r}', font_size=22,
                             color=EXACT if total >= 50.0 else ERROR)
            mark = (checkmark(size=0.3) if total >= 50.0 else crossmark(size=0.26))
            if total >= 50.0:
                ticks_ok.append(mark)
            rows.add(VGroup(text, mark))
        for r in rows:
            r[1].next_to(r[0], RIGHT, buff=0.4)
        rows.arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to(DOWN * 1.3)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows], lag_ratio=0.35), run_time=2.4)
        self.at('Sometimes it comes out right')
        self.play(*[Indicate(m, color=EXACT, scale_factor=1.5) for m in ticks_ok])
        self.finish()


# ---------------------------------------------------------------- 3.4

class Segment_3_4(Segment):
    """Situation 3: dollars to cents, the wrong way (q03-03)."""
    EPISODE, SEGMENT = 3, '3.4'

    def construct(self):
        lines = snippet_output(P3)
        heading = Text('situation 3: conversion to cents', font_size=34, color=FOCUS).to_edge(UP, buff=0.4)
        self.play(FadeIn(heading))

        # Dollars on one side, whole cents on the other: the conversion goes between them
        first = lines[0]
        price = first.split()[0]
        self.at('count money in')
        stack = VGroup(*[penny(0.22) for _ in range(5)]).arrange(RIGHT, buff=-0.12)
        cents_label = Text('whole cents', font_size=26, color=MONEY).next_to(stack, DOWN, buff=0.25)
        goal = VGroup(stack, cents_label).move_to(RIGHT * 4.6 + DOWN * 1.8)
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.4) for c in stack], lag_ratio=0.2), FadeIn(cents_label),
                  run_time=1.0)
        self.at('take the dollar amount')
        tag = price_tag(f'${price}').move_to(LEFT * 5.9 + UP * 0.6)
        dollars_label = Text('dollars', font_size=26, color=MONEY).next_to(tag, DOWN, buff=0.25)
        self.play(FadeIn(tag, shift=RIGHT * 0.4), FadeIn(dollars_label), run_time=0.6)

        # [V3.4a] $0.29 goes into "× 100", comes out 28.999999999999996, then "int" chops it to 28
        times = label_box('× 100', font_size=34, color=STORED).move_to(LEFT * 3.9 + UP * 0.6)
        chop = label_box('int', font_size=34, color=ERROR).move_to(RIGHT * 4.2 + UP * 0.6)
        self.at('multiply by a hundred')
        self.play(FadeIn(times, scale=0.8))
        self.at('turn it into an integer')
        self.play(FadeIn(chop, scale=0.8))
        self.at('Twenty-nine cents')
        self.play(FadeOut(dollars_label), run_time=0.3)
        self.play(tag.animate.move_to(times).scale(0.3).set_opacity(0), run_time=0.6)
        self.remove(tag)
        self.at('Times a hundred is')
        product = value_after(first, '= ')
        middle = code_text(product, font_size=30, color=STORED).move_to(RIGHT * 0.15 + UP * 0.6)
        self.play(FadeIn(middle, shift=RIGHT * 0.5), run_time=0.8)
        self.at('was stored slightly')
        # What 0.29 really is as a double, computed here with Decimal.
        stored = str(Decimal(float(price)))[:22] + '…'
        note = Text(f'{price} is stored as {stored}', font_size=24, color=STORED).move_to(DOWN * 1.2)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.at("And int doesn't round")
        self.play(middle.animate.next_to(chop, LEFT, buff=0.2), run_time=0.6)
        self.at('It chops off everything')
        point = product.index('.')
        dropped = middle.chars(point)
        kept = middle.chars(0, point)
        self.play(dropped.animate.shift(DOWN * 1.0).set_color(ERROR).set_opacity(0), run_time=0.9)
        self.at('Twenty-eight. A', lead=0.6)
        result = value_after(first, 'int: ')
        whole = code_text(result, font_size=40, color=ERROR).next_to(chop, DOWN, buff=0.5)
        lost = penny(0.3).next_to(whole, RIGHT, buff=0.3)
        self.play(ReplacementTransform(kept, whole.glyphs), FadeIn(lost, scale=0.5), run_time=0.5)

        # [V3.4b] code panel q03-03; the console prints the five price rows, int results in red
        self.at('A dollar fifteen')
        code = code_panel(snippet_lines(P3, 4, 5), font_size=18).to_edge(UP, buff=0.35)
        out = output_console(P3, font_size=18)
        out.next_to(code, DOWN, buff=0.35).to_edge(LEFT, buff=0.4)
        self.play(Rotate(lost, -4 * PI), lost.animate.shift(RIGHT * 4 + DOWN * 0.5), run_time=0.8,
                  rate_func=rate_functions.ease_in_quad)
        self.remove(lost)
        self.play(FadeOut(VGroup(times, chop, middle, dropped, whole, note, heading, goal)), FadeIn(code),
                  FadeIn(out.background), run_time=0.5)
        card = show_qr(self, 'q03-03')
        ints = []
        for i in range(5):
            ints.append(out.lines[i].chars(out.lines[i].source.index('int: ') + 5))
        self.play(Succession(*[out.type_line(i, run_time=0.45) for i in range(3)]), run_time=1.35)
        self.play(*[ints[i].animate.set_color(ERROR) for i in range(3)], run_time=0.3)
        self.at('Nineteen ninety-nine becomes')
        for i in (3, 4):
            self.play(out.type_line(i, run_time=0.7))
            self.play(ints[i].animate.set_color(ERROR), run_time=0.25)
        self.at('and it loses')
        coins = VGroup(*[penny(0.16).next_to(ints[i], RIGHT, buff=0.25) for i in range(5)])
        self.play(LaggedStart(*[FadeIn(c, scale=0.5) for c in coins], lag_ratio=0.15), run_time=0.6)
        self.play(LaggedStart(*[c.animate.shift(RIGHT * 2.0).set_opacity(0) for c in coins], lag_ratio=0.15),
                  run_time=1.2)
        self.remove(coins)

        # [V3.4c] every amount $0.00–$99.99 as a 100 × 100 grid; the ones int() gets wrong turn red
        self.at('How often?', lead=0.6)
        hide_qr(self, card)
        self.play(FadeOut(code), out.animate.to_edge(UP, buff=0.5).to_edge(RIGHT, buff=0.35), run_time=0.8)
        cell = 0.05
        origin = np.array([-6.2, 2.6, 0])              # top-left corner of the grid
        rows_bg = VGroup(*[Rectangle(width=cell * 100, height=cell).set_fill(GREY_E, 1).set_stroke(width=0)
                           .move_to(origin + RIGHT * cell * 50 + DOWN * cell * (r + 0.5)) for r in range(100)])
        frame = Rectangle(width=cell * 100, height=cell * 100).set_stroke(GREY_C, 1)
        frame.move_to(origin + (RIGHT + DOWN) * cell * 50)
        guides = VGroup(*[Line(origin + DOWN * cell * 10 * k, origin + DOWN * cell * 10 * k + RIGHT * cell * 100,
                               color=BLACK, stroke_width=1) for k in range(1, 10)],
                        *[Line(origin + RIGHT * cell * 10 * k, origin + RIGHT * cell * 10 * k + DOWN * cell * 100,
                               color=BLACK, stroke_width=1) for k in range(1, 10)])
        row_labels = VGroup(*[Text(f'${10 * k}', font_size=18, color=SCAFFOLD)
                              .next_to(origin + DOWN * cell * (10 * k + 0.5), LEFT, buff=0.12) for k in range(10)])
        col_labels = VGroup(Text('.00', font_size=18, color=SCAFFOLD).next_to(origin + RIGHT * cell * 0.5, UP, buff=0.1),
                            Text('.99', font_size=18, color=SCAFFOLD).next_to(origin + RIGHT * cell * 99.5, UP, buff=0.1),
                            Text('cents →', font_size=18, color=SCAFFOLD).next_to(origin + RIGHT * cell * 50, UP, buff=0.1))
        self.at('The code checks every amount')
        self.play(FadeIn(frame), FadeIn(row_labels), FadeIn(col_labels),
                  LaggedStart(*[FadeIn(r) for r in rows_bg], lag_ratio=0.03), run_time=2.0)
        self.add(guides)
        # The real pattern: the same test q03-03 runs, cell by cell (row = dollars, column = cents).
        red = VGroup()
        wrong = 0
        for dollars in range(100):
            col = 0
            while col < 100:
                cents = dollars * 100 + col
                if int(cents / 100 * 100) != cents:
                    end = col
                    while end + 1 < 100 and int((dollars * 100 + end + 1) / 100 * 100) != dollars * 100 + end + 1:
                        end += 1
                    run = end - col + 1
                    wrong += run
                    rect = Rectangle(width=cell * run, height=cell).set_fill(ERROR, 1).set_stroke(width=0)
                    rect.move_to(origin + RIGHT * cell * (col + run / 2) + DOWN * cell * (dollars + 0.5))
                    red.add(rect)
                    col = end + 1
                else:
                    col += 1
        assert f'{wrong} of 10,000' in lines[5], 'the grid must match q03-03'
        self.at('Five hundred and seventy-three')
        self.play(LaggedStart(*[FadeIn(r) for r in red], lag_ratio=0.004), run_time=2.0)
        self.play(out.type_line(5, run_time=1.0))
        self.play(out.lines[5].part(str(wrong)).animate.set_color(ERROR))
        self.at('more than one in twenty')
        share = Text(f'{wrong} / 10,000 = {wrong / 100:.2f} %', font_size=28, color=ERROR)   # computed here
        share.next_to(out, DOWN, buff=0.5)
        self.play(FadeIn(share, shift=UP * 0.2))
        self.at('not random-looking')
        thirties = SurroundingRectangle(VGroup(rows_bg[30], rows_bg[31]), color=FOCUS, buff=0.03)
        thirties_label = Text('the $30s: none at all', font_size=24, color=FOCUS)
        thirties_label.next_to(out, DOWN, buff=0.5).set_y(-2.6)
        pointer = Line(thirties_label.get_left() + LEFT * 0.1, thirties.get_right(), color=FOCUS, stroke_width=2)
        self.play(Create(thirties), FadeIn(thirties_label), Create(pointer))
        self.at('always in the same direction')
        down = Text('every one: 1¢ short', font_size=26, color=ERROR).next_to(share, DOWN, buff=0.35)
        arrow = Arrow(UP * 0.4, DOWN * 0.4, buff=0, color=ERROR).next_to(down, LEFT, buff=0.2)
        self.play(FadeIn(down), GrowArrow(arrow), red.animate.shift(DOWN * cell * 0.3), run_time=0.6)
        self.play(red.animate.shift(UP * cell * 0.3), run_time=0.4)

        # [V3.4d] the round() line prints 0: every red cell turns green
        self.at('Not one of the ten thousand')
        self.play(FadeOut(VGroup(thirties, thirties_label, pointer)), out.type_line(6, run_time=1.0))
        self.play(out.lines[6].part('0', 0).animate.set_color(EXACT),
                  red.animate.set_fill(EXACT, 1), FadeOut(VGroup(share, down, arrow)), run_time=1.2)
        self.at('round fixes the conversion')
        moral = VGroup(Text('round() fixes the conversion,', font_size=28, color=EXACT),
                       Text('not the float', font_size=28, color=ERROR)).arrange(DOWN, buff=0.2)
        moral.next_to(out, DOWN, buff=0.8)
        self.play(FadeIn(moral[0], shift=UP * 0.2))
        self.play(FadeIn(moral[1], shift=UP * 0.2))
        self.finish()


# ---------------------------------------------------------------- 3.5

def half_up(value):
    """Round a decimal string to cents the way most of us expect: halves go up."""
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class Segment_3_5(Segment):
    """Situation 4: multiplying by rates."""
    EPISODE, SEGMENT = 3, '3.5'

    def construct(self):
        heading = Text('situation 4: multiplying by rates', font_size=34, color=FOCUS).to_edge(UP, buff=0.4)
        self.play(FadeIn(heading))

        # [V3.5a] a receipt: a subtotal, then rate lines whose products trail long grey tails
        base = float(output_line(P3, '19.99').split()[0])       # $19.99, one of q03-03's prices
        # Illustrative rates from the script; each product is computed here with Python floats.
        rates = [('tax 8.25%', base * 0.0825), ('discount 15%', base * 0.15),
                 ('interest 3.5% ÷ 365', base * (0.035 / 365)), ('converted at 0.9187', base * 0.9187)]
        rows = [('Subtotal', f'{base:.2f}'), ('-', '')] + [(label, repr(v)) for label, v in rates]
        bill = receipt(rows, width=8.2, font_size=20, title='RECEIPT').move_to(LEFT * 2.3 + UP * 0.3)
        lines = [l for l in bill.rows if l is not None]
        for line in lines[1:]:
            line.set_opacity(0)
        self.play(FadeIn(bill.paper), FadeIn(bill.lines[0]), FadeIn(bill.lines[1]), FadeIn(bill.lines[2]), run_time=0.6)
        tails = []
        for (label, value), cue in zip(rates, ['sales tax', 'commissions', 'Multiply a price', 'usually has more']):
            self.at(cue)
            line = lines[rates.index((label, value)) + 1]
            amount = repr(value)
            start = len(line.source) - len(amount)
            tail = line.chars(start + amount.index('.') + 3)
            self.play(line.animate.set_opacity(1), run_time=0.5)
            self.play(tail.animate.set_color(GREY), run_time=0.4)
            tails.append(tail)
        self.at('it has to be rounded')
        brackets = VGroup(*[SurroundingRectangle(t, color=FOCUS, buff=0.04) for t in tails])
        self.play(LaggedStart(*[Create(b) for b in brackets], lag_ratio=0.2), run_time=1.0)
        code = code_text(snippet_find(P5, 'tax = round'), font_size=24, color=GREY_A).move_to(DOWN * 3.2)
        self.play(FadeIn(code, shift=UP * 0.2))

        # The decision: which side of halfway is the answer on?
        self.at('That rounding is a decision')
        self.play(FadeOut(brackets), bill.animate.to_edge(LEFT, buff=0.3), run_time=0.8)
        tax = Decimal(repr(rates[0][1]))
        lo = tax.quantize(Decimal('0.01'), rounding='ROUND_FLOOR')
        hi = lo + Decimal('0.01')
        mini = FloatLine(Fraction(str(lo)), Fraction(str(hi)), width=4.0, ticks=[Fraction(str(lo)), Fraction(str(hi))],
                         labels={Fraction(str(lo)): str(lo), Fraction(str(hi)): str(hi)}, label_size=22)
        mini.move_to(RIGHT * 4.6 + UP * 0.3)
        mid = Fraction(str(lo + hi)) / 2
        half = DashedLine(mini.point(mid) + DOWN * 0.3, mini.point(mid) + UP * 0.3, color=SCAFFOLD, dash_length=0.06)
        half_label = Text('halfway', font_size=20, color=SCAFFOLD).next_to(half, DOWN, buff=0.15)
        marker = Dot(mini.point(Fraction(str(tax))), radius=0.09, color=FOCUS)
        self.play(Create(mini), FadeIn(half), FadeIn(half_label))
        self.play(FadeIn(marker, shift=DOWN * 0.3))
        self.at('which side of the halfway')
        # The tax figure rounds to its nearer cent: computed here with Decimal.
        goes = mini.point(Fraction(str(half_up(str(tax)))))
        snap = CurvedArrow(marker.get_center() + UP * 0.15, goes + UP * 0.15, angle=-PI / 2.5, color=FOCUS, tip_length=0.15)
        self.play(Create(snap))
        self.at('very close to half a cent')
        self.play(FadeOut(snap), marker.animate.move_to(mini.point(mid)), run_time=0.8)
        question = Text('?', font_size=40, color=FOCUS).next_to(marker, UP, buff=0.25)
        self.play(FadeIn(question))
        for shift in (LEFT, RIGHT * 2, LEFT * 2, RIGHT):
            self.play(marker.animate.shift(shift * 0.08), run_time=0.25)

        # [V3.5b] 1.00 to 1.01: the true value 1.005 is exactly halfway; the stored double sits a hair left
        self.at('Take one dollar and half a cent')
        self.play(FadeOut(VGroup(bill, mini, half, half_label, marker, question, code)), run_time=0.6)
        one, one01, value = Fraction('1.00'), Fraction('1.01'), Fraction('1.005')
        big = FloatLine(one, one01, width=11, ticks=[one, one01], labels={one: '1.00', one01: '1.01'},
                        label_size=30, tick_height=0.6).move_to(UP * 0.3)
        mid_tick = DashedLine(big.point(value) + DOWN * 0.45, big.point(value) + UP * 0.45, color=SCAFFOLD,
                              dash_length=0.08)
        diamond = big.diamond(value, size=0.3).shift(UP * 0.15)
        true_label = code_text('1.005', font_size=30, color=FOCUS).next_to(diamond, UP, buff=0.2)
        self.play(Create(big), FadeIn(mid_tick), run_time=0.8)
        self.play(FadeIn(diamond, shift=DOWN * 0.4), FadeIn(true_label))
        self.at('most of us expect')
        expected = CurvedArrow(diamond.get_right() + RIGHT * 0.1, big.point(one01) + UP * 0.4, angle=-PI / 3,
                               color=FOCUS, tip_length=0.18)
        expected_label = Text('expected: 1.01', font_size=24, color=FOCUS).next_to(expected, UP, buff=0.1)
        self.play(Create(expected), FadeIn(expected_label))
        self.at("Python's round gives")
        # round(1.005, 2) evaluated here with Python (fact check 3.5).
        verdict = code_text(f'round(1.005, 2) → {round(1.005, 2)!r}', font_size=34, color=STORED).move_to(DOWN * 2.6)
        stored = Dot(big.point(value) + LEFT * 0.18 + DOWN * 0.0, radius=0.11, color=STORED)   # offset exaggerated
        rounds = CurvedArrow(stored.get_center() + UP * 0.2, big.point(one) + UP * 0.4, angle=PI / 4,
                             color=STORED, tip_length=0.18)
        self.play(FadeIn(stored, scale=2), FadeIn(verdict, shift=UP * 0.2))
        self.play(Create(rounds), FadeOut(VGroup(expected, expected_label)))
        self.at('is a hair below it')
        # The stored double's exact value, from Decimal.
        exact_stored = str(Decimal(1.005))[:20] + '…'
        stored_label = Text(f'stored: {exact_stored}', font_size=24, color=STORED).move_to(DOWN * 1.3)
        hair = Text('(the hair is drawn much wider than it is)', font_size=18, color=DIM).next_to(stored_label, DOWN, buff=0.12)
        pointer = Line(stored.get_bottom(), stored_label.get_top(), color=STORED, stroke_width=2)
        self.play(FadeIn(stored_label), Create(pointer), FadeIn(hair))
        self.play(Indicate(stored, color=STORED, scale_factor=1.6))

        # [V3.5c] many near-halfway values: each one snaps the way its stored double leans
        self.at('Rates create these')
        self.play(FadeOut(VGroup(big, mid_tick, diamond, true_label, stored, rounds, verdict, stored_label, hair, pointer)),
                  run_time=0.6)
        values = ['1.005', '4.445', '2.675', '8.345', '0.285', '2.345', '1.115', '1.015']
        minis = VGroup()
        drops = []
        for text in values:
            v = Decimal(text)
            low = v.quantize(Decimal('0.01'), rounding='ROUND_FLOOR')
            high = low + Decimal('0.01')
            m = FloatLine(Fraction(str(low)), Fraction(str(high)), width=2.3, ticks=[Fraction(str(low)), Fraction(str(high))],
                          labels={Fraction(str(low)): str(low), Fraction(str(high)): str(high)}, label_size=20)
            centre = DashedLine(m.point(Fraction(text)) + DOWN * 0.22, m.point(Fraction(text)) + UP * 0.22,
                                color=SCAFFOLD, dash_length=0.05)
            minis.add(VGroup(m, centre))
        minis.arrange_in_grid(rows=2, cols=4, buff=(0.55, 1.6)).move_to(DOWN * 0.1)
        self.play(LaggedStart(*[FadeIn(m) for m in minis], lag_ratio=0.1), run_time=1.0)
        anims_land, anims_lean, anims_snap, flashes = [], [], [], []
        for text, group in zip(values, minis):
            m = group[0]
            v = Fraction(text)
            d = m.diamond(v, size=0.2)
            label = code_text(text, font_size=22, color=FOCUS).next_to(d, UP, buff=0.12)
            # Which way the stored double leans, and where round() sends it: computed here.
            lean = 1 if Decimal(float(text)) > Decimal(text) else -1
            got = round(float(text), 2)
            wrong = Decimal(repr(got)) != half_up(text)
            dot = Dot(m.point(v), radius=0.07, color=STORED)
            end = m.point(Fraction(repr(got)))
            arrow = Arrow(m.point(v) + lean * RIGHT * 0.12 + UP * 0.2, end + UP * 0.2, buff=0,
                          color=ERROR if wrong else EXACT, stroke_width=4, max_tip_length_to_length_ratio=0.2)
            anims_land.append(AnimationGroup(FadeIn(d, shift=DOWN * 0.6), FadeIn(label, shift=DOWN * 0.6)))
            anims_lean.append(AnimationGroup(FadeIn(dot), dot.animate.shift(lean * RIGHT * 0.12)))
            anims_snap.append(GrowArrow(arrow))
            if wrong:
                flashes.append(Flash(end, color=ERROR, flash_radius=0.3))
            group.add(d, label, dot, arrow)
        self.play(LaggedStart(*anims_land, lag_ratio=0.15), run_time=1.6)
        self.play(LaggedStart(*anims_lean, lag_ratio=0.1), run_time=1.0)
        self.play(LaggedStart(*anims_snap, lag_ratio=0.15), run_time=1.6)
        self.play(*flashes, run_time=0.8)
        self.at('Episode six is all about rounding')
        later = Text('more in episode 6: rounding', font_size=26, color=SCAFFOLD).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(later, shift=UP * 0.2))
        self.finish()


# ---------------------------------------------------------------- 3.6

class Segment_3_6(Segment):
    """Situation 5: same numbers, different order (q03-04)."""
    EPISODE, SEGMENT = 3, '3.6'

    def construct(self):
        heading = Text('situation 5: order of addition', font_size=34, color=FOCUS).to_edge(UP, buff=0.4)
        self.play(FadeIn(heading))

        # In school, order doesn't matter: A + B + C = C + B + A ... until floats
        self.at('In school')
        abc = VGroup(*[Text(t, font_size=56) for t in ('A', '+', 'B', '+', 'C')]).arrange(RIGHT, buff=0.3)
        abc.move_to(LEFT * 3.2)
        self.play(FadeIn(abc, lag_ratio=0.2))
        self.at('is the same as')
        cba = abc.copy().move_to(RIGHT * 3.2)
        equals = Text('=', font_size=56, color=EXACT)
        self.play(FadeIn(equals), TransformFromCopy(abc, cba), run_time=0.6)
        self.play(cba[0].animate.move_to(cba[4].get_center()), cba[4].animate.move_to(cba[0].get_center()), run_time=0.8)
        self.at('With floats')
        nope = Text('≠', font_size=56, color=ERROR)
        self.play(Transform(equals, nope))

        # [V3.6a] code panel q03-04's add_up; a deck of transaction cards shuffles
        self.at('Here are a thousand')
        self.play(FadeOut(VGroup(abc, cba, equals, heading)), run_time=0.4)
        code = code_panel(snippet_lines(P4, 6, 10), font_size=22).to_corner(UL, buff=0.4)
        # The first eight of q03-04's amounts, drawn here with the snippet's own seed and formula.
        rng = random.Random(2024)
        amounts = [rng.randint(-50_000, 100_000) / 100 for _ in range(1_000)][:8]
        cards = VGroup()
        for v in amounts:
            face = RoundedRectangle(width=1.05, height=0.7, corner_radius=0.08).set_fill(GREY_E, 1).set_stroke(MONEY, 2)
            label = Text(f'{v:.2f}', font_size=20, color=ERROR if v < 0 else WHITE).move_to(face)
            cards.add(VGroup(face, label))
        deck_spot = LEFT * 3.0 + DOWN * 2.2
        for k, c in enumerate(cards):
            c.move_to(deck_spot + UP * 0.04 * k + RIGHT * 0.02 * k)
        more = Text('… 1,000 in all', font_size=22, color=SCAFFOLD)
        self.play(FadeIn(code), FadeIn(cards, lag_ratio=0.1), run_time=0.6)
        left_half, right_half = cards[:4], cards[4:]
        self.play(left_half.animate.shift(LEFT * 1.3), right_half.animate.shift(RIGHT * 1.3), run_time=0.35)
        self.play(*[c.animate.move_to(deck_spot + UP * 0.04 * k) for k, c in enumerate(cards)], run_time=0.35)
        self.play(left_half.animate.shift(LEFT * 1.3), right_half.animate.shift(RIGHT * 1.3), run_time=0.3)
        self.play(*[c.animate.move_to(deck_spot + UP * 0.04 * k) for k, c in enumerate(cards)], run_time=0.3)

        # [V3.6b] the console prints three totals: in order, reversed, sorted; their tails differ
        out = output_console(P4, font_size=22)
        out.to_corner(UR, buff=0.4).shift(DOWN * 0.1)
        slots = [LEFT * 6.1 + DOWN * 2.3 + RIGHT * 1.2 * k for k in range(8)]

        def lay(order, run_time=1.0):
            self.play(*[cards[i].animate.move_to(slots[k] + RIGHT * 0.5) for k, i in enumerate(order)],
                      run_time=run_time)

        def tail(i):
            line = out.lines[i]
            value = line.source.split()[-1]
            start = len(line.source) - len(value)
            return line.chars(start + value.index('.') + 1)

        self.at('Add them up the plain way')
        self.play(FadeIn(out.background), run_time=0.4)
        card = show_qr(self, 'q03-04')
        lay(range(8))
        more.move_to((slots[0] + slots[7]) / 2 + RIGHT * 0.5 + DOWN * 0.75)
        self.play(FadeIn(more), out.type_line(0, run_time=1.0))
        self.at('ends in nine nine nine')
        self.play(tail(0).animate.set_color(ERROR))
        self.at('Reverse them')
        lay(list(reversed(range(8))))
        self.play(out.type_line(1, run_time=1.0))
        self.play(tail(1).animate.set_color(ERROR))
        self.at('Sort them')
        lay(sorted(range(8), key=lambda i: amounts[i]))
        self.play(out.type_line(2, run_time=1.0))
        self.play(tail(2).animate.set_color(ERROR))
        self.at('Three different totals')
        self.play(*[Indicate(tail(i), color=ERROR) for i in range(3)])

        # [V3.6c] sum(), math.fsum and exact cents all print 241354.0 in green
        self.at("Python's built-in sum")
        self.play(out.type_line(3, run_time=0.8))
        self.play(out.lines[3].chars(len(out.lines[3].source) - len(out.lines[3].source.split()[-1])).animate.set_color(EXACT))
        self.at('keeps track of the bits')
        bits = VGroup(*[Dot(radius=0.05, color=FOCUS) for _ in range(6)]).arrange(RIGHT, buff=0.12)
        bits.next_to(out.lines[3], DOWN, buff=0.05).shift(RIGHT * 2.5).set_opacity(0)
        self.play(bits.animate.set_opacity(1).shift(LEFT * 0.6), run_time=0.6)
        self.play(bits.animate.move_to(out.lines[3].get_right() + RIGHT * 0.3).scale(0.2).set_opacity(0), run_time=0.8)
        self.at('goes further')
        hide_qr(self, card)
        self.play(out.type_line(4, run_time=0.8))
        self.play(out.lines[4].chars(len(out.lines[4].source) - len(out.lines[4].source.split()[-1])).animate.set_color(EXACT))
        self.play(out.type_line(5, run_time=0.8))
        self.play(out.lines[5].chars(len(out.lines[5].source) - len(out.lines[5].source.split()[-1])).animate.set_color(EXACT))
        self.at('adds the plain way')
        plain = line_highlight(code, 3, color=ERROR)
        self.play(Create(plain))
        self.play(Indicate(out.lines[0], color=ERROR, scale_factor=1.05))

        # [V3.6d] a database query: the table split across four workers, then a final sum
        self.at('And order is something')
        self.play(FadeOut(VGroup(code, plain, out, cards, more)), run_time=0.6)
        rng = random.Random(2024)
        everything = [rng.randint(-50_000, 100_000) / 100 for _ in range(1_000)]
        colours = [STORED, TEAL, PURPLE_B, ORANGE]
        chips = VGroup(*[RoundedRectangle(width=1.1, height=0.32, corner_radius=0.05).set_fill(GREY_D, 1).set_stroke(width=0)
                         for _ in range(14)]).arrange(DOWN, buff=0.07)
        table_head = Text('amounts', font_size=22, color=SCAFFOLD)
        table = VGroup(table_head, chips).arrange(DOWN, buff=0.2).move_to(LEFT * 5.6 + UP * 0.1)
        table_more = Text('…', font_size=24, color=SCAFFOLD).next_to(chips, DOWN, buff=0.05)
        workers = VGroup()
        for k in range(4):
            box = RoundedRectangle(width=3.4, height=1.05, corner_radius=0.1).set_stroke(colours[k], 3)
            name = Text(f'worker {k + 1}', font_size=20, color=colours[k]).move_to(box).shift(UP * 0.25)
            workers.add(VGroup(box, name))
        workers.arrange(DOWN, buff=0.25).move_to(LEFT * 1.4 + UP * 0.1)
        final = RoundedRectangle(width=4.2, height=1.5, corner_radius=0.12).set_stroke(MONEY, 3).move_to(RIGHT * 4.3 + UP * 1.4)
        final_name = Text('total', font_size=24, color=MONEY).move_to(final).shift(UP * 0.4)
        links = VGroup(*[Arrow(w.get_right(), final.get_left(), buff=0.1, color=GREY_C, stroke_width=3,
                               max_tip_length_to_length_ratio=0.06) for w in workers])
        feed = VGroup(*[Arrow(chips.get_right(), w.get_left(), buff=0.1, color=GREY_D, stroke_width=2,
                              max_tip_length_to_length_ratio=0.06) for w in workers])
        self.play(FadeIn(table), FadeIn(table_more), FadeIn(final), FadeIn(final_name), run_time=0.6)
        self.at('split the work')
        self.play(LaggedStart(*[FadeIn(w) for w in workers], lag_ratio=0.2), Create(feed), run_time=1.0)

        def run_with(seed):
            # One possible split, computed here: shuffle the rows (seeded), deal them to four
            # workers, add each part the plain way, then add the four partial sums.
            idx = list(range(1_000))
            random.Random(seed).shuffle(idx)
            owner = {row: pos % 4 for pos, row in enumerate(idx)}
            parts = [[everything[row] for row in idx[k::4]] for k in range(4)]
            partials = []
            for part in parts:
                t = 0.0
                for a in part:
                    t += a
                partials.append(t)
            total = 0.0
            for p in partials:
                total += p
            return owner, partials, total

        history = VGroup()
        partial_texts = VGroup()
        total_text = None

        def show_run(seed, first=False):
            nonlocal partial_texts, total_text
            owner, partials, total = run_with(seed)
            recolour = [chips[r].animate.set_fill(colours[owner[r]], 0.9) for r in range(len(chips))]
            self.play(*recolour, run_time=0.8)
            texts = VGroup(*[code_text(repr(p), font_size=20, color=WHITE).move_to(workers[k][0]).shift(DOWN * 0.2)
                             for k, p in enumerate(partials)])
            self.play(FadeOut(partial_texts), FadeIn(texts), run_time=0.6)
            partial_texts = texts
            if first:
                self.play(Create(links), run_time=0.6)
            fresh = code_text(repr(total), font_size=26, color=MONEY).move_to(final).shift(DOWN * 0.2)
            flying = [t.copy() for t in texts]
            self.play(*[f.animate.move_to(fresh).set_opacity(0) for f in flying], run_time=0.8)
            self.remove(*flying)
            if total_text is not None:
                self.play(FadeOut(total_text), run_time=0.3)
            self.play(FadeIn(fresh), run_time=0.4)
            total_text = fresh
            row = code_text(f'run {len(history) + 1}:  {total!r}', font_size=20, color=GREY_A)
            value = repr(total)
            row.chars(len(row.source) - len(value) + value.index('.') + 1).set_color(ERROR)
            if len(history):
                row.next_to(history, DOWN, buff=0.2).align_to(history, LEFT)
            else:
                row.next_to(final, DOWN, buff=0.4).align_to(final, LEFT)
            self.play(FadeIn(row, shift=UP * 0.2), run_time=0.4)
            history.add(row)
            return total

        self.at('combine the pieces')
        totals = [show_run(0, first=True)]
        self.at('A distributed job')
        totals.append(show_run(2))
        self.at('run twice on the same data')
        totals.append(show_run(5))
        caption_order = Text('order not guaranteed', font_size=28, color=FOCUS).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(caption_order, shift=UP * 0.2))
        self.at('rounding to cents hides it')
        # The same three totals rounded to cents, here with Python: they agree again.
        cents = VGroup(*[code_text(f'run {k + 1}:  {t:.2f}', font_size=20, color=EXACT).move_to(h, aligned_edge=LEFT)
                         for k, (h, t) in enumerate(zip(history, totals))])
        self.play(*[ReplacementTransform(h, c) for h, c in zip(history, cents)], run_time=1.0)
        self.at('Occasionally')
        self.play(*[ReplacementTransform(c, h) for h, c in zip(history, cents)], run_time=0.8)
        self.at('nobody can explain')
        puzzle = Text('?', font_size=60, color=FOCUS).next_to(history, DOWN, buff=0.2)
        self.play(FadeIn(puzzle, scale=1.5))
        self.play(Wiggle(puzzle))
        self.finish()


# ---------------------------------------------------------------- 3.7

class Segment_3_7(Segment):
    """Situation 6: crossing boundaries."""
    EPISODE, SEGMENT = 3, '3.7'

    def construct(self):
        heading = Text('situation 6: crossing boundaries', font_size=34, color=FOCUS).to_edge(UP, buff=0.4)
        self.play(FadeIn(heading))

        # [V3.7a] a chain of systems; a gold $19.99 travels along the arrows
        names = ['web page (JavaScript)', 'JSON', 'API server', 'CSV export', 'spreadsheet', 'data frame']
        boxes = [label_box(n, font_size=26) for n in names]
        for b in boxes:
            b[0].stretch_to_fit_width(4.0).stretch_to_fit_height(1.1)
            b[1].move_to(b[0])
        top = VGroup(*boxes[:3]).arrange(RIGHT, buff=0.6).move_to(UP * 1.7)
        bottom = VGroup(*boxes[3:]).arrange(LEFT, buff=0.6).move_to(DOWN * 1.6)
        bottom.align_to(top, RIGHT)
        arrows = VGroup()
        order = boxes
        for a, b in zip(order, order[1:]):
            if abs(a.get_y() - b.get_y()) < 0.1:
                start, end = (a.get_right(), b.get_left()) if b.get_x() > a.get_x() else (a.get_left(), b.get_right())
            else:
                start, end = a[0].get_corner(DR) + LEFT * 0.3, b[0].get_corner(UR) + LEFT * 0.3
            arrows.add(Arrow(start, end, buff=0.08, color=GREY_C, stroke_width=3, max_tip_length_to_length_ratio=0.2))
        self.play(LaggedStart(*[FadeIn(b) for b in boxes], lag_ratio=0.15), run_time=1.2)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.15), run_time=1.0)
        self.at('It travels')
        amount = price_tag('$19.99', font_size=24).next_to(boxes[0], DOWN, buff=0.3)
        self.play(FadeIn(amount, scale=0.6), run_time=0.4)
        for k in range(1, 6):
            self.play(amount.animate.next_to(boxes[k], DOWN, buff=0.3), run_time=1.6)
            self.wait(0.4)

        # [V3.7b] wherever the amount becomes a binary float, a blue "float" badge snaps on and the
        # amount gains a faint grey tail of digits
        self.at('And at each crossing')
        self.play(FadeOut(amount), run_time=0.4)
        # The double nearest 19.99, written out here with Decimal.
        exact = str(Decimal(19.99))[:17] + '…'
        keep = 5                                       # '19.98' is where the two agree
        values = {}
        for k in range(6):
            t = Text('$19.99', font_size=24, color=MONEY).next_to(boxes[k], DOWN, buff=0.25).align_to(boxes[k], LEFT).shift(RIGHT * 0.1)
            values[k] = t
        self.play(*[FadeIn(values[k]) for k in range(6)], run_time=0.6)

        def badge_on(k):
            badge = label_box('float', color=STORED, font_size=20, fill=STORED, pad=0.12)
            badge.move_to(boxes[k][0].get_corner(UR)).shift(LEFT * 0.35 + UP * 0.05)
            tail = Text('$' + exact, font_size=24, color=MONEY)
            tail[keep + 1:].set_color(GREY_C)
            tail.move_to(values[k], aligned_edge=LEFT)
            self.play(FadeIn(badge, shift=DOWN * 0.4, scale=1.3), run_time=0.4)
            self.play(ReplacementTransform(values[k], tail), run_time=0.6)
            values[k] = tail
            return badge

        badges = VGroup()
        self.at('reads a number with a decimal point')
        badges.add(badge_on(2))
        self.at("JavaScript's")
        badges.add(badge_on(0))
        self.at('Spreadsheets store numbers')
        badges.add(badge_on(4))
        self.at('libraries that read')
        badges.add(badge_on(5))
        text_hops = VGroup(*[Text('text', font_size=20, color=SCAFFOLD).move_to(boxes[k][0].get_corner(UR))
                             .shift(LEFT * 0.35 + UP * 0.05) for k in (1, 3)])
        self.play(FadeIn(text_hops), run_time=0.4)

        # [V3.7c] zoom on the JSON hop: q03-05's json.loads line, and parse_float=Decimal instead
        self.at('So even if your own code')
        pair = VGroup(boxes[1], boxes[2], arrows[1], badges[0], text_hops[0], values[1], values[2])
        rest = VGroup(*[boxes[k] for k in (0, 3, 4, 5)], *[arrows[k] for k in (0, 2, 3, 4)], *badges[1:],
                      text_hops[1], *[values[k] for k in (0, 3, 4, 5)])
        home = pair.get_center()
        self.play(FadeOut(rest), FadeOut(heading), pair.animate.move_to(UP * 2.3), run_time=0.8)
        line = code_text(snippet_find(P5, 'json.loads(text)'), font_size=40, color=GREY_A).move_to(LEFT * 2.2 + UP * 0.0)
        note = label_box('items become floats', color=STORED, font_size=24, fill=STORED).next_to(line, RIGHT, buff=0.5)
        hint = snippet_find(P5, 'parse_float')
        better = hint[hint.index('json.loads'):hint.index(')') + 1]          # from q03-05's hint comment
        alt = code_text(better, font_size=36, color=EXACT).next_to(line, DOWN, buff=0.9).align_to(line, LEFT)
        alt_label = Text('instead: numbers stay exact', font_size=26, color=EXACT).next_to(alt, DOWN, buff=0.2).align_to(alt, LEFT)
        zoom = SurroundingRectangle(VGroup(boxes[1], boxes[2]), color=FOCUS, buff=0.08)
        self.play(Create(zoom))
        self.play(FadeIn(line, scale=0.5), run_time=0.8)
        self.play(FadeIn(note, shift=LEFT * 0.3))
        self.play(FadeIn(alt, shift=UP * 0.2), FadeIn(alt_label))

        # The least exact place
        self.at('A system is only as exact')
        self.play(FadeOut(VGroup(zoom, line, note, alt, alt_label)), pair.animate.move_to(home), run_time=0.8)
        self.play(FadeIn(rest), FadeIn(heading), run_time=0.6)
        weak = VGroup(*[SurroundingRectangle(boxes[k], color=ERROR, buff=0.06) for k in (0, 2, 4, 5)])
        self.play(LaggedStart(*[Create(w) for w in weak], lag_ratio=0.2), run_time=1.0)
        self.finish()


# ---------------------------------------------------------------- 3.8

class Segment_3_8(Segment):
    """Situation 7: very big, very small."""
    EPISODE, SEGMENT = 3, '3.8'

    def construct(self):
        heading = Text('situation 7: size', font_size=34, color=FOCUS).to_edge(UP, buff=0.4)
        divider = DashedLine(UP * 3.0, DOWN * 3.7, color=GREY_D, dash_length=0.12)
        self.play(FadeIn(heading), Create(divider))

        # [V3.8a] left, very big: a total races up toward the 32-bit "gap > 1¢" marker
        big_title = Text('very big', font_size=32).move_to(LEFT * 3.6 + UP * 2.6)
        # A float32 has 24 significant bits: its gap passes a cent at 2**17 (computed here).
        limit = 2 ** 17
        gap_below = 2.0 ** (16 - 23)
        gap_at = 2.0 ** (17 - 23)
        assert gap_below < 0.01 < gap_at
        top_value = 2 ** 18
        bar_bottom, bar_height = LEFT * 5.6 + DOWN * 3.2, 5.0
        shaft = Rectangle(width=0.5, height=bar_height).set_stroke(SCAFFOLD, 2).move_to(bar_bottom + UP * bar_height / 2)
        fill = Rectangle(width=0.5, height=0.01).set_fill(MONEY, 0.9).set_stroke(width=0).move_to(bar_bottom, aligned_edge=DOWN)
        marker_y = bar_bottom + UP * bar_height * limit / top_value
        marker = DashedLine(marker_y + LEFT * 0.4, marker_y + RIGHT * 0.9, color=ERROR, dash_length=0.08)
        marker_label = Text('gap > 1¢', font_size=22, color=ERROR).next_to(marker, RIGHT, buff=0.1)
        total = number(0, font_size=40, color=MONEY, commas=True).move_to(LEFT * 2.7 + UP * 1.4)
        dollar = Text('$', font_size=40, color=MONEY)
        dollar.add_updater(lambda m: m.next_to(total, LEFT, buff=0.1))
        self.play(FadeIn(big_title), Create(shaft), FadeIn(fill), FadeIn(total), FadeIn(dollar), run_time=0.8)
        self.add(marker, marker_label)
        tracker = ValueTracker(0)
        fill.add_updater(lambda m: m.stretch_to_fit_height(max(0.01, bar_height * min(tracker.get_value(), top_value) / top_value))
                         .move_to(bar_bottom, aligned_edge=DOWN))
        total.add_updater(lambda m: m.set_value(tracker.get_value()))
        self.play(tracker.animate.set_value(limit), run_time=6.0, rate_func=rate_functions.ease_in_quad)
        badge = VGroup(label_box('32-bit', color=STORED, font_size=22, fill=STORED, pad=0.12),
                       Text(f'gap > 1¢ at ${limit:,}', font_size=24, color=ERROR)).arrange(RIGHT, buff=0.25)
        badge.move_to(LEFT * 2.6 + UP * 0.8)
        self.at('run out of cents')
        self.play(Flash(marker.get_center(), color=ERROR), FadeIn(badge, shift=UP * 0.2), run_time=0.8)
        # One cent added to 131,072 in float32, computed here with struct.
        import struct
        f32 = struct.unpack('f', struct.pack('f', limit + 0.01))[0]
        sum_line = Text(f'{limit:,} + 0.01 in 32 bits\n→ {f32:,.6f}', font_size=22, line_spacing=0.8, color=ERROR)
        sum_line.next_to(badge, DOWN, buff=0.3).align_to(badge, LEFT)
        self.play(FadeIn(sum_line, shift=UP * 0.2))
        self.at('Big aggregates')
        self.play(tracker.animate.set_value(top_value), run_time=3.0, rate_func=rate_functions.linear)
        total.clear_updaters()
        fill.clear_updaters()

        # [V3.8a] right, very small: a per-request meter ticks while a request counter spins into the billions
        self.at('The opposite end')
        small_title = Text('very small', font_size=32).move_to(RIGHT * 3.6 + UP * 2.6)
        price = Text('price per request:\na few millionths of a dollar', font_size=24, line_spacing=0.8, color=MONEY)
        price.next_to(small_title, DOWN, buff=0.35)
        dial = Arc(radius=1.1, start_angle=PI, angle=-PI, color=SCAFFOLD, stroke_width=4).move_to(RIGHT * 3.6 + UP * 0.2)
        dial_centre = dial.get_center() + DOWN * 0.55
        dial.shift(UP * 0.0)
        hand = Line(dial_centre, dial_centre + LEFT * 0.95, color=MONEY, stroke_width=5)
        hub = Dot(dial_centre, radius=0.07, color=MONEY)
        sliver = sliced_penny(12, 0.35)[0].copy().move_to(dial_centre + UP * 0.45)
        self.play(FadeIn(small_title), FadeIn(price), Create(dial), Create(hand), FadeIn(hub), FadeIn(sliver), run_time=1.0)
        for _ in range(4):
            self.play(Rotate(hand, -PI / 24, about_point=dial_centre), run_time=0.25, rate_func=rate_functions.rush_into)
            self.wait(0.15)
        requests = number(0, font_size=36, color=WHITE, commas=True).move_to(RIGHT * 3.6 + DOWN * 1.6)
        requests_label = Text('requests', font_size=24, color=SCAFFOLD).next_to(requests, DOWN, buff=0.2)
        self.at('A price of a few')
        self.play(FadeIn(requests), FadeIn(requests_label), run_time=0.4)
        self.play(ChangeDecimalToValue(requests, 3_000_000_000), Rotate(hand, -PI / 2, about_point=dial_centre),
                  run_time=2.2, rate_func=rate_functions.ease_in_cubic)
        requests_label.add_updater(lambda m: m.next_to(requests, DOWN, buff=0.2))

        # [V3.8b] the two sides meet in the middle at one multiplication sign
        self.at('is a multiplication')
        times = Text('×', font_size=72, color=FOCUS).move_to(UP * 0.8)
        tiny = Text('tiny price', font_size=32, color=MONEY)
        huge = Text('huge count', font_size=32, color=WHITE)
        tiny.next_to(times, LEFT, buff=0.4)
        huge.next_to(times, RIGHT, buff=0.4)
        left_side = VGroup(big_title, shaft, fill, marker, marker_label, total, dollar, badge, sum_line)
        right_side = VGroup(small_title, dial, hand, hub, sliver, requests, requests_label)
        dollar.clear_updaters()
        requests_label.clear_updaters()
        self.play(FadeOut(divider), left_side.animate.scale(0.6).set_opacity(0.3).to_edge(LEFT, buff=0.2),
                  right_side.animate.scale(0.6).set_opacity(0.3).to_edge(RIGHT, buff=0.2),
                  ReplacementTransform(price, tiny), FadeIn(huge, shift=LEFT * 0.5), FadeIn(times, scale=2),
                  run_time=1.2)
        self.at('followed by a rounding')
        rounding = label_box('rounded to cents', color=FOCUS, font_size=26).next_to(times, DOWN, buff=0.6)
        down = Arrow(times.get_bottom(), rounding.get_top(), buff=0.1, color=FOCUS)
        invoice = receipt([('usage', '$ ?'), ('-', ''), ('Total', '$ ?')], width=3.0, font_size=20, title='INVOICE')
        invoice.next_to(rounding, DOWN, buff=0.3)
        self.play(GrowArrow(down), FadeIn(rounding))
        self.play(FadeIn(invoice, shift=LEFT * 0.4))
        self.finish()


# ---------------------------------------------------------------- 3.9

class Segment_3_9(Segment):
    """Recap, challenge (q03-05), QR wall and the teaser for episode 4."""
    EPISODE, SEGMENT = 3, '3.9'

    def construct(self):
        # [V3.9a] a risk map: how often × how visible, with the seven situations as dots
        origin = np.array([-5.0, -3.0, 0])
        width, height = 10.5, 5.6
        x_axis = Arrow(origin, origin + RIGHT * width, buff=0, color=SCAFFOLD, stroke_width=3)
        y_axis = Arrow(origin, origin + UP * height, buff=0, color=SCAFFOLD, stroke_width=3)
        x_label = Text('how often it happens', font_size=22, color=SCAFFOLD).next_to(x_axis, DOWN, buff=0.15)
        y_label = Text('how visible the damage is', font_size=22, color=SCAFFOLD).rotate(PI / 2).next_to(y_axis, LEFT, buff=0.15)
        self.play(Create(x_axis), Create(y_axis), FadeIn(x_label), FadeIn(y_label), run_time=1.0)

        def spot(fx, fy):
            return origin + RIGHT * width * fx + UP * height * fy

        situations = [
            ('Accumulation, where', 'accumulation', 0.62, 0.10, RIGHT),
            ('Comparisons and thresholds', 'comparisons', 0.70, 0.90, LEFT),
            ('Converting to cents', 'conversion to cents', 0.62, 0.70, LEFT),
            ('Multiplying by rates', 'rates', 0.80, 0.62, RIGHT),
            ('Order of addition', 'order', 0.38, 0.24, RIGHT),
            ('Boundaries, where', 'boundaries', 0.93, 0.22, LEFT),
            ('And size', 'size', 0.12, 0.66, RIGHT),
        ]
        dots = {}
        for cue, name, fx, fy, side in situations:
            self.at(cue)
            d = Dot(spot(fx, fy), radius=0.12, color=FOCUS)
            label = Text(name, font_size=24).next_to(d, side, buff=0.2)
            self.play(FadeIn(d, scale=2), FadeIn(label, shift=side * -0.2), run_time=0.5)
            dots[name] = VGroup(d, label)
            if name == 'order':
                # invisible until it isn't: a dashed jump up the visibility axis
                jump = DashedLine(d.get_center() + UP * 0.2, spot(fx, 0.55), color=FOCUS, dash_length=0.08)
                jump.add_tip(tip_length=0.15)
                self.play(Create(jump), run_time=0.6)
                dots[name].add(jump)
        self.at('huge totals')
        cluster = VGroup(dots['comparisons'][0], dots['conversion to cents'][0], dots['rates'][0])
        hot = VGroup(*[Ellipse(width=w, height=h).set_fill(ERROR, o).set_stroke(width=0)
                       for w, h, o in ((3.4, 2.4, 0.12), (2.6, 1.8, 0.18), (1.8, 1.2, 0.25))]).move_to(cluster)
        levels = [e.get_fill_opacity() for e in hot]
        hot.set_fill(opacity=0)
        self.add(hot)
        self.bring_to_back(hot)
        self.play(*[e.animate.set_fill(opacity=o) for e, o in zip(hot, levels)], run_time=0.8)
        self.play(hot.animate.scale(1.1), rate_func=there_and_back, run_time=1.0)

        # [V3.9b] the challenge: q03-05's code panel and its output; nothing is highlighted
        self.at("Here's a challenge")
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        code = code_panel(snippet_lines(P5, 7, 18), font_size=18).to_corner(UL, buff=0.25)
        out = output_console(P5, font_size=18).next_to(code, DOWN, buff=0.3).align_to(code, LEFT)
        self.play(FadeIn(code), FadeIn(out.background), run_time=0.6)
        card = show_qr(self, 'q03-05')
        self.at('It reads an order')
        self.play(out.type_line(0, run_time=1.4))
        self.at('The items are')
        # What the order should come to: the items as q03-05's JSON text lists them, and the
        # subtotal, total and payment the script states.
        text = snippet_find(P5, 'text = ')
        items = text.split('[')[1].split(']')[0].split(', ')
        rows = [('item', i) for i in items] + [('-', ''), ('should be', f'{sum(Decimal(i) for i in items)}')]
        bill = receipt(rows, width=2.9, font_size=18, title='ORDER').to_corner(UR, buff=0.2)
        bill_rows = [l for l in bill.rows if l is not None]
        for l in bill_rows[3:]:
            l.set_opacity(0)
        self.play(FadeIn(bill.paper), FadeIn(bill.lines[0]), LaggedStart(*[FadeIn(l) for l in bill_rows[:3]], lag_ratio=0.3),
                  FadeIn(bill.lines[4]), run_time=1.2)
        self.at('should be thirty dollars')
        self.play(bill_rows[3].animate.set_opacity(1))
        self.at('and the total thirty-two')
        should = VGroup(Text('total should be 32.77', font_size=22, color=EXACT),
                        Text('customer paid 32.77', font_size=22, color=EXACT)).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        should.next_to(bill, DOWN, buff=0.3).align_to(bill, LEFT)
        self.play(FadeIn(should[0], shift=UP * 0.2))
        self.at('paid exactly that')
        self.play(FadeIn(should[1], shift=UP * 0.2))
        self.at('But the program charges')
        self.play(out.type_line(1, run_time=1.0))
        self.at('says a balance is due')
        self.play(out.type_line(2, run_time=0.8))
        self.at('Five lines in it')
        finds = VGroup(*[Circle(radius=0.17).set_stroke(FOCUS, 3) for _ in range(5)]).arrange(RIGHT, buff=0.18)
        finds_label = Text('find 5 risky lines', font_size=22, color=FOCUS)
        task = VGroup(finds_label, finds).arrange(RIGHT, buff=0.3).next_to(out, DOWN, buff=0.35).align_to(out, LEFT)
        self.play(FadeIn(finds_label), LaggedStart(*[Create(c) for c in finds], lag_ratio=0.2), run_time=1.0)

        # [V3.9c] the QR wall: every code in this episode, for 10 seconds
        self.at('Find them all')
        hide_qr(self, card, hold=10.0)
        self.play(FadeOut(VGroup(code, out, bill, should, task)), run_time=0.5)
        wall = qr_wall(episode_qr_ids(3))
        self.play(FadeIn(wall), run_time=0.6)
        wall_at = self.renderer.time
        self.at('Next time')
        if self.renderer.time - wall_at < 10:
            self.wait(10 - (self.renderer.time - wall_at))

        # [V3.9d] teaser: a statement reading "Balance: $0.00" beside a red PAST DUE light
        self.play(FadeOut(wall), run_time=0.5)
        sheet = RoundedRectangle(width=4.6, height=2.6, corner_radius=0.12).set_fill(PAPER, 1).set_stroke(width=0)
        sheet_title = Text('STATEMENT', font_size=24, color=INK, weight=BOLD).move_to(sheet.get_top() + DOWN * 0.45)
        balance = Text('Balance: $0.00', font_size=36, color=INK).move_to(sheet).shift(DOWN * 0.15)
        statement = VGroup(sheet, sheet_title, balance)
        light = status_light()
        due = Text('PAST DUE', font_size=32, color=ERROR, weight=BOLD)
        alarm = VGroup(light, due).arrange(DOWN, buff=0.25)
        tease = VGroup(statement, alarm).arrange(RIGHT, buff=1.2).move_to(UP * 1.0)
        card4 = end_card('Episode 4', 'What goes wrong').next_to(tease, DOWN, buff=0.8)
        self.play(FadeIn(statement, shift=UP * 0.2), run_time=0.6)
        self.play(FadeIn(alarm, scale=0.6), run_time=0.5)
        self.play(FadeIn(card4, shift=UP * 0.2), run_time=0.6)
        for _ in range(3):
            self.play(light[0].animate.scale(1.25).set_opacity(0.5), run_time=0.5, rate_func=there_and_back)
        self.finish()

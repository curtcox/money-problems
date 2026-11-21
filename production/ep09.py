"""Episode 9 · Doing money right. One Scene per script segment.

    python3 production/render.py 9 [-ql] [segment ...]

Shot ids in comments ([V9.1a] ...) refer to episodes/09-doing-money-right.md. Code and console
text come from snippets/ep09/ (q09-01 ... q09-05); the few values no snippet prints (cents from
a price tag, divmod parts, random receipts for the invariant test) are computed below with
Python, and each one says so.
"""
import random
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa: E402,F403

P1 = 'ep09/01-counting-cents.py'
P2 = 'ep09/02-decimal-done-right.py'
P3 = 'ep09/03-tiny-money-type.py'
P4 = 'ep09/04-json-without-floats.py'
P5 = 'ep09/05-test-the-invariant.py'

# Checklist box text as each rule segment writes it (9.2 ... 9.8), and the recap card (9.9).
SHORT_RULES = [
    "Count, don't measure: whole minor units",
    'Decimal for rates, built from strings',
    'Round once, at a defined point, with a named mode',
    'Carry the currency; minor units differ',
    'Guard the boundaries',
    "Allocate, don't divide",
    'Test the invariants',
]
FULL_RULES = [
    "Count, don't measure: store whole minor units.",
    'Decimal for rates, built from strings, never from floats.',
    'Round once, at a defined point, with a named mode.',
    'Carry the currency; minor units differ.',
    'Guard the boundaries: JSON, databases, browsers, files.',
    "Allocate, don't divide.",
    'Test the invariants.',
]


def after_equals(line):
    """The value part of a recorded output line ('float total  = 10000.0...' -> '10000.0...')."""
    return line.split('= ', 1)[1]


def snippet_functions(path, first, last):
    """Run a snippet's function definitions (lines first..last) so a scene can call them."""
    namespace = {}
    exec(snippet_lines(path, first, last), namespace)
    return namespace


def hl(code, first, last=None, color=FOCUS, full=True):
    """A highlight box around code lines first..last (0-based) of a code_panel. Unlike
    common.line_highlight it is only as tall as the line pitch, so boxes on neighbouring lines
    never overlap. full=False hugs the text instead of spanning the panel."""
    last = first if last is None else last
    lines = code.code_lines
    pitch = (lines[0].get_y() - lines[-1].get_y()) / max(len(lines) - 1, 1)
    group = VGroup(*lines[first:last + 1])
    box = SurroundingRectangle(group, color=color, buff=0.03, corner_radius=0.04, stroke_width=2.5)
    box.stretch_to_fit_height(pitch * (last - first + 0.92))
    y = (lines[first].get_y() + lines[last].get_y()) / 2
    if full:
        box.stretch_to_fit_width(code.background.width - 0.2).move_to([code.background.get_x(), y, 0])
    else:
        box.stretch_to_fit_width(group.width + 0.14).move_to([group.get_x(), y, 0])
    return box


# ---------------------------------------------------------------- the checklist card

def checklist(texts, font_size=26, title='Checklist'):
    """The checklist card: seven boxes, each with its rule text (`.items`), a blank line for
    rules not written yet (`.blanks`), `.ticks` for 9.9, `.frame` and `.title`."""
    boxes, items, blanks, ticks = VGroup(), VGroup(), VGroup(), VGroup()
    pitch = font_size / 26 * 0.68
    for i, text in enumerate(texts):
        box = Square(font_size / 26 * 0.4).set_stroke(SCAFFOLD, 2.5).move_to(DOWN * pitch * i)
        item = Text(f'{i + 1}. {text}', font_size=font_size)
        item.next_to(box, RIGHT, buff=0.3)
        blank = Line(ORIGIN, RIGHT * 3.6, color=DIM, stroke_width=3)
        blank.next_to(box, RIGHT, buff=0.3).align_to(box, DOWN).shift(UP * 0.04)
        tick = checkmark(size=font_size / 26 * 0.42).move_to(box).shift(UP * 0.04 + RIGHT * 0.03)
        boxes.add(box)
        items.add(item)
        blanks.add(blank)
        ticks.add(tick)
    head = Text(title, font_size=font_size, color=SCAFFOLD, weight=BOLD)
    head.next_to(boxes, UP, buff=0.45).align_to(boxes, LEFT)
    body = VGroup(head, boxes, items, blanks)
    frame = RoundedRectangle(width=max(body.width + 0.9, 8.5), height=body.height + 0.8, corner_radius=0.18)
    frame.set_fill(PANEL, 1).set_stroke(GREY_D, 2).move_to(body)
    head.align_to(frame, LEFT).shift(RIGHT * 0.45)
    card = VGroup(frame, head, boxes, items, blanks)
    card.frame, card.title, card.boxes, card.items, card.blanks, card.ticks = frame, head, boxes, items, blanks, ticks
    shift = -frame.get_center()
    card.shift(shift)
    ticks.shift(shift)
    return card


def show_rule(scene, n, collapse_at=None, previous_header=None):
    """[V9.Na] The checklist card with boxes 1..n-1 filled; box n writes itself; then the card
    folds away and box n's line stays as a header in the top-left corner. Returns the header."""
    card = checklist(SHORT_RULES)
    shown = [card.frame, card.title, card.boxes] + [card.items[i] for i in range(n - 1)] + \
            [card.blanks[i] for i in range(n - 1, 7)]
    for i in range(n - 1):
        card.items[i].set_color(GREY_B)
    intro = [FadeIn(VGroup(*shown), scale=0.96)]
    if previous_header is not None:
        intro.append(FadeOut(previous_header))
    scene.play(*intro, run_time=0.7)
    current = card.items[n - 1].set_color(FOCUS)
    card.boxes[n - 1].set_stroke(MONEY, 3)
    scene.play(FadeOut(card.blanks[n - 1]), Write(current), run_time=1.6)
    if collapse_at:
        scene.at(collapse_at)
    else:
        scene.wait(1.0)
    header = VGroup(card.boxes[n - 1], current)
    target = header.copy().scale(0.82)
    target[1].set_color(WHITE)
    target.to_corner(UL, buff=0.32)
    rest = VGroup(*[m for m in shown if m is not card.boxes] + [card.boxes[i] for i in range(7) if i != n - 1])
    rest.remove(card.blanks[n - 1])
    scene.play(FadeOut(rest), Transform(header, target), run_time=0.8)
    scene.remove(*header)
    scene.add(header)
    return header


# ---------------------------------------------------------------- small pieces

def flip(scene, front, back, run_time=0.7):
    """Turn a tag over: it narrows to an edge, and widens again showing its back."""
    back.move_to(front)
    scene.play(front.animate.stretch(0.02, 0), run_time=run_time / 2, rate_func=rate_functions.ease_in_sine)
    back.stretch(0.02, 0)
    scene.remove(front)
    scene.add(back)
    scene.play(back.animate.stretch(50, 0), run_time=run_time / 2, rate_func=rate_functions.ease_out_sine)


def fill_jar(pot, fraction, color=MONEY):
    """A fill rectangle sitting on a jar's floor, `fraction` of its inner height (starts flat)."""
    body = pot[0]
    inner_h = body.height - 0.16
    rect = Rectangle(width=body.width - 0.16, height=inner_h * fraction).set_fill(color, 0.85).set_stroke(width=0)
    rect.align_to(body, DOWN).shift(UP * 0.08).set_x(body.get_x())
    return rect


def door(label, height=1.3):
    """A plain door: frame, a knob and its label underneath."""
    frame = RoundedRectangle(width=height * 0.62, height=height, corner_radius=0.06)
    frame.set_fill('#2a2622', 1).set_stroke(GREY_B, 2.5)
    knob = Dot(radius=0.05, color=MONEY).move_to(frame.get_right() + LEFT * 0.14)
    text = Text(label, font_size=22, color=GREY_A).next_to(frame, DOWN, buff=0.12)
    group = VGroup(frame, knob, text)
    group.frame, group.label = frame, text
    return group


def chip(text, color=SCAFFOLD, font_size=22, mono=False):
    """A small rounded label."""
    label = Text(text, font_size=font_size, color=color, font=MONO if mono else FONT)
    box = RoundedRectangle(width=label.width + 0.36, height=label.height + 0.26, corner_radius=0.1)
    box.set_stroke(color, 2).set_fill(BLACK, 0.6)
    return VGroup(box, label.move_to(box))


def spark(point, color=ERROR, radius=0.45):
    """A starburst of short lines."""
    rays = VGroup()
    for k in range(10):
        angle = k * TAU / 10
        direction = np.array([math.cos(angle), math.sin(angle), 0])
        rays.add(Line(point + direction * radius * 0.35, point + direction * radius, color=color, stroke_width=5))
    return rays


def digit_ruler(amount, minor_digits, cell=0.42, font_size=26, slots=None):
    """A row of digit cells for an amount; the minor-unit cells are outlined GOLD. With `slots`,
    only that many minor cells are drawn and extra digits hang off the end (`.overflow`)."""
    whole, _, frac = amount.partition('.')
    cells, digits = VGroup(), VGroup()
    x = 0.0
    for ch in whole:
        sq = Square(cell).set_stroke(GREY_B, 2).move_to(RIGHT * x)
        cells.add(sq)
        digits.add(Text(ch, font=MONO, font_size=font_size).move_to(sq))
        x += cell
    point = None
    if minor_digits or frac:
        point = Dot(radius=0.05, color=WHITE).move_to(RIGHT * (x - cell / 2 + cell * 0.25) + DOWN * cell * 0.38)
        x += cell * 0.5
    n_slots = minor_digits if slots is None else slots
    minor_cells = VGroup()
    overflow = VGroup()
    for k in range(max(n_slots, len(frac))):
        ch = frac[k] if k < len(frac) else ''
        if k < n_slots:
            sq = Square(cell).set_stroke(MONEY, 3).set_fill(MONEY, 0.18).move_to(RIGHT * x)
            minor_cells.add(sq)
            pos = sq.get_center()
        else:
            pos = RIGHT * x
        if ch:
            glyph = Text(ch, font=MONO, font_size=font_size, color=MONEY if k < n_slots else ERROR).move_to(pos)
            (digits if k < n_slots else overflow).add(glyph)
        x += cell
    group = VGroup(cells, minor_cells, digits, overflow)
    if point is not None:
        group.add(point)
    group.cells, group.minor_cells, group.digits, group.overflow = cells, minor_cells, digits, overflow
    return group.center()


# ---------------------------------------------------------------- 9.1

class Segment_9_1(Segment):
    """Cold open: the million-cent loop again, counting whole cents (q09-01)."""
    EPISODE, SEGMENT = 9, '9.1'

    def construct(self):
        out_lines = snippet_output(P1)

        # [V9.1a] the trailer's jar of pennies returns; the counter runs to 1,000,000 cents
        pot = jar(2.0, 2.2).move_to(LEFT * 2.2 + DOWN * 0.4)
        count = number(0, font_size=44, color=MONEY, commas=True)
        count_left = pot.get_right() + RIGHT * 1.0 + UP * 0.3
        count.move_to(count_left, aligned_edge=LEFT)
        unit = Text('cents', font_size=34, color=MONEY)

        def place_unit():
            count.move_to([count_left[0], count_left[1], 0], aligned_edge=LEFT)
            unit.next_to(count, RIGHT, buff=0.2, aligned_edge=DOWN)
        place_unit()
        self.play(FadeIn(pot), FadeIn(count), FadeIn(unit))
        self.at('Add one cent to a total')
        pile = VGroup()
        drops = [0.45, 0.35, 0.3, 0.2, 0.15, 0.1, 0.08, 0.06, 0.05, 0.05, 0.05, 0.05]
        shown = [1, 2, 3, 4, 5, 10, 50, 100, 1_000, 10_000, 100_000, 1_000_000]
        for run_time, value in zip(drops, shown):
            cent = penny(0.28).move_to(pot.get_top() + UP * 1.2)
            spot = pot[0].get_bottom() + UP * (0.3 + 0.08 * len(pile)) + RIGHT * 0.25 * ((len(pile) % 3) - 1)
            self.play(cent.animate.move_to(spot), run_time=run_time, rate_func=rate_functions.ease_in_quad)
            if len(pile) < 12:
                pile.add(cent)
            else:
                self.remove(cent)
            count.set_value(value)
            place_unit()
        self.add(pile)
        self.at('With floats, you get')
        total = MonoLine(after_equals(out_lines[0]), font_size=34, color=STORED)
        total.next_to(VGroup(count, unit), DOWN, buff=0.5).align_to(count, LEFT)
        self.play(FadeIn(total, shift=UP * 0.2))
        self.at('and a sliver')
        sliver = total.chars(total.source.index('.') + 1)
        self.play(sliver.animate.set_color(ERROR).scale(1.15), run_time=0.6)

        # [V9.1b] q09-01 on the left; two running totals, as_float BLUE and as_cents GOLD
        self.at('Now do it again')
        self.play(FadeOut(VGroup(pot, pile, count, unit, total)), run_time=0.6)
        code = code_panel(snippet_lines(P1, 4, 14), font_size=18).to_corner(UL, buff=0.35)
        self.play(FadeIn(code, shift=RIGHT * 0.3))
        names = VGroup(code_text('as_float', font_size=24, color=STORED), code_text('as_cents', font_size=24, color=MONEY))
        floats = number(0, decimals=2, font_size=36, color=STORED)
        cents = number(0, font_size=36, color=MONEY)
        right_x = code.get_right()[0] + 0.5
        names[0].set_anchor([right_x, 3.0, 0])
        floats.next_to(names[0], DOWN, buff=0.25).align_to(names[0], LEFT)
        names[1].set_anchor([right_x, 1.3, 0])
        cents.next_to(names[1], DOWN, buff=0.25).align_to(names[1], LEFT)
        floats.add_updater(lambda m: m.align_to(names[0], LEFT))
        cents.add_updater(lambda m: m.align_to(names[1], LEFT))
        self.play(FadeIn(names), FadeIn(floats), FadeIn(cents))
        self.at('count cents instead')
        loop = VGroup(hl(code, 3, color=STORED), hl(code, 4, color=MONEY))
        self.play(Create(loop))
        self.at('Add one to a whole number')
        self.play(ChangeDecimalToValue(floats, 10000.00), ChangeDecimalToValue(cents, 1_000_000),
                  run_time=3.5, rate_func=linear)

        # [V9.1c] the console prints; the float's tail glows red, the counted cents green
        out = output_console(P1, font_size=20)
        out.to_corner(DL, buff=0.35)
        card = qr_card('q09-01')
        self.play(FadeOut(loop), FadeIn(out.background), FadeIn(card, shift=UP * 0.2), run_time=0.6)
        card_shown = self.renderer.time
        self.play(out.type_line(0))
        tail = out.lines[0].chars(out.lines[0].source.index('10000.') + len('10000.'))
        exact_float = MonoLine(after_equals(out_lines[0]), font_size=26, color=STORED)
        exact_float.move_to(floats, aligned_edge=LEFT)
        float_tail = exact_float.chars(exact_float.source.index('.') + 1)
        float_tail.set_color(ERROR)
        self.play(tail.animate.set_color(ERROR), FadeOut(floats), FadeIn(exact_float), run_time=0.6)
        self.at('The total is one million cents')
        self.play(out.type_line(1))
        self.play(out.part(1, '1000000').animate.set_color(EXACT), cents.animate.set_color(EXACT), run_time=0.6)
        self.at('Format it as dollars and cents')
        self.play(out.type_line(2))
        self.play(out.part(2, '$10,000.00').animate.set_color(EXACT), run_time=0.5)
        self.at('Ask whether it equals')
        self.play(out.type_line(3))
        self.at('the answer is yes')
        self.play(out.part(3, 'True').animate.set_color(EXACT).scale(1.2), run_time=0.5)
        self.play(out.part(3, 'True').animate.scale(1 / 1.2), run_time=0.3)

        # [V9.1d] two jars: "measured" slightly overflowing with red dust, "counted" exactly full
        self.at("That's the whole difference")
        self.wait_since(card_shown, 8.2)
        self.remove(card)
        self.play(FadeOut(VGroup(code, names, exact_float, cents, out)), run_time=0.7)
        measured, counted = jar(2.0, 2.6), jar(2.0, 2.6)
        measured.move_to(LEFT * 3.3 + UP * 0.6)
        counted.move_to(RIGHT * 3.3 + UP * 0.6)
        line_y = measured[0].get_top()[1] - 0.45
        marks = VGroup(*[DashedLine([j[0].get_left()[0] - 0.2, line_y, 0], [j[0].get_right()[0] + 0.2, line_y, 0],
                                    color=GREY_A, dash_length=0.1) for j in (measured, counted)])
        loop_lines = [MonoLine(snippet_find(P1, needle), font_size=22) for needle in ('as_float += 0.01', 'as_cents += 1')]
        captions = VGroup()
        for j, line, op, note, color in ((measured, loop_lines[0], 'as_float += 0.01', '# measure a cent', STORED),
                                         (counted, loop_lines[1], 'as_cents += 1', '# count a cent', MONEY)):
            stmt = line.part(op).copy().set_color(color)
            comment = line.part(note).copy().set_color(GREY_B)
            name = Text('measured' if j is measured else 'counted', font_size=30)
            group = VGroup(name, stmt, comment).arrange(DOWN, buff=0.18).next_to(j, DOWN, buff=0.35)
            captions.add(group)
        self.play(FadeIn(measured), FadeIn(counted), Create(marks), FadeIn(captions[0][0]), FadeIn(captions[1][0]))
        self.at('The float version measures a cent')
        full = (line_y - (measured[0].get_bottom()[1] + 0.08)) / (measured[0].height - 0.16)
        m_fill = fill_jar(measured, full, color=STORED).stretch(0.01, 1, about_edge=DOWN)
        self.add(m_fill)
        self.play(FadeIn(captions[0][1:]), run_time=0.5)
        self.at('it adds a length')
        self.play(m_fill.animate.stretch_to_fit_height(m_fill_height(measured, full) * 1.04, about_edge=DOWN),
                  run_time=3.0, rate_func=linear)
        dust = VGroup(*[Dot(radius=0.025, color=ERROR).move_to(
            [measured.get_x() + 0.8 * math.sin(7.3 * k), line_y + 0.15 + 0.3 * ((k * 37) % 11) / 11, 0]) for k in range(22)])
        self.play(LaggedStart(*[FadeIn(d, shift=UP * 0.1) for d in dust], lag_ratio=0.08), run_time=1.2)
        self.at('The integer version counts a cent')
        self.play(FadeIn(captions[1][1:]), run_time=0.5)
        c_fill = fill_jar(counted, full).stretch(0.01, 1, about_edge=DOWN)
        self.add(c_fill)
        self.play(c_fill.animate.stretch_to_fit_height(m_fill_height(counted, full), about_edge=DOWN),
                  run_time=2.4, rate_func=linear)
        self.at('counting never drifts')
        self.play(marks[1].animate.set_color(EXACT), Flash(marks[1].get_right(), color=EXACT), run_time=0.8)

        # Seven rules, a tiny money type, a checklist: the empty card that 9.2 starts from
        self.at("We've spent eight episodes")
        self.play(FadeOut(VGroup(measured, counted, marks, captions, m_fill, c_fill, dust)), run_time=0.8)
        card = checklist(SHORT_RULES)
        self.at('Seven rules')
        self.play(FadeIn(card.frame), FadeIn(card.title))
        self.play(LaggedStart(*[FadeIn(VGroup(b, l), shift=RIGHT * 0.2) for b, l in zip(card.boxes, card.blanks)],
                              lag_ratio=0.2), run_time=1.6)
        self.at('a tiny money type')
        money = label_box('Money', color=MONEY, font_size=28, fill=MONEY).next_to(card.frame, RIGHT, buff=0.3)
        self.play(FadeIn(money, shift=LEFT * 0.3))
        self.at('a checklist you can take')
        self.play(FadeOut(money), Indicate(card.boxes, color=FOCUS, scale_factor=1.1), run_time=1.0)
        self.finish()


def m_fill_height(pot, fraction):
    return (pot[0].height - 0.16) * fraction


# ---------------------------------------------------------------- 9.2

class Segment_9_2(Segment):
    """Rule 1: count, don't measure."""
    EPISODE, SEGMENT = 9, '9.2'

    def construct(self):
        # [V9.2a] box 1 writes itself
        header = show_rule(self, 1, collapse_at='Store amounts as whole numbers')

        # Minor units: the smallest unit of each currency
        pairs = VGroup()
        for big, small in (('dollars', 'cents'), ('euros', 'cents'), ('pounds', 'pence')):
            a = Text(big, font_size=30)
            arrow = Arrow(LEFT * 0.5, RIGHT * 0.5, buff=0, color=SCAFFOLD, stroke_width=3)
            b = Text(small, font_size=30, color=MONEY)
            pairs.add(VGroup(a, arrow, b).arrange(RIGHT, buff=0.3))
        pairs.arrange(DOWN, buff=0.4)
        for p in pairs:
            p[1].set_x(pairs.get_x())
            p[0].next_to(p[1], LEFT, buff=0.3)
            p[2].next_to(p[1], RIGHT, buff=0.3)
        pairs.move_to(UP * 0.2)
        self.at('cents for dollars')
        self.play(FadeIn(pairs[0], shift=UP * 0.2))
        self.play(FadeIn(pairs[1], shift=UP * 0.2), run_time=0.6)
        self.at('pence for pounds')
        self.play(FadeIn(pairs[2], shift=UP * 0.2), run_time=0.6)
        self.at('Programmers call these minor units')
        smalls = VGroup(*[p[2] for p in pairs])
        bracket = SurroundingRectangle(smalls, color=MONEY, buff=0.2, corner_radius=0.1)
        minor = Text('minor units', font_size=30, color=MONEY).next_to(bracket, RIGHT, buff=0.35)
        self.play(Create(bracket), FadeIn(minor, shift=LEFT * 0.2))

        # Whole cents sit on ticks: they can't drift or land between two values
        self.at("A whole number of cents can't drift")
        self.play(FadeOut(VGroup(pairs, bracket, minor)), run_time=0.5)
        values = list(range(1997, 2002))       # whole cents around 1999 (computed)
        axis = Line(LEFT * 5, RIGHT * 5, color=SCAFFOLD, stroke_width=2).move_to(UP * 1.4)
        ticks = VGroup(*[Line(DOWN * 0.2, UP * 0.2, color=MONEY, stroke_width=4).move_to(axis.point_from_proportion(k / 4))
                         for k in range(5)])
        labels = VGroup(*[Text(f'{v}¢', font=MONO, font_size=22, color=SCAFFOLD).next_to(t, DOWN, buff=0.15)
                          for v, t in zip(values, ticks)])
        self.play(Create(axis), FadeIn(ticks), FadeIn(labels))
        dot = penny(0.22).move_to(ticks[2].get_center() + UP * 0.45)
        self.play(FadeIn(dot, scale=0.5))
        self.at("it can't sit between two values")
        self.play(dot.animate.shift(RIGHT * 1.25), run_time=0.6)       # pushed half way...
        self.play(dot.animate.move_to(ticks[3].get_center() + UP * 0.45), run_time=0.3)   # ...it snaps to a tick
        self.play(dot.animate.move_to(ticks[2].get_center() + UP * 0.45), run_time=0.4)
        self.at('Addition is exact')
        ops = VGroup()
        for text, target in (('+ 1¢', 3), ('− 1¢', 2)):
            op = Text(text, font_size=26, color=EXACT).next_to(dot, UP, buff=0.2)
            self.play(FadeIn(op, shift=UP * 0.1), run_time=0.3)
            self.play(dot.animate.move_to(ticks[target].get_center() + UP * 0.45), FadeOut(op), run_time=0.6)
        self.at('equals equals means what it says')
        same = Text('1999¢ = 1999¢', font_size=28, color=EXACT).next_to(axis, UP, buff=0.9)
        self.play(FadeIn(same), Flash(dot, color=EXACT), run_time=0.8)

        # [V9.2b] $19.99 turns over: 1999¢. Then three more tags flip.
        self.at('Nineteen ninety-nine is simply')
        fronts = ['$19.99', '$0.10', '$1.15', '$10,000.00']
        # The backs are computed: whole cents from the tag's text, never through a float.
        backs = [f"{int(Decimal(t.strip('$').replace(',', '')) * 100)}¢" for t in fronts]
        tags = VGroup(*[price_tag(t, font_size=30) for t in fronts]).arrange(RIGHT, buff=0.5).move_to(DOWN * 1.9)
        self.play(FadeIn(tags[0], shift=UP * 0.2))
        flip(self, tags[0], price_tag(backs[0], font_size=30, color=EXACT))
        self.play(FadeIn(tags[1:], shift=UP * 0.2), run_time=0.6)
        for tag, back in zip(tags[1:], backs[1:]):
            flip(self, tag, price_tag(back, font_size=30, color=EXACT), run_time=0.5)

        # [V9.2c] the formatting line enlarges; divmod splits 1000000 into 10000 and 00
        self.at('You only turn it back into dollars')
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not header])), run_time=0.6)
        code = code_panel(snippet_find(P1, 'divmod(as_cents', 'as money'), font_size=26).move_to(UP * 2.0)
        self.play(FadeIn(code, scale=0.6))
        cents_text = after_equals(output_line(P1, 'cents total'))         # '1000000'
        dollars, cents = divmod(int(cents_text), 100)                      # computed: 10000, 0
        whole = MonoLine(cents_text, font_size=44, color=MONEY).move_to(DOWN * 0.1)
        self.play(FadeIn(whole))
        self.at("you don't need a float")
        nofloat = chip('no float', color=EXACT, font_size=26).move_to(RIGHT * 4.6 + DOWN * 0.1)
        self.play(FadeIn(nofloat, shift=LEFT * 0.2))
        self.at('Divmod by one hundred')
        self.play(Create(hl(code, 0)), run_time=0.5)
        n = len(cents_text)
        head, tail = whole.chars(0, n - 2), whole.chars(n - 2)
        left = MonoLine(str(dollars), font_size=44, color=MONEY)
        right = MonoLine(f'{cents:02d}', font_size=44, color=MONEY)
        left.move_to(head.get_center() + LEFT * 0.9)
        right.move_to(tail.get_center() + RIGHT * 0.9)
        self.play(ReplacementTransform(head, left), ReplacementTransform(tail, right), run_time=1.0)
        self.remove(whole)
        tags2 = VGroup(Text('dollars', font_size=22, color=SCAFFOLD).next_to(left, DOWN, buff=0.2),
                       Text('cents', font_size=22, color=SCAFFOLD).next_to(right, DOWN, buff=0.2))
        self.play(FadeIn(tags2))
        self.at('you print them with a dot')
        self.play(Create(hl(code, 1)), run_time=0.5)
        money = MonoLine(after_equals(output_line(P1, 'as money')), font_size=52, color=EXACT).move_to(DOWN * 1.8)
        m = len(money.source)
        self.play(FadeOut(tags2), ReplacementTransform(left, money.chars(1, m - 3)),
                  ReplacementTransform(right, money.chars(m - 2)), run_time=1.0)
        self.play(FadeIn(money.chars(0, 1)), FadeIn(money.chars(m - 3, m - 2)), run_time=0.5)
        self.play(nofloat.animate.next_to(money, RIGHT, buff=0.5), run_time=0.6)

        # [V9.2d] inset: int(1.15 * 100) gives 114 (episode 3); "1.15" read as text gives 115
        self.at('Back in episode three')
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not header])), run_time=0.6)
        frame = RoundedRectangle(width=11.5, height=3.6, corner_radius=0.18).set_stroke(GREY_D, 2).set_fill(PANEL, 1)
        frame.move_to(DOWN * 0.3)
        tag = Text('episode 3', font_size=22, color=SCAFFOLD).next_to(frame.get_corner(UL), DR, buff=0.2)
        self.play(FadeIn(frame), FadeIn(tag))
        bad = MonoLine(output_line('ep00/01-four-surprises.py', 'int(1.15'), font_size=30)
        bad.move_to(frame.get_center() + UP * 0.55)
        self.at('int of one point one five')
        self.play(LaggedStart(*[FadeIn(g) for g in bad.glyphs], lag_ratio=0.03), run_time=1.0)
        self.at('one hundred and fourteen')
        self.play(bad.part('114').animate.set_color(ERROR).scale(1.25), run_time=0.5)
        cross = crossmark(size=0.4).next_to(bad, RIGHT, buff=0.35)
        self.play(Create(cross), run_time=0.4)
        self.at('If an amount arrives as text')
        text_in = MonoLine('"1.15"', font_size=30, color=EXACT)
        text_out = MonoLine(str(int(Decimal('1.15') * 100)), font_size=30, color=EXACT)   # computed: 115
        arrow = Arrow(LEFT * 0.7, RIGHT * 0.7, buff=0, color=EXACT, stroke_width=4)
        good = VGroup(text_in, arrow, text_out).arrange(RIGHT, buff=0.35).move_to(frame.get_center() + DOWN * 0.7)
        good.align_to(bad, LEFT)
        self.play(FadeIn(text_in))
        self.play(GrowArrow(arrow), FadeIn(text_out, shift=RIGHT * 0.2), run_time=0.8)
        tick = checkmark(size=0.4).next_to(good, RIGHT, buff=0.35).set_x(cross.get_x())
        self.play(Create(tick), run_time=0.4)
        self.at('Which brings us to rule two')
        self.play(Indicate(text_in, color=FOCUS), run_time=1.0)
        self.finish()


# ---------------------------------------------------------------- 9.3

class Segment_9_3(Segment):
    """Rule 2: decimals from strings (q09-02)."""
    EPISODE, SEGMENT = 9, '9.3'

    def construct(self):
        # [V9.3a] box 2 writes itself
        header = show_rule(self, 2, collapse_at='But money arithmetic')

        # [V9.3c] a tax rate and an exchange rate: "not whole cents"
        self.at('a tax rate of eight and a quarter')
        tax = price_tag('8.25 %', color=STORED, font_size=30)
        fx = price_tag('1.0837', color=STORED, font_size=30)
        rates = VGroup(tax, fx).arrange(RIGHT, buff=1.2).move_to(UP * 0.4)
        self.play(FadeIn(tax, shift=UP * 0.3))
        self.at('an exchange rate')
        self.play(FadeIn(fx, shift=UP * 0.3))
        note = Text('not whole cents', font_size=28, color=FOCUS).next_to(rates, DOWN, buff=0.5)
        self.at('four or five decimal places')
        self.play(FadeIn(note, shift=UP * 0.15))
        self.play(rates.animate.shift(UP * 0.12), rate_func=there_and_back, run_time=0.8)

        # [V9.3b] code panel q09-02; 0.3 prints in green beside the faded float answer
        self.at("Python's Decimal stores")
        code_short = code_panel(snippet_find(P2, 'CENT = ', '0.1 + 0.2'), font_size=18)
        code_long = code_panel(snippet_find(P2, 'CENT = ', '0.1 + 0.2', "from '1.005'", 'from 1.005'), font_size=18)
        code_long.move_to(UP * 1.5)
        code_short.align_to(code_long, UL)
        rates_top = VGroup(rates, note.copy())
        note_target = Text('not whole cents', font_size=22, color=FOCUS)
        rates_target = VGroup(tax.copy().scale(0.75), fx.copy().scale(0.75), note_target).arrange(RIGHT, buff=0.35)
        rates_target.to_corner(UR, buff=0.32)
        card = qr_card('q09-02')
        self.play(Transform(rates, rates_target[:2]), Transform(note, rates_target[2]),
                  FadeIn(code_short, shift=UP * 0.2), FadeIn(card, shift=UP * 0.2))
        out = output_console(P2, ['0.1 + 0.2', "from '1.005'", 'from 1.005'], font_size=22)
        out.to_edge(LEFT, buff=0.35).set_y(-1.15)
        self.at('So Decimal of the string zero point one')
        self.play(Create(hl(code_short, 1, color=EXACT)), run_time=0.5)
        self.at('is exactly zero point three')
        self.play(FadeIn(out.background), run_time=0.3)
        self.play(out.type_line(0))
        three = out.part(0, '0.3')
        float_answer = after_equals(output_line('ep01/01-ten-plus-twenty.py', '0.30000000000000004'))
        faded = MonoLine(float_answer, font_size=22, color=STORED).set_opacity(0.4)
        faded.next_to(out.lines[0], RIGHT, buff=0.9)
        vs = Text('float:', font_size=20, color=SCAFFOLD).set_opacity(0.6).next_to(faded, UP, buff=0.1, aligned_edge=LEFT)
        self.play(three.animate.set_color(EXACT).scale(1.3), FadeIn(faded), FadeIn(vs), run_time=0.7)
        self.play(three.animate.scale(1 / 1.3), run_time=0.3)
        self.at('The fives that broke binary')
        self.play(Indicate(three, color=EXACT, scale_factor=1.4), run_time=1.0)

        # [V9.3d] "1.005" (green path) and 1.005 (red path, through a float line) into Decimal
        self.at('But notice the quotation marks')
        highlights = [m for m in self.mobjects if isinstance(m, SurroundingRectangle)]
        self.play(FadeOut(VGroup(faded, vs, card, *highlights)), FadeIn(code_long), FadeOut(code_short), run_time=0.6)
        quote_lines = VGroup(hl(code_long, 2, color=EXACT), hl(code_long, 3, color=ERROR))
        box = label_box('Decimal', color=FOCUS, font_size=30).move_to(RIGHT * 4.3 + DOWN * 2.2)
        from_text = code_text('"1.005"', font_size=30, color=EXACT).move_to(RIGHT * 0.1 + DOWN * 1.2)
        from_float = code_text('1.005', font_size=30, color=ERROR).move_to(LEFT * 0.85 + DOWN * 3.2)
        green_path = Arrow(from_text.get_right(), box.get_left() + UP * 0.15, buff=0.15, color=EXACT, stroke_width=4)
        # a little float line on the red path: 1.005 snaps to the double just below it
        icon_axis = Line(LEFT * 1.0, RIGHT * 1.0, color=SCAFFOLD, stroke_width=3)
        icon_ticks = VGroup(*[Line(DOWN * 0.18, UP * 0.18, color=STORED, stroke_width=4).move_to(RIGHT * x)
                              for x in (-0.85, -0.2, 0.45)])
        icon = VGroup(icon_axis, icon_ticks).move_to(RIGHT * 1.5 + DOWN * 3.2)
        diamond = Square(0.16).rotate(PI / 4).set_fill(FOCUS, 1).set_stroke(width=0).move_to(icon.get_center() + RIGHT * 0.15 + UP * 0.45)
        red_in = Arrow(from_float.get_right(), icon.get_left(), buff=0.12, color=ERROR, stroke_width=4)
        red_out = Arrow(icon.get_right(), box.get_left() + DOWN * 0.15, buff=0.12, color=ERROR, stroke_width=4)
        self.at('Decimal of the string one point zero zero five')
        self.play(FadeIn(box), FadeIn(from_text), Create(quote_lines[0]))
        self.play(GrowArrow(green_path))
        self.at('gives one dollar and one cent')
        self.play(out.type_line(1))
        self.play(out.part(1, '1.01').animate.set_color(EXACT), run_time=0.4)
        self.at('Decimal of the float one point zero zero five')
        self.play(FadeIn(from_float), FadeIn(icon), FadeIn(diamond), ReplacementTransform(quote_lines[0], quote_lines[1]))
        self.play(GrowArrow(red_in), run_time=0.5)
        self.at("It's a little below")
        snap = CurvedArrow(diamond.get_bottom(), icon_ticks[1].get_top(), color=FOCUS, angle=-PI / 3, stroke_width=3, tip_length=0.12)
        self.play(Create(snap), run_time=0.5)
        self.play(GrowArrow(red_out), run_time=0.5)
        self.at('so the same rounding gives one dollar')
        self.play(out.type_line(2))
        self.play(out.part(2, '1.00', occurrence=1).animate.set_color(ERROR), run_time=0.4)

        # Strings, integers, other decimals go in; floats never do
        self.at('A decimal type only protects you')
        self.play(FadeOut(VGroup(from_text, from_float, icon, diamond, snap, green_path, red_in, red_out, quote_lines[1])),
                  run_time=0.6)
        sources = VGroup(chip('strings', EXACT), chip('integers', EXACT), chip('decimals', EXACT), chip('floats', ERROR))
        sources.arrange(DOWN, buff=0.18).move_to(RIGHT * 0.9 + DOWN * 2.2)
        arrows = VGroup(*[Arrow(s.get_right(), box.get_left(), buff=0.12, color=EXACT, stroke_width=3,
                                max_tip_length_to_length_ratio=0.12) for s in sources[:3]])
        self.at('Build decimals from strings')
        for s, a in zip(sources[:3], arrows):
            self.play(FadeIn(s, shift=RIGHT * 0.2), GrowArrow(a), run_time=0.5)
        self.at('Never from floats')
        self.play(FadeIn(sources[3], shift=RIGHT * 0.2), run_time=0.4)
        no = crossmark(size=0.35).next_to(sources[3], RIGHT, buff=0.25)
        self.play(sources[3].animate.shift(RIGHT * 0.4), rate_func=there_and_back, run_time=0.5)
        self.play(Create(no), run_time=0.4)
        self.finish()


# ---------------------------------------------------------------- 9.4

class Segment_9_4(Segment):
    """Rule 3: round once, on purpose (q09-02)."""
    EPISODE, SEGMENT = 9, '9.4'

    def construct(self):
        # [V9.4a] box 3 writes itself
        header = show_rule(self, 3, collapse_at='Multiplying these decimals')

        # [V9.4b] the tax lines: 2.50 x 0.05 = 0.1250, exact
        code = code_panel(snippet_lines(P2, 8, 13), font_size=18).move_to(UP * 1.85)
        self.play(FadeIn(code, shift=UP * 0.2))
        self.play(Create(hl(code, 2)), run_time=0.5)
        out = output_console(P2, ['2.50 x', 'half up', 'half even'], font_size=22)
        out.to_edge(LEFT, buff=0.35).set_y(-0.95)
        self.at('Two fifty times five percent')
        self.play(FadeIn(out.background), run_time=0.3)
        self.play(out.type_line(0))
        fifty = out.lines[0].chars(len(out.lines[0].source) - 2)
        self.at('is exactly zero point one two five zero')
        self.play(fifty.animate.set_color(FOCUS), run_time=0.5)
        exact = Text('exact: no rounding yet', font_size=22, color=FOCUS).next_to(out.background, DOWN, buff=0.25, aligned_edge=LEFT)
        pointer = SurroundingRectangle(fifty, color=FOCUS, buff=0.05, stroke_width=2.5)
        self.play(FadeIn(exact), Create(pointer))

        # [V9.4c] the rounding number line between 0.12 and 0.13, with 0.125 in the middle
        self.at('an exact tie')
        line = FloatLine(Fraction('0.12'), Fraction('0.13'), width=6.0, color=SCAFFOLD,
                         ticks=[Fraction('0.12'), Fraction('0.125'), Fraction('0.13')],
                         labels={Fraction('0.12'): '0.12', Fraction('0.125'): '0.125', Fraction('0.13'): '0.13'},
                         label_size=22)
        line.move_to(RIGHT * 3.2 + DOWN * 1.0)
        tie = line.diamond(Fraction('0.125'))
        self.play(Create(line.axis), FadeIn(line.ticks), FadeIn(line.labels))
        self.play(FadeIn(tie, shift=DOWN * 0.2))
        self.at('Now you round, deliberately')
        quant = hl(code, 4, 5)
        self.play(Create(quant), run_time=0.6)
        self.at('Half up gives thirteen cents')
        self.play(out.type_line(1))
        up = CurvedArrow(tie.get_top() + UP * 0.05, line.point(Fraction('0.13')) + UP * 0.25, angle=-PI / 2.5,
                         color=EXACT, stroke_width=4, tip_length=0.18)
        up_label = Text('half up', font_size=22, color=EXACT).next_to(up, UP, buff=0.08)
        self.play(Create(up), FadeIn(up_label), out.part(1, '0.13').animate.set_color(EXACT))
        self.at('Half even gives twelve')
        self.play(out.type_line(2))
        down_start = line.point(Fraction('0.125')) + DOWN * 0.6
        down = CurvedArrow(down_start, line.point(Fraction('0.12')) + DOWN * 0.65, angle=-PI / 2.5,
                           color=STORED, stroke_width=4, tip_length=0.18)
        down_label = Text('half even', font_size=22, color=STORED).next_to(down, DOWN, buff=0.08)
        self.play(Create(down), FadeIn(down_label), out.part(2, '0.12').animate.set_color(STORED))
        self.at('a question for your tax authority')
        who = VGroup(chip('tax authority'), chip('contract'), chip('accountant')).arrange(RIGHT, buff=0.25)
        who.move_to(RIGHT * 3.2 + DOWN * 3.35)
        self.play(LaggedStart(*[FadeIn(w, shift=UP * 0.2) for w in who], lag_ratio=0.5), run_time=1.6)

        # Habit one: always name the mode
        self.at('always pass the rounding mode explicitly')
        modes = hl(code, 4, 5, color=MONEY)
        named = Text('a named mode, every time', font_size=24, color=MONEY).move_to(who)
        self.play(ReplacementTransform(quant, modes), FadeOut(who), run_time=0.6)
        self.play(FadeIn(named, shift=UP * 0.15), Indicate(modes, color=MONEY, scale_factor=1.02), run_time=0.9)

        # [V9.4d] habit two: one pipeline with a single gold rounding box, and the crossed-out one
        self.at('decide where rounding happens')
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not header])), run_time=0.6)
        steps = [label_box('price × quantity'), label_box('× rate'),
                 label_box('round to cents', color=MONEY, fill=MONEY), label_box('store')]
        good = VGroup(*steps).arrange(RIGHT, buff=0.75).move_to(UP * 1.2)
        good_arrows = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.1, color=SCAFFOLD, stroke_width=3)
                               for a, b in zip(steps, steps[1:])])
        self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.2) for s in steps], lag_ratio=0.3),
                  LaggedStart(*[GrowArrow(a) for a in good_arrows], lag_ratio=0.3), run_time=1.6)
        self.at('per line or per invoice')
        whens = VGroup(chip('per line'), chip('per invoice'), chip('per day'), chip('per month'))
        whens.arrange(RIGHT, buff=0.25).next_to(good, UP, buff=0.45)
        self.play(FadeIn(whens[:2], shift=DOWN * 0.15), run_time=0.6)
        self.at('per day or per month')
        self.play(FadeIn(whens[2:], shift=DOWN * 0.15), run_time=0.6)
        self.at('Then round there, once')
        once = Text('once', font_size=26, color=MONEY).next_to(steps[2], DOWN, buff=0.2)
        self.play(Indicate(steps[2], color=MONEY), FadeIn(once))
        self.at('Rounding at every step')
        names = ['price × quantity', 'round', '× rate', 'round', 'store']
        bad_steps = [label_box(n, font_size=22, color=MONEY if n == 'round' else SCAFFOLD) for n in names]
        bad = VGroup(*bad_steps).arrange(RIGHT, buff=0.55).move_to(DOWN * 1.9)
        bad_arrows = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.08, color=SCAFFOLD, stroke_width=3)
                              for a, b in zip(bad_steps, bad_steps[1:])])
        self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.2) for s in bad_steps], lag_ratio=0.25),
                  LaggedStart(*[GrowArrow(a) for a in bad_arrows], lag_ratio=0.25), run_time=1.5)
        self.at('lets small errors pile up')
        strike = VGroup(Line(bad.get_corner(UL) + UL * 0.15, bad.get_corner(DR) + DR * 0.15, color=ERROR, stroke_width=6),
                        Line(bad.get_corner(DL) + DL * 0.15, bad.get_corner(UR) + UR * 0.15, color=ERROR, stroke_width=6))
        self.play(Create(strike), run_time=0.8)
        self.finish()


# ---------------------------------------------------------------- 9.5

class Segment_9_5(Segment):
    """Rule 4: carry the currency."""
    EPISODE, SEGMENT = 9, '9.5'

    def construct(self):
        # [V9.5a] box 4 writes itself
        header = show_rule(self, 4, collapse_at='A bare one thousand')

        # [V9.5c] a bare 1999 and its question mark
        bare = Text('1999', font=MONO, font_size=80).move_to(UP * 0.6)
        mark = Text('?', font_size=72, color=FOCUS).next_to(bare, RIGHT, buff=0.25).align_to(bare, UP)
        self.play(FadeIn(bare, scale=0.8))
        self.play(FadeIn(mark, shift=DOWN * 0.2), run_time=0.5)
        guesses = VGroup(Text('$19.99?', font_size=36), Text('¥1,999?', font_size=36), Text('1.999 KWD?', font_size=36))
        guesses.arrange(RIGHT, buff=1.0).move_to(DOWN * 1.6)
        self.at('Is it nineteen dollars')
        self.play(FadeIn(guesses[0], shift=UP * 0.2))
        self.at('yen?')
        self.play(FadeIn(guesses[1], shift=UP * 0.2))
        self.at('Something else entirely')
        self.play(FadeIn(guesses[2], shift=UP * 0.2))
        self.play(mark.animate.set_color(ERROR).scale(1.3), run_time=0.6)

        # [V9.5b] three tags, each with a ruler of its minor-unit digits
        self.at('It matters more than you might expect')
        self.play(FadeOut(VGroup(bare, mark, guesses)), run_time=0.6)
        specs = [('USD', '19.99', 2, '2 minor digits'), ('JPY', '1500', 0, 'no minor digits'),
                 ('KWD', '1.250', 3, '3 minor digits')]
        columns = VGroup()
        for code_, amount, digits, words in specs:
            tag = price_tag(f'{code_} {amount}', font_size=34)
            ruler = digit_ruler(amount, digits, cell=0.56, font_size=32)
            words_t = Text(words, font_size=24, color=MONEY if digits else SCAFFOLD)
            columns.add(VGroup(tag, ruler, words_t).arrange(DOWN, buff=0.4))
        columns.arrange(RIGHT, buff=1.2, aligned_edge=UP).move_to(UP * 0.5)
        self.play(LaggedStart(*[FadeIn(c[0], shift=UP * 0.2) for c in columns], lag_ratio=0.3), run_time=1.2)
        self.at('because currencies')
        for c in columns:
            self.play(c[0].animate.shift(UP * 0.15), rate_func=there_and_back, run_time=0.5)
        self.at('lists how many minor-unit digits')
        heading = Text('minor-unit digits', font_size=28, color=MONEY).next_to(columns, UP, buff=0.45)
        self.play(FadeIn(heading, shift=DOWN * 0.15))
        for phrase, column in zip(('The US dollar has two', 'The Japanese yen has none', 'The Kuwaiti dinar has three'),
                                  columns):
            self.at(phrase)
            ruler = column[1]
            self.play(FadeIn(ruler.cells), FadeIn(ruler.digits), *([FadeIn(ruler[4])] if len(ruler) > 4 else []),
                      run_time=0.6)
            self.play(Create(ruler.minor_cells) if len(ruler.minor_cells) else Wait(0.1), FadeIn(column[2]),
                      run_time=0.6)
        self.at('a thousand fils to the dinar')
        fils = Text('1,000 fils = 1 dinar', font_size=22, color=SCAFFOLD).next_to(columns[2], DOWN, buff=0.3)
        self.play(FadeIn(fils, shift=UP * 0.1))
        self.at('So "multiply by one hundred"')
        times = VGroup(*[chip('× 100', color=MONEY, font_size=24) for _ in columns])
        verdicts = VGroup()
        for t, column, ok in zip(times, columns, (True, False, False)):
            t.move_to([column.get_x(), columns.get_bottom()[1] - 1.15, 0])
            verdicts.add((checkmark(size=0.35) if ok else crossmark(size=0.35)).next_to(t, RIGHT, buff=0.25))
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in times], lag_ratio=0.3), run_time=1.0)
        self.at("It's a fact about some currencies")
        self.play(LaggedStart(*[Create(v) for v in verdicts], lag_ratio=0.3), run_time=1.0)

        # [V9.5d] 5 USD and 5 JPY bump with a red spark: "not the same 5"
        self.at('five dollars plus five yen')
        self.play(FadeOut(VGroup(columns, fils, times, verdicts, heading)), run_time=0.6)
        usd = price_tag('5 USD', font_size=36).move_to(LEFT * 4.5 + UP * 0.2)
        jpy = price_tag('5 JPY', font_size=36).move_to(RIGHT * 4.5 + UP * 0.2)
        self.play(FadeIn(usd), FadeIn(jpy))
        self.play(usd.animate.next_to(ORIGIN + UP * 0.2, LEFT, buff=0.02),
                  jpy.animate.next_to(ORIGIN + UP * 0.2, RIGHT, buff=0.02), run_time=0.8, rate_func=rate_functions.ease_in_quad)
        burst = spark(UP * 0.2 + UP * 0.9)
        self.play(FadeIn(burst, scale=0.4), usd.animate.shift(LEFT * 0.8), jpy.animate.shift(RIGHT * 0.8), run_time=0.4)
        same = Text('not the same 5', font_size=34, color=ERROR).move_to(DOWN * 1.4)
        self.play(FadeIn(same, shift=UP * 0.2), FadeOut(burst))
        self.at('Code that adds amounts in different currencies')
        plus = Text('+', font_size=60, color=GREY_A).move_to(UP * 0.2)
        self.play(FadeIn(plus))
        self.at('the moment it happens')
        stop = crossmark(size=0.7).move_to(plus)
        self.play(FadeOut(plus), Create(stop), Flash(stop, color=ERROR), run_time=0.8)
        self.finish()


# ---------------------------------------------------------------- 9.6

class Segment_9_6(Segment):
    """A tiny Money type (q09-03)."""
    EPISODE, SEGMENT = 9, '9.6'

    def bracket(self, code, index, text, color=FOCUS):
        box = hl(code, index, color=color, full=False)
        label = Text(text, font_size=22, color=color).next_to(box, RIGHT, buff=0.3)
        self.play(Create(box), FadeIn(label, shift=LEFT * 0.15), run_time=0.6)
        return VGroup(box, label)

    def construct(self):
        # [V9.6a] q09-03, scrolled to the class (first the fields and Money.of)
        top = code_panel(snippet_lines(P3, 8, 18), font_size=18).to_corner(UL, buff=0.35)
        card = qr_card('q09-03')
        self.play(FadeIn(top, shift=UP * 0.2), FadeIn(card, shift=UP * 0.2))
        self.at('small enough to fit in a QR code')
        ring = SurroundingRectangle(card[2], color=FOCUS, buff=0.08)
        self.play(Create(ring))
        self.play(FadeOut(ring), run_time=0.5)
        self.at('it builds in all four rules')
        rules = VGroup(*[chip(f'rule {k}', color=FOCUS) for k in range(1, 5)]).arrange(RIGHT, buff=0.25)
        rules.next_to(top, DOWN, buff=0.3).align_to(top, LEFT)
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rules], lag_ratio=0.25), run_time=1.0)

        # minor: int (rule 1), and frozen
        self.at('A Money is two things')
        self.play(FadeOut(rules), run_time=0.4)
        marks = VGroup(self.bracket(top, 2, 'rule 1: whole minor units'))
        self.at('and a currency code')
        marks.add(self.bracket(top, 3, 'rule 4: its currency'))
        self.at("It's frozen")
        marks.add(self.bracket(top, 0, 'frozen: no changes'))

        # Money.of: Decimal(text) (rule 2); the console's first results, and 1.005 refused
        out = output_console(P3, font_size=20, rows=5)
        out.to_corner(DL, buff=0.35)
        self.at('You create one from text')
        self.play(FadeOut(marks), FadeOut(card), run_time=0.6)
        marks = VGroup(self.bracket(top, 7, 'rule 2: Decimal(text)'))
        self.at('checks that the result is a whole number')
        marks.add(self.bracket(top, 8, 'whole?'))
        # Each conversion is computed here, the way Money.of does it: Decimal(text).scaleb(digits).
        digits = {'USD': 2, 'JPY': 0, 'KWD': 3}
        rows = VGroup()
        anchor_x = out.background.get_right()[0] + 0.6
        for i, (text, cur) in enumerate((('19.99', 'USD'), ('1500', 'JPY'), ('1.25', 'KWD'))):
            minor = int(Decimal(text).scaleb(digits[cur]))
            row = MonoLine(f'{text} {cur} → {minor}', font_size=22)
            row.set_anchor([anchor_x, -0.95 - 0.5 * i, 0])
            row.part(str(minor), occurrence=0 if str(minor) not in f'{text} {cur} ' else 1).set_color(MONEY)
            rows.add(row)
        for phrase, row in zip(('Nineteen ninety-nine dollars becomes', 'Fifteen hundred yen', 'One and a quarter dinars'), rows):
            self.at(phrase)
            self.play(FadeIn(row, shift=LEFT * 0.2), run_time=0.6)
        self.play(FadeIn(out.background), run_time=0.3)
        self.play(out.type_line(1))
        self.play(out.part(1, '1500').animate.set_color(EXACT), run_time=0.4)
        self.at('prints as one point two five zero')
        self.play(out.part(1, '1.250').animate.set_color(EXACT), run_time=0.5)

        # [V9.6c] 1.005 dollars is refused: three digits, two cent slots
        self.at('But one point zero zero five dollars')
        ruler = digit_ruler('1.005', 2, cell=0.5, font_size=30)
        ruler.move_to([anchor_x + 1.9, -2.95, 0])
        ruler_label = Text('1.005 USD', font=MONO, font_size=22).next_to(ruler, UP, buff=0.18)
        self.play(FadeIn(ruler_label), FadeIn(ruler.cells), FadeIn(ruler.minor_cells), FadeIn(ruler[4]),
                  FadeIn(ruler.digits))
        self.play(FadeIn(ruler.overflow, shift=RIGHT * 0.3))
        self.play(ruler.overflow.animate.shift(DOWN * 0.15).rotate(-0.4), run_time=0.5)
        self.at('is refused')
        self.play(out.type_line(3))
        self.play(out.lines[3].glyphs.animate.set_color(ERROR), run_time=0.4)
        self.at("won't quietly round it")
        self.play(Indicate(ruler.overflow, color=ERROR, scale_factor=1.4), run_time=0.8)

        # __add__ checks the currency (rule 4): scroll on to the rest of the class
        self.at('Adding checks the currencies first')
        rest = code_panel(snippet_lines(P3, 20, 27), font_size=18).to_corner(UL, buff=0.35)
        self.play(FadeOut(marks), top.animate.shift(UP * 0.6).set_opacity(0),
                  FadeOut(VGroup(rows, ruler, ruler_label)), run_time=0.6)
        self.remove(top)
        self.play(FadeIn(rest, shift=UP * 0.6), run_time=0.6)
        marks = VGroup(self.bracket(rest, 1, 'rule 4: same currency?'))
        self.at('Dollars plus dollars works')
        self.play(out.type_line(0))
        self.play(out.part(0, 'USD 20.00').animate.set_color(EXACT), run_time=0.4)
        self.at('Dollars plus yen raises an error')
        self.play(Indicate(rest.code_lines[2], color=ERROR, scale_factor=1.04), run_time=0.7)
        self.play(out.type_line(4))
        self.play(out.lines[4].glyphs.animate.set_color(ERROR), run_time=0.4)

        # times(rate, rounding): the one place rounding happens (rule 3)
        self.at('And multiplying by a rate')
        self.play(FadeOut(marks), run_time=0.4)
        marks = VGroup(self.bracket(rest, 5, 'rule 3: round here, once'))
        self.at('does the multiplication exactly in Decimal')
        marks.add(hl(rest, 6, color=FOCUS, full=False))
        self.play(Create(marks[-1]), run_time=0.5)
        self.at('half even unless you say otherwise')
        self.play(Indicate(rest.code_lines[5], color=FOCUS, scale_factor=1.04), run_time=0.8)
        self.at('comes to one dollar sixty-five')
        self.play(out.type_line(2))
        self.play(out.part(2, 'USD 1.65').animate.set_color(EXACT), run_time=0.4)

        # Make the right thing easy, the wrong thing an error
        self.at("It's not a complete library")
        self.play(FadeOut(marks), run_time=0.4)
        extras = VGroup(chip('allocation'), chip('locale formatting'), chip('much more'))
        extras.arrange(DOWN, buff=0.2, aligned_edge=LEFT).next_to(out.background, RIGHT, buff=0.6).align_to(out.background, UP)
        self.at('Real ones add allocation')
        self.play(LaggedStart(*[FadeIn(e, shift=LEFT * 0.2) for e in extras], lag_ratio=0.4), run_time=1.5)
        self.at('make the right thing easy')
        ticks = VGroup(*[checkmark(size=0.28).next_to(out.background, RIGHT, buff=0.2).set_y(out.lines[i].get_y())
                         for i in (0, 1, 2)])
        crosses = VGroup(*[crossmark(size=0.28).next_to(out.background, RIGHT, buff=0.2).set_y(out.lines[i].get_y())
                           for i in (3, 4)])
        self.play(FadeOut(extras), LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.3), run_time=1.0)
        self.at('and the wrong thing an error')
        self.play(LaggedStart(*[Create(c) for c in crosses], lag_ratio=0.3), run_time=0.8)
        self.finish()


# ---------------------------------------------------------------- 9.7

def hub(doors_at, center=ORIGIN, scale=1.0):
    """'your code' in the middle, green inside, with doors around it."""
    core = RoundedRectangle(width=2.6, height=1.5, corner_radius=0.2).set_fill(EXACT, 0.3).set_stroke(EXACT, 3)
    label = Text('your code', font_size=28).move_to(core)
    inside = VGroup(core, label)
    doors = VGroup()
    for name, offset in doors_at:
        doors.add(door(name).move_to(offset))
    group = VGroup(inside, doors).scale(scale).shift(center)
    group.inside, group.doors = inside, doors
    return group


DOOR_NAMES = ['JSON', 'database', 'browser', 'spreadsheet', 'CSV']


class Segment_9_7(Segment):
    """Rule 5: guard the boundaries (q09-04)."""
    EPISODE, SEGMENT = 9, '9.7'

    def construct(self):
        # [V9.7a] box 5; "your code" in the centre, doors all around
        header = show_rule(self, 5, collapse_at='Your own code can be perfect')
        spots = [LEFT * 4.6 + UP * 0.9, LEFT * 2.6 + DOWN * 2.2, UP * 2.0, RIGHT * 2.6 + DOWN * 2.2, RIGHT * 4.6 + UP * 0.9]
        house = hub(list(zip(DOOR_NAMES, spots)), center=DOWN * 0.3)
        self.play(FadeIn(house.inside, scale=0.9))
        self.play(LaggedStart(*[FadeIn(d, shift=-d.get_center() * 0.08) for d in house.doors], lag_ratio=0.2), run_time=1.4)
        self.at('a float can still sneak in')
        intruder = chip('float', color=ERROR, font_size=22).move_to(house.doors[4].frame)
        self.play(FadeIn(intruder, scale=0.5))
        self.play(intruder.animate.move_to(house.inside.get_right() + LEFT * 0.4 + UP * 0.35), run_time=1.2)
        self.play(house.inside[0].animate.set_fill(ERROR, 0.25), Flash(intruder, color=ERROR), run_time=0.6)
        self.at('every time money enters or leaves')
        self.play(FadeOut(intruder), house.inside[0].animate.set_fill(EXACT, 0.3), run_time=0.6)
        for d in house.doors:
            self.play(d.frame.animate.set_stroke(FOCUS, 4), Indicate(d.label, color=FOCUS), run_time=0.3)
            self.play(d.frame.animate.set_stroke(GREY_B, 2.5), run_time=0.15)

        # [V9.7b] through the JSON door: 4.35 as a float, then with parse_float=Decimal
        self.at('is the classic example')
        code = code_panel(snippet_find(P4, 'text = ', 'as_float = json', 'float price x 100', 'as_decimal = json',
                                       'Decimal price x 100'), font_size=18)
        code.to_corner(UL, buff=0.35).shift(DOWN * 0.55)
        out = output_console(P4, font_size=18, width=9.6)
        out.to_corner(DL, buff=0.3)
        json_door = house.doors[0]
        self.play(FadeOut(house.doors[1:]), FadeOut(house.inside), run_time=0.5)
        inside = hub([], center=ORIGIN).inside.scale(0.8).move_to(LEFT * 0.4 + DOWN * 0.25)
        card = qr_card('q09-04')
        self.play(json_door.animate.scale(0.85).move_to(LEFT * 5.6 + DOWN * 0.25), FadeIn(inside),
                  FadeIn(code, shift=UP * 0.2), FadeIn(card, shift=UP * 0.2))
        self.at('turns anything with a decimal point into a float')
        self.play(Create(hl(code, 1, color=STORED)), run_time=0.5)
        price = code_text('4.35', font_size=28, color=STORED).next_to(json_door.frame, LEFT, buff=0.15).shift(UP * 0.25)
        as_type = Text('float', font_size=20, color=STORED).next_to(price, DOWN, buff=0.1)
        traveller = VGroup(price, as_type)
        self.play(FadeIn(traveller))
        self.play(traveller.animate.move_to(inside.get_left() + LEFT * 0.75), run_time=1.0)
        self.at('A coffee priced at four thirty-five')
        self.play(FadeIn(out.background), run_time=0.3)
        self.play(out.type_line(0))
        bad_tail = out.lines[0].chars(out.lines[0].source.index('= ') + 2)
        self.play(bad_tail.animate.set_color(ERROR), traveller.animate.set_color(ERROR), run_time=0.5)
        self.at('But pass parse float equals Decimal')
        self.play(FadeOut(traveller), Create(hl(code, 3, color=EXACT)), run_time=0.6)
        price2 = code_text('4.35', font_size=28, color=EXACT).next_to(json_door.frame, LEFT, buff=0.15).shift(UP * 0.25)
        as_type2 = Text('Decimal', font_size=20, color=EXACT).next_to(price2, DOWN, buff=0.1)
        traveller2 = VGroup(price2, as_type2)
        self.play(FadeIn(traveller2))
        self.play(traveller2.animate.move_to(inside.get_left() + LEFT * 0.85), run_time=1.0)
        self.at('four hundred and thirty-five cents')
        self.play(out.type_line(1))
        self.play(out.lines[1].chars(out.lines[1].source.index('= ') + 2).animate.set_color(EXACT), run_time=0.5)

        # [V9.7c] on the way out: a string price, integer price_minor, and a helpful refusal
        self.at('Going out, send amounts')
        exit_door = door('JSON').scale(0.85).move_to(RIGHT * 5.6 + DOWN * 0.25)
        highlights = [m for m in self.mobjects if isinstance(m, SurroundingRectangle)]
        self.play(FadeOut(VGroup(card, traveller2, *highlights)), FadeIn(exit_door), run_time=0.6)
        line3, line4 = out.lines[2], out.lines[3]
        as_text = code_text('"4.35"', font_size=26, color=EXACT)           # from {"price": "4.35", ...}
        as_minor = code_text('435', font_size=26, color=EXACT)              # from {"price_minor": 435, ...}
        assert '"4.35"' in line3.source and '435' in line4.source
        for value, line, dy in ((as_text, 2, 0.3), (as_minor, 3, -0.45)):
            value.move_to(inside.get_right() + RIGHT * 0.7 + UP * dy)
            self.play(FadeIn(value, shift=RIGHT * 0.2), run_time=0.4)
            self.play(value.animate.next_to(exit_door.frame, LEFT, buff=0.3).set_y(exit_door.frame.get_y() + dy),
                      out.type_line(line), run_time=1.0)
        self.at('Python actually refuses')
        self.play(out.type_line(4))
        self.play(out.lines[4].glyphs.animate.set_color(FOCUS), run_time=0.4)
        self.at('which is a helpful refusal')
        refusal = Text('a helpful refusal', font_size=22, color=FOCUS)
        refusal.next_to(out.background, RIGHT, buff=0.3).align_to(out.lines[4], DOWN)
        self.play(FadeIn(refusal, shift=LEFT * 0.2))

        # [V9.7d] the database door: DECIMAL(19, 4), not FLOAT
        self.at('The same idea applies at every other door')
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not header])), run_time=0.6)
        spots_small = [LEFT * 5.9 + UP * 1.1, LEFT * 5.0 + DOWN * 2.0, LEFT * 3.4 + UP * 2.0, LEFT * 1.8 + DOWN * 2.0,
                       LEFT * 0.9 + UP * 1.1]
        house = hub(list(zip(DOOR_NAMES, spots_small)))
        house.inside.scale(0.8).move_to(LEFT * 3.4 + DOWN * 0.15)
        self.play(FadeIn(house.inside), LaggedStart(*[FadeIn(d) for d in house.doors], lag_ratio=0.15), run_time=1.2)
        detail_center = RIGHT * 3.8 + DOWN * 0.3

        def open_door(index):
            d = house.doors[index]
            self.play(d.frame.animate.set_stroke(FOCUS, 4), d.label.animate.set_color(FOCUS), run_time=0.4)
            return d

        def close_door(d, detail):
            self.play(FadeOut(detail), d.frame.animate.set_stroke(GREY_B, 2.5), d.label.animate.set_color(GREY_A), run_time=0.5)

        self.at('In a database')
        db = open_door(1)
        good_col = code_text('amount DECIMAL(19, 4)', font_size=28, color=EXACT)
        bad_col = code_text('amount FLOAT', font_size=28, color=ERROR)
        cols = VGroup(good_col, bad_col).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to(detail_center)
        strike = Line(bad_col.get_left() + LEFT * 0.1, bad_col.get_right() + RIGHT * 0.1, color=ERROR, stroke_width=5)
        self.play(FadeIn(good_col, shift=RIGHT * 0.2))
        self.at('never in a float or real column')
        self.play(FadeIn(bad_col, shift=RIGHT * 0.2))
        self.play(Create(strike), run_time=0.5)
        detail = VGroup(cols, strike)

        # [V9.7e] the browser door: a price in a web page
        self.at('In a JavaScript front end')
        close_door(db, detail)
        web = open_door(2)
        page = RoundedRectangle(width=4.6, height=2.6, corner_radius=0.12).set_fill('#262a30', 1).set_stroke(GREY_B, 2)
        bar = Rectangle(width=4.6, height=0.4).set_fill(GREY_D, 1).set_stroke(width=0).align_to(page, UP)
        lights = VGroup(*[Dot(radius=0.06, color=GREY_B) for _ in range(3)]).arrange(RIGHT, buff=0.12)
        lights.move_to(bar).align_to(bar, LEFT).shift(RIGHT * 0.25)
        shown_price = Text('$4.35', font_size=44, color=MONEY).move_to(page).shift(DOWN * 0.15)
        window = VGroup(page, bar, lights, shown_price).move_to(detail_center + UP * 0.6)
        note = wrapped_text('integers or a decimal library inside; formatting only at display', 6.0, font_size=22,
                            color=EXACT).next_to(window, DOWN, buff=0.3)
        self.play(FadeIn(VGroup(page, bar, lights)))
        self.at('keep amounts as integers of minor units')
        self.play(FadeIn(note, shift=UP * 0.15))
        self.at('format for display only at the very end')
        self.play(FadeIn(shown_price, scale=0.8))
        detail = VGroup(window, note)

        # The spreadsheet and CSV doors: read the amounts as text
        self.at('And when a spreadsheet')
        close_door(web, detail)
        sheet, csv = open_door(3), open_door(4)
        as_text_label = chip('read amounts as text', color=EXACT, font_size=26).move_to(detail_center)
        self.play(FadeIn(as_text_label))
        self.at('rather than letting a tool guess')
        guess = chip('float?', color=ERROR, font_size=24).next_to(as_text_label, DOWN, buff=0.6)
        self.play(FadeIn(guess, shift=UP * 0.2))
        no = crossmark(size=0.32).next_to(guess, RIGHT, buff=0.2)
        self.play(Create(no), run_time=0.4)
        self.finish()


# ---------------------------------------------------------------- 9.8

def money_text(cents):
    """'$33.34' from whole cents, without a float."""
    return f'${cents // 100:,}.{cents % 100:02d}'


class Segment_9_8(Segment):
    """Rules 6 and 7: allocate, and test (q09-05)."""
    EPISODE, SEGMENT = 9, '9.8'

    def construct(self):
        functions = snippet_functions(P5, 6, 12)        # float_split and allocate, run as written
        allocate, float_split = functions['allocate'], functions['float_split']

        # [V9.8a] box 6; the three-way split from episode 8, in miniature
        header = show_rule(self, 6, collapse_at="allocate, don't divide")
        whole = price_tag(money_text(10_000), font_size=36).move_to(UP * 1.4)
        self.play(FadeIn(whole, shift=DOWN * 0.2))
        parts = allocate(10_000, 3)                      # computed: [3334, 3333, 3333]
        shares = VGroup(*[price_tag(money_text(p), font_size=32) for p in parts]).arrange(RIGHT, buff=0.6).move_to(DOWN * 0.6)
        self.at('Whenever an amount is split')
        self.play(*[TransformFromCopy(whole, s) for s in shares], run_time=1.0)
        total = Text(f'sum {money_text(sum(parts))}', font_size=32, color=EXACT).next_to(shares, DOWN, buff=0.6)
        self.at('add up exactly')
        self.play(FadeIn(total, shift=UP * 0.2))
        self.at('who gets the leftover cents')
        extra = penny(0.2).next_to(shares[0], UP, buff=0.15)
        self.play(FadeIn(extra, shift=DOWN * 0.3), Indicate(shares[0], color=FOCUS), run_time=0.9)

        # [V9.8b] box 7; code panel q09-05
        self.at('And rule seven')
        self.play(FadeOut(VGroup(whole, shares, total, extra)), run_time=0.4)
        header = show_rule(self, 7, collapse_at='An invariant is something', previous_header=header)
        code = code_panel(snippet_lines(P5, 6, 12), font_size=18).move_to(UP * 1.75)
        card = qr_card('q09-05')
        self.play(FadeIn(code, shift=UP * 0.2), FadeIn(card, shift=UP * 0.2))

        # [V9.8d] the invariants, as the narration names them
        invariants = VGroup(*[Text(t, font_size=22) for t in ('parts sum to the whole', 'debits equal credits',
                                                              'parse then format gives back the text',
                                                              'refunds never exceed payments')])
        invariants.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        bullets = VGroup(*[checkmark(size=0.24).next_to(t, LEFT, buff=0.2) for t in invariants])
        inv = VGroup(bullets, invariants).to_corner(DL, buff=0.45).shift(UP * 0.2)
        for k, phrase in enumerate(('For a split', 'For a ledger', 'Parsing an amount')):
            self.at(phrase)
            self.play(FadeIn(bullets[k]), FadeIn(invariants[k], shift=RIGHT * 0.2), run_time=0.6)
        self.play(FadeIn(bullets[3]), FadeIn(invariants[3], shift=RIGHT * 0.2), run_time=0.6)

        # Random receipts: each splits into parts, and the parts must snap back to the whole
        self.at("you don't have to work out the right answer")
        out = output_console(P5, font_size=22)
        out.to_corner(DL, buff=0.35)
        inv_target = inv.copy().scale(0.92).to_corner(DR, buff=0.35)
        self.play(FadeOut(card), run_time=0.5)
        self.play(Transform(inv, inv_target), run_time=0.7)
        lanes = {float_split: -0.15, allocate: -1.05}
        names = VGroup(*[code_text(f.__name__, font_size=22, color=STORED if f is float_split else MONEY)
                         .move_to([-5.6, y, 0]) for f, y in lanes.items()])
        # The same random totals the snippet draws for float_split: random.Random(2026), computed here.
        rng = random.Random(2026)
        kept = None

        self.at('You can throw thousands')
        self.play(Create(hl(code, 0, 2, color=STORED)), Create(hl(code, 4, 6, color=MONEY)), FadeIn(names), run_time=0.6)
        deadline = phrase_seconds(self.EPISODE, self.SEGMENT, 'fails seven thousand') - 0.4
        k = 0
        while True:
            pace = 1.6 if k < 3 else 1.0
            if self.renderer.time + pace > deadline:
                break
            total_c, n = rng.randint(1, 1_000_000), rng.randint(1, 12)
            slip = Rectangle(width=2.6, height=0.62).set_fill(PAPER, 1).set_stroke(width=0)
            label = Text(f'{money_text(total_c)} ÷ {n}', font=MONO, font_size=20, color=INK).move_to(slip)
            receipt_ = VGroup(slip, label).move_to([-2.9, -0.6, 0])
            spreads, joins, results, verdicts, colours = VGroup(), [], VGroup(), VGroup(), []
            for split, y in lanes.items():
                pieces = split(total_c, n)
                ok = sum(pieces) == total_c
                bars = VGroup(*[Rectangle(width=2.6 / n, height=0.18).set_fill(MONEY, 1).set_stroke(BLACK, 1)
                                for _ in range(n)]).arrange(RIGHT, buff=0)
                bars.move_to([-1.2 + 1.3, y, 0])
                spread = bars.copy().arrange(RIGHT, buff=0.12).move_to(bars, aligned_edge=LEFT)
                result = Text(f'sum {money_text(sum(pieces))}', font=MONO, font_size=20,
                              color=EXACT if ok else ERROR).move_to([3.1, y, 0], aligned_edge=LEFT)
                verdict = (checkmark(size=0.28) if ok else crossmark(size=0.28)).next_to(result, RIGHT, buff=0.2)
                spreads.add(spread)
                joins.append(Transform(spread, bars))
                results.add(result)
                verdicts.add(verdict)
                colours.append(EXACT if ok else ERROR)
                if split is float_split and not ok and kept is None:
                    kept = (total_c, n)
            self.play(FadeIn(receipt_, shift=LEFT * 0.6), FadeIn(spreads, shift=RIGHT * 0.3), run_time=pace * 0.3)
            self.play(*joins, run_time=pace * 0.25)
            self.play(FadeIn(results), FadeIn(verdicts),
                      *[sp.animate.set_fill(c, 1) for sp, c in zip(spreads, colours)], run_time=pace * 0.2)
            self.play(FadeOut(VGroup(receipt_, spreads, results, verdicts), shift=LEFT * 0.6), run_time=pace * 0.25)
            k += 1

        self.at('fails seven thousand')
        self.play(FadeIn(out.background), run_time=0.3)
        self.play(out.type_line(0))
        self.play(out.part(0, '7431').animate.set_color(ERROR).scale(1.2), run_time=0.5)
        self.at('fails zero times')
        self.play(out.type_line(1))
        self.play(out.part(1, ' 0 ').animate.set_color(EXACT).scale(1.2), run_time=0.5)

        # Keep a failure as a permanent test
        self.at('Random inputs find the awkward amounts')
        highlights = [m for m in self.mobjects if isinstance(m, SurroundingRectangle)]
        self.play(FadeOut(names), FadeOut(VGroup(*highlights)), run_time=0.3)
        total_c, n = kept
        slip = Rectangle(width=2.8, height=0.62).set_fill(PAPER, 1).set_stroke(width=0)
        label = Text(f'{money_text(total_c)} ÷ {n}', font=MONO, font_size=20, color=INK).move_to(slip)
        found = VGroup(slip, label).move_to([-2.0, -0.6, 0])
        self.play(FadeIn(found, shift=LEFT * 0.6))
        self.play(Indicate(found, color=ERROR), run_time=0.8)
        self.at('keep that amount as a permanent test')
        pin = chip('permanent test', color=FOCUS, font_size=22).next_to(found, RIGHT, buff=0.5)
        self.play(FadeIn(pin, shift=LEFT * 0.2))
        self.at('can never quietly return')
        lock = SurroundingRectangle(VGroup(found, pin), color=FOCUS, buff=0.15, corner_radius=0.1)
        self.play(Create(lock), run_time=0.7)
        self.finish()


# ---------------------------------------------------------------- 9.9

class Segment_9_9(Segment):
    """Recap and challenge; QR wall; teaser for episode 10."""
    EPISODE, SEGMENT = 9, '9.9'

    def construct(self):
        # [V9.9a] the full checklist card, ticked box by box
        card = checklist(FULL_RULES, font_size=30)
        fit(card, 13.2)
        if card.height > 7.4:
            card.scale_to_fit_height(7.4)
        card.move_to(ORIGIN)
        self.play(FadeIn(VGroup(card.frame, card.title, card.boxes)), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(i, shift=RIGHT * 0.15) for i in card.items], lag_ratio=0.12), run_time=1.6)
        ticks = VGroup(*[checkmark(size=card.boxes[0].width * 1.05).move_to(b).shift(UP * 0.03 + RIGHT * 0.03)
                         for b in card.boxes])
        phrases = ["Count, don't measure", 'Use a decimal type', 'Round once', 'Carry the currency',
                   'Guard the boundaries', "Allocate, don't divide", 'And test the invariants']
        for k, phrase in enumerate(phrases):
            self.at(phrase)
            self.play(Create(ticks[k]), card.boxes[k].animate.set_stroke(EXACT, 3), run_time=0.5)
        self.at('take a screenshot')
        self.play(Indicate(card.frame, color=EXACT, scale_factor=1.01), run_time=1.0)

        # [V9.9b] the q09-05 code returns, the challenge comment highlighted
        self.at("Here's the challenge")
        self.play(FadeOut(VGroup(card, ticks)), run_time=0.6)
        code = code_panel(snippet_lines(P5, 1, 12), font_size=18).to_corner(UL, buff=0.35)
        qr = qr_card('q09-05')
        self.play(FadeIn(code, shift=UP * 0.2), FadeIn(qr, shift=UP * 0.2))
        self.at('The code in the corner')
        ring = SurroundingRectangle(qr[2], color=FOCUS, buff=0.08)
        self.play(Create(ring))
        self.play(FadeOut(ring), run_time=0.5)
        self.at('Add a test of your own')
        challenge = hl(code, 2)
        self.play(Create(challenge))
        self.at('Or break the allocate function', lead=0.0)
        alloc = hl(code, 9, 11, color=MONEY)
        self.play(ReplacementTransform(challenge, alloc), run_time=0.6)
        self.wait(1.2)

        # [V9.9c] the QR wall, ten seconds; [V9.9d] the teaser for episode 10
        wall_start = phrase_seconds(self.EPISODE, self.SEGMENT, 'Next time') - 10.6
        if self.renderer.time < wall_start:
            self.wait(wall_start - self.renderer.time)
        wall = qr_wall(episode_qr_ids(9))
        self.play(FadeOut(VGroup(code, qr, alloc)), run_time=0.4)
        self.add(wall)
        self.wait(10.0)
        self.at('Next time')
        self.remove(wall)
        trap = output_line('ep10/01-decimal-trap.py', 'Decimal(0.1)')
        call = MonoLine(trap.split('=')[0].strip(), font_size=40, color=WHITE).move_to(UP * 1.6)
        digits = MonoLine(after_equals(trap), font_size=24, color=STORED)
        fit(digits, 13.0).move_to(UP * 0.3)
        self.play(LaggedStart(*[FadeIn(g) for g in call.glyphs], lag_ratio=1.0), run_time=1.2)
        self.at("decimals that import a float's error")
        self.play(LaggedStart(*[FadeIn(g, shift=RIGHT * 0.1) for g in digits.glyphs], lag_ratio=0.6), run_time=2.5)
        word = call.part('Decimal')
        crack = VMobject(color=ERROR, stroke_width=5).set_points_as_corners(
            [word.get_top() + LEFT * 0.3 + UP * 0.1, word.get_center() + RIGHT * 0.15 + UP * 0.1,
             word.get_center() + LEFT * 0.2 + DOWN * 0.1, word.get_bottom() + RIGHT * 0.1 + DOWN * 0.1])
        self.at('integer cents that overflow')
        self.play(Create(crack), word.animate.set_color(ERROR), run_time=0.8)
        self.at('And, at last')
        teaser = end_card('Episode 10', 'When the fixes fail').move_to(DOWN * 2.0)
        self.play(FadeIn(teaser, shift=UP * 0.2))
        self.finish()

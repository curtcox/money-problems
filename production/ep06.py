"""Episode 6 · Rounding is a policy. One Scene per script segment.

    python3 production/render.py 6 [-ql] [segment ...]

Shot ids in comments ([V6.1a] ...) refer to episodes/06-rounding-is-a-policy.md. Code and
console text come from snippets/ep06/ (q06-01 ... q06-05) and their recorded output. Values
the script describes but no snippet prints (the five-cent cash totals, 2.97, ≈ 51.129 EUR, the
q06-03 error walk) are computed below with Python's decimal module, and say so.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa: E402,F403

import re  # noqa: E402
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP  # noqa: E402
from fractions import Fraction  # noqa: E402

Q1 = 'ep06/01-why-2675-rounds-down.py'
Q2 = 'ep06/02-eight-ways-to-round.py'
Q3 = 'ep06/03-the-bias-of-half-up.py'
Q4 = 'ep06/04-per-line-or-per-invoice.py'
Q5 = 'ep06/05-challenge-euro-triangle.py'
CENT = Decimal('0.01')


# ---------------------------------------------------------------- local helpers

def show_card(scene, qr_id):
    """Fade a QR card in (bottom right) and remember when, so hide_card can hold it long enough."""
    card = qr_card(qr_id)
    scene.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)
    scene.card_since = scene.renderer.time
    return card


def hide_card(scene, card, hold=8.0, *anims):
    remaining = scene.card_since + hold + 0.2 - scene.renderer.time
    if remaining > 1 / 30:
        scene.wait(remaining)
    scene.play(FadeOut(card), *anims, run_time=0.6)


def ring_card(scene, card):
    """Point at a QR code without touching it: a yellow rectangle around it."""
    ring = SurroundingRectangle(card[2], color=FOCUS, buff=0.08)
    scene.play(Create(ring), run_time=0.6)
    scene.play(FadeOut(ring), run_time=0.5)


def type_code(code, run_time=None):
    """Type a code_panel's glyphs out in reading order (put code.background on screen first)."""
    glyphs = [g for line in code.code_lines for g in line]
    run_time = run_time or min(2.5, max(0.8, 0.025 * len(glyphs)))
    return LaggedStart(*[FadeIn(g, run_time=0.05) for g in glyphs], lag_ratio=1.0, run_time=run_time)


def gem(color=FOCUS, size=0.22):
    return Square(size).rotate(PI / 4).set_fill(color, 1).set_stroke(width=0)


def result_glyphs(line):
    """The glyphs after '= ' in a console line such as 'round(1.005, 2) = 1.0'."""
    return line.chars(line.source.index('= ') + 2)


def cent_line(lo, hi, width, centre, ticks=None, label_size=20):
    """A plain number line (the float line's look, grey cent ticks) with its axis centred at `centre`."""
    if ticks is None:
        n = round((Fraction(hi) - Fraction(lo)) * 100)
        ticks = [Fraction(lo) + Fraction(k, 100) for k in range(n + 1)]
    ticks = [Fraction(t) for t in ticks]
    line = FloatLine(lo, hi, width=width, ticks=ticks, color=SCAFFOLD, tick_height=0.4,
                     labels={t: f'{float(t):.2f}' for t in ticks}, label_size=label_size)
    line.shift(np.array([centre[0], centre[1], 0.0]) - line.axis.get_center())
    return line


def money_chip(text, color=MONEY, font_size=24):
    label = Text(text, font_size=font_size, color=BLACK, weight=BOLD)
    chip = RoundedRectangle(width=label.width + 0.4, height=label.height + 0.3, corner_radius=0.12)
    chip.set_fill(color, 1).set_stroke(width=0)
    return VGroup(chip, label.move_to(chip))


# ---------------------------------------------------------------- 6.1

class Segment_6_1(Segment):
    """Cold open: round(2.675, 2) is 2.67 (q06-01)."""
    EPISODE, SEGMENT = 6, '6.1'

    def construct(self):
        # [V6.1a] black canvas; a price tag swings in; a yellow arrow points at the final 5
        tag = price_tag('$2.675', font_size=64).move_to(UP * 0.8)
        pivot = tag[1].get_center()
        tag.rotate(-0.5, about_point=pivot).shift(UP * 6)
        self.play(tag.animate.shift(DOWN * 6), run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        for angle in (0.8, -0.45, 0.15):          # the swing settles back to level
            self.play(Rotate(tag, angle, about_point=pivot), run_time=0.45)
        five = tag[2][-1]
        pointer = Arrow(five.get_top() + UP * 1.4, five.get_top() + UP * 0.1, buff=0, color=FOCUS, stroke_width=6)
        self.play(GrowArrow(pointer))

        self.at('At school')
        school = Text('school rule: a 5 rounds up', font_size=30, color=SCAFFOLD)
        guess = Text('→  $2.68', font_size=36, color=SCAFFOLD)
        VGroup(school, guess).arrange(RIGHT, buff=0.4).next_to(tag, DOWN, buff=0.8)
        self.play(FadeIn(school, shift=UP * 0.2))
        self.at('so the answer is')
        self.play(FadeIn(guess, shift=RIGHT * 0.3))

        # [V6.1b] the q06-01 panel types out on the left; the console prints round(2.675, 2) = 2.67
        code = code_panel(snippet_lines(Q1, 5, 6), font_size=20).to_corner(UL, buff=0.45).shift(DOWN * 0.5)
        con = Console(snippet_output(Q1)[:4], font_size=30)
        con.next_to(code, DOWN, buff=0.4).align_to(code, LEFT)
        self.at('Python says two sixty-seven', lead=1.8)
        self.play(FadeOut(VGroup(school, guess, pointer)), tag.animate.scale(0.6).move_to([5.0, 2.8, 0]),
                  FadeIn(code.background), run_time=0.6)
        self.play(type_code(code, run_time=1.0))
        self.add(code)
        self.play(FadeIn(con.background), run_time=0.3)
        self.play(con.type_line(0, run_time=0.8))
        seven = con.lines[0].chars(len(con.lines[0].source) - 1)
        self.play(seven.animate.set_color(ERROR).scale(1.6), run_time=0.35)
        self.play(seven.animate.scale(1 / 1.6), run_time=0.35)

        # [V6.1c] the next three lines print one by one; a "?" over the first two; the QR code
        self.at('A dollar and half a cent')
        card = show_card(self, 'q06-01')
        marks = VGroup()
        self.play(con.type_line(1, run_time=0.8))
        mark = Text('?', font_size=34, color=FOCUS).next_to(result_glyphs(con.lines[1]), RIGHT, buff=0.25)
        marks.add(mark)
        self.play(FadeIn(mark, shift=DOWN * 0.15), run_time=0.4)
        self.at('Twelve and a half cents')
        self.play(con.type_line(2, run_time=0.8))
        mark = Text('?', font_size=34, color=FOCUS).next_to(result_glyphs(con.lines[2]), RIGHT, buff=0.25)
        marks.add(mark)
        self.play(FadeIn(mark, shift=DOWN * 0.15), run_time=0.4)
        self.at('And thirty-seven and a half')
        self.play(con.type_line(3, run_time=0.8))

        # Four amounts that each end in a five; they don't agree: three go down, one goes up
        self.at('Four amounts that each end in a five')
        fives = VGroup()
        for line in con.lines:
            typed = line.source[line.source.index('(') + 1:line.source.index(',')]
            fives.add(line.part(typed)[-1])
        self.play(*[g.animate.set_color(FOCUS).scale(1.4) for g in fives], run_time=0.5)
        self.play(*[g.animate.scale(1 / 1.4) for g in fives], run_time=0.4)
        self.at("they don't even agree")
        arrows = VGroup()
        column_x = con.background.get_right()[0] + 1.1
        for line in con.lines:
            typed = Decimal(line.source[line.source.index('(') + 1:line.source.index(',')])
            printed = Decimal(line.source.split('= ')[1])
            direction = UP if printed > typed else DOWN       # from the two printed numbers
            y = line.anchor()[1]
            arrows.add(Arrow([column_x, y, 0] - direction * 0.22, [column_x, y, 0] + direction * 0.22, buff=0,
                             color=FOCUS, stroke_width=6, max_tip_length_to_length_ratio=0.45))
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.3), run_time=1.2)

        self.at('It can.')
        hide_card(self, card, 8.0, FadeOut(marks))
        self.at('Every one of these answers follows a precise rule')
        self.play(arrows.animate.set_color(EXACT), run_time=0.6)

        # [V6.1d] the tag flips; on its back the stored value scrolls past in tiny blue digits
        self.at('two different rules tangled together')
        self.play(tag.animate.scale(0.9 / 0.6).move_to([4.95, 1.2, 0]), run_time=0.7)
        back = VGroup(tag[0].copy().set_fill(PANEL, 1).set_stroke(MONEY, 3), tag[1].copy().set_fill(MONEY, 1))
        self.play(tag.animate.stretch(0.02, 0), run_time=0.3, rate_func=rate_functions.ease_in_sine)
        self.remove(tag)
        back.stretch(0.02, 0)
        self.add(back)
        self.play(back.animate.stretch(50, 0), run_time=0.3, rate_func=rate_functions.ease_out_sine)
        digits = output_line(Q1, 'stored 2.675').split('= ')[1]
        left, right = back[0].get_left()[0] + 0.45, back[0].get_right()[0] - 0.2
        y = back[0].get_y()
        ticker = MonoLine(digits, font_size=22, color=STORED).set_anchor([right, y, 0])

        def scroll(m, dt):
            m.shift(LEFT * 1.4 * dt)
            if m.glyphs[-1].get_right()[0] < left:
                m.set_anchor([right, y, 0])
            for g in m.glyphs:
                x = g.get_x()
                g.set_opacity(float(np.clip(min(x - left, right - x) / 0.25, 0, 1)))

        scroll(ticker, 0)
        ticker.add_updater(scroll)
        note = Text("what's really stored", font_size=20, color=SCAFFOLD).next_to(back, DOWN, buff=0.25)
        self.add(ticker)
        self.play(FadeIn(note), run_time=0.6)

        # how, where, and who: rounding is a decision
        self.at('how to round')
        how = label_box('how?', color=FOCUS, font_size=36)
        where = label_box('where?', color=FOCUS, font_size=36)
        who = label_box('who decides?', color=FOCUS, font_size=36)
        VGroup(how, where, who).arrange(RIGHT, buff=0.9).move_to(DOWN * 2.85)
        self.play(FadeIn(how, scale=0.8), run_time=0.4)
        self.at('and where')
        self.play(FadeIn(where, scale=0.8), run_time=0.4)
        self.at('a government')
        self.play(FadeIn(who, scale=0.8), run_time=0.4)
        self.finish()


# ---------------------------------------------------------------- 6.2

DESCRIBE = {
    'ROUND_UP': 'away from zero',
    'ROUND_DOWN': 'toward zero: truncation',
    'ROUND_CEILING': 'toward plus infinity',
    'ROUND_FLOOR': 'toward minus infinity',
    'ROUND_HALF_UP': 'nearest; ties away from zero',
    'ROUND_HALF_DOWN': 'nearest; ties toward zero',
    'ROUND_HALF_EVEN': 'nearest; ties to the even cent',
    'ROUND_05UP': 'truncate, unless that leaves a 0 or 5',
}


class Segment_6_2(Segment):
    """Eight ways to round, on a number line (q06-02)."""
    EPISODE, SEGMENT = 6, '6.2'

    def construct(self):
        out = snippet_output(Q2)
        amounts = out[0].split()                                  # the five amounts, as printed
        modes = [row.split()[0] for row in out[1:]]
        table = {row.split()[0]: row.split()[1:] for row in out[1:]}

        # [V6.2a] the number line 2.33 .. 2.37, an inset near 2.30, a mirrored line below zero
        main = cent_line('2.33', '2.37', 7.6, (-2.75, 3.0))
        inset = cent_line('2.295', '2.315', 3.2, (4.85, 3.0), ticks=['2.30', '2.31'])
        neg = cent_line('-2.37', '-2.33', 7.6, (-2.75, 1.05))
        homes = [main, main, main, inset, neg]
        dia = VGroup(*[line.diamond(a) for line, a in zip(homes, amounts)])
        home_points = [d.get_center() for d in dia]
        tags = VGroup(*[Text(a, font=MONO, font_size=18, color=FOCUS).next_to(d, UP, buff=0.08)
                        for d, a in zip(dia, amounts)])
        tags[0].align_to(dia[0], RIGHT)        # 2.341 and 2.345 sit close: lean their tags apart
        tags[1].align_to(dia[1], LEFT)
        dia.set_z_index(3)
        self.play(Create(main), Create(neg), run_time=1.2)
        self.play(Create(inset), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(VGroup(d, t), shift=DOWN * 0.2) for d, t in zip(dia, tags)], lag_ratio=0.2),
                  run_time=1.4)

        # Rounding to the cent: choose one of two neighbouring cents
        self.at('Rounding to the cent means')
        start = dia[0].get_center()
        choices = VGroup(*[DashedLine(start, main.point(v) + UP * 0.45, color=FOCUS, stroke_width=3).add_tip(
            tip_length=0.15) for v in ('2.34', '2.35')])
        self.play(Create(choices), run_time=0.8)

        # [V6.2b] code panel q06-02 and the QR code
        self.at('the code in the corner')
        code = code_panel(snippet_lines(Q2, 12, 15), font_size=18).to_edge(LEFT, buff=0.3)
        code.shift(UP * (-1.25 - code.get_bottom()[1]))
        self.play(FadeOut(choices), FadeIn(code.background), run_time=0.5)
        card = show_card(self, 'q06-02')
        self.play(type_code(code, run_time=1.6))
        self.add(code)

        con = output_console(Q2, font_size=18).to_corner(DL, buff=0.3)
        self.at('The first four ignore')
        self.play(FadeOut(code), FadeIn(con.background), run_time=0.6)
        self.play(con.type_line(0, run_time=0.8))

        state = {'box': None, 'label': None, 'trails': VGroup(), 'moved': []}

        def mode_label(mode):
            name = Text(mode, font=MONO, font_size=26, color=FOCUS)
            desc = wrapped_text(DESCRIBE[mode], 3.8, font_size=22, color=GREY_A)
            return VGroup(name, desc).arrange(DOWN, buff=0.15).move_to([4.75, -0.5, 0])

        def reset_anims(keep=()):
            anims = [FadeOut(state['trails'])] if len(state['trails']) else []
            anims += [dia[j].animate.move_to(home_points[j]) for j in state['moved'] if j not in keep]
            state['moved'] = [j for j in state['moved'] if j in keep]
            state['trails'] = VGroup()
            return anims

        def type_row(i, extra=()):
            mode = modes[i - 1]
            box = SurroundingRectangle(con.lines[i], color=FOCUS, buff=0.06)
            label = mode_label(mode)
            anims = [con.type_line(i, run_time=0.7), *extra]
            anims.append(Create(box) if state['box'] is None else ReplacementTransform(state['box'], box))
            anims.append(FadeIn(label) if state['label'] is None else FadeTransform(state['label'], label))
            state['box'], state['label'] = box, label
            self.play(*anims)
            return mode

        def move(mode, cols, width=4, run_time=0.9, values=None, path_arc=0.0, keep_trails=False):
            anims, trails = [], VGroup()
            for j in cols:
                value = (values or table[mode])[j]
                end = homes[j].point(Fraction(value)) + UP * 0.45
                begin = dia[j].get_center()
                if abs(end[0] - begin[0]) > 0.02:
                    step = np.sign(end[0] - begin[0]) * RIGHT
                    trail = Line(begin, end - step * 0.16, color=FOCUS, stroke_width=width, stroke_opacity=0.7)
                    trail.add_tip(tip_length=0.12 + width * 0.012, tip_width=0.1 + width * 0.012)
                    trail.set_z_index(2)
                    trails.add(trail)
                    anims.append(Create(trail))
                anims.append(dia[j].animate(path_arc=path_arc).move_to(end))
                if j not in state['moved']:
                    state['moved'].append(j)
            self.play(*anims, run_time=run_time)
            state['trails'].add(*trails)

        everything = range(5)
        # The four direction-only modes
        self.at('Round up moves away from zero')
        hide_card(self, card)
        move(type_row(1), everything)
        self.at('Round down moves toward zero')
        move(type_row(2, reset_anims()), everything)
        self.at('Ceiling always moves')
        move(type_row(3, reset_anims()), everything)
        self.at('and floor toward minus infinity')
        move(type_row(4, reset_anims()), everything)

        # Ceiling and up agree for positive amounts, not for negative ones
        def cells(i, first, last=None):
            last = first if last is None else last
            return con.lines[i].chars(16 + 8 * first, 24 + 8 * last)

        self.at('For positive amounts, ceiling and up agree')
        agree = VGroup(*[SurroundingRectangle(cells(i, 0, 3), color=EXACT, buff=0.05) for i in (1, 3)])
        self.play(Create(agree), run_time=0.7)
        self.at("they don't, and the last column")
        differ = VGroup(*[SurroundingRectangle(cells(i, 4), color=ERROR, buff=0.05) for i in (1, 3)])
        self.play(Create(differ), run_time=0.7)

        # [V6.2c] the three "half" modes: 2.341 goes to the nearest cent in all three and greys out
        self.at('The next three are the ones')
        self.play(FadeOut(agree), FadeOut(differ), *reset_anims(), run_time=0.6)
        self.at('go to the nearest cent')
        nontie, ties = (0, 3), (1, 2, 4)
        move('ROUND_HALF_UP', nontie)
        self.play(*[dia[j].animate.set_fill(GREY_C) for j in nontie], *[tags[j].animate.set_color(GREY_C)
                                                                       for j in nontie], FadeOut(state['trails']))
        state['trails'] = VGroup()
        self.at('sits exactly halfway')
        rings = VGroup()
        for j in ties:
            ring = Square(0.42).rotate(PI / 4).set_stroke(FOCUS, 3).move_to(dia[j])
            ring.add_updater(lambda m, d=dia[j]: m.move_to(d))
            rings.add(ring)
        self.play(Create(rings), run_time=0.7)

        self.at('Half up sends a tie away from zero')
        move(type_row(5, reset_anims(keep=nontie)), ties, width=8)
        self.at('Half down sends it toward zero')
        move(type_row(6, reset_anims(keep=nontie)), ties, width=8)

        # [V6.2d] half even: 2.34 and 2.36 are the even neighbours
        self.at('And half even sends it')
        type_row(7, reset_anims(keep=nontie))
        evens = VGroup(*[Text('even', font_size=20, color=EXACT).next_to(main.labels[k], DOWN, buff=0.06)
                         for k in (1, 3)])
        self.play(*[main.labels[k].animate.set_color(EXACT) for k in (1, 3)], FadeIn(evens, shift=UP * 0.1))
        self.at('So two thirty-four and a half goes down')
        move('ROUND_HALF_EVEN', (1, 4), width=8)
        self.at('and two thirty-five and a half goes up')
        move('ROUND_HALF_EVEN', (2,), width=8)

        # [V6.2e] ROUND_05UP: 2.301 truncates to 2.30, the 0 lights up, it bounces to 2.31
        self.at('The eighth mode is a curiosity')
        type_row(8, [*reset_anims(), FadeOut(rings), FadeOut(evens),
                     *[main.labels[k].animate.set_color(SCAFFOLD) for k in (1, 3)],
                     *[dia[j].animate.set_fill(FOCUS) for j in nontie],
                     *[tags[j].animate.set_color(FOCUS) for j in nontie]])
        self.at('It truncates')
        move('ROUND_DOWN', everything, width=3)                     # truncation: the ROUND_DOWN row
        self.at('leave a zero or a five')
        lit = VGroup(inset.labels[0][-1], main.labels[2][-1])       # the 0 of 2.30 and the 5 of 2.35
        self.play(*[g.animate.set_color(FOCUS).scale(1.5) for g in lit], run_time=0.5)
        self.at('rounds away from zero instead')
        move('ROUND_05UP', (3, 2), width=6, path_arc=-PI / 2)
        self.play(*[g.animate.scale(1 / 1.5) for g in lit], run_time=0.3)
        self.at('Two dollars, thirty and a tenth cents becomes')
        hit = SurroundingRectangle(cells(8, 3), color=EXACT, buff=0.05)
        self.play(Create(hit), run_time=0.6)

        # They disagree in every column
        self.at('Eight rules, all reasonable')
        self.play(FadeOut(hit), FadeOut(state['box']), *reset_anims(), lit.animate.set_color(SCAFFOLD), run_time=0.6)
        self.at('they disagree in every column')
        sweep = None
        for j in range(5):
            column = SurroundingRectangle(VGroup(*[cells(i, j) for i in range(1, 9)]), color=FOCUS, buff=0.06)
            self.play(Create(column) if sweep is None else ReplacementTransform(sweep, column), run_time=0.45)
            sweep = column
        self.at('Each is a choice')
        choice = Text('Each is a choice.', font_size=34, color=FOCUS).move_to([4.75, -2.4, 0])
        self.play(FadeOut(sweep), FadeIn(choice, shift=UP * 0.2))
        self.finish()


# ---------------------------------------------------------------- 6.3

CELL = 0.2                  # one amount in the zoomed strip
STRIP_TOP = 2.55
CURSOR_X = -3.3             # the column being read sits here
MASK_X = -4.75              # the label panel covers the strip left of this


def strip_pixels(columns, px, gap):
    """Pixels for a strip of amounts: one column per cent, ten rows (tenths of a cent);
    the tie row (x.xx5) is outlined in yellow."""
    yellow = (np.array(ManimColor(FOCUS).to_rgb()) * 255).astype(np.uint8)
    tile = np.zeros((10 * px, px, 4), np.uint8)
    tile[..., 3] = 255
    for r in range(10):
        y0 = r * px
        if px <= 2:
            tile[y0:y0 + px, :, :3] = yellow if r == 5 else 95
            continue
        if r == 5:
            b = max(2, px // 6)
            tile[y0 + gap:y0 + px - gap, gap:px - gap, :3] = yellow
            tile[y0 + gap + b:y0 + px - gap - b, gap + b:px - gap - b, :3] = 30
        else:
            tile[y0 + gap:y0 + px - gap, gap:px - gap, :3] = 85
    return np.tile(tile, (1, columns, 1))


class Meter(VGroup):
    """A balance-style meter: a needle that leans right for upward error, left for downward."""

    def __init__(self, name, radius=0.85, **kwargs):
        super().__init__(**kwargs)
        self.value = ValueTracker(0.0)
        self.radius = radius
        arc = Arc(radius=radius, start_angle=PI / 2 + 1.25, angle=-2.5, color=SCAFFOLD, stroke_width=4)
        zero = Line(UP * radius * 0.82, UP * radius * 1.1, color=SCAFFOLD, stroke_width=3)
        minus = Text('-', font_size=30, color=SCAFFOLD).move_to(radius * 1.2 * np.array([-np.sin(1.25), np.cos(1.25), 0]))
        plus = Text('+', font_size=30, color=SCAFFOLD).move_to(radius * 1.2 * np.array([np.sin(1.25), np.cos(1.25), 0]))
        self.pivot = Dot(ORIGIN, radius=0.07, color=GREY_A)
        self.needle = Line(ORIGIN, UP * radius * 0.9, color=FOCUS, stroke_width=5)
        self.name = Text(name, font_size=24).next_to(self.pivot, DOWN, buff=0.25)
        self.readout = number(0, decimals=3, font_size=30, include_sign=True).next_to(self.name, DOWN, buff=0.12)
        self.add(arc, zero, minus, plus, self.needle, self.pivot, self.name, self.readout)

        def follow(m):
            theta = 1.2 * np.tanh(self.value.get_value() / 0.02)
            centre = self.pivot.get_center()
            m.put_start_and_end_on(centre, centre + self.radius * 0.9 * np.array([np.sin(theta), np.cos(theta), 0]))

        def show(m):
            m.set_value(self.value.get_value())

        self.needle.add_updater(follow)
        self.readout.add_updater(show)


class Segment_6_3(Segment):
    """Why round half to even: the drift of half-up over 10,000 amounts (q06-03)."""
    EPISODE, SEGMENT = 6, '6.3'

    def construct(self):
        first = snippet_output(Q3)[0]
        n_amounts, n_ties = (int(n) for n in re.findall(r'\d+', first))     # 10000 and 1000, as printed
        up_final = float(re.search(r'error ([+-][\d.]+)', output_line(Q3, 'half-up')).group(1))
        even_final = float(re.search(r'error ([+-][\d.]+)', output_line(Q3, 'half-even')).group(1))
        columns = n_amounts // 10

        # [V6.3a] the whole strip, packed into a band; the ties are the yellow row
        overview = ImageMobject(strip_pixels(columns, 1, 0))
        overview.set_resampling_algorithm(RESAMPLING_ALGORITHMS['nearest'])
        overview.stretch_to_fit_width(12.6).stretch_to_fit_height(0.6).move_to(ORIGIN)
        title = Text('every amount from $0.000 to $9.999', font_size=28).next_to(overview, UP, buff=0.5)
        count = Text(f'{n_amounts} amounts', font_size=26, color=GREY_A).next_to(overview, DOWN, buff=0.4).align_to(overview, LEFT)
        tie_note = Text(f'{n_ties} ties', font_size=26, color=FOCUS).next_to(overview, DOWN, buff=0.4).align_to(overview, RIGHT)
        self.play(FadeIn(overview, scale=0.9), FadeIn(title), run_time=1.0)
        self.at('Because of what happens to ties')
        ties_box = SurroundingRectangle(overview, color=FOCUS, buff=0.06).stretch_to_fit_height(0.14).move_to(overview)
        self.play(Create(ties_box), FadeIn(tie_note, shift=UP * 0.15), run_time=0.8)
        self.play(FadeOut(ties_box), run_time=0.4)

        # The strip moves up as an overview; a zoomed window opens under it
        self.at('This code takes every amount')
        ov_target_y = 3.3
        self.play(overview.animate.stretch_to_fit_height(0.32).move_to([0.25, ov_target_y, 0]),
                  title.animate.scale(0.8).move_to([-3.6, 3.78, 0]),
                  FadeOut(tie_note), FadeOut(count), run_time=1.0)
        ov_left, ov_width = overview.get_left()[0], overview.width

        band = ImageMobject(strip_pixels(72, 16, 2))
        band.set_resampling_algorithm(RESAMPLING_ALGORITHMS['nearest'])
        band.stretch_to_fit_width(72 * CELL).stretch_to_fit_height(10 * CELL)
        pos = ValueTracker(0.0)                    # the cent column under the cursor (may be fractional)
        band_y = STRIP_TOP - 5 * CELL

        def place_band(m):
            frac = pos.get_value() - np.floor(pos.get_value())
            m.move_to([CURSOR_X - 9.5 * CELL - frac * CELL + m.width / 2, band_y, 0])

        place_band(band)
        band.add_updater(place_band)
        before = Rectangle(width=16, height=10 * CELL + 0.1).set_fill(BLACK, 1).set_stroke(width=0)
        after = before.copy()
        before.add_updater(lambda m: m.move_to([CURSOR_X - (pos.get_value() + 0.5) * CELL - 8, band_y, 0]))
        after.add_updater(lambda m: m.move_to([CURSOR_X + (columns - 0.5 - pos.get_value()) * CELL + 8, band_y, 0]))

        cent_labels = VGroup(*[Text(f'${c // 100}.{c % 100:02d}', font=MONO, font_size=18, color=SCAFFOLD)
                               for c in range(0, columns, 10)])
        label_y = STRIP_TOP - 10 * CELL - 0.22

        def place_labels(group):
            for k, label in enumerate(group):
                x = CURSOR_X + (10 * k - pos.get_value()) * CELL
                label.move_to([x, label_y, 0])
                label.set_opacity(1 if MASK_X + 0.4 < x < 6.6 else 0)

        place_labels(cent_labels)
        cent_labels.add_updater(place_labels)

        def row_y(r):
            return STRIP_TOP - (r + 0.5) * CELL

        panel = Rectangle(width=MASK_X + 7.3, height=10 * CELL + 0.8).set_fill(BLACK, 1).set_stroke(width=0)
        panel.move_to([(MASK_X - 7.3) / 2, band_y, 0])
        side = VGroup(
            Text('exact', font_size=20, color=GREY_A).move_to([MASK_X - 0.75, row_y(0), 0]),
            Text('rounds down', font_size=20, color=GREY_A).move_to([MASK_X - 1.15, row_y(2.5), 0]),
            Text('tie', font_size=22, color=FOCUS).move_to([MASK_X - 0.55, row_y(5), 0]),
            Text('rounds up', font_size=20, color=GREY_A).move_to([MASK_X - 1.0, row_y(7.5), 0]),
            Line([MASK_X - 0.12, row_y(0.6), 0], [MASK_X - 0.12, row_y(4.4), 0], color=SCAFFOLD, stroke_width=2),
            Line([MASK_X - 0.12, row_y(5.6), 0], [MASK_X - 0.12, row_y(9.4), 0], color=SCAFFOLD, stroke_width=2))
        for item in side[:4]:
            item.align_to([MASK_X - 0.25, 0, 0], RIGHT)
        marker = Triangle(color=FOCUS).set_fill(FOCUS, 1).scale(0.09)
        marker.add_updater(lambda m: m.move_to([ov_left + (pos.get_value() + 0.5) / columns * ov_width,
                                                ov_target_y - 0.3, 0]))
        lens = VGroup(DashedLine([ov_left, ov_target_y - 0.18, 0], [MASK_X, STRIP_TOP + 0.02, 0], color=GREY_D),
                      DashedLine([ov_left + 72 / columns * ov_width, ov_target_y - 0.18, 0], [7.1, STRIP_TOP + 0.02, 0],
                                 color=GREY_D))
        self.play(FadeIn(band), FadeIn(before), FadeIn(after), FadeIn(cent_labels), Create(lens), run_time=0.8)
        self.add_foreground_mobjects(panel)
        self.play(FadeIn(side), FadeIn(marker), run_time=0.6)
        self.add_foreground_mobjects(side)

        self.at('ten thousand amounts')
        self.play(FadeOut(lens), Indicate(title, color=FOCUS, scale_factor=1.05), run_time=0.8)

        # [V6.3b] two meters start at zero
        self.at('adds up the errors')
        up = Meter('half-up').move_to([-4.6, -0.95, 0])
        even = Meter('half-even').move_to([-1.4, -0.95, 0])
        self.play(FadeIn(up), FadeIn(even), run_time=0.8)

        cursor = Square(CELL).set_stroke(FOCUS, 3).move_to([CURSOR_X, row_y(0), 0])

        def error(amount, mode):
            # computed here with decimal, exactly as q06-03 does: rounded minus true
            return float(amount.quantize(CENT, mode) - amount)

        # Non-ties nudge both meters by the same amount; over each cent they cancel
        self.at('For most amounts')
        self.play(Create(cursor), run_time=0.3)
        total = 0.0
        for c in range(3):
            if c:
                self.play(pos.animate.set_value(c), cursor.animate.move_to([CURSOR_X, row_y(0), 0]), run_time=0.3)
            for r in range(10):
                if r == 5:
                    continue
                total += error(Decimal(10 * c + r) / 1000, ROUND_HALF_UP)
                self.play(cursor.animate.move_to([CURSOR_X, row_y(r), 0]), up.value.animate.set_value(total),
                          even.value.animate.set_value(total), run_time=0.24)

        self.at('rounds up by three tenths')
        pair = VGroup()
        for r, text in ((3, '-0.3¢'), (7, '+0.3¢')):
            box = Square(CELL).set_stroke(FOCUS, 4).move_to([CURSOR_X, row_y(r), 0])
            label = Text(text, font_size=24, color=FOCUS)
            label.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.08)
            label.next_to(box, RIGHT, buff=0.5)
            pair.add(box, label)
        self.play(FadeOut(cursor), FadeIn(pair), run_time=0.6)

        # [V6.3c] the ties: half-up ticks up every time; half-even alternates down, up
        self.at('But one amount in ten is an exact tie')
        self.play(FadeOut(pair), pos.animate.set_value(0), run_time=0.7)
        tie_row = Rectangle(width=7.1 - MASK_X, height=CELL + 0.08).set_stroke(FOCUS, 4)
        tie_row.move_to([(7.1 + MASK_X) / 2, row_y(5), 0])
        self.play(Create(tie_row), run_time=0.6)
        self.play(FadeOut(tie_row), run_time=0.5)

        self.at('Half up rounds every tie upward')
        cursor.move_to([CURSOR_X, row_y(5), 0])
        self.play(FadeIn(cursor), run_time=0.2)
        up_total, even_total = 0.0, 0.0
        pops = VGroup()
        for j in range(6):
            tie = Decimal(10 * j + 5) / 1000
            du, de = error(tie, ROUND_HALF_UP), error(tie, ROUND_HALF_EVEN)
            up_total += du
            even_total += de
            pop_up = Text('+½¢', font_size=26, color=ERROR).move_to(up.get_center() + RIGHT * 1.45 + UP * 0.35)
            pop_even = Text('+½¢' if de > 0 else '-½¢', font_size=26, color=GREY_A).move_to(
                even.get_center() + RIGHT * 1.45 + UP * 0.35)
            self.play(pos.animate.set_value(j), up.value.animate.set_value(up_total),
                      even.value.animate.set_value(even_total), FadeOut(pops), FadeIn(pop_up, shift=UP * 0.2),
                      FadeIn(pop_even, shift=UP * 0.2), run_time=0.6)
            pops = VGroup(pop_up, pop_even)
        self.play(FadeOut(pops), run_time=0.3)

        # A thousand ties: the strip races to the end
        self.at('A thousand ties')
        k = ValueTracker(6)

        def race(_):
            done = int(k.get_value())
            pos.set_value(k.get_value() - 1)
            up.value.set_value(0.005 * done)                       # +½¢ for every tie
            even.value.set_value(-0.005 if done % 2 else 0.0)      # down, up, down, up ...

        racer = Mobject().add_updater(race)
        self.add(racer)
        self.play(k.animate.set_value(n_ties), FadeOut(cursor), run_time=4.5, rate_func=rate_functions.ease_in_out_sine)
        self.remove(racer)
        up.value.set_value(up_final)
        even.value.set_value(even_final)
        self.play(up.readout.animate.set_color(ERROR), up.needle.animate.set_color(ERROR), run_time=0.5)
        self.play(Indicate(up.readout, color=ERROR, scale_factor=1.2), run_time=0.8)

        # [V6.3d] half-even cancels: its needle wobbles and returns; the console; the QR code
        self.at('Half even rounds half of the ties up')
        for value in (-0.005, 0.0, -0.005, 0.0):
            self.play(even.value.animate.set_value(value), run_time=0.35)
        con = output_console(Q3, font_size=20).to_corner(DL, buff=0.35)
        self.at('Total drift: zero')
        self.play(even.readout.animate.set_color(EXACT), even.needle.animate.set_color(EXACT), FadeIn(con.background),
                  run_time=0.5)
        card = show_card(self, 'q06-03')
        for i in range(3):
            self.play(con.type_line(i, run_time=0.7))
        self.play(con.part(1, up_final_text(con.lines[1].source)).animate.set_color(ERROR),
                  con.part(2, up_final_text(con.lines[2].source)).animate.set_color(EXACT), run_time=0.5)

        # [V6.3e] the IEEE 754 default; Python's round() too
        self.at("That's why it's the default")
        band.clear_updaters()
        self.play(*[FadeOut(m) for m in (band, before, after, cent_labels, overview, marker, title)], run_time=0.6)
        self.remove_foreground_mobjects(panel, side)
        self.remove(panel, side)
        ieee = Text("IEEE 754's default: round to nearest, ties to even.", font_size=32, color=FOCUS).move_to(UP * 3.1)
        self.play(Write(ieee), run_time=1.4)
        self.at("It's also what Python's built-in round")
        rounded = code_text(output_line(Q1, 'round(0.125'), font_size=28, color=WHITE)
        evens = Text('ties to even', font_size=24, color=EXACT)
        VGroup(rounded, evens).arrange(RIGHT, buff=0.6).move_to(UP * 2.0)
        self.play(FadeIn(rounded, shift=UP * 0.2), run_time=0.6)
        self.play(FadeIn(evens), result_glyphs(rounded).animate.set_color(EXACT), run_time=0.5)
        self.at("often called banker's rounding")
        bankers = Text("“banker's rounding”: a common name, a disputed history", font_size=24, color=SCAFFOLD)
        bankers.move_to(UP * 1.05)
        self.play(FadeIn(bankers, shift=UP * 0.2))
        hide_card(self, card)
        self.at('plenty of financial rules say half up')
        still = Text('half-up: still the rule in plenty of places', font_size=24, color=GREY_A)
        still.next_to(even, RIGHT, buff=0.9).align_to(up.name, UP)
        self.play(FadeIn(still, shift=LEFT * 0.2), Indicate(up.name, color=FOCUS), run_time=0.8)
        self.at('who gets to choose')
        who = Text('who chooses?', font_size=34, color=FOCUS)
        # Right of the q06-03 console, which reaches to about x = 2.8 below the gauges.
        who.move_to([3.4 + who.width / 2, still.get_y() - 0.9, 0])
        self.play(FadeIn(who, scale=0.8))
        self.finish()


def up_final_text(source):
    """The first signed total in a q06-03 output line ('+5.000')."""
    return re.search(r'[+-][\d.]+', source).group(0)


# ---------------------------------------------------------------- 6.4

def schematic_ticks(lo_x, hi_x, mid_x, offset, spacing, y, avoid=(), height=0.36):
    """Blue double ticks drawn far apart (not to scale), placed so that mid_x sits `offset`
    spacings to the right of one of them, as the real doubles sit around the true value."""
    ticks = VGroup()
    j = -40
    while True:
        x = mid_x + (j - offset) * spacing
        j += 1
        if x > hi_x:
            break
        if x < lo_x or any(abs(x - a) < 0.15 for a in avoid):
            continue
        ticks.add(Line([x, y - height / 2, 0], [x, y + height / 2, 0], color=STORED, stroke_width=3))
    return ticks


class Segment_6_4(Segment):
    """Two layers of rounding: the float layer, then the rounding rule (q06-01)."""
    EPISODE, SEGMENT = 6, '6.4'

    def construct(self):
        # The cold open's four answers: round() rounds half to even, but that explains only two
        con = Console(snippet_output(Q1)[:4], font_size=28).move_to([-3.7, 0.6, 0])
        self.play(FadeIn(con.background), run_time=0.4)
        self.play(con.type_all(run_time_per_line=0.5))
        self.at('rounds half to even')
        header = Text('round(): half to even', font=MONO, font_size=26, color=FOCUS).next_to(con, UP, buff=0.4)
        self.play(FadeIn(header, shift=DOWN * 0.2))
        self.at('only explains two of the four')
        marks = VGroup()
        for i, line in enumerate(con.lines):
            mark = checkmark(size=0.32) if i >= 2 else Text('?', font_size=34, color=FOCUS)
            marks.add(mark.move_to([con.background.get_right()[0] + 0.45, line.anchor()[1], 0]))
        self.play(LaggedStart(*[FadeIn(m, scale=0.6) for m in marks], lag_ratio=0.2), run_time=0.9)

        # [V6.4d] (right half) 0.125 = 1/8 is stored exactly: a true tie, and half even sends it to 0.12
        divider = Line([1.65, 3.7, 0], [1.65, -2.95, 0], color=GREY_D, stroke_width=2)
        lo_x, hi_x, axis_y = 2.4, 6.6, 1.3
        mid = (lo_x + hi_x) / 2
        right_axis = Line([lo_x - 0.3, axis_y, 0], [hi_x + 0.3, axis_y, 0], color=SCAFFOLD, stroke_width=2)
        right_cents = VGroup(*[Line([x, axis_y - 0.4, 0], [x, axis_y + 0.4, 0], color=GREY_B, stroke_width=6)
                               for x in (lo_x, hi_x)])
        right_labels = VGroup(*[Text(t, font=MONO, font_size=24, color=SCAFFOLD).move_to([x, axis_y - 0.7, 0])
                                for t, x in (('0.12', lo_x), ('0.13', hi_x))])
        right_doubles = schematic_ticks(lo_x - 0.2, hi_x + 0.2, mid, 0.0, 0.9, axis_y, avoid=(lo_x, hi_x))
        right_dia = gem().move_to([mid, axis_y + 0.45, 0])
        right_tag = Text('0.125', font=MONO, font_size=22, color=FOCUS).next_to(right_dia, UP, buff=0.12)
        self.at('Twelve and a half cents')
        self.play(Create(divider), Create(right_axis), Create(right_cents), FadeIn(right_labels), run_time=0.8)
        self.play(Create(right_doubles), FadeIn(right_dia, shift=DOWN * 0.2), FadeIn(right_tag), run_time=0.8)
        self.at('one eighth')
        right_title = Text('0.125 = 1/8', font_size=30).move_to([4.5, 3.4, 0])
        self.play(FadeIn(right_title, shift=DOWN * 0.2))
        self.at("so it's stored exactly")
        on_tick = Dot([mid, axis_y + 0.18, 0], radius=0.08, color=STORED)
        exact = Text('stored exactly', font_size=24, color=STORED).move_to([mid, axis_y - 1.15, 0])
        stored125 = code_text(output_line(Q1, 'stored 0.125'), font_size=20, color=STORED).move_to([4.45, -0.5, 0])
        self.play(FadeIn(on_tick, scale=2), FadeIn(exact), run_time=0.6)
        self.play(FadeIn(stored125, shift=UP * 0.15), run_time=0.5)
        self.at('It really is a tie')
        tie_title = Text('a true tie', font_size=30, color=EXACT).next_to(right_title, DOWN, buff=0.15)
        self.play(FadeIn(tie_title, shift=DOWN * 0.15))
        self.at('half even sends it to twelve')
        to_even = CurvedArrow(right_dia.get_left() + LEFT * 0.05, [lo_x + 0.05, axis_y + 0.45, 0], angle=PI / 3,
                              color=EXACT, stroke_width=4, tip_length=0.18)
        even_tag = Text('even', font_size=20, color=EXACT).next_to(right_labels[0], DOWN, buff=0.06)
        self.play(Create(to_even), right_labels[0].animate.set_color(EXACT), FadeIn(even_tag), run_time=0.9)
        self.at('Thirty-seven and a half cents')
        r375 = code_text(output_line(Q1, 'round(0.375'), font_size=22, color=WHITE).move_to([4.3, -1.35, 0])
        why375 = Text('3/8: exact, a true tie, 8 is even', font_size=20, color=EXACT).next_to(r375, DOWN, buff=0.15)
        self.play(FadeIn(r375, shift=UP * 0.15), con.lines[3].animate.set_color(FOCUS), run_time=0.6)
        self.at('half even sends it to thirty-eight')
        self.play(FadeIn(why375), result_glyphs(r375).animate.set_color(EXACT), run_time=0.6)
        self.at('So far, so consistent')
        self.play(Indicate(marks[2:], color=EXACT, scale_factor=1.3), run_time=0.8)

        # [V6.4a] (left half) the float line near 2.675: the true value sits exactly halfway
        self.at("But two point six seven five isn't stored exactly")
        self.play(FadeOut(VGroup(con, header, marks)), run_time=0.5)
        a, b, y0 = -6.0, 0.8, 1.3
        m = (a + b) / 2
        axis = Line([a - 0.45, y0, 0], [b + 0.45, y0, 0], color=SCAFFOLD, stroke_width=2)
        cents = VGroup(*[Line([x, y0 - 0.4, 0], [x, y0 + 0.4, 0], color=GREY_B, stroke_width=6) for x in (a, b)])
        cent_tags = VGroup(*[Text(t, font=MONO, font_size=24, color=SCAFFOLD).move_to([x, y0 - 0.7, 0])
                             for t, x in (('2.67', a), ('2.68', b))])
        # Around 2.675 the doubles lie 0.6 and 0.4 of a spacing either side (2.675 - stored = 0.4 ulp)
        doubles = schematic_ticks(a - 0.4, b + 0.4, m, 0.4, 0.9, y0, avoid=(a, b))
        dia = gem().move_to([m, y0 + 0.45, 0])
        dia_tag = Text('2.675', font=MONO, font_size=22, color=FOCUS).next_to(dia, UP, buff=0.12)
        not_scale = Text('blue: doubles, not to scale', font_size=18, color=SCAFFOLD).move_to([-0.15, y0 + 0.75, 0])
        left_title = Text('2.675', font_size=30).move_to([-2.6, 3.4, 0])
        self.play(Create(axis), Create(cents), FadeIn(cent_tags), FadeIn(left_title), run_time=0.8)
        self.play(Create(doubles), FadeIn(not_scale), FadeIn(dia, shift=DOWN * 0.2), FadeIn(dia_tag), run_time=0.8)
        halfway = DashedLine([m, y0 - 0.3, 0], [m, y0 + 0.25, 0], color=FOCUS, stroke_width=2)
        self.play(Create(halfway), run_time=0.4)

        # [V6.4b] typing it rounds it to the nearest double, a hair below halfway; the magnifier
        self.at('When you typed it')
        snapped_x = m - 0.4 * 0.9
        stored_dot = Dot([snapped_x, y0 + 0.18, 0], radius=0.08, color=STORED)
        snap = Arrow(dia.get_bottom() + DOWN * 0.02, stored_dot.get_center() + UP * 0.06, buff=0, color=FOCUS,
                     stroke_width=4, max_tip_length_to_length_ratio=0.35)
        self.play(GrowArrow(snap), FadeIn(stored_dot, scale=2), run_time=0.7)
        lens = Circle(radius=0.55, color=GREY_B, stroke_width=3).move_to([m - 0.2, y0 + 0.15, 0])
        box = Rectangle(width=6.8, height=2.45, color=GREY_B, stroke_width=2).move_to([-2.85, -1.55, 0])
        rays = VGroup(Line(lens.point_at_angle(PI * 1.15), box.get_corner(UL), color=GREY_D, stroke_width=2),
                      Line(lens.point_at_angle(-PI * 0.15), box.get_corner(UR), color=GREY_D, stroke_width=2))
        ulp = Fraction(math.ulp(2.675))
        real = FloatLine(Fraction('2.675') - Fraction(5, 2) * ulp, Fraction('2.675') + Fraction(5, 2) * ulp, width=6.0)
        real.move_to([-2.85, -1.45, 0])
        real_dia = real.diamond('2.675')
        real_tag = Text('2.675', font=MONO, font_size=20, color=FOCUS).next_to(real_dia, UP, buff=0.1)
        box_title = Text('zoomed in: the real doubles near 2.675', font_size=20, color=SCAFFOLD)
        box_title.move_to(box.get_corner(DL) + RIGHT * (box_title.width / 2 + 0.2) + UP * 0.28)
        self.play(Create(lens), Create(rays), Create(box), run_time=0.8)
        self.play(Create(real), FadeIn(real_dia), FadeIn(real_tag), FadeIn(box_title), run_time=0.8)
        self.at('a hair below the halfway point')
        real_snap = real.snap('2.675')
        hair = Text('a hair below halfway', font_size=20, color=FOCUS).move_to([-0.75, -0.75, 0])
        self.play(Create(real_snap), FadeIn(hair), run_time=0.8)

        self.at('Two point six seven four nine')
        stored_text = output_line(Q1, 'stored 2.675')
        short = stored_text.split('= ')[1][:19] + '…'                  # the stored digits, cut short
        near = real.point(real.nearest('2.675'))
        short_tag = Text(short, font=MONO, font_size=20, color=STORED).next_to(near, DOWN, buff=0.35)
        bottom = code_text(stored_text, font_size=20, color=STORED).to_edge(DOWN, buff=0.25).to_edge(LEFT, buff=0.35)
        self.play(FadeIn(short_tag, shift=UP * 0.1), run_time=0.6)
        self.play(FadeIn(bottom, shift=UP * 0.15), run_time=0.6)

        # [V6.4c] the second arrow: round() takes that double to the nearer cent, 2.67
        self.at('slightly closer to two sixty-seven')
        down = CurvedArrow(stored_dot.get_center() + UP * 0.1, [a + 0.06, y0 + 0.45, 0], angle=PI / 3,
                           color=STORED, stroke_width=4, tip_length=0.18)
        self.play(Create(down), cent_tags[0].animate.set_color(STORED), run_time=1.0)
        self.at('The same thing happens to a dollar and half a cent')
        r1005 = code_text(output_line(Q1, 'round(1.005'), font_size=22, color=WHITE).move_to([4.3, -2.3, 0])
        why1005 = Text('same story: stored just below the tie', font_size=20, color=SCAFFOLD).next_to(r1005, DOWN, buff=0.15)
        self.play(FadeIn(r1005, shift=UP * 0.15), FadeIn(why1005), run_time=0.7)

        self.at("That's the second layer")
        layer2 = Text('layer 2: round() rounds that double to cents', font_size=22, t2c={'layer 2:': FOCUS})
        layer2.move_to([-2.6, 2.5, 0])
        self.play(FadeIn(layer2, shift=DOWN * 0.15))
        self.at('already rounded your number once')
        layer1 = Text('layer 1: typing 2.675 rounds to a double', font_size=22, t2c={'layer 1:': FOCUS})
        layer1.next_to(box, DOWN, buff=0.18).align_to(box, LEFT)
        self.play(FadeIn(layer1, shift=UP * 0.15))
        self.at('The ties you meant may not be ties')
        not_tie = Text('not a tie any more', font_size=30, color=ERROR).next_to(left_title, DOWN, buff=0.15)
        not_tie.align_to(left_title, ORIGIN)
        # keep the two titles on the same baseline as the right half's
        not_tie.move_to([-2.6, tie_title.get_y(), 0])
        self.play(FadeIn(not_tie, shift=DOWN * 0.15))

        # The fix: no float layer. [V6.4e] Decimal('2.675') rounded half up is 2.68
        self.at('never let the float layer happen')
        strike = Line(layer1.get_left() + LEFT * 0.05, layer1.get_right() + RIGHT * 0.05, color=ERROR, stroke_width=4)
        self.play(FadeOut(VGroup(real, real_dia, real_tag, real_snap, hair, short_tag, box_title, lens, rays, box,
                                 doubles, snap, stored_dot, down, not_scale)),
                  cent_tags[0].animate.set_color(SCAFFOLD), run_time=0.8)
        self.play(Create(strike), layer1.animate.set_opacity(0.5), run_time=0.5)
        self.at('Start from the digits you meant')
        fixed = code_text(output_line(Q1, "Decimal('2.675')"), font_size=26, color=EXACT)
        fixed.to_edge(DOWN, buff=0.3).to_edge(LEFT, buff=0.35)
        self.play(FadeOut(bottom, shift=DOWN * 0.2), run_time=0.4)
        self.play(AddTextLetterByLetter(fixed.glyphs, time_per_char=0.04))
        self.add(fixed)
        self.at('rounded half up to the cent, is two sixty-eight')
        up_arrow = CurvedArrow(dia.get_right() + RIGHT * 0.05, [b - 0.06, y0 + 0.45, 0], angle=-PI / 3, color=EXACT,
                               stroke_width=4, tip_length=0.18)
        self.play(Create(up_arrow), cent_tags[1].animate.set_color(EXACT), run_time=0.9)
        self.at('only one layer of rounding')
        one = Text('one layer: the rule you chose', font_size=24, color=EXACT).move_to(layer2)
        self.play(FadeTransform(layer2, one), FadeOut(halfway), run_time=0.8)
        self.finish()


# ---------------------------------------------------------------- 6.5

RECEIPT_W, RECEIPT_FS = 5.4, 24


def receipt_columns():
    return int((RECEIPT_W - 0.5) / MonoLine('M', font_size=RECEIPT_FS).cell)


def receipt_variant(line, label, amount, color=INK):
    """A receipt line with a different amount, on the same anchor (for swapping amounts)."""
    text = label + amount.rjust(receipt_columns() - len(label))
    return MonoLine(text, font_size=RECEIPT_FS, color=color).set_anchor(line.anchor())


class Segment_6_5(Segment):
    """Per line or per invoice: where you round changes the answer (q06-04)."""
    EPISODE, SEGMENT = 6, '6.5'

    def construct(self):
        out = snippet_output(Q4)
        exact_line = out[0].split(': ')[1]                                  # 0.081675
        per_line = re.findall(r'\d+\.\d+', out[1])                          # 0.08, 0.08, 0.08, 0.24
        exact_total = out[2].split(': ')[1]                                 # 0.245025
        rounded_total = out[3].split()[-1]                                  # 0.25
        price = re.search(r'Decimal\("([\d.]+)"\)', snippet_find(Q4, 'items =')).group(1)   # 0.99
        subtotal = str(3 * Decimal(price))                                  # 2.97, computed here
        rate = Decimal(re.search(r'"([\d.]+)"', snippet_find(Q4, 'rate =')).group(1))
        percent = f'{rate * 100:.2f}%'                                      # 8.25%

        # How, then where
        how = label_box('how to round', color=GREY_B, font_size=30)
        where = label_box('where to round', color=FOCUS, font_size=30)
        VGroup(how, where).arrange(RIGHT, buff=1.2)
        self.play(FadeIn(how, shift=UP * 0.2))
        self.at('Just as important is where')
        self.play(FadeIn(where, shift=UP * 0.2), how.animate.set_opacity(0.4))

        # [V6.5a] the receipt: three items at 0.99, subtotal, an 8.25 % tax rate
        items = [(f'Item {k}', price) for k in (1, 2, 3)]
        start_rows = items + [('-', ''), ('Subtotal', subtotal), ('Tax rate', percent)]
        bill = receipt(start_rows, width=RECEIPT_W, font_size=RECEIPT_FS, title='RECEIPT')
        bill.move_to([0, 1.5, 0])
        self.at("Here's a receipt")
        self.play(FadeOut(VGroup(how, where)), FadeIn(bill, shift=UP * 0.3), run_time=0.8)
        code = code_panel(snippet_lines(Q4, 6, 8), font_size=18).move_to([0, -1.75, 0])
        self.at('There are no floats anywhere')
        self.play(FadeIn(code.background), run_time=0.3)
        self.play(type_code(code, run_time=1.4))
        self.add(code)
        self.at('Every number is an exact decimal')
        boxes = VGroup(*[line_highlight(code, i, color=EXACT) for i in range(3)])
        self.play(LaggedStart(*[Create(b) for b in boxes], lag_ratio=0.3), run_time=0.9)

        # And yet two answers: the receipt splits into two copies
        self.at('And yet there are two answers')
        right_copy = bill.copy()
        self.add(right_copy)
        left_x, right_x, top = -4.3, 1.3, 3.5
        self.play(FadeOut(code), FadeOut(boxes),
                  bill.animate.move_to([left_x, top - bill.height / 2, 0]),
                  right_copy.animate.move_to([right_x, top - bill.height / 2, 0]), run_time=0.9)
        asks = VGroup(*[Text('?', font_size=44, color=FOCUS).next_to(r.lines[-1], RIGHT, buff=0.3) for r in (bill, right_copy)])
        self.play(FadeIn(asks, scale=0.6), run_time=0.4)

        # [V6.5b] the left copy grows a tax entry on every line; the QR code
        self.at('If you work out the tax for each line')
        tax_row = ('  tax', exact_line)
        rows = [items[0], tax_row, items[1], tax_row, items[2], tax_row, ('-', ''), ('Subtotal', subtotal),
                (f'Tax {percent}', per_line[-1])]
        grown = receipt(rows, width=RECEIPT_W, font_size=RECEIPT_FS, title='RECEIPT')
        grown.move_to([left_x, top - grown.height / 2, 0])
        old = bill.lines                                     # title, items, rule, subtotal, tax rate
        new = grown.lines
        tax_lines = [new[2], new[4], new[6]]
        total_line = new[-1]
        total_label = total_line.part(f'Tax {percent}')
        total_amount = total_line.part(per_line[-1])
        pairs = [(old[0], new[0]), (old[1], new[1]), (old[2], new[3]), (old[3], new[5]), (old[4], new[7]),
                 (old[5], new[8])]
        self.play(FadeOut(asks), Transform(bill.paper, grown.paper),
                  *[o.animate.move_to(n) for o, n in pairs], FadeTransform(old[6], total_label), run_time=1.0)
        self.remove(bill, *[o for o, _ in pairs])
        self.add(grown.paper, *[n for _, n in pairs], total_label)
        card = show_card(self, 'q06-04')

        self.at('about eight point one seven cents')
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.2) for t in tax_lines], lag_ratio=0.25), run_time=1.0)
        self.at('Round that to eight cents')
        rounded = [receipt_variant(t, '  tax', per_line[k], color=STORED) for k, t in enumerate(tax_lines)]
        self.play(*[ReplacementTransform(t.part(exact_line), r.part(per_line[k])) for k, (t, r) in
                    enumerate(zip(tax_lines, rounded))], run_time=0.8)
        eights = VGroup(*[r.part(per_line[k]) for k, r in enumerate(rounded)])
        self.at('and the tax is twenty-four cents')
        flying = eights.copy()
        total_amount.set_color(STORED)
        self.play(ReplacementTransform(flying, total_amount), run_time=1.0)

        # [V6.5c] the right copy: one tax entry on the subtotal, 0.245025, which rounds to 0.25
        self.at('If you add up the items first')
        hide_card(self, card)
        right_rows = items + [('-', ''), ('Subtotal', subtotal), (f'Tax {percent}', exact_total)]
        whole = receipt(right_rows, width=RECEIPT_W, font_size=RECEIPT_FS, title='RECEIPT').move_to(right_copy)
        sub_box = SurroundingRectangle(right_copy.lines[5], color=FOCUS, buff=0.06)
        self.play(Create(sub_box), run_time=0.6)
        self.at('work out the tax on the total')
        self.play(FadeTransform(right_copy.lines[6], whole.lines[6]), FadeOut(sub_box), run_time=0.8)
        self.at('which rounds to twenty-five')
        right_total = receipt_variant(whole.lines[6], f'Tax {percent}', rounded_total, color=STORED)
        self.play(ReplacementTransform(whole.lines[6].part(exact_total), right_total.part(rounded_total)), run_time=0.8)
        right_label = whole.lines[6].part(f'Tax {percent}')
        right_amount = right_total.part(rounded_total)

        # [V6.5d] side by side: the totals glow; a penny hovers between them, unsure
        self.at('Which is right?')
        left_all = VGroup(grown.paper, *[n for _, n in pairs], total_label, total_amount,
                          *[t.part('  tax'.strip()) for t in tax_lines], eights)
        right_all = VGroup(right_copy.paper, *right_copy.lines[:6], right_label, right_amount)
        self.play(left_all.animate.shift(RIGHT * 0.7), right_all.animate.shift(RIGHT * 1.5), run_time=0.8)
        self.play(total_amount.animate.set_color(MONEY).scale(1.25), right_amount.animate.set_color(MONEY).scale(1.25),
                  run_time=0.5)
        coin_ = penny(0.35).move_to([(grown.paper.get_right()[0] + right_copy.paper.get_left()[0]) / 2, 1.2, 0])
        self.play(FadeIn(coin_, scale=0.5), run_time=0.4)
        for side in (LEFT, RIGHT):
            self.play(coin_.animate.shift(side * 0.3), rate_func=there_and_back, run_time=0.6)

        # [V6.5e] both get a green tick; the stamp
        self.at('Both.')
        ticks = VGroup(*[checkmark(size=0.6).next_to(p, UP, buff=0.2).align_to(p, RIGHT)
                         for p in (grown.paper, right_copy.paper)])
        self.play(FadeOut(coin_, scale=0.5), LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.3), run_time=0.8)
        self.at('The difference is a policy decision')
        words = Text('Both correct. Pick one, and write it down.', font_size=28, color=EXACT)
        frame = RoundedRectangle(width=words.width + 0.6, height=words.height + 0.5, corner_radius=0.1)
        frame.set_stroke(EXACT, 4)
        stamp = VGroup(frame, words).rotate(0.04).move_to([0.6, -3.35, 0])
        self.play(FadeIn(stamp, scale=1.4), run_time=0.5)

        # The trap: two systems, two rules, a cent apart
        self.at("If your checkout page")
        checkout = Text('checkout page: per line', font_size=24, color=GREY_A).next_to(grown.paper, UP, buff=0.2)
        invoicing = Text('invoicing system: on the total', font_size=24, color=GREY_A).next_to(right_copy.paper, UP, buff=0.2)
        self.play(FadeOut(ticks), FadeIn(checkout, shift=DOWN * 0.15), run_time=0.6)
        self.at('your invoicing system')
        self.play(FadeIn(invoicing, shift=DOWN * 0.15), run_time=0.6)
        self.at('disagree by a cent')
        apart = VGroup(SurroundingRectangle(total_amount, color=ERROR, buff=0.06),
                       SurroundingRectangle(right_amount, color=ERROR, buff=0.06))
        gap = Text('1¢', font_size=34, color=ERROR).move_to([(grown.paper.get_right()[0] + right_copy.paper.get_left()[0]) / 2,
                                                             (total_amount.get_y() + right_amount.get_y()) / 2, 0])
        self.play(Create(apart), FadeIn(gap, scale=0.6), run_time=0.7)
        self.at('So the rule has to be chosen once')
        self.play(FadeOut(apart), Indicate(stamp, color=EXACT, scale_factor=1.08), run_time=1.0)
        self.finish()


# ---------------------------------------------------------------- 6.6

class Segment_6_6(Segment):
    """When there's no penny: cash totals round to five cents."""
    EPISODE, SEGMENT = 6, '6.6'

    def construct(self):
        # [V6.6a] a register display: $1.01 ... $1.10
        totals = [Decimal(100 + k) / 100 for k in range(1, 11)]
        lines = stack_lines([MonoLine(f'${t:.2f}', font_size=28, color=GREY_A) for t in totals], spacing=1.6)
        screen = RoundedRectangle(width=lines.width + 0.8, height=lines.height + 0.7, corner_radius=0.12)
        screen.set_fill(PANEL, 1).set_stroke(GREY_D, 1)
        lines.move_to(screen)
        register = VGroup(screen, lines).move_to([-4.8, -0.55, 0])
        heading = Text('cash register', font_size=22, color=SCAFFOLD).next_to(screen, UP, buff=0.15)
        self.play(FadeIn(screen), FadeIn(heading), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in lines], lag_ratio=0.15), run_time=1.6)

        # [V6.6b] the penny fades out (2013); a plain silver 5¢ replaces it
        self.at('comes from the coins themselves')
        one = penny(0.6).move_to([1.3, 2.6, 0])
        self.play(FadeIn(one, scale=0.6))
        self.at('In 2013')
        year = Text('2013', font_size=24, color=SCAFFOLD).next_to(one, DOWN, buff=0.15)
        canada = Text('Canada: no more pennies', font_size=26).next_to(one, RIGHT, buff=0.5)
        self.play(FadeIn(year), FadeIn(canada, shift=LEFT * 0.2), run_time=0.6)
        self.at('stopped distributing pennies')
        nickel = coin('5¢', 0.6, color=GREY_B).move_to(one)
        self.play(FadeOut(one, scale=0.6), FadeOut(year), FadeIn(nickel, scale=0.6), run_time=1.0)

        # [V6.6d] a card payment is charged to the cent
        self.at('card payments are still charged')
        card = RoundedRectangle(width=1.3, height=0.85, corner_radius=0.1).set_fill(BLUE_E, 1).set_stroke(GREY_B, 2)
        stripe = Rectangle(width=1.3, height=0.16).set_fill(GREY_D, 1).set_stroke(width=0).move_to(card).shift(UP * 0.18)
        chip = RoundedRectangle(width=0.26, height=0.2, corner_radius=0.04).set_fill(MONEY, 1).set_stroke(width=0)
        chip.move_to(card.get_corner(DL) + RIGHT * 0.3 + UP * 0.25)
        card_icon = VGroup(card, stripe, chip).move_to([1.3, 0.5, 0])
        basket = totals[2]                                     # $1.03, from the visual note
        charged = Text(f'${basket:.2f} charged: ${basket:.2f}', font_size=28, color=EXACT).next_to(card_icon, RIGHT, buff=0.4)
        self.play(FadeIn(card_icon, shift=RIGHT * 0.2), FadeIn(charged), run_time=0.7)

        # [V6.6c] cash: each total goes to the nearest five cents (computed here with decimal)
        nickel_step = Decimal('0.05')

        def to_nickel(t):
            return (t / nickel_step).quantize(Decimal(1), ROUND_HALF_UP) * nickel_step

        pitch = lines[1].get_y() - lines[0].get_y()
        targets = {}
        for value in sorted({to_nickel(t) for t in totals}):
            row = round((value - Decimal('1.01')) * 100)       # row of the register line it sits beside
            y = lines[0].get_y() + pitch * row
            targets[value] = MonoLine(f'${value:.2f}', font_size=30, color=MONEY).move_to([-1.2, y, 0])
        self.at('But when you pay in cash')
        cash_label = Text('cash: nearest 5¢', font_size=24, color=MONEY).move_to([-1.2, 3.45, 0])
        self.play(FadeIn(cash_label), LaggedStart(*[FadeIn(t, shift=LEFT * 0.2) for t in targets.values()],
                                                 lag_ratio=0.2), run_time=0.9)
        arrows = {}
        for t, line in zip(totals, lines):
            end = targets[to_nickel(t)]
            colour = GREY_B if to_nickel(t) == t else FOCUS
            arrows[t] = Arrow(line.get_right() + RIGHT * 0.15, end.get_left() + LEFT * 0.1, buff=0, color=colour,
                              stroke_width=3, max_tip_length_to_length_ratio=0.08)

        def draw(keys):
            self.play(*[GrowArrow(arrows[k]) for k in keys], run_time=0.7)

        self.at('A dollar and one or two cents')
        draw([t for t in totals if t in (Decimal('1.01'), Decimal('1.02'))])
        self.at('A dollar and three or four cents')
        draw([t for t in totals if t in (Decimal('1.03'), Decimal('1.04'))])
        rest = [t for t in totals if t not in [Decimal(x) / 100 for x in (101, 102, 103, 104)]]
        draw([t for t in rest if t < Decimal('1.08')])
        draw([t for t in rest if t >= Decimal('1.08')])

        self.at('its own increment')
        column = SurroundingRectangle(VGroup(*targets.values()), color=MONEY, buff=0.15)
        step = Text('increment: 5¢, not 1¢', font_size=24, color=MONEY).next_to(column, DOWN, buff=0.25)
        self.play(Create(column), FadeIn(step), run_time=0.8)

        # The same basket costs two amounts, depending on how you pay; both are correct
        self.at('one payment method but not another')
        self.play(FadeOut(column), FadeOut(step), run_time=0.4)
        self.at('The same basket of groceries')
        row = list(totals).index(basket)
        hot = SurroundingRectangle(lines[row], color=FOCUS, buff=0.08)
        paid = to_nickel(basket)
        small = coin('5¢', 0.42, color=GREY_B).move_to([1.3, -1.0, 0])
        cash = Text(f'${basket:.2f} in cash: ${paid:.2f}', font_size=28, color=MONEY).next_to(small, RIGHT, buff=0.55)
        cash.align_to(charged, LEFT)
        self.play(Create(hot), arrows[basket].animate.set_stroke(width=6), targets[paid].animate.scale(1.2), run_time=0.6)
        self.play(FadeIn(small, scale=0.6), FadeIn(cash, shift=LEFT * 0.2), run_time=0.7)
        self.at('both are correct')
        ticks = VGroup(checkmark(size=0.4).next_to(charged, RIGHT, buff=0.3),
                       checkmark(size=0.4).next_to(cash, RIGHT, buff=0.3))
        ticks[1].set_x(ticks[0].get_x())
        self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.3), run_time=0.7)

        # Other countries: the right question is "to which increment?"
        self.at('Several other countries')
        others = VGroup(coin('5¢', 0.32, color=GREY_B), coin('10¢', 0.32, color=GREY_B))
        others.arrange(RIGHT, buff=0.25).move_to([1.6, -2.4, 0])
        elsewhere = Text('elsewhere: 5¢ or 10¢', font_size=24, color=GREY_A).next_to(others, RIGHT, buff=0.35)
        self.play(FadeIn(others, scale=0.6), FadeIn(elsewhere), run_time=0.7)
        self.at("rounding to the cent isn't even")
        question = Text('round to the cent?', font_size=30).move_to([-4.8, -3.4, 0])
        question.set_x(0.9 + question.width / 2)
        strike = Line(question.get_left(), question.get_right(), color=ERROR, stroke_width=5)
        self.play(FadeIn(question), run_time=0.4)
        self.play(Create(strike), run_time=0.5)
        self.finish()


# ---------------------------------------------------------------- 6.7

def euro_triangle(scale=1.0):
    """DEM bottom left, FRF bottom right, EUR on top, with the two fixed rates on the edges."""
    source = snippet_source(Q5)
    dem_rate = re.search(r'DEM = Decimal\("([\d.]+)"\)', source).group(1)
    frf_rate = re.search(r'FRF = Decimal\("([\d.]+)"\)', source).group(1)
    eur, dem, frf = UP * 2.0, LEFT * 2.4 + DOWN * 2.0, RIGHT * 2.4 + DOWN * 2.0
    nodes = VGroup(*[label_box(name, color=c, font_size=30, fill=c)
                     for name, c in (('EUR', STORED), ('DEM', GREY_B), ('FRF', GREY_B))])
    for node, point in zip(nodes, (eur, dem, frf)):
        node.move_to(point)
    left_edge = Line(dem, eur, color=GREY_B, stroke_width=4)
    right_edge = Line(eur, frf, color=GREY_B, stroke_width=4)
    for edge in (left_edge, right_edge):
        edge.set_length(edge.get_length() - 1.1)
    bottom = DashedLine(dem + RIGHT * 0.65, frf + LEFT * 0.65, color=ERROR, stroke_width=4)
    angle = np.arctan2(eur[1] - dem[1], eur[0] - dem[0])
    left_tag = Text(f'{dem_rate} per euro', font_size=22, color=GREY_A).rotate(angle)
    left_tag.move_to((dem + eur) / 2 + np.array([-np.sin(angle), np.cos(angle), 0]) * 0.38)
    right_tag = Text(f'{frf_rate} per euro', font_size=22, color=GREY_A).rotate(-angle)
    right_tag.move_to((frf + eur) / 2 + np.array([np.sin(angle), np.cos(angle), 0]) * 0.38)
    bottom_tag = Text('cross rate (not allowed)', font_size=22, color=ERROR).next_to(bottom, DOWN, buff=0.15)
    group = VGroup(nodes, left_edge, right_edge, left_tag, right_tag, bottom, bottom_tag).scale(scale)
    group.nodes, group.left_edge, group.right_edge = nodes, left_edge, right_edge
    group.left_tag, group.right_tag, group.bottom, group.bottom_tag = left_tag, right_tag, bottom, bottom_tag
    return group


class Segment_6_7(Segment):
    """Rounding written into law: the 1999 euro conversion rules (q06-05)."""
    EPISODE, SEGMENT = 6, '6.7'

    def construct(self):
        # [V6.7a] the triangle of currencies and the two fixed rates
        tri = euro_triangle().move_to([-3.7, 0.2, 0])
        tri.bottom.set_stroke(opacity=0)
        tri.bottom_tag.set_opacity(0)
        law = Text('a rounding rule written into law', font_size=30, color=FOCUS).move_to(UP * 3.5)
        self.play(FadeIn(law, shift=DOWN * 0.2))
        self.at('When the euro was introduced')
        year = Text('1999', font_size=30, color=GREY_A).next_to(tri.nodes[0], RIGHT, buff=0.4)
        self.play(FadeOut(law), FadeIn(tri.nodes[0], scale=0.8), FadeIn(year), run_time=0.7)
        self.at('eleven national currencies')
        self.play(FadeIn(tri.nodes[1:], scale=0.8), Create(tri.left_edge), Create(tri.right_edge), run_time=0.9)
        self.at('One euro was set at')
        self.play(Write(tri.left_tag), Indicate(tri.nodes[1], color=FOCUS), run_time=1.0)
        self.at('and at six point five five nine five seven')
        self.play(Write(tri.right_tag), Indicate(tri.nodes[2], color=FOCUS), run_time=1.0)

        # [V6.7b] the rules type out beside it
        self.at('a European regulation spelled out')
        heading = Text('the conversion rules', font_size=28, color=FOCUS).move_to([3.0, 3.3, 0])
        self.play(FadeOut(year), FadeIn(heading, shift=DOWN * 0.2))
        texts = ['rates: 6 significant figures', 'never round or invert a rate',
                 'national currency → national currency goes through the euro',
                 'the euro amount: at least 3 decimals', 'results: nearest cent, halves up']
        rules = VGroup()
        for text in texts:
            body = wrapped_text(text, 6.0, font_size=24)
            bullet = Text('•', font_size=24, color=FOCUS).next_to(body[0] if len(body.submobjects) else body, LEFT,
                                                                   buff=0.2)
            rules.add(VGroup(bullet, body))
        rules.arrange(DOWN, buff=0.38, aligned_edge=LEFT).next_to(heading, DOWN, buff=0.45).set_x(3.1)
        for rule in rules:
            rule[0].align_to(rule[1], UP).shift(DOWN * 0.02)
        cues = ['six significant figures', 'you may not round them', 'you must go through the euro',
                'no fewer than three decimal places', 'rounded to the nearest cent']
        for rule, cue in zip(rules, cues):
            self.at(cue)
            self.play(FadeIn(rule[0]), AddTextLetterByLetter(rule[1], time_per_char=0.03))

        # [V6.7c] the code; a 100 DEM token travels up to the euro and down to francs
        out_via = output_line(Q5, 'via the euro')
        out_cross = output_line(Q5, 'cross rate')
        via = re.search(r'([\d.]+) FRF', out_via).group(1)                  # 335.38
        cross = re.search(r'([\d.]+) FRF', out_cross).group(1)              # 335.39
        dem_rate = Decimal(re.search(r'DEM = Decimal\("([\d.]+)"\)', snippet_source(Q5)).group(1))
        euro = (Decimal(100) / dem_rate).quantize(Decimal('0.001'), ROUND_HALF_UP)   # 51.129, computed here
        code = code_panel(snippet_lines(Q5, 9, 14), font_size=18).to_edge(DOWN, buff=0.3)
        self.at('The code follows those rules')
        self.play(FadeOut(rules), FadeOut(heading), tri.animate.move_to([-0.6, 1.45, 0]), run_time=0.9)
        self.play(FadeIn(code.background), run_time=0.3)
        self.play(type_code(code, run_time=1.4))
        self.add(code)

        nodes = tri.nodes
        token = money_chip('100 DEM').move_to(nodes[1])
        self.at('A hundred marks')
        self.play(FadeIn(token, scale=0.6), run_time=0.4)
        hl = line_highlight(code, 1)
        self.play(Create(hl), MoveAlongPath(token, Line(nodes[1].get_center(), nodes[0].get_center())), run_time=1.2)
        at_euro = money_chip(f'≈ {euro} EUR').move_to(nodes[0])
        self.play(Transform(token, at_euro), run_time=0.4)
        euro_note = Text(f'≈ {euro} EUR', font_size=24, color=MONEY).next_to(nodes[0], RIGHT, buff=0.3)
        self.add(euro_note)
        hl2 = line_highlight(code, 2)
        self.play(ReplacementTransform(hl, hl2), MoveAlongPath(token, Line(nodes[0].get_center(), nodes[2].get_center())),
                  run_time=1.2)
        legal = Text(f'{via} FRF', font_size=30, color=EXACT).next_to(nodes[2], RIGHT, buff=0.35).shift(UP * 0.25)
        self.play(ReplacementTransform(token, legal), run_time=0.6)

        # [V6.7d] the shortcut: a dashed red edge straight across; it arrives one centime off
        self.at('Now take the obvious shortcut')
        hl3 = SurroundingRectangle(VGroup(code.code_lines[4], code.code_lines[5]), color=ERROR, buff=0.06)
        hl3.stretch_to_fit_width(code.background.width - 0.2).set_x(code.background.get_x())
        self.play(tri.bottom.animate.set_stroke(opacity=1), tri.bottom_tag.animate.set_opacity(1),
                  ReplacementTransform(hl2, hl3), run_time=0.9)
        self.at('and multiply')
        token2 = money_chip('100 DEM').move_to(nodes[1])
        self.play(FadeIn(token2, scale=0.6), run_time=0.3)
        self.play(MoveAlongPath(token2, Line(nodes[1].get_center(), nodes[2].get_center())), run_time=1.0)
        shortcut = Text(f'{cross} FRF', font_size=30, color=ERROR).next_to(nodes[2], RIGHT, buff=0.35).shift(DOWN * 0.3)
        self.play(ReplacementTransform(token2, shortcut), run_time=0.6)

        # [V6.7e] the two results side by side, one centime apart
        self.at('One centime more')
        pair = VGroup(Text(f'{via} FRF', font_size=40, color=EXACT), Text(f'{cross} FRF', font_size=40, color=ERROR))
        pair.arrange(RIGHT, buff=1.4).move_to([0, -0.2, 0])
        captions = VGroup(Text('through the euro', font_size=22, color=GREY_A).next_to(pair[0], UP, buff=0.2),
                          Text('cross rate', font_size=22, color=GREY_A).next_to(pair[1], UP, buff=0.2))
        apart = Text('one centime apart', font_size=26, color=ERROR).next_to(pair, DOWN, buff=0.35)
        self.play(FadeOut(code), FadeOut(hl3), FadeOut(euro_note),
                  FadeOut(VGroup(tri.left_tag, tri.right_tag, tri.bottom_tag)))
        tri.remove(tri.left_tag, tri.right_tag, tri.bottom_tag)
        self.play(tri.animate.scale(0.62).move_to([0, 2.35, 0]), ReplacementTransform(legal, pair[0]),
                  ReplacementTransform(shortcut, pair[1]), run_time=1.0)
        self.play(FadeIn(captions), FadeIn(apart, shift=UP * 0.15), run_time=0.6)

        # Without one rule, every bank gets its own answer; with it, everyone gets the same one
        self.at('every bank would get')
        answers = (via, cross, via)                                         # both printed by q06-05
        banks = VGroup()
        for k, answer in enumerate(answers):
            name = label_box(f'Bank {"ABC"[k]}', font_size=24)
            value = Text(f'{answer} FRF', font_size=26, color=EXACT if answer == via else ERROR)
            banks.add(VGroup(name, value.next_to(name, DOWN, buff=0.2)))
        banks.arrange(RIGHT, buff=1.3).move_to([0, -2.6, 0])
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in banks], lag_ratio=0.25), run_time=1.0)
        self.at('would be a dispute')
        bolts = VGroup(*[DashedLine(banks[k][1].get_right() + RIGHT * 0.1, banks[k + 1][1].get_left() + LEFT * 0.1,
                                    color=ERROR, stroke_width=4) for k in range(2)])
        self.play(Create(bolts), run_time=0.6)
        self.at('make sure everyone got the same one')
        same = [Text(f'{via} FRF', font_size=26, color=EXACT).move_to(b[1]) for b in banks]
        self.play(FadeOut(bolts), *[Transform(b[1], s) for b, s in zip(banks, same)], run_time=0.8)
        ticks = VGroup(*[checkmark(size=0.35).next_to(b[1], RIGHT, buff=0.15) for b in banks])
        self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.2), run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 6.8

def recap_icon(kind):
    """Small moving pictures for the recap column; each returns (icon, animation)."""
    if kind == 'modes':
        axis = Line(LEFT * 0.55, RIGHT * 0.55, color=SCAFFOLD, stroke_width=3)
        ends = VGroup(*[Line(DOWN * 0.15, UP * 0.15, color=SCAFFOLD, stroke_width=3).move_to(x * RIGHT) for x in (-0.5, 0.5)])
        dot = gem(size=0.16).move_to(UP * 0.22 + RIGHT * 0.08)
        arrows = VGroup(*[Arrow(dot.get_center(), [x * 0.85, 0.22, 0], buff=0.1, color=c, stroke_width=3,
                                max_tip_length_to_length_ratio=0.35) for x, c in ((-0.5, STORED), (0.5, EXACT))])
        return VGroup(axis, ends, dot, arrows), LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.4)
    if kind == 'drift':
        m = Meter('', radius=0.45)
        m.remove(m.name, m.readout)
        m.readout.clear_updaters()
        return m, m.value.animate.set_value(0.08)
    if kind == 'layers':
        axis = Line(LEFT * 0.55, RIGHT * 0.55, color=SCAFFOLD, stroke_width=3)
        ticks = VGroup(*[Line(DOWN * 0.12, UP * 0.12, color=STORED, stroke_width=3).move_to(x * RIGHT) for x in (-0.36, 0.24)])
        dot = gem(size=0.16).move_to(UP * 0.3)
        arrow = Arrow(dot.get_center(), [-0.36, 0.1, 0], buff=0.05, color=FOCUS, stroke_width=3,
                      max_tip_length_to_length_ratio=0.35)
        return VGroup(axis, ticks, dot, arrow), GrowArrow(arrow)
    if kind == 'where':
        papers = VGroup(*[Rectangle(width=0.36, height=0.62).set_fill(PAPER, 1).set_stroke(width=0) for _ in range(2)])
        papers.arrange(RIGHT, buff=0.35)
        sign = Text('≠', font_size=28, color=ERROR).move_to(papers)
        return VGroup(papers, sign), Indicate(sign, color=ERROR, scale_factor=1.4)
    tri = euro_triangle(scale=0.22)
    tri.remove(tri.left_tag, tri.right_tag, tri.bottom_tag, tri.bottom)
    for node in tri.nodes:
        node[1].set_opacity(0)
    return tri, Indicate(tri.nodes[0], color=FOCUS, scale_factor=1.3)


class Segment_6_8(Segment):
    """Recap and challenge: the euro triangle (q06-05), the QR wall, and episode 7."""
    EPISODE, SEGMENT = 6, '6.8'

    def construct(self):
        # [V6.8a] the recap column builds, each line with a small moving picture
        items = [('modes', 'Rounding has a mode: up, down, ceiling, floor, half-up, half-down, half-even, 05up',
                  "decimal module names eight"),
                 ('drift', "Half-up drifts; half-even doesn't", 'over many ties it drifts'),
                 ('layers', "Floats round first, so ties aren't ties", 'Floats add a second, hidden layer'),
                 ('where', 'Where you round matters: per line ≠ per invoice', 'And where you round'),
                 ('law', 'Write the rule down; sometimes it’s law', 'Sometimes your team writes it')]
        heading = Text("Let's take stock", font_size=36, color=FOCUS).move_to(UP * 3.45)
        self.play(FadeIn(heading, shift=DOWN * 0.2))
        rows = VGroup()
        for k, (kind, text, cue) in enumerate(items):
            icon, motion = recap_icon(kind)
            icon.scale_to_fit_height(min(icon.height, 0.8)).move_to([-6.0, 2.45 - 1.3 * k, 0])
            words = wrapped_text(text, 11.2, font_size=28)
            words.next_to(icon, RIGHT, buff=0.55).set_x(-5.15 + words.width / 2)
            self.at(cue)
            self.play(FadeIn(icon, scale=0.7), FadeIn(words, shift=RIGHT * 0.2), run_time=0.6)
            self.play(motion, run_time=0.8)
            rows.add(VGroup(icon, words))
        self.at("sometimes it's the law")
        self.play(Indicate(rows[-1][1], color=FOCUS, scale_factor=1.04), run_time=0.8)

        # [V6.8b] the euro triangle returns with q06-05's code; how many amounts differ? "?"
        self.at("Here's a challenge")
        tri = euro_triangle(scale=0.85).move_to([-3.6, 1.6, 0])
        code = code_panel(snippet_lines(Q5, 16, 18), font_size=18).to_corner(DL, buff=0.35)
        self.play(FadeOut(rows), FadeOut(heading), run_time=0.5)
        card = show_card(self, 'q06-05')
        self.play(FadeIn(tri), FadeIn(code.background), run_time=0.6)
        self.play(type_code(code, run_time=1.2))
        self.add(code)
        counter_title = Text('amounts that differ, 1 to 1000 DEM', font_size=26).move_to([3.3, 3.0, 0])
        unknown = Text('?', font_size=96, color=FOCUS).next_to(counter_title, DOWN, buff=0.35)
        self.play(FadeIn(counter_title), FadeIn(unknown, scale=0.6), run_time=0.7)
        self.at('loop over every whole amount')
        amount = number(1, font_size=30, color=BLACK)
        unit = Text('DEM', font_size=26, color=BLACK, weight=BOLD)
        chip = RoundedRectangle(width=2.6, height=0.6, corner_radius=0.12).set_fill(MONEY, 1).set_stroke(width=0)
        chip.move_to([3.7, 0.5, 0])
        reading = Text('every amount:', font_size=24, color=GREY_A).next_to(chip, LEFT, buff=0.3)

        def centre(m):
            pair = VGroup(amount, unit)
            unit.next_to(amount, RIGHT, buff=0.15)
            pair.move_to(chip)

        unit.add_updater(centre)
        self.play(FadeIn(reading), FadeIn(chip), FadeIn(amount), FadeIn(unit), run_time=0.4)
        self.play(ChangeDecimalToValue(amount, 1000), run_time=3.0, rate_func=linear)
        self.at('count how often')
        self.play(Indicate(unknown, color=FOCUS, scale_factor=1.25), run_time=0.8)

        # [V6.8c] the QR wall, 10 seconds
        hide_card(self, card, 10.0, FadeOut(VGroup(tri, code, counter_title, unknown, chip, amount, unit, reading)))
        wall = qr_wall(episode_qr_ids(6))
        self.play(FadeIn(wall), run_time=0.6)
        self.wait(10)
        self.play(FadeOut(wall), run_time=0.6)

        # [V6.8d] teaser: a penny sliced into slivers; one slides off into a jar marked "?"
        whole = penny(0.9).move_to([-2.2, 1.0, 0])
        slices = sliced_penny(12, 0.9).move_to(whole)
        apart = sliced_penny(12, 0.9, gap=0.12).move_to(whole)
        pot = jar(1.5, 1.8).move_to([2.4, 0.7, 0])
        mark = Text('?', font_size=48, color=FOCUS).move_to(pot[0])
        teaser = end_card('Episode 7', 'Fractions of a penny')
        sub = Text('what Office Space got right and wrong', font_size=26, color=SCAFFOLD)
        sub.next_to(teaser, DOWN, buff=0.25)
        VGroup(teaser, sub).move_to(DOWN * 2.4)
        self.play(FadeIn(whole, scale=0.6), FadeIn(pot), FadeIn(mark), run_time=0.7)
        self.remove(whole)
        self.add(slices)
        self.play(Transform(slices, apart), run_time=0.8)
        sliver = slices[2]
        self.play(sliver.animate.move_to(pot[0].get_top() + UP * 0.4).scale(0.6), run_time=1.0)
        self.play(sliver.animate.move_to(pot[0].get_bottom() + UP * 0.35).set_opacity(0.85), run_time=0.6,
                  rate_func=rate_functions.ease_in_quad)
        self.at('What Office Space got right')
        self.play(FadeIn(teaser, shift=UP * 0.2), FadeIn(sub, shift=UP * 0.2))
        self.finish()

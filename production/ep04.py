"""Episode 4 · What goes wrong. One Scene per script segment.

    python3 production/render.py 4 [-ql] [segment ...]

Shot ids in comments ([V4.1a] ...) refer to episodes/04-what-goes-wrong.md. Code and console
text come from snippets/ep04/ (q04-01 ... q04-05). Values the script shows but no snippet
prints are computed below with Python, and each place says so.
"""
import random
import sys
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa: E402,F403

Q1 = 'ep04/01-paid-off-or-not.py'
Q2 = 'ep04/02-loop-skips-zero.py'
Q3 = 'ep04/03-two-systems.py'
Q4 = 'ep04/04-one-way-street.py'
Q5 = 'ep04/05-challenge-reconcile.py'
Q0 = 'ep00/01-four-surprises.py'


# ---------------------------------------------------------------- local helpers

def show_qr(scene, qr_id):
    """Bring a QR card in (bottom right) and note when, so hide_qr can hold it 8 seconds."""
    card = qr_card(qr_id)
    scene.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)
    scene.qr_since = scene.renderer.time
    return card


def hide_qr(scene, card, hold=8.4):
    remaining = scene.qr_since + hold - scene.renderer.time
    if remaining > 1 / 30:
        scene.wait(remaining)
    scene.play(FadeOut(card), run_time=0.5)


def clear(scene, run_time=0.6, keep=()):
    mobs = [m for m in scene.mobjects if m not in keep and m not in scene.foreground_mobjects]
    if mobs:
        scene.play(FadeOut(Group(*mobs)), run_time=run_time)


def strip_comments(source):
    """Snippet lines with their trailing comments cut (the series bible allows dropping comments)."""
    return '\n'.join(line.split('  #')[0].rstrip() for line in source.splitlines())


def after_colon(line):
    """The value part of a labelled output line ('in time order:   263006.59...' -> '263006.59...')."""
    return line.split(':', 1)[1].strip()


def person(color=GREY_B, height=1.3):
    head = Circle(0.2).set_fill(color, 1).set_stroke(width=0)
    body = RoundedRectangle(width=0.64, height=0.62, corner_radius=0.26).set_fill(color, 1).set_stroke(width=0)
    body.next_to(head, DOWN, buff=0.06)
    return VGroup(head, body).scale_to_fit_height(height)


def bubble(text, color=WHITE, font_size=30):
    label = Text(text, font_size=font_size, color=color)
    box = RoundedRectangle(width=max(label.width + 0.4, 0.7), height=label.height + 0.35, corner_radius=0.18)
    box.set_fill(GREY_E, 1).set_stroke(GREY_B, 2)
    label.move_to(box)
    return VGroup(box, label)


def stamp(text, color, font_size=34):
    label = Text(text, font_size=font_size, weight=BOLD, color=color)
    box = RoundedRectangle(width=label.width + 0.5, height=label.height + 0.4, corner_radius=0.1)
    box.set_stroke(color, 6).set_fill(BLACK, 0.6)
    label.move_to(box)
    return VGroup(box, label)


def envelope(lines, width=3.2, height=1.5):
    body = Rectangle(width=width, height=height).set_fill(PAPER, 1).set_stroke(GREY_B, 2)
    flap = VMobject().set_points_as_corners([body.get_corner(UL), body.get_center() + UP * height * 0.2,
                                             body.get_corner(UR)]).set_stroke(GREY, 2)
    text = VGroup(*[Text(l, font_size=20, color=INK) for l in lines]).arrange(DOWN, buff=0.08)
    text.move_to(body).shift(DOWN * height * 0.2)
    return VGroup(body, flap, text)


def account_card(n, balance, haloed):
    box = RoundedRectangle(width=1.6, height=1.3, corner_radius=0.12).set_fill(GREY_E, 1).set_stroke(GREY_B, 2)
    title = Text(f'Account {n}', font_size=18, color=SCAFFOLD).move_to(box.get_top() + DOWN * 0.3)
    amount = code_text(balance, font_size=26, color=WHITE if haloed else EXACT)
    amount.move_to(box).shift(DOWN * 0.15)
    card = VGroup(box, title, amount)
    card.halo = None
    if haloed:
        card.halo = box.copy().set_fill(opacity=0).set_stroke(ERROR, 14, opacity=0.35)
        card.add_to_back(card.halo)
    card.box, card.amount = box, amount
    return card


def funnel(width=2.6, height=1.5, neck=0.5, color=GREY_B):
    top = height / 2
    left = VMobject().set_points_as_corners([[-width / 2, top, 0], [-neck / 2, -top + 0.3, 0], [-neck / 2, -top, 0]])
    right = VMobject().set_points_as_corners([[width / 2, top, 0], [neck / 2, -top + 0.3, 0], [neck / 2, -top, 0]])
    return VGroup(left, right).set_stroke(color, 4)


class Bin(VGroup):
    """An open-topped bin whose fill rises: `bin.fill_to(height)` is an animation."""

    def __init__(self, width=1.4, height=2.0, color=ERROR, **kwargs):
        super().__init__(**kwargs)
        self.walls = VMobject().set_points_as_corners([[-width / 2, height / 2, 0], [-width / 2, -height / 2, 0],
                                                       [width / 2, -height / 2, 0], [width / 2, height / 2, 0]])
        self.walls.set_stroke(GREY_B, 3)
        self.base_y = -height / 2
        self.inner = width - 0.12
        self.level = Rectangle(width=self.inner, height=0.001).set_fill(color, 0.8).set_stroke(width=0)
        self.level.move_to([0, self.base_y + 0.0005, 0])
        self.add(self.walls, self.level)

    def fill_to(self, height, **kwargs):
        bottom = self.walls.get_bottom()
        target = Rectangle(width=self.inner, height=max(height, 0.001)).set_fill(self.level.get_fill_color(), 0.8)
        target.set_stroke(width=0).move_to(bottom + UP * max(height, 0.001) / 2)
        return Transform(self.level, target, **kwargs)


def magnifier(radius=0.45):
    lens = Circle(radius).set_stroke(WHITE, 4)
    handle = Line(lens.point_at_angle(-3 * PI / 4), lens.point_at_angle(-3 * PI / 4) + (DL * 0.5), stroke_width=8, color=WHITE)
    return VGroup(lens, handle)


def ticket(text, width=5.4):
    label = code_text(text, font_size=18, color=WHITE)
    box = RoundedRectangle(width=width, height=0.5, corner_radius=0.08).set_fill(GREY_E, 1).set_stroke(ERROR, 2)
    label.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.2)
    return VGroup(box, label)


def colour_value(line, prefix_len, good=EXACT, bad=ERROR):
    """Colour the first prefix_len characters of a MonoLine green and the rest red."""
    line.chars(0, prefix_len).set_color(good)
    line.chars(prefix_len).set_color(bad)
    return line


def common_prefix(strings):
    n = 0
    while all(len(s) > n for s in strings) and len({s[n] for s in strings}) == 1:
        n += 1
    return n


def float_total(values):
    """A plain running total, like q04-05's total()."""
    t = 0.0
    for v in values:
        t += v
    return t


def q05_amounts():
    """The 1,000 transactions of q04-05, generated here exactly as the snippet does."""
    rng = random.Random(1)
    return [rng.randrange(-50_000, 100_000) / 100 for _ in range(1000)]


# ---------------------------------------------------------------- 4.1

class Segment_4_1(Segment):
    """Cold open: a loan that prints $-0.00 but isn't zero (q04-01)."""
    EPISODE, SEGMENT = 4, '4.1'

    def construct(self):
        # The loan and its payments, read from q04-01's own source.
        loan = float(snippet_find(Q1, 'balance = 1000').split('=')[1])
        payments = eval(snippet_find(Q1, 'payments = ').split('=', 1)[1])   # [83.33] * 11 + [83.37]
        paid = sum(Decimal(f'{p:.2f}') for p in payments)                     # exactly 1000.00 on paper
        rows = [('Loan amount', f'{loan:,.2f}'), ('-', '')]
        rows += [(f'Payment {m:2}', f'{p:.2f}') for m, p in enumerate(payments, 1)]
        rows += [('-', ''), ('Total paid', f'{paid:,.2f}')]

        # [V4.1a] the receipt as a loan statement; twelve payment lines scroll past
        # The statement is taller than the frame, so its lines scroll up a fixed strip of paper,
        # fading as they leave the top.
        bill = receipt(rows, width=5.0, font_size=22, title='LOAN STATEMENT')
        lines = bill.lines
        window = Rectangle(width=5.0, height=7.6).set_fill(PAPER, 1).set_stroke(width=0).move_to(UP * 0.05)
        VGroup(*lines).shift(UP * (window.get_top()[1] - 0.3 - lines[0].get_top()[1]))
        shown = [lines[0], lines[1], lines[2]]
        self.play(FadeIn(window, shift=DOWN * 0.3), FadeIn(lines[0]), run_time=0.8)
        self.play(FadeIn(lines[1], shift=UP * 0.1), FadeIn(lines[2]), run_time=0.6)
        self.at('Eleven payments of')
        for k, line in enumerate(lines[3:], start=3):
            over = -3.45 - line.get_bottom()[1]
            if over > 0:
                for h in lines[k:]:
                    h.shift(UP * over)
                leaving = [m for m in shown if m.get_top()[1] + over > 3.7]
                self.play(*[m.animate.shift(UP * over).set_opacity(0) if m in leaving else m.animate.shift(UP * over)
                            for m in shown], run_time=0.12)
                self.remove(*leaving)
                shown = [m for m in shown if m not in leaving]
            if k == 14:
                self.at('a final payment')
            if k == 16:
                self.at('Add them up on paper')
            self.play(FadeIn(line, shift=UP * 0.1), run_time=0.18 if k < 14 else 0.45)
            shown.append(line)
            if k == 14:
                self.play(line.chars(len(line.source) - 5).animate.set_color(FOCUS), run_time=0.4)
        total = lines[-1]
        self.play(total.chars(len(total.source) - 8).animate.set_color(EXACT).scale(1.15), run_time=0.6)

        # [V4.1b] code panel left; the console prints the last three months
        self.at('Run it')
        out_balance = output_line(Q1, 'statement says').split()[-1]       # $-0.00
        statement = receipt([('Loan amount', f'{loan:,.2f}'), ('Total paid', f'{paid:,.2f}'), ('-', ''),
                             ('Balance', out_balance)], width=4.4, font_size=22, title='LOAN STATEMENT')
        statement.move_to([4.55, 3.7 - statement.height / 2, 0])
        balance_glyphs = statement.lines[-1].part(out_balance)
        balance_glyphs.set_opacity(0)
        code = code_panel(snippet_lines(Q1, 4, 7), font_size=20).to_corner(UL, buff=0.35)
        out = output_console(Q1, font_size=20)
        out.next_to(code, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeOut(Group(window, *shown)), FadeIn(statement, shift=LEFT * 0.3), FadeIn(code), run_time=0.8)
        card = show_qr(self, 'q04-01')
        self.play(FadeIn(out.background), run_time=0.3)
        for i in range(3):
            self.play(out.type_line(i, run_time=0.7))
        self.at('minus zero dollars')
        minus = out.lines[2].part('-')
        self.play(minus.animate.set_color(ERROR).scale(1.8), balance_glyphs.animate.set_opacity(1), run_time=0.5)
        self.play(minus.animate.scale(1 / 1.8), statement.lines[-1].part('-').animate.set_color(ERROR), run_time=0.4)
        self.at('Minus zero.')
        glow = minus.copy().set_stroke(ERROR, 8, opacity=0.5)
        self.play(FadeIn(glow), run_time=0.3)
        self.play(FadeOut(glow), run_time=0.5)
        self.at('Now ask the question')
        self.play(out.type_line(3, run_time=0.7))
        hide_qr(self, card)

        # [V4.1c] PAID IN FULL swings down and stops in mid-air, held by a red label
        self.play(statement.animate.move_to([4.55, 0.3 - statement.height / 2, 0]), run_time=0.7)
        held = code_text(output_line(Q1, 'balance == 0'), font_size=20, color=ERROR).move_to([4.55, 0.75, 0])
        paid_stamp = stamp('PAID IN FULL', EXACT).rotate(-0.6).move_to([4.6, 5.4, 0])
        self.at('is the balance zero')
        self.play(paid_stamp.animate.rotate(0.45).move_to([4.55, 1.95, 0]), run_time=1.3,
                  rate_func=rate_functions.ease_out_back)
        self.at('False.')
        self.play(out.type_line(4, run_time=0.4))
        self.play(out.lines[4].part('False').animate.set_color(ERROR), TransformFromCopy(out.lines[4], held),
                  run_time=0.5)
        self.play(paid_stamp.animate.shift(DOWN * 0.12), run_time=0.1)
        self.play(paid_stamp.animate.shift(UP * 0.12), run_time=0.2, rate_func=rate_functions.ease_out_bounce)

        # [V4.1d] the stored value; the float line zooms in on zero
        self.at("What's left is about")
        self.play(out.type_line(5, run_time=1.0))
        stored_text = after_colon(output_line(Q1, 'what is stored'))
        stored = float(stored_text)
        self.play(out.lines[5].part(stored_text).animate.set_color(MONEY), run_time=0.4)
        wide = FloatLine(-1, 1, width=8, ticks=[-1, -0.5, 0, 0.5, 1], labels={-1: '-1.00', 0: '0', 1: '1.00'})
        wide.move_to([-2.6, -2.75, 0])
        self.play(FadeIn(wide), run_time=0.6)
        zoom_box = Square(0.5).set_stroke(FOCUS, 3).move_to(wide.point(0))
        self.play(Create(zoom_box), run_time=0.4)
        near = FloatLine(Fraction(-2, 10 ** 13), Fraction(1, 10 ** 13), width=8, ticks=[stored, 0.0],
                         labels={0: '0'})
        near.move_to(wide.axis.get_center() + UP * (near.get_center()[1] - near.axis.get_center()[1]))
        value_label = code_text(stored_text, font_size=18, color=MONEY)
        value_label.next_to(near.point(stored), DOWN, buff=0.35)
        self.play(zoom_box.animate.scale(16).set_stroke(opacity=0), FadeOut(wide, scale=4), FadeIn(near, scale=0.3),
                  run_time=1.0)
        self.remove(zoom_box)
        dot = Dot(near.point(stored), radius=0.11, color=MONEY)
        tiny = Text('about one ten-trillionth of a dollar, below zero', font_size=20, color=SCAFFOLD)
        tiny.move_to([-2.6, -1.75, 0])
        self.play(FadeIn(dot, scale=2), FadeIn(value_label), FadeIn(tiny, shift=UP * 0.1), run_time=0.7)
        self.at('Nobody owes it')
        self.play(Flash(dot, color=MONEY, line_length=0.15, flash_radius=0.25), run_time=0.7)
        self.at('none of those payments')
        box = line_highlight(code, 1)
        self.play(Create(box), run_time=0.5)
        self.at('But it\'s enough to keep')
        for _ in range(2):
            self.play(paid_stamp.animate.shift(DOWN * 0.15), run_time=0.25)
            self.play(paid_stamp.animate.shift(UP * 0.15), run_time=0.35, rate_func=rate_functions.ease_out_bounce)

        # Downstream: the errors from episode 3 float down a stream into what they break
        self.at('In the last episode')
        clear(self)
        head = title_card('What goes wrong', 'Episode 4').to_edge(UP, buff=0.8)
        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.8)
        stream = FunctionGraph(lambda x: -1.6 + 0.35 * np.sin(1.1 * x), x_range=[-6.6, 3.2], color=STORED,
                               stroke_width=5).set_stroke(opacity=0.6)
        self.play(Create(stream), run_time=0.8)
        targets = VGroup(label_box('balances', font_size=22), label_box('loops', font_size=22),
                         label_box('reports', font_size=22)).arrange(DOWN, buff=0.25).move_to([5.2, -1.6, 0])
        self.play(FadeIn(targets, shift=LEFT * 0.2), run_time=0.5)
        self.at('we follow them downstream')
        drops = VGroup(*[Dot(radius=0.09, color=ERROR) for _ in range(5)])
        moves = []
        for k, d in enumerate(drops):
            d.move_to(stream.get_start())
            moves.append(MoveAlongPath(d, stream, run_time=2.4, rate_func=rate_functions.linear))
        self.play(LaggedStart(*moves, lag_ratio=0.18), run_time=3.0)
        self.play(*[t[0].animate.set_stroke(ERROR, 3) for t in targets],
                  *[d.animate.move_to(targets[k % 3].get_left()).set_opacity(0) for k, d in enumerate(drops)],
                  run_time=0.8)
        self.finish()


# ---------------------------------------------------------------- 4.2

class Segment_4_2(Segment):
    """Ghost balances."""
    EPISODE, SEGMENT = 4, '4.2'

    def construct(self):
        statement = output_line(Q1, 'statement says').split()[-1]       # $-0.00, from q04-01
        zero = statement.replace('-', '')                               # $0.00
        haloed = {1: statement, 3: zero, 5: statement}
        # [V4.2a] a row of account cards; three carry a faint red halo
        cards = VGroup(*[account_card(i + 1, haloed.get(i, zero), i in haloed) for i in range(7)])
        cards.arrange(RIGHT, buff=0.25).move_to(UP * 1.9)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.12), run_time=1.6)
        ghost = Text('ghost balance', font_size=28, color=ERROR).next_to(cards[1], DOWN, buff=0.35)
        self.play(FadeIn(ghost, shift=UP * 0.1), Indicate(cards[1].amount, color=ERROR), run_time=0.8)
        self.at('Is the account empty')
        questions = VGroup(*[Text(q, font_size=24, color=SCAFFOLD) for q in
                             ('empty?', 'close it?', 'behind on payments?', 'send a statement?')])
        questions.arrange(RIGHT, buff=0.6).move_to(DOWN * 1.6)
        self.play(FadeOut(ghost), FadeIn(questions[0], shift=UP * 0.1), run_time=0.4)

        # [V4.2b] "close account" runs down the row
        self.at('Can we close it')
        self.play(FadeIn(questions[1], shift=UP * 0.1), run_time=0.3)
        closer = label_box('close account', color=FOCUS, font_size=22).move_to([cards[0].get_x() - 1.2, 3.35, 0])
        self.play(FadeIn(closer), run_time=0.3)
        refusals = VGroup()
        for i, c in enumerate(cards):
            if i == 2:
                self.at('Is the customer behind')
                self.play(FadeIn(questions[2], shift=UP * 0.1), run_time=0.3)
            if i == 4:
                self.at('Should we send a statement')
                self.play(FadeIn(questions[3], shift=UP * 0.1), run_time=0.3)
            self.play(closer.animate.set_x(c.get_x()), run_time=0.22)
            self.play(closer.animate.shift(DOWN * 0.2), run_time=0.1)
            if i in haloed:
                no = Text('balance ≠ 0', font_size=18, color=ERROR).next_to(c, DOWN, buff=0.15)
                refusals.add(no)
                self.play(closer.animate.shift(UP * 0.35), Wiggle(c, scale_value=1.05), FadeIn(no), run_time=0.45)
                self.play(closer.animate.shift(DOWN * 0.15), run_time=0.12)
            else:
                tick = checkmark(size=0.35).move_to(c.box.get_corner(DR) + UL * 0.25)
                self.play(closer.animate.shift(UP * 0.2), c.animate.set_opacity(0.35).scale(0.96),
                          Create(tick), run_time=0.3)
                c.add(tick)
        self.at('Each of those is a comparison')
        self.play(FadeOut(closer), *[cards[i].halo.animate.set_stroke(opacity=0.7) for i in haloed], run_time=0.6)
        self.play(*[cards[i].halo.animate.set_stroke(opacity=0.35) for i in haloed], run_time=0.6)
        self.at('accounts that refuse to close')
        self.play(*[Wiggle(cards[i], scale_value=1.04) for i in haloed], run_time=0.8)

        # [V4.2c] the haloed accounts get statements
        self.at('Statements that ask for')
        letters = VGroup()
        for i in haloed:
            due = cards[i].amount.source
            env = envelope(['Your statement:', f'amount due {due}']).move_to([cards[i].get_x(), -0.45, 0])
            letters.add(env)
        self.play(FadeOut(questions), FadeOut(refusals), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(e, shift=DOWN * 0.4) for e in letters], lag_ratio=0.3), run_time=1.4)

        # [V4.2d] zoom into one haloed card: its stored balance, a gold speck near zero
        self.at('And the strangest one')
        focus = cards[1]
        others = [m for m in self.mobjects if m is not focus]
        self.play(FadeOut(Group(*others)), focus.animate.scale(2.2).move_to(UP * 1.6), run_time=0.8)
        # A schematic float line near zero: evenly spaced ticks, not real doubles (those are far
        # denser); the speck sits a few ticks left of zero.
        line = FloatLine(-8, 4, width=11, ticks=list(range(-8, 5)), labels={0: '0'}).move_to(UP * 1.6)
        speck = Dot(line.point(-3), radius=0.08, color=MONEY)
        speck_label = Text('stored balance', font_size=20, color=MONEY).next_to(speck, UP, buff=0.35)
        note = Text('zoomed in near zero · not to scale', font_size=18, color=SCAFFOLD).next_to(line, DOWN, buff=0.25)
        self.play(focus.animate.scale(6).set_opacity(0), FadeIn(line, scale=0.5), run_time=0.9)
        self.remove(focus)
        self.play(FadeIn(speck, scale=3), FadeIn(speck_label), FadeIn(note), run_time=0.6)

        # A tiny negative number rounded to two places for display: the sign survives.
        stored_text = after_colon(output_line(Q1, 'what is stored'))
        shown_text = f'{float(stored_text):.2f}'                       # '-0.00', computed here
        raw = code_text(stored_text, font_size=30, color=MONEY).move_to([-3.2, -1.4, 0])
        rounded = code_text(shown_text, font_size=40, color=WHITE).move_to([4.2, -1.4, 0])
        arrow = Arrow(raw.get_right() + RIGHT * 0.15, rounded.get_left() + LEFT * 0.2, buff=0, color=SCAFFOLD)
        how = Text('rounded to two places', font_size=22, color=SCAFFOLD).next_to(arrow, UP, buff=0.15)
        self.at('a tiny negative number')
        self.play(TransformFromCopy(speck, raw), run_time=0.8)
        self.play(GrowArrow(arrow), FadeIn(how), run_time=0.6)
        self.play(TransformFromCopy(raw, rounded), run_time=0.8)
        self.at('The rounding throws away')
        digits = raw.chars(1)
        self.play(digits.animate.set_color(GREY_D).shift(DOWN * 0.15), run_time=0.8)
        self.at('but the sign survives')
        signs = VGroup(raw.chars(0, 1), rounded.chars(0, 1))
        self.play(*[g.animate.set_color(ERROR).scale(1.6) for g in signs], run_time=0.5)
        self.play(*[g.animate.scale(1 / 1.6) for g in signs], run_time=0.4)

        # None of it loses money, but each case lands in front of a person
        self.at('None of this loses')
        clear(self)
        lost = VGroup(Text('money lost:', font_size=30, color=SCAFFOLD),
                      code_text(zero, font_size=34, color=EXACT)).arrange(RIGHT, buff=0.3).move_to(UP * 2.8)
        self.play(FadeIn(lost, shift=UP * 0.1), run_time=0.6)
        self.at('ends up in front of a person')
        clerk = person(GREY_B, 1.6).move_to([2.6, -0.6, 0])
        desk = Line([1.4, -1.5, 0], [3.8, -1.5, 0], color=GREY_B, stroke_width=6)
        self.play(FadeIn(clerk), Create(desk), run_time=0.6)
        queue = VGroup(*[account_card(n, statement if n % 2 else zero, True).scale(0.7) for n in (2, 4, 6)],
                       *[envelope(['Your statement:', f'amount due {statement}']).scale(0.45) for _ in range(2)])
        queue.arrange(RIGHT, buff=0.15).move_to([-3.4, -0.6, 0])
        spots = [item.get_center() for item in queue]
        for item in queue:
            item.move_to([-8.5, -0.6, 0])
        self.play(LaggedStart(*[q.animate.move_to(s) for q, s in zip(queue, spots)], lag_ratio=0.2), run_time=2.0)
        self.at('explain it to a customer')
        customer = person(STORED, 1.6).move_to([5.4, -0.6, 0])
        ask = bubble('?', ERROR, 36).next_to(customer, UP, buff=0.2)
        reply = bubble('…', WHITE, 30).next_to(clerk, UP, buff=0.2)
        self.play(FadeIn(customer, shift=LEFT * 0.3), run_time=0.5)
        self.play(FadeIn(ask, scale=0.6), FadeIn(reply, scale=0.6), run_time=0.5)
        self.at("can't count")
        self.play(Wiggle(ask), run_time=0.8)
        self.finish()


# ---------------------------------------------------------------- 4.3

class ScrollConsole:
    """A console window of `rows` lines that scrolls as lines are typed beyond it."""

    def __init__(self, lines, rows, font_size=18):
        full = Console(lines, font_size=font_size)
        self.lines, self.rows = full.lines, rows
        self.pitch = MonoLine('M', font_size=font_size).line_height * 1.45
        inner_h = self.pitch * (rows - 1) + MonoLine('M', font_size=font_size).line_height
        self.background = RoundedRectangle(width=full.background.width, height=inner_h + 0.5, corner_radius=0.12)
        self.background.set_fill(PANEL, 1).set_stroke(GREY_D, 1)
        self.background.align_to(full.background, UP).align_to(full.background, LEFT)
        self.group = VGroup(self.background, *self.lines)

    def type(self, scene, i, run_time=0.6):
        if i >= self.rows:
            visible = self.lines[i - self.rows + 1:i]
            scene.play(FadeOut(self.lines[i - self.rows]), *[l.animate.shift(UP * self.pitch) for l in visible],
                       run_time=0.12)
            self.lines[i].shift(UP * self.pitch * (i - self.rows + 1))
        glyphs = self.lines[i].glyphs
        scene.play(LaggedStart(*[FadeIn(g, run_time=0.05) for g in glyphs], lag_ratio=1.0, run_time=run_time))


class Segment_4_3(Segment):
    """The loop that skips zero (q04-02)."""
    EPISODE, SEGMENT = 4, '4.3'

    def construct(self):
        steps = snippet_output(Q2)
        values = [line.split('= ')[1] for line in steps]

        # [V4.3a] code panel, and a vertical number line from 1 down to -0.3 with a gold marker
        code = code_panel(snippet_lines(Q2, 7, 9), font_size=20).to_corner(UL, buff=0.35)
        console = ScrollConsole(steps, rows=6, font_size=18)
        console.group.next_to(code, DOWN, buff=0.3, aligned_edge=LEFT)
        top_y, bottom_y, axis_x = 2.0, -3.6, 0.9

        def y_of(v):
            return bottom_y + (float(v) + 0.3) / 1.3 * (top_y - bottom_y)

        axis = Line([axis_x, top_y + 0.15, 0], [axis_x, bottom_y - 0.15, 0], color=SCAFFOLD, stroke_width=2)
        tenths = [Fraction(10 - k, 10) for k in range(14)]           # 1.0, 0.9, ..., -0.3
        ticks = VGroup(*[Line(LEFT * 0.12, RIGHT * 0.12, color=SCAFFOLD, stroke_width=3).move_to([axis_x, y_of(t), 0])
                         for t in tenths])
        labels = VGroup(*[Text(f'{float(t):.1f}' if t else '0', font=MONO, font_size=18, color=SCAFFOLD)
                          for t in tenths])
        for label, t in zip(labels, tenths):
            label.next_to([axis_x - 0.15, y_of(t), 0], LEFT, buff=0.08)
        number_line = VGroup(axis, ticks, labels)
        marker = Triangle(color=MONEY).set_fill(MONEY, 1).scale(0.13).rotate(PI / 2)
        marker.move_to([axis_x + 0.22, y_of(1), 0])
        self.play(FadeIn(code), run_time=0.6)
        self.at('keep paying ten cents')
        self.play(FadeIn(number_line), FadeIn(marker, shift=LEFT * 0.2), run_time=0.8)
        self.at('We start at one dollar')
        self.play(Indicate(marker, color=MONEY), run_time=0.6)
        self.at('Ten payments of a dime')
        target = Text('target: 0', font_size=20, color=EXACT).next_to(ticks[10], RIGHT, buff=0.3)
        self.play(FadeIn(target, shift=LEFT * 0.1), Indicate(labels[10], color=EXACT), run_time=0.8)
        self.play(FadeIn(console.background), run_time=0.4)

        # [V4.3b] each step: the marker drops a dime and the console prints the line. From step 3 the
        # stored value sits a hair off its tenth; the drift is drawn exaggerated, sideways.
        def drift(k):
            stored = Fraction(float(values[k]))
            tenth = Fraction(float(f'{float(tenths[k + 1]):.1f}'))   # the double nearest that tenth
            return float(stored - tenth)

        scale = 1.0 / 1.4e-16                                        # units per dollar of drift
        bracket = VGroup()
        note = Text('not to scale', font_size=18, color=FOCUS)

        def step(k, run_time=0.5):
            nonlocal bracket
            y = y_of(tenths[k + 1]) + (0.13 if k == 9 else 0)
            x = axis_x + 0.22 + drift(k) * scale
            anims = [marker.animate.move_to([x, y, 0])]
            d = drift(k)
            if abs(d) > 0:
                new = VMobject(color=FOCUS, stroke_width=3).set_points_as_corners(
                    [[axis_x, y + 0.08, 0], [axis_x, y + 0.2, 0], [x - 0.13, y + 0.2, 0], [x - 0.13, y + 0.08, 0]])
                note_target = note.copy().next_to(new, UP, buff=0.06).align_to([axis_x + 0.2, 0, 0], LEFT)
                if len(bracket):
                    anims += [Transform(bracket, new), note.animate.move_to(note_target)]
                else:
                    bracket = new
                    note.move_to(note_target)
                    anims += [Create(bracket), FadeIn(note)]
            elif len(bracket):
                anims += [FadeOut(bracket), FadeOut(note)]
                bracket = VGroup()
            self.play(*anims, run_time=run_time * 0.6)
            console.type(self, k, run_time=run_time)

        self.at('Watch the printed balance')
        self.play(FadeOut(target), run_time=0.3)
        step(0)
        step(1)
        self.at('After three payments')
        step(2, run_time=0.8)
        src = console.lines[2].source
        trailing = console.lines[2].chars(src.index(values[2]) + 3)
        self.play(trailing.animate.set_color(FOCUS), run_time=0.4)
        self.at('fourteen zeros and a one')
        self.play(Indicate(console.lines[2].chars(len(src) - 1), color=FOCUS), run_time=0.6)
        self.at('The error from each dime')
        for k in range(3, 9):
            step(k, run_time=0.3)

        # [V4.3c] step 10 stops just above zero; a magnifier shows the gap; owed != 0 is still true
        self.at('After ten payments')
        step(9, run_time=0.7)
        card = show_qr(self, 'q04-02')
        lens = magnifier(0.42).move_to(marker.get_center() + RIGHT * 0.05 + DOWN * 0.05)
        gap = values[9]
        readout = VGroup(Text('gap above zero', font_size=20, color=SCAFFOLD),
                         code_text(gap, font_size=24, color=FOCUS)).arrange(DOWN, buff=0.12)
        readout.move_to([4.6, -0.3, 0])
        frame = SurroundingRectangle(readout, color=GREY_B, buff=0.15, corner_radius=0.1)
        link = Line(lens[0].get_top() + RIGHT * 0.2, frame.get_left(), color=GREY_B, stroke_width=2)
        self.at("It's about one ten-quadrillionth")
        self.play(FadeIn(lens, scale=0.6), run_time=0.5)
        self.play(Create(link), FadeIn(frame), FadeIn(readout), run_time=0.7)
        self.at('is still true')
        check = line_highlight(code, 0, color=EXACT)
        still = Text('still true', font_size=24, color=EXACT).next_to(code, RIGHT, buff=0.25).align_to(check, UP)
        self.play(Create(check), FadeIn(still, shift=LEFT * 0.1), run_time=0.5)
        self.play(check.animate.set_stroke(width=8), run_time=0.25)
        self.play(check.animate.set_stroke(width=4), run_time=0.25)
        self.at('and the loop goes around again')
        self.play(FadeOut(lens), FadeOut(link), FadeOut(frame), FadeOut(readout), run_time=0.5)
        hide_qr(self, card)

        # [V4.3d] step 11 jumps past zero; the 0 mark flashes red; the guard catches it at 13
        self.at('The eleventh payment')
        step(10, run_time=0.6)
        self.play(labels[10].animate.set_color(ERROR), ticks[10].animate.set_color(ERROR).scale(1.6), run_time=0.4)
        self.play(ticks[10].animate.scale(1 / 1.6), run_time=0.3)
        self.at('only moves away from zero')
        step(11)
        step(12)
        glyphs = code.code_lines[0]
        source = snippet_lines(Q2, 7, 7)
        nonspace = re.sub(r'\s', '', source)
        start = nonspace.index('steps<13')
        guard_glyphs = VGroup(*glyphs[start:start + len('steps<13')])
        guard_box = SurroundingRectangle(guard_glyphs, color=FOCUS, buff=0.05)
        self.play(FadeOut(check), FadeOut(still), Create(guard_box), run_time=0.5)
        caught = Text('caught by the guard', font_size=20, color=FOCUS).next_to(marker, RIGHT, buff=0.2)
        self.play(FadeIn(caught), run_time=0.4)

        # [V4.3e] the guard is struck out; the marker falls off the bottom of the screen
        self.at('Without the little guard')
        strike = Line(guard_glyphs.get_left() + LEFT * 0.05, guard_glyphs.get_right() + RIGHT * 0.05,
                      color=ERROR, stroke_width=5)
        self.play(Create(strike), FadeOut(guard_box), FadeOut(caught), run_time=0.5)
        if len(bracket):
            self.play(FadeOut(bracket), FadeOut(note), run_time=0.2)
        self.play(marker.animate.shift(DOWN * 4.5), run_time=1.6, rate_func=rate_functions.ease_in_quad)
        never = Text('never ends', font_size=24, color=ERROR).move_to([axis_x + 1.4, -3.3, 0])
        self.play(FadeIn(never), run_time=0.4)

        # Where the pattern hides, and the fix
        self.at('In real systems')
        clear(self, keep=(code,))
        places = VGroup(label_box('retry loops', font_size=24), label_box('payment schedules', font_size=24),
                        label_box('settle up until the difference is gone', font_size=24))
        places.arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([-1.5, -0.3, 0])
        loops = VGroup(*[Arc(radius=0.22, start_angle=0.3, angle=TAU * 0.8, color=ERROR, stroke_width=4)
                         .add_tip(tip_length=0.12).next_to(p, LEFT, buff=0.25) for p in places])
        for p, l, phrase in zip(places, loops, ('retry loops', 'payment schedules', 'code that "settles up"')):
            self.at(phrase)
            self.play(FadeIn(p, shift=RIGHT * 0.2), Create(l), run_time=0.5)
        self.play(*[Rotate(l, -TAU, about_point=l.get_center()) for l in loops], run_time=1.2)
        self.at('never ask a float')
        self.play(FadeOut(places), FadeOut(loops), run_time=0.4)
        no_box = line_highlight(code, 0, color=ERROR)
        rule1 = VGroup(crossmark(size=0.4), Text('never test a float for exactly zero', font_size=28))
        rule1.arrange(RIGHT, buff=0.3).move_to([-0.5, -0.6, 0])
        self.play(Create(no_box), FadeIn(rule1, shift=UP * 0.1), run_time=0.6)
        self.at('even better not to use floats')
        rule2 = VGroup(checkmark(size=0.4), Text('better still: keep balances out of floats', font_size=28),
                       penny(0.3)).arrange(RIGHT, buff=0.3)
        rule2.next_to(rule1, DOWN, buff=0.5).align_to(rule1, LEFT)
        self.play(FadeIn(rule2, shift=UP * 0.1), run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 4.4

class Segment_4_4(Segment):
    """Two systems, one cent apart (q04-03)."""
    EPISODE, SEGMENT = 4, '4.4'

    def construct(self):
        rows = snippet_output(Q3)
        prices = [r.split(':')[0] for r in rows]                       # $0.30 ... $4.10
        float_fees = [r.split('float ')[1].split()[0] for r in rows]
        decimal_fees = [r.split('decimal ')[1].split()[0] for r in rows]

        # Reconciliation: four systems record one payment; each night someone checks they agree
        systems = VGroup(*[label_box(n, font_size=22) for n in
                           ('payment processor', 'billing platform', 'general ledger', 'bank')])
        systems.arrange(RIGHT, buff=0.35).move_to(UP * 1.0)
        fit(systems, 13.2)
        self.at('A payment processor')
        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.2) for s in systems], lag_ratio=0.25), run_time=1.6)
        self.at('each one records the same transaction')
        payment = penny(0.22).move_to(systems[0].get_left() + LEFT * 0.6)
        records = VGroup()
        self.play(FadeIn(payment), run_time=0.3)
        for s in systems:
            self.play(payment.animate.move_to(s.get_top() + UP * 0.35), run_time=0.45)
            rec = penny(0.14).move_to(s.get_bottom() + DOWN * 0.35)
            records.add(rec)
            self.play(TransformFromCopy(payment, rec), run_time=0.3)
        self.play(FadeOut(payment), run_time=0.3)
        self.at('someone checks that they all agree')
        arcs = VGroup(*[ArcBetweenPoints(records[k].get_bottom() + DOWN * 0.1, records[k + 1].get_bottom() + DOWN * 0.1,
                                         angle=PI / 3, color=FOCUS, stroke_width=3) for k in range(3)])
        self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.4), run_time=1.2)
        self.at('That check is called reconciliation')
        name = Text('reconciliation', font_size=36, color=FOCUS).move_to(DOWN * 1.9)
        ticks = VGroup(*[checkmark(size=0.3).next_to(a, DOWN, buff=0.08) for a in arcs])
        self.play(Write(name), LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.3), run_time=1.0)

        # [V4.4a] two systems, each a ledger; both receive the same price list and a 5% fee
        self.at('Now imagine two of those systems')
        clear(self, 0.5)
        books, titles = VGroup(), VGroup()
        for k, (title, colour) in enumerate((('System A (floats)', STORED), ('System B (decimals)', EXACT))):
            book = ledger([''] * 6, ['?'] * 6, headings=('Price', ''), width=5.4, font_size=20)
            book.move_to([-3.5 if k == 0 else 3.5, -0.75, 0])
            for line in book.right:
                line.set_color(SCAFFOLD)
            book.fee_spot = book.headings[0].get_center() + RIGHT * 5.4 / 2
            book.balance.set_color(colour)
            head = Text(title, font_size=28, color=colour).next_to(book, UP, buff=0.25)
            books.add(book)
            titles.add(head)
        self.play(*[FadeIn(b) for b in books], *[FadeIn(t, shift=DOWN * 0.1) for t in titles], run_time=0.8)
        price_list = VGroup(*[code_text(p, font_size=20, color=MONEY) for p in prices])
        for p, line in zip(price_list, books[0].left):
            p.move_to([0, line.get_y(), 0])
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.1) for p in price_list], lag_ratio=0.1), run_time=0.8)
        copies = VGroup()
        for b in books:
            for p, line in zip(price_list, b.left):
                copies.add(p.copy())
        moves = []
        for k, c in enumerate(copies):
            b, line = books[k // 6], books[k // 6].left[k % 6]
            moves.append(c.animate.move_to(line.get_center()))
        self.play(*moves, FadeOut(price_list), run_time=1.0)
        self.at('compute the same five percent fee')
        fees = VGroup()
        for b in books:
            tag = price_tag('5% fee', font_size=22).move_to(b.fee_spot + UP * 2.0)
            fees.add(tag)
        self.play(*[t.animate.move_to(b.fee_spot) for t, b in zip(fees, books)], run_time=0.7,
                  rate_func=rate_functions.ease_out_bounce)
        self.at('System A uses floats')
        self.play(Indicate(titles[0], color=STORED), run_time=0.8)
        self.at('System B uses decimals')
        self.play(Indicate(titles[1], color=EXACT), run_time=0.8)
        self.at('Both pass their own tests')
        oks = VGroup(*[checkmark(size=0.35).next_to(t, RIGHT, buff=0.2) for t in titles])
        self.play(LaggedStart(*[Create(o) for o in oks], lag_ratio=0.4), run_time=0.8)

        # [V4.4b] code panel and console: five breaks, one match
        self.at('Five out of these six')
        clear(self, 0.5)
        code = code_panel(snippet_lines(Q3, 7, 9), font_size=18).to_edge(UP, buff=0.3)
        out = output_console(Q3, font_size=22)
        out.next_to(code, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeIn(code), FadeIn(out.background), run_time=0.5)
        card = show_qr(self, 'q04-03')
        for i in range(6):
            self.play(out.type_line(i, run_time=0.3))
        breaks = [out.lines[i].part('<- break') for i in range(6) if 'break' in rows[i]]
        match = out.lines[prices.index('$1.00')]
        self.play(*[b.animate.set_color(ERROR) for b in breaks], match.glyphs.animate.set_color(EXACT), run_time=0.6)

        # [V4.4c] close-up of $0.30: 1.5 cents, exactly on the midpoint
        self.at('Thirty cents times five percent')
        self.play(FadeOut(code), out.animate.to_corner(UL, buff=0.35), run_time=0.7)
        row30 = SurroundingRectangle(out.lines[0], color=FOCUS, buff=0.06)
        self.play(Create(row30), run_time=0.4)
        left_x, right_x, y = -5.8, 2.2, -1.4
        mid_x = (left_x + right_x) / 2
        axis = Line([left_x - 0.4, y, 0], [right_x + 0.4, y, 0], color=SCAFFOLD, stroke_width=2)
        cent_ticks = VGroup(*[Line(UP * 0.2, DOWN * 0.2, color=SCAFFOLD, stroke_width=3).move_to([x, y, 0])
                              for x in (left_x, right_x)])
        cent_labels = VGroup(Text('1¢', font_size=26, color=MONEY).next_to(cent_ticks[0], DOWN, buff=0.15),
                             Text('2¢', font_size=26, color=MONEY).next_to(cent_ticks[1], DOWN, buff=0.15))
        mid_tick = DashedLine([mid_x, y - 0.3, 0], [mid_x, y + 0.3, 0], color=GREY_B)
        diamond = Square(0.22).rotate(PI / 4).set_fill(FOCUS, 1).set_stroke(width=0).move_to([mid_x, y + 0.45, 0])
        exact_label = Text('$0.30 × 5% = 1½¢, exactly halfway', font_size=22, color=FOCUS)
        exact_label.next_to(diamond, LEFT, buff=0.2)
        self.play(Create(axis), FadeIn(cent_ticks), FadeIn(cent_labels), run_time=0.6)
        self.play(Create(mid_tick), FadeIn(diamond, scale=0.5), FadeIn(exact_label), run_time=0.7)
        self.at('System B rounds that up')
        up = CurvedArrow(diamond.get_right() + RIGHT * 0.1, cent_ticks[1].get_top() + UP * 0.1, angle=-PI / 3,
                         color=EXACT, stroke_width=4)
        b_label = Text('System B: half up → 2¢', font_size=22, color=EXACT).move_to([right_x - 0.6, y + 1.55, 0])
        self.play(Create(up), FadeIn(b_label), run_time=0.9)
        self.at('But System A never sees')
        # The double nearest 0.30 × 0.05, computed here: a hair below 0.015.
        nearest = Decimal(float(prices[0][1:]) * 0.05) * 100
        stored_x = mid_x - 0.35                                          # drawn exaggerated
        stored_tick = Line(UP * 0.2, DOWN * 0.2, color=STORED, stroke_width=4).move_to([stored_x, y, 0])
        stored_label = code_text(f'{str(nearest)[:14]}…¢', font_size=20, color=STORED)
        stored_label.next_to(stored_tick, DOWN, buff=0.15).align_to(stored_tick, LEFT).shift(LEFT * 0.05)
        hair = Text('the stored double: a hair below', font_size=20, color=STORED)
        hair.next_to(stored_label, DOWN, buff=0.12).align_to(stored_label, LEFT)
        self.play(Create(stored_tick), FadeIn(stored_label), FadeIn(hair), run_time=0.7)
        hide_qr(self, card)
        self.at('It sees the nearest double')
        down = CurvedArrow(stored_tick.get_bottom() + DOWN * 0.05, cent_labels[0].get_right() + RIGHT * 0.15,
                           angle=PI / 4, color=STORED, stroke_width=4)
        a_label = Text('System A → 1¢', font_size=22, color=STORED).next_to(down, DOWN, buff=0.1)
        self.play(Create(down), FadeIn(a_label), run_time=0.9)
        self.at('or it lands exactly on a midpoint')
        i250 = prices.index('$2.50')
        row250 = SurroundingRectangle(out.lines[i250], color=FOCUS, buff=0.06)
        product = repr(float(prices[i250][1:]) * 0.05)                   # 0.125, computed here
        tie = Text(f'$2.50 × 5% = {product} exactly: a tie, and round() goes to the even neighbour, '
                   f'{float_fees[i250]}', font_size=22, color=FOCUS)
        fit(tie, 13.0).move_to(DOWN * 3.55)
        self.play(ReplacementTransform(row30, row250), FadeIn(tie, shift=UP * 0.1), run_time=0.7)
        self.at('Either way, System A says one cent')
        self.play(Indicate(a_label, color=STORED), run_time=0.8)

        # [V4.4d] the two ledgers' totals differ by a cent; tickets pile into the exceptions queue
        self.at('Each difference is a single cent')
        clear(self, 0.5)
        book = ledger([('$0.30 fee', float_fees[0])], [('$0.30 fee', decimal_fees[0])],
                      totals=(float_fees[0], decimal_fees[0]), headings=('System A', 'System B'),
                      width=7.0, font_size=22)
        book.move_to([-3.3, 1.0, 0])
        book.totals.set_opacity(0)
        self.play(FadeIn(book), run_time=0.6)
        self.play(book.totals.animate.set_opacity(1), run_time=0.5)
        cent = Text('1¢ apart', font_size=26, color=ERROR).next_to(book, DOWN, buff=0.3)
        self.play(tip_scale(book.balance, -0.2), book.totals.left.animate.set_color(ERROR),
                  book.totals.right.animate.set_color(ERROR), FadeIn(cent), run_time=0.8)
        self.at('every one is a reconciliation break')
        queue_title = Text('Reconciliation exceptions', font_size=26, color=ERROR).move_to([3.7, 3.4, 0])
        self.play(FadeIn(queue_title), run_time=0.5)
        tickets = VGroup(*[ticket(r.split('  <-')[0]) for r in rows if 'break' in r])
        for k, t in enumerate(tickets):
            t.move_to([3.7, 2.7 - 0.62 * k, 0])
        self.play(FadeIn(tickets[0], shift=LEFT * 0.4), run_time=0.5)
        self.at("It's settled by a person")
        clerk = person(GREY_B, 1.5).move_to([-5.6, -2.7, 0])
        self.play(FadeIn(clerk), run_time=0.5)
        slip = tickets[0][0].copy()
        self.play(tickets[0][0].animate.set_stroke(FOCUS, 3), run_time=0.3)
        self.play(slip.animate.stretch_to_fit_width(0.5).stretch_to_fit_height(0.65).set_fill(GREY_E, 1)
                  .set_stroke(FOCUS, 3).move_to(clerk.get_right() + RIGHT * 1.8), run_time=0.8)
        self.at('pulls the records from both systems')
        papers = VGroup(*[Rectangle(width=0.5, height=0.65).set_fill(PAPER, 1).set_stroke(width=0) for _ in range(2)])
        papers[0].move_to(book.totals.left.get_center())
        papers[1].move_to(book.totals.right.get_center())
        self.play(papers[0].animate.move_to(clerk.get_right() + RIGHT * 0.5),
                  papers[1].animate.move_to(clerk.get_right() + RIGHT * 1.15), run_time=0.8)
        self.at('decides which one is right')
        self.play(LaggedStart(*[FadeIn(t, shift=LEFT * 0.4) for t in tickets[1:]], lag_ratio=0.3), run_time=1.4)
        self.at('Multiply that by thousands')
        pile = VGroup(*[RoundedRectangle(width=0.8, height=0.32, corner_radius=0.05).set_fill(GREY_E, 1)
                        .set_stroke(ERROR, 1.5) for _ in range(42)])
        pile.arrange_in_grid(rows=6, cols=7, buff=(0.1, 0.1)).move_to([3.7, -2.0, 0])
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in pile], lag_ratio=0.06), run_time=2.4)
        self.finish()


# ---------------------------------------------------------------- 4.5

class Segment_4_5(Segment):
    """Totals that don't foot."""
    EPISODE, SEGMENT = 4, '4.5'

    def construct(self):
        # The receipt: five prices drawn from q03-05's items and q04-03's price list, taxed at
        # q03-05's 8.25 %. Every tax and total below is computed here in floats: each line's tax
        # is rounded for display, the tax line from the unrounded sum, so they differ by a cent.
        rate = 0.0825
        items = [('Pencil', 0.29), ('Notebook', 9.99), ('Backpack', 19.99), ('Folder', 1.00), ('Stapler', 4.10)]
        taxes = [p * rate for _, p in items]
        tax_sum = float_total(taxes)
        shown = [f'{t:.2f}' for t in taxes]
        shown_sum = sum(Decimal(s) for s in shown)
        tax_line = f'{tax_sum:.2f}'
        assert abs(shown_sum - Decimal(tax_line)) == Decimal('0.01')
        subtotal = float_total(p for _, p in items)
        rows = [('Item         Price', 'Tax'), ('-', '')]
        rows += [(f'{n:<10}{p:>8.2f}', s) for (n, p), s in zip(items, shown)]
        rows += [('-', ''), ('Subtotal', f'{subtotal:.2f}'), ('Tax 8.25%', tax_line),
                 ('Total', f'{subtotal + tax_sum:.2f}')]

        # [V4.5a] the receipt: five lines, each with its own rounded tax
        bill = receipt(rows, width=6.0, font_size=22, title='RECEIPT').move_to([-3.4, 0, 0])
        self.play(FadeIn(bill.paper, shift=UP * 0.3), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.05) for l in bill.lines], lag_ratio=0.12), run_time=2.2)
        item_lines = bill.lines[3:8]
        sub_line, tax_row, total_line = bill.lines[9], bill.lines[10], bill.lines[11]

        # Footing: a tick runs down the price column; cross-footing: across to the total
        self.at('footing')
        price_col = VGroup(*[l.chars(10, 18) for l in item_lines])
        runner = SurroundingRectangle(item_lines[0].chars(10, 18), color=FOCUS, buff=0.05)
        self.play(Create(runner), run_time=0.3)
        for l in item_lines[1:] + [sub_line]:
            target = SurroundingRectangle(l.chars(len(l.source) - 8 if l is sub_line else 10, None if l is sub_line else 18),
                                          color=FOCUS, buff=0.05)
            self.play(Transform(runner, target), run_time=0.3)
        foot_tick = checkmark(size=0.3).next_to(bill.paper, RIGHT, buff=0.15).set_y(sub_line.get_y())
        self.play(FadeOut(runner), Create(foot_tick), run_time=0.4)
        self.at('cross-footing')
        cross = Arrow(sub_line.get_right() + RIGHT * 0.05, total_line.get_right() + RIGHT * 0.05, buff=0,
                      color=FOCUS, stroke_width=3, max_tip_length_to_length_ratio=0.2).shift(RIGHT * 0.7)
        cross_tick = checkmark(size=0.3).next_to(cross, RIGHT, buff=0.1)
        self.play(GrowArrow(cross), Create(cross_tick), run_time=0.6)
        self.play(FadeOut(cross), FadeOut(cross_tick), FadeOut(foot_tick), run_time=0.4)

        # Each line rounded for display; the tax line from the unrounded values
        self.at('Each line is rounded for display')
        raws = VGroup()
        for l, t in zip(item_lines, taxes):
            raw = code_text(repr(t), font_size=20, color=SCAFFOLD)
            raw.next_to(bill.paper, RIGHT, buff=0.5).set_y(l.get_y())
            raws.add(raw)
        self.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.2) for r in raws], lag_ratio=0.15),
                  *[l.chars(len(l.source) - 4).animate.set_color('#a86a00') for l in item_lines], run_time=1.2)
        self.at('the total is computed from the unrounded values')
        raw_sum = code_text(repr(tax_sum), font_size=20, color=SCAFFOLD)
        raw_sum.next_to(bill.paper, RIGHT, buff=0.5).set_y(tax_row.get_y())
        self.play(TransformFromCopy(raws, raw_sum), run_time=1.0)
        to_tax = Arrow(raw_sum.get_left() + LEFT * 0.05, tax_row.get_right() + RIGHT * 0.05, buff=0.05,
                       color=SCAFFOLD, stroke_width=3, max_tip_length_to_length_ratio=0.25)
        self.play(GrowArrow(to_tax), run_time=0.5)

        # [V4.5b] a yellow adding-machine tape runs down the tax column and disagrees by a cent
        self.at('So the printed lines add up')
        self.play(FadeOut(raws), FadeOut(raw_sum), FadeOut(to_tax), run_time=0.4)
        tape_lines = [code_text(f'{s:>6} +', font_size=22, color=INK) for s in shown]
        tape_lines.append(code_text(f'{shown_sum:>6}  ', font_size=22, color=ERROR))
        stack_lines(tape_lines, spacing=1.5)
        tape_text = VGroup(*tape_lines)
        tape = RoundedRectangle(width=tape_text.width + 0.6, height=tape_text.height + 0.6, corner_radius=0.06)
        tape.set_fill(FOCUS, 0.9).set_stroke(width=0)
        tape.next_to(bill.paper, RIGHT, buff=0.6).align_to(item_lines[0], UP).shift(UP * 0.3)
        tape_text.move_to(tape)
        rule = Line(tape_lines[-2].get_left() + DOWN * 0.22, tape_lines[-2].get_right() + DOWN * 0.22, color=INK)
        self.play(GrowFromEdge(tape, UP), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(l) for l in tape_lines[:-1]], lag_ratio=0.3), run_time=1.4)
        self.play(Create(rule), FadeIn(tape_lines[-1]), run_time=0.5)
        bad = tax_row.part(tax_line)
        self.play(bad.animate.set_color(ERROR), run_time=0.4)
        link = DashedLine(bad.get_right() + RIGHT * 0.1, tape_lines[-1].get_left() + LEFT * 0.1, color=ERROR)
        self.play(Create(link), run_time=0.5)
        self.at("To a customer, that's a receipt")
        shopper = person(STORED, 1.4).move_to([5.6, -2.6, 0])
        ask = bubble('?', ERROR, 34).next_to(shopper, UP, buff=0.15)
        self.play(FadeIn(shopper), FadeIn(ask, scale=0.6), run_time=0.6)

        # [V4.5c] a monthly report: tick marks foot each column and cross-foot each row
        self.at('To an auditor')
        clear(self, 0.5)
        regions, months = ['North', 'South', 'East', 'West'], ['Jan', 'Feb', 'Mar']
        # Tax collected (8.25 %) on q04-05's positive transactions, five per cell, summed as floats;
        # this slicing gives one row and one column that don't foot. All computed here.
        positive = [a for a in q05_amounts() if a > 0]
        cells = [[float_total(a * rate for a in positive[(r * 4 + c) * 5:(r * 4 + c + 1) * 5]) for c in range(4)]
                 for r in range(3)]
        row_totals = [float_total(row) for row in cells]
        col_totals = [float_total(cells[r][c] for r in range(3)) for c in range(4)]
        grand = float_total(row_totals)
        bad_rows = [r for r in range(3) if sum(Decimal(f'{v:.2f}') for v in cells[r]) != Decimal(f'{row_totals[r]:.2f}')]
        bad_cols = [c for c in range(4) if sum(Decimal(f'{cells[r][c]:.2f}') for r in range(3))
                    != Decimal(f'{col_totals[c]:.2f}')]
        assert len(bad_rows) == 1 and len(bad_cols) == 1
        table = [[f'{v:.2f}' for v in row] + [f'{t:.2f}'] for row, t in zip(cells, row_totals)]
        table.append([f'{t:.2f}' for t in col_totals] + [f'{grand:.2f}'])
        names = months + ['Total']
        col_w, row_h, label_w = 1.9, 0.62, 1.3
        x0, y0 = -5.4, 1.9
        grid = VGroup()
        texts = {}
        for c, h in enumerate(regions + ['Total']):
            t = Text(h, font_size=22, color=SCAFFOLD).move_to([x0 + label_w + col_w * (c + 0.5), y0, 0])
            grid.add(t)
        for r, n in enumerate(names):
            y = y0 - row_h * (r + 1)
            grid.add(Text(n, font_size=22, color=SCAFFOLD).move_to([x0 + label_w / 2, y, 0]))
            for c in range(5):
                cell = Rectangle(width=col_w, height=row_h).set_stroke(GREY_D, 1)
                cell.move_to([x0 + label_w + col_w * (c + 0.5), y, 0])
                value = code_text(table[r][c], font_size=22, color=MONEY if (r == 3 or c == 4) else WHITE)
                value.move_to(cell).shift(LEFT * 0.15)
                texts[r, c] = (cell, value)
                grid.add(cell, value)
        sheet_title = Text('Monthly report · tax collected by region', font_size=26).move_to([0, 2.9, 0])
        self.play(FadeIn(sheet_title), LaggedStart(*[FadeIn(m) for m in grid], lag_ratio=0.01), run_time=1.2)

        def tick_at(r, c, good):
            cell = texts[r, c][0]
            mark = checkmark(size=0.22) if good else crossmark(size=0.22)
            return mark.move_to(cell.get_right() + LEFT * 0.2)

        marks = VGroup()
        for c in range(5):
            sweep = Line(texts[0, c][0].get_top(), texts[2, c][0].get_bottom(), color=FOCUS, stroke_width=5)
            sweep.set_x(texts[0, c][0].get_right()[0] - 0.05)
            good = c not in bad_cols
            mark = tick_at(3, c, good)
            marks.add(mark)
            self.play(Create(sweep), run_time=0.28)
            self.play(FadeOut(sweep), Create(mark), run_time=0.2)
        self.at('a report that doesn')
        for r in range(4):
            sweep = Line(texts[r, 0][0].get_left(), texts[r, 3][0].get_right(), color=FOCUS, stroke_width=5)
            sweep.set_y(texts[r, 0][0].get_bottom()[1] + 0.05)
            good = r not in bad_rows
            mark = tick_at(r, 4, good)
            marks.add(mark)
            self.play(Create(sweep), run_time=0.28)
            self.play(FadeOut(sweep), Create(mark), run_time=0.2)
        culprit = texts[bad_rows[0], bad_cols[0]]
        self.play(culprit[0].animate.set_fill(ERROR, 0.35).set_stroke(ERROR, 3), culprit[1].animate.set_color(ERROR),
                  run_time=0.5)
        self.play(Wiggle(culprit[1]), run_time=0.7)

        # [V4.5d] the stamp, then the pointer to episode 6
        self.at('The honest explanation')
        no_foot = stamp("DOESN'T FOOT", ERROR, font_size=40).rotate(0.12).move_to([0, -2.6, 0])
        self.play(FadeIn(no_foot, scale=1.8), run_time=0.4, rate_func=rate_functions.ease_in_quad)
        self.play(no_foot.animate.shift(DOWN * 0.05), run_time=0.1)
        self.at('Part of this problem')
        clear(self, 0.5)
        card6 = Text('Episode 6: where to round is a policy.', font_size=40).move_to(UP * 1.0)
        self.play(FadeIn(card6, shift=UP * 0.2), run_time=0.8)
        self.at('But floats make it worse')
        # One of the receipt's own taxes, computed here: the double is off before any rounding.
        price = items[1][1]
        product = repr(price * rate)
        expr = Text(f'{price:.2f} × 8.25% =', font_size=30, color=SCAFFOLD)
        value = code_text(product, font_size=34, color=STORED)
        row = VGroup(expr, value).arrange(RIGHT, buff=0.35).move_to(DOWN * 1.0)
        self.play(FadeIn(expr), run_time=0.4)
        self.play(FadeIn(value, shift=LEFT * 0.2), run_time=0.6)
        tail = value.chars(product.index('00'))
        self.play(tail.animate.set_color(ERROR), run_time=0.5)
        note = Text('slightly off before anything is rounded', font_size=26, color=ERROR).next_to(row, DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.1), run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 4.6

class Segment_4_6(Segment):
    """Truncation's one-way street (q04-04)."""
    EPISODE, SEGMENT = 4, '4.6'

    def construct(self):
        # Errors that go both ways: the cent grid's arrows for cents .01 to .40
        cents = [c for c in range(1, 41) if stored_direction(c)]
        arrows = VGroup()
        for k, c in enumerate(cents):
            d = stored_direction(c)
            a = Arrow(ORIGIN, UP * 0.6 * d, buff=0, stroke_width=4, max_tip_length_to_length_ratio=0.35,
                      color=STORED if d > 0 else ERROR)
            a.move_to([-6.3 + k * 0.33, 0.3 * d, 0])
            arrows.add(a)
        base = Line([-6.6, 0, 0], [6.6, 0, 0], color=SCAFFOLD, stroke_width=2)
        high = Text('stored a little high', font_size=22, color=STORED).move_to([-3.5, 1.4, 0])
        low = Text('stored a little low', font_size=22, color=ERROR).move_to([-3.5, -1.4, 0])
        self.play(Create(base), run_time=0.5)
        self.at('Some amounts are stored')
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.04), FadeIn(high), FadeIn(low),
                  run_time=1.8)
        self.at('they tend to partly cancel')
        net = Dot(color=FOCUS, radius=0.12).move_to([5.5, 0, 0])
        net_label = Text('running net', font_size=20, color=FOCUS).next_to(net, DOWN, buff=1.0)
        self.play(FadeIn(net), FadeIn(net_label), run_time=0.4)
        running = 0
        for c in cents[:12]:
            running += stored_direction(c)
            self.play(net.animate.set_y(0.18 * running), run_time=0.15)

        # Truncation breaks the symmetry: every arrow turns down
        self.at('truncation.')
        downs = [Arrow(ORIGIN, DOWN * 0.6, buff=0, stroke_width=4, max_tip_length_to_length_ratio=0.35, color=ERROR)
                 .move_to([a.get_x(), -0.3, 0]) for a in arrows]
        self.play(*[Transform(a, d) for a, d in zip(arrows, downs)], FadeOut(high), net.animate.set_y(-2.2),
                  run_time=1.2)

        # [V4.6a] a cent sliced into hundredths; 100,000 accounts, each producing a sliver
        self.at('Cutting off everything past the cent')
        clear(self, 0.5)
        cent = sliced_penny(100, radius=1.4).move_to([-4.3, 0.6, 0])
        cent_label = Text('one cent, in hundredths', font_size=22, color=MONEY).next_to(cent, DOWN, buff=0.3)
        self.play(FadeIn(cent, scale=0.8), FadeIn(cent_label), run_time=0.8)
        self.play(LaggedStart(*[w.animate.shift(RIGHT * 0.25 + DOWN * 0.1).set_fill(ERROR, 0.9) for w in cent[63:]],
                              lag_ratio=0.02), run_time=1.2)
        self.at('In episode three')
        classic = code_text(output_line(Q0, 'int('), font_size=26, color=WHITE).move_to([2.6, 2.3, 0])
        self.play(FadeIn(classic, shift=UP * 0.1), run_time=0.6)
        self.play(classic.part('114').animate.set_color(ERROR), run_time=0.5)
        self.at("This code computes one day's interest")
        self.play(FadeOut(classic), run_time=0.3)
        icons = VGroup(*[Square(0.13).set_fill(STORED, 0.8).set_stroke(width=0) for _ in range(30 * 12)])
        icons.arrange_in_grid(rows=12, cols=30, buff=0.07).move_to([2.6, 0.9, 0])
        many = Text('100,000 accounts (a few hundred shown)', font_size=20, color=SCAFFOLD).next_to(icons, DOWN, buff=0.3)
        self.play(LaggedStart(*[FadeIn(i) for i in icons], lag_ratio=0.002), FadeIn(many), run_time=1.2)
        rng = random.Random(7)                                         # which icons sparkle: decoration only
        slivers = VGroup(*[Dot(radius=0.05, color=MONEY).move_to(icons[rng.randrange(len(icons))]) for _ in range(24)])
        self.play(LaggedStart(*[s.animate.move_to(cent.get_center()).set_opacity(0.2) for s in slivers],
                              lag_ratio=0.05), run_time=1.6)
        self.remove(slivers)

        # [V4.6b] two funnels: truncation sends every tail to one bin; rounding fills two, level
        self.at('To keep floating point out of the picture')
        clear(self, 0.5)
        # One day's interest on q04-04's 100,000 balances, generated here exactly as the snippet does.
        rng = random.Random(4)
        daily = Decimal('0.05') / 365
        interests = [Decimal(rng.randrange(1, 1_000_000)) / 100 * daily for _ in range(100_000)]
        tails = [(i * 100) % 1 for i in interests]                     # fraction of a cent past the cut
        lost_trunc = sum(tails) / 100
        lost_round = sum(t for t in tails if t < Decimal('0.5')) / 100
        gained_round = sum(1 - t for t in tails if t >= Decimal('0.5')) / 100
        assert f'{lost_trunc:.2f}' == output_line(Q4, 'short by').split()[-1]

        t_funnel = funnel().move_to([-3.6, 1.2, 0])
        r_funnel = funnel().move_to([3.6, 1.2, 0])
        t_title = Text('truncate (round down)', font_size=26).next_to(t_funnel, UP, buff=0.75)
        r_title = Text('round to nearest', font_size=26).next_to(r_funnel, UP, buff=0.75)
        t_bin = Bin(1.5, 2.0, ERROR).move_to([-3.6, -2.3, 0])
        r_lost = Bin(1.3, 2.0, ERROR).move_to([2.75, -2.3, 0])
        r_gain = Bin(1.3, 2.0, EXACT).move_to([4.45, -2.3, 0])
        bin_labels = VGroup(Text('lost', font_size=20, color=ERROR).next_to(t_bin, LEFT, buff=0.2),
                            Text('lost', font_size=20, color=ERROR).next_to(r_lost, LEFT, buff=0.2),
                            Text('gained', font_size=20, color=EXACT).next_to(r_gain, RIGHT, buff=0.2))
        self.play(FadeIn(VGroup(t_funnel, r_funnel, t_title, r_title, t_bin, r_lost, r_gain, bin_labels)), run_time=0.8)
        self.at('The only difference')
        unit = 1.6                                                      # bin height for one whole cent
        levels = [0, 0, 0]
        for k in range(4):
            c = interests[k] * 100
            tail = tails[k]
            whole = int(c)
            pair = VGroup()
            for x in (-3.6, 3.6):
                pair.add(code_text(f'{c:.3f}¢', font_size=22, color=MONEY).move_to([x, 2.35, 0]))
            self.play(*[FadeIn(p, shift=DOWN * 0.2) for p in pair], run_time=0.2)
            up = tail >= Decimal('0.5')
            t_out = code_text(f'{whole}¢', font_size=22, color=MONEY).move_to([-3.6, 0.0, 0])
            r_out = code_text(f'{whole + (1 if up else 0)}¢', font_size=22, color=MONEY).move_to([3.6, 0.0, 0])
            t_chip = Rectangle(width=0.5, height=0.12).set_fill(ERROR, 1).set_stroke(width=0).move_to([-3.6, 0.0, 0])
            r_chip = Rectangle(width=0.5, height=0.12).set_fill(EXACT if up else ERROR, 1).set_stroke(width=0)
            r_chip.move_to([3.6, 0.0, 0])
            levels[0] += float(tail) * unit / 4
            if up:
                levels[2] += float(1 - tail) * unit / 4
            else:
                levels[1] += float(tail) * unit / 4
            self.play(pair[0].animate.move_to(t_out), pair[1].animate.move_to(r_out), run_time=0.3)
            self.play(ReplacementTransform(pair[0], t_out), ReplacementTransform(pair[1], r_out), run_time=0.15)
            self.add(t_chip, r_chip)
            self.play(t_chip.animate.move_to(t_bin.walls.get_center()).set_opacity(0),
                      r_chip.animate.move_to((r_gain if up else r_lost).walls.get_center()).set_opacity(0),
                      t_bin.fill_to(levels[0]), r_lost.fill_to(levels[1]), r_gain.fill_to(levels[2]),
                      FadeOut(t_out), FadeOut(r_out), run_time=0.35)
            self.remove(t_chip, r_chip)
        # ... and the other 99,996 accounts at once
        scale = 1.8 / float(lost_trunc)
        times = Text('× 100,000', font_size=30, color=FOCUS).move_to([0, 1.2, 0])
        self.play(FadeIn(times, scale=0.6), run_time=0.4)
        self.play(t_bin.fill_to(float(lost_trunc) * scale), r_lost.fill_to(float(lost_round) * scale),
                  r_gain.fill_to(float(gained_round) * scale), run_time=1.2)

        # [V4.6c] code panel and console; the three totals as bars
        self.at('Rounding to nearest ends up')
        clear(self, 0.5)
        code = code_panel(snippet_lines(Q4, 10, 15), font_size=18).to_corner(UL, buff=0.35)
        out = output_console(Q4, font_size=20).next_to(code, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeIn(code), FadeIn(out.background), run_time=0.5)
        card = show_qr(self, 'q04-04')
        self.play(out.type_line(0, run_time=0.6))
        totals = [Decimal(after_colon(l).split()[0]) for l in snippet_output(Q4)]
        floor = Decimal(67500)                                          # where the bars start (zoomed in)
        per = 4.0 / float(totals[0] - floor)
        names = ['exact', 'after truncating', 'after rounding']
        colours = [MONEY, ERROR, STORED]
        bars, bar_labels = VGroup(), VGroup()
        for k, (n, t) in enumerate(zip(names, totals)):
            y = -1.25 - 0.75 * k
            label = Text(n, font_size=22, color=SCAFFOLD).move_to([-5.0, y, 0], aligned_edge=RIGHT)
            label.align_to([-4.4, 0, 0], RIGHT)
            bar = Rectangle(width=float(t - floor) * per, height=0.42).set_fill(colours[k], 0.85).set_stroke(width=0)
            bar.move_to([-4.2, y, 0], aligned_edge=LEFT)
            bars.add(bar)
            bar_labels.add(label)
        start_note = Text('bars start at 67,500', font_size=18, color=SCAFFOLD).move_to([-2.2, -3.65, 0])
        self.play(FadeIn(bar_labels[0]), GrowFromEdge(bars[0], LEFT), FadeIn(start_note), run_time=0.8)
        self.play(out.type_line(2, run_time=0.7))
        self.play(FadeIn(bar_labels[2]), GrowFromEdge(bars[2], LEFT), out.part(2, 'off by -0.46').animate.set_color(GREY),
                  run_time=0.8)
        self.at('Truncating comes up short')
        self.play(out.type_line(1, run_time=0.7))
        self.play(FadeIn(bar_labels[1]), GrowFromEdge(bars[1], LEFT), out.part(1, 'short by 500.48').animate.set_color(ERROR),
                  run_time=0.9)
        gap = DashedLine(bars[1].get_right(), [bars[0].get_right()[0], bars[1].get_y(), 0], color=ERROR)
        self.play(Create(gap), run_time=0.5)
        self.at('In one day')
        hide_qr(self, card)
        self.at('Every single cut went the same way')
        self.play(Indicate(bars[1], color=ERROR, scale_factor=1.05), run_time=0.8)

        # Noise and bias; bias moves money from one party to another
        self.at('noise and bias')
        clear(self, 0.5)
        noise_title = Text('noise', font_size=32).move_to([-3.6, 2.8, 0])
        bias_title = Text('bias', font_size=32, color=ERROR).move_to([3.6, 2.8, 0])
        line_l = Line([-6.0, 1.2, 0], [-1.2, 1.2, 0], color=SCAFFOLD)
        line_r = Line([1.2, 1.2, 0], [6.0, 1.2, 0], color=SCAFFOLD)
        noise = VGroup()
        for k, c in enumerate(cents[:14]):
            d = stored_direction(c)
            noise.add(Arrow(ORIGIN, UP * 0.5 * d, buff=0, stroke_width=4, max_tip_length_to_length_ratio=0.35,
                            color=STORED if d > 0 else ERROR).move_to([-5.8 + 0.34 * k, 1.2 + 0.25 * d, 0]))
        bias = VGroup(*[Arrow(ORIGIN, DOWN * 0.5, buff=0, stroke_width=4, max_tip_length_to_length_ratio=0.35,
                              color=ERROR).move_to([1.4 + 0.34 * k, 0.95, 0]) for k in range(14)])
        self.play(FadeIn(noise_title), FadeIn(bias_title), Create(line_l), Create(line_r), run_time=0.5)
        self.play(LaggedStart(*[GrowArrow(a) for a in noise], lag_ratio=0.05),
                  LaggedStart(*[GrowArrow(a) for a in bias], lag_ratio=0.05), run_time=1.2)
        self.at('Bias moves money')
        payer, payee = person(GREY_B, 1.4).move_to([-3.0, -2.3, 0]), person(GREY_B, 1.4).move_to([3.0, -2.3, 0])
        self.play(FadeIn(payer), FadeIn(payee), run_time=0.4)
        coins = VGroup(*[penny(0.18) for _ in range(8)])
        for k, c in enumerate(coins):
            c.move_to(payer.get_right() + RIGHT * 0.4 + UP * 0.2 * (k % 3))
        self.play(LaggedStart(*[c.animate.move_to(payee.get_left() + LEFT * 0.4 + UP * 0.2 * (k % 3))
                                for k, c in enumerate(coins)], lag_ratio=0.15), run_time=2.0)
        self.at('ends up in court')
        self.play(Indicate(bias_title, color=ERROR), run_time=0.7)
        self.at('Hold on to this one')
        clear(self, 0.5)
        ahead = end_card('Episode 7', 'Fractions of a penny').move_to(UP * 0.8)
        slices = sliced_penny(12, 0.6, gap=0.04).next_to(ahead, DOWN, buff=0.6)
        self.play(FadeIn(ahead, shift=UP * 0.2), FadeIn(slices, scale=0.8), run_time=0.8)
        self.play(Rotate(slices, -PI / 2), run_time=1.5)
        self.finish()


# ---------------------------------------------------------------- 4.7

class Segment_4_7(Segment):
    """The report you can't reproduce (q04-05)."""
    EPISODE, SEGMENT = 4, '4.7'

    def construct(self):
        # In ordinary arithmetic the order doesn't matter
        self.at('In ordinary arithmetic')
        terms = VGroup(*[Text(t, font_size=56) for t in ('2', '+', '3', '+', '4', '=', '9')]).arrange(RIGHT, buff=0.3)
        terms.move_to(UP * 1.0)
        self.play(FadeIn(terms, shift=UP * 0.2), run_time=0.8)
        self.at('whichever way you go')
        slots = [terms[0].get_center(), terms[2].get_center(), terms[4].get_center()]
        self.play(terms[0].animate.move_to(slots[2]), terms[4].animate.move_to(slots[0]), path_arc=PI / 2, run_time=1.0)
        self.play(terms[6].animate.set_color(EXACT), run_time=0.4)

        # With floats every addition rounds to the nearest double
        self.at('With floats, every single addition')
        self.play(terms.animate.scale(0.6).to_edge(UP, buff=0.4), run_time=0.6)
        line = FloatLine('0.29999999999999993', '0.30000000000000016', width=10,
                         labels={0.3: '0.3', 0.1 + 0.2: '0.30000000000000004'})
        line.move_to(UP * 0.4)
        self.play(FadeIn(line), run_time=0.6)
        diamond = line.diamond(Fraction(3, 10))
        self.play(FadeIn(diamond, shift=DOWN * 0.2), run_time=0.4)
        self.play(Create(line.snap(Fraction(3, 10))), run_time=0.6)
        self.at('Change the order')
        # Two orders of the same three additions, computed here.
        a, b = (0.1 + 0.2) + 0.3, 0.1 + (0.2 + 0.3)
        orders = VGroup(code_text(f'(0.1 + 0.2) + 0.3 = {a!r}', font_size=26),
                        code_text(f'0.1 + (0.2 + 0.3) = {b!r}', font_size=26)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        orders.move_to(DOWN * 2.2)
        self.play(FadeIn(orders[0], shift=UP * 0.1), run_time=0.5)
        self.play(FadeIn(orders[1], shift=UP * 0.1), run_time=0.5)
        self.play(orders[0].part(repr(a)).animate.set_color(ERROR), orders[1].part(repr(b)).animate.set_color(STORED),
                  run_time=0.5)

        # [V4.7a] three stacks of the same 1,000 transactions, ordered three ways
        self.at('These are the same thousand transactions')
        clear(self, 0.5)
        amounts = q05_amounts()
        tops = [amounts[0], max(amounts), min(amounts)]                 # each stack's top card, computed here
        orders_names = ['by time', 'largest first', 'smallest first']
        xs = [-4.6, 0, 4.6]
        stacks = VGroup()
        for x, name, top in zip(xs, orders_names, tops):
            cards = VGroup(*[RoundedRectangle(width=2.2, height=1.0, corner_radius=0.08).set_fill(GREY_E, 1)
                             .set_stroke(GREY_B, 1.5).shift(UP * 0.07 * k + RIGHT * 0.05 * k) for k in range(7)])
            amount = code_text(f'{top:.2f}', font_size=24, color=MONEY).move_to(cards[-1])
            title = Text(name, font_size=26).next_to(cards, UP, buff=0.3)
            stack = VGroup(cards, amount, title).move_to([x, 2.0, 0])
            stacks.add(stack)
        count = Text('1,000 transactions each', font_size=20, color=SCAFFOLD).move_to([0, 3.6, 0])
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.2) for s in stacks], lag_ratio=0.2), FadeIn(count), run_time=1.2)

        # [V4.7b] each stack feeds an adding machine; three totals print side by side
        machines = VGroup(*[label_box('running total', font_size=22).move_to([x, -0.4, 0]) for x in xs])
        self.play(FadeIn(machines), run_time=0.4)
        feeds = []
        for s, m in zip(stacks, machines):
            for k in range(4):
                c = s[0][-1].copy().set_fill(GREY_D, 1)
                feeds.append(c.animate.move_to(m).scale(0.3).set_opacity(0))
        self.play(LaggedStart(*feeds, lag_ratio=0.08), run_time=1.6)
        texts = [after_colon(l) for l in snippet_output(Q5)]
        agree = common_prefix(texts)
        totals = VGroup(*[colour_value(code_text(t, font_size=24), agree).move_to([x, -1.7, 0]) for t, x in zip(texts, xs)])
        self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in totals], lag_ratio=0.3), run_time=1.2)
        three = Text('three totals', font_size=24, color=ERROR).move_to(DOWN * 2.8)
        self.play(FadeIn(three), run_time=0.4)

        # [V4.7c] a server rack splits the cards across eight workers; two runs, two totals
        self.at('Because big systems split the work')
        clear(self, 0.5)
        rack = VGroup()
        for k in range(8):
            slot = RoundedRectangle(width=2.6, height=0.55, corner_radius=0.06).set_stroke(GREY_B, 2).set_fill(GREY_E, 1)
            slot.add(Text(f'worker {k + 1}', font_size=18, color=SCAFFOLD).move_to(slot).shift(LEFT * 0.5))
            rack.add(slot)
        rack.arrange(DOWN, buff=0.1).move_to([-1.6, 0, 0])
        frame = SurroundingRectangle(rack, color=GREY_B, buff=0.15, corner_radius=0.1)
        pile = VGroup(*[RoundedRectangle(width=1.4, height=0.7, corner_radius=0.06).set_fill(GREY_E, 1)
                        .set_stroke(GREY_B, 1.5).shift(UP * 0.06 * k) for k in range(6)]).move_to([-5.6, 0, 0])
        pile_label = Text('1,000 cards', font_size=20, color=SCAFFOLD).next_to(pile, DOWN, buff=0.25)
        self.play(FadeIn(rack), Create(frame), FadeIn(pile), FadeIn(pile_label), run_time=0.7)

        # Two runs: cards go to random workers, each adds its share, then the partial sums are
        # added in the order the workers finish. Computed here; seeds 1 and 5 give two totals.
        def run(seed):
            rng = random.Random(seed)
            shares = [[] for _ in range(8)]
            for a in amounts:
                shares[rng.randrange(8)].append(a)
            parts = [float_total(s) for s in shares]
            order = list(range(8))
            rng.shuffle(order)
            return float_total(parts[i] for i in order), rng

        runs = [run(1)[0], run(5)[0]]
        assert runs[0] != runs[1]
        run_texts = [repr(r) for r in runs]
        agree = common_prefix(run_texts)
        results = VGroup()
        for k, (seed, colour) in enumerate(((1, STORED), (5, PURPLE_B))):
            pick = random.Random(seed + 100)                            # which slot each flying card lands in
            flying = VGroup(*[pile[-1].copy().set_fill(colour, 0.8) for _ in range(10)])
            self.play(LaggedStart(*[f.animate.scale(0.35).move_to(rack[pick.randrange(8)].get_right() + LEFT * 0.45
                                                                   + RIGHT * 0.12 * (j % 3))
                                    for j, f in enumerate(flying)], lag_ratio=0.1), run_time=1.6)
            label = Text(f'run {k + 1}', font_size=24, color=colour)
            value = colour_value(code_text(run_texts[k], font_size=26), agree)
            result = VGroup(label, value).arrange(RIGHT, buff=0.35).move_to([3.9, 0.9 - 1.6 * k, 0])
            arrows = VGroup(*[Arrow(rack[j].get_right(), result.get_left(), buff=0.1, stroke_width=2,
                                    color=colour, max_tip_length_to_length_ratio=0.05) for j in range(8)])
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.05), run_time=0.8)
            self.play(FadeIn(result, shift=RIGHT * 0.2), FadeOut(arrows), FadeOut(flying), run_time=0.6)
            results.add(result)
            if k == 0:
                self.at('Run the same report twice')

        # Rounding to cents hides it ... unless a total sits next to a half cent
        self.at('rounding to cents hides it')
        cents_view = VGroup(*[code_text(f'{r:.2f}', font_size=26, color=EXACT).next_to(res, DOWN, buff=0.25)
                              for r, res in zip(runs, results)])
        self.play(*[FadeIn(c, shift=DOWN * 0.1) for c in cents_view], run_time=0.6)
        same = checkmark(size=0.35).next_to(cents_view[1], RIGHT, buff=0.3)
        self.play(Create(same), run_time=0.4)
        self.at('But not always')
        clear(self, 0.5)
        ax_l, ax_r, y = -5.0, 5.0, 0.3
        axis = Line([ax_l - 0.4, y, 0], [ax_r + 0.4, y, 0], color=SCAFFOLD)
        ends = VGroup(*[Line(UP * 0.25, DOWN * 0.25, color=MONEY, stroke_width=4).move_to([x, y, 0]) for x in (ax_l, ax_r)])
        end_labels = VGroup(Text('one cent', font_size=24, color=MONEY).next_to(ends[0], DOWN, buff=0.2),
                            Text('the next cent', font_size=24, color=MONEY).next_to(ends[1], DOWN, buff=0.2))
        half = DashedLine([0, y - 0.45, 0], [0, y + 0.45, 0], color=FOCUS)
        half_label = Text('half a cent', font_size=24, color=FOCUS).next_to(half, UP, buff=0.15)
        self.play(Create(axis), FadeIn(ends), FadeIn(end_labels), Create(half), FadeIn(half_label), run_time=0.8)
        dots = VGroup(Dot([-0.25, y, 0], color=STORED, radius=0.1), Dot([0.25, y, 0], color=PURPLE_B, radius=0.1))
        self.play(FadeIn(dots, scale=2), run_time=0.4)
        arrows = VGroup(CurvedArrow(dots[0].get_center() + DOWN * 0.15, ends[0].get_bottom() + DOWN * 0.6 + RIGHT * 0.6,
                                    angle=-PI / 4, color=STORED),
                        CurvedArrow(dots[1].get_center() + DOWN * 0.15, ends[1].get_bottom() + DOWN * 0.6 + LEFT * 0.6,
                                    angle=PI / 4, color=PURPLE_B))
        runs_l = VGroup(Text('run 1 rounds down', font_size=22, color=STORED).move_to([-2.7, -1.9, 0]),
                        Text('run 2 rounds up', font_size=22, color=PURPLE_B).move_to([2.7, -1.9, 0]))
        self.at('the order of addition decides')
        self.play(Create(arrows[0]), FadeIn(runs_l[0]), run_time=0.7)
        self.play(Create(arrows[1]), FadeIn(runs_l[1]), run_time=0.7)

        # [V4.7d] an auditor holds up two printouts of the "same" report
        self.at('And when a regulator asks')
        clear(self, 0.5)
        auditor = person(GREY_B, 2.0).move_to([0, -1.0, 0])
        prints = VGroup()
        for k, t in enumerate((texts[0], texts[2])):
            p = receipt([('Transactions', '1,000'), ('-', ''), ('Total', t)], width=4.8, font_size=20,
                        title='QUARTERLY REPORT')
            colour_value(p.rows[2], len(p.rows[2].source) - len(t) + agree, good=INK)
            p.move_to([-4.0 if k == 0 else 4.0, -4.8, 0])
            prints.add(p)
        self.play(FadeIn(auditor), run_time=0.5)
        self.play(prints[0].animate.move_to([-4.0, 0.9, 0]).rotate(0.05),
                  prints[1].animate.move_to([4.0, 0.9, 0]).rotate(-0.05), run_time=1.0)
        hands = VGroup(Line(auditor.get_top() + DOWN * 0.7 + LEFT * 0.3, prints[0].get_bottom() + RIGHT * 0.8,
                            color=GREY_B, stroke_width=8),
                       Line(auditor.get_top() + DOWN * 0.7 + RIGHT * 0.3, prints[1].get_bottom() + LEFT * 0.8,
                            color=GREY_B, stroke_width=8))
        self.play(Create(hands), run_time=0.4)
        self.at('is not the answer')
        neq = Text('≠', font_size=72, color=ERROR).move_to(UP * 1.4)
        self.play(FadeIn(neq, scale=0.6), run_time=0.5)
        self.finish()


# ---------------------------------------------------------------- 4.8

class Segment_4_8(Segment):
    """A stock index that sank."""
    EPISODE, SEGMENT = 4, '4.8'

    def construct(self):
        # Two real stories
        stories = VGroup(label_box('1982 · a stock index', font_size=28), label_box('1991 · a clock', font_size=28))
        stories.arrange(RIGHT, buff=1.4).move_to(UP * 0.2)
        slide = VMobject(color=STORED, stroke_width=4).set_points_smoothly(
            [LEFT * 1.0 + UP * 0.35, LEFT * 0.3 + UP * 0.1, RIGHT * 0.4 + DOWN * 0.1, RIGHT * 1.0 + DOWN * 0.35])
        slide.next_to(stories[0], UP, buff=0.5)
        cells = VGroup(*[Square(0.22).set_stroke(GREY_B, 2) for _ in range(8)]).arrange(RIGHT, buff=0)
        cells.next_to(stories[1], UP, buff=0.5)
        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.2) for s in stories], lag_ratio=0.4), run_time=1.2)
        self.play(Create(slide), LaggedStart(*[Create(c) for c in cells], lag_ratio=0.1), run_time=1.4)
        self.at('a number that couldn')
        common = Text('a number that couldn\'t be stored exactly', font_size=26, color=FOCUS).next_to(stories, DOWN, buff=0.6)
        self.play(FadeIn(common, shift=UP * 0.1), run_time=0.6)
        self.at('nobody watched the error grow')
        self.play(Indicate(common, color=FOCUS), run_time=0.8)

        # [V4.8a] the index from January 1982 at 1000, sliding down to about 524.811 by November 1983
        self.at('In 1982, the Vancouver')
        clear(self, 0.5)
        ox, oy, w, h = -5.8, -3.0, 7.6, 5.6
        top_value = 1200

        def pt(month, value):
            return np.array([ox + w * month / 22, oy + h * value / top_value, 0])

        axes = VGroup(Line(pt(0, 0), pt(22, 0) + RIGHT * 0.2, color=SCAFFOLD), Line(pt(0, 0), pt(0, top_value), color=SCAFFOLD))
        grid = VGroup(*[DashedLine(pt(0, v), pt(22, v), color=GREY_D, stroke_width=1.5) for v in (500, 1000)])
        y_labels = VGroup(*[Text(str(v), font_size=20, color=SCAFFOLD).next_to(pt(0, v), LEFT, buff=0.15)
                            for v in (500, 1000)])
        x_labels = VGroup(Text('Jan 1982', font_size=20, color=SCAFFOLD).next_to(pt(0, 0), DOWN, buff=0.15),
                          Text('Nov 1983', font_size=20, color=SCAFFOLD).next_to(pt(22, 0), DOWN, buff=0.15))
        title = Text('Vancouver Stock Exchange index', font_size=26).move_to([ox + w / 2, 3.5, 0])
        self.play(FadeIn(VGroup(axes, grid, y_labels, x_labels, title)), run_time=0.8)
        # A schematic path: a steady slide from 1000 to 524.811 over 22 months (the two ends are
        # the fact-checked values; the months between are drawn as an even decline, not data).
        end_value = 524.811
        path = VMobject(color=STORED, stroke_width=4).set_points_smoothly(
            [pt(m, 1000 * (end_value / 1000) ** (m / 22)) for m in range(23)])
        start_dot = Dot(pt(0, 1000), color=STORED)
        self.play(FadeIn(start_dot), run_time=0.3)

        # [V4.8b] inset: one update, its digits past the third cut off into a red bin
        self.at('It was recalculated with every trade')
        inset = RoundedRectangle(width=4.2, height=2.6, corner_radius=0.12).set_stroke(GREY_B, 2).move_to([4.7, 2.2, 0])
        inset_title = Text('one update', font_size=22, color=SCAFFOLD).next_to(inset.get_top(), DOWN, buff=0.2)
        rate_note = Text('thousands of updates a day', font_size=20, color=FOCUS).next_to(inset, DOWN, buff=0.2)
        cut_bin = Bin(1.6, 1.4, ERROR).move_to([4.7, -1.9, 0])
        bin_label = Text('cut off', font_size=20, color=ERROR).next_to(cut_bin, DOWN, buff=0.15)
        self.play(FadeIn(inset),
                  FadeIn(inset_title), FadeIn(rate_note), FadeIn(cut_bin), FadeIn(bin_label), run_time=0.6)
        # Illustrative updates, computed here: tiny random moves of the index, each new value
        # truncated to three decimals. They show the mechanism, not real trades.
        rng = random.Random(1982)
        old = Decimal('1000.000')
        level = 0.0
        drawn = 0.0
        for k in range(4):
            true = old * (1 + Decimal(rng.randint(-600_000, 400_000)) / Decimal(10) ** 10)
            text = f'{true:.7f}'
            kept_len = text.index('.') + 4
            value = code_text(text, font_size=28).move_to(inset.get_center() + DOWN * 0.15)
            knife = DashedLine(UP * 0.35, DOWN * 0.35, color=ERROR).move_to(value.chars(kept_len - 1, kept_len).get_right()
                                                                           + RIGHT * 0.06)
            self.play(FadeIn(value, shift=DOWN * 0.15), run_time=0.3)
            self.play(Create(knife), run_time=0.2)
            tail = value.chars(kept_len)
            level += 0.18
            self.play(tail.animate.set_color(ERROR).move_to(cut_bin.walls.get_center()).scale(0.5).set_opacity(0),
                      cut_bin.fill_to(level), run_time=0.6)
            self.play(FadeOut(value), FadeOut(knife), run_time=0.2)
            old = true.quantize(Decimal('0.001'), rounding=ROUND_DOWN)
            # the main chart creeps along between updates
            nxt = min(1.0, drawn + 0.12)
            self.play(Create(path.copy().pointwise_become_partial(path, drawn, nxt)), run_time=0.3)
            drawn = nxt
        self.at('Not rounded')
        no_round = Text('not rounded:', font_size=24, color=SCAFFOLD).move_to(inset.get_center() + UP * 0.25)
        cut = Text('truncated', font_size=30, color=ERROR).next_to(no_round, DOWN, buff=0.2)
        self.play(FadeIn(no_round), run_time=0.4)
        self.at('Truncated.')
        self.play(FadeIn(cut, scale=1.3), run_time=0.4)

        self.at('Every recalculation lost a little')
        rest = path.copy().pointwise_become_partial(path, drawn, 1.0)
        self.play(Create(rest), cut_bin.fill_to(1.25), run_time=5.0, rate_func=rate_functions.linear)
        end_label = Text('≈ 524.811', font_size=24, color=STORED).next_to(pt(22, end_value), DOWN, buff=0.25)
        self.play(FadeIn(end_label), run_time=0.4)
        self.at('about half its starting value')
        half = DashedLine(pt(22, 1000) + RIGHT * 0.15, pt(22, end_value) + RIGHT * 0.15, color=GREY_B)
        self.play(Create(half), run_time=0.6)

        # [V4.8c] the recalculated value, and a green jump up to it
        self.at('When the error was found')
        self.play(FadeOut(VGroup(inset, inset_title, no_round, cut, rate_note, half)), run_time=0.5)
        new_value = 1098.892
        jump = Arrow(pt(22, end_value) + UP * 0.1, pt(22, new_value), buff=0, color=EXACT, stroke_width=6)
        new_label = Text('≈ 1098.892', font_size=28, color=EXACT).next_to(pt(22, new_value), RIGHT, buff=0.25)
        self.at('it jumped from around')
        self.play(GrowArrow(jump), run_time=0.8)
        self.play(FadeIn(new_label, shift=LEFT * 0.2), Flash(pt(22, new_value), color=EXACT), run_time=0.6)
        overnight = Text('overnight', font_size=22, color=EXACT).next_to(new_label, DOWN, buff=0.15)
        self.at('overnight')
        self.play(FadeIn(overnight), run_time=0.4)

        # [V4.8d] the caption
        self.at("That's truncation's one-way street")
        lesson = VGroup(Text('Truncation, not floating point.', font_size=28),
                        Text('Same lesson.', font_size=28, color=FOCUS)).arrange(DOWN, buff=0.2)
        lesson.move_to([4.2, -2.3, 0])
        self.play(FadeOut(cut_bin), FadeOut(bin_label), run_time=0.4)
        self.play(FadeIn(lesson[0], shift=UP * 0.1), run_time=0.6)
        self.at('No floating point required')
        self.play(FadeIn(lesson[1], shift=UP * 0.1), run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 4.9

class Segment_4_9(Segment):
    """One tenth of a second: plain, grey and white, no drama."""
    EPISODE, SEGMENT = 4, '4.9'

    def construct(self):
        # The binary digits of 1/10, computed here by doubling.
        f, bits = Fraction(1, 10), ''
        for _ in range(34):
            f *= 2
            bits += str(int(f))
            f -= int(f)
        kept, spill = bits[:24], bits[24:]

        # [V4.9a] a 24-box register holding the start of 1/10 in binary
        size = 0.36
        boxes = VGroup(*[Square(size).set_stroke(GREY_B, 2) for _ in range(24)]).arrange(RIGHT, buff=0)
        point = Text('0.', font=MONO, font_size=28, color=WHITE)
        register = VGroup(point, boxes).arrange(RIGHT, buff=0.12).move_to([-1.2, 0.6, 0])
        caption_top = Text('one tenth, in binary', font_size=24, color=SCAFFOLD).next_to(register, UP, buff=0.5)
        digits = VGroup(*[Text(b, font=MONO, font_size=24, color=WHITE).move_to(box) for b, box in zip(kept, boxes)])
        extra = VGroup(*[Text(b, font=MONO, font_size=24, color=GREY_D).move_to(boxes[-1].get_center() + RIGHT * size * (k + 1))
                         for k, b in enumerate(spill)])
        self.wait(0.6)
        self.play(FadeIn(caption_top), FadeIn(register), run_time=1.2)
        self.at('In 1991')
        self.play(LaggedStart(*[FadeIn(d) for d in digits], lag_ratio=0.25), run_time=8.0, rate_func=rate_functions.linear)
        self.at('fixed-point register')
        width = Text('24 bits', font_size=22, color=SCAFFOLD).next_to(boxes, DOWN, buff=0.3)
        self.play(FadeIn(width), boxes.animate.set_stroke(WHITE, 2), run_time=0.8)
        self.at('held only so many bits')
        self.play(LaggedStart(*[FadeIn(e) for e in extra], lag_ratio=0.1), run_time=1.0)
        self.play(LaggedStart(*[e.animate.shift(DOWN * 1.6).set_opacity(0) for e in extra], lag_ratio=0.12),
                  run_time=2.0, rate_func=rate_functions.ease_in_quad)

        # [V4.9b] a clock counts in tenths; a tiny error builds with every tick
        self.at('so every tick carried')
        self.play(VGroup(caption_top, register, digits, width).animate.scale(0.85).to_edge(UP, buff=0.5), run_time=0.8)
        clock_label = Text('time counted', font_size=22, color=SCAFFOLD).move_to([-3.0, 0.6, 0])
        clock = number(0, decimals=1, font_size=44, color=WHITE).next_to(clock_label, DOWN, buff=0.25)
        unit = Text('seconds', font_size=22, color=SCAFFOLD)
        unit.add_updater(lambda m: m.next_to(clock, RIGHT, buff=0.2, aligned_edge=DOWN))
        err_label = Text('error', font_size=22, color=SCAFFOLD).move_to([1.0, 0.6, 0], aligned_edge=LEFT)
        err_base = Line([1.0, -0.3, 0], [6.4, -0.3, 0], color=GREY_D, stroke_width=2)
        err_bar = Rectangle(width=0.001, height=0.16).set_fill(WHITE, 1).set_stroke(width=0)
        err_bar.move_to(err_base.get_start(), aligned_edge=LEFT)
        self.play(FadeIn(clock_label), FadeIn(clock), FadeIn(unit), FadeIn(err_label), Create(err_base), run_time=0.6)
        self.add(err_bar)
        for k in range(1, 11):
            grown = Rectangle(width=0.012 * k, height=0.16).set_fill(WHITE, 1).set_stroke(width=0)
            grown.move_to(err_base.get_start(), aligned_edge=LEFT)
            self.play(clock.animate.set_value(k / 10), Transform(err_bar, grown), run_time=0.2)
        self.at('After about a hundred hours')
        hours_label = Text('hours running', font_size=22, color=SCAFFOLD).move_to(clock_label)
        hours = number(0, font_size=44, color=WHITE).move_to(clock)
        unit.clear_updaters()
        self.play(FadeOut(clock), FadeOut(unit), ReplacementTransform(clock_label, hours_label), FadeIn(hours), run_time=0.5)
        full = Rectangle(width=5.4, height=0.16).set_fill(WHITE, 1).set_stroke(width=0)
        full.move_to(err_base.get_start(), aligned_edge=LEFT)
        self.play(hours.animate.set_value(100), Transform(err_bar, full), run_time=2.5, rate_func=rate_functions.linear)
        self.at('the clock had drifted')
        drift = Text('about 100 hours of operation → about 0.34 seconds', font_size=26).move_to(DOWN * 2.0)
        self.play(FadeIn(drift), run_time=1.0)
        self.at('enough for the system to look')
        self.play(err_bar.animate.set_fill(GREY_B), run_time=1.0)

        # [V4.9c] a plain text card, held three seconds in silence at the end
        self.at('Twenty-eight soldiers')
        clear(self, 1.0)
        card = VGroup(Text('Dhahran, Saudi Arabia', font_size=34),
                      Text('25 February 1991', font_size=30, color=GREY_B),
                      Text('28 soldiers killed', font_size=30, color=GREY_B)).arrange(DOWN, buff=0.35)
        self.play(FadeIn(card), run_time=1.2)
        self.finish(extra=3.0)


# ---------------------------------------------------------------- 4.10

def recap_icon(kind):
    """A small icon (about 0.9 × 0.7) for each recap item, echoing its segment."""
    if kind == 0:   # ghost balance: a haloed account card
        card = RoundedRectangle(width=0.9, height=0.6, corner_radius=0.08).set_fill(GREY_E, 1).set_stroke(GREY_B, 2)
        halo = card.copy().set_fill(opacity=0).set_stroke(ERROR, 8, opacity=0.4)
        return VGroup(halo, card, code_text('-0.00', font_size=18, color=WHITE).move_to(card))
    if kind == 1:   # a marker jumping past zero
        axis = Line(UP * 0.35, DOWN * 0.35, color=SCAFFOLD)
        zero = Line(LEFT * 0.12, RIGHT * 0.12, color=ERROR, stroke_width=4)
        hop = CurvedArrow(UP * 0.25 + RIGHT * 0.1, DOWN * 0.28 + RIGHT * 0.1, angle=-PI * 0.8, color=MONEY,
                          stroke_width=3, tip_length=0.12)
        return VGroup(axis, zero, hop)
    if kind == 2:   # a tipped balance scale
        scale = balance_scale(width=2.0)
        scale.beam.rotate(-0.25, about_point=scale.beam[2].get_center())
        return scale.scale_to_fit_height(0.7)
    if kind == 3:   # a receipt that doesn't add up
        paper = Rectangle(width=0.55, height=0.72).set_fill(PAPER, 1).set_stroke(width=0)
        lines = VGroup(*[Line(LEFT * 0.18, RIGHT * 0.18, color=GREY, stroke_width=2).shift(UP * (0.2 - 0.11 * k))
                         for k in range(4)]).move_to(paper)
        return VGroup(paper, lines, crossmark(size=0.22).next_to(paper, RIGHT, buff=0.05))
    if kind == 4:   # truncation's funnel and its red bin
        f = funnel(0.7, 0.4, 0.15).set_stroke(width=3)
        b = Rectangle(width=0.5, height=0.22).set_fill(ERROR, 0.8).set_stroke(width=0).next_to(f, DOWN, buff=0.08)
        return VGroup(f, b)
    a = Rectangle(width=0.35, height=0.5).set_fill(PAPER, 1).set_stroke(width=0)
    b = a.copy()
    neq = Text('≠', font_size=24, color=ERROR)
    return VGroup(a, neq, b).arrange(RIGHT, buff=0.08)


class Segment_4_10(Segment):
    """Recap and challenge (q04-05)."""
    EPISODE, SEGMENT = 4, '4.10'

    def construct(self):
        # [V4.10a] the recap column builds, one item per segment, each with its icon
        items = ['ghost balances', 'loops that skip zero', 'reconciliation breaks', "totals that don't foot",
                 'bias from truncation', "reports you can't reproduce"]
        cues = ['A tiny error in a balance', 'Ask whether a float', 'Two sensible systems', "Reports don't foot",
                'Truncation turns noise', 'And a total can depend']
        rows = VGroup()
        for k, item in enumerate(items):
            icon = recap_icon(k)
            icon.move_to([-3.4, 2.9 - 1.1 * k, 0])
            label = Text(item, font_size=30).move_to([-2.5, icon.get_y(), 0], aligned_edge=LEFT)
            rows.add(VGroup(icon, label))
        for row, cue in zip(rows, cues):
            self.at(cue)
            self.play(FadeIn(row[0], scale=0.6), FadeIn(row[1], shift=RIGHT * 0.2), run_time=0.6)
            if row is rows[2]:
                self.play(Indicate(row[0], color=ERROR), run_time=0.6)

        # [V4.10b] the challenge: q04-05's code and its three totals; the hint collapses them
        self.at("Here's the challenge")
        clear(self, 0.5)
        code = code_panel(strip_comments(snippet_lines(Q5, 6, 10)), font_size=22).to_corner(UL, buff=0.35)
        out = output_console(Q5, font_size=22).next_to(code, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeIn(code), FadeIn(out.background), run_time=0.5)
        card = show_qr(self, 'q04-05')
        texts = [after_colon(l) for l in snippet_output(Q5)]
        agree = common_prefix(texts)
        for i in range(3):
            self.play(out.type_line(i, run_time=0.6))
        self.play(*[out.lines[i].chars(len(out.lines[i].source) - len(t) + agree).animate.set_color(ERROR)
                    for i, t in enumerate(texts)], run_time=0.5)
        self.at('Change it so that every amount')
        # The hint, computed here: the same amounts as whole cents, and their exact total.
        amounts = q05_amounts()
        cents = [round(a * 100) for a in amounts]
        exact = 0
        for c in cents:
            exact += c
        hint = VGroup()
        for a, c in zip(amounts[:4], cents[:4]):
            before = code_text(f'{a:.2f}', font_size=24, color=MONEY)
            after = code_text(str(c), font_size=24, color=EXACT)
            hint.add(VGroup(before, after))
        hint_title = Text('amounts as whole cents', font_size=22, color=SCAFFOLD).move_to([4.0, 3.4, 0])
        for k, (before, after) in enumerate(hint):
            before.move_to([4.0, 2.8 - 0.5 * k, 0], aligned_edge=RIGHT).shift(RIGHT * 0.5)
            after.move_to(before, aligned_edge=RIGHT)
        self.play(FadeIn(hint_title), *[FadeIn(h[0]) for h in hint], run_time=0.5)
        hide_qr(self, card, hold=10.4)
        self.play(*[ReplacementTransform(h[0], h[1]) for h in hint], run_time=0.8)
        one = code_text(str(exact), font_size=34, color=EXACT).move_to([0.6, -1.6, 0])
        one_label = Text('cents, in every order', font_size=24, color=EXACT).next_to(one, RIGHT, buff=0.3)
        copies = VGroup(*[out.lines[i].copy() for i in range(3)])
        self.play(*[c.animate.move_to(one).scale(0.6).set_opacity(0) for c in copies], FadeIn(one, scale=0.7), run_time=1.0)
        self.play(FadeIn(one_label), Flash(one, color=EXACT), run_time=0.6)

        # [V4.10c] the QR wall, ten seconds
        self.at('One small hint')
        clear(self, 0.5)
        wall = qr_wall(episode_qr_ids(4))
        self.play(FadeIn(wall), run_time=0.6)
        self.wait(10.0)

        # [V4.10d] the teaser: 0.1 + 0.2 in four fonts and colour schemes, one answer
        self.at('Next time')
        clear(self, 0.5)
        expression = snippet_find('ep05/02-four-costumes.py', '0.1 + 0.2').split('= ', 1)[1]
        answer = output_line(Q0, '0.30000000000000004').split('= ')[-1]
        schemes = [('Menlo', PANEL, WHITE, STORED), ('Courier New', PAPER, INK, '#b5442a'),
                   ('Monaco', '#002b36', '#93a1a1', '#2aa198'), ('Andale Mono', '#282c34', '#abb2bf', '#e5c07b')]
        panels = VGroup()
        for font, bg, fg, accent in schemes:
            left = Text(expression, font=font, font_size=28, color=fg)
            right = Text(answer, font=font, font_size=28, color=accent)
            row = VGroup(left, right).arrange(RIGHT, buff=0.8)
            box = RoundedRectangle(width=8.4, height=0.72, corner_radius=0.1).set_fill(bg, 1).set_stroke(GREY_D, 1)
            row.move_to(box)
            panels.add(VGroup(box, row))
        panels.arrange(DOWN, buff=0.2).move_to(UP * 1.6)
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.3) for p in panels], lag_ratio=0.3), run_time=1.6)
        teaser = end_card('Episode 5', 'Every language, the same answer').next_to(panels, DOWN, buff=0.7)
        self.at('We\'ll ask eight languages')
        self.play(FadeIn(teaser, shift=UP * 0.2), run_time=0.8)
        self.at('And we\'ll find out why')
        self.play(Indicate(teaser[1], color=FOCUS, scale_factor=1.05), run_time=0.8)
        self.finish()

"""Episode 0 · Trailer: Ten cents that don't exist. One Scene per script segment.

    python3 production/render.py 0 [-ql] [segment ...]

Shot ids in comments ([V0.1a] ...) refer to episodes/00-trailer.md. The console lines are
q00-01's recorded output, read from snippets/ep00/01-four-surprises.out.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa: E402,F403

SNIPPET = 'ep00/01-four-surprises.py'


# ---------------------------------------------------------------- 0.1

class Segment_0_1(Segment):
    """Four surprises (q00-01)."""
    EPISODE, SEGMENT = 0, '0.1'

    def construct(self):
        out = output_console(SNIPPET, font_size=26)
        out.to_edge(UP, buff=0.6)
        lines = out.lines
        stage = DOWN * 1.3            # where each surprise is acted out, under the console

        # [V0.1a] the console types the first line; the trailing 4 pulses red
        self.play(FadeIn(out.background))
        self.play(out.type_line(0, run_time=1.4))
        self.at('Zero point three, then fifteen zeros')
        four = lines[0].part('4', occurrence=0)
        self.play(four.animate.set_color(ERROR).scale(1.6), run_time=0.4)
        self.play(four.animate.scale(1 / 1.6), run_time=0.4)

        # [V0.1b] hard cut: cents drop into a jar, faster and faster, to a million
        self.at('Add one cent to a total')
        pot = jar(2.0, 2.2).move_to(stage + LEFT * 1.5)
        count = number(0, font_size=40, color=MONEY, commas=True)
        unit = Text('cents', font_size=32, color=MONEY)
        count.next_to(pot, RIGHT, buff=1.0)
        unit.add_updater(lambda m: m.next_to(count, RIGHT, buff=0.2, aligned_edge=DOWN))
        counter = VGroup(count, unit)
        self.add(pot, counter)
        pile = VGroup()
        drops = [0.5, 0.4, 0.3, 0.2, 0.15, 0.1, 0.08, 0.06, 0.05, 0.05, 0.05, 0.05]
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
        self.add(pile)
        self.play(Indicate(counter, color=MONEY))
        self.at('You have ten thousand dollars and a sliver')
        self.play(out.type_line(1, run_time=1.2))
        sliver = lines[1].chars(lines[1].source.index('10000.') + len('10000.'))
        self.play(sliver.animate.set_color(ERROR), run_time=0.6)

        # [V0.1c] hard cut: $1.15 goes into "× 100, keep the whole part" and 114¢ comes out
        self.at('Turn a dollar fifteen into cents')
        self.remove(pot, counter, pile)
        machine = label_box('× 100, keep the whole part', font_size=26).move_to(stage)
        tag = price_tag('$1.15').next_to(machine, LEFT, buff=0.8)
        self.add(machine, tag)
        self.play(tag.animate.move_to(machine.get_center()).scale(0.4).set_opacity(0), run_time=0.9)
        self.remove(tag)
        self.at('one hundred and fourteen')
        result = Text('114¢', font_size=40, color=MONEY).next_to(machine, RIGHT, buff=0.8)
        self.play(FadeIn(result, shift=RIGHT * 0.6), out.type_line(2, run_time=0.8))
        self.at('A cent just walked away')
        lost = penny(0.3).next_to(result, DOWN, buff=0.25)
        self.play(FadeIn(lost, scale=0.5), run_time=0.3)
        self.play(Rotate(lost, -4 * PI), lost.animate.shift(RIGHT * 5), run_time=1.6, rate_func=rate_functions.ease_in_quad)
        self.remove(lost)

        # [V0.1d] hard cut: round(2.675, 2) prints 2.67, a question mark over the 7; the QR code
        self.at('And round two point six seven five')
        self.remove(machine, result)
        call = code_text('round(2.675, 2)', font_size=44, color=WHITE).move_to(stage + LEFT * 3.2)
        card = qr_card('q00-01')
        self.add(call)
        self.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)
        self.at('Two point six seven.')
        answer = code_text('2.67', font_size=44, color=STORED).next_to(call, RIGHT, buff=0.8)
        self.play(out.type_line(3, run_time=0.8), FadeIn(answer))
        question = Text('?', font_size=48, color=FOCUS).next_to(answer.part('7'), UP, buff=0.1)
        self.play(FadeIn(question, shift=DOWN * 0.2))

        # All four answers together, then the corner code
        self.at('None of these is a bug')
        self.play(FadeOut(VGroup(call, answer, question)))
        self.play(out.animate.move_to(UP * 0.4).scale(1.1))
        self.at('Scan the code in the corner')
        # Never Indicate or recolour a QR code itself: it must stay black on white to scan.
        ring = SurroundingRectangle(card[2], color=FOCUS, buff=0.08)
        self.play(Create(ring))
        self.play(FadeOut(ring), run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 0.2

def tile(number, content, width=2.5, height=2.45):
    """One montage tile: a frame, its episode number, and a little scene inside."""
    frame = RoundedRectangle(width=width, height=height, corner_radius=0.12).set_stroke(GREY_D, 2)
    badge = Text(str(number), font_size=22, color=SCAFFOLD).move_to(frame.get_corner(UL) + RIGHT * 0.22 + DOWN * 0.2)
    content.scale_to_fit_height(min(content.height, height * 0.62))
    if content.width > width * 0.85:
        content.scale_to_fit_width(width * 0.85)
    content.move_to(frame).shift(DOWN * 0.08)
    group = VGroup(frame, badge, content)
    group.content = content
    return group


def mini_float_line():
    """Ticks whose gaps double from left to right: the float line sliding right (episode 2)."""
    axis = Line(LEFT * 2.2, RIGHT * 2.2, color=SCAFFOLD, stroke_width=2)
    xs, x, gap = [], -2.2, 0.06
    while x <= 2.2:
        xs.append(x)
        x += gap
        gap *= 1.25
    ticks = VGroup(*[Line(DOWN * 0.18, UP * 0.18, color=STORED, stroke_width=3).move_to([v, 0, 0]) for v in xs])
    return VGroup(axis, ticks)


def risk_map():
    axes = VGroup(Arrow(ORIGIN, RIGHT * 2.6, buff=0, color=SCAFFOLD, stroke_width=3),
                  Arrow(ORIGIN, UP * 1.8, buff=0, color=SCAFFOLD, stroke_width=3))
    labels = VGroup(Text('how often', font_size=18, color=SCAFFOLD).next_to(axes[0], DOWN, buff=0.08),
                    Text('how visible', font_size=18, color=SCAFFOLD).rotate(PI / 2).next_to(axes[1], LEFT, buff=0.08))
    hot = VGroup(*[Circle(radius=r).set_fill(ERROR, o).set_stroke(width=0) for r, o in ((0.5, 0.2), (0.32, 0.4), (0.16, 0.9))])
    hot.move_to(RIGHT * 2.0 + UP * 0.4)
    return VGroup(axes, labels, hot)


def languages():
    names = VGroup(*[Text(n, font_size=22, color=SCAFFOLD) for n in ('Python', 'JavaScript', 'Java', 'Go', 'Rust')])
    names.arrange(DOWN, buff=0.12, aligned_edge=RIGHT)
    answers = VGroup(*[code_text('0.30000000000000004', font_size=20, color=STORED) for _ in names])
    for name, answer in zip(names, answers):
        answer.next_to(name, RIGHT, buff=0.3)
        answer.align_to(answers[0] if len(answers) else answer, LEFT)
    for answer in answers:
        answer.set_x(names.get_right()[0] + 0.3 + answer.width / 2)
    return VGroup(names, answers)


def rounding_arrows():
    """A value between two neighbours, with eight rounding arrows fanned above and below it."""
    axis = Line(LEFT * 2, RIGHT * 2, color=SCAFFOLD, stroke_width=2)
    ends = VGroup(*[Line(DOWN * 0.15, UP * 0.15, color=SCAFFOLD, stroke_width=3).move_to(x * RIGHT) for x in (-1.6, 1.6)])
    point = Dot(RIGHT * 0.2, color=FOCUS, radius=0.09)
    colours = [STORED, EXACT, FOCUS, ERROR, MONEY, TEAL, PURPLE, GREY_B]
    arrows = VGroup()
    for k in range(8):
        side = ends[k % 2].get_center()
        lift = (0.25 + 0.22 * (k // 2)) * (1 if k < 4 else -1)
        arrows.add(Arrow(point.get_center() + UP * lift * 0.4, side + UP * lift, buff=0.05, color=colours[k],
                         stroke_width=3, max_tip_length_to_length_ratio=0.12))
    return VGroup(axis, ends, arrows, point)


def bill_and_stacks():
    bill = RoundedRectangle(width=2.2, height=1.0, corner_radius=0.08).set_fill('#2f6b3a', 1).set_stroke(EXACT, 2)
    bill.add(Text('$100', font_size=30, color=WHITE).move_to(bill))
    stacks = VGroup(*[VGroup(*[RoundedRectangle(width=0.7, height=0.14, corner_radius=0.03).set_fill('#2f6b3a', 1)
                                .set_stroke(EXACT, 1).shift(UP * 0.1 * i) for i in range(5)]) for _ in range(3)])
    stacks.arrange(RIGHT, buff=0.3)
    labels = VGroup(*[Text('33.33', font_size=18, color=MONEY).next_to(s, DOWN, buff=0.08) for s in stacks])
    stray = penny(0.16).next_to(stacks, RIGHT, buff=0.25).shift(DOWN * 0.2)
    return bill, VGroup(stacks, labels), stray


def checklist():
    items = VGroup(*[Text(t, font_size=22) for t in ('count cents', 'round on purpose', 'carry the currency')])
    items.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
    boxes = VGroup(*[Square(0.28).set_stroke(SCAFFOLD, 2).next_to(i, LEFT, buff=0.2) for i in items])
    ticks = VGroup(*[checkmark(size=0.3).move_to(b) for b in boxes])
    return VGroup(items, boxes), ticks


def cracking_decimal():
    third = Text('1/3', font_size=40, color=FOCUS)
    sign = Text('Decimal', font=MONO, font_size=30, color=STORED).next_to(third, DOWN, buff=0.35)
    crack = VMobject(color=ERROR, stroke_width=4).set_points_as_corners(
        [sign.get_top() + LEFT * 0.1, sign.get_center() + RIGHT * 0.15, sign.get_center() + LEFT * 0.1 + DOWN * 0.1,
         sign.get_bottom() + RIGHT * 0.05])
    return VGroup(third, sign), crack


class Segment_0_2(Segment):
    """The series: title, a montage of the recurring visuals, and the first episode."""
    EPISODE, SEGMENT = 0, '0.2'

    def construct(self):
        # [V0.2a] the title writes itself
        title = Text('Money Problems', font_size=72, weight=BOLD)
        subtitle = Text("why floating point can't count your cents", font_size=30, color=SCAFFOLD)
        heading = VGroup(title, subtitle).arrange(DOWN, buff=0.3)
        self.play(Write(title), run_time=1.6)
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.play(heading.animate.scale(0.55).to_edge(UP, buff=0.35))

        # [V0.2b] the montage: ten tiles, each with its episode number, as the narration names it
        slots = VGroup(*[Rectangle(width=2.5, height=2.45) for _ in range(10)])
        slots.arrange_in_grid(rows=2, cols=5, buff=(0.2, 0.3)).next_to(heading, DOWN, buff=0.4)

        def place(number, content):
            t = tile(number, content).move_to(slots[number - 1])
            self.play(FadeIn(t, scale=0.92), run_time=0.4)
            return t

        # 1 · the cent grid lights its four exact cells
        self.at('cannot store ten cents')
        grid = cent_grid(cell=0.3, font_size=7, show_arrows=False)
        t1 = place(1, grid)
        self.play(*grid.light_exact(), run_time=0.6)

        # 2 · the float line slides right and its ticks spread apart
        self.at('what it stores instead')
        line = mini_float_line()
        t2 = place(2, line)
        self.play(line[1].animate.stretch(1.5, 0, about_point=line[1].get_left()), run_time=0.9)

        # 3 · a risk map with a red hotspot
        self.at('Where that tiny error')
        risk = risk_map()
        t3 = place(3, risk)
        self.play(Indicate(risk[2], color=ERROR, scale_factor=1.3), run_time=0.6)

        # 4 · a ledger whose balance tips by one cent
        self.at('what it costs')
        book = ledger(['100.00'], ['99.99'], width=4.0, font_size=20, headings=('Debits', 'Credits'))
        t4 = place(4, book)
        self.play(tip_scale(book.balance, 0.18), book.right[0].animate.set_color(ERROR), run_time=0.6)

        # 5 · every language prints the same digits
        self.at('nearly every programming language')
        langs = languages()
        place(5, langs)

        # 6 · a number line with eight rounding arrows
        self.at('How rounding really works')
        rounding = rounding_arrows()
        rounding[2].set_opacity(0)
        t6 = place(6, rounding)
        self.play(LaggedStart(*[a.animate.set_opacity(1) for a in rounding[2]], lag_ratio=0.15), run_time=0.9)

        # 7 · a penny sliced into slivers that drop into a hidden jar
        self.at('Office Space got right')
        slices = sliced_penny(10, 0.7)
        hidden = jar(0.9, 0.8, color=GREY_D)
        seven = VGroup(slices, hidden).arrange(RIGHT, buff=0.5)
        t7 = place(7, seven)
        self.play(LaggedStart(*[s.animate.move_to(hidden[0]).scale(0.2).set_opacity(0) for s in slices[:4]],
                              lag_ratio=0.3), run_time=1.0)

        # 8 · a $100 bill splits into three stacks and one stray penny
        self.at('split a bill')
        bill, stacks, stray = bill_and_stacks()
        eight = VGroup(bill, stacks, stray)
        t8 = place(8, VGroup(bill, stacks.copy().set_opacity(0), stray.copy().set_opacity(0)))
        stacks.match_height(t8.content[1]).move_to(t8.content[1])
        stray.match_height(t8.content[2]).move_to(t8.content[2])
        self.play(ReplacementTransform(t8.content[0], stacks), FadeIn(stray, shift=RIGHT * 0.2), run_time=0.8)

        # 9 · a checklist ticks itself
        self.at('handle money correctly')
        items, ticks = checklist()
        nine = VGroup(items, ticks)
        t9 = place(9, VGroup(items, ticks.set_opacity(0)))
        self.play(LaggedStart(*[t.animate.set_opacity(1) for t in ticks], lag_ratio=0.4), run_time=0.9)

        # 10 · a Decimal sign cracks under 1/3
        self.at('the usual fixes still go wrong')
        sign, crack = cracking_decimal()
        t10 = place(10, VGroup(sign, crack.set_opacity(0)))
        self.play(Create(crack.set_opacity(1)), sign[1].animate.set_color(ERROR), run_time=0.6)

        # [V0.2c] the end card: episode 1
        self.at('It starts with one small coin')
        self.play(FadeOut(Group(*self.mobjects)))
        dime = coin('10¢', 0.9)
        card = end_card('Episode 1', "The dime that doesn't exist").next_to(dime, DOWN, buff=0.6)
        VGroup(dime, card).move_to(ORIGIN)
        self.play(FadeIn(dime, scale=0.6), FadeIn(card, shift=UP * 0.2))
        self.at("Why doesn't ten cents exist?")
        outline = DashedVMobject(Circle(radius=0.9, color=MONEY), num_dashes=30).move_to(dime)
        self.play(FadeOut(dime), FadeIn(outline), run_time=1.2)
        self.finish()

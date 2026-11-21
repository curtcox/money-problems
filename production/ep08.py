"""Episode 8 · Splitting the penny. One Scene per script segment.

    python3 production/render.py 8 [-ql] [segment ...]

Shot ids in comments ([V8.1a] ...) refer to episodes/08-splitting-the-penny.md. Code panels
and console lines are read from snippets/ep08/ (q08-01 ... q08-05) and their recorded output;
the few values no snippet prints (exact shares, remainders, sums of whole parts) are computed
below with integer or Fraction arithmetic, and say so where they are.
"""
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa: E402,F403

Q1 = 'ep08/01-three-ways.py'
Q2 = 'ep08/02-largest-remainder.py'
Q3 = 'ep08/03-spreading-a-discount.py'
Q4 = 'ep08/04-twelve-payments.py'
Q5 = 'ep08/05-alabama-paradox.py'

BILL_GREEN = '#2f6b3a'
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
CELL = 0.7                  # one cent, magnified, at the end of every share bar


# ---------------------------------------------------------------- local helpers

def dollars(cents):
    """Whole cents as dollars, the way q08-02 prints them (for values computed in a scene)."""
    return f'${cents // 100:,}.{cents % 100:02d}'


def bracket_items(line, occurrence=0):
    """The items of the n-th [...] list printed in an output line, as strings."""
    groups = re.findall(r'\[([^\]]*)\]', line)
    return [s.strip().strip("'") for s in groups[occurrence].split(',')]


def show_card(scene, qr_id):
    card = qr_card(qr_id)
    scene.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)
    card.shown_at = scene.renderer.time
    return card


def hide_card(scene, card, hold=8.0):
    """Fade a QR card out, but never before it has been fully visible for `hold` seconds."""
    remaining = card.shown_at + hold - scene.renderer.time
    if remaining > 0:
        scene.wait(remaining)
    scene.play(FadeOut(card), run_time=0.5)


def lines_highlight(code, first, last, color=FOCUS):
    """line_highlight stretched over code lines first..last."""
    box = line_highlight(code, first, color)
    if last > first:
        bottom = line_highlight(code, last, color)
        top_y, bottom_y = box.get_top()[1], bottom.get_bottom()[1]
        box.stretch_to_fit_height(top_y - bottom_y).move_to([box.get_x(), (top_y + bottom_y) / 2, 0])
    return box


def move_highlight(scene, current, target, run_time=0.5):
    if current is None:
        scene.play(Create(target), run_time=run_time)
    else:
        scene.play(Transform(current, target), run_time=run_time)
        return current
    return target


def bill(text='$100.00', width=2.8, height=1.3):
    """A plain bill: a green rectangle with its amount in text (no real banknote design)."""
    body = RoundedRectangle(width=width, height=height, corner_radius=0.1).set_fill(BILL_GREEN, 1).set_stroke(MONEY, 3)
    inner = RoundedRectangle(width=width - 0.25, height=height - 0.25, corner_radius=0.06).set_stroke(EXACT, 1.5, 0.6)
    label = Text(text, font_size=40, color=MONEY, weight=BOLD).move_to(body)
    return VGroup(body, inner, label)


def figure(letter):
    """A plain person: a circle head, a body and a name tag. No face."""
    body = RoundedRectangle(width=1.1, height=0.75, corner_radius=0.32).set_fill(GREY_E, 1).set_stroke(SCAFFOLD, 3)
    head = Circle(radius=0.33).set_fill(GREY_E, 1).set_stroke(SCAFFOLD, 3).next_to(body, UP, buff=0.08)
    tag = RoundedRectangle(width=0.46, height=0.36, corner_radius=0.05).set_fill(WHITE, 1).set_stroke(width=0)
    tag.move_to(body).shift(UP * 0.05)
    name = Text(letter, font_size=22, color=BLACK, weight=BOLD).move_to(tag)
    return VGroup(body, head, tag, name)


def money_stack(label, sheets=5, width=1.2, font_size=26):
    """A gold stack of notes with its amount under it."""
    dark = interpolate_color(ManimColor(MONEY), BLACK, 0.45)
    pile = VGroup(*[RoundedRectangle(width=width, height=0.16, corner_radius=0.03).set_fill(MONEY, 1)
                    .set_stroke(dark, 1.5).shift(UP * 0.11 * i) for i in range(sheets)])
    text = Text(label, font_size=font_size, color=MONEY).next_to(pile, DOWN, buff=0.12)
    group = VGroup(pile, text)
    group.pile, group.label = pile, text
    return group


def start_spin(mob, speed=1.8):
    """Spin a coin about its vertical axis (squash its width with |cos|) until stop_spin."""
    base = mob.copy()
    state = {'t': 0.0}

    def update(m, dt):
        state['t'] += dt
        squash = max(abs(math.cos(state['t'] * speed)), 0.05)
        m.become(base.copy().stretch(squash, 0).move_to(m.get_center()))

    mob.spin_base = base
    mob.add_updater(update)


def stop_spin(mob):
    mob.clear_updaters()
    mob.become(mob.spin_base.copy().move_to(mob.get_center()))


class ShareBar(VGroup):
    """One person's share: GOLD whole cents, a YELLOW sliver for the fraction of a cent left
    over (the last cent is magnified to CELL wide), and a YELLOW outline round the exact share."""

    def __init__(self, name, width, frac, label='', height=0.55, cell=CELL, name_size=24, amount_size=24):
        super().__init__()
        self.cell = cell
        sliver_w = float(Fraction(frac)) * cell
        self.gold = Rectangle(width=width, height=height).set_fill(MONEY, 0.9).set_stroke(width=0)
        self.sliver = Rectangle(width=max(sliver_w, 0.001), height=height).set_fill(FOCUS, 0.55 if sliver_w else 0)
        self.sliver.set_stroke(width=0).next_to(self.gold, RIGHT, buff=0)
        self.outline = Rectangle(width=width + sliver_w, height=height + 0.08).set_stroke(FOCUS, 3)
        self.outline.align_to(self.gold, LEFT).set_y(self.gold.get_y())
        if label.strip():
            self.amount = Text(label, font_size=amount_size, color=BLACK, weight=BOLD).move_to(self.gold)
        else:
            self.amount = VectorizedPoint(self.gold.get_center())
        self.name = Text(name, font_size=name_size, color=SCAFFOLD).next_to(self.gold, LEFT, buff=0.3)
        self.add(self.gold, self.sliver, self.outline, self.amount, self.name)

    def place(self, left_point):
        """Put the bar's left edge (not its name) at a point."""
        return self.shift(np.array(left_point, dtype=float) - self.gold.get_left())


def drop_cent(scene, bar, new_label, cent=None, run_time=0.8, label_size=24):
    """A penny falls onto the bar's next cent; the gold grows by one cent and relabels."""
    spot = bar.gold.get_right() + RIGHT * bar.cell / 2
    if cent is None:
        cent = penny(0.26).move_to(spot + UP * 1.4)
        scene.add(cent)
    scene.play(cent.animate.move_to(spot), run_time=run_time, rate_func=rate_functions.ease_in_quad)
    width = bar.gold.width + bar.cell
    centre = bar.gold.get_left() + RIGHT * width / 2
    label = Text(new_label, font_size=label_size, color=BLACK, weight=BOLD).move_to(centre)
    scene.play(bar.gold.animate.stretch_to_fit_width(width, about_edge=LEFT),
               bar.sliver.animate.set_fill(opacity=0), FadeOut(cent, scale=0.4),
               Transform(bar.amount, label), run_time=0.6)


def calendar(width=1.0, height=1.0, gap=0.06, name_size=18):
    """A strip of twelve month boxes; `strip[i].box`, `strip[i].slot` (where an amount goes)."""
    strip = VGroup()
    for m in MONTHS:
        box = RoundedRectangle(width=width, height=height, corner_radius=0.06).set_stroke(GREY_D, 2).set_fill(GREY_E, 0.5)
        name = Text(m, font_size=name_size, color=SCAFFOLD).move_to(box.get_top() + DOWN * 0.2)
        month = VGroup(box, name)
        month.box = box
        strip.add(month)
    strip.arrange(RIGHT, buff=gap)
    return strip


def slot(month):
    return month.box.get_center() + DOWN * 0.14 * month.box.height


def amount_in(month, text, color=MONEY, font_size=18):
    return code_text(text, font_size=font_size, color=color).move_to(slot(month))


def cent_pile_spot(base, k, cols=3, pitch=0.7):
    """Where the k-th penny of a pile sits: rows of three, growing downward from base."""
    row, col = divmod(k, cols)
    return base + RIGHT * (col - (cols - 1) / 2) * pitch + DOWN * row * pitch


def alabama_outline(height=4.2):
    """A plain outline of the state of Alabama (approximate, from a handful of border points)."""
    lon_lat = [(-88.20, 35.00), (-85.61, 34.98), (-85.39, 33.90), (-85.18, 32.86), (-84.96, 32.42),
               (-85.06, 31.98), (-85.05, 31.60), (-85.00, 31.00), (-87.60, 31.00), (-87.43, 30.48),
               (-87.52, 30.28), (-87.90, 30.25), (-88.40, 30.38), (-88.47, 31.89)]
    squash = math.cos(math.radians(32.7))
    points = [np.array([lon * squash, lat, 0]) for lon, lat in lon_lat]
    shape = Polygon(*points).set_stroke(SCAFFOLD, 3).set_fill(GREY_E, 0.6)
    return shape.scale_to_fit_height(height)


# ---------------------------------------------------------------- 8.1

class Segment_8_1(Segment):
    """Cold open: a hundred dollars, three ways (q08-01)."""
    EPISODE, SEGMENT = 8, '8.1'

    def construct(self):
        out = snippet_output(Q1)
        each = output_line(Q1, 'each pays').split('=')[1].strip()          # 33.33

        # [V8.1a] black canvas: the $100.00 bill in the centre, three plain figures below it
        note = bill().move_to(UP * 1.4)
        people = VGroup(*[figure(c) for c in 'ABC']).arrange(RIGHT, buff=2.4).move_to(DOWN * 2.3)
        self.play(FadeIn(note, scale=0.9), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in people], lag_ratio=0.25), run_time=1.2)

        # [V8.1b] the bill splits into three gold stacks of $33.33 that slide to the figures
        self.at('Easy: everyone pays a third.')
        stacks = VGroup(*[money_stack('$' + each) for _ in people])
        for stack, person in zip(stacks, people):
            stack.next_to(person, UP, buff=0.3)
        starts = [s.copy().scale(0.5).move_to(note) for s in stacks]
        cent = penny(0.45).move_to(note)
        self.play(*[Transform(s0, s) for s0, s in zip(starts, stacks)], FadeOut(note, scale=0.6),
                  run_time=1.2, rate_func=rate_functions.ease_out_cubic)
        self.remove(*starts)
        self.add(stacks)

        # [V8.1c] a penny remains where the bill was, spinning slowly, a red question mark above
        question = Text('?', font_size=60, color=ERROR, weight=BOLD).next_to(cent, UP, buff=0.2)
        self.play(FadeIn(cent, scale=0.4), run_time=0.5)
        start_spin(cent)
        self.play(FadeIn(question, shift=DOWN * 0.2), run_time=0.5)

        # [V8.1d] code panel left, console right; the scene steps down to make room; QR q08-01
        self.at('Ask Python for a third')
        stop_spin(cent)
        scene_group = VGroup(people, stacks, cent, question)
        code = code_panel(snippet_lines(Q1, 4, 7), font_size=20).to_corner(UL, buff=0.35)
        con = output_console(Q1, font_size=18).to_corner(UR, buff=0.35)
        self.play(scene_group.animate.scale(0.8).move_to([-2.4, -1.35, 0]),
                  FadeIn(code, shift=RIGHT * 0.3), FadeIn(con.background, shift=LEFT * 0.3), run_time=1.0)
        start_spin(cent)
        card = show_card(self, 'q08-01')

        self.at('and it gives you')
        mark = line_highlight(code, 2)
        self.play(Create(mark), con.type_line(0, run_time=1.2))
        self.at('and then a six at the end')
        tail = con.lines[0].glyphs[-1]
        self.play(tail.animate.set_color(ERROR).scale(1.5), run_time=0.4)
        self.play(tail.animate.scale(1 / 1.5), run_time=0.4)

        self.at('So round it to cents')
        self.play(Transform(mark, line_highlight(code, 3)), con.type_line(1, run_time=0.8))

        self.at('Now add the three shares back up.')
        self.play(FadeOut(mark), run_time=0.4)
        self.play(*[Indicate(s.label, color=MONEY, scale_factor=1.15) for s in stacks], run_time=0.8)
        self.at('Ninety-nine ninety-nine.')
        self.play(con.type_line(2, run_time=0.8))
        self.play(con.lines[2].part('99.99').animate.set_color(ERROR), run_time=0.4)
        self.at('A cent is missing.')
        self.play(con.type_line(3, run_time=0.8))
        self.play(con.lines[3].part('0.01').animate.set_color(ERROR), Indicate(question, color=ERROR), run_time=0.6)

        # [V8.1e] the last line prints in green; the penny stops spinning and is labelled
        self.at('Count in cents')
        con.lines[4].set_color(EXACT)
        self.play(con.type_line(4, run_time=1.2))
        hide_card(self, card)
        self.at('That last cent has to go somewhere.')
        stop_spin(cent)
        self.play(scene_group.animate.scale(1.12).move_to([-0.6, -1.25, 0]), run_time=0.8)
        label = Text('someone has to take it', font_size=26, color=FOCUS).next_to(cent, RIGHT, buff=0.3)
        self.play(FadeOut(question), FadeIn(label, shift=LEFT * 0.2), cent.animate.scale(1.2), run_time=0.8)

        # The extra cent lands on one stack: that person pays $33.34 (q08-02's first share)
        self.at('Someone pays thirty-three thirty-four.')
        first = bracket_items(output_line(Q2, '[1, 1, 1]'), 1)[0]          # $33.34
        target = stacks[0].pile.get_top() + UP * 0.25
        new_label = Text(first, font_size=26, color=FOCUS).scale(0.8).move_to(stacks[0].label)
        self.play(FadeOut(label), cent.animate.scale(0.5).move_to(target), run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
        self.play(Transform(stacks[0].label, new_label), run_time=0.6)
        self.at('and how you decide')
        self.play(Circumscribe(VGroup(stacks, people), color=FOCUS, buff=0.15), run_time=1.5)
        self.finish()


# ---------------------------------------------------------------- 8.2

class Segment_8_2(Segment):
    """The conservation law: the parts must add up to the whole."""
    EPISODE, SEGMENT = 8, '8.2'

    def construct(self):
        each = '$' + output_line(Q1, 'each pays').split('=')[1].strip()            # $33.33
        short = '$' + output_line(Q1, 'three shares').split('=')[1].strip()        # $99.99
        gap = '$' + output_line(Q1, 'missing').split('=')[1].strip()               # $0.01

        # [V8.2a] the ledger "Dinner": $100.00 credit, three $33.33 debits; the scale tips
        book = ledger([('A ', each), ('B ', each), ('C ', each), ('rounding ', gap)], [('bill ', '$100.00')],
                      totals=('$100.00', '$100.00'), width=8.0, font_size=24)
        title = Text('Dinner', font_size=34, weight=BOLD).next_to(book.headings, UP, buff=0.35).align_to(book.frame, LEFT)
        whole = VGroup(book, title)
        whole.scale_to_fit_height(6.6).move_to(DOWN * 0.3)
        cols = len(book.totals.left.source)
        low = MonoLine(short.rjust(cols), font_size=24, color=MONEY).scale(book.totals.left.cell / MonoLine('M', font_size=24).cell)
        low.set_anchor(book.totals.left.anchor())
        rounding = book.left[3]
        rounding.set_opacity(0)
        book.totals.left.set_opacity(0)
        pieces = VGroup(book.frame, book.headings, book.balance, title)
        self.play(FadeIn(pieces), run_time=0.8)
        self.play(FadeIn(book.right[0], shift=LEFT * 0.3), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(l, shift=DOWN * 0.3) for l in book.left[:3]], lag_ratio=0.4), run_time=1.2)
        self.play(FadeIn(book.totals[0]), FadeIn(low), FadeIn(book.totals.right), run_time=0.6)
        gap_label = Text(f'gap {gap}', font_size=28, color=ERROR).next_to(low, LEFT, buff=0.6)
        self.play(tip_scale(book.balance, -0.16), FadeIn(gap_label, shift=RIGHT * 0.2), low.animate.set_color(ERROR), run_time=0.8)

        # [V8.2c] the rule writes itself in large type, beside the ledger
        self.at('The parts must add up to the whole.')
        rule = VGroup(Text('The parts must add up', font_size=46, weight=BOLD),
                      Text('to the whole.', font_size=46, weight=BOLD),
                      Text('Exactly.', font_size=58, weight=BOLD, color=FOCUS)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        everything = VGroup(whole, low, gap_label)
        self.play(everything.animate.scale(0.62).to_edge(LEFT, buff=0.4), run_time=0.8)
        rule.next_to(everything, RIGHT, buff=0.7)
        fit(rule, 6.8 - rule.get_left()[0]).next_to(everything, RIGHT, buff=0.7)
        self.play(Write(rule[0]), run_time=1.2)
        self.play(Write(rule[1]), run_time=0.8)
        self.at('Exactly.')
        self.play(FadeIn(rule[2], scale=1.3), run_time=0.6)
        self.at('Not to within a cent')
        self.play(Circumscribe(rule[2], color=FOCUS), run_time=1.0)

        # the rule becomes a banner; the ledger comes back as a conservation law
        self.at('Think of it as a conservation law.')
        banner = Text('The parts must add up to the whole. Exactly.', font_size=30, weight=BOLD).to_edge(UP, buff=0.3)
        banner[-8:].set_color(FOCUS)
        K = 0.92                    # the ledger's size from here on, relative to where it started
        self.play(ReplacementTransform(rule, banner), everything.animate.scale(K / 0.62).move_to(DOWN * 0.45),
                  run_time=1.0)
        self.at('A hundred dollars came in')
        self.play(Circumscribe(book.right[0], color=EXACT, buff=0.08), run_time=1.0)
        self.at('must go out')
        self.play(Circumscribe(VGroup(*book.left[:3]), color=FOCUS, buff=0.08), run_time=1.0)
        self.at('If the parts come to ninety-nine')
        self.play(Indicate(low, color=ERROR), Indicate(gap_label, color=ERROR), run_time=0.9)
        self.at('a cent has vanished')
        self.play(Wiggle(gap_label), run_time=0.8)

        # what if the parts came to a cent too many: the scale tips the other way
        self.at('If they come to a hundred dollars and one cent')
        over = MonoLine('$100.01'.rjust(cols), font_size=24, color=ERROR).scale(low.cell / MonoLine('M', font_size=24).cell)
        over.set_anchor(low.anchor())
        plus = Text(f'extra {gap}', font_size=28, color=ERROR).scale(K).move_to(gap_label, aligned_edge=RIGHT)
        self.play(ReplacementTransform(low, over), ReplacementTransform(gap_label, plus), tip_scale(book.balance, 0.32), run_time=1.0)
        self.at('and someone has been charged for it')
        self.play(Indicate(plus, color=ERROR), run_time=0.8)

        # [V8.2b] back to $99.99; a fourth line, "rounding $0.01", is written in by hand: the scale levels
        self.at('Accountants have a name')
        low2 = low.copy().set_color(ERROR)
        gap2 = Text(f'gap {gap}', font_size=28, color=ERROR).scale(K).move_to(plus, aligned_edge=RIGHT)
        self.play(ReplacementTransform(over, low2), ReplacementTransform(plus, gap2), tip_scale(book.balance, -0.32), run_time=1.0)
        self.at('they balance.')
        rounding.set_opacity(1).set_color(EXACT)
        self.play(Write(rounding), run_time=1.0)
        book.totals.left.set_opacity(1).set_color(EXACT)
        self.play(ReplacementTransform(low2, book.totals.left), FadeOut(gap2), tip_scale(book.balance, 0.16),
                  book.balance.animate.set_color(EXACT), book.totals.right.animate.set_color(EXACT), run_time=1.0)

        # somebody will spend an afternoon looking for a lost cent: a magnifier sweeps the books
        self.at('will spend an afternoon')
        glass = VGroup(Circle(radius=0.45).set_stroke(SCAFFOLD, 5).set_fill(BLUE_E, 0.2),
                       Line(ORIGIN, DR * 0.55, stroke_width=9, color=SCAFFOLD))
        glass[1].next_to(glass[0], DR, buff=-0.12)
        path_start = book.left[0].get_left() + LEFT * 0.4
        glass.move_to(path_start)
        self.play(FadeIn(glass), run_time=0.3)
        self.play(glass.animate.move_to(book.left[2].get_right() + RIGHT * 0.2), run_time=1.6, rate_func=there_and_back_with_pause)
        self.play(FadeOut(glass), run_time=0.3)

        # [V8.2d] three wholes split into parts; rounding each part alone lets errors pile up
        self.at('Notice that rounding each share')
        self.play(FadeOut(VGroup(book, title)), FadeOut(banner), run_time=0.6)
        examples = [('payroll total', 'paycheck', 4), ('restaurant bill', 'card', 3), ('tax total', 'line', 4)]
        rows = VGroup()
        for name, part, n in examples:
            whole_box = label_box(name, color=MONEY, font_size=24, fill=MONEY)
            arrow = Arrow(LEFT * 0.5, RIGHT * 0.5, color=SCAFFOLD, buff=0)
            parts = VGroup(*[label_box(part, color=SCAFFOLD, font_size=22) for _ in range(n)]).arrange(RIGHT, buff=0.2)
            row = VGroup(whole_box, arrow, parts).arrange(RIGHT, buff=0.3)
            row.whole, row.arrow, row.parts = whole_box, arrow, parts
            rows.add(row)
        rows.arrange(DOWN, buff=0.8, aligned_edge=LEFT)
        fit(rows, 11.0).move_to(LEFT * 0.7 + UP * 0.3)
        for row, phrase in zip(rows, ('Notice that rounding', 'Each share is rounded', 'with no idea what happened')):
            self.at(phrase)
            self.play(FadeIn(row.whole, shift=RIGHT * 0.2), run_time=0.4)
            self.play(GrowArrow(row.arrow),
                      LaggedStart(*[TransformFromCopy(row.whole, p) for p in row.parts], lag_ratio=0.15), run_time=0.9)

        # each part is rounded on its own: a tiny error arrow on each, up or down at random
        self.at('the little rounding errors')
        pattern = [1, -1, 1, 1, -1, 1, 1, 1, 1, -1, 1]
        nudges = VGroup()
        k = 0
        for row in rows:
            for p in row.parts:
                d = pattern[k % len(pattern)]
                k += 1
                arrow = Arrow(ORIGIN, UP * 0.35 * d, buff=0, color=STORED if d > 0 else ERROR, stroke_width=4,
                              max_tip_length_to_length_ratio=0.4).next_to(p, UP if d > 0 else DOWN, buff=0.04)
                nudges.add(arrow)
        self.play(LaggedStart(*[GrowArrow(a) for a in nudges], lag_ratio=0.08), run_time=1.6)
        misses = VGroup(*[Text('≠ whole', font_size=24, color=ERROR).next_to(row, RIGHT, buff=0.3) for row in rows])
        self.play(LaggedStart(*[FadeIn(m, shift=LEFT * 0.2) for m in misses], lag_ratio=0.3), run_time=1.0)

        # decided together: each row's parts are bound into one decision, and they add up
        self.at('the shares have to be')
        binders = VGroup(*[SurroundingRectangle(row.parts, color=EXACT, buff=0.12, corner_radius=0.1) for row in rows])
        oks = VGroup(*[Text('= whole', font_size=24, color=EXACT).move_to(m, aligned_edge=LEFT) for m in misses])
        self.play(FadeOut(nudges), Create(binders), ReplacementTransform(misses, oks), run_time=1.0)
        self.finish()


# ---------------------------------------------------------------- 8.3

class Segment_8_3(Segment):
    """Largest remainder (q08-02)."""
    EPISODE, SEGMENT = 8, '8.3'

    def construct(self):
        total, weights = 10_000, [1, 1, 1]          # the first split q08-02 runs

        # [V8.3a] the allocate function; QR q08-02
        code = code_panel(snippet_lines(Q2, 5, 15), font_size=18).to_edge(UP, buff=0.2)
        self.play(FadeIn(code, shift=DOWN * 0.2), run_time=0.8)
        card = show_card(self, 'q08-02')

        self.at('First, work in whole cents')
        cents = Text('$100.00', font_size=44, color=MONEY).move_to([-3.6, -1.3, 0])
        cents_after = Text(f'{total:,}¢', font_size=44, color=MONEY).move_to(cents)
        self.play(FadeIn(cents, shift=UP * 0.2), run_time=0.5)
        self.play(Transform(cents, cents_after), run_time=0.8)
        self.at('An even three-way split')
        weight_text = Text('weights  1 : 1 : 1', font_size=34).next_to(cents, DOWN, buff=0.5)
        mark = line_highlight(code, 0)
        self.play(FadeIn(weight_text, shift=UP * 0.2), Create(mark), run_time=0.7)

        # [V8.3b] three bars: the exact share is a yellow outline; whole cents fill gold, a third remains
        self.at('For each person')
        hide_card(self, card)
        exact = [Fraction(total * w, sum(weights)) for w in weights]            # computed: 3333 1/3
        floors = [divmod(total * w, sum(weights)) for w in weights]               # computed: (3333, 1)
        bars = VGroup()
        for i, (letter, (share, rem)) in enumerate(zip('ABC', floors)):
            bar = ShareBar(letter, 5.4, Fraction(rem, sum(weights)), f'{share}¢')
            bar.place([-6.0, -0.75 - 0.95 * i, 0])
            bars.add(bar)
        self.play(FadeOut(cents), FadeOut(weight_text), Transform(mark, line_highlight(code, 4)),
                  LaggedStart(*[FadeIn(b.name) for b in bars], lag_ratio=0.2), run_time=0.8)
        self.play(LaggedStart(*[Create(b.outline) for b in bars], lag_ratio=0.2), run_time=1.0)
        self.at('keep only the whole')
        self.play(LaggedStart(*[GrowFromEdge(b.gold, LEFT) for b in bars], lag_ratio=0.2), run_time=1.2)
        self.play(*[FadeIn(b.amount) for b in bars], *[FadeIn(b.sliver) for b in bars], run_time=0.6)
        thirds = VGroup(*[Text(f'+ {Fraction(r, sum(weights))}¢', font_size=24, color=FOCUS)
                          .next_to(b.outline, RIGHT, buff=0.25) for b, (_, r) in zip(bars, floors)])
        head = Text('remainder', font_size=22, color=FOCUS).next_to(thirds[0], UP, buff=0.3).align_to(thirds[0], LEFT)
        self.at('Divmod does that')
        self.play(LaggedStart(*[FadeIn(t, shift=LEFT * 0.2) for t in thirds], lag_ratio=0.2), FadeIn(head), run_time=0.9)
        self.at('the whole part and the remainder')
        self.play(*[Indicate(b.gold, color=MONEY, scale_factor=1.03) for b in bars], run_time=0.7)
        self.play(*[Indicate(b.sliver, color=FOCUS, scale_factor=1.3) for b in bars], run_time=0.7)

        # "Ten thousand cents times one, divided by three": computed with divmod in this scene
        self.at('Ten thousand cents times one')
        share0, rem0 = floors[0]
        sum_line = Text(f'{total:,} × 1 ÷ 3  =  {share0} remainder {rem0}', font_size=28).move_to([-2.4, -3.45, 0])
        sum_line[-len(f'remainder{rem0}'):].set_color(FOCUS)
        self.play(Write(sum_line), run_time=1.4)

        # [V8.3c] add up the whole parts: one cent is left over, a single penny
        self.at('So add up the whole parts')
        self.play(Transform(mark, line_highlight(code, 7)), run_time=0.5)
        wholes = sum(s for s, _ in floors)                                     # computed: 9999
        left_line = Text(f'{total:,} − {wholes:,}  =  {total - wholes}¢ left over', font_size=28).move_to(sum_line)
        self.play(ReplacementTransform(sum_line, left_line), run_time=0.8)
        self.at('Here, one.')
        pool = penny(0.38).move_to([4.0, -0.65, 0])
        pool_label = Text('left over', font_size=22, color=MONEY).next_to(pool, RIGHT, buff=0.2)
        self.play(FadeIn(pool, scale=0.4), FadeIn(pool_label), run_time=0.6)

        # the remainders line up, biggest first; ties broken by position
        self.at('Now hand out the leftover cents')
        self.play(Transform(mark, lines_highlight(code, 8, 9)), run_time=0.5)
        row = VGroup(*[b.sliver.copy() for b in bars])
        targets = VGroup(*[Rectangle(width=0.62, height=1.0).set_fill(FOCUS, 0.55).set_stroke(FOCUS, 2) for _ in bars])
        targets.arrange(RIGHT, buff=0.55).move_to([3.4, -2.35, 0])
        tags = VGroup(*[Text(l, font_size=22, color=SCAFFOLD).next_to(t, UP, buff=0.12) for l, t in zip('ABC', targets)])
        self.play(*[Transform(s, t) for s, t in zip(row, targets)], run_time=1.2)
        self.play(FadeIn(tags), run_time=0.4)
        self.at('the ones who were rounded down')
        self.play(Indicate(row, color=FOCUS, scale_factor=1.08), run_time=0.8)
        self.at('If remainders tie')
        self.play(Transform(mark, line_highlight(code, 6)), run_time=0.5)
        order = VGroup(*[Text(o, font_size=22, color=FOCUS).next_to(t, DOWN, buff=0.15)
                         for o, t in zip(('1st', '2nd', '3rd'), targets)])
        self.play(LaggedStart(*[FadeIn(o, shift=UP * 0.15) for o in order], lag_ratio=0.4), run_time=1.2)
        self.at('so the answer is the same')
        winner = SurroundingRectangle(VGroup(row[0], order[0], tags[0]), color=FOCUS, buff=0.1)
        self.play(Create(winner), run_time=0.5)
        self.play(FadeOut(pool_label), FadeOut(thirds[0]), run_time=0.3)
        drop_cent(self, bars[0], f'{floors[0][0] + 1}¢', cent=pool, run_time=1.0)

        # [V8.3d] the result: the console prints the first line; its sum glows green
        self.at('And the result')
        con = output_console(Q2, font_size=20).to_edge(UP, buff=0.5)
        self.play(FadeOut(code), FadeOut(mark), FadeOut(VGroup(row, tags, order, winner, left_line)), run_time=0.6)
        self.play(FadeIn(con.background), run_time=0.4)
        self.play(con.type_line(0, run_time=1.4))
        self.at('Sum: exactly one hundred dollars.')
        self.play(con.part(0, 'sum $100.00').animate.set_color(EXACT), *[b.outline.animate.set_stroke(EXACT) for b in bars],
                  run_time=0.6)
        self.at('because we handed out precisely')
        self.play(Circumscribe(con.part(0, 'sum $100.00'), color=EXACT), run_time=1.2)
        self.finish()


# ---------------------------------------------------------------- 8.4

class Segment_8_4(Segment):
    """Weights and percentages (q08-02, second and third lines)."""
    EPISODE, SEGMENT = 8, '8.4'

    def construct(self):
        con = output_console(Q2, font_size=18).to_edge(UP, buff=0.3)
        lines = snippet_output(Q2)
        left = [-4.4, 0, 0]
        ys = [0.35, -1.05, -2.45]

        # Start where 8.3 ended: three equal bars, the first one a cent fuller
        first = [divmod(10_000 * w, 3) for w in (1, 1, 1)]                    # computed: 3333 r 1
        start = VGroup()
        for i, (letter, (share, _)) in enumerate(zip('ABC', first)):
            extra = 1 if i == 0 else 0
            bar = ShareBar(letter, 5.4 + CELL * extra, 0, f'{share + extra}¢', height=0.75).place([left[0], ys[i], 0])
            bar.outline.set_stroke(EXACT)
            start.add(bar)
        self.add(con.background, *con.lines[0].glyphs, start)
        con.part(0, 'sum $100.00').set_color(EXACT)

        # [V8.4a] the bars become 1 : 2 : 3, "shares held", under a $1,000.00 total
        self.at('Suppose three partners')
        weights, total = [1, 2, 3], 100_000
        floors = [divmod(total * w, sum(weights)) for w in weights]            # computed: (16666, 4) ...
        unit = 7.6 / max(weights)
        bars = VGroup()
        for i, (w, (share, rem)) in enumerate(zip(weights, floors)):
            bar = ShareBar(f'{w} share' + ('s' if w > 1 else ''), unit * w - CELL * 0.5, Fraction(rem, sum(weights)),
                           f'{share}¢', height=0.75, name_size=26).place([left[0], ys[i], 0])
            bars.add(bar)
        header = Text('shares held', font_size=24, color=FOCUS).next_to(bars[0].name, UP, buff=0.45).align_to(bars[0].name, LEFT)
        pot = Text('$1,000.00', font_size=44, color=MONEY).move_to([0.6, 1.55, 0])
        for bar in bars:
            bar.outline.set_stroke(opacity=0)
            bar.sliver.set_fill(opacity=0)
            bar.amount.set_opacity(0)
        self.play(*[ReplacementTransform(a, b) for a, b in zip(start, bars)], FadeIn(header), FadeIn(pot, shift=DOWN * 0.2),
                  run_time=1.4)
        self.at('a thousand dollars of profit')
        self.play(Indicate(pot, color=MONEY), run_time=0.8)

        # exact shares: a sixth, two sixths, three sixths; the 1/6 bar keeps a sliver of 4/6¢
        self.at('Their exact shares are')
        sixths = VGroup(*[Text(f'{w}/{sum(weights)}', font_size=26, color=FOCUS).next_to(b.gold, RIGHT, buff=0.95)
                          for w, b in zip(weights, bars)])
        self.play(LaggedStart(*[FadeIn(s, shift=LEFT * 0.2) for s in sixths], lag_ratio=0.4), run_time=1.2)
        rems = VGroup(*[Text(f'+ {r}/{sum(weights)}¢' if r else '+ 0', font_size=22, color=FOCUS)
                        .next_to(s, RIGHT, buff=0.3) for s, (_, r) in zip(sixths, floors)])
        self.play(*[b.outline.animate.set_stroke(opacity=1) for b in bars], *[b.sliver.animate.set_fill(opacity=0.55) for b in bars],
                  *[b.amount.animate.set_opacity(1) for b in bars], FadeIn(rems), run_time=1.0)

        # [V8.4b] the second output line; one penny drops on the first bar; the amounts land
        self.at('Largest remainder gives')
        self.play(con.type_line(1, run_time=1.4))
        drop_cent(self, bars[0], f'{floors[0][0] + 1}¢', run_time=0.7)
        amounts = bracket_items(lines[1], 1)                                       # $166.67 $333.33 $500.00
        self.at('hundred sixty-six sixty-seven')
        landed = [Text(a, font_size=24, color=BLACK, weight=BOLD).move_to(b.gold) for a, b in zip(amounts, bars)]
        self.play(LaggedStart(*[Transform(b.amount, t) for b, t in zip(bars, landed)], lag_ratio=0.5), run_time=2.0)
        self.at('Sum: a thousand dollars.')
        self.play(con.part(1, 'sum $1,000.00').animate.set_color(EXACT), run_time=0.6)

        # [V8.4c] percentages: 33.3 %, 33.3 %, 33.4 %, written as weights 333, 333, 334, on $10.00
        self.at('Percentages work too.')
        pweights = [int(w) for w in bracket_items(lines[2], 0)]                    # 333 333 334
        pfloor = [divmod(1_000 * w, sum(pweights)) for w in pweights]             # computed: exact, no remainder
        unit = 7.6 / max(pweights)
        pbars = VGroup()
        for i, (w, (share, rem)) in enumerate(zip(pweights, pfloor)):
            bar = ShareBar(f'{w / 10:.1f} %', unit * w, Fraction(rem, sum(pweights)), ' ', height=0.75,
                           name_size=26).place([left[0], ys[i], 0])
            pbars.add(bar)
        self.play(FadeOut(sixths), FadeOut(rems), *[ReplacementTransform(a, b) for a, b in zip(bars, pbars)],
                  Transform(header, Text('percent', font_size=24, color=FOCUS).move_to(header, aligned_edge=LEFT)),
                  run_time=1.2)
        self.at('as the whole-number weights')
        names = [Text(str(w), font_size=24, color=SCAFFOLD).move_to(b.name, aligned_edge=RIGHT) for w, b in zip(pweights, pbars)]
        self.play(*[Transform(b.name, n) for b, n in zip(pbars, names)],
                  Transform(header, Text('weights', font_size=24, color=FOCUS).move_to(header, aligned_edge=LEFT)), run_time=0.9)
        self.at('Split ten dollars')
        self.play(Transform(pot, Text('$10.00', font_size=44, color=MONEY).move_to(pot)), run_time=0.6)
        self.play(con.type_line(2, run_time=1.2))
        self.at('and the shares are')
        small = bracket_items(lines[2], 1)                                          # $3.33 $3.33 $3.34
        landed = [Text(a, font_size=24, color=BLACK, weight=BOLD).move_to(b.gold) for a, b in zip(small, pbars)]
        self.play(LaggedStart(*[Transform(b.amount, t) for b, t in zip(pbars, landed)], lag_ratio=0.5), run_time=1.8)

        # [V8.4d] every sum glows green in turn; the weights could be anything you can count
        self.at('The weights never need to be money')
        for i in range(3):
            whole = con.lines[i].chars(con.lines[i].source.index('sum'))
            self.play(whole.animate.set_color(EXACT), Indicate(whole, color=EXACT, scale_factor=1.15), run_time=0.6)
        for phrase, label in (('Shares, hours worked', 'shares'), ('hours worked', 'hours worked'),
                              ('square metres', 'm² of office space'), ('the prices on a receipt', 'prices on a receipt'),
                              ('Anything you can count.', 'anything you can count')):
            self.at(phrase)
            new = Text(label, font_size=24, color=FOCUS if label != 'anything you can count' else MONEY)
            self.play(Transform(header, new.move_to(header, aligned_edge=LEFT)), run_time=0.5)
        self.play(Circumscribe(pbars, color=MONEY, buff=0.12), run_time=1.2)
        self.finish()


# ---------------------------------------------------------------- 8.5

class Segment_8_5(Segment):
    """Spreading a discount (q08-03)."""
    EPISODE, SEGMENT = 8, '8.5'

    def construct(self):
        out = snippet_output(Q3)
        prices = [1999, 500, 1250]                  # the receipt in the script, as q08-03 has it
        coupon = 500

        # [V8.5a] the receipt: Book, Mug, Lamp, subtotal; a gold coupon slides onto the bottom
        slip = receipt([('Book', '$19.99'), ('Mug', '$5.00'), ('Lamp', '$12.50'), ('-', ''), ('Subtotal', '$37.49')],
                       width=4.2, font_size=22)
        slip.scale(1.3).move_to([-0.6, 0.7, 0])
        items = [r for r in slip.rows if r is not None]
        self.play(FadeIn(slip.paper, shift=DOWN * 0.3), run_time=0.6)
        self.at('A customer buys')
        self.play(LaggedStart(*[FadeIn(l) for l in slip.lines], lag_ratio=0.25), run_time=1.6)
        self.at('uses a five dollar coupon')
        ticket = price_tag('−$5.00', font_size=34)
        ticket.next_to(slip.paper, DOWN, buff=0.35)
        start = ticket.copy().shift(RIGHT * 8)
        self.play(Transform(start, ticket), run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        self.remove(start)
        self.add(ticket)
        self.at('subtract five dollars')
        self.play(Indicate(ticket, color=MONEY), run_time=0.8)
        self.at('the discount on every line')
        blanks = VGroup(*[label_box('?', color=MONEY, font_size=26).next_to(items[i], RIGHT, buff=0.45) for i in range(3)])
        for b in blanks:
            b.set_x(slip.paper.get_right()[0] + 0.25 + b.width / 2)
        self.play(LaggedStart(*[TransformFromCopy(ticket, b) for b in blanks], lag_ratio=0.25), run_time=1.2)

        # [V8.5b] code panel q08-03; the naive line: 2.67, 0.67, 1.67 adds to 5.01
        self.at('The tempting approach')
        code = code_panel(snippet_find(Q3, 'prices = [', 'coupon = 500', 'naive = [', 'shares = allocate(coupon'),
                          font_size=18).to_corner(UL, buff=0.2)
        con = output_console(Q3, font_size=18).to_edge(RIGHT, buff=0.2)
        con.set_y(code.get_bottom()[1] - 0.2 - con.height / 2)
        shop = VGroup(slip, ticket, blanks)
        self.play(shop.animate.scale(0.9 / 1.3).to_edge(LEFT, buff=0.3).set_y(-1.1), FadeIn(code, shift=DOWN * 0.2),
                  FadeIn(con.background), run_time=1.0)
        card = show_card(self, 'q08-03')
        mark = line_highlight(code, 2)
        self.play(Create(mark), run_time=0.4)

        def tag(text, color, near):
            box = RoundedRectangle(width=1.05, height=0.42, corner_radius=0.06).set_fill(MONEY, 0.2).set_stroke(color, 2)
            label = code_text(text, font_size=20, color=color).move_to(box)
            return VGroup(box, label).move_to(near)

        naive = bracket_items(out[0], 0)                                            # 2.67 0.67 1.67
        self.at('Two sixty-seven')
        tags = VGroup(*[tag(v, MONEY, b) for v, b in zip(naive, blanks)])
        self.play(con.type_line(0, run_time=1.2), *[ReplacementTransform(b, t) for b, t in zip(blanks, tags)], run_time=1.2)
        self.at('Add them up')
        rule = Line(LEFT * 0.55, RIGHT * 0.55, color=SCAFFOLD).next_to(tags, DOWN, buff=0.12)
        total_naive = output_line(Q3, 'rounded each').split('sum')[1].strip()       # 5.01
        bad = code_text(total_naive, font_size=22, color=ERROR).next_to(rule, DOWN, buff=0.15)
        self.play(Create(rule), FadeIn(bad, shift=UP * 0.15), con.part(0, 'sum 5.01').animate.set_color(ERROR), run_time=0.7)
        self.at('a bigger discount than the coupon')
        self.play(Indicate(bad, color=ERROR, scale_factor=1.4), Indicate(ticket, color=MONEY), run_time=0.9)
        hide_card(self, card)

        # [V8.5c] largest remainder: 2.66, 0.67, 1.67; the book's tag flicks down; the sum is 5.00
        self.at('Largest remainder, with the prices')
        self.play(Transform(mark, line_highlight(code, 3)), con.type_line(1, run_time=1.2))
        shares = [int(s) for s in bracket_items(out[1], 0)]                          # 266 67 167
        self.at('gives two sixty-six')
        fixed = [tag(f'{s / 100:.2f}', EXACT, t) for s, t in zip(shares, tags)]   # cents shown as dollars
        flash = SurroundingRectangle(tags[0], color=FOCUS, buff=0.06)
        self.play(Create(flash), run_time=0.3)
        self.play(*[Transform(t, f) for t, f in zip(tags, fixed)], run_time=0.6)
        self.play(FadeOut(flash), run_time=0.3)
        self.at('Exactly five')
        good = code_text(f'{sum(shares) / 100:.2f}', font_size=22, color=EXACT).move_to(bad)   # computed: 5.00
        self.play(Transform(bad, good), con.part(1, 'sum 500').animate.set_color(EXACT), run_time=0.7)

        # look at the book: alone it rounds to 2.67, but its remainder is the smallest of the three
        self.at('Look at the book.')
        book_box = SurroundingRectangle(VGroup(items[0], tags[0]), color=FOCUS, buff=0.08)
        self.play(Create(book_box), run_time=0.5)
        self.at('its share would be')
        ghost = tag(naive[0], FOCUS, tags[0]).next_to(tags[0], UP, buff=0.12)
        self.play(FadeIn(ghost, shift=DOWN * 0.15), run_time=0.5)
        self.at('But its remainder was the smallest')
        exact = [Fraction(coupon * p, sum(prices)) for p in prices]                 # computed exact shares, in cents
        names = ['Book', 'Mug', 'Lamp']
        head = Text('exact share, in cents', font_size=20, color=SCAFFOLD)
        rows = VGroup()
        for name, e in zip(names, exact):
            whole = math.floor(e)
            frac = e - whole
            label = code_text(f'{name:<5}{whole:>4} + {float(frac):.2f}', font_size=20, color=WHITE)
            label.part(f'{float(frac):.2f}').set_color(FOCUS)
            sliver = Rectangle(width=float(frac) * 1.6, height=0.28).set_fill(FOCUS, 0.6).set_stroke(width=0)
            sliver.next_to(label, RIGHT, buff=0.3)
            rows.add(VGroup(label, sliver))
        rows.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        for r in rows:
            r[1].align_to(rows[0][1], LEFT)
        panel = VGroup(head, rows).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to([3.4, -2.1, 0])
        self.play(FadeIn(panel, shift=UP * 0.2), run_time=0.8)
        self.play(Indicate(rows[0][1], color=FOCUS, scale_factor=1.4), rows[0][0].animate.set_color(FOCUS), run_time=0.8)
        self.at('when the leftover cents were')
        floors = [math.floor(e) for e in exact]
        cents_left = coupon - sum(floors)                                            # computed: 2
        winners = sorted(range(3), key=lambda i: (-(exact[i] - floors[i]), i))[:cents_left]
        drops = VGroup(*[penny(0.17).move_to(rows[i][1].get_right() + RIGHT * 0.35 + UP * 0.8) for i in winners])
        self.play(LaggedStart(*[d.animate.move_to(rows[i][1].get_right() + RIGHT * 0.35)
                                for d, i in zip(drops, winners)], lag_ratio=0.3), run_time=1.0)
        self.at('it went without')
        self.play(FadeOut(ghost), Wiggle(rows[0][0]), run_time=0.8)

        # [V8.5d] the three discounted lines print, then the receipt total
        self.at('Every line is within a cent')
        self.play(FadeOut(book_box), FadeOut(mark), con.type_line(2, 0.6), run_time=0.6)
        self.play(con.type_line(3, 0.6))
        self.play(con.type_line(4, 0.6))
        self.at('and the lines add up')
        self.play(con.type_line(5, 1.0))
        self.play(con.part(5, '3249').animate.set_color(EXACT), run_time=0.5)

        # [V8.5e] the mug comes back: its line lifts off with "refund $4.33", not $5.00
        self.at('If the customer returns the mug')
        self.play(FadeOut(code), FadeOut(panel), FadeOut(drops), run_time=0.6)
        mug_line = items[1]
        mug_tag = tags[1]
        paid = int(out[3].split('=')[1])                                              # 433
        strip = Rectangle(width=slip.paper.width, height=mug_line.line_height * 1.9).set_fill(PAPER, 1).set_stroke(width=0)
        strip.move_to([slip.paper.get_x(), mug_line.anchor()[1], 0])
        self.add(strip, mug_line)
        lifted = VGroup(strip, mug_line, mug_tag)
        self.play(lifted.animate.move_to([-3.2, 3.0, 0]), run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        refund = label_box(f'refund {dollars(paid)}', color=EXACT, font_size=26, fill=EXACT).next_to(lifted, RIGHT, buff=0.4)
        self.at('you refund what they actually paid')
        self.play(FadeIn(refund, shift=LEFT * 0.2), con.part(3, '433').animate.set_color(EXACT), run_time=0.7)
        self.at('Not five dollars')
        wrong = Text('$5.00', font_size=30, color=ERROR).next_to(refund, RIGHT, buff=0.6)
        cross = Line(wrong.get_left() + LEFT * 0.1, wrong.get_right() + RIGHT * 0.1, color=ERROR, stroke_width=5)
        self.play(FadeIn(wrong), run_time=0.4)
        self.play(Create(cross), run_time=0.4)
        self.at('The split you store today')
        stored = label_box('stored: ' + ' · '.join(str(s) for s in shares) + ' ¢', color=STORED, font_size=24, fill=STORED)
        stored.next_to(lifted, DOWN, buff=0.35).align_to(lifted, LEFT)
        link = Arrow(stored.get_right(), refund.get_bottom(), color=STORED, buff=0.1, stroke_width=3)
        self.play(FadeIn(stored, shift=UP * 0.2), run_time=0.6)
        self.play(GrowArrow(link), run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 8.6

class Segment_8_6(Segment):
    """Twelve payments (q08-04)."""
    EPISODE, SEGMENT = 8, '8.6'

    def construct(self):
        out = snippet_output(Q4)
        naive = re.search(r'x ([\d.]+) =', out[0]).group(1)                         # 83.33
        short = out[0].split('=')[1].strip()                                         # 999.96
        each, extra = (int(x) for x in re.findall(r'\d+', out[1]))                   # 8333, 4

        # [V8.6a] a calendar strip of twelve months under "$1,000.00 a year"
        title = Text('$1,000.00 a year', font_size=42, color=MONEY).move_to(UP * 1.6)
        months = calendar(width=1.0, height=1.0).move_to(DOWN * 0.2)
        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.15) for m in months], lag_ratio=0.08), run_time=1.4)
        self.at('paid monthly.')
        self.play(LaggedStart(*[Indicate(m.box, color=MONEY, scale_factor=1.08) for m in months], lag_ratio=0.08), run_time=1.5)

        # [V8.6b] code panel q08-04; twelve 83.33 tags fall onto the months; 999.96 glows red
        self.at('Divide by twelve and round')
        code = code_panel(snippet_lines(Q4, 4, 6), font_size=18)
        small = output_console(Q4, needles=['float:'], font_size=20)
        self.play(title.animate.scale(0.75).to_edge(UP, buff=0.25), months.animate.move_to(UP * 2.35), run_time=0.8)
        code.to_edge(LEFT, buff=0.3).set_y(0.7)
        small.next_to(code, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeIn(code, shift=RIGHT * 0.2), FadeIn(small.background), run_time=0.6)
        card = show_card(self, 'q08-04')
        self.play(small.type_line(0, run_time=1.0))
        self.at('eighty-three thirty-three')
        tags = VGroup(*[amount_in(m, naive) for m in months])
        self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.6) for t in tags], lag_ratio=0.12), run_time=1.8)
        self.at('Twelve of those')
        sum_text = Text(f'→ ${short}', font_size=32, color=ERROR).next_to(title, RIGHT, buff=0.4)
        self.play(small.part(0, short).animate.set_color(ERROR), FadeIn(sum_text, shift=LEFT * 0.2), run_time=0.7)
        self.at('Four cents short')
        pot = jar(1.3, 1.5).move_to([2.6, 0.5, 0])
        holes = VGroup(*[DashedVMobject(Circle(radius=0.2, color=ERROR), num_dashes=12) for _ in range(extra)])
        holes.arrange_in_grid(rows=2, cols=2, buff=0.12).move_to(pot[0]).shift(DOWN * 0.25)
        missing = Text(f'{extra}¢ short', font_size=26, color=ERROR).next_to(pot, RIGHT, buff=0.3)
        self.play(FadeIn(pot), run_time=0.4)
        self.play(LaggedStart(*[Create(h) for h in holes], lag_ratio=0.2), FadeIn(missing), run_time=1.0)
        self.at('for every customer')
        self.play(Indicate(sum_text, color=ERROR), run_time=0.8)

        # [V8.6c] in whole cents: 8333 each with 4 left over; two calendars, two policies
        self.at('In whole cents')
        hide_card(self, card)
        code2 = code_panel(snippet_find(Q4, 'each, extra = divmod', 'last_pays =', 'first_pay ='), font_size=18)
        code2.to_corner(UL, buff=0.25)
        con = output_console(Q4, font_size=18).to_edge(DOWN, buff=0.9)
        row1 = calendar(width=1.0, height=0.85).move_to([0, 1.2, 0])
        row2 = calendar(width=1.0, height=0.85).move_to([0, -0.45, 0])
        con.lines[0].set_color(GREY_A)
        con.part(0, short).set_color(ERROR)
        self.play(FadeOut(VGroup(code, title, sum_text, missing, tags)), FadeOut(small.background), FadeOut(small.lines[0]),
                  FadeIn(code2, shift=RIGHT * 0.2), ReplacementTransform(months, row1),
                  VGroup(pot, holes).animate.move_to([4.8, 3.05, 0]), run_time=1.0)
        self.play(FadeIn(con.background), FadeIn(con.lines[0]), run_time=0.5)
        mark = line_highlight(code2, 0)
        self.play(Create(mark), con.type_line(1, run_time=1.0))
        self.at('eight thousand three hundred and thirty-three cents a month')
        base1 = VGroup(*[amount_in(m, str(each), color=WHITE) for m in row1])
        self.play(LaggedStart(*[FadeIn(a) for a in base1], lag_ratio=0.06), run_time=1.0)
        self.at('with four cents left over')
        coins = VGroup(*[penny(0.2).move_to(h) for h in holes])
        self.play(LaggedStart(*[FadeIn(c, scale=0.5) for c in coins], lag_ratio=0.2), FadeOut(holes), run_time=0.9)

        self.at('You could put all four cents')
        label1 = Text(out[2][:17].strip(), font_size=22, color=SCAFFOLD).next_to(row1, UP, buff=0.12).align_to(row1, LEFT)
        self.play(Transform(mark, line_highlight(code2, 1)), FadeIn(label1), run_time=0.6)
        dec = row1[-1]
        flying = coins.copy()
        coins.set_opacity(0.3)
        self.play(LaggedStart(*[c.animate.move_to(dec.box.get_center() + UP * 0.05 + RIGHT * (k - 1.5) * 0.18).scale(0.6)
                                for k, c in enumerate(flying)], lag_ratio=0.2), run_time=1.4)
        self.at('and one at eighty-three thirty-seven')
        new_dec = amount_in(dec, str(each + extra), color=FOCUS)                     # 8337, as q08-04 prints
        self.play(FadeOut(flying), Transform(base1[-1], new_dec), con.type_line(2, run_time=1.2), run_time=1.2)

        self.at('Or you could spread them out')
        base2 = VGroup(*[amount_in(m, str(each), color=WHITE) for m in row2])
        label2 = Text(out[3][:17].strip(), font_size=22, color=SCAFFOLD).next_to(row2, UP, buff=0.12).align_to(row2, LEFT)
        self.play(FadeIn(row2), FadeIn(base2), FadeIn(label2), Transform(mark, line_highlight(code2, 2)),
                  coins.animate.set_opacity(1), run_time=0.8)
        self.at('one extra')
        flying = coins.copy()
        coins.set_opacity(0.3)
        self.play(LaggedStart(*[c.animate.move_to(row2[k].box.get_center() + UP * 0.05).scale(0.6)
                                for k, c in enumerate(flying)], lag_ratio=0.25), run_time=1.4)
        bumped = [amount_in(row2[k], str(each + 1), color=FOCUS) for k in range(extra)]  # 8334, as q08-04 prints
        self.play(FadeOut(flying), *[Transform(base2[k], b) for k, b in enumerate(bumped)], con.type_line(3, run_time=1.2),
                  run_time=1.2)

        # [V8.6d] both sums glow green
        self.at('Both add')
        self.play(FadeOut(mark), con.part(2, 'sum 100000').animate.set_color(EXACT),
                  con.part(3, 'sum 100000').animate.set_color(EXACT), run_time=0.6)
        self.play(*[Indicate(VGroup(r), color=EXACT, scale_factor=1.02) for r in (row1, row2)], run_time=0.8)

        # policy: early extra is collected sooner; late extra is never paid by a customer who cancels
        self.at('Charging the extra early')
        early = SurroundingRectangle(VGroup(*row2[:extra]), color=FOCUS, buff=0.06)
        early_label = Text('collected sooner', font_size=22, color=FOCUS).next_to(label2, RIGHT, buff=0.5)
        self.play(Create(early), FadeIn(early_label), run_time=0.7)
        self.at('a customer who cancels early')
        cut_x = (row1[5].get_right()[0] + row1[6].get_left()[0]) / 2
        cut = DashedLine([cut_x, row1.get_top()[1] + 0.1, 0], [cut_x, row1.get_bottom()[1] - 0.1, 0], color=ERROR, stroke_width=4)
        cut_label = Text('cancels', font_size=22, color=ERROR).next_to(label1, RIGHT, buff=0.5)
        self.play(Create(cut), FadeIn(cut_label), run_time=0.6)
        never = crossmark(size=0.5).move_to(dec.box)
        shade = SurroundingRectangle(VGroup(*row1[6:]), buff=0.04).set_stroke(width=0).set_fill(BLACK, 0.7)
        self.play(FadeIn(shade), Create(never), run_time=0.8)

        self.at('Which one you choose')
        self.play(FadeOut(VGroup(early, early_label, cut, cut_label, never, shade)), run_time=0.6)
        checks = VGroup()
        for words in ('on purpose', 'written down', 'the same every time'):
            item = VGroup(checkmark(size=0.32), Text(words, font_size=24)).arrange(RIGHT, buff=0.15)
            checks.add(item)
        checks.arrange(RIGHT, buff=0.9).move_to(DOWN * 3.6)
        for item, phrase in zip(checks, ('on purpose', 'write it down', 'the same way every time')):
            self.at(phrase)
            self.play(Create(item[0]), FadeIn(item[1], shift=UP * 0.15), run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 8.7

class Segment_8_7(Segment):
    """Who gets the extra cent?"""
    EPISODE, SEGMENT = 8, '8.7'

    def construct(self):
        # [V8.7a] the three figures return under a calendar; every month's extra cent goes to A
        months = calendar(width=0.88, height=0.6, gap=0.08).move_to(UP * 3.15)
        for m in months:
            m[1].move_to(m.box)
        people = VGroup(*[figure(c).scale(1.3) for c in 'ABC']).arrange(RIGHT, buff=1.5).move_to([-2.65, 1.0, 0])
        bases = [p.get_bottom() + DOWN * 0.6 for p in people]
        self.play(FadeIn(months), LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in people], lag_ratio=0.2), run_time=1.2)
        counts = VGroup(*[number(0, font_size=32, color=MONEY) for _ in people])
        units = VGroup(*[Text('¢', font_size=32, color=MONEY) for _ in people])
        for c, u, p in zip(counts, units, people):
            c.next_to(p, RIGHT, buff=0.25)
            u.add_updater(lambda m, c=c: m.next_to(c, RIGHT, buff=0.06, aligned_edge=DOWN))
            u.update()
        self.add(counts, units)

        def month_of_pennies(owner_of, speeds):
            piles = [VGroup() for _ in people]
            for k, (m, run_time) in enumerate(zip(months, speeds)):
                who = owner_of(k)
                cent = penny(0.3).move_to(m.box.get_bottom() + DOWN * 0.35)
                spot = cent_pile_spot(bases[who], len(piles[who]))
                self.play(m.box.animate.set_stroke(FOCUS, 3), FadeIn(cent, scale=0.5), run_time=run_time * 0.3)
                self.play(cent.animate.move_to(spot), m.box.animate.set_stroke(GREY_D, 2), run_time=run_time * 0.7,
                          rate_func=rate_functions.ease_in_out_sine)
                piles[who].add(cent)
                counts[who].set_value(len(piles[who]))
            return piles

        self.at('Split a monthly bill three ways')
        speeds = [1.0, 0.9, 0.8, 0.7, 0.6, 0.55, 0.5, 0.45, 0.45, 0.45, 0.45, 0.45]
        piles = month_of_pennies(lambda k: 0, speeds)

        self.at('a policy that looked neutral')
        frame = SurroundingRectangle(VGroup(piles[0], people[0], counts[0], units[0]), color=ERROR, buff=0.15)
        self.play(*[c[0].animate.set_fill(ERROR) for c in piles[0]], counts[0].animate.set_color(ERROR), Create(frame), run_time=0.8)

        # [V8.7c] the properties to aim for, as labels over the scene
        props = VGroup(*[Text(t, font_size=34, weight=BOLD) for t in ('deterministic', 'documented', 'fair over time')])
        props.arrange(DOWN, buff=1.0, aligned_edge=LEFT)
        props.shift([2.9 - props.get_left()[0], -0.6 - props.get_y(), 0])
        notes = VGroup(Text('same input, same answer', font_size=22, color=SCAFFOLD),
                       Text('who pays the extra, and why', font_size=22, color=SCAFFOLD),
                       Text('rotate the extra cent', font_size=22, color=SCAFFOLD))
        for n, p in zip(notes, props):
            n.next_to(p, DOWN, buff=0.12, aligned_edge=LEFT)
        self.at('deterministic')
        self.play(FadeIn(props[0], shift=LEFT * 0.2), FadeIn(notes[0]), run_time=0.6)
        self.at('run it twice')
        again = VGroup(*[penny(0.25).move_to(months[0].box.get_bottom() + DOWN * 0.3) for _ in range(2)])
        for g in again:
            self.play(FadeIn(g, scale=0.5), run_time=0.2)
            self.play(g.animate.move_to(people[0].get_top() + UP * 0.2), run_time=0.6)
            self.play(FadeOut(g, scale=0.3), run_time=0.2)
        tick = checkmark(size=0.35).next_to(props[0], RIGHT, buff=0.2)
        self.play(Create(tick), run_time=0.4)
        self.at('documented')
        self.play(FadeIn(props[1], shift=LEFT * 0.2), FadeIn(notes[1]), run_time=0.6)
        self.at('why they paid a cent more')
        self.play(Indicate(props[1], color=FOCUS), run_time=0.8)

        # [V8.7b] rewind; now the extra cent rotates A, B, C ...: four pennies each, green
        self.at('fair over time')
        self.play(FadeIn(props[2], shift=LEFT * 0.2), FadeIn(notes[2]), FadeOut(frame), run_time=0.6)
        self.play(LaggedStart(*[c.animate.move_to(months[k].box.get_center()).set_opacity(0)
                                for k, c in reversed(list(enumerate(piles[0])))], lag_ratio=0.08),
                  ChangeDecimalToValue(counts[0], 0), run_time=1.4)
        counts[0].set_color(MONEY)
        self.remove(*piles[0])
        piles = month_of_pennies(lambda k: k % 3, [0.3] * 12)
        self.play(*[c[0].animate.set_fill(EXACT) for pile in piles for c in pile],
                  *[n.animate.set_color(EXACT) for n in counts], run_time=0.6)
        fair = SurroundingRectangle(VGroup(*people, *piles, counts, units), color=EXACT, buff=0.15)
        self.play(Create(fair), run_time=0.5)

        # all of these are choices about who gets a penny ... can a reasonable rule misbehave?
        self.at('All of these are choices')
        veil = FullScreenRectangle().set_stroke(width=0).set_fill(BLACK, 0.85)
        big = penny(0.9).move_to(ORIGIN)
        self.play(FadeIn(veil), FadeIn(big, scale=0.5), run_time=0.8)
        self.at('Can a reasonable rule')
        mark = Text('?', font_size=72, color=FOCUS, weight=BOLD).next_to(big, RIGHT, buff=0.4)
        self.play(FadeIn(mark, shift=LEFT * 0.2), Rotate(big, PI / 8), run_time=0.6)
        self.at('It can.')
        bang = Text('!', font_size=72, color=ERROR, weight=BOLD).move_to(mark)
        self.play(Transform(mark, bang), big[0].animate.set_stroke(ERROR, 8), run_time=0.5)
        self.play(Wiggle(big), run_time=0.8)
        self.finish()


# ---------------------------------------------------------------- 8.8

class Segment_8_8(Segment):
    """The Alabama paradox (q08-05)."""
    EPISODE, SEGMENT = 8, '8.8'

    def construct(self):
        out = snippet_output(Q5)
        weights = [int(w) for w in re.search(r'WEIGHTS = \[([^\]]*)\]', snippet_source(Q5)).group(1).split(',')]
        results = [[int(x) for x in bracket_items(line)] for line in out]

        # [V8.8a] code panel with WEIGHTS = [1, 3, 3]; three bars of weights 1, 3, 3
        code = code_panel(snippet_find(Q5, 'WEIGHTS = [', 'for total in range', 'shares = allocate(total, WEIGHTS)'),
                          font_size=20).to_corner(UL, buff=0.3)
        con = Console(out[:5], font_size=18).next_to(code, DOWN, buff=0.2, aligned_edge=LEFT)
        unit = 1.7
        bars = VGroup()
        for i, w in enumerate(weights):
            bar = Rectangle(width=unit * w, height=0.4).set_fill(STORED, 0.5).set_stroke(STORED, 2)
            name = Text(f'weight {w}', font_size=26, color=SCAFFOLD).next_to(bar, LEFT, buff=0.3)
            row = VGroup(bar, name)
            row.bar = bar
            bars.add(row)
        for i, row in enumerate(bars):
            row.shift([-5.0, -1.0 - 1.15 * i, 0] - row.bar.get_left())
        self.play(FadeIn(code, shift=RIGHT * 0.2), run_time=0.6)
        self.play(Indicate(code.code_lines[0], color=FOCUS), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in bars],
                                                                         lag_ratio=0.2), run_time=1.0)

        # [V8.8b] the console prints line by line; pennies sit on the bars to match; QR q08-05
        self.at('Here are the results')
        self.play(FadeIn(con.background), run_time=0.4)
        card = show_card(self, 'q08-05')
        on_bar = [[] for _ in weights]

        def spot(i, k):
            return bars[i].bar.get_corner(UL) + RIGHT * (0.34 + 0.6 * k) + UP * 0.29

        def show_result(n, run_time=0.8):
            """Move pennies so the bars hold results[n]: surplus pennies move to bars that need them."""
            target = results[n]
            spare, anims = [], []
            for i in range(len(weights)):
                while len(on_bar[i]) > target[i]:
                    spare.append(on_bar[i].pop())
            for i in range(len(weights)):
                while len(on_bar[i]) < target[i]:
                    if spare:
                        c = spare.pop(0)
                        anims.append(c.animate.move_to(spot(i, len(on_bar[i]))))
                    else:
                        c = penny(0.26).move_to(spot(i, len(on_bar[i])) + UP * 1.3)
                        self.add(c)
                        anims.append(c.animate.move_to(spot(i, len(on_bar[i]))))
                    on_bar[i].append(c)
            anims += [FadeOut(c, scale=0.4) for c in spare]
            if anims:
                self.play(*anims, run_time=run_time, rate_func=rate_functions.ease_in_out_sine)

        for n, phrase in enumerate(('for one cent', 'two cents', 'three cents')):
            self.at(phrase)
            self.play(con.type_line(n, run_time=0.5))
            show_result(n, 0.7)
        self.at('At three cents, everyone gets one.')
        self.play(*[Indicate(VGroup(*p), color=MONEY) for p in on_bar], Indicate(con.lines[2], color=FOCUS), run_time=0.8)

        # [V8.8c] four cents: the first bar's penny lifts off to another bar as a new one arrives
        self.at('Four cents')
        typed = len('4¢ -> [0, 2, 2]')
        glyphs = con.lines[3].glyphs
        main = len(re.sub(r'\s', '', out[3][:typed]))
        self.play(LaggedStart(*[FadeIn(g, run_time=0.05) for g in glyphs[:main]], lag_ratio=1.0, run_time=0.6))
        lifted = on_bar[0][0]
        self.play(lifted.animate.shift(UP * 0.6), run_time=0.4)
        show_result(3, 1.0)
        self.at('nothing.')
        self.play(bars[0].bar.animate.set_fill(ERROR, 0.7).set_stroke(ERROR), run_time=0.3)
        self.play(bars[0].bar.animate.set_fill(STORED, 0.5).set_stroke(STORED), run_time=0.3)
        self.play(bars[0].bar.animate.set_fill(ERROR, 0.7).set_stroke(ERROR), run_time=0.3)
        con.lines[3].chars(typed).set_color(ERROR)
        self.play(LaggedStart(*[FadeIn(g, run_time=0.05) for g in glyphs[main:]], lag_ratio=1.0, run_time=1.2))
        self.at('their share shrank')
        self.play(Indicate(con.lines[3].chars(typed), color=ERROR, scale_factor=1.05), run_time=0.8)

        # [V8.8d] why: exact shares and remainders at 3¢ and at 4¢; largest remainders in yellow
        self.at("Here's why.")
        hide_card(self, card)
        self.play(con.type_line(4, run_time=0.5))

        def table(total):
            cols = MonoLine('exact  whole  remainder', font_size=24, color=SCAFFOLD)
            cols.set_anchor([0.6, bars[0].bar.get_y() + 0.85, 0])
            rows = VGroup()
            for w, bar in zip(weights, bars):
                whole, rem = divmod(total * w, sum(weights))        # computed: exact share total·w/7
                text = f'{f"{total * w}/7":>5}  {whole:>5}  {f"{rem}/7":>9}'
                rows.add(MonoLine(text, font_size=24, color=WHITE).set_anchor([0.6, bar.bar.get_y(), 0]))
            head = Text(f'{total}¢, in sevenths', font_size=28, color=FOCUS).next_to(cols, UP, buff=0.18)
            head.align_to(cols, LEFT)
            group = VGroup(head, cols, rows)
            group.rows = rows
            return group

        def rem_glyphs(t, i):
            src = t.rows[i].source
            return t.rows[i].chars(len(src) - len(src.split()[-1]))

        self.at('With three cents')
        self.play(FadeOut(con), bars[0].bar.animate.set_fill(STORED, 0.5).set_stroke(STORED), run_time=0.4)
        show_result(2, 0.9)
        t3 = table(3)
        self.play(FadeIn(t3[0]), FadeIn(t3[1]), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.2) for r in t3.rows], lag_ratio=0.3), run_time=1.2)
        self.at('all of it remainder')
        self.play(rem_glyphs(t3, 0).animate.set_color(FOCUS), run_time=0.5)
        self.at('the biggest')
        box3 = SurroundingRectangle(rem_glyphs(t3, 0), color=FOCUS, buff=0.08)
        self.play(Create(box3), run_time=0.5)
        self.at('so they get a cent')
        self.play(Indicate(VGroup(*on_bar[0]), color=MONEY, scale_factor=1.3), run_time=0.7)

        self.at('With four cents')
        t4 = table(4)
        self.play(FadeOut(box3), ReplacementTransform(t3, t4), run_time=0.8)
        self.at('But the other two have grown faster')
        self.play(Indicate(VGroup(t4.rows[1], t4.rows[2]), color=FOCUS, scale_factor=1.05), run_time=0.8)
        self.at('a remainder of')
        self.play(rem_glyphs(t4, 1).animate.set_color(FOCUS), rem_glyphs(t4, 2).animate.set_color(FOCUS), run_time=0.5)
        boxes = VGroup(*[SurroundingRectangle(rem_glyphs(t4, i), color=FOCUS, buff=0.08) for i in (1, 2)])
        self.play(Create(boxes), run_time=0.5)
        self.at("Now the first person's remainder")
        self.play(rem_glyphs(t4, 0).animate.set_color(ERROR), Wiggle(t4.rows[0]), run_time=0.8)
        self.at('and they drop to zero')
        show_result(3, 1.0)

        # [V8.8e] Hamilton's method, the 1880 census, and Alabama: 299 seats gives 8, 300 gives 7
        self.at('This has a famous name.')
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
        name = Text('largest remainder', font_size=40, color=MONEY)
        aka = Text("= Hamilton's method", font_size=40).next_to(name, RIGHT, buff=0.3)
        heading = VGroup(name, aka).move_to(UP * 3.2)
        self.play(FadeIn(name, shift=DOWN * 0.2), run_time=0.6)
        self.at('Alexander Hamilton')
        self.play(FadeIn(aka, shift=LEFT * 0.2), run_time=0.6)
        self.at('House of Representatives')
        house = VGroup()
        for r, n in ((1.4, 13), (1.85, 17), (2.3, 21)):
            for k in range(n):
                angle = PI * (k + 0.5) / n
                house.add(Dot([r * math.cos(angle), r * math.sin(angle), 0], radius=0.08, color=STORED))
        house.scale(1.25).move_to([3.5, 0.35, 0])
        seats_label = Text('House seats', font_size=24, color=SCAFFOLD).next_to(house, DOWN, buff=0.3)
        self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in house], lag_ratio=0.02), FadeIn(seats_label), run_time=1.5)

        self.at('After the 1880')
        state = alabama_outline(4.9).move_to([-3.6, -0.75, 0])
        state_name = Text('Alabama', font_size=28).next_to(state, UP, buff=0.2)
        census = Text('1880 census', font_size=28, color=SCAFFOLD).next_to(house, UP, buff=0.35)
        self.play(Create(state), FadeIn(state_name), FadeIn(census), run_time=1.5)
        self.play(state.animate.set_fill(GREY_E, 0.9), run_time=0.3)
        alabama_seats = VGroup(*[Dot(radius=0.16, color=MONEY) for _ in range(8)]).arrange_in_grid(rows=4, cols=2, buff=0.3)
        alabama_seats.move_to(state).shift(DOWN * 0.1)
        self.at('two hundred and ninety-nine seats')
        line299 = Text('299 seats → 8', font_size=36).next_to(seats_label, DOWN, buff=0.25)
        self.play(FadeIn(line299, shift=UP * 0.2), LaggedStart(*[FadeIn(s, scale=0.3) for s in alabama_seats], lag_ratio=0.1),
                  run_time=1.0)
        self.at('to three')
        extra_seat = Dot([0, 0, 0], radius=0.08, color=FOCUS).move_to(house[30].get_center() + DOWN * 0.3)
        self.play(FadeIn(extra_seat, scale=3), run_time=0.6)
        line300 = Text('300 seats → 7', font_size=36, color=ERROR).next_to(line299, DOWN, buff=0.15)
        self.at('Alabama would lose a seat')
        self.play(FadeIn(line300, shift=UP * 0.2), run_time=0.5)
        self.play(alabama_seats[-1].animate.set_color(ERROR), run_time=0.3)
        self.play(alabama_seats[-1].animate.shift(DOWN * 2.6 + RIGHT * 0.3).set_opacity(0), run_time=0.9,
                  rate_func=rate_functions.ease_in_quad)
        self.at('Alabama paradox')
        title = Text('the Alabama paradox', font_size=44, weight=BOLD, color=FOCUS).move_to(heading)
        self.play(ReplacementTransform(heading, title), run_time=0.8)
        self.at('one reason the House')
        self.play(Indicate(house, color=SCAFFOLD, scale_factor=1.03), run_time=0.8)
        self.at('every allocation method is a policy')
        policy = Text('every allocation method is a policy', font_size=30, color=MONEY).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(policy, shift=UP * 0.2), run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 8.9

class Segment_8_9(Segment):
    """Recap and challenge; the QR wall; the teaser for episode 9."""
    EPISODE, SEGMENT = 8, '8.9'

    def construct(self):
        # [V8.9a] the recap column builds, each line with a small moving reminder of its idea
        texts = ['Rounding each share can lose or invent a cent',
                 'Parts must add up to the whole, exactly',
                 'Floor every share, give leftovers to the largest remainders',
                 'Ties broken the same way every time',
                 'Who gets the extra cent is policy']
        lines = VGroup(*[Text(t, font_size=32) for t in texts])
        lines.arrange(DOWN, buff=0.78, aligned_edge=LEFT)
        fit(lines, 11.2).move_to([1.2, 0.6, 0])
        icon_x = lines.get_left()[0] - 1.0

        def at_icon(mob, line):
            return mob.move_to([icon_x, line.get_y(), 0])

        phrases = ['Dividing money', 'The rule is that', 'Largest remainder guarantees', 'breaking ties',
                   'And who gets the extra']

        # 1: a penny drops away and leaves a red dashed gap
        self.at(phrases[0])
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2), run_time=0.6)
        c1 = at_icon(penny(0.3), lines[0])
        hole = DashedVMobject(Circle(radius=0.3, color=ERROR), num_dashes=14).move_to(c1)
        self.play(FadeIn(c1, scale=0.5), run_time=0.3)
        self.play(c1.animate.shift(DOWN * 0.6).set_opacity(0), Create(hole), run_time=0.7)

        # 2: a small balance scale levels and turns green
        self.at(phrases[1])
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2), run_time=0.6)
        scale = at_icon(balance_scale(width=1.6).scale(0.45), lines[1])
        self.play(FadeIn(scale), tip_scale(scale, -0.2), run_time=0.5)
        self.play(tip_scale(scale, 0.2), scale.animate.set_color(EXACT), run_time=0.7)

        # 3: three short bars with remainder slivers; a penny drops on the first
        self.at(phrases[2])
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2), run_time=0.6)
        minis = VGroup(*[VGroup(Rectangle(width=0.6, height=0.14).set_fill(MONEY, 0.9).set_stroke(width=0),
                                Rectangle(width=0.12, height=0.14).set_fill(FOCUS, 0.6).set_stroke(width=0))
                         .arrange(RIGHT, buff=0) for _ in range(3)]).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        at_icon(minis, lines[2])
        self.play(FadeIn(minis), run_time=0.4)
        drop = penny(0.1).move_to(minis[0][1].get_center() + UP * 0.5)
        self.play(drop.animate.move_to(minis[0][1]), run_time=0.5, rate_func=rate_functions.ease_in_quad)
        self.play(FadeOut(drop), minis[0][1].animate.set_fill(MONEY, 0.9), run_time=0.3)

        # 4: 1st, 2nd, 3rd, the same every run
        self.at(phrases[3])
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2), run_time=0.6)
        ranks = VGroup(*[Text(r, font_size=18, color=FOCUS) for r in ('1st', '2nd', '3rd')]).arrange(RIGHT, buff=0.08)
        at_icon(ranks, lines[3])
        self.play(LaggedStart(*[FadeIn(r, scale=0.6) for r in ranks], lag_ratio=0.4), run_time=0.8)

        # the method works for every kind of split in this episode
        self.at('It works for even splits')
        kinds = VGroup(*[Text(k, font_size=24, color=SCAFFOLD) for k in
                         ('even splits', 'weights', 'percentages', 'discounts', 'payments over time')])
        kinds.arrange(RIGHT, buff=0.45)
        kinds.next_to(lines, DOWN, buff=0.55).align_to(lines, LEFT)
        for k, phrase in zip(kinds, ('even splits', 'weights,', 'percentages', 'discounts', 'payments over time')):
            self.at(phrase)
            self.play(FadeIn(k, shift=UP * 0.15), k.animate.set_color(EXACT), run_time=0.4)

        # 5: the extra cent, with a question mark
        self.at(phrases[4])
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2), run_time=0.6)
        c5 = at_icon(penny(0.28), lines[4])
        q = Text('?', font_size=28, color=ERROR, weight=BOLD).next_to(c5, UR, buff=0.0)
        self.play(FadeIn(c5), run_time=0.3)
        self.play(Rotate(c5, TAU, axis=UP), FadeIn(q), run_time=0.9)
        self.at('or even paradoxical')
        self.play(Indicate(lines[4], color=FOCUS, scale_factor=1.05), run_time=0.8)

        # [V8.9b] the q08-05 code returns with its challenge comments highlighted; QR q08-05
        self.at("Here's a challenge")
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        code = code_panel(snippet_lines(Q5, 1, 4), font_size=18).to_edge(UP, buff=0.35)
        fit(code, 13.4)
        self.play(FadeIn(code, shift=DOWN * 0.2), run_time=0.6)
        card = show_card(self, 'q08-05')
        self.at('Find other weights')
        mark = line_highlight(code, 2)
        self.play(Create(mark), run_time=0.5)
        # challenge 1, acted out: 1 : 3 : 3 becomes ? : ? : ?
        try_w = Text('weights  1 : 3 : 3', font_size=36).move_to([-2.6, 0.4, 0])
        self.play(FadeIn(try_w, shift=UP * 0.2), run_time=0.5)
        self.at('pot gives someone less')
        self.play(Transform(try_w, Text('weights  ? : ? : ?', font_size=36, color=FOCUS).move_to(try_w)), run_time=0.7)

        # bonus: rotate who gets the extra cent, month after month
        self.at('Then, for a bonus')
        self.play(Transform(mark, line_highlight(code, 3)), run_time=0.5)
        months = calendar(width=0.66, height=0.8, gap=0.06, name_size=18).move_to([-2.6, -1.7, 0])
        self.play(FadeIn(months), run_time=0.6)
        self.at('rotates who gets the extra cent')
        whos = VGroup(*[Text('ABC'[k % 3], font_size=24, color=MONEY, weight=BOLD).move_to(slot(m)) for k, m in enumerate(months)])
        self.play(LaggedStart(*[FadeIn(w, scale=0.5) for w in whos], lag_ratio=0.15), run_time=2.4)
        self.at('and check that over a year')
        tally = Text('A 4 · B 4 · C 4', font_size=30, color=EXACT).next_to(months, DOWN, buff=0.35)
        self.play(FadeIn(tally, shift=UP * 0.2), run_time=0.6)

        # [V8.9c] the QR wall: q08-01 ... q08-05, held for ten seconds
        self.at('everyone pays the same')
        remaining = card.shown_at + 10.0 - self.renderer.time
        if remaining > 0:
            self.wait(remaining)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
        wall = qr_wall(episode_qr_ids(8))
        self.play(FadeIn(wall), run_time=0.6)
        self.wait(10.0)

        # [V8.9d] teaser: a checklist card with seven empty boxes; the first ticks itself
        self.play(FadeOut(wall), run_time=0.5)
        card_box = RoundedRectangle(width=4.6, height=5.6, corner_radius=0.18).set_fill(GREY_E, 0.6).set_stroke(SCAFFOLD, 2)
        boxes = VGroup(*[Square(0.36).set_stroke(SCAFFOLD, 2) for _ in range(7)]).arrange(DOWN, buff=0.34)
        boxes.move_to(card_box).align_to(card_box, LEFT).shift(RIGHT * 0.4)
        blanks = VGroup(*[Line(LEFT, RIGHT, color=GREY_D, stroke_width=6).set_width(2.9).next_to(b, RIGHT, buff=0.3)
                          for b in boxes[1:]])
        first = Text("count, don't measure", font_size=24).next_to(boxes[0], RIGHT, buff=0.3)
        checklist = VGroup(card_box, boxes, blanks, first)
        teaser = end_card('Episode 9', 'Doing money right')
        checklist.scale(1.15)
        VGroup(checklist, teaser).arrange(RIGHT, buff=1.0).move_to(ORIGIN)
        first.set_opacity(0)
        self.play(FadeIn(card_box), LaggedStart(*[Create(b) for b in boxes], lag_ratio=0.1), FadeIn(blanks),
                  FadeIn(teaser, shift=UP * 0.2), run_time=1.2)
        tick = checkmark(size=0.42).move_to(boxes[0]).shift(UP * 0.05 + RIGHT * 0.05)
        self.play(Create(tick), first.animate.set_opacity(1), run_time=0.8)
        self.finish(extra=1.5)

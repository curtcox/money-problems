"""Episode 7 · Fractions of a penny: what Office Space got right and wrong. One Scene per segment.

    python3 production/render.py 7 [-ql] [segment ...]

Shot ids in comments ([V7.1a] ...) refer to episodes/07-fractions-of-a-penny.md. On-screen code
and output come from snippets/ep07/. The film is discussed as commentary only: it appears here
as plain-text names, never as imagery. Every picture is our own diagram (desks, a vault, jars,
pennies, rulers, ledgers, code).
"""
import random
import re
import sys
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa: E402,F403

Q1 = 'ep07/01-where-fractions-come-from.py'
Q2 = 'ep07/02-the-virus.py'
Q3 = 'ep07/03-round-dont-truncate.py'
Q4 = 'ep07/04-the-decimal-point-mistake.py'
Q5 = 'ep07/05-challenge-catch-the-virus.py'

DAILY = Decimal('0.035') / 365          # the daily rate every ep07 snippet uses
CENT = Decimal('0.01')
TINY = Decimal('1e-10')                 # q07-05 keeps interest to ten places


# ---------------------------------------------------------------- data helpers

def field(line, label):
    """The token after `label` in a recorded output line ('pay 0.11' -> '0.11')."""
    match = re.search(re.escape(label) + r'\s+(\S+)', line)
    if not match:
        raise ValueError(f'no {label!r} in {line!r}')
    return match.group(1)


def seeded_balances(n):
    """The first n balances the seeded snippets draw (random.seed(1999), $0.01 to $50,000).
    q07-02, q07-03 and q07-05 all start with these accounts, so cards built from them show
    the snippets' own customers (computed here, not printed by any snippet)."""
    rng = random.Random(1999)
    return [Decimal(rng.randint(1, 5_000_000)) / 100 for _ in range(n)]


def slice_cents(balance):
    """A day's interest on a balance, truncated: (interest, paid, slice in cents)."""
    interest = balance * DAILY
    paid = interest.quantize(CENT, ROUND_DOWN)
    return interest, paid, (interest - paid) * 100


# ---------------------------------------------------------------- QR timing

def show_qr(scene, qr_id):
    card = qr_card(qr_id)
    scene.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)
    card.shown_at = scene.renderer.time
    return card


def hide_qr(scene, card, hold=8.0):
    """Fade a QR card out, but never before it has been fully up for `hold` seconds."""
    remaining = card.shown_at + hold - scene.renderer.time
    if remaining > 0:
        scene.wait(remaining)
    scene.play(FadeOut(card), run_time=0.5)


# ---------------------------------------------------------------- drawing helpers

def sliver(size=0.2):
    """One wedge of the sliced penny: a fraction of a cent."""
    return sliced_penny(12, size)[0].copy().move_to(ORIGIN)


def desk(color=GREY_B):
    """A plain office desk with a monitor (generic, no characters)."""
    top = Line(LEFT * 0.85, RIGHT * 0.85, color=color, stroke_width=6)
    legs = VGroup(Line(top.get_start(), top.get_start() + DOWN * 0.6),
                  Line(top.get_end(), top.get_end() + DOWN * 0.6)).set_stroke(color, 4)
    stand = Line(ORIGIN, UP * 0.18, color=color, stroke_width=4).next_to(top, UP, buff=0)
    screen = RoundedRectangle(width=1.05, height=0.68, corner_radius=0.06).set_stroke(color, 3).set_fill(GREY_E, 1)
    screen.next_to(stand, UP, buff=0)
    group = VGroup(legs, top, stand, screen)
    group.screen = screen
    return group


def vault_icon(label):
    box = RoundedRectangle(width=1.7, height=1.7, corner_radius=0.15).set_stroke(GREY_B, 3).set_fill(GREY_E, 1)
    door = Circle(radius=0.55).set_stroke(GREY_B, 3)
    # A four-spoke vault wheel with knobbed ends (three spokes in a ring read as a car badge).
    ends = [0.42 * np.array([math.cos(a), math.sin(a), 0]) for a in (PI / 4, 3 * PI / 4, 5 * PI / 4, 7 * PI / 4)]
    spokes = VGroup(*[Line(ORIGIN, e) for e in ends]).set_stroke(GREY_B, 3)
    spokes.add(*[Dot(e, radius=0.06, color=GREY_B) for e in ends])
    hub = Dot(radius=0.08, color=GREY_B)
    text = Text(label, font_size=22, color=SCAFFOLD).next_to(box, DOWN, buff=0.15)
    group = VGroup(box, door, spokes, hub, text)
    group.box = box
    return group


def labelled_jar(label, width=1.4, height=1.7, color=SCAFFOLD, font_size=22):
    pot = jar(width, height)
    text = Text(label, font_size=font_size, color=color).next_to(pot, DOWN, buff=0.15)
    group = VGroup(pot, text)
    group.pot = pot
    return group


def account_card(text, width=2.1, height=0.9, color=WHITE):
    card = RoundedRectangle(width=width, height=height, corner_radius=0.1).set_fill(GREY_E, 1).set_stroke(GREY_B, 2)
    label = Text(text, font_size=22, color=color).move_to(card)
    return VGroup(card, label)


def cent_ruler(lo, hi, width, fmt='{}¢', y=0.0, label_size=18, labelled=None):
    """The cent ruler: a tick every cent from lo to hi (a FloatLine with whole-cent ticks)."""
    ticks = list(range(lo, hi + 1))
    labels = {k: fmt.format(k) for k in (labelled if labelled is not None else ticks)}
    ruler = FloatLine(lo, hi, width=width, ticks=ticks, labels=labels, color=SCAFFOLD, label_size=label_size)
    return ruler.shift(UP * y)


def span(ruler, a, b, color, height=0.24, lift=0.2):
    """A bar standing on a ruler from value a to value b."""
    p, q = ruler.point(a), ruler.point(b)
    rect = Rectangle(width=max(q[0] - p[0], 0.02), height=height).set_fill(color, 0.95).set_stroke(width=0)
    return rect.move_to((p + q) / 2 + UP * (lift + height / 2))


def cut_line(ruler, value, color=WHITE, height=1.1):
    p = ruler.point(value)
    return DashedLine(p + DOWN * 0.25, p + UP * height, color=color, stroke_width=3, dash_length=0.08)


def bounce_path(points, height=1.2):
    """A path of hops between successive points (each hop arcs upward)."""
    path = VMobject()
    for a, b in zip(points[:-1], points[1:]):
        a, b = np.array(a, float), np.array(b, float)
        mid = (a + b) / 2 + UP * height
        hop = VMobject().set_points_smoothly([a, (a + mid) / 2 + UP * height * 0.35, mid,
                                             (mid + b) / 2 + UP * height * 0.35, b])
        if len(path.points):
            path.append_points(hop.points)
        else:
            path.set_points(hop.points)
    return path


def spill(pot, count=8, seed=3, floor=-3.7, reach=1.6):
    """Animations: pennies tumbling over a jar's rim to the floor on both sides."""
    rng = random.Random(seed)
    top = pot[1].get_top()
    pennies, moves = VGroup(), []
    for k in range(count):
        side = -1 if k % 2 else 1
        p = penny(0.16).move_to(top + RIGHT * side * 0.2)
        end = np.array([top[0] + side * rng.uniform(pot.width / 2 + 0.25, pot.width / 2 + reach), floor, 0])
        arc = ArcBetweenPoints(p.get_center(), end, angle=-side * PI / 2)
        pennies.add(p)
        moves.append(Succession(FadeIn(p, run_time=0.05), MoveAlongPath(p, arc, run_time=0.8,
                                                                         rate_func=rate_functions.ease_in_quad)))
    return pennies, moves


def magnifier(radius=0.32):
    lens = Circle(radius=radius).set_stroke(WHITE, 4).set_fill(BLUE_E, 0.15)
    handle = Line(ORIGIN, DR * 0.38, color=WHITE, stroke_width=7).shift(lens.point_at_angle(-PI / 4))
    return VGroup(lens, handle)


def calendar_page(text, total):
    page = RoundedRectangle(width=2.3, height=2.1, corner_radius=0.12).set_fill(PAPER, 1).set_stroke(width=0)
    band = Rectangle(width=2.3, height=0.45).set_fill(ERROR, 0.85).set_stroke(width=0).align_to(page, UP)
    rings = VGroup(*[Circle(radius=0.07).set_fill(GREY_D, 1).set_stroke(width=0).move_to(band.get_top() + RIGHT * x)
                     for x in (-0.6, 0.6)])
    label = Text(text, font_size=30, color=INK, weight=BOLD).move_to(page).shift(DOWN * 0.2)
    amount = Text(total, font_size=26, color=MONEY).next_to(page, DOWN, buff=0.2)
    return VGroup(page, band, rings, label, amount)


def checklist_item(text, font_size=26):
    box = Square(0.36).set_stroke(SCAFFOLD, 2)
    label = Text(text, font_size=font_size).next_to(box, RIGHT, buff=0.25)
    tick = checkmark(size=0.38).move_to(box)
    group = VGroup(box, label)
    group.tick = tick
    return group


class Filler(VGroup):
    """Gold rising inside a jar; `rate` is the share of the jar filled per second."""

    def __init__(self, pot, level=0.0, rate=0.0):
        super().__init__()
        self.pot, self.level, self.rate = pot, level, rate
        body = pot[0]
        self.max_height = body.height - 0.14
        self.rect = Rectangle(width=body.width - 0.2, height=0.02).set_fill(MONEY, 0.75).set_stroke(width=0)
        self.add(self.rect)
        self.redraw()
        self.add_updater(lambda m, dt: m.tick(dt))

    def tick(self, dt):
        self.level = min(1.0, self.level + self.rate * dt)
        self.redraw()

    def redraw(self):
        h = max(0.02, self.level * self.max_height)
        self.rect.stretch_to_fit_height(h)
        self.rect.move_to(self.pot[0].get_bottom() + UP * (0.07 + h / 2))


class SliverStream(VGroup):
    """Penny slivers flowing along an arc from start to end, forever (driven by an updater)."""

    def __init__(self, start, end, count=12, size=0.13, arc=1.2, speed=0.3, spread=0.05, seed=1, spin=2.0):
        super().__init__()
        rng = random.Random(seed)
        self.start, self.end = np.array(start, float), np.array(end, float)
        self.arc, self.speed, self.clock, self.spin = arc, speed, 0.0, spin
        self.offsets = [(i + rng.uniform(-0.3, 0.3)) / count for i in range(count)]
        self.jitter = [rng.uniform(-spread, spread) for _ in range(count)]
        for _ in range(count):
            self.add(sliver(size).rotate(rng.uniform(0, TAU)))
        self.place(0)
        self.add_updater(lambda m, dt: m.place(dt))

    def point(self, f):
        return self.start + (self.end - self.start) * f + UP * self.arc * 4 * f * (1 - f)

    def place(self, dt):
        self.clock += dt * self.speed
        for w, offset, jit in zip(self.submobjects, self.offsets, self.jitter):
            f = (self.clock + offset) % 1.0
            w.rotate(dt * self.spin)
            w.move_to(self.point(f) + UP * jit)
            w.set_opacity(max(0.0, min(1.0, f / 0.08, (1 - f) / 0.08)))


class Dust(VGroup):
    """Slivers drifting slowly about the frame like dust."""

    def __init__(self, count=34, seed=5, box=(6.2, 3.2)):
        super().__init__()
        rng = random.Random(seed)
        self.box = box
        self.velocity = []
        for _ in range(count):
            s = sliver(rng.uniform(0.08, 0.16)).rotate(rng.uniform(0, TAU))
            s.move_to([rng.uniform(-box[0], box[0]), rng.uniform(-box[1], box[1]), 0])
            s.set_opacity(rng.uniform(0.5, 0.9))
            self.add(s)
            self.velocity.append(np.array([rng.uniform(-0.25, 0.25), rng.uniform(-0.2, 0.2), 0]))
        self.add_updater(lambda m, dt: m.drift(dt))

    def drift(self, dt):
        for s, v in zip(self.submobjects, self.velocity):
            s.shift(v * dt)
            s.rotate(dt * 0.8)
            x, y = s.get_x(), s.get_y()
            if abs(x) > self.box[0]:
                v[0] = -v[0]
            if abs(y) > self.box[1]:
                v[1] = -v[1]


class BeltFlow(VGroup):
    """Account cards riding a conveyor belt from x0 to x1, speeding up to a blur."""

    def __init__(self, texts, x0, x1, y, speed=0.15, accel=0.0, top_speed=3.0):
        super().__init__()
        self.x0, self.x1, self.y = x0, x1, y
        self.speed, self.accel, self.top_speed, self.clock = speed, accel, top_speed, 0.0
        for t in texts:
            self.add(account_card(t, width=1.55, height=0.8))
        self.place(0)
        self.add_updater(lambda m, dt: m.place(dt))

    def place(self, dt):
        self.speed = min(self.top_speed, self.speed + self.accel * dt)
        self.clock += dt * self.speed
        n = len(self.submobjects)
        blur = min(1.0, self.speed / self.top_speed)
        for i, card in enumerate(self.submobjects):
            f = (self.clock + i / n) % 1.0
            card.move_to([self.x0 + (self.x1 - self.x0) * f, self.y, 0])
            edge = max(0.0, min(1.0, f / 0.06, (1 - f) / 0.06))
            card.set_opacity(edge * (1 - 0.55 * blur))


# ---------------------------------------------------------------- 7.1

class Segment_7_1(Segment):
    """Cold open: the heist, paraphrased, as our own diagram."""
    EPISODE, SEGMENT = 7, '7.1'

    def construct(self):
        # [V7.1a] black canvas, the film's name in plain type; no imagery from the film
        title = Text('Office Space (1999)', font_size=64)
        self.play(FadeIn(title, shift=UP * 0.2), run_time=1.2)

        # [V7.1b] three grey desks, each with a monitor
        self.at('Three fed-up employees')
        self.play(title.animate.scale(0.5).to_edge(UP, buff=0.3), run_time=0.8)
        desks = VGroup(*[desk() for _ in range(3)]).arrange(RIGHT, buff=1.1).move_to(UP * 1.45)
        self.play(LaggedStart(*[FadeIn(d, shift=UP * 0.3) for d in desks], lag_ratio=0.3), run_time=1.2)
        self.at('decide to get even')
        self.play(*[d.screen.animate.set_fill(ERROR, 0.35) for d in desks], run_time=0.6)

        # the virus goes into the company's accounting system: a vault of transactions
        self.at('slip a virus')
        vault = vault_icon('transactions').move_to(LEFT * 4.4 + DOWN * 1.75)
        pot = labelled_jar('our account').move_to(RIGHT * 4.4 + DOWN * 1.85)
        virus = label_box('virus', color=ERROR, font_size=22).move_to(desks[1].screen)
        self.play(FadeIn(vault), FadeIn(pot), FadeIn(virus, scale=0.5), run_time=0.8)
        self.play(virus.animate.scale(0.7).move_to(vault.box.get_center()), run_time=1.0)
        self.play(FadeOut(virus), vault.box.animate.set_stroke(ERROR, 3), run_time=0.4)

        # a thin gold stream of slivers from the vault to the jar
        self.at('Whenever a transaction leaves')
        fill = Filler(pot.pot, rate=0.012)
        stream = SliverStream(vault.box.get_right() + RIGHT * 0.15, pot.pot.get_top() + DOWN * 0.15,
                              count=12, arc=1.3, speed=0.28)
        self.add(fill, stream)
        self.at('less than a penny')
        inset = VGroup(sliver(0.32), Text('<', font_size=40), penny(0.32)).arrange(RIGHT, buff=0.3)
        inset.move_to(DOWN * 2.7)
        self.play(FadeIn(inset, shift=UP * 0.2), run_time=0.5)
        self.at('millions of transactions')
        stream.speed = 0.45
        fill.rate = 0.03

        # [V7.1c] the nod to Superman III, as a caption beside the stream
        self.at('Superman the Third')
        note = Text('see: Superman III', font_size=28, color=SCAFFOLD).move_to(DOWN * 2.7)
        self.play(FadeOut(inset), FadeIn(note, scale=0.8), run_time=0.5)

        # [V7.1d] the stream becomes a torrent and the jar overflows
        self.at("it goes wrong")
        torrent = SliverStream(vault.box.get_right() + RIGHT * 0.15, pot.pot.get_top() + DOWN * 0.15,
                               count=70, size=0.17, arc=1.3, speed=0.9, spread=0.28, seed=2, spin=5.0)
        self.add(torrent)
        fill.rate = 0.35

        # a red decimal point bounces across the screen and lands in the wrong place on a tag
        self.at('misplaces a decimal point')
        tag_box = RoundedRectangle(width=2.6, height=1.1, corner_radius=0.1).set_fill(MONEY, 1).set_stroke(width=0)
        hole = Circle(radius=0.07).set_fill(BLACK, 1).set_stroke(width=0).move_to(tag_box.get_left() + RIGHT * 0.22)
        old = Text('$4.35', font_size=48, color=BLACK, weight=BOLD)      # q07-04's first amount
        new = Text('$43.5', font_size=48, color=BLACK, weight=BOLD)
        tag = VGroup(tag_box, hole).move_to(UP * 1.4)
        old.move_to(tag_box).shift(RIGHT * 0.1)
        new.move_to(old)
        self.play(FadeOut(desks), FadeIn(tag), FadeIn(old), run_time=0.6)
        point = old[2]
        self.play(point.animate.set_color(ERROR).scale(1.6), run_time=0.3)
        target = new[3].get_center()
        path = bounce_path([point.get_center(), [-5.6, 0.2, 0], [-2.8, 0.2, 0], [0.4, 0.2, 0], [3.4, 0.2, 0],
                            [5.6, 0.6, 0], target], height=1.0)
        self.play(MoveAlongPath(point, path), old[3].animate.move_to(new[2]), run_time=2.6,
                  rate_func=rate_functions.linear)
        self.play(Indicate(point, color=ERROR, scale_factor=1.5), run_time=0.6)

        self.at('far too much money to explain')
        pennies, moves = spill(pot.pot, count=10)
        self.play(LaggedStart(*moves, lag_ratio=0.15), run_time=2.0)

        # the case study: rounding, money and a bug, then right or wrong
        self.at("It's a great film")
        self.play(FadeOut(VGroup(stream, torrent, fill, vault, pot, pennies, note, tag, old)), run_time=0.8)
        self.remove(stream, torrent, fill)
        self.at("doesn't owe anyone a code review")
        review = label_box('code review', font_size=32).move_to(UP * 2.4)
        no = crossmark(size=0.4).next_to(review, RIGHT, buff=0.3)
        self.play(FadeIn(review, shift=UP * 0.2), run_time=0.5)
        self.play(Create(no), run_time=0.4)
        self.at('a story about rounding')
        themes = VGroup(label_box('rounding', font_size=32), label_box('money', color=MONEY, font_size=32),
                        label_box('a bug', color=ERROR, font_size=32)).arrange(RIGHT, buff=0.7).move_to(DOWN * 0.1)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in themes], lag_ratio=0.35), run_time=1.4)
        self.at('the perfect case study')
        frame = SurroundingRectangle(themes, color=FOCUS, buff=0.25, corner_radius=0.12)
        study = Text('a case study', font_size=26, color=FOCUS).next_to(frame, UP, buff=0.12)
        self.play(Create(frame), FadeIn(study), run_time=0.8)
        self.at("So let's give it one anyway")
        yes = checkmark(size=0.45).move_to(no)
        self.play(ReplacementTransform(no, yes), review[0].animate.set_stroke(EXACT, 2), run_time=0.6)
        self.at('What did Office Space get right')
        right = VGroup(checkmark(size=0.5), Text('right?', font_size=40, color=EXACT)).arrange(RIGHT, buff=0.25)
        wrong = VGroup(crossmark(size=0.45), Text('wrong?', font_size=40, color=ERROR)).arrange(RIGHT, buff=0.25)
        verdict = VGroup(right, wrong).arrange(RIGHT, buff=2.0).move_to(DOWN * 2.3)
        self.play(FadeIn(right, shift=UP * 0.2), run_time=0.5)
        self.at('what did it get wrong')
        self.play(FadeIn(wrong, shift=UP * 0.2), run_time=0.5)
        self.finish()


# ---------------------------------------------------------------- 7.2

class Segment_7_2(Segment):
    """Where fractions of a penny come from (q07-01)."""
    EPISODE, SEGMENT = 7, '7.2'

    def construct(self):
        rows = snippet_output(Q1)
        interest, pay, left = field(rows[0], 'interest'), field(rows[0], 'pay'), field(rows[0], 'left')
        balance = Decimal(rows[0].split(':')[0].lstrip('$ '))

        # Do fractions of a penny exist? A penny, then its slices
        coin1 = penny(0.9).move_to(UP * 0.3)
        mark = Text('?', font_size=64, color=FOCUS).next_to(coin1, UR, buff=0.05)
        self.play(FadeIn(coin1, scale=0.6), FadeIn(mark), run_time=0.8)
        self.at('Absolutely')
        wedges = sliced_penny(8, 0.9, gap=0.14).move_to(coin1)
        self.play(FadeOut(mark), FadeOut(coin1), FadeIn(wedges, scale=1.1), run_time=0.7)
        self.play(Rotate(wedges, PI / 4), run_time=0.8)
        self.at('floating point has nothing')
        none = Text('no floating point involved', font_size=30, color=SCAFFOLD).next_to(wedges, DOWN, buff=0.5)
        self.play(FadeIn(none, shift=UP * 0.2))

        # [V7.2a] a passbook page: the balance and the rate
        self.at("Here's an example of our own")
        self.play(FadeOut(wedges), FadeOut(none), run_time=0.5)
        paper = RoundedRectangle(width=5.4, height=2.6, corner_radius=0.12).set_fill(PAPER, 1).set_stroke(width=0)
        head = Text('savings passbook', font_size=24, color=INK, weight=BOLD)
        line1 = MonoLine(f'balance  ${balance:,}', font_size=26, color=INK)
        line2 = MonoLine('rate     3.5 % a year', font_size=26, color=INK)
        daily = Text('interest worked out daily', font_size=20, color=GREY_D)
        stack_lines([line1, line2], spacing=1.8)
        book = VGroup(paper, head, line1, line2, daily)
        head.move_to(paper.get_top() + DOWN * 0.4)
        VGroup(line1, line2).move_to(paper).shift(DOWN * 0.05)
        daily.move_to(paper.get_bottom() + UP * 0.35)
        book.to_corner(UL, buff=0.5)
        self.play(FadeIn(VGroup(paper, head), shift=RIGHT * 0.3))
        self.at('a savings account paying')
        self.play(FadeIn(line2, shift=RIGHT * 0.2), run_time=0.6)
        self.at('with interest worked out daily')
        self.play(FadeIn(daily, shift=RIGHT * 0.2), run_time=0.6)
        self.play(Indicate(daily, color=FOCUS, scale_factor=1.15))
        self.at('A balance of twelve hundred')
        self.play(FadeIn(line1, shift=RIGHT * 0.2), run_time=0.6)
        self.play(Indicate(line1.chars(9), color=FOCUS), run_time=0.8)

        # [V7.2b] balance × 0.035 ÷ 365 unrolls as a long yellow decimal
        self.at('earns three and a half percent')
        calc = Text(f'${balance:,} × 0.035 ÷ 365 =', font_size=32).move_to(RIGHT * 3.3 + UP * 2.75)
        result = MonoLine(interest + '…', font_size=40, color=FOCUS)
        result.next_to(calc, DOWN, buff=0.45)
        self.play(Write(calc), run_time=1.2)
        self.at('every day')
        self.play(LaggedStart(*[FadeIn(g, shift=RIGHT * 0.1) for g in result.glyphs], lag_ratio=0.6), run_time=1.6)
        self.at('about eleven point eight cents')
        about = Text('≈ 11.8¢', font_size=34, color=FOCUS).next_to(result, DOWN, buff=0.3)
        self.play(FadeIn(about, scale=0.8), Indicate(result.chars(0, 6), color=FOCUS), run_time=0.8)

        # [V7.2c] a cent ruler: the amount snaps down to 11¢ and the sliver is cut off
        self.at('you can only pay whole cents')
        ruler = cent_ruler(0, 13, width=12.0, y=-2.4)
        amount = Decimal(interest) * 100                       # 11.838247 cents, from q07-01's output
        bar = span(ruler, 0, amount, FOCUS)
        self.play(FadeIn(ruler), run_time=0.6)
        self.play(GrowFromEdge(bar, LEFT), run_time=1.0)
        self.at('So the bank has to round')
        cut = cut_line(ruler, 11)
        self.play(Create(cut), run_time=0.5)
        self.at('if it pays eleven cents')
        paid = span(ruler, 0, 11, EXACT)
        piece = span(ruler, 11, amount, MONEY)
        self.remove(bar)
        self.add(paid, piece)
        pay_label = Text(f'pay {pay}', font_size=26, color=EXACT).next_to(paid, UP, buff=0.2)
        self.play(FadeIn(pay_label), run_time=0.5)
        self.at('the sliver is about eight tenths')
        self.play(piece.animate.shift(UP * 1.0 + RIGHT * 0.3), run_time=0.8)
        left_label = Text(left, font_size=28, color=MONEY).next_to(piece, UP, buff=0.15)
        self.play(FadeIn(left_label, shift=UP * 0.1), run_time=0.5)

        # [V7.2d] code panel and console; the leftover column glows; $10.01 pays nothing
        self.at('This code uses')
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        code = code_panel(snippet_lines(Q1, 5, 9), font_size=20)
        fit(code, 13.2).to_edge(UP, buff=0.3)
        out = output_console(Q1, font_size=20)
        out.next_to(code, DOWN, buff=0.3).to_edge(LEFT, buff=0.6)
        self.play(FadeIn(code), FadeIn(out.background), run_time=0.6)
        card = show_qr(self, 'q07-01')
        self.play(out.type_all(run_time_per_line=0.9))
        self.at('Every balance leaves')
        column = VGroup(*[line.chars(line.source.index('left')) for line in out.lines])
        glow = SurroundingRectangle(column, color=MONEY, buff=0.1, corner_radius=0.06)
        self.play(*[c.animate.set_color(MONEY) for c in column], Create(glow), run_time=0.8)
        self.at('a balance of ten dollars and one cent')
        last = out.lines[3]
        nothing = last.part(f'pay {field(rows[3], "pay")}')
        self.play(nothing.animate.set_color(ERROR), Indicate(last.chars(0, 9), color=FOCUS), run_time=0.8)
        note = Text('pays nothing: its whole interest is a sliver', font_size=26, color=MONEY)
        note.next_to(out, DOWN, buff=0.35).align_to(out, LEFT)
        arrow = Arrow(note.get_top() + RIGHT * 1.0, last.get_bottom() + DOWN * 0.02 + LEFT * 1.0, buff=0.08,
                      color=MONEY, stroke_width=3, max_tip_length_to_length_ratio=0.25)
        self.play(FadeIn(note, shift=UP * 0.15), GrowArrow(arrow), run_time=0.7)

        # every kind of money arithmetic sheds slivers; someone has to decide what happens to them
        self.at("So the film's premise is sound")
        hide_qr(self, card)
        self.play(FadeOut(VGroup(code, out, glow, note, arrow)), run_time=0.6)
        self.at('Percentages, interest')
        kinds = VGroup(*[label_box(k, font_size=24) for k in
                         ('percentages', 'interest', 'currency conversion', 'fees', 'taxes')])
        kinds.arrange(RIGHT, buff=0.3).move_to(UP * 1.6)
        fit(kinds, 13.2)
        pile_spot = DOWN * 1.6
        drops = []
        for k, box in enumerate(kinds):
            s = sliver(0.26).move_to(box.get_bottom() + DOWN * 0.3)
            drops.append(Succession(FadeIn(box, shift=DOWN * 0.2, run_time=0.4),
                                    FadeIn(s, run_time=0.1),
                                    s.animate(run_time=0.6).move_to(pile_spot + RIGHT * (k - 2) * 0.28)
                                    .rotate(k)))
        self.play(LaggedStart(*drops, lag_ratio=0.45), run_time=4.0)
        self.at('someone has to decide')
        decide = Text('?', font_size=72, color=FOCUS).next_to(pile_spot, UP, buff=0.3)
        ep6 = Text('Episode 6 · Rounding is a policy', font_size=26, color=SCAFFOLD).move_to(DOWN * 2.8)
        self.play(FadeIn(decide, scale=0.6), FadeIn(ep6, shift=UP * 0.2), run_time=0.8)
        self.finish()


# ---------------------------------------------------------------- 7.3

class Segment_7_3(Segment):
    """The scheme as code (q07-02)."""
    EPISODE, SEGMENT = 7, '7.3'

    def construct(self):
        # [V7.3a] the virus's loop
        code = code_panel(snippet_lines(Q2, 12, 17), font_size=19)
        fit(code, 13.4).to_edge(UP, buff=0.3)
        self.play(FadeIn(code), run_time=0.8)
        self.at("so here's our own version")
        loop = SurroundingRectangle(code.code_lines, color=FOCUS, buff=0.08, corner_radius=0.05)
        self.play(Create(loop), run_time=0.8)
        self.at('only a few lines long')
        self.play(FadeOut(loop), run_time=0.4)

        # [V7.3b] a conveyor belt of account cards and a cutting station labelled "truncate"
        self.at('For a hundred thousand accounts')
        belt_y, station_x = -0.95, -0.4
        belt = RoundedRectangle(width=10.6, height=0.18, corner_radius=0.09).set_fill(GREY_D, 1).set_stroke(width=0)
        belt.move_to([-1.5, belt_y, 0])
        rollers = VGroup(*[Circle(radius=0.11).set_stroke(GREY_B, 2).move_to([x, belt_y - 0.22, 0])
                           for x in np.arange(-6.4, 3.6, 0.9)])
        station = label_box('truncate', color=FOCUS, font_size=24).move_to([station_x, 0.75, 0])
        blade = Line(station.get_bottom(), station.get_bottom() + DOWN * 0.15, color=WHITE, stroke_width=5)
        bin_ = VGroup(Line(LEFT * 0.8 + UP * 0.65, LEFT * 0.8 + DOWN * 0.65), Line(LEFT * 0.8 + DOWN * 0.65, RIGHT * 0.8 + DOWN * 0.65),
                      Line(RIGHT * 0.8 + DOWN * 0.65, RIGHT * 0.8 + UP * 0.65)).set_stroke(EXACT, 4)
        bin_.move_to([5.4, belt_y - 0.2, 0])
        bin_label = Text('paid to people', font_size=22, color=EXACT).next_to(bin_, DOWN, buff=0.15)
        hidden = labelled_jar('hidden account', width=1.2, height=1.25, color=MONEY, font_size=22)
        hidden.move_to([station_x, -2.75, 0])
        self.play(FadeIn(VGroup(belt, rollers)), FadeIn(station), FadeIn(blade), FadeIn(bin_), FadeIn(bin_label),
                  FadeIn(hidden), run_time=0.8)
        balance = seeded_balances(1)[0]                    # q07-02's first account (computed here)
        interest, paid, _ = slice_cents(balance)
        card = account_card(f'${balance:,}').move_to([-5.4, belt_y + 0.55, 0])
        self.highlight = line_highlight(code, 1)
        self.play(FadeIn(card, shift=RIGHT * 0.3), Create(self.highlight), run_time=0.5)
        self.play(card.animate.move_to([station_x, belt_y + 0.55, 0]), run_time=1.2)

        self.at("work out a day's interest")
        self.move_highlight(code, 2)
        interest_text = Text(f'{interest:.8f}', font_size=22, color=FOCUS).move_to(card[1])
        self.play(FadeOut(card[1]), FadeIn(interest_text), run_time=0.6)
        card.remove(card[1])
        card.add(interest_text)
        self.at('Truncate it to the cent')
        self.move_highlight(code, 3)
        chip = label_box(f'{paid}', color=EXACT, font_size=22).move_to(card.get_center() + LEFT * 0.35)
        bit = sliver(0.28).move_to(card.get_center() + RIGHT * 0.7)
        self.play(blade.animate.put_start_and_end_on(station.get_bottom(), [station_x, belt_y + 0.1, 0]), run_time=0.3)
        self.play(ReplacementTransform(card, VGroup(chip, bit)),
                  blade.animate.put_start_and_end_on(station.get_bottom(), station.get_bottom() + DOWN * 0.15),
                  run_time=0.6)
        self.at('Pay the customer')
        self.move_highlight(code, 4)
        self.play(chip.animate.move_to(bin_.get_center() + DOWN * 0.25).scale(0.8), run_time=1.0)
        self.at('put the slice')
        self.move_highlight(code, 5)
        self.play(bit.animate.move_to(hidden.pot[0].get_bottom() + UP * 0.25), run_time=0.8)

        # [V7.3c] the belt speeds up to a blur; the counter reaches 100,000
        self.at('After one day')
        self.play(FadeOut(self.highlight), run_time=0.3)
        texts = [f'${b:,}' for b in seeded_balances(7)[1:]]
        flow = BeltFlow(texts, -6.3, 4.4, belt_y + 0.5, speed=0.12, accel=0.5, top_speed=1.6)
        drip = SliverStream([station_x, belt_y, 0], hidden.pot.get_top() + DOWN * 0.2, count=6, size=0.12,
                            arc=0.0, speed=0.9, spread=0.03)
        count = number(0, font_size=36, color=WHITE, commas=True)
        count_label = Text('accounts', font_size=26, color=SCAFFOLD)
        counter = VGroup(count_label, count).arrange(RIGHT, buff=0.25).move_to([-4.4, 0.6, 0])
        count.add_updater(lambda m: m.next_to(count_label, RIGHT, buff=0.25))
        self.add(flow, drip, counter)
        self.play(ChangeDecimalToValue(count, 100_000), run_time=3.5, rate_func=rate_functions.ease_in_quad)
        count.clear_updaters()

        # [V7.3d] the console prints; 500.88 and 0.501 cents are highlighted
        self.at('the customers have been paid')
        self.play(FadeOut(VGroup(flow, drip, belt, rollers, station, blade, bin_, bin_label, hidden, chip, bit, counter)),
                  run_time=0.6)
        self.remove(flow, drip)
        out = output_console(Q2, font_size=24)
        out.next_to(code, DOWN, buff=0.4).to_edge(LEFT, buff=0.6)
        self.play(FadeIn(out.background), run_time=0.3)
        card = show_qr(self, 'q07-02')
        self.play(out.type_line(0), run_time=0.7)
        self.play(out.type_line(1), run_time=0.7)
        self.at('And the hidden account holds')
        self.play(out.type_line(2), run_time=0.7)
        skim = out.part(2, field(out.lines[2].source, 'account:'))
        self.play(skim.animate.set_color(MONEY), Create(SurroundingRectangle(skim, color=MONEY, buff=0.08)), run_time=0.6)
        self.at('The average slice')
        self.play(out.type_line(3), run_time=0.7)
        avg = out.lines[3].chars(out.lines[3].source.index('0.'))
        self.play(avg.animate.set_color(FOCUS), Create(SurroundingRectangle(avg, color=FOCUS, buff=0.08)), run_time=0.6)

        # slices spread evenly between nothing and a cent average half a cent
        self.at('That makes sense')
        hide_qr(self, card)
        ruler = FloatLine(0, 1, width=5.6, ticks=[0, Fraction(1, 2), 1], labels={0: '0¢', Fraction(1, 2): '½¢', 1: '1¢'},
                          color=SCAFFOLD, label_size=22).move_to([3.4, -2.2, 0])
        self.play(FadeIn(ruler), run_time=0.5)
        # the slices of the first 40 seeded accounts (q07-02's own data, computed here)
        slices = [float(slice_cents(b)[2]) for b in seeded_balances(40)]
        bins = {}
        dots = VGroup()
        for s in slices:
            k = min(9, int(s * 10))
            level = bins.get(k, 0)
            bins[k] = level + 1
            dots.add(sliver(0.12).move_to(ruler.point(s) + UP * (0.3 + 0.18 * level)))
        self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.6) for d in dots], lag_ratio=0.08), run_time=2.6)
        self.at('their average is half a cent')
        mean = sum(slices) / len(slices)
        pointer = Arrow(ruler.point(mean) + UP * 2.1, ruler.point(mean) + UP * 1.3, buff=0, color=FOCUS)
        avg_text = Text('average ≈ ½¢', font_size=28, color=FOCUS).next_to(pointer, UP, buff=0.1)
        self.play(GrowArrow(pointer), FadeIn(avg_text), run_time=0.7)
        self.at('every single day')
        self.play(Indicate(out.lines[2], color=MONEY), run_time=0.8)
        self.finish()

    def move_highlight(self, code, index):
        self.play(self.highlight.animate.become(line_highlight(code, index)), run_time=0.3)


# ---------------------------------------------------------------- 7.4

class Segment_7_4(Segment):
    """Right: tiny times enormous."""
    EPISODE, SEGMENT = 7, '7.4'

    def construct(self):
        half_cent = Decimal('0.005')            # q07-02's average slice, 0.501 cents, as ½¢

        # [V7.4a] a single gold sliver, ½¢
        one = sliver(1.0).move_to(UP * 0.4)
        half = Text('½¢', font_size=44, color=MONEY).next_to(one, DOWN, buff=0.3)
        self.play(FadeIn(one, scale=0.4), FadeIn(half), run_time=0.8)
        self.at('Tiny amounts times enormous volume')
        self.play(Rotate(one, PI / 3), run_time=0.8)

        # [V7.4b] the sliver multiplies into a grid that zooms out
        self.at('Half a cent from a hundred thousand accounts')
        centre = LEFT * 3.4 + UP * 0.6
        grid = VGroup(*[sliver(0.11) for _ in range(100)]).arrange_in_grid(10, 10, buff=0.16).move_to(centre)
        self.play(FadeOut(half), LaggedStart(*[TransformFromCopy(one, s) for s in grid], lag_ratio=0.01),
                  FadeOut(one), run_time=1.6)
        field1 = self.tile_field(centre, 3.4)
        self.play(grid.animate.scale_to_fit_width(field1[0].width).move_to(field1[0]), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(t) for t in field1[1:]], lag_ratio=0.01), run_time=1.0)
        self.at('about five hundred dollars a day')
        day1 = Text(f'100,000 × ½¢ = ${100_000 * half_cent:,.0f} a day', font_size=30, color=MONEY)   # 500
        day1.move_to(RIGHT * 3.4 + UP * 2.6)
        self.play(FadeIn(day1, shift=LEFT * 0.2), run_time=0.6)
        self.at('A bank with ten million accounts')
        field2 = self.tile_field(centre, 3.4, opacity=0.75)
        self.play(VGroup(grid, field1).animate.scale_to_fit_width(field2[0].width).move_to(field2[0]), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(t) for t in field2[1:]], lag_ratio=0.01), run_time=1.0)
        self.at('about fifty thousand dollars a day')
        day2 = Text(f'10,000,000 × ½¢ ≈ ${10_000_000 * half_cent:,.0f} a day', font_size=30, color=MONEY)  # 50,000
        day2.next_to(day1, DOWN, buff=0.35)
        self.play(FadeIn(day2, shift=LEFT * 0.2), run_time=0.6)

        # [V7.4c] a calendar flips: a week, a month, a year (totals computed from $50,000 a day)
        self.at('every day, and')
        per_day = 10_000_000 * half_cent
        pages = [('a day', per_day), ('a week', per_day * 7), ('a month', per_day * 30), ('a year', per_day * 365)]
        cal = calendar_page(pages[0][0], f'≈ ${pages[0][1]:,.0f}').move_to(RIGHT * 3.4 + DOWN * 0.7)
        self.play(FadeIn(cal, shift=UP * 0.2), run_time=0.5)
        for name, total in pages[1:]:
            nxt = calendar_page(name, f'≈ ${total:,.0f}').move_to(cal)
            self.play(cal.animate.shift(UP * 0.3).set_opacity(0), FadeIn(nxt, shift=UP * 0.3), run_time=0.55)
            self.remove(cal)
            cal = nxt
        self.at('every individual customer')
        short = account_card('each customer: short by less than 1¢', width=6.0, height=0.75, color=SCAFFOLD)
        short.move_to(LEFT * 3.4 + DOWN * 2.6)
        self.play(FadeIn(short, shift=UP * 0.2), run_time=0.6)
        self.at('No one would ever check')
        tick = checkmark(color=SCAFFOLD, size=0.35).next_to(short, RIGHT, buff=0.2)
        self.play(Create(tick), run_time=0.5)

        # [V7.4d] the jar returns with the film's figure, and the estimate
        self.at('In the film, the account holds')
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        pot = labelled_jar('our account', width=2.0, height=2.4).move_to(LEFT * 3.6 + DOWN * 0.8)
        fill = Filler(pot.pot, level=0.0, rate=0.0)
        film = Text('the film: over $300,000 in a few days', font_size=32, color=MONEY).move_to(RIGHT * 2.6 + UP * 2.2)
        self.play(FadeIn(pot), FadeIn(film, shift=DOWN * 0.2), run_time=0.7)
        self.add(fill)
        self.play(UpdateFromAlphaFunc(fill, lambda m, a: setattr(m, 'level', 0.85 * a)), run_time=1.5)
        self.at('around sixty million slices')
        slices = Decimal(300_000) / half_cent           # 60,000,000
        estimate = Text(f'$300,000 ÷ ½¢ ≈ {slices / 1_000_000:.0f} million slices', font_size=32)
        estimate.move_to(RIGHT * 2.6 + UP * 0.6)
        self.play(Write(estimate), run_time=1.2)
        self.at('slow and invisible')
        source = pot.pot.get_top() + UP * 4.2
        trickle = SliverStream(source, pot.pot.get_top() + DOWN * 0.2, count=4, size=0.12, arc=0.0, speed=0.25,
                               spread=0.02, seed=6)
        self.add(trickle)
        self.at('fast and enormous')
        torrent = SliverStream(source, pot.pot.get_top() + DOWN * 0.2, count=40, size=0.15, arc=0.0,
                               speed=1.0, spread=0.3, seed=4, spin=5.0)
        fill.rate = 0.2
        self.remove(trickle)
        self.add(torrent)
        pennies, moves = spill(pot.pot, count=8, seed=8)
        self.wait(0.6)
        self.play(LaggedStart(*moves, lag_ratio=0.15), run_time=1.8)
        self.at('So the arithmetic of the scheme holds up')
        self.remove(torrent)
        tick = checkmark(size=0.5).next_to(estimate, RIGHT, buff=0.3)
        self.play(Create(tick), run_time=0.5)
        self.at("that there's always a slice to take")
        doubt = VGroup(sliver(0.45), Text('always a slice?', font_size=32, color=FOCUS)).arrange(RIGHT, buff=0.35)
        doubt.next_to(estimate, DOWN, buff=1.0)
        self.play(FadeIn(doubt, shift=UP * 0.2), run_time=0.6)
        self.finish()

    @staticmethod
    def tile_field(centre, size, opacity=0.55):
        """A 10 × 10 field of gold tiles; tile 0 is where the previous view shrinks to."""
        cell = size / 10
        tiles = VGroup(*[Square(cell * 0.86).set_fill(MONEY, opacity).set_stroke(MONEY, 1) for _ in range(100)])
        tiles.arrange_in_grid(10, 10, buff=cell * 0.14).move_to(centre)
        return tiles


# ---------------------------------------------------------------- 7.5

class Segment_7_5(Segment):
    """Wrong: round to nearest, and the slices cancel (q07-03)."""
    EPISODE, SEGMENT = 7, '7.5'

    def construct(self):
        # [V7.5a] the cent ruler; under truncation every amount goes left and drops a sliver
        mode = Text('truncate', font_size=36, color=FOCUS).to_edge(UP, buff=0.4)
        ruler = cent_ruler(10, 14, width=11.0, y=0.9, label_size=22)
        # Fractional cents of the first seeded accounts (q07-03's data, computed here), one per
        # cell pair, plus 11.838¢ from q07-01 (the narration's "eleven point eight cents").
        fractions = [slice_cents(b)[2] for b in seeded_balances(8)]
        q1_amount = Decimal(field(snippet_output(Q1)[0], 'interest')) * 100
        values = [10 + fractions[0], 10 + fractions[1], 11 + fractions[2], q1_amount,
                  12 + fractions[3], 12 + fractions[4], 13 + fractions[5], 13 + fractions[7]]
        dots = VGroup(*[Dot(ruler.point(v) + UP * 0.55, radius=0.09, color=FOCUS) for v in values])
        special = values.index(q1_amount)
        tag = Text('11.8¢', font_size=22, color=FOCUS).next_to(dots[special], UP, buff=0.15)
        pot = labelled_jar('the jar', width=1.8, height=1.6, color=MONEY).move_to(DOWN * 2.3)
        self.play(FadeIn(mode), FadeIn(ruler), FadeIn(pot), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.1), FadeIn(tag), run_time=1.0)
        self.at('Every interest payment is rounded down')
        arrows, bars = VGroup(), VGroup()
        for v, d in zip(values, dots):
            low = int(v)
            arrows.add(CurvedArrow(d.get_center() + LEFT * 0.08, ruler.point(low) + UP * 0.25, angle=PI / 3,
                                   color=FOCUS, stroke_width=3, tip_length=0.15))
            bars.add(span(ruler, low, v, MONEY, height=0.16, lift=0.04))
        self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.1), FadeIn(bars), run_time=1.4)
        self.at('they all pile up on one side')
        inside = self.jar_spots(pot.pot, len(bars))
        self.play(LaggedStart(*[b.animate.become(sliver(0.16).move_to(p)) for b, p in zip(bars, inside)],
                              lag_ratio=0.12), run_time=1.8)
        kept = bars

        # [V7.5b] half-up: lower half goes left (sliver in), upper half goes right (sliver out)
        self.at('They round to the nearest cent')
        half_up = Text('half-up', font_size=36, color=FOCUS).move_to(mode)
        mids = VGroup(*[DashedLine(ruler.point(k + Fraction(1, 2)) + DOWN * 0.15, ruler.point(k + Fraction(1, 2)) + UP * 0.15,
                                   color=SCAFFOLD, stroke_width=2, dash_length=0.05) for k in range(10, 14)])
        self.play(FadeOut(arrows), FadeOut(kept), ReplacementTransform(mode, half_up), Create(mids), run_time=0.8)
        self.at('something different happens')
        lower = [i for i, v in enumerate(values) if v - int(v) < Decimal('0.5')]
        upper = [i for i in range(len(values)) if i not in lower]
        down_arrows, in_bars = VGroup(), VGroup()
        for i in lower:
            v = values[i]
            down_arrows.add(CurvedArrow(dots[i].get_center() + LEFT * 0.08, ruler.point(int(v)) + UP * 0.25,
                                        angle=PI / 3, color=FOCUS, stroke_width=3, tip_length=0.15))
            in_bars.add(span(ruler, int(v), v, MONEY, height=0.16, lift=0.04))
        self.play(LaggedStart(*[Create(a) for a in down_arrows], lag_ratio=0.1), FadeIn(in_bars), run_time=1.0)
        spots = self.jar_spots(pot.pot, 8)
        self.play(LaggedStart(*[b.animate.become(sliver(0.16).move_to(p)) for b, p in zip(in_bars, spots)],
                              lag_ratio=0.12), run_time=1.4)
        self.at('rounds up to twelve')
        up_arrows = VGroup()
        for i in upper:
            v = values[i]
            up_arrows.add(CurvedArrow(dots[i].get_center() + RIGHT * 0.08, ruler.point(int(v) + 1) + UP * 0.25,
                                      angle=-PI / 3, color=EXACT, stroke_width=3, tip_length=0.15))
        k = upper.index(special)
        self.play(Create(up_arrows[k]), Indicate(tag, color=EXACT), run_time=0.8)
        self.at('the bank gives away')
        out_bars = VGroup(*[span(ruler, values[i], int(values[i]) + 1, MONEY, height=0.16, lift=0.04) for i in upper])
        sources = VGroup(*[sliver(0.16).move_to(p) for p in spots[len(in_bars):len(in_bars) + len(upper)]])
        self.play(FadeIn(sources), run_time=0.3)
        self.play(ReplacementTransform(sources[k], out_bars[k]), run_time=0.9)
        rest = [j for j in range(len(upper)) if j != k]
        self.play(*[Create(up_arrows[j]) for j in rest], run_time=0.6)
        self.play(*[ReplacementTransform(sources[j], out_bars[j]) for j in rest], run_time=0.9)

        # [V7.5c] code panel and console: both rows
        self.at('Run the same hundred thousand accounts')
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        code = code_panel(snippet_find(Q3, 'for name, mode in', 'slices = [', 'kept = sum', 'given = -sum'), font_size=20)
        fit(code, 13.2).to_edge(UP, buff=0.3)
        out = output_console(Q3, font_size=20)
        out.next_to(code, DOWN, buff=0.3).to_edge(LEFT, buff=0.6)
        self.play(FadeIn(code), FadeIn(out.background), run_time=0.6)
        card = show_qr(self, 'q07-03')
        self.play(out.type_line(0), run_time=1.0)
        self.play(out.lines[0].glyphs.animate.set_color(ERROR), run_time=0.4)
        self.at('The amounts that round down')
        self.play(out.type_line(1), run_time=1.0)
        keeps = out.part(1, 'keeps  125.18')
        self.play(keeps.animate.set_color(MONEY), run_time=0.4)
        self.at('need about a hundred and twenty-four')
        gives = out.part(1, 'gives  124.59')
        self.play(gives.animate.set_color(MONEY), run_time=0.4)

        # [V7.5d] the half-up jar is nearly empty; 0.59 rattles at the bottom
        self.at('Net: fifty-nine cents')
        self.play(out.lines[1].glyphs.animate.set_color(EXACT), run_time=0.4)
        full = labelled_jar('truncate', width=1.6, height=1.7)
        empty = labelled_jar('half-up', width=1.6, height=1.7)
        VGroup(full, empty).arrange(RIGHT, buff=1.6).move_to(LEFT * 3.6 + DOWN * 2.3)
        full_fill = Filler(full.pot, level=0.9)
        full_fill.clear_updaters()
        big = Text(field(out.lines[0].source, 'net'), font_size=30, color=ERROR).next_to(full.pot, UP, buff=0.2)
        small = Text(field(out.lines[1].source, 'net'), font_size=22, color=EXACT)
        small.move_to(empty.pot[0].get_bottom() + UP * 0.25)
        self.play(FadeIn(full), FadeIn(full_fill), FadeIn(empty), run_time=0.6)
        self.play(FadeIn(big), FadeIn(small), run_time=0.4)
        self.play(Wiggle(small, scale_value=1.3, rotation_angle=0.15 * TAU, n_wiggles=6), run_time=1.4)
        self.at('For a hundred thousand accounts')
        self.play(Wiggle(small, scale_value=1.2, rotation_angle=0.1 * TAU, n_wiggles=6), run_time=1.2)
        self.at('essentially noise')
        self.play(Wiggle(small, scale_value=1.2, rotation_angle=0.1 * TAU, n_wiggles=6), run_time=1.2)

        # collecting only the positive slices unbalances what was meant to cancel
        self.at('So under round to nearest')
        hide_qr(self, card)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        scale = balance_scale(width=4.0).scale(1.2).move_to(UP * 0.2)
        pans = scale.beam[1]
        plus = VGroup(*[sliver(0.2) for _ in range(4)]).arrange(RIGHT, buff=0.08)
        minus = VGroup(*[sliver(0.2) for _ in range(4)]).arrange(RIGHT, buff=0.08)
        plus.next_to(pans[0][2], UP, buff=0.02)
        minus.next_to(pans[1][2], UP, buff=0.02)
        labels = VGroup(Text('rounded down: bank keeps', font_size=22, color=MONEY),
                        Text('rounded up: bank gives', font_size=22, color=MONEY))
        labels[0].next_to(pans[0], DOWN, buff=0.35)
        labels[1].next_to(pans[1], DOWN, buff=0.35)
        pans[1].add(minus)
        self.play(FadeIn(scale), FadeIn(plus), FadeIn(labels), run_time=0.8)
        self.at('no pile of free fractions')
        level = Text('they cancel', font_size=28, color=EXACT).next_to(scale, UP, buff=0.3)
        self.play(FadeIn(level), run_time=0.5)
        self.at('collects only the positive slices')
        virus = label_box('virus', color=ERROR, font_size=26).move_to(LEFT * 5.2 + UP * 2.2)
        self.play(FadeIn(virus), FadeOut(level), run_time=0.4)
        self.play(LaggedStart(*[p.animate.move_to(virus.get_center()).scale(0.5).set_opacity(0) for p in plus],
                              lag_ratio=0.15), run_time=1.2)
        self.remove(plus)
        self.play(tip_scale(scale, -0.22), labels[1].animate.shift(DOWN * 0.45), run_time=0.8)
        self.at('balance against the negative ones')
        self.play(Indicate(minus, color=ERROR), run_time=0.8)
        self.finish()

    @staticmethod
    def jar_spots(pot, n):
        body = pot[0]
        base = body.get_bottom() + UP * 0.25
        return [base + RIGHT * (((k % 4) - 1.5) * 0.32) + UP * (k // 4) * 0.22 for k in range(n)]


# ---------------------------------------------------------------- 7.6

class Segment_7_6(Segment):
    """Wrong: fractions don't vanish (q07-05's ledger)."""
    EPISODE, SEGMENT = 7, '7.6'

    def construct(self):
        # fractions of a penny as dust
        dust = Dust()
        self.add(dust)
        self.play(FadeIn(dust), run_time=1.0)
        self.at('Too small to belong to anyone')
        pot = labelled_jar('yours?', width=1.4, height=1.6, color=SCAFFOLD).move_to(DOWN * 2.0)
        self.play(FadeIn(pot), run_time=0.5)
        self.at('might as well belong to you')
        dust.clear_updaters()
        spots = [pot.pot[0].get_center() + RIGHT * ((k % 5) - 2) * 0.2 + UP * ((k // 5) * 0.15 - 0.4)
                 for k in range(len(dust))]
        self.play(LaggedStart(*[s.animate.move_to(p) for s, p in zip(dust, spots)], lag_ratio=0.03), run_time=1.8)

        # [V7.6a] the ledger: interest expense, customers, acct 1999, with the scale above
        self.at("Real accounting doesn't work that way")
        self.play(FadeOut(dust), FadeOut(pot), run_time=0.5)
        rows = snippet_output(Q1)
        interest, pay = field(rows[0], 'interest'), field(rows[0], 'pay')
        rest = str(Decimal(interest) - Decimal(pay))           # 0.00838247: the slice in dollars
        book = ledger([('interest expense', interest)], [('customers', pay), ('acct 1999', rest)],
                      width=12.6, font_size=20, headings=('Debits', 'Credits'))
        book.to_edge(UP, buff=0.35)
        amounts = [book.left[0].part(interest), book.right[0].part(pay), book.right[1].part(rest)]
        for a in amounts:
            a.set_opacity(0)
        self.play(FadeIn(book), run_time=1.0)
        self.at('every amount that leaves one account')
        flow = CurvedArrow(book.left[0].get_right() + DOWN * 0.15, book.right[0].get_left() + DOWN * 0.15,
                           angle=PI / 4, color=FOCUS, stroke_width=3, tip_length=0.15)
        self.play(Create(flow), run_time=0.8)
        self.at('the two sides must always add up')
        self.play(tip_scale(book.balance, 0.12), run_time=0.4)
        self.play(tip_scale(book.balance, -0.12), run_time=0.5)
        self.play(FadeOut(flow), run_time=0.3)

        # [V7.6b] one account's interest as a gold bar: cents to customers, sliver to acct 1999
        self.at('If the bank pays out interest')
        whole = 3.0
        gold = Rectangle(width=whole, height=0.3).set_fill(MONEY, 1).set_stroke(width=0)
        gold.move_to(amounts[0])
        self.play(amounts[0].animate.set_opacity(1).set_color(MONEY), FadeIn(gold, scale=0.6), run_time=0.6)
        self.play(gold.animate.move_to(DOWN * 2.6), run_time=0.8)
        cents_w = whole * float(Decimal(pay) / Decimal(interest))
        left_part = Rectangle(width=cents_w, height=0.3).set_fill(MONEY, 1).set_stroke(width=0)
        right_part = Rectangle(width=whole - cents_w, height=0.3).set_fill(MONEY, 1).set_stroke(width=0)
        left_part.move_to(gold.get_left(), aligned_edge=LEFT)
        right_part.move_to(gold.get_right(), aligned_edge=RIGHT)
        self.remove(gold)
        self.add(left_part, right_part)
        self.play(left_part.animate.shift(LEFT * 0.2), right_part.animate.shift(RIGHT * 0.3), run_time=0.5)
        self.at('every last fraction of it')
        self.play(left_part.animate.move_to(amounts[1]).scale(0.4).set_opacity(0),
                  amounts[1].animate.set_opacity(1), run_time=0.9)
        self.play(right_part.animate.move_to(amounts[2]).set_opacity(0),
                  amounts[2].animate.set_opacity(1).set_color(MONEY), run_time=0.9)
        level = Text('balanced', font_size=24, color=EXACT).next_to(book.balance, RIGHT, buff=0.4)
        self.play(FadeIn(level), run_time=0.4)

        # [V7.6c] a thousand customers: the q07-05 ledger, and the books balance
        self.at('on a thousand customers')
        out = output_console(Q5, font_size=22)
        out.next_to(book, DOWN, buff=0.35)
        self.play(FadeIn(out.background), run_time=0.3)
        self.play(out.type_line(0), run_time=0.8)
        self.at('The customers got the truncated amounts')
        self.play(out.type_line(1), run_time=0.6)
        self.at('called nineteen ninety-nine')
        self.play(out.type_line(2), run_time=0.8)
        self.play(out.lines[2].glyphs.animate.set_color(MONEY), run_time=0.4)
        self.at('Add it all up')
        self.play(out.type_line(3), run_time=0.8)
        self.play(out.lines[3].glyphs.animate.set_color(EXACT), tip_scale(book.balance, 0.06), run_time=0.4)
        self.play(tip_scale(book.balance, -0.06), Indicate(level, color=EXACT), run_time=0.5)

        # [V7.6d] a magnifier recomputes each customer; shortfalls flash red and point at acct 1999
        self.at('So balancing alone')
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        acct = label_box('acct 1999', color=MONEY, font_size=30).move_to(RIGHT * 4.0 + UP * 0.2)
        grows = Text('grows every day', font_size=22, color=SCAFFOLD).next_to(acct, DOWN, buff=0.2)
        self.at('a real, named account')
        self.play(FadeIn(acct, scale=0.8), run_time=0.6)
        self.at('for no business reason')
        self.play(FadeIn(grows), acct.animate.scale(1.1), run_time=0.6)
        # First eight q07-05 customers: paid (truncated) vs owed (the bank's rule, half-up),
        # recomputed here exactly as q07-05 does.
        heading = MonoLine('customer   paid   owed', font_size=24, color=SCAFFOLD)
        lines, short = [heading], []
        for k, b in enumerate(seeded_balances(8)):
            exact = (b * DAILY).quantize(TINY)
            paid = exact.quantize(CENT, ROUND_DOWN)
            owed = exact.quantize(CENT, ROUND_HALF_UP)
            lines.append(MonoLine(f'   #{k + 1:<5} {paid:>5}  {owed:>5}', font_size=24))
            short.append(owed > paid)
        table = stack_lines(lines, spacing=1.7)
        table.move_to(LEFT * 3.4 + DOWN * 0.3)
        title = Text("recompute: the bank's own rule", font_size=24, color=FOCUS).next_to(table, UP, buff=0.35)
        self.at('Recompute each customer')
        self.play(FadeIn(table), FadeIn(title), run_time=0.7)
        lens = magnifier().move_to(lines[1].get_right() + RIGHT * 0.5)
        self.play(FadeIn(lens), run_time=0.3)
        self.at('compare it with what they were actually paid')
        flashes = VGroup()
        for row, bad in zip(lines[1:], short):
            self.play(lens.animate.move_to(row.get_right() + RIGHT * 0.5), run_time=0.35)
            if bad:
                minus = Text('−1¢', font_size=24, color=ERROR).next_to(row, RIGHT, buff=1.0)
                ray = Arrow(minus.get_right(), acct.get_left(), buff=0.15, color=ERROR, stroke_width=3,
                            max_tip_length_to_length_ratio=0.08)
                self.play(row.glyphs.animate.set_color(ERROR), FadeIn(minus), GrowArrow(ray), run_time=0.45)
                flashes.add(minus, ray)
        self.at('all of them pointing at the same place')
        self.play(acct[0].animate.set_stroke(ERROR, 4).set_fill(ERROR, 0.3), acct[1].animate.set_color(ERROR),
                  FadeOut(lens), run_time=0.6)
        self.play(Indicate(acct, color=ERROR), run_time=0.8)

        # reconciliation: two independent calculations, compared
        self.at('two independent calculations')
        recon = Text('reconciliation: two calculations, compared', font_size=30, color=EXACT).to_edge(UP, buff=0.4)
        paid_col = SurroundingRectangle(VGroup(*[r.chars(10, 16) for r in lines[1:]]), color=STORED, buff=0.08)
        owed_col = SurroundingRectangle(VGroup(*[r.chars(17) for r in lines[1:]]), color=FOCUS, buff=0.08)
        self.play(FadeIn(recon, shift=DOWN * 0.2), Create(paid_col), Create(owed_col), run_time=0.8)
        self.at('it runs every day')
        daily = Text('every day', font_size=24, color=SCAFFOLD).next_to(recon, DOWN, buff=0.15)
        self.play(FadeIn(daily), run_time=0.4)
        self.at('catches schemes like this')
        caught = checkmark(size=0.6).next_to(acct, UP, buff=0.3)
        self.play(Create(caught), run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 7.7

class Segment_7_7(Segment):
    """Right: the decimal point mistake (q07-04, part 1)."""
    EPISODE, SEGMENT = 7, '7.7'

    def construct(self):
        dot = Dot(radius=0.22, color=ERROR).move_to(UP * 0.4)
        label = Text('the decimal point', font_size=40).next_to(dot, DOWN, buff=0.5)
        self.play(FadeIn(dot, scale=0.3), FadeIn(label), run_time=0.8)
        self.play(dot.animate.scale(1.5), rate_func=there_and_back, run_time=0.8)
        self.at('more realistic than it has any right to be')
        digits = Text('4823 71', font=MONO, font_size=56, color=GREY_B).move_to(UP * 0.4)
        self.play(FadeOut(label), FadeIn(digits), dot.animate.scale(0.5).move_to(digits[3].get_corner(DR) + RIGHT * 0.17 + UP * 0.1),
                  run_time=0.8)
        for k in (2, 1, 0, 3):
            target = digits[k].get_corner(DR) + RIGHT * 0.17 + UP * 0.1
            self.play(MoveAlongPath(dot, bounce_path([dot.get_center(), target], height=0.6)), run_time=0.6)
        label = digits

        # [V7.7a] the skim function, "meant" and "oops"
        self.at('one way it could happen')
        code = code_panel(snippet_find(Q4, 'def skim', 'return sum', 'meant = skim', 'oops = skim'), font_size=20)
        fit(code, 12.0).to_edge(UP, buff=0.3).to_edge(RIGHT, buff=0.3)
        meant = Text('meant', font_size=24, color=EXACT).next_to(code, LEFT, buff=0.2)
        meant.set_y(code.code_lines[2].get_y())
        oops = Text('oops', font_size=24, color=ERROR).next_to(code, LEFT, buff=0.2)
        oops.set_y(code.code_lines[3].get_y())
        self.play(FadeOut(dot), FadeOut(label), FadeIn(code), run_time=0.7)
        self.at('Our skimming function takes a unit')
        hl = line_highlight(code, 0)
        self.play(Create(hl), run_time=0.4)
        self.at('keeps whatever is left below it')
        self.play(hl.animate.become(line_highlight(code, 1)), run_time=0.4)

        # the cent ruler: the cut at the cent leaves a hair of a sliver
        self.at('Meant to be a cent')
        rows = snippet_output(Q1)
        amount = (Decimal(field(rows[0], 'interest')) * 100).normalize()   # 11.838247¢, q07-01's first account
        ruler = cent_ruler(0, 13, width=11.6, y=-2.1)
        bar = span(ruler, 0, amount, FOCUS)
        cut = cut_line(ruler, 11, height=0.65)
        hair = span(ruler, 11, amount, MONEY)
        keep = Text(f'keeps {field(rows[0], "left")}', font_size=26, color=MONEY).next_to(hair, UP, buff=0.25)
        self.play(hl.animate.become(line_highlight(code, 2, color=EXACT)), FadeIn(meant), FadeIn(ruler),
                  GrowFromEdge(bar, LEFT), run_time=0.8)
        self.play(Create(cut), run_time=0.4)
        self.add(hair)
        self.play(hair.animate.shift(UP * 0.15), FadeIn(keep), run_time=0.5)
        self.at('Now change one constant')
        self.play(hl.animate.become(line_highlight(code, 3, color=ERROR)), FadeIn(oops), run_time=0.5)

        # [V7.7b] the ruler zooms out to dollars: the cut moves to the dollar tick
        self.at('keeps fractions of a dollar')
        dollar_labels = VGroup(Text('$0', font=MONO, font_size=22, color=SCAFFOLD).move_to(ruler.labels[0]),
                               Text('$1 tick: far to the right →', font_size=22, color=SCAFFOLD)
                               .next_to(ruler.labels[-1], DOWN, buff=0.15).align_to(ruler, RIGHT))
        self.play(FadeOut(ruler.ticks[1:]), FadeOut(ruler.labels), FadeIn(dollar_labels), FadeOut(keep),
                  run_time=0.8)
        whole = span(ruler, 0, amount, MONEY).shift(UP * 0.15)
        keep2 = Text(f'keeps {amount}¢: all of it', font_size=26, color=MONEY).next_to(whole, UP, buff=0.25)
        self.play(cut.animate.move_to(ruler.point(0) + UP * (cut.get_center()[1] - ruler.point(0)[1])),
                  ReplacementTransform(VGroup(bar, hair), whole), run_time=1.2)
        self.play(FadeIn(keep2), run_time=0.5)

        # [V7.7c] the console: 96 times as much
        self.at('On ten thousand accounts')
        self.play(FadeOut(VGroup(ruler.axis, ruler.ticks[0], dollar_labels, cut, whole, keep2)), run_time=0.5)
        out = output_console(Q4, needles=['meant:'], font_size=24)
        out.next_to(code, DOWN, buff=0.4).to_edge(LEFT, buff=0.5)
        self.play(FadeIn(out.background), run_time=0.3)
        card = show_qr(self, 'q07-04')
        self.play(out.type_line(0), run_time=1.4)
        meant_v = field(out.lines[0].source, 'meant:')
        oops_v = field(out.lines[0].source, 'oops:')
        unit = 2.6 / float(oops_v)
        base = DOWN * 3.3
        bar_m = Rectangle(width=0.9, height=max(0.03, float(meant_v) * unit)).set_fill(EXACT, 1).set_stroke(width=0)
        bar_o = Rectangle(width=0.9, height=float(oops_v) * unit).set_fill(ERROR, 1).set_stroke(width=0)
        bar_m.move_to(LEFT * 5.0 + base, aligned_edge=DOWN)
        bar_o.move_to(LEFT * 2.6 + base, aligned_edge=DOWN)
        tag_m = Text(meant_v, font_size=22, color=EXACT).next_to(bar_m, UP, buff=0.12)
        tag_o = Text(oops_v, font_size=22, color=ERROR).next_to(bar_o, UP, buff=0.12)
        floor = Line(LEFT * 6.2 + base, LEFT * 1.4 + base, color=SCAFFOLD, stroke_width=2)
        self.play(Create(floor), GrowFromEdge(bar_m, DOWN), FadeIn(tag_m), run_time=0.6)
        self.at('collects four thousand')
        self.play(GrowFromEdge(bar_o, DOWN), FadeIn(tag_o, shift=UP * 0.2), run_time=1.2)
        self.at('Ninety-six times as much')
        times = out.part(0, '96 times as much')
        self.play(times.animate.set_color(ERROR).scale(1.25), run_time=0.4)
        self.play(times.animate.scale(1 / 1.25), run_time=0.4)
        self.play(times.animate.scale(1.25), run_time=0.4)
        self.play(times.animate.scale(1 / 1.25), run_time=0.4)

        # [V7.7d] the same bug in the wild, as generic labels
        self.at('Mixing up units')
        hide_qr(self, card)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        cases = [('price in cents,\nread as dollars', '× 100'), ('amount in dollars,\nsent as cents', '÷ 100'),
                 ('yen treated\nas having cents', '÷ 100')]
        tiles, badges = VGroup(), VGroup()
        for text, factor in cases:
            frame = RoundedRectangle(width=3.9, height=2.0, corner_radius=0.15).set_stroke(SCAFFOLD, 2)
            words = Text(text, font_size=28, line_spacing=0.9).move_to(frame)
            tiles.add(VGroup(frame, words))
            badges.add(label_box(factor, color=ERROR, font_size=30, fill=ERROR))
        tiles.arrange(RIGHT, buff=0.35).move_to(UP * 0.8)
        for tile, badge in zip(tiles, badges):
            badge.next_to(tile, DOWN, buff=0.4)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in tiles], lag_ratio=0.3), run_time=1.4)
        self.at('One system stores prices as whole cents')
        self.play(tiles[0][0].animate.set_stroke(FOCUS, 3), run_time=0.5)
        self.at('a hundred times too big or too small')
        self.play(LaggedStart(*[FadeIn(b, scale=0.6) for b in badges], lag_ratio=0.25), run_time=1.0)
        self.play(*[Indicate(b, color=ERROR) for b in badges], run_time=0.8)
        self.at("As we'll see in episode ten")
        ep10 = Text('Episode 10 · When the fixes fail', font_size=28, color=SCAFFOLD).move_to(DOWN * 2.9)
        self.play(FadeIn(ep10, shift=UP * 0.2), run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 7.8

class Segment_7_8(Segment):
    """Where floats come in (q07-04, part 2)."""
    EPISODE, SEGMENT = 7, '7.8'

    def construct(self):
        floats = [line for line in snippet_output(Q4) if line.startswith('$')]
        parsed = [re.match(r'^\$(\S+) is (\S+) cents; float slice (\S+)$', l).groups() for l in floats]

        exact = label_box('exact decimals', color=EXACT, font_size=32)
        tick = checkmark(size=0.45).next_to(exact, RIGHT, buff=0.3)
        VGroup(exact, tick).move_to(UP * 0.6)
        self.play(FadeIn(exact), Create(tick), run_time=0.8)
        self.at('nothing in it needs floating point')
        self.play(Indicate(exact, color=EXACT), run_time=0.8)
        self.at('this is a series about floats')
        what = label_box('floats?', color=STORED, font_size=32).next_to(exact, DOWN, buff=0.6)
        self.play(FadeIn(what, shift=UP * 0.2), run_time=0.6)
        self.at('What if the virus had used them?')
        bug = label_box('virus', color=ERROR, font_size=28).next_to(what, RIGHT, buff=0.8)
        self.play(FadeIn(bug, shift=LEFT * 0.3), run_time=0.5)
        self.play(Wiggle(what), run_time=0.8)

        # [V7.8a] the loop; $4.35 goes into × 100 and comes out as 434.99999999999994
        self.at('Take an amount of four dollars')
        self.play(FadeOut(VGroup(exact, tick, what, bug)), run_time=0.5)
        code = code_panel(snippet_find(Q4, 'for dollars in', 'cents = dollars * 100', 'print(f"${dollars}'),
                          font_size=18)
        fit(code, 13.4).to_edge(UP, buff=0.3)
        out = Console(floats, font_size=18)
        out.next_to(code, DOWN, buff=0.25).to_edge(LEFT, buff=0.5)
        row_y = -0.55
        tag = price_tag(f'${parsed[0][0]}').move_to([-5.4, row_y, 0])
        box = label_box('× 100', font_size=30).move_to([-2.5, row_y, 0])
        self.play(FadeIn(code), FadeIn(out.background), FadeIn(tag), FadeIn(box), run_time=0.8)
        self.at('The slice should be zero')
        zero = Text('slice should be 0¢', font_size=26, color=EXACT).next_to(tag, DOWN, buff=0.3)
        self.play(FadeIn(zero), run_time=0.5)
        self.at('But in floating point')
        self.play(tag.animate.move_to(box).scale(0.4).set_opacity(0), FadeOut(zero), run_time=0.8)
        self.remove(tag)
        result = code_text(parsed[0][1], font_size=32, color=STORED)
        result.next_to(box, RIGHT, buff=0.6)
        self.play(FadeIn(result, shift=RIGHT * 0.5), out.type_line(0, run_time=1.2), run_time=1.2)

        # [V7.8b] the ruler from 434 to 435: the value sits a hair left of 435
        self.at('The whole-cents part')
        ruler = FloatLine(434, 435, width=9.0, ticks=[434, 435], labels={434: '434¢', 435: '435¢'},
                          color=SCAFFOLD, label_size=22).move_to([-1.6, -2.9, 0])
        # Drawn at 434.97 so the gap shows; the real gap is 0.00000000000006 of a cent.
        where = Fraction(43497, 100)
        marker = ruler.diamond(where, color=STORED)
        hair = Text('a hair below 435', font_size=20, color=STORED).next_to(marker, UP, buff=0.1).shift(LEFT * 0.8)
        self.play(FadeIn(ruler), FadeIn(marker, shift=DOWN * 0.2), FadeIn(hair), run_time=0.8)
        cut = cut_line(ruler, 434, color=ERROR)
        piece = span(ruler, 434, where, ERROR, height=0.22, lift=0.05)
        self.play(Create(cut), GrowFromEdge(piece, LEFT), run_time=0.8)
        self.at('the slice handed to the virus')
        slice_text = Text(f'slice {parsed[0][2]}', font_size=26, color=ERROR).next_to(piece, UP, buff=0.55)
        slice_text.align_to(piece, LEFT).shift(RIGHT * 0.3)
        pot = labelled_jar('virus', width=1.3, height=1.4, color=ERROR, font_size=22).move_to([5.4, -2.7, 0])
        self.play(FadeIn(slice_text), FadeIn(pot), run_time=0.5)
        self.play(piece.animate.move_to(pot.pot[0]).scale(0.15), run_time=1.0)
        out.lines[0].part(parsed[0][2]).set_color(ERROR)

        # [V7.8c] $1.15 and $0.29: the same near-whole-cent slice
        self.at('A dollar fifteen does the same')
        self.play(out.type_line(1, run_time=1.0))
        self.play(out.lines[1].part(parsed[1][2]).animate.set_color(ERROR), run_time=0.3)
        self.at('So does twenty-nine cents')
        self.play(out.type_line(2, run_time=1.0))
        self.play(out.lines[2].part(parsed[2][2]).animate.set_color(ERROR), run_time=0.3)

        # [V7.8d] exact versus float, side by side
        self.at('Amounts that have no fraction at all')
        self.play(FadeOut(VGroup(box, result, ruler, marker, hair, cut, piece, slice_text, pot)), run_time=0.6)
        left = VGroup(label_box('exact: slice 0¢', color=EXACT, font_size=30), labelled_jar('', 1.3, 1.3))
        right = VGroup(label_box('float: slice ≈ 1¢', color=ERROR, font_size=30), labelled_jar('', 1.3, 1.3))
        for side in (left, right):
            side[1].next_to(side[0], DOWN, buff=0.3)
        VGroup(left, right).arrange(RIGHT, buff=2.2).move_to(DOWN * 1.9)
        self.play(FadeIn(left, shift=UP * 0.2), FadeIn(right, shift=UP * 0.2), run_time=0.7)
        self.at('a float-based virus would happily take it')
        cent = penny(0.3).next_to(right[1], UP, buff=0.9)
        self.play(FadeIn(cent), run_time=0.3)
        self.play(cent.animate.move_to(right[1].pot[0].get_bottom() + UP * 0.35), run_time=0.8,
                  rate_func=rate_functions.ease_in_quad)

        # our addition, and the episode 3 mistake: whole cents, one direction, a few percent
        self.at('not in the film')
        ours = Text('our addition, not the film', font_size=26, color=STORED).next_to(right[0], UP, buff=0.3)
        self.play(FadeIn(ours), run_time=0.5)
        self.at('from episode three')
        self.play(FadeOut(VGroup(code, out, left, right, cent, ours)), run_time=0.6)
        same = Text('the episode 3 mistake: float cents, truncated', font_size=32).move_to(UP * 3.0)
        self.play(FadeIn(same, shift=DOWN * 0.2), run_time=0.6)
        self.at("doesn't even need bad intentions")
        intent = Text('no bad intentions needed', font_size=28, color=SCAFFOLD).next_to(same, DOWN, buff=0.3)
        self.play(FadeIn(intent, shift=UP * 0.2), run_time=0.6)
        self.at('Any system that converts')
        stages = VGroup(label_box('float dollars', color=STORED, font_size=26), label_box('× 100, truncate', font_size=26),
                        label_box('cents', color=MONEY, font_size=26)).arrange(RIGHT, buff=0.9).move_to(UP * 0.9)
        links = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.12, color=SCAFFOLD, stroke_width=3)
                         for a, b in zip(stages[:-1], stages[1:])])
        self.play(LaggedStart(FadeIn(stages[0]), GrowArrow(links[0]), FadeIn(stages[1]), GrowArrow(links[1]),
                              FadeIn(stages[2]), lag_ratio=0.3), run_time=1.6)
        self.at('quietly moving whole cents')
        chips = VGroup(*[RoundedRectangle(width=0.5, height=0.36, corner_radius=0.06).set_fill(GREY_D, 1)
                         .set_stroke(GREY_B, 1) for _ in range(20)]).arrange(RIGHT, buff=0.12).move_to(DOWN * 0.6)
        sink = labelled_jar('one direction', width=1.2, height=1.2, color=ERROR, font_size=22).move_to([5.2, -2.2, 0])
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.3) for c in chips], lag_ratio=0.05), FadeIn(sink),
                  run_time=1.0)
        losers = [4, 15]                       # one in ten here; episode 3 counted 5.73 % (q03-03)
        drops = []
        for k in losers:
            coin_k = penny(0.15).move_to(chips[k])
            path = VMobject().set_points_smoothly([chips[k].get_center(), chips[k].get_center() + DOWN * 1.4,
                                                   sink.pot[0].get_center() + LEFT * 1.0 + UP * 0.2,
                                                   sink.pot[0].get_center()])
            drops.append(Succession(AnimationGroup(chips[k].animate.set_stroke(ERROR, 3), FadeIn(coin_k), run_time=0.3),
                                    MoveAlongPath(coin_k, path, run_time=1.4)))
        self.play(LaggedStart(*drops, lag_ratio=0.5), run_time=2.4)
        self.at('a few percent of its amounts')
        few = Text('a few percent of amounts lose a whole cent', font_size=28, color=ERROR).move_to(LEFT * 1.8 + DOWN * 2.6)
        self.play(FadeIn(few, shift=UP * 0.2), run_time=0.6)
        self.finish()


# ---------------------------------------------------------------- 7.9

class Segment_7_9(Segment):
    """Real salami slicing."""
    EPISODE, SEGMENT = 7, '7.9'

    def construct(self):
        # [V7.9a] a salami on a board, sliced into paper-thin rounds marked ¢
        board = RoundedRectangle(width=10.5, height=2.4, corner_radius=0.2).set_fill('#7a5a3a', 1).set_stroke('#5a4028', 3)
        board.move_to(DOWN * 0.4)
        meat = RoundedRectangle(width=5.0, height=1.3, corner_radius=0.6).set_fill('#8e2f2f', 1).set_stroke('#5e1d1d', 3)
        meat.move_to(board).shift(LEFT * 2.2 + UP * 0.1)
        rng = random.Random(9)
        flecks = VGroup(*[Ellipse(width=0.14, height=0.09).set_fill('#e8c8b8', 0.9).set_stroke(width=0)
                          .move_to(meat.get_center() + RIGHT * rng.uniform(-2.1, 2.1) + UP * rng.uniform(-0.4, 0.4))
                          for _ in range(22)])
        salami = VGroup(meat, flecks)
        title = Text('salami slicing', font_size=40).to_edge(UP, buff=0.6)
        self.play(FadeIn(board), FadeIn(salami), run_time=0.8)
        self.at('salami slicing')
        self.play(Write(title), run_time=0.8)
        knife = Polygon([0, 0.9, 0], [0.12, 0.9, 0], [0.12, -0.9, 0], [0, -0.7, 0]).set_fill(GREY_B, 1).set_stroke(WHITE, 1)
        knife.move_to(meat.get_right() + LEFT * 0.12 + UP * 1.6)
        self.play(FadeIn(knife), run_time=0.3)
        rounds = VGroup()
        for k in range(6):
            edge = meat.get_right()
            self.play(knife.animate.move_to(edge + LEFT * 0.06), run_time=0.25)
            disc = Circle(radius=0.42).set_fill('#a63a3a', 1).set_stroke('#5e1d1d', 2)
            mark = Text('¢', font_size=26, color='#f2e0d0').move_to(disc)
            piece = VGroup(disc, mark).move_to(edge + RIGHT * 0.1).stretch(0.12, 0)
            spot = board.get_center() + RIGHT * (0.8 + 0.75 * k) + DOWN * 0.1
            self.add(piece)
            self.play(meat.animate.stretch_to_fit_width(meat.width - 0.25, about_edge=LEFT),
                      knife.animate.shift(UP * 1.4), piece.animate.stretch(1 / 0.12, 0).move_to(spot), run_time=0.45)
            rounds.add(piece)
        self.play(FadeOut(knife), run_time=0.3)

        # [V7.9b] index cards: penny-shaving stories, most stamped "source?"
        self.at('stories about rogue programmers')
        self.play(FadeOut(VGroup(board, salami, rounds, title)), run_time=0.6)
        cards = VGroup()
        for k in range(5):
            card = RoundedRectangle(width=3.6, height=2.2, corner_radius=0.08).set_fill(PAPER, 1).set_stroke(GREY_B, 1)
            lines = VGroup(*[Line(LEFT * 1.4, RIGHT * 1.4, color=GREY_B, stroke_width=2) for _ in range(4)])
            lines.arrange(DOWN, buff=0.32).move_to(card).shift(DOWN * 0.15)
            cards.add(VGroup(card, lines))
        cards.arrange(RIGHT, buff=-1.2).move_to(DOWN * 0.3)
        for k, c in enumerate(cards):
            c.rotate((k - 2) * 0.06)
        heading = Text('penny-shaving stories', font_size=36).to_edge(UP, buff=0.7)
        self.play(FadeIn(heading), LaggedStart(*[FadeIn(c, shift=UP * 0.4) for c in cards], lag_ratio=0.2),
                  run_time=1.4)
        self.at('surprisingly hard to pin')
        stamps = VGroup()
        for c in (cards[0], cards[1], cards[3], cards[4]):
            word = Text('source?', font_size=28, color=GREY_B, weight=BOLD)
            frame = SurroundingRectangle(word, color=GREY_B, buff=0.1, corner_radius=0.05)
            stamps.add(VGroup(frame, word).rotate(0.25).move_to(c[0].get_center() + UP * 0.25))
        self.play(LaggedStart(*[FadeIn(s, scale=1.6) for s in stamps], lag_ratio=0.35), run_time=2.0)
        self.at('easy to imagine and hard to keep hidden')
        self.play(Indicate(cards[2], color=FOCUS, scale_factor=1.05), run_time=0.8)

        # [V7.9c] the checklist that actually stops it
        self.at('What actually stops it')
        self.play(FadeOut(VGroup(cards, stamps, heading)), run_time=0.6)
        items = VGroup(*[checklist_item(t, font_size=30) for t in
                         ('rounding rule written down', 'reconciliation daily', 'no unexplained accounts',
                          'two people to change money code')]).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        items.move_to(ORIGIN)
        stops = Text('what stops it', font_size=36, color=SCAFFOLD).next_to(items, UP, buff=0.6)
        self.play(FadeIn(stops), LaggedStart(*[FadeIn(i, shift=RIGHT * 0.2) for i in items], lag_ratio=0.15),
                  run_time=1.2)
        for item, phrase in zip(items, ('a written rounding rule', 'double entry', 'daily reconciliation',
                                        'change control')):
            self.at(phrase)
            item.tick.move_to(item[0])
            self.play(Create(item.tick), item[1].animate.set_color(EXACT), run_time=0.5)
        self.finish()


# ---------------------------------------------------------------- 7.10

class Segment_7_10(Segment):
    """Recap and challenge (q07-05), the QR wall, and the teaser for episode 8."""
    EPISODE, SEGMENT = 7, '7.10'

    def construct(self):
        # [V7.10a] three columns: right, wrong, our addition
        xs = (-4.6, 0.0, 4.6)
        heads = VGroup(
            VGroup(checkmark(size=0.4), Text('Right', font_size=36, color=EXACT)).arrange(RIGHT, buff=0.2),
            VGroup(crossmark(size=0.36), Text('Wrong', font_size=36, color=ERROR)).arrange(RIGHT, buff=0.2),
            Text('Our addition', font_size=36, color=STORED))
        for h, x in zip(heads, xs):
            h.move_to([x, 3.2, 0])
        rules = VGroup(*[Line(LEFT * 2.0, RIGHT * 2.0, color=GREY_D).move_to([x, 2.75, 0]) for x in xs])
        entries = [
            (0, 'fractions of a cent are real', 'Fractions of a cent are real'),
            (0, 'tiny × huge volume = real money', 'tiny amounts times enormous volumes'),
            (0, 'a decimal point mistake is very believable', 'a misplaced decimal point'),
            (1, 'round to nearest leaves almost nothing to skim', 'Under round to nearest'),
            (1, "fractions don't vanish: double entry", 'Under double entry'),
            (1, 'a daily reconciliation would catch it', 'a daily reconciliation would find'),
            (2, 'floats would skim nearly whole cents', 'Floating point'),
        ]
        colors = (EXACT, ERROR, STORED)
        filled = [2.4, 2.4, 2.4]
        self.play(FadeIn(heads[0]), Create(rules[0]), run_time=0.6)
        for col, text, phrase in entries:
            self.at(phrase)
            if col and filled[col] == 2.4:
                self.play(FadeIn(heads[col]), Create(rules[col]), run_time=0.5)
            item = wrapped_text(text, 3.9, font_size=30)
            item.move_to([xs[col], 0, 0]).align_to([0, filled[col], 0], UP)
            bullet = Dot(radius=0.06, color=colors[col]).next_to(item, LEFT, buff=0.15).align_to(item, UP).shift(DOWN * 0.1)
            filled[col] = item.get_bottom()[1] - 0.7
            self.play(FadeIn(item, shift=UP * 0.2), FadeIn(bullet), run_time=0.6)
        self.at('turning amounts with no fraction')
        self.play(Indicate(item, color=STORED, scale_factor=1.08), run_time=1.0)

        # [V7.10b] the challenge: "Your check goes here." in yellow, and the QR card
        self.at('a challenge')
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        out = output_console(Q5, font_size=26)
        out.to_corner(UL, buff=0.6)
        code = code_panel(snippet_find(Q5, 'print("books balance:"', '# Your check goes here.'), font_size=28)
        code.next_to(out, DOWN, buff=0.4).align_to(out, LEFT)
        self.play(FadeIn(out), FadeIn(code), run_time=0.6)
        card = show_qr(self, 'q07-05')
        self.at('shows that the books balance')
        self.play(out.lines[3].glyphs.animate.set_color(EXACT), run_time=0.5)
        self.at('write the check that catches it')
        hl = line_highlight(code, 1, color=FOCUS)
        self.play(Create(hl), code.code_lines[1].animate.set_color(FOCUS), run_time=0.6)
        cursor = Rectangle(width=0.14, height=0.36).set_fill(FOCUS, 1).set_stroke(width=0)
        cursor.next_to(code.code_lines[1], RIGHT, buff=0.12)
        self.add(cursor)
        for _ in range(3):
            self.play(cursor.animate.set_opacity(0), rate_func=there_and_back, run_time=0.7)

        # [V7.10c] the QR wall, 10 seconds
        self.at('Recompute each customer')
        hide_qr(self, card, hold=10.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
        wall = qr_wall(episode_qr_ids(7))
        self.play(FadeIn(wall), run_time=0.6)
        wall_at = self.renderer.time
        self.at('Next time')
        remaining = wall_at + 10.0 - self.renderer.time
        if remaining > 0:
            self.wait(remaining)

        # [V7.10d] teaser: $100 splits into three stacks; one penny is left, spinning
        self.play(FadeOut(wall), run_time=0.5)
        bill = RoundedRectangle(width=3.0, height=1.4, corner_radius=0.1).set_fill('#2f6b3a', 1).set_stroke(EXACT, 2)
        bill_text = Text('$100', font_size=40, color=WHITE).move_to(bill)
        note = VGroup(bill, bill_text).move_to(UP * 1.8)
        self.play(FadeIn(note, scale=0.8), run_time=0.6)
        third = (Decimal(100) / 3).quantize(CENT, ROUND_DOWN)      # 33.33, computed
        stacks = VGroup()
        for _ in range(3):
            stack = VGroup(*[RoundedRectangle(width=1.4, height=0.24, corner_radius=0.04).set_fill('#2f6b3a', 1)
                             .set_stroke(EXACT, 1).shift(UP * 0.14 * i) for i in range(6)])
            label = Text(f'{third}', font_size=26, color=MONEY).next_to(stack, DOWN, buff=0.15)
            stacks.add(VGroup(stack, label))
        stacks.arrange(RIGHT, buff=0.8).move_to(UP * 1.6)
        self.at('splitting a hundred dollars three ways')
        self.play(FadeOut(note, scale=0.6), LaggedStart(*[FadeIn(s, shift=DOWN * 0.3) for s in stacks], lag_ratio=0.25),
                  run_time=1.2)
        self.at("the penny that's always left over")
        left_over = penny(0.4).next_to(stacks, RIGHT, buff=0.7).shift(DOWN * 0.3)
        self.play(FadeIn(left_over, scale=0.5), run_time=0.4)
        self.play(Rotate(left_over, 4 * TAU, axis=UP), run_time=2.0, rate_func=rate_functions.ease_out_sine)
        card8 = end_card('Episode 8', 'Splitting the penny').move_to(DOWN * 1.6)
        self.play(FadeIn(card8, shift=UP * 0.2), run_time=0.6)
        self.at('Who should get it?')
        self.play(Rotate(left_over, 3 * TAU, axis=UP), run_time=1.8, rate_func=rate_functions.ease_out_sine)
        self.finish()

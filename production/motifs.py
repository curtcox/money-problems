"""A contact sheet of the recurring visuals, for checking common.py by eye.

    manim -qm -s production/motifs.py Motifs
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa: E402,F403


class Motifs(Scene):
    def construct(self):
        grid = cent_grid(cell=0.34, font_size=9).to_corner(UL, buff=0.3)
        for cell in grid.exact:
            cell.set_fill(EXACT, 0.55).set_stroke(EXACT, 2)
        line = FloatLine('0.29999999999999993', '0.30000000000000016', width=5.5,
                         labels={0.3: '0.3', 0.1 + 0.2: '0.1+0.2'}).next_to(grid, RIGHT, buff=0.5).shift(UP * 0.8)
        line.add(line.diamond('0.3'), line.snap('0.3'))
        code = code_panel(snippet_lines('ep01/01-ten-plus-twenty.py', 4, 7), font_size=16)
        code.next_to(line, DOWN, buff=0.6).align_to(line, LEFT)
        box = line_highlight(code, 2)
        out = output_console('ep01/01-ten-plus-twenty.py', font_size=14).next_to(code, DOWN, buff=0.2, aligned_edge=LEFT)
        out.part(0, '4').set_color(ERROR)
        out.lines[3].part('True').set_color(EXACT)
        bill = receipt([('Coffee', '0.99'), ('Muffin', '0.99'), ('Tea', '0.99'), ('-', ''),
                        ('Subtotal', '2.97'), ('Tax 8.25%', '0.25'), ('Total', '3.22')],
                       width=3.0, font_size=14, title='RECEIPT').to_corner(DL, buff=0.3)
        book = ledger(['100.00', '0.10'], [('Cash', '100.00')], totals=('100.10', '100.00'),
                      width=4.4, font_size=16).scale(0.8).to_corner(DR, buff=0.4).shift(UP * 0.8)
        book.balance.beam.rotate(0.15, about_point=book.balance.beam[2].get_center())
        book.totals.left.set_color(ERROR)
        coins = VGroup(penny(0.4), coin('10¢', 0.4), sliced_penny(8, 0.4, gap=0.05), jar(0.9, 1.1),
                       price_tag('$1.15', font_size=22)).arrange(RIGHT, buff=0.3).next_to(bill, RIGHT, buff=0.4).align_to(bill, DOWN)
        card = qr_card('q01-01', height=1.2).to_corner(UR, buff=0.2)
        self.add(grid, line, code, box, out, bill, book, coins, card)

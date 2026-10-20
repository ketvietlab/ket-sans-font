"""Figures 3–9, on the 0 1 2 system: figure strokes, tabular advance, c-like
terminals cut horizontally, the arch shoulder on 5, the 0 oval on 6 9, rings on 8."""

from __future__ import annotations

from .geometry import Contour, add, flatten, intersect_lines, mul, offset_line, polygon, rect, stroke, superellipse, vec
from .glyphs import Glyph
from .upper import hcut_centre


class FigureMixin:
    def _fig(self, name, uni, cs, note):
        W, adv = self.wd.figure, self.wd.tabularAdvance
        return Glyph(name, [uni], adv, cs, note=note).shifted((adv - W) / 2)

    @property
    def _F(self):
        return self.sys.m.figureHeight

    def three(self):
        st, k = self.st, self.ten
        W, C = self.wd.figure, self._F
        T, B = C + self.of, -self.of
        side, top = st.figureSide, st.figureTop
        tw = top - 12
        ko, ki, kt = k.outer, k.inner, k.terminal
        y_wb = 0.52 * C - tw / 2
        x_w = 0.36 * W
        y_t = (0.735 - self.sh.terminalClose) * C
        r_u = W - 56
        y_ru = (T + y_wb) / 2
        c = Contour((30, y_t))
        c.curve((0.48 * W, T), 76, 0, kt, ko)
        c.curve((r_u, y_ru), 0, 270, ko)
        c.curve((0.55 * W, y_wb), 270, 180, ko)
        c.line((x_w, y_wb)).line((x_w, y_wb + tw)).line((0.55 * W, y_wb + tw))
        c.curve((r_u - side + 10, y_ru), 0, 90, ki)
        c.curve((0.48 * W, T - top), 90, 180, ki)
        c.curve((30 + side + 12, y_t), 180, 256, ki, kt)
        upper = c.close().oriented(True)
        y_rl = (y_wb + tw + B) / 2
        y_lt = (0.25 + self.sh.terminalClose) * C
        c = Contour((x_w, y_wb + tw)).line((0.52 * W, y_wb + tw))
        c.curve((W, y_rl), 0, 270, ko)
        c.curve((0.5 * W, B), 270, 180, ko)
        c.curve((14, y_lt), 180, 104, ko, kt)
        c.line((14 + side + 18, y_lt))
        c.curve((0.5 * W, B + top), 284, 0, kt, ki)
        c.curve((W - side, y_rl), 0, 90, ki)
        c.curve((0.52 * W, y_wb), 90, 180, ki)
        c.line((x_w, y_wb))
        lower = c.close().oriented(True)
        return self._fig("three", 0x33, [upper, lower], "2 top + two bowls meeting in a waist cut vertically; lower terminal like s")

    def four(self):
        st = self.st
        W, C = self.wd.figure, self._F
        S, tb = st.figureStem, st.figureTop + 4
        xs = 0.64 * W
        yb = 0.215 * C
        t = st.figureStem * 0.78
        reach = 34  # the bar runs past the figure width; the 4 is re-centred below
        p, q = (0, yb + tb), (xs, C)
        inner = offset_line(p, q, -t)
        y_i = intersect_lines(*inner, (xs, 0), (xs, C))[1]
        x_bi = intersect_lines(*inner, (0, yb + tb), (W, yb + tb))[0]
        diag = polygon([p, q, (xs, y_i), (x_bi, yb + tb)]).oriented(True)
        cs = [rect(xs, 0, xs + S, C), rect(0, yb, W + reach, yb + tb), diag]
        cs = [c.translated(-reach / 2, 0) for c in cs]
        return self._fig("four", 0x34, cs, "closed 4: figure stem, bar at 0.215 reaching 0.14 cap past the stem, diagonal x0.78 meeting the stem top")

    def five(self):
        st, k = self.st, self.ten
        W, C = self.wd.figure, self._F
        B = -self.of
        S, side, top = st.figureStem, st.figureSide, st.figureTop
        ko, ki, kt = k.outer, k.inner, k.terminal
        xs = 0.05 * W  # bottom left of the vertical
        lean, w_v = 0.11, S * 0.88  # dx/dy of the vertical (SF 0.10, Inter 0.12, Helvetica 0.15) and its weight
        t_top = top + 4
        y_sb = 0.47 * C
        edge_at = lambda y: xs + w_v + lean * (y - y_sb)
        join, a_join = (edge_at(0.585 * C), 0.585 * C), 62.0
        crotch, a_crotch = (edge_at(0.50 * C), 0.50 * C), 238.0
        edge = crotch[0]
        y_ap = 0.645 * C
        y_r = 0.31 * C
        start = add(join, mul(vec(a_join), -110))
        c = Contour(start).line(join)
        c.curve((0.54 * W, y_ap), a_join, 0, k.shoulderOuter)
        c.curve((W, y_r), 0, 270, ko)
        c.curve((0.5 * W, B), 270, 180, ko)
        y_lt = (0.25 + self.sh.terminalClose) * C
        c.curve((14, y_lt), 180, 104, ko, kt)
        c.line((14 + side + 18, y_lt))
        c.curve((0.5 * W, B + top), 284, 0, kt, ki)
        c.curve((W - side, y_r), 0, 90, ki)
        c.curve((0.53 * W, y_ap - top + 6), 90, 180, ki)
        c.curve(crotch, 180, a_crotch, k.shoulderInner)
        c.line((edge - 80, crotch[1])).line((edge - 80, start[1]))
        bowl = c.close().oriented(True)
        x_bar = xs + lean * (C - y_sb)  # the vertical runs to the top, so the bar's corner is flush with its left edge
        vertical = polygon([(xs, y_sb), (xs + w_v, y_sb), (edge_at(C), C), (x_bar, C)]).oriented(True)
        cs = [rect(x_bar, C - t_top, W - 40, C), vertical, bowl]
        return self._fig("five", 0x35, cs, "leaning vertical (x0.88) + top bar; bowl leaves it like the n shoulder; lower terminal like 3")

    def _six_contours(self):
        """One outline on the 0 oval (top, left side, bottom) whose lower right
        is the bowl; the bowl top dives into the rising stroke like the n
        shoulder, and the stroke ends in a horizontal cut near full width."""
        st, k = self.st, self.ten
        W, C = self.wd.figure, self._F
        T, B = C + self.of, -self.of
        side, top = st.figureSide, st.figureTop
        ko, ki, kt = k.outer, k.inner, k.terminal
        y_bt = 0.645 * C  # bowl top
        cy = (y_bt + B) / 2  # bowl right extreme
        y_l = 0.50 * C  # outer left extreme, level with the crotch so the stroke keeps the figure side
        y_j = y_l  # crotch: bowl top meets the inner edge of the stroke (thinned to ~0.67 side, like n)
        y_t = (0.775 - self.sh.terminalClose) * C  # terminal height
        x_to, cut = W - 40, side + 10  # terminal outer end and horizontal cut length
        k_ll = ko + 0.05  # outline lower left: the taller 0 curve, filled out a little
        c = Contour((x_to, y_t))
        c.curve((0.52 * W, T), 104, 180, kt, ko)
        c.curve((0, y_l), 180, 270, ko)
        c.curve((W / 2, B), 270, 0, k_ll)
        c.curve((W, cy), 0, 90, ko)
        c.curve((0.54 * W, y_bt), 90, 180, ko)
        c.curve((side, y_j), 180, 236, k.shoulderOuter)
        c.curve((0.54 * W, T - top), 90, 0, ki)
        c.curve((x_to - cut, y_t), 0, 284, ki, kt)
        outline = c.close().oriented(True)
        # Counter: the left wall keeps the figure side, measured from the outline.
        lower_left = Contour((0, y_l)).curve((W / 2, B), 270, 0, k_ll).segments[0]
        pts = flatten([(0, y_l), *lower_left[1:]], 64)
        x_out = next(x0 + (cy - y0) / (y1 - y0) * (x1 - x0) for (x0, y0), (x1, y1) in zip(pts, pts[1:]) if y1 <= cy <= y0)
        xl, xr = x_out + side, W - side
        yb, yt = B + top, y_bt - top
        icy, mid = (yb + yt) / 2, (xl + xr) / 2
        # Lower counter quadrants a little rounder (still above a circle's 0.552) and
        # the bottom point shifted right keep the walls near the 0's diagonals where
        # the outline follows the larger 0 curve.
        k_bl, k_br, dx_b = ki - 0.04, ki - 0.04, 36
        cnt = Contour((xr, icy)).curve((mid + dx_b, yb), 270, 180, k_br).curve((xl, icy), 180, 90, k_bl)
        cnt.curve((mid, yt), 90, 0, ki).curve((xr, icy), 0, 270, ki)
        counter = cnt.close().oriented(False)
        return [outline, counter]

    def six(self):
        return self._fig("six", 0x36, self._six_contours(), "0 oval outline; bowl joins the rising stroke like the n shoulder; terminal cut horizontally")

    def nine(self):
        W, C = self.wd.figure, self._F
        cs = [c.rotated180(W / 2, C / 2) for c in self._six_contours()]
        return self._fig("nine", 0x39, cs, "6 rotated 180°")

    def seven(self):
        st = self.st
        W, C = self.wd.figure, self._F
        t_top = st.figureTop + 4
        t = st.figureStem * 0.96
        foot = (0.31 * W, 0)
        top = hcut_centre(foot, W, C - t_top, t, +1)
        diag = stroke(foot, (top[0], top[1] + 1), t, cut="h")
        return self._fig("seven", 0x37, [rect(10, C - t_top, W, C), diag], "top bar + straight diagonal of figure-stem weight")

    def eight(self):
        st = self.st
        W, C = self.wd.figure, self._F
        T, B = C + self.of, -self.of
        side, top = st.figureSide - 6, st.figureTop - 6
        tw = top
        y_w = 0.575 * C
        lower = self.ring(W / 2, (y_w + B) / 2, W / 2, (y_w - B) / 2, side, tw, bottom=top + 6)
        y_ub = y_w - tw
        upper = self.ring(W / 2, (T + y_ub) / 2, 0.445 * W, (T - y_ub) / 2, side - 12, top, bottom=tw)
        return self._fig("eight", 0x38, lower + upper, "two 0 rings, upper 0.89 wide, sharing one waist stroke")


FIGURES = ["three", "four", "five", "six", "seven", "eight", "nine"]

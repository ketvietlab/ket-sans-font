"""Glyph recipes for KÉT Sans.

Glyphs are not drawn one by one.  A handful of master constructions carry
the design system and every other glyph inherits from them:

    stem / bar      H I E N l i t 1  (straight strokes, flat grid-aligned ends)
    ring            O o 0            (oval outside, firmer oval inside)
    arch            n h m r u        (shoulder with notch and thin crotch)
    bowl            b d p q          (ring half that joins a stem like an arch)
    cut ring        c e              (ring cut by horizontal terminal lines)
    diagonal        A V N            (strokes of perpendicular width)
    explicit spine  s a 2            (point/tangent recipes on the same tension)

The ``note`` on each glyph records what it inherits so that a change to a
master can be traced to every glyph it touches.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .geometry import (
    Contour,
    add,
    cubic_point,
    cubic_t_at,
    intersect_lines,
    mul,
    offset_line,
    oval_quadrants,
    polygon,
    rect,
    split_cubic,
    superellipse,
    vec,
    x_at_y,
)
from .system import Namespace, System


@dataclass
class Glyph:
    name: str
    unicodes: list[int]
    width: float
    contours: list[Contour] = field(default_factory=list)
    components: list[tuple[str, float, float]] = field(default_factory=list)
    anchors: dict[str, tuple[float, float]] = field(default_factory=dict)
    note: str = ""

    def shifted(self, dx: float) -> "Glyph":
        self.contours = [c.translated(dx, 0) for c in self.contours]
        self.anchors = {k: (v[0] + dx, v[1]) for k, v in self.anchors.items()}
        return self


def _contour_from_beziers(beziers) -> Contour:
    """Chain bezier point lists (each starting where the last ended)."""
    c = Contour(beziers[0][0])
    for seg in beziers:
        if len(seg) == 2:
            c.line(seg[1])
        else:
            c.cubic(seg[1], seg[2], seg[3])
    return c


def _cut(seg, value, axis, keep):
    """Split ``seg`` where it crosses ``value`` and keep 'before' or 'after'."""
    ts = cubic_t_at(seg, value, axis)
    if not ts:
        raise ValueError(f"segment does not cross {value} on axis {axis}")
    t = ts[0] if keep == "after" else ts[-1]
    a, b = split_cubic(seg, t)
    return b if keep == "after" else a


def _reverse_seg(seg):
    return list(reversed(seg))


class Builder:
    def __init__(self, system: System):
        self.sys = system
        m = system.m
        self.xh = m.xHeight
        self.cap = m.capHeight
        self.asc = m.ascender
        self.desc = m.descender
        self.oc = m.overshoot.capRound
        self.ox = m.overshoot.lowercaseRound
        self.oa = m.overshoot.arch
        self.of = m.overshoot.figureRound
        self.st = system.st
        self.ten = system.k
        self.sh = system.sh
        self.wd = system.w
        self.sp = system.sp
        # Recipes that write a weight as a Regular number (punctuation, symbols,
        # small marks) scale it with the stem, or with the mark pen, in heavier
        # masters; both factors are exactly 1 at Regular.
        self.reg = Namespace(system.raw["masters"]["Regular"]["stroke"])
        self.wk = self.st.stemLower / self.reg.stemLower
        self.mk = self.st.markStroke / self.reg.markStroke

    # ================================================================ masters
    def ring(self, cx, cy, rx, ry, side, top, k_out=None, k_in=None, bottom=None):
        k_out = k_out or self.ten.outer
        k_in = k_in or self.ten.inner
        bottom = top if bottom is None else bottom
        outer = superellipse(cx, cy, rx, ry, k_out)
        iry = ry - (top + bottom) / 2
        icy = cy + (bottom - top) / 2
        inner = superellipse(cx, icy, rx - side, iry, k_in).reversed()
        return [outer, inner]

    def oval_right_x(self, cx, cy, rx, ry, y):
        """x of an outer oval's right edge at height ``y`` (upper half)."""
        q = oval_quadrants(cx, cy, rx, ry, self.ten.outer)[0]
        return cubic_point(q, cubic_t_at(q, y, 1)[0])[0]

    def arch_parts(self, xl, sl, xr, sr, top=None, apex_x=None):
        """Shoulder that leaves a stem [xl, xl+sl] and lands as the stem
        [xr-sr, xr].  Returns the construction points and curves."""
        X = top if top is not None else self.xh
        st, sh, k = self.st, self.sh, self.ten
        edge = xl + sl
        join = (edge, sh.archJoinOuter * self.xh)
        a_join = sh.archJoinAngle
        apex = (xl + (xr - xl) * (apex_x or sh.archApexX), X + self.oa)
        right = (xr, sh.archRightTangent * self.xh)
        inner_right = (xr - sr, sh.archRightTangent * self.xh - 12)
        inner_apex = (edge + (xr - sr - edge) * 0.52, X + self.oa - st.archTop)
        crotch = (edge, sh.archCrotch * self.xh)
        a_crotch = sh.archCrotchAngle
        outer1 = [join, *Contour(join).curve(apex, a_join, 0, k.shoulderOuter).segments[0][1:]]
        outer2 = [apex, *Contour(apex).curve(right, 0, 270, k.shoulderOuter).segments[0][1:]]
        inner1 = [inner_right, *Contour(inner_right).curve(inner_apex, 90, 180, k.shoulderInner).segments[0][1:]]
        inner2 = [inner_apex, *Contour(inner_apex).curve(crotch, 180, a_crotch, k.shoulderInner).segments[0][1:]]
        ext = 110
        start = add(join, mul(vec(a_join), -ext))
        return dict(
            edge=edge, join=join, apex=apex, right=right, inner_right=inner_right,
            inner_apex=inner_apex, crotch=crotch, outer1=outer1, outer2=outer2,
            inner1=inner1, inner2=inner2, start=start, a_join=a_join, xr=xr, sr=sr,
        )

    def arch(self, xl, sl, xr, sr, top=None, apex_x=None) -> Contour:
        p = self.arch_parts(xl, sl, xr, sr, top, apex_x)
        inset = min(sl, 110) - 20
        c = Contour(p["start"])
        c.line(p["join"])
        c.cubic(*p["outer1"][1:])
        c.cubic(*p["outer2"][1:])
        c.line((xr, 0)).line((xr - sr, 0)).line(p["inner_right"])
        c.cubic(*p["inner1"][1:])
        c.cubic(*p["inner2"][1:])
        c.line((p["edge"] - inset, p["crotch"][1]))
        c.line((p["edge"] - inset, p["start"][1]))
        return c.close().oriented(True)

    def bowl_parts(self, x0, xs, side, top, bottom=None, apex_ratio=0.55):
        """Bowl on the left of a stem whose left edge is ``xs``; joins like an
        arch at top and bottom (vertically symmetric about x-height / 2)."""
        X, sh = self.xh, self.sh
        bottom = top if bottom is None else bottom
        y_tj = sh.bowlJoinOuter * X
        y_tc = sh.bowlCrotch * X
        y_bj = X - y_tj
        y_bc = X - y_tc
        a_join = sh.bowlJoinAngle
        a_crotch = sh.bowlCrotchAngle
        width = xs - x0
        top_apex = (x0 + width * apex_ratio, X + self.ox)
        bot_apex = (x0 + width * apex_ratio, -self.ox)
        left = (x0, X / 2)
        i_top = (x0 + side + (width - side) * 0.53, X + self.ox - top)
        i_bot = (x0 + side + (width - side) * 0.53, -self.ox + bottom)
        i_left = (x0 + side, X / 2)
        return dict(
            y_tj=y_tj, y_tc=y_tc, y_bj=y_bj, y_bc=y_bc, a_join=a_join, a_crotch=a_crotch,
            top_apex=top_apex, bot_apex=bot_apex, left=left, i_top=i_top, i_bot=i_bot, i_left=i_left,
        )

    def bowl(self, x0, xs, side, top, bottom=None, apex_ratio=0.55) -> Contour:
        p = self.bowl_parts(x0, xs, side, top, bottom, apex_ratio)
        k_o, k_i = self.ten.outer, self.ten.inner
        a_j, a_c = p["a_join"], p["a_crotch"]
        ext, inset = 100, 70
        j_t = (xs, p["y_tj"])
        j_b = (xs, p["y_bj"])
        start = add(j_t, mul(vec(180 - a_j), -ext))
        c = Contour(start).line(j_t)
        c.curve(p["top_apex"], 180 - a_j, 180, self.ten.shoulderOuter, k_o)
        c.curve(p["left"], 180, 270, k_o)
        c.curve(p["bot_apex"], 270, 0, k_o)
        c.curve(j_b, 0, a_j, k_o, self.ten.shoulderOuter)
        c.line(add(j_b, mul(vec(a_j), ext)))
        c.line((xs + inset, p["y_bc"]))
        c.line((xs, p["y_bc"]))
        c.curve(p["i_bot"], 180 + a_c, 180, self.ten.shoulderInner, k_i)
        c.curve(p["i_left"], 180, 90, k_i)
        c.curve(p["i_top"], 90, 0, k_i)
        c.curve((xs, p["y_tc"]), 0, 360 - a_c, k_i, self.ten.shoulderInner)
        c.line((xs + inset, p["y_tc"]))
        return c.close().oriented(True)

    def cut_ring(self, cx, cy, rx, ry, side, top, y_upper, y_lower, k_out=None, k_in=None, k_right=None):
        """Ring opened on the right by two horizontal terminal cuts (c)."""
        k_out = k_out or self.ten.outer
        k_in = k_in or self.ten.inner
        k_right = k_right or self.ten.terminal
        o = oval_quadrants(cx, cy, rx, ry, k_out)
        i = oval_quadrants(cx, cy, rx - side, ry - top, k_in)
        # Firmer tension on the open right side keeps terminals upright.
        o[0] = superellipse(cx, cy, rx, ry, k_right).beziers().__next__()
        o[3] = list(superellipse(cx, cy, rx, ry, k_right).beziers())[3]
        i[0] = superellipse(cx, cy, rx - side, ry - top, k_right).beziers().__next__()
        i[3] = list(superellipse(cx, cy, rx - side, ry - top, k_right).beziers())[3]
        o_up = _cut(o[0], y_upper, 1, "after")
        o_lo = _cut(o[3], y_lower, 1, "before")
        i_up = _cut(i[0], y_upper, 1, "after")
        i_lo = _cut(i[3], y_lower, 1, "before")
        outer = [o_up, o[1], o[2], o_lo]
        inner = [_reverse_seg(i_lo), _reverse_seg(i[2]), _reverse_seg(i[1]), _reverse_seg(i_up)]
        c = _contour_from_beziers(outer)
        c.line(inner[0][0])
        for seg in inner:
            c.cubic(*seg[1:])
        return c.close().oriented(True)

    def side_bowl(self, xs, y0, y1, xr, t_top, t_bot, side, rh=None, overlap=20) -> Contour:
        """D-type bowl right of a stem edge ``xs``: flat arms (``t_top`` /
        ``t_bot`` thick) turning into a round side whose outer extreme is
        ``xr``.  Outer and inner curves share their centre so the stroke
        thins evenly into the corners (B D P R Þ)."""
        k_o, k_i = self.ten.outer, self.ten.inner
        rv = (y1 - y0) / 2
        rh = min(rh or rv, xr - xs - 40)
        xa = xr - rh
        ym = (y0 + y1) / 2
        yim = (y0 + t_bot + y1 - t_top) / 2
        c = Contour((xs - overlap, y1)).line((xa, y1))
        c.curve((xr, ym), 0, 270, k_o)
        c.curve((xa, y0), 270, 180, k_o)
        c.line((xs - overlap, y0)).line((xs - overlap, y0 + t_bot)).line((xa, y0 + t_bot))
        c.curve((xr - side, yim), 0, 90, k_i)
        c.curve((xa, y1 - t_top), 90, 180, k_i)
        c.line((xs - overlap, y1 - t_top))
        return c.close().oriented(True)

    def cup(self, x0, x1, sl, sr, top, yj, bottom_t, o, yj_in=None) -> Contour:
        """U-shaped stroke: stems [x0, x0+sl] and [x1-sr, x1] from ``top``
        down to ``yj`` and a round bottom with overshoot ``o`` (U)."""
        k_o, k_i = self.ten.outer, self.ten.inner
        yj_in = yj if yj_in is None else yj_in
        c = Contour((x0, top)).line((x0, yj))
        c.curve(((x0 + x1) / 2, -o), 270, 0, k_o)
        c.curve((x1, yj), 0, 90, k_o)
        c.line((x1, top)).line((x1 - sr, top)).line((x1 - sr, yj_in))
        c.curve(((x0 + sl + x1 - sr) / 2, -o + bottom_t), 270, 180, k_i)
        c.curve((x0 + sl, yj_in), 180, 90, k_i)
        c.line((x0 + sl, top))
        return c.close().oriented(True)

    def hook_stem(self, x0, S, top, base, bend_o, bend_i, apex_o, apex_i, x_term, bottom_t, o) -> Contour:
        """The t master: a stem [x0, x0+S] from ``top`` down into a hook that
        turns right and ends in a vertical cut at ``x_term``.  Both edges of
        the tail rise by half the overshoot, so it runs out level at an even
        ``bottom_t`` instead of flicking up.  Heights are relative to
        ``base``; mirror the result for left or upward hooks (j, f)."""
        k = self.ten
        y_end = base - o / 2
        c = Contour((x0, top))
        c.line((x0, base + bend_o))
        c.curve((x0 + S + apex_o, base - o), 270, 0, k.outer)
        c.curve((x_term, y_end), 0, 3, 0.55)
        c.line((x_term, y_end + bottom_t))
        c.curve((x0 + S + apex_i, base - o + bottom_t), 183, 180, 0.55)
        c.curve((x0 + S, base + bend_i), 180, 90, k.inner)
        c.line((x0 + S, top))
        return c.close().oriented(True)

    def cut_cup(self, xr, S, top, yj, xm, o, bottom_t, y_cut) -> Contour:
        """Stem [xr-S, xr] from ``top`` into the lower-left quarter of a ring
        that is cut horizontally at ``y_cut`` (J): the c terminal on a stem."""
        k = self.ten
        rx, ry = xr - xm, yj + o
        o_q = oval_quadrants(xm, yj, rx, ry, k.outer)
        o_l = list(superellipse(xm, yj, rx, ry, k.terminal, k.outer).beziers())[2]
        i_q = oval_quadrants(xm, yj, rx - S, ry - bottom_t, k.inner)
        i_l = list(superellipse(xm, yj, rx - S, ry - bottom_t, k.terminal, k.inner).beziers())[2]
        c = Contour((xr, top)).line((xr, yj))
        c.cubic(*_reverse_seg(o_q[3])[1:])
        cut_o = _cut(_reverse_seg(o_l), y_cut, 1, "before")
        c.cubic(*cut_o[1:])
        cut_i = _cut(i_l, y_cut, 1, "after")
        c.line(cut_i[0])
        c.cubic(*cut_i[1:])
        c.cubic(*i_q[3][1:])
        c.line((xr - S, top))
        return c.close().oriented(True)

    # ============================================================== uppercase
    def H(self):
        st, C = self.st, self.cap
        W, S, B = self.wd.H, st.stemUpper, st.barUpper
        yc = self.sh.barUpperCenter * C
        cs = [rect(0, 0, S, C), rect(W - S, 0, W, C), rect(S - 10, yc - B / 2, W - S + 10, yc + B / 2)]
        g = Glyph("H", [0x48], W + 2 * self.sp.upperStraight, cs, note="stem + bar master")
        g.anchors = {"top": (W / 2, C), "bottom": (W / 2, 0)}
        return g.shifted(self.sp.upperStraight)

    def I(self):
        S, C = self.st.stemUpper, self.cap
        g = Glyph("I", [0x49], S + 2 * self.sp.upperStraight, [rect(0, 0, S, C)], note="H stem")
        g.anchors = {"top": (S / 2, C), "bottom": (S / 2, 0), "ogonek": (S / 2, 0)}
        return g.shifted(self.sp.upperStraight)

    def E(self):
        st, C = self.st, self.cap
        W, S, B = self.wd.E, st.stemUpper, st.barUpper
        yc = self.sh.barUpperCenter * C
        cs = [
            rect(0, 0, S, C),
            rect(S - 10, C - B, W, C),
            rect(S - 10, yc - (B - 6) / 2, W - 64, yc + (B - 6) / 2),
            rect(S - 10, 0, W + 16, B + 6),
        ]
        g = Glyph("E", [0x45], self.sp.upperStraight + W + 16 + 112, cs, note="H stem + H bar height; arms open")
        g.anchors = {"top": ((W + 16) / 2 + 30, C), "bottom": ((W + 16) / 2 + 30, 0), "ogonek": (W - 40, 0)}
        return g.shifted(self.sp.upperStraight)

    def O(self):
        st, C = self.st, self.cap
        W = self.wd.O
        cs = self.ring(W / 2, C / 2, W / 2, C / 2 + self.oc, st.roundUpperSide, st.roundUpperTop)
        g = Glyph("O", [0x4F], W + 2 * self.sp.upperRound, cs, note="ring master (capital)")
        y_h = self.sh.HornRoot * C
        g.anchors = {"top": (W / 2, C + self.oc / 2), "bottom": (W / 2, 0), "horn": (self.oval_right_x(W / 2, C / 2, W / 2, C / 2 + self.oc, y_h), y_h)}
        return g.shifted(self.sp.upperRound)

    def _apex_letter(self, W, flat, t_left, t_right, invert=False, bar=None):
        C = self.cap
        lo = ((0, 0), (W / 2 - flat / 2, C))
        ro = ((W, 0), (W / 2 + flat / 2, C))
        li = offset_line(*lo, -t_left)  # shift to the right of the left leg
        ri = offset_line(*ro, t_right)
        # offset_line shifts along the left normal of p->q; for the left leg
        # (going up-right) the left normal points up-left, so negate.
        apex_in = intersect_lines(*li, *ri)
        x_li0 = x_at_y(*li, 0)
        x_ri0 = x_at_y(*ri, 0)
        if bar is None:
            pts = [lo[0], (x_li0, 0), apex_in, (x_ri0, 0), ro[0], ro[1], lo[1]]
            cs = [polygon(pts)]
        else:
            b0, b1 = bar
            pts = [
                lo[0], (x_li0, 0), (x_at_y(*li, b0), b0), (x_at_y(*ri, b0), b0),
                (x_ri0, 0), ro[0], ro[1], lo[1],
            ]
            hole = polygon([(x_at_y(*li, b1), b1), (x_at_y(*ri, b1), b1), apex_in])
            cs = [polygon(pts).oriented(True), hole.oriented(False)]
        if invert:
            cs = [c.mirrored_y(C / 2) for c in cs]
        return [c.oriented(c.signed_area() > 0) for c in cs]

    def A(self):
        st = self.st
        W = self.wd.A
        b0 = self.sh.aBarUpper * self.cap
        cs = self._apex_letter(W, 204 * self.wk, st.diagonalUpper, st.diagonalUpper, bar=(b0, b0 + st.barUpper - 6))
        g = Glyph("A", [0x41], W + 2 * self.sp.upperDiagonal, cs, note="diagonal master; flat apex, low bar")
        g.anchors = {"top": (W / 2, self.cap), "bottom": (W / 2, 0), "ogonek": (W - 100, 0)}
        return g.shifted(self.sp.upperDiagonal)

    def V(self):
        st = self.st
        W = self.wd.V
        cs = self._apex_letter(W, 204 * self.wk, st.diagonalUpper, st.diagonalUpper, invert=True)
        g = Glyph("V", [0x56], W + 2 * self.sp.upperDiagonal, cs, note="A inverted without bar")
        g.anchors = {"top": (W / 2, self.cap), "bottom": (W / 2, 0)}
        return g.shifted(self.sp.upperDiagonal)

    def N(self):
        st, C = self.st, self.cap
        W, S, t = self.wd.N, st.stemN, st.diagonalN
        # Solve the horizontal width of the diagonal for its perpendicular width.
        wh = t
        for _ in range(20):
            ang = math.atan2(C, W - wh)
            wh = t / math.sin(ang)
        diag = polygon([(0, C), (wh, C), (W, 0), (W - wh, 0)])
        cs = [rect(0, 0, S, C), rect(W - S, 0, W, C), diag.oriented(True)]
        g = Glyph("N", [0x4E], W + 2 * self.sp.upperStraight - 8, cs, note="H stems (x0.91) + heavy diagonal")
        g.anchors = {"top": (W / 2, C), "bottom": (W / 2, 0)}
        return g.shifted(self.sp.upperStraight - 4)

    # ============================================================== lowercase
    def n(self, name="n", uni=0x6E, stem_top=None):
        st = self.st
        W, S, Sr = self.wd.n, st.stemLower, st.stemLowerRight
        top = stem_top or self.xh
        cs = [rect(0, 0, S, top), self.arch(0, S, W, Sr)]
        g = Glyph(name, [uni], self.sp.lowerStraight + W + self.sp.lowerStraightRight, cs, note="arch master")
        g.anchors = {"top": (W / 2 + 10, self.xh), "bottom": (W / 2, 0)}
        return g.shifted(self.sp.lowerStraight)

    def h(self):
        g = self.n("h", 0x68, stem_top=self.asc)
        g.note = "n with ascender stem"
        return g

    def m(self):
        st = self.st
        W, S = self.wd.m, st.stemM
        x2 = S + (W - 3 * S) / 2 + S  # right edge of the middle stem
        cs = [rect(0, 0, S, self.xh), self.arch(0, S, x2, S), self.arch(x2 - S, S, W, S - 2)]
        g = Glyph("m", [0x6D], self.sp.lowerStraight + W + self.sp.lowerStraightRight, cs, note="two n arches, counters x0.92")
        g.anchors = {"top": (W / 2, self.xh), "bottom": (W / 2, 0)}
        return g.shifted(self.sp.lowerStraight)

    def u(self):
        n = self.n()
        W = self.wd.n
        cx = self.sp.lowerStraight + W / 2
        cs = [c.rotated180(cx, self.xh / 2) for c in n.contours]
        g = Glyph("u", [0x75], n.width, cs, note="n rotated 180°")
        dx = self.sp.lowerStraightRight - self.sp.lowerStraight
        g.contours = [c.translated(dx, 0) for c in g.contours]
        g.anchors = {"top": (cx + dx - 10, self.xh), "bottom": (cx + dx, 0), "horn": (cx + dx + W / 2, self.sh.hornRoot * self.xh), "ogonek": (cx + dx + W / 2 - self.st.stemLower / 2, 0)}
        return g

    def r(self):
        st = self.st
        Wn, S, Wr = self.wd.n, st.stemLower, self.wd.r
        p = self.arch_parts(0, S, Wn, st.stemLowerRight)
        o2 = _cut(p["outer2"], Wr, 0, "before")
        i1 = _reverse_seg(p["inner1"])  # inner apex -> right
        # inner2 runs inner apex -> crotch; inner1 reversed runs inner apex -> right.
        i_seg = _cut(i1, Wr, 0, "before")  # inner apex -> cut
        c = Contour(p["start"]).line(p["join"])
        c.cubic(*p["outer1"][1:])
        c.cubic(*o2[1:])
        c.line(i_seg[-1])
        for seg in [_reverse_seg(i_seg)]:
            c.cubic(*seg[1:])
        c.cubic(*p["inner2"][1:])
        inset = 90
        c.line((S - inset, p["crotch"][1])).line((S - inset, p["start"][1]))
        arm = c.close().oriented(True)
        g = Glyph("r", [0x72], self.sp.lowerStraight + Wr + 36, [rect(0, 0, S, self.xh), arm], note="n arch cut vertically")
        g.anchors = {"top": (S / 2 + 90, self.xh), "bottom": (S / 2, 0)}
        return g.shifted(self.sp.lowerStraight)

    def o(self):
        st = self.st
        W = self.wd.o
        cs = self.ring(W / 2, self.xh / 2, W / 2, self.xh / 2 + self.ox, st.roundLowerSide, st.roundLowerTop)
        g = Glyph("o", [0x6F], W + 2 * self.sp.lowerRound, cs, note="ring master (lowercase)")
        y_h = self.sh.hornRoot * self.xh
        g.anchors = {"top": (W / 2, self.xh), "bottom": (W / 2, 0), "horn": (self.oval_right_x(W / 2, self.xh / 2, W / 2, self.xh / 2 + self.ox, y_h), y_h)}
        return g.shifted(self.sp.lowerRound)

    def _bowl_stem(self, name, uni, stem_side, stem_from, stem_to):
        st = self.st
        W, S = self.wd.d, st.stemLower
        bowl = self.bowl(0, W - S, st.roundLowerSide, st.roundLowerTop)
        stem = rect(W - S, stem_from, W, stem_to)
        cs = [bowl, stem]
        if stem_side == "left":
            cs = [c.mirrored_x(W / 2) for c in cs]
        lsb, rsb = (self.sp.lowerRound, self.sp.lowerStraight) if stem_side == "right" else (self.sp.lowerStraight, self.sp.lowerRound)
        g = Glyph(name, [uni], lsb + W + rsb, cs)
        cx = (W - S) * 0.5 if stem_side == "right" else W - (W - S) * 0.5
        g.anchors = {"top": (cx, self.xh), "bottom": (cx, 0)}
        return g.shifted(lsb)

    def d(self):
        g = self._bowl_stem("d", 0x64, "right", 0, self.asc)
        g.note = "bowl master + ascender stem"
        g.anchors["top"] = (g.anchors["top"][0], self.asc)
        g.anchors["topright"] = (self.sp.lowerRound + self.wd.d + 50, self.asc)
        return g

    def b(self):
        g = self._bowl_stem("b", 0x62, "left", 0, self.asc)
        g.note = "d mirrored"
        return g

    def q(self):
        g = self._bowl_stem("q", 0x71, "right", self.desc, self.xh)
        g.note = "d bowl + descender stem"
        return g

    def p(self):
        g = self._bowl_stem("p", 0x70, "left", self.desc, self.xh)
        g.note = "q mirrored"
        return g

    def c(self):
        st = self.st
        W = self.wd.c
        rx, ry = W / 2, self.xh / 2 + self.ox
        cy = self.xh / 2
        y_up = cy + self.sh.cTerminalUpper * ry
        y_lo = cy - self.sh.cTerminalLower * ry
        ring = self.cut_ring(W / 2, cy, rx, ry, st.roundLowerSide, st.roundLowerTop, y_up, y_lo)
        b = ring.bounds()
        g = Glyph("c", [0x63], self.sp.lowerRound + b[2] + self.sp.lowerTerminal, [ring], note="o ring cut by horizontal terminals")
        g.anchors = {"top": (W / 2 + 10, self.xh), "bottom": (W / 2 + 10, 0)}
        return g.shifted(self.sp.lowerRound)

    def e(self):
        st, k = self.st, self.ten
        W = self.wd.e
        rx, ry = W / 2, self.xh / 2 + self.ox
        cx, cy = W / 2, self.xh / 2
        side, top = st.roundLowerSide, st.roundLowerTop
        yb0 = self.sh.barLowerE * self.xh
        yb1 = yb0 + st.barE
        y_lo = cy - self.sh.eTerminalLower * ry
        o = oval_quadrants(cx, cy, rx, ry, k.outer)
        i = oval_quadrants(cx, cy, rx - side, ry - top, k.inner)
        o_lr = list(superellipse(cx, cy, rx, ry, k.terminal).beziers())[3]
        i_lr = list(superellipse(cx, cy, rx - side, ry - top, k.terminal).beziers())[3]
        # Outer: from the bar's bottom on the right, round the top, left and
        # bottom, to the lower terminal.
        if yb0 < cy:
            start_seg = _cut(o_lr, yb0, 1, "after")
            outer = [start_seg, o[0], o[1], o[2], _cut(o_lr, y_lo, 1, "before")]
        else:
            outer = [_cut(o[0], yb0, 1, "after"), o[1], o[2], _cut(o_lr, y_lo, 1, "before")]
        c = _contour_from_beziers(outer)
        # Terminal (horizontal) then inner curve back up to the bar.
        i_lo = _cut(i_lr, y_lo, 1, "before")
        c.line(i_lo[-1])
        c.cubic(*_reverse_seg(i_lo)[1:])
        i_left_low = _cut(i[2], yb0, 1, "after") if yb0 < cy else None
        if i_left_low is not None:
            c.cubic(*_reverse_seg(i_left_low)[1:])
        main = c.close().oriented(True)
        # Eye: inner curve above the bar.
        if yb1 <= cy:
            raise ValueError("the e bar must end above the bowl centre")
        eye_r = _cut(i[0], yb1, 1, "after")
        eye_l = _cut(i[1], yb1, 1, "before")
        eye = _contour_from_beziers([eye_r, eye_l]).close().oriented(False)
        g = Glyph("e", [0x65], self.sp.lowerRound + W + self.sp.lowerRound - 10, [main, eye], note="o ring + bar; lower terminal cut horizontally")
        g.anchors = {"top": (W / 2, self.xh), "bottom": (W / 2, 0), "ogonek": (W * 0.6, 0)}
        return g.shifted(self.sp.lowerRound)

    def s_shape(self, W, H, o, side, top_t, bot_t) -> Contour:
        """The S master: two ovals stacked (the upper one inset by
        sUpperInset), each cut by a horizontal terminal like c, joined by a
        shallow spine.  The spine edges leave the ovals' vertical extremes
        and cross the centre at sSpineAngle, sSpineWeight x side apart, so the
        stroke stays even from bowl to spine to bowl."""
        k, sh = self.ten, self.sh
        T, B = H + o, -o
        inset = sh.sUpperInset * W
        yu, yl = sh.sExtremeUpper * H, sh.sExtremeLower * H
        # Upper oval: left extreme (inset, yu), top T; lower: right extreme (W, yl), bottom B.
        urx, ury, lrx, lry = W / 2 - inset, T - yu, W / 2, yl - B
        uo = oval_quadrants(W / 2, yu, urx, ury, k.outer)
        ui = oval_quadrants(W / 2, yu, urx - side, ury - top_t, k.inner)
        lo = oval_quadrants(W / 2, yl, lrx, lry, k.outer)
        li = oval_quadrants(W / 2, yl, lrx - side, lry - bot_t, k.inner)
        uo[0] = list(superellipse(W / 2, yu, urx, ury, k.terminal).beziers())[0]
        ui[0] = list(superellipse(W / 2, yu, urx - side, ury - top_t, k.terminal).beziers())[0]
        lo[2] = list(superellipse(W / 2, yl, lrx, lry, k.terminal).beziers())[2]
        li[2] = list(superellipse(W / 2, yl, lrx - side, lry - bot_t, k.terminal).beziers())[2]
        y_ut = yu + sh.sTerminalUpper * ury
        y_lt = yl - sh.sTerminalLower * lry
        # Spine: centre between the extremes, edges offset along the normal.
        a = sh.sSpineAngle
        centre = ((inset + W) / 2, (yu + yl) / 2)
        n_up = mul(vec(90 - a), sh.sSpineWeight * side / 2)
        m_up, m_lo = add(centre, n_up), add(centre, mul(n_up, -1))
        ul_o, ul_i = (inset, yu), (inset + side, yu)
        lr_o, lr_i = (W, yl), (W - side, yl)
        ks = sh.sSpineTension
        c = _contour_from_beziers([_cut(uo[0], y_ut, 1, "after"), uo[1]])
        c.curve(m_lo, 270, 360 - a, k.outer, ks)
        c.curve(lr_i, 360 - a, 270, ks, k.inner)
        for seg in (_reverse_seg(li[3]), _cut(_reverse_seg(li[2]), y_lt, 1, "before")):
            c.cubic(*seg[1:])
        o_l = _cut(lo[2], y_lt, 1, "after")
        c.line(o_l[0])
        for seg in (o_l, lo[3]):
            c.cubic(*seg[1:])
        c.curve(m_up, 90, 180 - a, k.outer, ks)
        c.curve(ul_i, 180 - a, 90, ks, k.inner)
        for seg in (_reverse_seg(ui[1]), _cut(_reverse_seg(ui[0]), y_ut, 1, "before")):
            c.cubic(*seg[1:])
        return c.close().oriented(True)

    def s(self):
        st = self.st
        W, X = self.wd.s, self.xh
        s = self.s_shape(W, X, self.ox, st.sSide, st.roundLowerTop - 4, st.roundLowerTop)
        g = Glyph("s", [0x73], 2 * 92 + W, [s], note="two stacked ovals cut like c + shallow spine of near-stem weight")
        g.anchors = {"top": (W / 2, X), "bottom": (W / 2, 0)}
        return g.shifted(92)

    def a(self):
        st, k, sh = self.st, self.ten, self.sh
        W, S = self.wd.a, st.stemLower - 4
        X, T, B = self.xh, self.xh + self.ox, -self.ox
        side, top = st.roundLowerSide, st.roundLowerTop
        xs = W - S
        ko, ki, kt = k.outer, k.inner, k.terminal
        # Hook + stem (one contour): the n shoulder landing on the stem, over
        # an oval that spans the whole letter; its left quarter is cut
        # horizontally like the c terminal, just short of turning vertical.
        y_r = sh.archRightTangent * X
        x_l = sh.aHookLeft * W
        apex, i_apex = ((x_l + W) / 2, T), ((x_l + side + xs) / 2, T - st.archTop)
        left, i_left = (x_l, y_r), (x_l + side, y_r - 12)
        q_o = [apex, *Contour(apex).curve(left, 180, 270, kt).segments[0][1:]]
        q_i = [i_apex, *Contour(i_apex).curve(i_left, 180, 270, kt).segments[0][1:]]
        y_t = y_r + sh.aTerminal * (T - y_r)
        o_cut, i_cut = _cut(q_o, y_t, 1, "before"), _cut(q_i, y_t, 1, "before")
        hook = Contour((W, 0))
        hook.line((W, y_r))
        hook.curve(apex, 90, 180, k.shoulderOuter)
        hook.cubic(*o_cut[1:])
        hook.line(i_cut[-1])
        hook.cubic(*_reverse_seg(i_cut)[1:])
        hook.curve((xs, y_r - 12), 0, 270, k.shoulderInner)
        hook.line((xs, 0))
        hook = hook.close().oriented(True)
        # Bowl: a straight top that falls gently from the stem, an o quadrant
        # into the left side, and a long shoulder back up into the stem.
        y_bt = sh.aBowlTop * X
        y_bti = y_bt - st.barLower
        y_bj, y_bc = sh.aBowlJoin * X, sh.aBowlCrotch * X
        a_j = sh.bowlJoinAngle
        slope, x_c = sh.aBowlSlope, sh.aBowlCorner * xs
        fall = (xs - x_c) * math.tan(math.radians(slope))
        b_left, b_i_left = (0, (y_bt - fall + B) / 2), (side, (y_bti - fall + B + top) / 2)
        b_apex, b_i_apex = (0.5 * xs, B), (0.5 * (side + xs), B + top)
        bowl = Contour((xs + 60, y_bt))
        bowl.line((xs, y_bt))
        bowl.line((x_c, y_bt - fall))
        bowl.curve(b_left, 180 + slope, 270, ko)
        bowl.curve(b_apex, 270, 0, ko)
        bowl.curve((xs, y_bj), 0, a_j, ko, k.shoulderOuter)
        bowl.line(add((xs, y_bj), mul(vec(a_j), 90)))
        bowl.line((xs + 60, y_bc))
        bowl.line((xs, y_bc))
        bowl.curve(b_i_apex, 270, 180, ki)
        bowl.curve(b_i_left, 180, 90, ki)
        bowl.curve((x_c, y_bti - fall), 90, slope, ki)
        bowl.line((xs, y_bti))
        bowl = bowl.close().oriented(True)
        g = Glyph("a", [0x61], 92 + W + self.sp.lowerStraightRight, [hook, bowl], note="n shoulder cut like c + straight-topped bowl")
        g.anchors = {"top": (W * 0.47, X), "bottom": (W * 0.47, 0), "ogonek": (W - 80, 0)}
        return g.shifted(92)

    def t(self):
        st, k = self.st, self.ten
        S, X = st.stemLower, self.xh
        x0 = self.sp.lowerStraight  # stem left edge sits where n's stem would
        top = round(self.sh.tTop * self.asc)
        bar = rect(20, X - st.barLower, self.wd.t - 10, X)
        x_term = self.wd.t - 4
        bend = self.sh.tHookBend * X
        stem = self.hook_stem(x0, S, top, 0, bend, bend + 0.05 * X, 150, 132, x_term, st.barLower + 2, self.ox)
        g = Glyph("t", [0x74], x_term + 40, [bar, stem], note="stem + x-height bar; u-like hook, vertical terminal")
        # The vertical caron (ť) moves in as the stem grows so it stays inside the advance.
        g.anchors = {"top": (x0 + S / 2, top), "bottom": (x0 + S / 2 + 60, 0), "topright": (x0 + S + 90 - 0.2 * (S - self.reg.stemLower), self.asc)}
        return g

    def dot(self, cx, y0):
        d = self.sh.dotDiameter * self.st.stemLower
        return superellipse(cx, y0 + d / 2, d / 2, d / 2, self.ten.circle)

    def i(self):
        S = self.st.stemLower
        y_dot = self.xh + self.sh.dotGap * self.xh
        cs = [rect(0, 0, S, self.xh), self.dot(S / 2, y_dot)]
        g = Glyph("i", [0x69], S + 2 * self.sp.lowerStraight, cs, note="n stem + round dot")
        g.anchors = {"top": (S / 2, self.xh), "bottom": (S / 2, 0), "ogonek": (S / 2, 0)}
        return g.shifted(self.sp.lowerStraight)

    def dotlessi(self):
        S = self.st.stemLower
        g = Glyph("dotlessi", [0x131], S + 2 * self.sp.lowerStraight, [rect(0, 0, S, self.xh)], note="i without dot (base for Vietnamese marks)")
        g.anchors = {"top": (S / 2, self.xh), "bottom": (S / 2, 0)}
        return g.shifted(self.sp.lowerStraight)

    def l(self):
        S = self.st.stemLower
        g = Glyph("l", [0x6C], S + 2 * self.sp.lowerStraight, [rect(0, 0, S, self.asc)], note="n stem at ascender")
        g.anchors = {"top": (S / 2, self.asc), "bottom": (S / 2, 0), "topright": (S + 50, self.asc)}
        return g.shifted(self.sp.lowerStraight)

    # ================================================================ figures
    def zero(self):
        st = self.st
        W, adv = self.wd.figure, self.wd.tabularAdvance
        C = self.sys.m.figureHeight
        cs = self.ring(W / 2, C / 2, W / 2, C / 2 + self.of, st.figureSide, st.figureTop, k_in=self.ten.inner + 0.02)
        g = Glyph("zero", [0x30], adv, cs, note="O ring narrowed to tabular width")
        return g.shifted((adv - W) / 2)

    def one(self):
        st = self.st
        adv = self.wd.tabularAdvance
        C = self.sys.m.figureHeight
        S = st.figureStem
        xl = adv * 0.56 - S / 2
        flag_len, drop, t = 340, 236, st.figureTop + 8
        ang = math.atan2(drop, flag_len)
        tv = t / math.cos(ang)
        xf = xl - flag_len
        flag = polygon([(xl, C), (xf, C - drop), (xf, C - drop - tv), (xl + S / 2, C - tv + drop * (S / 2) / flag_len), (xl + S / 2, C)])
        cs = [rect(xl, 0, xl + S, C), flag.oriented(True)]
        return Glyph("one", [0x31], adv, cs, note="H stem + straight flag cut vertically; no foot")

    def two(self):
        st, k = self.st, self.ten
        W, adv = self.wd.figure, self.wd.tabularAdvance
        C = self.sys.m.figureHeight
        T = C + self.of
        side, top = st.figureSide, st.figureTop
        base = st.barUpper + 4
        y_t = (0.705 - self.sh.terminalClose) * C
        t_o, t_i = (24, y_t), (24 + side + 12, y_t)
        apex_o, apex_i = (0.5 * W, T), (0.5 * W, T - top)
        r_o, r_i = (W - 10, 0.7 * C), (W - 10 - side, 0.69 * C)
        a_sp = 40.0  # spine angle above horizontal where it lands on the base
        sw = st.figureStem * 0.84 / math.sin(math.radians(a_sp))
        ko, ki, kt = k.outer, k.inner, k.terminal
        c = Contour(t_o)
        c.curve(apex_o, 76, 0, kt, ko)
        c.curve(r_o, 0, 270, ko)
        c.curve((sw, base), 270, 180 + a_sp, ko, 0.57)
        c.line((W + 10, base)).line((W + 10, 0)).line((0, 0)).line((0, base))
        c.curve(r_i, a_sp, 90, 0.57, ki)
        c.curve(apex_i, 90, 180, ki)
        c.curve(t_i, 180, 256, ki, kt)
        two = c.close().oriented(True)
        g = Glyph("two", [0x32], adv, [two], note="c-like top + one-curve spine + base at cap-bar weight")
        return g.shifted((adv - W) / 2)

    def space(self):
        return Glyph("space", [0x20, 0xA0], 520, note="0.25 em; also no-break space")

    def period(self):
        d = self.sh.dotDiameter * self.st.stemLower
        g = Glyph("period", [0x2E], d + 2 * 130, [self.dot(d / 2, -2)], note="i dot on the baseline")
        return g.shifted(130)

    def comma(self):
        d = self.sh.dotDiameter * self.st.stemLower
        r = d / 2
        head = self.dot(r, -2)
        tail = polygon([(r + r - 8, r - 14), (r + 6 * self.wk, -330), (r - 104 * self.wk, -330), (r - 0.4 * r, 28)])
        g = Glyph("comma", [0x2C], d + 2 * 120, [head, tail.oriented(True)], note="period head + straight tail cut horizontally")
        return g.shifted(120)

    def hyphen(self):
        t = self.st.barLower
        y = 0.47 * self.xh
        g = Glyph("hyphen", [0x2D], 560 + 2 * 120, [rect(0, y - t / 2, 560, y + t / 2)], note="bar weight at e-bar height")
        return g.shifted(120)

    def notdef(self):
        W, C = 1000, self.cap
        t = 100
        cs = [rect(0, 0, W, C), rect(t, t, W - t, C - t).reversed()]
        return Glyph(".notdef", [], W + 2 * 120, cs, note="empty box").shifted(120)


CORE = [
    ".notdef", "space", "H", "O", "I", "E", "A", "V", "N",
    "n", "o", "h", "p", "d", "b", "q", "a", "e", "c", "s", "r", "t", "u", "m", "i", "l", "dotlessi",
    "zero", "one", "two", "period", "comma", "hyphen",
]

_METHOD = {".notdef": "notdef", "zero": "zero", "one": "one", "two": "two"}


def build_core(builder: Builder) -> dict[str, Glyph]:
    out = {}
    for name in CORE:
        out[name] = getattr(builder, _METHOD.get(name, name))()
    return out

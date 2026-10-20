"""Lowercase recipes beyond the Phase 2 core.

    hook (t master)   f j ȷ             (t hook mirrored up or left, vertical cut)
    bowl + tail       g                 (q bowl; tail is the a hook mirrored, cut horizontally)
    diagonal          k v w x y z       (strokes of perpendicular width diagonalLower)
    joins             æ œ               (a/o sharing a stroke with e)
    marks of stroke   ø ð ħ ł þ         (slash, bar, extended stems)
    superiors         ª º               (a/o scaled, re-emboldened to 0.77 stroke)
"""

from __future__ import annotations

import math

from .geometry import Contour, intersect_lines, offset_line, polygon, rect, shared_foot, stroke, untangled, with_corner, with_foot, x_at_y
from .glyphs import Glyph
from .upper import hcut_centre


def apex_polygon(W, H, flat, t, invert=False):
    """The A/V diagonal pair (flat apex, horizontal feet) at height ``H``."""
    lo = ((0, 0), (W / 2 - flat / 2, H))
    ro = ((W, 0), (W / 2 + flat / 2, H))
    li = offset_line(*lo, -t)
    ri = offset_line(*ro, t)
    apex_in = intersect_lines(*li, *ri)
    pts = [lo[0], (x_at_y(*li, 0), 0), apex_in, (x_at_y(*ri, 0), 0), ro[0], ro[1], lo[1]]
    c = polygon(pts)
    if invert:
        c = c.mirrored_y(H / 2)
    return c.oriented(True)


class LowerMixin:
    def _lc(self, name, uni, W, cs, lsb, rsb, note, anchors=None):
        X = self.xh
        g = Glyph(name, [uni] if uni else [], lsb + W + rsb, cs, note=note)
        g.anchors = anchors if anchors is not None else {"top": (W / 2, X), "bottom": (W / 2, 0)}
        return g.shifted(lsb)

    # ------------------------------------------------------------------ hooks
    def f(self):
        st, X, A = self.st, self.xh, self.asc
        S = st.stemLower
        x0 = 150
        x_term = x0 + S + 300
        bend = self.sh.tHookBend * X
        hook = self.hook_stem(x0, S, A, 0, bend, bend + 0.05 * X, 170, 150, x_term, st.archTop - 2, self.ox)
        hook = hook.mirrored_y(A / 2).oriented(True)
        bar = rect(10, X - st.barLower, x0 + S + 210, X)
        g = Glyph("f", [0x66], x_term + self.sp.lowerHook, [hook, bar], note="t hook mirrored to the ascender; t bar")
        g.anchors = {"top": (x0 + S / 2 + 60, X), "bottom": (x0 + S / 2, 0)}
        return g

    def dotlessj(self):
        st, X, D = self.st, self.xh, self.desc
        S = st.stemLower
        x0 = self.sp.lowerStraight
        hook = self.hook_stem(x0, S, X, D, 330, 370, 96, 80, x0 + S + 230, st.barLower, self.ox)
        hook = hook.mirrored_x(x0 + S / 2).oriented(True)
        g = Glyph("dotlessj", [0x237], S + 2 * x0, [hook], note="i stem into the t hook, mirrored to the left at the descender")
        g.anchors = {"top": (x0 + S / 2, X), "bottom": (x0 + S / 2, 0)}
        return g

    def j(self):
        g = self.dotlessj()
        S = self.st.stemLower
        x0 = self.sp.lowerStraight
        g.contours.append(self.dot(x0 + S / 2, self.xh + self.sh.dotGap * self.xh))
        g.name, g.unicodes, g.note = "j", [0x6A], "dotless j + i dot"
        return g

    def g(self):
        st, k = self.st, self.ten
        W, S, X, D = self.wd.d, st.stemLower, self.xh, self.desc
        xs = W - S
        bowl = self.bowl(0, xs, st.roundLowerSide, st.roundLowerTop)
        B = D - self.ox
        bt = st.roundLowerTop - 6
        y_rv = B + 400
        y_t = B + 240 + self.sh.terminalClose * X
        ko, ki, kt = k.outer, k.inner, k.terminal
        c = Contour((W, X)).line((W, y_rv))
        c.curve((0.49 * W, B), 270, 180, ko)
        c.curve((60, y_t), 180, 116, ko, kt)
        c.line((60 + st.roundLowerSide + 8, y_t))
        c.curve((0.5 * W, B + bt), 296, 0, kt, ki)
        c.curve((xs, y_rv + 20), 0, 90, ki)
        c.line((xs, X))
        tail = c.close().oriented(True)
        return self._lc("g", 0x67, W, [bowl, tail], self.sp.lowerRound, self.sp.lowerStraight,
                        "q bowl + a hook mirrored as the tail (horizontal cut)",
                        {"top": ((W - S) * 0.5, X), "bottom": ((W - S) * 0.5, 0)})

    # -------------------------------------------------------------- diagonals
    def k(self):
        st, X, A, sp = self.st, self.xh, self.asc, self.sp
        W, S = self.wd.k, st.stemLower
        t = st.diagonalLower
        root = (S * 0.5, self.sh.KArmRoot * X)
        tip = hcut_centre(root, W - 10, X, t - 6, +1)
        arm = stroke(root, tip, t - 6, cut=("p", "h"))
        j = (root[0] + (tip[0] - root[0]) * 0.42, root[1] + (tip[1] - root[1]) * 0.42)
        foot = hcut_centre(j, W + 20, 0, t, +1)
        leg = stroke(j, foot, t, cut=("p", "h"))
        return self._lc("k", 0x6B, W + 20, [rect(0, 0, S, A), arm, leg], sp.lowerStraight, sp.lowerDiagonal,
                        "l stem + K arm/leg at x-height", {"top": (S / 2, A), "bottom": (W * 0.45, 0)})

    def v(self):
        st, X, sp = self.st, self.xh, self.sp
        W = self.wd.v
        c = apex_polygon(W, X, 180, st.diagonalLower, invert=True)
        return self._lc("v", 0x76, W, [c], sp.lowerDiagonal, sp.lowerDiagonal, "V at x-height, diagonalLower")

    def w(self):
        st, X, sp = self.st, self.xh, self.sp
        W, t = self.wd.w, st.diagonalLower - 12
        b, c, d = 0.25 * W, 0.5 * W, 0.75 * W
        a = hcut_centre((b, 0), 0, X, t, -1)
        e = hcut_centre((d, 0), W, X, t, +1)
        cs = (shared_foot([stroke(a, (b, 0), t), stroke((b, 0), (c, X), t)])
              + shared_foot([stroke((c, X), (d, 0), t), stroke((d, 0), e, t)]))
        return self._lc("w", 0x77, W, cs, sp.lowerDiagonal, sp.lowerDiagonal, "W at x-height")

    def x(self):
        st, X, sp = self.st, self.xh, self.sp
        W, t = self.wd.x, st.diagonalLower
        inset = 30
        m = (W / 2, X / 2)
        cs = [
            stroke(hcut_centre(m, 0, 0, t, -1), hcut_centre(m, W - inset, X, t, +1), t),
            stroke(hcut_centre(m, W, 0, t - 12, +1), hcut_centre(m, inset, X, t - 12, -1), t - 12),
        ]
        return self._lc("x", 0x78, W, cs, sp.lowerDiagonal + 4, sp.lowerDiagonal + 4, "X at x-height")

    def _dot_clear(self, t):
        """Extra room for the dot below beside a heavier tail and a larger dot
        (0 at Regular)."""
        d = self.sh.dotDiameter * self.st.stemLower
        d0 = self.sys.raw["shapes"]["dotDiameter"] * self.reg.stemLower
        return 0.55 * (t - self.reg.diagonalLower) + 0.5 * (d - d0)

    def y(self):
        st, X, D, sp = self.st, self.xh, self.desc, self.sp
        W, t = self.wd.y, st.diagonalLower
        vx = 0.5 * W + 20
        left_top = hcut_centre((vx, 0), 0, X, t, -1)
        right_top = hcut_centre((vx, 0), W, X, t, +1)
        tail = (vx - (right_top[0] - vx) * (-D) / X, D)
        right = stroke(right_top, tail, t)
        # The left arm's outer foot corner is a shared corner on the right
        # stroke's edge and its inner corner sits 1 unit inside the stroke, so
        # the rounded union has no unit step at the baseline.
        rp = [right.start] + [seg[-1] for seg in right.segments]
        xl, xr = sorted(x_at_y(p, q, 0) for p, q in zip(rp, rp[1:] + rp[:1]) if p[1] * q[1] < 0)
        cs = [with_foot(stroke(left_top, (vx, 0), t), 0, xl, xr - 1), with_corner(right, (xl, 0))]
        return self._lc("y", 0x79, W, cs, sp.lowerDiagonal, sp.lowerDiagonal, "v whose right stroke runs straight to the descender",
                        {"top": (W / 2, X), "bottom": (vx + 170 + self._dot_clear(t), 0)})

    def z(self):
        st, X, sp = self.st, self.xh, self.sp
        W, T, t = self.wd.z, st.barLower, st.diagonalLower + 8
        top_r = W - 20
        p_r, p_l = (top_r, X - T), (0, T + 4)
        dx, dy = p_r[0] - p_l[0], p_r[1] - p_l[1]
        th = math.atan2(dy, dx) + math.asin(t / math.hypot(dx, dy))
        ux, uy = math.cos(th), math.sin(th)
        x_at = lambda p, yy: p[0] + (yy - p[1]) * ux / uy
        diag = polygon([p_l, (x_at(p_l, X - T), X - T), p_r, (x_at(p_r, T + 4), T + 4)]).oriented(True)
        cs = [rect(24, X - T, top_r, X), rect(0, 0, W, T + 4), diag]
        return self._lc("z", 0x7A, W, cs, sp.lowerBar, sp.lowerBar, "Z at x-height with e-bar weight")

    # ------------------------------------------------------------------ joins
    def ae(self):
        a, e = self.a(), self.e()
        S = self.st.stemLower - 4
        stem_left = 92 + self.wd.a - S
        dx = stem_left - self.sp.lowerRound
        cs = list(a.contours) + [c.translated(dx, 0) for c in e.contours]
        g = Glyph("ae", [0xE6], dx + e.width, cs, note="a + e sharing the a stem")
        g.anchors = {"top": ((dx + e.width) / 2, self.xh), "bottom": ((dx + e.width) / 2, 0)}
        return g

    def oe(self):
        o, e = self.o(), self.e()
        right_stroke = self.sp.lowerRound + self.wd.o - self.st.roundLowerSide
        dx = right_stroke - self.sp.lowerRound
        cs = list(o.contours) + [c.translated(dx, 0) for c in e.contours]
        g = Glyph("oe", [0x153], dx + e.width, cs, note="o + e sharing one round stroke")
        g.anchors = {"top": ((dx + e.width) / 2, self.xh), "bottom": ((dx + e.width) / 2, 0)}
        return g

    def oslash(self):
        g = self.o()
        W, X, lsb = self.wd.o, self.xh, self.sp.lowerRound
        g.contours.append(stroke((lsb + 0.06 * W, -0.08 * X), (lsb + 0.94 * W, 1.08 * X), self.st.punctStroke - 10, cut="h"))
        g.name, g.unicodes, g.note = "oslash", [0xF8], "o + slash"
        g.anchors = {k: v for k, v in g.anchors.items() if k != "horn"}
        return g

    def eth(self):
        st, k, X, A = self.st, self.ten, self.xh, self.asc
        W = self.wd.o
        side, top = st.roundLowerSide, st.roundLowerTop
        ring = self.ring(W / 2, X / 2, W / 2, X / 2 + self.ox, side, top)
        t_top = st.barLower + 10
        x_top = 0.3 * W
        c = Contour((W, X / 2))
        c.curve((x_top + 200, A), 90, 125, k.outer)
        c.line((x_top, A))
        c.curve((W - side, X / 2 + 60), 305, 270, k.inner)
        rise = c.close().oriented(True)
        bar = stroke((0.22 * W, 0.80 * A), (0.80 * W, 0.94 * A), st.barLower - 10, cut="v")
        return self._lc("eth", 0xF0, W, ring + [rise, bar], self.sp.lowerRound, self.sp.lowerRound,
                        "o ring + a rising curved stroke to the ascender, crossed by a bar")

    def thorn(self):
        g = self._bowl_stem("thorn", 0xFE, "left", self.desc, self.asc)
        g.note = "p bowl + stem from descender to ascender"
        return g

    def hbar(self):
        g = self.h()
        st = self.st
        x0 = self.sp.lowerStraight
        yc = (self.xh + self.asc) / 2 + 30
        T = st.barLower
        g.contours.append(rect(x0 - 70, yc - T / 2, x0 + st.stemLower + 150, yc + T / 2))
        g.name, g.unicodes, g.note = "hbar", [0x127], "h + đ bar"
        return g

    def lslash(self):
        st, X = self.st, self.xh
        S = st.stemLower
        reach = 230
        x0 = reach + 40
        cx = x0 + S / 2
        slash = stroke((cx - reach, 0.46 * X), (cx + reach, 0.46 * X + 300), st.punctStroke, cut="v")
        g = Glyph("lslash", [0x142], 2 * x0 + S, [rect(x0, 0, x0 + S, self.asc), slash], note="l + slash (vertical cuts)")
        return g

    def germandbls(self):
        st, k, X, A, sp = self.st, self.ten, self.xh, self.asc, self.sp
        S = st.stemLower
        W = 1000 + 1.5 * (S - self.reg.stemLower)  # widens with the stem
        ko, ki, kt = k.outer, k.inner, k.terminal
        side, top = st.roundLowerSide, st.roundLowerTop
        bw = st.bowlWaist - 10
        y_s = 0.72 * A
        T = A + self.oa
        y_wt = 0.79 * X
        x_w = 0.4 * W
        y_ur = (T + y_wt - bw) / 2
        c = Contour((0, 0)).line((0, y_s))
        c.curve((0.43 * W, T), 90, 0, ko)
        c.curve((0.8 * W, y_ur), 0, 270, ko)
        c.curve((x_w, y_wt - bw), 270, 180, ko)
        c.line((x_w, y_wt))
        c.curve((0.8 * W - side + 14, y_ur), 0, 90, ki)
        c.curve((0.44 * W, T - top), 90, 180, ki)
        c.curve((S, y_s), 180, 270, ki)
        c.line((S, 0))
        upper = c.close().oriented(True)
        y_lr = (y_wt - self.ox) / 2
        # The terminal rides on the bottom stroke; the counter's lowest point
        # stays right of the cut (at Regular both rules give the plain values).
        x_t, y_t = S + 84, (0.2 + self.sh.terminalClose) * X + (top - self.reg.roundLowerTop)
        x_cut = x_t + side + 8
        x_bi = max(0.56 * W, x_cut + 98)
        c = Contour((x_w, y_wt))
        c.curve((W, y_lr), 0, 270, ko)
        c.curve((x_bi - 0.01 * W, -self.ox), 270, 180, ko)
        c.curve((x_t, y_t), 180, 114, ko, kt)
        c.line((x_cut, y_t))
        c.curve((x_bi, -self.ox + top), 294, 0, kt, ki)
        c.curve((W - side, y_lr), 0, 90, ki)
        c.curve((x_w, y_wt - bw), 90, 180, ki)
        lower = c.close().oriented(True)
        return self._lc("germandbls", 0xDF, W, [upper, lower], sp.lowerStraight, sp.lowerRound - 10,
                        "stem rising into an arch; waist ends in a vertical cut; lower bowl cut like s")

    # -------------------------------------------------------------- superiors
    def superior(self, g: Glyph, name, uni, scale=0.62, weight=0.77):
        """``g`` scaled to ``scale`` with its baseline raised so the scaled
        x-height meets the cap height, then emboldened back to ``weight`` of
        the full stroke.  Underlined (Spanish ordinals)."""
        st = self.st
        b = [c.bounds() for c in g.contours]
        x0 = min(bb[0] for bb in b)
        x1 = max(bb[2] for bb in b)
        base = self.cap - scale * self.xh
        d = (weight - scale) * st.stemLower / 2
        sb = 70
        cs = [part for c in g.contours for part in untangled(c.translated(-x0, 0).scaled(scale).translated(sb + d, base).offset(d))]
        w = (x1 - x0) * scale + 2 * d
        bar_t = st.hairStroke - 10
        y_bar = base - 100 - bar_t
        cs.append(rect(sb, y_bar, sb + w, y_bar + bar_t))
        return Glyph(name, [uni], w + 2 * sb, cs, note=f"{g.name} superior: x{scale}, stroke x{weight}, underlined")

    def ordfeminine(self):
        return self.superior(self.a(), "ordfeminine", 0xAA)

    def ordmasculine(self):
        return self.superior(self.o(), "ordmasculine", 0xBA)


LOWER = ["f", "g", "j", "dotlessj", "k", "v", "w", "x", "y", "z", "ae", "oe", "oslash", "eth", "thorn", "hbar",
         "lslash", "germandbls", "ordfeminine", "ordmasculine"]

"""Uppercase recipes beyond the Phase 2 core.

Every capital reuses a master from ``glyphs.Builder``:

    stem / bar      F L T Ħ Ł          (H stem, H bar weight, open arms)
    side bowl       B D P R Þ Œ        (flat arms turning into the O curve)
    cut ring        C G                (O ring cut by horizontal terminals)
    cup             U J                (O curve on stems; J cut like c)
    diagonal        K M W X Y Z Æ      (strokes of perpendicular width)
    S master        S                  (the s spine scaled to the cap height)
"""

from __future__ import annotations

import math

from .geometry import Contour, intersect_lines, oval_quadrants, polygon, rect, stroke, superellipse
from .glyphs import Glyph, _contour_from_beziers, _cut, _reverse_seg


def hcut_centre(p, x_edge, y, width, side):
    """Centre-line end (x, y) of a stroke from ``p`` whose horizontally cut
    end has its ``side`` edge (-1 left, +1 right) exactly at ``x_edge``."""
    x = x_edge
    for _ in range(30):
        ang = math.atan2(abs(y - p[1]), abs(x - p[0]))
        hw = width / 2 / math.sin(ang)
        x = x_edge - side * hw
    return (x, y)


class UpperMixin:
    def _cap_glyph(self, name, uni, W, cs, lsb, rsb, note, anchors=None):
        C = self.cap
        g = Glyph(name, [uni] if uni else [], lsb + W + rsb, cs, note=note)
        g.anchors = anchors if anchors is not None else {"top": (W / 2, C), "bottom": (W / 2, 0)}
        return g.shifted(lsb)

    # ------------------------------------------------------------ stem + bars
    def F(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S, T = self.wd.F, st.stemUpper, st.barUpper
        yc = self.sh.barUpperCenter * C - 12
        cs = [rect(0, 0, S, C), rect(S - 10, C - T, W, C), rect(S - 10, yc - (T - 6) / 2, W - 72, yc + (T - 6) / 2)]
        return self._cap_glyph("F", 0x46, W, cs, sp.upperStraight, sp.upperArm, "E without the bottom arm",
                               {"top": (W / 2 + 10, C), "bottom": (S / 2 + 40, 0)})

    def L(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S, T = self.wd.L, st.stemUpper, st.barUpper
        cs = [rect(0, 0, S, C), rect(S - 10, 0, W, T + 6)]
        return self._cap_glyph("L", 0x4C, W, cs, sp.upperStraight, sp.upperBar, "H stem + E bottom arm",
                               {"top": (S / 2 + 40, C), "bottom": (W * 0.46, 0), "topright": (S + 80, C)})

    def T(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S, T = self.wd.T, st.stemUpper, st.barUpper
        cs = [rect(0, C - T, W, C), rect(W / 2 - S / 2, 0, W / 2 + S / 2, C - T + 10)]
        return self._cap_glyph("T", 0x54, W, cs, sp.upperOpen, sp.upperOpen, "H bar on an H stem")

    # ------------------------------------------------------------- side bowls
    def B(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S, T, Tw = self.wd.B, st.stemUpper, st.barUpper, st.bowlWaist
        ym = self.sh.BWaist * C
        side = st.roundUpperSide - 8
        upper = self.side_bowl(S, ym - Tw / 2, C, W - 72, T, Tw, side - 6)
        lower = self.side_bowl(S, 0, ym + Tw / 2, W, Tw, T + 6, side)
        return self._cap_glyph("B", 0x42, W, [rect(0, 0, S, C), upper, lower], sp.upperStraight, sp.upperBowl,
                               "H stem + two side bowls; upper bowl 72 narrower, waist = bowlWaist",
                               {"top": (W * 0.46, C), "bottom": (W * 0.46, 0)})

    def D(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S, T = self.wd.D, st.stemUpper, st.barUpper
        bowl = self.side_bowl(S, 0, C, W, T, T + 6, st.roundUpperSide, rh=0.84 * C / 2)
        return self._cap_glyph("D", 0x44, W, [rect(0, 0, S, C), bowl], sp.upperStraight, sp.upperRound,
                               "H stem + side bowl (O curve, flat arms)",
                               {"top": (W * 0.46, C), "bottom": (W * 0.46, 0)})

    def P(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S, T = self.wd.P, st.stemUpper, st.barUpper
        y0 = self.sh.PBowlBottom * C
        bowl = self.side_bowl(S, y0, C, W, T, st.bowlWaist, st.roundUpperSide)
        return self._cap_glyph("P", 0x50, W, [rect(0, 0, S, C), bowl], sp.upperStraight, sp.upperBowl,
                               "H stem + side bowl closing at PBowlBottom",
                               {"top": (W * 0.46, C), "bottom": (S / 2 + 40, 0)})

    def R(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S, T, Tw = self.wd.R, st.stemUpper, st.barUpper, st.bowlWaist
        y0 = self.sh.PBowlBottom * C
        bowl = self.side_bowl(S, y0, C, W - 50, T, Tw, st.roundUpperSide)
        t = st.diagonalUpper
        top = (0.5 * W, y0 + Tw / 2)
        bot = hcut_centre(top, W, 0, t, +1)
        leg = stroke(top, bot, t, cut=("p", "h"))
        return self._cap_glyph("R", 0x52, W, [rect(0, 0, S, C), bowl, leg], sp.upperStraight, sp.upperDiagonal + 22,
                               "P bowl + straight leg from the waist",
                               {"top": (W * 0.44, C), "bottom": (W * 0.44, 0)})

    def Thorn(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S, T = self.wd.P - 20, st.stemUpper, st.barUpper
        bowl = self.side_bowl(S, 0.19 * C, 0.79 * C, W, T, T, st.roundUpperSide)
        return self._cap_glyph("Thorn", 0xDE, W, [rect(0, 0, S, C), bowl], sp.upperStraight, sp.upperBowl,
                               "H stem + P bowl lowered into the middle")

    # -------------------------------------------------------------- cut rings
    def C(self):
        st, C, sp = self.st, self.cap, self.sp
        W = self.wd.C
        rx, ry, cy = W / 2, C / 2 + self.oc, C / 2
        y_up = cy + self.sh.CTerminalUpper * ry
        y_lo = cy - self.sh.CTerminalLower * ry
        ring = self.cut_ring(W / 2, cy, rx, ry, st.roundUpperSide, st.roundUpperTop, y_up, y_lo)
        right = ring.bounds()[2]
        g = Glyph("C", [0x43], sp.upperRound + right + sp.upperTerminal, [ring], note="O ring cut by horizontal terminals (c)")
        g.anchors = {"top": (W / 2 + 20, C + self.oc / 2), "bottom": (W / 2 + 20, 0)}
        return g.shifted(sp.upperRound)

    def G(self):
        st, C, sp, k = self.st, self.cap, self.sp, self.ten
        W = self.wd.G
        cx, cy, rx, ry = W / 2, C / 2, W / 2, C / 2 + self.oc
        side, top, Sg, Tb = st.roundUpperSide, st.roundUpperTop, st.stemUpper, st.barUpper
        y_up = cy + self.sh.CTerminalUpper * ry
        yv, ybt = self.sh.GJoin * C, self.sh.GBarTop * C
        x_bl = 0.56 * W
        o = oval_quadrants(cx, cy, rx, ry, k.outer)
        i = oval_quadrants(cx, cy, rx - side, ry - top, k.inner)
        o_up = _cut(list(superellipse(cx, cy, rx, ry, k.terminal).beziers())[0], y_up, 1, "after")
        i_up = _cut(list(superellipse(cx, cy, rx - side, ry - top, k.terminal).beziers())[0], y_up, 1, "after")
        c = _contour_from_beziers([o_up, o[1], o[2]])
        c.curve((W, yv), 0, 90, k.outer)
        c.line((W, ybt)).line((x_bl, ybt)).line((x_bl, ybt - Tb)).line((W - Sg, ybt - Tb)).line((W - Sg, yv + 24))
        c.curve((cx, -self.oc + top), 270, 180, k.inner)
        c.cubic(*_reverse_seg(i[2])[1:])
        c.cubic(*_reverse_seg(i[1])[1:])
        c.cubic(*_reverse_seg(i_up)[1:])
        g = Glyph("G", [0x47], sp.upperRound + W + (sp.upperStraight + sp.upperRound) / 2, [c.close().oriented(True)],
                  note="C ring; lower right turns vertical at GJoin and ends in an H-weight bar, no spur")
        g.anchors = {"top": (W / 2, C + self.oc / 2), "bottom": (W / 2, 0)}
        return g.shifted(sp.upperRound)

    def Q(self):
        st, C, sp = self.st, self.cap, self.sp
        W = self.wd.O
        cs = self.ring(W / 2, C / 2, W / 2, C / 2 + self.oc, st.roundUpperSide, st.roundUpperTop)
        tail = stroke((0.62 * W, 0.16 * C), (0.95 * W, -0.15 * C), st.diagonalUpper - 6, cut="h")
        g = Glyph("Q", [0x51], W + 2 * sp.upperRound, cs + [tail], note="O ring + straight tail, both ends cut horizontally")
        g.anchors = {"top": (W / 2, C + self.oc / 2), "bottom": (W / 2, 0)}
        return g.shifted(sp.upperRound)

    def S(self):
        st, C, sp = self.st, self.cap, self.sp
        W = self.wd.S
        side = st.sSide + 12
        s = self.s_shape(W, C, self.oc, side, st.roundUpperTop - 4, st.roundUpperTop)
        return self._cap_glyph("S", 0x53, W, [s], sp.upperBowl, sp.upperBowl, "s master at cap height",
                               {"top": (W / 2, C + self.oc / 2), "bottom": (W / 2, 0)})

    # ------------------------------------------------------------------- cups
    def U(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S = self.wd.U, st.stemUpper - 4
        cup = self.cup(0, W, S, S, C, self.sh.UJoin * C, st.roundUpperTop, self.oc)
        return self._cap_glyph("U", 0x55, W, [cup], sp.upperCup, sp.upperCup, "H stems x0.98 into the O curve",
                               {"top": (W / 2, C), "bottom": (W / 2, 0), "ogonek": (W * 0.6, 0), "horn": (W, self.sh.HornRoot * C)})

    def J(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S = self.wd.J, st.stemUpper
        c = self.cut_cup(W, S, C, self.sh.UJoin * C, 0.5 * W, self.oc, st.roundUpperTop, 0.22 * C)
        return self._cap_glyph("J", 0x4A, W, [c], sp.upperHook, sp.upperStraight, "H stem into the U curve, cut like c",
                               {"top": (W - S / 2, C), "bottom": (W / 2, 0)})

    # -------------------------------------------------------------- diagonals
    def K(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S = self.wd.K, st.stemUpper
        t_a, t_l = st.diagonalUpper - 10, st.diagonalUpper
        root = (S * 0.5, self.sh.KArmRoot * C)
        tip = hcut_centre(root, W, C, t_a, +1)
        arm = stroke(root, tip, t_a, cut=("p", "h"))
        j = (root[0] + (tip[0] - root[0]) * 0.4, root[1] + (tip[1] - root[1]) * 0.4)
        foot = hcut_centre(j, W + 30, 0, t_l, +1)
        leg = stroke(j, foot, t_l, cut=("p", "h"))
        return self._cap_glyph("K", 0x4B, W + 30, [rect(0, 0, S, C), arm, leg], sp.upperStraight, sp.upperDiagonal + 6,
                               "H stem; arm from KArmRoot, leg branching off the arm")

    def M(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S, t = self.wd.M, st.stemN, st.diagonalM
        wh = t
        for _ in range(30):
            ang = math.atan2(C, W / 2 - wh / 2)
            wh = t / math.sin(ang)
        left = polygon([(0, C), (wh, C), (W / 2 + wh / 2, 0), (W / 2 - wh / 2, 0)]).oriented(True)
        right = left.mirrored_x(W / 2).oriented(True)
        cs = [rect(0, 0, S, C), rect(W - S, 0, W, C), left, right]
        return self._cap_glyph("M", 0x4D, W, cs, sp.upperStraight - 4, sp.upperStraight - 4,
                               "N stems; two diagonals meet in a flat vertex on the baseline")

    def W(self):
        st, C, sp = self.st, self.cap, self.sp
        W, t = self.wd.W, st.diagonalUpper - 12
        b, c, d = 0.255 * W, 0.5 * W, 0.745 * W
        a = hcut_centre((b, 0), 0, C, t, -1)
        e = hcut_centre((d, 0), W, C, t, +1)
        cs = [stroke(a, (b, 0), t), stroke((b, 0), (c, C), t), stroke((c, C), (d, 0), t), stroke((d, 0), e, t)]
        return self._cap_glyph("W", 0x57, W, cs, sp.upperDiagonal, sp.upperDiagonal,
                               "two V at diagonalUpper - 12; middle apex at cap height")

    def X(self):
        st, C, sp = self.st, self.cap, self.sp
        W, t = self.wd.X, st.diagonalUpper
        inset = 40  # the top is narrower than the foot
        p0 = hcut_centre((W / 2, C / 2), 0, 0, t, -1)
        q0 = hcut_centre((W / 2, C / 2), W - inset, C, t, +1)
        p1 = hcut_centre((W / 2, C / 2), W, 0, t - 12, +1)
        q1 = hcut_centre((W / 2, C / 2), inset, C, t - 12, -1)
        cs = [stroke(p0, q0, t), stroke(p1, q1, t - 12)]
        return self._cap_glyph("X", 0x58, W, cs, sp.upperDiagonal + 6, sp.upperDiagonal + 6,
                               "two crossing diagonals, top 40 narrower; the falling stroke 12 lighter")

    def Y(self):
        st, C, sp = self.st, self.cap, self.sp
        W, t, S = self.wd.Y, st.diagonalUpper, st.stemUpper
        xm, yj = W / 2, self.sh.YJoin * C
        a = hcut_centre((xm, yj), 0, C, t, -1)
        hw = a[0]
        d = (xm - a[0], yj - C)
        outer_l = ((0, C), (d[0], C + d[1]))
        inner_l = ((2 * hw, C), (2 * hw + d[0], C + d[1]))
        crotch = intersect_lines(*inner_l, (xm, 0), (xm, C))
        y_m = intersect_lines(*outer_l, (xm - S / 2, 0), (xm - S / 2, C))[1]
        pts = [(0, C), (2 * hw, C), crotch, (W - 2 * hw, C), (W, C), (xm + S / 2, y_m), (xm + S / 2, 0), (xm - S / 2, 0), (xm - S / 2, y_m)]
        return self._cap_glyph("Y", 0x59, W, [polygon(pts).oriented(True)], sp.upperDiagonal, sp.upperDiagonal,
                               "V arms meeting at YJoin; outer edges land on the H stem")

    def Z(self):
        st, C, sp = self.st, self.cap, self.sp
        W, T, t = self.wd.Z, st.barUpper, st.diagonalUpper + 6
        top_r = W - 24
        p_r, p_l = (top_r, C - T), (0, T + 6)
        dx, dy = p_r[0] - p_l[0], p_r[1] - p_l[1]
        L = math.hypot(dx, dy)
        th = math.atan2(dy, dx) + math.asin(t / L)
        ux, uy = math.cos(th), math.sin(th)
        x_at = lambda p, y: p[0] + (y - p[1]) * ux / uy
        diag = polygon([p_l, (x_at(p_l, C - T), C - T), p_r, (x_at(p_r, T + 6), T + 6)]).oriented(True)
        cs = [rect(30, C - T, top_r, C), rect(0, 0, W, T + 6), diag]
        return self._cap_glyph("Z", 0x5A, W, cs, sp.upperBar, sp.upperBar, "H bars + diagonal of perpendicular width")

    # ------------------------------------------------------------- composites
    def AE(self):
        st, C, sp = self.st, self.cap, self.sp
        S, T, t = st.stemUpper, st.barUpper, st.diagonalUpper
        xe = 760
        We = xe + self.wd.E - 40
        top = (xe + 0, C)
        foot = hcut_centre(top, 0, 0, t, -1)
        hw = foot[0]
        leg = stroke(foot, (xe + hw, C), t)
        b0 = self.sh.aBarUpper * C
        yc = self.sh.barUpperCenter * C
        cs = [
            leg, rect(xe, 0, xe + S, C), rect(xe, C - T, We, C),
            rect(xe + S - 10, yc - (T - 6) / 2, We - 64, yc + (T - 6) / 2),
            rect(xe + S - 10, 0, We + 16, T + 6),
            rect(hw + b0 * xe / C, b0, xe + 10, b0 + T - 6),
        ]
        return self._cap_glyph("AE", 0xC6, We + 16, cs, sp.upperDiagonal, 112, "A left leg + E", {"top": ((We + 16) / 2, C), "bottom": ((We + 16) / 2, 0)})

    def OE(self):
        st, C, sp = self.st, self.cap, self.sp
        S, T = st.stemUpper, st.barUpper
        Wb = 1180
        bowl = self.side_bowl(S, 0, C, Wb, T, T + 6, st.roundUpperSide, rh=0.86 * C / 2).mirrored_x(Wb / 2).oriented(True)
        xs = Wb - S
        We = xs + self.wd.E - 30
        yc = self.sh.barUpperCenter * C
        cs = [bowl, rect(xs, 0, Wb, C), rect(xs, C - T, We, C), rect(xs + S - 10, yc - (T - 6) / 2, We - 64, yc + (T - 6) / 2), rect(xs + S - 10, 0, We + 16, T + 6)]
        return self._cap_glyph("OE", 0x152, We + 16, cs, sp.upperRound, 112, "D bowl mirrored + E")

    def Oslash(self):
        st, C, sp = self.st, self.cap, self.sp
        W = self.wd.O
        cs = self.ring(W / 2, C / 2, W / 2, C / 2 + self.oc, st.roundUpperSide, st.roundUpperTop)
        slash = stroke((0.07 * W, -0.06 * C), (0.93 * W, 1.06 * C), st.punctStroke, cut="h")
        g = Glyph("Oslash", [0xD8], W + 2 * sp.upperRound, cs + [slash], note="O + slash at punctStroke")
        g.anchors = {"top": (W / 2, C), "bottom": (W / 2, 0)}
        return g.shifted(sp.upperRound)

    def Dcroat(self):
        st, C = self.st, self.cap
        d = self.D()
        lsb = self.sp.upperStraight
        T = st.barUpper - 14
        bar = rect(lsb - 120, C / 2 - T / 2, lsb + st.stemUpper + 230, C / 2 + T / 2)
        g = Glyph("Dcroat", [0x110], d.width, list(d.contours) + [bar], note="D + bar through the stem at C/2")
        g.anchors = dict(d.anchors)
        return g

    def Lslash(self):
        st, C, sp = self.st, self.cap, self.sp
        g = self.L()
        lsb = sp.upperStraight
        S = st.stemUpper
        slash = stroke((lsb - 130, 0.34 * C), (lsb + S + 300, 0.6 * C), st.punctStroke, cut="v")
        g.contours.append(slash)
        g.name, g.unicodes, g.note = "Lslash", [0x141], "L + slash across the stem (vertical cuts)"
        g.anchors = {k: v for k, v in g.anchors.items() if k in ("top", "bottom")}
        return g

    def Hbar(self):
        st, C = self.st, self.cap
        g = self.H()
        lsb, W = self.sp.upperStraight, self.wd.H
        T = st.barUpper - 20
        g.contours.append(rect(lsb - 70, 0.74 * C, lsb + W + 70, 0.74 * C + T))
        g.name, g.unicodes, g.note = "Hbar", [0x126], "H + bar above the crossbar"
        return g

    def Germandbls(self):
        st, C, sp = self.st, self.cap, self.sp
        S, T, Tw = st.stemUpper, st.barUpper, st.bowlWaist
        dS = S - self.reg.stemUpper  # keep the diagonal and bowl clear of the stem
        W = 1060 + dS
        x_tr = 848 + 1.1 * dS
        y_w = 0.6 * C
        t = st.diagonalUpper
        foot = (381.6 + 1.3 * dS, y_w - Tw)
        tip = hcut_centre(foot, x_tr, C, t, +1)
        diag = stroke(foot, tip, t, cut="h")
        hw = x_tr - tip[0]
        x_left_top = foot[0] + (tip[0] - foot[0]) * Tw / (C - foot[1]) - hw
        bowl = self.side_bowl(x_left_top + 6, 0, y_w, W, Tw, T + 6, st.roundUpperSide, overlap=0)
        cs = [rect(0, 0, S, C), rect(S - 10, C - T, x_tr, C), diag, bowl]
        return self._cap_glyph("uni1E9E", 0x1E9E, W, cs, sp.upperStraight, sp.upperBowl, "stem + top arm + diagonal into a B lower bowl open at the left")


UPPER = ["B", "C", "D", "F", "G", "J", "K", "L", "M", "P", "Q", "R", "S", "T", "U", "W", "X", "Y", "Z",
         "AE", "OE", "Oslash", "Dcroat", "Thorn", "Lslash", "Hbar", "Germandbls"]

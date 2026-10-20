"""Punctuation and symbols.

    dot (i dot)          : ; ! ? ¡ ¿ … · • ÷
    comma                ' " ‘ ’ “ ” ‚ „ (comma family; straight quotes taper)
    bar weight           - – — _ = + − ± (barLower), # (bars + slanted stems)
    stroke               / \\ | < > ‹ › « » × (punctStroke, grid-cut ends)
    curve                ( ) { } and ? (ring tensions)
    letters / figures    $ ¢ £ ¥ € ₫ & @ § ¶ © ® ° ™ % (built from the
                         letter and figure masters, re-emboldened when scaled)

Math symbols sit on the tabular advance and centre on ``mathAxis`` x cap height.
"""

from __future__ import annotations

import math

from .geometry import Contour, add, intersect_lines, mul, offset_cubic, oval_quadrants, polygon, rect, stroke, superellipse, united, vec
from .glyphs import Glyph, _contour_from_beziers
from .lower import apex_polygon
from .upper import hcut_centre


class PunctMixin:
    # ------------------------------------------------------------- helpers
    @property
    def _d(self):
        return self.sh.dotDiameter * self.st.stemLower

    def _g(self, name, uni, width, cs, note, shift=0.0, anchors=None):
        unis = uni if isinstance(uni, list) else ([uni] if uni else [])
        g = Glyph(name, unis, width, cs, note=note)
        if anchors:
            g.anchors = anchors
        return g.shifted(shift) if shift else g

    def _scaled(self, g: Glyph, scale, weight, dx, dy, ref_stem=None):
        """Contours of ``g`` (left edge at 0) scaled and re-emboldened so the
        stroke reads ``weight`` x the full stroke."""
        ref = ref_stem or self.st.stemUpper
        b = [c.bounds() for c in g.contours]
        x0 = min(bb[0] for bb in b)
        d = (weight - scale) * ref / 2
        cs = [c.translated(-x0, 0).scaled(scale).translated(dx + d, dy).offset(d) for c in g.contours]
        w = (max(bb[2] for bb in b) - x0) * scale + 2 * d
        return cs, w

    def _math(self, name, uni, cs, note):
        adv = self.wd.tabularAdvance
        return Glyph(name, [uni], adv, [c.translated(adv / 2, 0) for c in cs], note=note)

    @property
    def _ym(self):
        return self.sh.mathAxis * self.cap

    # ----------------------------------------------------------------- dots
    def colon(self):
        d = self._d
        cs = [self.dot(d / 2, 0), self.dot(d / 2, self.xh - d)]
        return self._g("colon", 0x3A, d + 260, cs, "two period dots, the upper one under the x-height", 130)

    def semicolon(self):
        d = self._d
        comma = self.comma()
        cs = list(comma.contours) + [self.dot(120 + d / 2, self.xh - d)]
        return self._g("semicolon", 0x3B, comma.width, cs, "comma + colon dot")

    def exclam(self):
        d, C = self._d, self.cap
        cx = 130 + d / 2
        wt, wb = 196 * self.wk, 160 * self.wk
        bar = polygon([(cx - wb / 2, 0.31 * C), (cx + wb / 2, 0.31 * C), (cx + wt / 2, C), (cx - wt / 2, C)]).oriented(True)
        return self._g("exclam", 0x21, d + 260, [bar, self.dot(cx, 0)], "tapered stem (196 -> 160) + period dot")

    def exclamdown(self):
        g = self.exclam()
        cx = 130 + self._d / 2
        cs = [c.rotated180(cx, self.xh / 2) for c in g.contours]
        return self._g("exclamdown", 0xA1, g.width, cs, "! rotated about x-height / 2")

    def _question_contours(self):
        """Top arc as the 2, then an S spine drawn as a centre line offset by
        half the stem on each side, into a centred stem."""
        st, k, C = self.st, self.ten, self.cap
        W, t = 820, st.stemLower - 6
        top = st.roundLowerTop
        T = C + self.oc
        cx = W / 2
        y_r, y_s1, y_s0, y_t = 0.73 * C, 0.47 * C, 0.31 * C, (0.71 - self.sh.terminalClose) * C
        ko, ki, kt = k.outer, k.inner, k.terminal
        spine = [(W - t / 2, y_r), (W - t / 2, y_r - 170), (cx, y_s1 + 190), (cx, y_s1)]
        right = offset_cubic(spine, t / 2)
        left = offset_cubic(spine, -t / 2)
        c = Contour((0, y_t))
        c.curve((0.5 * W, T), 76, 0, kt, ko)
        c.curve(right[0], 0, 270, ko)
        c.cubic(*right[1:])
        c.line((cx + t / 2, y_s0)).line((cx - t / 2, y_s0)).line(left[3])
        c.cubic(left[2], left[1], left[0])
        c.curve((0.5 * W, T - top), 90, 180, ki)
        c.curve((t + 30, y_t), 180, 256, ki, kt)
        return [c.close().oriented(True), self.dot(cx, 0)], W

    def question(self):
        cs, W = self._question_contours()
        return self._g("question", 0x3F, W + 2 * 100, cs, "2 top turning into a centred stem; period dot", 100)

    def questiondown(self):
        cs, W = self._question_contours()
        cs = [c.rotated180(W / 2, self.xh / 2) for c in cs]
        return self._g("questiondown", 0xBF, W + 2 * 100, cs, "? rotated about x-height / 2", 100)

    def periodcentered(self):
        d = self._d
        return self._g("periodcentered", 0xB7, d + 260, [self.dot(d / 2, 0.47 * self.xh - d / 2)], "period dot at hyphen height", 130)

    def bullet(self):
        d = 1.5 * self._d
        c = superellipse(d / 2, 0.47 * self.xh, d / 2, d / 2, self.ten.circle)
        return self._g("bullet", 0x2022, d + 2 * 120, [c], "dot x1.5 at hyphen height", 120)

    def ellipsis(self):
        d = self._d
        gap = 150
        cs = [self.dot(d / 2 + i * (d + gap), 0) for i in range(3)]
        return self._g("ellipsis", 0x2026, 3 * d + 2 * gap + 2 * 120, cs, "three period dots", 120)

    # --------------------------------------------------------------- quotes
    def _comma_shape(self):
        return list(self.comma().contours)  # already shifted by its 120 sidebearing

    def quoteright(self):
        d = self._d
        dy = self.cap - (d - 2)
        cs = [c.translated(0, dy) for c in self._comma_shape()]
        return self._g("quoteright", 0x2019, self.comma().width, cs, "comma raised to the cap height")

    def quoteleft(self):
        g = self.quoteright()
        b = [c.bounds() for c in g.contours]
        cx = (min(x[0] for x in b) + max(x[2] for x in b)) / 2
        cy = (min(x[1] for x in b) + max(x[3] for x in b)) / 2
        return self._g("quoteleft", 0x2018, g.width, [c.rotated180(cx, cy) for c in g.contours], "’ rotated 180°")

    def quotesinglbase(self):
        return self._g("quotesinglbase", 0x201A, self.comma().width, self._comma_shape(), "comma")

    def _double(self, single: Glyph, name, uni, note):
        step = self._d + 90
        cs = list(single.contours) + [c.translated(step, 0) for c in single.contours]
        return self._g(name, uni, single.width + step, cs, note)

    def quotedblright(self):
        return self._double(self.quoteright(), "quotedblright", 0x201D, "two ’")

    def quotedblleft(self):
        return self._double(self.quoteleft(), "quotedblleft", 0x201C, "two ‘")

    def quotedblbase(self):
        return self._double(self.quotesinglbase(), "quotedblbase", 0x201E, "two ‚")

    @property
    def _tick_w(self):
        return 168 * self.wk, 120 * self.wk

    def _tick(self, x):
        C = self.cap
        wt, wb = self._tick_w
        return polygon([(x - wb / 2, 0.67 * C), (x + wb / 2, 0.67 * C), (x + wt / 2, C), (x - wt / 2, C)]).oriented(True)

    def quotesingle(self):
        wt = self._tick_w[0]
        return self._g("quotesingle", 0x27, wt + 2 * 130, [self._tick(130 + wt / 2)], "tapered tick, cap height to 0.67")

    def quotedbl(self):
        gap, wt = 120, self._tick_w[0]
        x1 = 130 + wt / 2
        return self._g("quotedbl", 0x22, 2 * wt + gap + 2 * 130, [self._tick(x1), self._tick(x1 + wt + gap)], "two ticks")

    # ------------------------------------------------------------ chevrons
    def _chevron(self, x_tip, yc, w, h, t, left=True):
        tip = (x_tip, yc)
        a = hcut_centre(tip, x_tip + w, yc + h / 2, t, +1)
        b = hcut_centre(tip, x_tip + w, yc - h / 2, t, +1)
        cs = [stroke(tip, a, t), stroke(tip, b, t)]
        if not left:
            cs = [c.mirrored_x(x_tip + w / 2).oriented(True) for c in cs]
        return cs

    def _guil(self, name, uni, count, left):
        """Chevrons keep Regular's angle and counter: a heavier stroke grows
        outward, and the gap between the two chevrons of « stays, so the
        counter never closes.  Equal side bearings either way."""
        w, h, step0, sb = 330, 520, 300, 150
        t, t0 = self.st.punctStroke, self.reg.punctStroke
        yc = 0.5 * self.xh
        L0 = w - t0 / 2 / math.sin(math.atan2(h / 2, w))  # Regular: tip to inner end corner
        sin0 = math.sin(math.atan2(h / 2, hcut_centre((0, 0), L0, h / 2, t0, +1)[0]))
        grow = (t - t0) / 2 / sin0  # the stroke's extra half-width along the axis
        L, step = L0 + grow, step0 + 2 * grow
        cs = []
        for i in range(count):
            cs += self._chevron(i * step, yc, L, h, t, left)
        x0, x1 = min(c.bounds()[0] for c in cs), max(c.bounds()[2] for c in cs)
        cs = [c.translated(sb - x0, 0) for c in cs]
        return self._g(name, uni, x1 - x0 + 2 * sb, cs, f"{count} chevron(s) of punctStroke, pointed tip")

    def guilsinglleft(self):
        return self._guil("guilsinglleft", 0x2039, 1, True)

    def guilsinglright(self):
        return self._guil("guilsinglright", 0x203A, 1, False)

    def guillemotleft(self):
        return self._guil("guillemotleft", 0xAB, 2, True)

    def guillemotright(self):
        return self._guil("guillemotright", 0xBB, 2, False)

    # --------------------------------------------------------------- dashes
    def _bar_glyph(self, name, uni, width, inset, note):
        t, y = self.st.barLower, 0.47 * self.xh
        return self._g(name, uni, width, [rect(inset, y - t / 2, width - inset, y + t / 2)], note)

    def endash(self):
        return self._bar_glyph("endash", 0x2013, 1024, 60, "hyphen bar, half em")

    def emdash(self):
        return self._bar_glyph("emdash", 0x2014, 2048, 60, "hyphen bar, one em")

    def underscore(self):
        t = self.st.barLower
        return self._g("underscore", 0x5F, 1000, [rect(0, -330, 1000, -330 + t)], "bar weight below the baseline, joins")

    # -------------------------------------------------------------- strokes
    def slash(self):
        t = self.st.punctStroke
        y0, y1 = -280, 1600
        w = 620
        hw = t / 2 / math.sin(math.atan2(y1 - y0, w))
        c = stroke((hw, y0), (hw + w, y1), t)
        return self._g("slash", 0x2F, w + 2 * hw + 2 * 30, [c], "punctStroke from -280 to 1600", 30)

    def backslash(self):
        g = self.slash()
        return self._g("backslash", 0x5C, g.width, [c.mirrored_x(g.width / 2).oriented(True) for c in g.contours], "slash mirrored")

    def bar(self):
        t = 160 * self.wk
        return self._g("bar", 0x7C, t + 2 * 190, [rect(0, -440, t, 1620)], "vertical bar, descender to above the ascender", 190)

    def _paren(self):
        st, y_top, y_bot = self.st, 1640, -400
        ym = (y_top + y_bot) / 2
        x_end, we, t = 300, 150, st.stemLower - 14
        c = Contour((x_end, y_top))
        c.curve((0, ym), 238, 270, 0.6)
        c.curve((x_end, y_bot), 270, 302, 0.6)
        c.line((x_end + we, y_bot))
        c.curve((t, ym), 122, 90, 0.6)
        c.curve((x_end + we, y_top), 90, 58, 0.6)
        return c.close().oriented(True), x_end + we

    def parenleft(self):
        c, w = self._paren()
        return self._g("parenleft", 0x28, w + 110 + 70, [c], "arc of stem weight, ends cut horizontally", 110)

    def parenright(self):
        g = self.parenleft()
        return self._g("parenright", 0x29, g.width, [c.mirrored_x(g.width / 2).oriented(True) for c in g.contours], "( mirrored")

    def bracketleft(self):
        t, tb, y_top, y_bot, w = 170 * self.wk, self.st.barLower, 1640, -400, 380
        cs = [rect(0, y_bot, t, y_top), rect(t - 10, y_top - tb, w, y_top), rect(t - 10, y_bot, w, y_bot + tb)]
        return self._g("bracketleft", 0x5B, w + 150 + 60, cs, "stem + bar-weight arms", 150)

    def bracketright(self):
        g = self.bracketleft()
        return self._g("bracketright", 0x5D, g.width, [c.mirrored_x(g.width / 2).oriented(True) for c in g.contours], "[ mirrored")

    def braceleft(self):
        k = self.ten
        t, tb, y_top, y_bot = 168 * self.wk, self.st.barLower, 1640, -400
        ym = (y_top + y_bot) / 2
        tip_w = 190
        x_s = 70 + tip_w  # stem left edge; the point sits 70 from the origin
        r = 300   # corner radius (outer): the arms are mostly curve
        x_end = x_s + r + 40
        c = Contour((x_end, y_top))
        c.line((x_s + r, y_top))
        c.curve((x_s, y_top - r), 180, 270, k.outer)
        c.line((x_s, ym + 260))
        c.curve((x_s - tip_w, ym + tb / 2 + 4), 270, 180, k.outer)
        c.line((x_s - tip_w, ym - tb / 2 - 4))
        c.curve((x_s, ym - 260), 0, 270, k.outer)
        c.line((x_s, y_bot + r))
        c.curve((x_s + r, y_bot), 270, 0, k.outer)
        c.line((x_end, y_bot)).line((x_end, y_bot + tb))
        c.line((x_s + r, y_bot + tb))
        c.curve((x_s + t, y_bot + r), 180, 90, k.inner)
        c.line((x_s + t, ym - 240))
        c.curve((x_s + t - 150, ym), 90, 180, k.inner)
        c.curve((x_s + t, ym + 240), 0, 90, k.inner)
        c.line((x_s + t, y_top - r))
        c.curve((x_s + r, y_top - tb), 90, 0, k.inner)
        c.line((x_end, y_top - tb))
        return self._g("braceleft", 0x7B, x_end + 70, [c.close().oriented(True)], "stem with arms that are mostly curve and a flat-cut point at mid-height", 0)

    def braceright(self):
        g = self.braceleft()
        return self._g("braceright", 0x7D, g.width, [c.mirrored_x(g.width / 2).oriented(True) for c in g.contours], "{ mirrored")

    # -------------------------------------------------------------- symbols
    def asterisk(self):
        C, t = self.cap, self.st.punctStroke - 10
        R = 0.25 * C
        cx, cy = 80 + R * math.cos(math.radians(30)) + t / 2, C - R
        cs = []
        for a in (90, 270):
            cs.append(stroke((cx, cy), (cx, cy + R * math.sin(math.radians(a))), t, cut=("p", "h")))
        for a in (30, 150, 210, 330):
            end = (cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)))
            cs.append(stroke((cx, cy), end, t, cut=("p", "v")))
        return self._g("asterisk", 0x2A, 2 * (cx), cs, "six spokes; vertical ones cut horizontally, slanted ones vertically")

    def numbersign(self):
        C = self.cap
        W, t_v, t_h, sl = 1000, 160 * self.wk, 150 * self.wk, 60
        cs = []
        for x in (0.34 * W, 0.68 * W):
            cs.append(stroke((x - sl, 0), (x + sl, C), t_v))
        for y in (0.33 * C, 0.65 * C):
            cs.append(rect(0.04 * W, y - t_h / 2, 0.98 * W, y + t_h / 2))
        adv = self.wd.tabularAdvance
        return self._g("numbersign", 0x23, adv, cs, "slanted stems + bar-weight bars, tabular", (adv - W) / 2)

    def percent(self):
        C, st = self.cap, self.st
        side, top = 146 * self.wk, 128 * self.wk
        # Heavier rings grow so their counters keep the Regular opening;
        # lighter rings keep the Regular size (their counters open, as in SF).
        grow = max(0.0, side - 146)
        rw, rh = 400 + 1.6 * grow, 600 + 0.8 * grow
        W = 1460
        up = self.ring(rw / 2, C - rh / 2, rw / 2, rh / 2 + self.oc / 2, side, top)
        lo = self.ring(W - rw / 2, rh / 2, rw / 2, rh / 2 + self.oc / 2, side, top)
        sl = stroke(hcut_centre((W / 2, C / 2), 0.24 * W, 0, st.punctStroke, -1), hcut_centre((W / 2, C / 2), 0.76 * W, C, st.punctStroke, +1), st.punctStroke)
        return self._g("percent", 0x25, W + 2 * 60, up + lo + [sl], "two small rings + slash", 60)

    def ampersand(self):
        """A round loop whose left side runs straight down to the baseline as
        the leg and whose right side turns down-left into the bowl; the bowl
        rises on the right into a tail cut horizontally.  The leg crosses the
        loop's right side and the bowl, as in the neo-grotesque &."""
        st, k, C = self.st, self.ten, self.cap
        W, o = 1380, self.oc
        T, B = C + o, -o
        ko, ki, kt = k.outer, k.inner, k.terminal
        side_l, top_l = 160 * self.wk, 148 * self.wk
        t_leg = t_d = st.diagonalUpper - 8
        side_b, bot_b, t_tail = st.roundUpperSide - 12, st.roundUpperTop - 12, st.stemUpper - 22
        # Loop: the top half of an oval.
        lx, rx, ly = 0.39 * W, 0.235 * W, 0.78 * C
        ry = T - ly
        oq, iq = oval_quadrants(lx, ly, rx, ry, ko), oval_quadrants(lx, ly, rx - side_l, ry - top_l, ki)
        loop = _contour_from_beziers([oq[0], oq[1]]).line((lx - rx + side_l, ly))
        for seg in (list(reversed(iq[1])), list(reversed(iq[0]))):
            loop.cubic(*seg[1:])
        loop = loop.close().oriented(True)
        # Leg: from the loop's left side straight to the baseline at 48°.
        leg_a = 48
        th = math.radians(leg_a)
        p_r = (0.97 * W, 0)
        p_l = (p_r[0] - t_leg / math.sin(th), 0)
        lo, li = (lx - rx, ly), (lx - rx + side_l, ly)

        def on_leg(p, x_side):
            y_hit = (p[0] - x_side) * math.tan(th)  # where the side's vertical meets the leg edge
            y = y_hit - 0.9 * (ly - y_hit)
            return (p[0] - y / math.tan(th), y)

        leg = Contour(lo).curve(on_leg(p_l, lo[0]), 270, 360 - leg_a, ko)
        leg.line(p_l).line(p_r).line(on_leg(p_r, li[0]))
        leg.curve(li, 180 - leg_a, 90, ki)
        leg = leg.close().oriented(True)
        # Bowl: the loop's right side bends down-left round one centre (its
        # counter edge becomes the bowl's outside), rounds the left and
        # bottom, and rises into the tail.
        a_d, a_t, r_o = 210, 80, 380
        ro, ri = (lx + rx, ly), (lx + rx - side_l, ly)
        j_ul = add((ro[0] - r_o, ly), mul(vec(a_d + 90), r_o - side_l))
        j_lr = add(j_ul, mul(vec(a_d + 90), t_d))
        yb, bx = 0.29 * C, 0.41 * W
        tail = (0.81 * W, 0.55 * C)
        c = Contour(ri)
        c.curve(j_ul, 270, a_d, ki)
        c.curve((0, yb), a_d, 270, ko)
        c.curve((bx, B), 270, 0, ko)
        c.curve(tail, 0, a_t, ko, kt)
        c.line((tail[0] - t_tail / math.sin(math.radians(a_t)), tail[1]))
        c.curve((bx + 10, B + bot_b), 180 + a_t, 180, kt, ki)
        c.curve((side_b, yb), 180, 90, ki)
        c.curve(j_lr, 90, a_d - 180, ki)
        c.curve(ro, a_d - 180, 90, ko)
        bowl = c.close().oriented(True)
        return self._g("ampersand", 0x26, W + 2 * 70, [loop, leg, bowl], "oval loop; left side runs into a 48° leg, right side into the bowl; tail cut horizontally", 70)

    def at(self):
        st, k, C = self.st, self.ten, self.cap
        W = 1640
        t = st.hairStroke + 10
        top, bot = 1.0 * C, -0.24 * C
        cy = (top + bot) / 2
        ko, ki = k.outer, k.inner
        xs = 0.62 * W
        yi_t, yi_b = cy + 0.29 * C, cy - 0.29 * C
        bowl = self.ring(0.47 * W, cy, xs + t / 2 - 0.47 * W, 0.29 * C, st.roundLowerSide - 30, st.roundLowerTop - 24)
        c = Contour((xs, yi_t)).line((xs, cy - 0.17 * C))
        c.curve((0.8 * W, yi_b - 10), 270, 0, ko)
        c.curve((W, cy), 0, 90, ko)
        c.curve((W / 2, top), 90, 180, ko)
        c.curve((0, cy), 180, 270, ko)
        c.curve((W / 2, bot), 270, 0, ko)
        c.curve((0.8 * W, bot + 30), 0, 12, 0.55)
        c.line((0.8 * W, bot + 30 + t + 4))
        c.curve((W / 2, bot + t), 192, 180, 0.55)
        c.curve((t, cy), 180, 90, ki)
        c.curve((W / 2, top - t), 90, 0, ki)
        c.curve((W - t, cy), 0, 270, ki)
        c.curve((0.8 * W, yi_b - 10 + t), 270, 180, ki)
        c.curve((xs + t, cy - 0.17 * C + 30), 180, 90, ki)
        c.line((xs + t, yi_t))
        spiral = c.close().oriented(True)
        return self._g("at", 0x40, W + 2 * 70, bowl + [spiral], "single-storey a whose stem turns into the outer ring", 70)

    def section(self):
        """One s turned 180° about the centre of its lower bowl, which is
        closed into a full ring: the upper and lower strokes share the loop
        like the links of a chain."""
        st, C, k = self.st, self.cap, self.ten
        side, top_t, bot_t = st.sSide - 30, st.roundLowerTop - 30, st.roundLowerTop - 26
        W, H = 880 + (side - (self.reg.sSide - 30)), 0.83 * C  # widens by the added side weight
        o = self.oc / 2
        yl = self.sh.sExtremeLower * H
        y0 = C - (H + o - yl)  # ring centre: the upper s tops out at cap height + o
        up = self.s_shape(W, H, o, side, top_t, bot_t).translated(0, y0 - yl)
        lo = up.rotated180(W / 2, y0)
        rx, ry = W / 2, yl + o

        def ring(rx_, ry_, k_round):
            # Terminal tension on the quadrants that carry the hidden s terminals.
            t, r = oval_quadrants(W / 2, y0, rx_, ry_, k.terminal), oval_quadrants(W / 2, y0, rx_, ry_, k_round)
            return _contour_from_beziers([t[0], r[1], t[2], r[3]]).close()

        loop = [ring(rx, ry, k.outer), ring(rx - side, ry - bot_t, k.inner).reversed()]
        cs = united([[up], [lo], loop])
        return self._g("section", 0xA7, W + 2 * 90, cs, "s + the same s turned 180° about its lower bowl, closed into a ring", 90)

    def paragraph(self):
        C = self.cap
        W, t = 1000, 150 * self.wk
        x1, x2 = 0.5 * W, 0.8 * W
        y_bot = -0.25 * C
        bowl = Contour((x1 + 10, C)).curve((0, 0.70 * C), 180, 270, self.ten.outer).curve((x1 + 10, 0.40 * C), 270, 0, self.ten.outer).close().oriented(True)
        cs = [bowl, rect(x1, y_bot, x1 + t, C), rect(x2, y_bot, x2 + t, C), rect(x1, C - t, x2 + t, C)]
        return self._g("paragraph", 0xB6, x2 + t + 2 * 80, cs, "solid half bowl + two stems to the descender", 80)

    # -------------------------------------------------------------- currency
    def dollar(self):
        st, C = self.st, self.cap
        side = st.sSide + 6
        W = 920 + (side - (self.reg.sSide + 6))  # widens by the added side weight
        s = self.s_shape(W, C, self.oc, side, st.roundUpperTop - 8, st.roundUpperTop - 4)
        t = st.punctStroke - 10
        cx = W / 2
        cs = [s, rect(cx - t / 2, C - 40, cx + t / 2, C + 200), rect(cx - t / 2, -200, cx + t / 2, 40)]
        adv = self.wd.tabularAdvance
        return self._g("dollar", 0x24, adv, cs, "S + bar ends above and below, tabular", (adv - W) / 2)

    def cent(self):
        st = self.st
        W, H = 880, 1.12 * self.xh
        rx, ry, cy = W / 2, H / 2 + self.ox, H / 2
        ring = self.cut_ring(W / 2, cy, rx, ry, st.roundLowerSide, st.roundLowerTop, cy + self.sh.cTerminalUpper * ry, cy - self.sh.cTerminalLower * ry)
        t = st.punctStroke - 10
        cs = [ring, rect(W / 2 - t / 2, -150, W / 2 + t / 2, H + 150)]
        adv = self.wd.tabularAdvance
        return self._g("cent", 0xA2, adv, cs, "c at 1.12 x-height + vertical bar, tabular", (adv - W) / 2)

    def sterling(self):
        st, C = self.st, self.cap
        W, S = 1000, st.figureStem
        x0 = 0.24 * W
        hook = self.hook_stem(x0, S, C, 0, 0.42 * C * 0.75, 0.47 * C * 0.75, 240, 220, 0.94 * W, st.figureTop, self.of)
        hook = hook.mirrored_y(C / 2).oriented(True)
        tb = st.figureTop + 4
        cs = [hook, rect(0.02 * W, 0.42 * C, 0.7 * W, 0.42 * C + tb - 14), rect(0, 0, W, tb)]
        adv = self.wd.tabularAdvance
        return self._g("sterling", 0xA3, adv, cs, "f-like hooked stem + crossbar + base bar, tabular", (adv - W) / 2)

    def yen(self):
        st, C = self.st, self.cap
        W, t, S = 1060, st.diagonalUpper - 6, st.figureStem
        xm, yj = W / 2, 0.48 * C
        a = hcut_centre((xm, yj), 0, C, t, -1)
        hw = a[0]
        dvec = (xm - a[0], yj - C)
        outer_l = ((0, C), (dvec[0], C + dvec[1]))
        inner_l = ((2 * hw, C), (2 * hw + dvec[0], C + dvec[1]))
        crotch = intersect_lines(*inner_l, (xm, 0), (xm, C))
        y_m = intersect_lines(*outer_l, (xm - S / 2, 0), (xm - S / 2, C))[1]
        pts = [(0, C), (2 * hw, C), crotch, (W - 2 * hw, C), (W, C), (xm + S / 2, y_m), (xm + S / 2, 0), (xm - S / 2, 0), (xm - S / 2, y_m)]
        tb = st.punctStroke - 10
        cs = [polygon(pts).oriented(True), rect(0.16 * W, 0.40 * C - tb, 0.84 * W, 0.40 * C), rect(0.16 * W, 0.20 * C - tb, 0.84 * W, 0.20 * C)]
        adv = self.wd.tabularAdvance
        return self._g("yen", 0xA5, adv, cs, "Y on figure stem + two bars, tabular", (adv - W) / 2)

    def Euro(self):
        st, C = self.st, self.cap
        W = 1000
        rx, ry, cy = (W - 110) / 2, C / 2 + self.oc, C / 2
        cxr = 110 + rx
        ring = self.cut_ring(cxr, cy, rx, ry, st.figureSide, st.figureTop, cy + self.sh.CTerminalUpper * ry, cy - self.sh.CTerminalLower * ry)
        tb = st.punctStroke - 14
        cs = [ring, rect(0, 0.56 * C, 0.66 * W, 0.56 * C + tb), rect(0, 0.38 * C, 0.62 * W, 0.38 * C + tb)]
        adv = self.wd.tabularAdvance
        return self._g("Euro", 0x20AC, adv, cs, "C on figure strokes + two bars, tabular", (adv - W) / 2)

    def dong(self):
        st = self.st
        from .marks import dcroat

        d = dcroat(self, self.d())
        scale = 0.8
        lift = 0.18 * self.cap
        cs, w = self._scaled(d, scale, 0.92, 0, lift, ref_stem=st.stemLower)
        tb = st.barLower - 14
        cs.append(rect(0, 0, w, tb))
        adv = self.wd.tabularAdvance
        return self._g("dong", 0x20AB, adv, cs, "đ x0.8 (stroke x0.92) on a bar, tabular", (adv - w) / 2)

    # ------------------------------------------------------------------ math
    def plus(self):
        t, L, ym = self.st.punctStroke, 880, self._ym
        return self._math("plus", 0x2B, [rect(-L / 2, ym - t / 2, L / 2, ym + t / 2), rect(-t / 2, ym - L / 2, t / 2, ym + L / 2)], "bars on the math axis")

    def minus(self):
        t, L, ym = self.st.punctStroke, 880, self._ym
        return self._math("minus", 0x2212, [rect(-L / 2, ym - t / 2, L / 2, ym + t / 2)], "plus bar")

    def equal(self):
        t, L, ym = self.st.punctStroke, 880, self._ym
        return self._math("equal", 0x3D, [rect(-L / 2, ym + 90, L / 2, ym + 90 + t), rect(-L / 2, ym - 90 - t, L / 2, ym - 90)], "two plus bars")

    def less(self):
        t, ym = self.st.punctStroke, self._ym
        w, h = 800, 760
        hw = t / 2 / math.sin(math.atan2(h / 2, w))
        cs = self._chevron(-w / 2 + hw, ym, w - hw, h, t, True)
        return self._math("less", 0x3C, cs, "chevron on the math axis")

    def greater(self):
        g = self.less()
        adv = self.wd.tabularAdvance
        return Glyph("greater", [0x3E], adv, [c.mirrored_x(adv / 2).oriented(True) for c in g.contours], note="< mirrored")

    def multiply(self):
        t, a, ym = self.st.punctStroke, 300, self._ym
        return self._math("multiply", 0xD7, [stroke((-a, ym - a), (a, ym + a), t, "p"), stroke((-a, ym + a), (a, ym - a), t, "p")], "plus rotated 45°")

    def divide(self):
        t, L, ym = self.st.punctStroke, 880, self._ym
        d = 0.9 * self._d
        cs = [rect(-L / 2, ym - t / 2, L / 2, ym + t / 2), superellipse(0, ym + 290, d / 2, d / 2, self.ten.circle), superellipse(0, ym - 290, d / 2, d / 2, self.ten.circle)]
        return self._math("divide", 0xF7, cs, "minus + two dots")

    def asciitilde(self):
        t, ym = self.st.punctStroke, self._ym
        amp, w = 190, 800
        pts = [(-w / 2, ym - amp / 2 + 0.22 * amp), (-w * 0.2, ym + amp / 2), (w * 0.2, ym - amp / 2), (w / 2, ym - amp / 2 + 0.78 * amp)]
        top = [(x, y + t / 2) for x, y in pts]
        bot = [(x, y - t / 2) for x, y in pts]
        c = Contour(bot[0])
        c.curve(bot[1], 58, 0, 0.56).curve(bot[2], 0, 0, 0.62).curve(bot[3], 0, 58, 0.56)
        c.line(top[3])
        c.curve(top[2], 238, 180, 0.56).curve(top[1], 180, 180, 0.62).curve(top[0], 180, 238, 0.56)
        return self._math("asciitilde", 0x7E, [c.close().oriented(True)], "tilde mark drawing at math size")

    def asciicircum(self):
        C, t = self.cap, self.st.punctStroke
        w, h, flat = 760, 0.42 * C, 150
        c = apex_polygon(w, h, flat, t).translated(-w / 2, C - h)
        return self._math("asciicircum", 0x5E, [c], "circumflex drawing at symbol size, top on the cap height")

    # --------------------------------------------------------- marks as signs
    def degree(self):
        C = self.cap
        r = 0.18 * C
        t = self.st.hairStroke
        cs = [superellipse(r, C - r, r, r, self.ten.outer), superellipse(r, C - r, r - t, r - t, self.ten.inner).reversed()]
        return self._g("degree", 0xB0, 2 * r + 2 * 90, cs, "small ring at the cap height", 90)

    def _circled(self, inner_cs, name, uni, note):
        C, t = self.cap, self.st.hairStroke - 8
        W = 1540
        ring = [superellipse(W / 2, C / 2, W / 2, C / 2 + self.oc, self.ten.outer),
                superellipse(W / 2, C / 2, W / 2 - t, C / 2 + self.oc - t, self.ten.outer).reversed()]
        return self._g(name, uni, W + 2 * 70, ring + inner_cs, note, 70)

    def copyright(self):
        st, C = self.st, self.cap
        W = 1540
        # The small c thickens at 0.6 the stem rate and grows with its weight.
        kc = 1 + 0.6 * (self.wk - 1)
        side, top = 150 * kc, 134 * kc
        rx, ry = 0.24 * W + (side - 150) / 2, 0.26 * C + (top - 134) / 2
        cx, cy = W / 2 + 10, C / 2
        c = self.cut_ring(cx, cy, rx, ry, side, top, cy + 0.5 * ry, cy - 0.52 * ry)
        return self._circled([c], "copyright", 0xA9, "hair ring + c at 0.5 size")

    def registered(self):
        R = self.R()
        cs, w = self._scaled(R, 0.42, 0.7, 0, 0)
        b = [c.bounds() for c in cs]
        h = max(x[3] for x in b)
        W, C = 1540, self.cap
        cs = [c.translated(W / 2 - w / 2 + 20, C / 2 - h / 2) for c in cs]
        return self._circled(cs, "registered", 0xAE, "hair ring + R x0.42 (stroke x0.7)")

    def trademark(self):
        C = self.cap
        T, M = self.T(), self.M()
        cs_t, wt = self._scaled(T, 0.42, 0.62, 0, 0)
        cs_m, wm = self._scaled(M, 0.42, 0.62, 0, 0)
        h = 0.42 * C
        dy = C - h - 4
        gap = 60
        cs = [c.translated(80, dy) for c in cs_t] + [c.translated(80 + wt + gap, dy) for c in cs_m]
        return self._g("trademark", 0x2122, 80 + wt + gap + wm + 80, cs, "T and M x0.42 (stroke x0.62), top on the cap height")


PUNCT = [
    "colon", "semicolon", "exclam", "exclamdown", "question", "questiondown", "periodcentered", "bullet", "ellipsis",
    "quoteright", "quoteleft", "quotesinglbase", "quotedblright", "quotedblleft", "quotedblbase", "quotesingle", "quotedbl",
    "guilsinglleft", "guilsinglright", "guillemotleft", "guillemotright", "endash", "emdash", "underscore",
    "slash", "backslash", "bar", "parenleft", "parenright", "bracketleft", "bracketright", "braceleft", "braceright",
    "asterisk", "numbersign", "percent", "ampersand", "at", "section", "paragraph",
    "dollar", "cent", "sterling", "yen", "Euro", "dong",
    "plus", "minus", "equal", "less", "greater", "multiply", "divide", "asciitilde", "asciicircum",
    "degree", "copyright", "registered", "trademark",
]

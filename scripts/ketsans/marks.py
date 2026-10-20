"""Vietnamese mark system for KÉT Sans.

Marks are drawn with the same stroke (``markStroke``), the same grid-cut
terminals and the same tension as the letters.  Lowercase marks sit
``lowerGap`` above the x-height; ``.case`` marks are flatter and sit
``upperGap`` above the cap height so stacked capitals stay inside ~1 em.

Stacking follows Vietnamese convention: after a circumflex the acute, grave
and hook sit on its upper right; the tilde and everything after a breve stack
vertically.  Pairs are pre-built (``circumflexcomb_acutecomb`` …) and used
both by precomposed letters and by ``ccmp`` for decomposed input, so NFC and
NFD text render identically.
"""

from __future__ import annotations

import math
import unicodedata

from fontTools.agl import UV2AGL

from .geometry import Contour, polygon, rect, superellipse
from .glyphs import Builder, Glyph

TOP_MARKS = {
    0x0300: "gravecomb",
    0x0301: "acutecomb",
    0x0302: "circumflexcomb",
    0x0303: "tildecomb",
    0x0304: "macroncomb",
    0x0306: "brevecomb",
    0x0307: "dotaccentcomb",
    0x0308: "dieresiscomb",
    0x0309: "hookabovecomb",
    0x030A: "ringcomb",
    0x030B: "hungarumlautcomb",
    0x030C: "caroncomb",
}
BOTTOM_MARKS = {0x0323: "dotbelowcomb", 0x0326: "commaaccentcomb", 0x0327: "cedillacomb"}
OGONEK = 0x0328
HORN = 0x031B

# Spacing (modifier) forms of the marks.
SPACING = {
    0x0060: "gravecomb", 0x00B4: "acutecomb", 0x00A8: "dieresiscomb", 0x00AF: "macroncomb",
    0x00B8: "cedillacomb", 0x02C6: "circumflexcomb", 0x02C7: "caroncomb", 0x02D8: "brevecomb",
    0x02D9: "dotaccentcomb", 0x02DA: "ringcomb", 0x02DB: "ogonekcomb", 0x02DC: "tildecomb",
    0x02DD: "hungarumlautcomb",
}
CEDILLA_AS_COMMA = set("GKLNkln")  # Latvian: drawn with a comma below
CARON_ALT = set("dltL")  # vertical caron beside the ascender
HORN_BASES = {"o": "ohorn", "u": "uhorn", "O": "Ohorn", "U": "Uhorn"}
ATTACHED = {"cedillacomb", "ogonekcomb"}  # marks that join the letter

SECOND = ["acutecomb", "gravecomb", "hookabovecomb", "tildecomb"]
FIRST = ["circumflexcomb", "brevecomb"]


class MarkMaker:
    def __init__(self, b: Builder):
        self.b = b
        st = b.st
        self.t = st.markStroke
        self.X = b.xh
        self.C = b.cap
        self.gap = {"": 152, ".case": 96}
        # Mark heights, lowercase / case.
        self.h = {
            "acute": {"": 326, ".case": 250},
            "circ": {"": 300, ".case": 214},
            "breve": {"": 290, ".case": 204},
            "tilde": {"": 124, ".case": 80},
            "hook": {"": 336, ".case": 250},
        }
        self.w = {
            "circ": {"": 650, ".case": 650},
            "breve": {"": 630, ".case": 640},
            "tilde": {"": 620, ".case": 660},
        }
        self.stack_gap = {"": 58, ".case": 36}
        # Heavier masters: widths open up by ``markWidth`` (circumflex, breve,
        # tilde, hook, macron, double acute); marks drawn with fixed radii grow
        # by ``gk`` so their counters keep the Regular opening.  All 1 at Regular.
        self.mw = b.sh.markWidth
        self.mk = b.mk
        self.gk = 1 + 0.7 * (b.mk - 1)
        # Capital marks open up half as much: they sit in a flatter budget.
        for key in self.w:
            self.w[key] = {s: v * (self.mw if s == "" else 1 + 0.5 * (self.mw - 1)) for s, v in self.w[key].items()}
        # Capital stacks (Ỗ) stay within one em: as the pen grows, the case
        # gap and the case tilde (amplitude and pen) give back the added height.
        self.dt = dt = self.t - b.reg.markStroke
        self.gap[".case"] -= 0.16 * dt
        self.h["tilde"][".case"] -= 0.55 * dt

    # ----------------------------------------------------------- base mark set
    def _place(self, name, contours, suffix, height, uni=None, gap=None):
        base_y = (self.X if suffix == "" else self.C)
        gap = self.gap[suffix] if gap is None else gap
        y0 = base_y + gap
        cs = [c.translated(0, y0) for c in contours]
        g = Glyph(name + suffix, [uni] if (uni and suffix == "") else [], 0, cs)
        g.anchors = {"_top": (0, base_y), "top": (0, y0 + height + self.gap[suffix] - 10)}
        g.note = "Vietnamese mark, markStroke pen"
        return g

    def acute(self, suffix="", grave=False):
        h = self.h["acute"][suffix]
        ang = math.radians(58 if suffix == "" else 52)
        dx = h / math.tan(ang)
        # Nearly even stroke (SF-like); a strong taper reads as a brush stroke.
        w_top = (self.t + 4) / math.sin(ang)
        w_bot = (self.t - 14) / math.sin(ang)
        shift = -(w_top - w_bot) / 4  # centre the tapered stroke by its box
        pts = [(-dx / 2 - w_bot / 2 + shift, 0), (-dx / 2 + w_bot / 2 + shift, 0), (dx / 2 + w_top / 2 + shift, h), (dx / 2 - w_top / 2 + shift, h)]
        if grave:
            pts = [(-x, y) for x, y in pts]
        c = polygon(pts).oriented(True)
        name = "gravecomb" if grave else "acutecomb"
        return self._place(name, [c], suffix, h, 0x0300 if grave else 0x0301)

    def grave(self, suffix=""):
        return self.acute(suffix, grave=True)

    def circumflex(self, suffix=""):
        h, w, t = self.h["circ"][suffix], self.w["circ"][suffix], self.t - 6
        flat = 110 * self.mk
        lo = ((-w / 2, 0), (-flat / 2, h))
        ro = ((w / 2, 0), (flat / 2, h))
        # Legs of perpendicular width t, flat apex, horizontal feet.
        from .geometry import intersect_lines, offset_line, x_at_y

        li = offset_line(*lo, -t)
        ri = offset_line(*ro, t)
        apex_in = intersect_lines(*li, *ri)
        pts = [lo[0], (x_at_y(*li, 0), 0), apex_in, (x_at_y(*ri, 0), 0), ro[0], ro[1], lo[1]]
        c = polygon(pts).oriented(True)
        return self._place("circumflexcomb", [c], suffix, h, 0x0302)

    def breve(self, suffix=""):
        h, w = self.h["breve"][suffix], self.w["breve"][suffix]
        t_side, t_bot = self.t - 10, self.t - 4
        k = self.b.ten
        rx = w / 2
        # Lower half of a ring, ends cut horizontally at the top.
        c = Contour((-rx, h))
        c.curve((0, 0), 270, 0, k.outer)
        c.curve((rx, h), 0, 90, k.outer)
        c.line((rx - t_side, h))
        c.curve((0, t_bot), 270, 180, k.inner)
        c.curve((-rx + t_side, h), 180, 90, k.inner)
        return self._place("brevecomb", [c.close().oriented(True)], suffix, h, 0x0306)

    def tilde(self, suffix=""):
        amp, w, t = self.h["tilde"][suffix], self.w["tilde"][suffix], self.t - 6 - (0.3 * self.dt if suffix else 0)
        # Centre line: low left end -> crest -> trough -> high right end;
        # the stroke is offset vertically so the slopes thin naturally and
        # both ends are cut vertically.
        a = 0.56
        pts = [(-w / 2, 0.22 * amp), (-w * 0.2, amp), (w * 0.2, 0), (w / 2, 0.78 * amp)]
        top = [(x, y + t / 2) for x, y in pts]
        bot = [(x, y - t / 2) for x, y in pts]
        c = Contour(bot[0])
        c.curve(bot[1], 58, 0, a).curve(bot[2], 0, 0, 0.62).curve(bot[3], 0, 58, a)
        c.line(top[3])
        c.curve(top[2], 238, 180, a).curve(top[1], 180, 180, 0.62).curve(top[0], 180, 238, a)
        g = self._place("tildecomb", [c.close().oriented(True)], suffix, amp + t)
        # Shift up by half the stroke so the mark's bottom sits on the gap.
        g.contours = [cc.translated(0, t / 2) for cc in g.contours]
        g.unicodes = [0x0303] if suffix == "" else []
        return g

    def hook(self, suffix=""):
        """Dấu hỏi: an open bowl over a short centred tail (a dotless '?')."""
        h = self.h["hook"][suffix]
        k = self.b.ten
        sx, sy = (1.0, 1.0) if suffix == "" else (0.9, 0.8)
        sc = sy
        # The hook's pen grows half as fast as the other marks; its bowl and
        # height grow by the same amount so the counter keeps its opening.
        t0 = self.t / self.mk - 26
        grow = t0 * 0.5 * (self.mk - 1)
        if suffix == "":
            h = h + grow
        else:
            grow *= 0.5  # the capital hook keeps its height (stack budget) and a lighter pen
        t = (t0 + grow) * (1.0 if suffix == "" else 0.92)
        rx, ry = 184 * sx * self.mw, (142 + grow) * sy
        yc = h - ry
        tail_w = t
        y_tail = 44 * sc  # where the bowl hands over to the vertical tail
        face = t + 26
        c = Contour((-rx, yc + 6))
        c.curve((0, h), 84, 0, k.terminal, k.outer)
        c.curve((rx, yc), 0, 270, k.outer)
        c.cubic((rx, yc - ry * 0.6), (tail_w / 2, y_tail + ry * 0.5), (tail_w / 2, y_tail))
        c.line((tail_w / 2, 0)).line((-tail_w / 2, 0)).line((-tail_w / 2, y_tail + 4))
        c.cubic((-tail_w / 2, y_tail + ry * 0.62), (rx - t, yc - (ry - t) * 0.9), (rx - t, yc))
        c.curve((0, h - t + 6), 90, 180, k.inner)
        c.curve((-rx + face, yc + 6), 180, 264, k.inner, k.terminal)
        return self._place("hookabovecomb", [c.close().oriented(True)], suffix, h, 0x0309)

    def dotbelow(self):
        d = self.b.sh.dotDiameter * self.b.st.stemLower
        c = superellipse(0, -126 - d / 2, d / 2, d / 2, self.b.ten.circle)
        g = Glyph("dotbelowcomb", [0x0323], 0, [c], note="i-dot family, below baseline")
        g.anchors = {"_bottom": (0, 0), "bottom": (0, -126 - d - 60)}
        return g

    def horn(self, suffix=""):
        """Horn drawn from its anchor (0, 0), a point on the base's outer edge
        at ``hornRoot``.  A level shelf leaves the shoulder and turns, round a
        small inner corner, into an upright stub of near-mark weight that ends
        in a horizontal cut well above the x-height (cap height for .case).
        The underside rises from the shoulder at 6° and turns upright; both
        roots stay buried in the base stroke."""
        k = self.b.ten
        lower = suffix == ""
        t = self.t + (4 if lower else 10)
        h = 0.34 * self.X if lower else 0.24 * self.C
        reach = (190 if lower else 200) + (t - (self.t / self.mk + (4 if lower else 10)))
        shelf, r = (120, 40) if lower else (115, 40)
        x_in = reach - t
        c = Contour((-90, -48))
        c.curve((reach, 0.55 * h), 6, 90, k.outer)
        c.line((reach, h)).line((x_in, h)).line((x_in, shelf + r))
        c.curve((x_in - r, shelf), 270, 180, k.circle)
        c.curve((-70, 60), 180, 205, k.inner)
        g = Glyph("horncomb" + suffix, [0x031B] if lower else [], 0, [c.close().oriented(True)], note="horn: level shelf turning into an upright stub, tip cut horizontally")
        g.anchors = {"_horn": (0, 0)}
        return g

    # ------------------------------------------------------- Latin marks
    def macron(self, suffix=""):
        w = {"": 520, ".case": 600}[suffix] * self.mw
        t = self.t - (22 if suffix == "" else 28)
        return self._place("macroncomb", [rect(-w / 2, 0, w / 2, t)], suffix, t, 0x0304)

    def _dot_d(self, suffix):
        return self.b.st.stemLower * (self.b.sh.markDot if suffix == "" else self.b.sh.markDotCase)

    def dotaccent(self, suffix=""):
        d = self._dot_d(suffix)
        c = superellipse(0, d / 2, d / 2, d / 2, self.b.ten.circle)
        return self._place("dotaccentcomb", [c], suffix, d, 0x0307)

    def dieresis(self, suffix=""):
        d = self._dot_d(suffix)
        # Keep the Regular white between the dots, opened by markWidth.
        sep0 = {"": 318, ".case": 344}[suffix]
        d0 = self.b.reg.stemLower * {"": 1.06, ".case": 1.0}[suffix]
        sep = d + (sep0 - d0) * self.mw
        cs = [superellipse(x, d / 2, d / 2, d / 2, self.b.ten.circle) for x in (-sep / 2, sep / 2)]
        return self._place("dieresiscomb", cs, suffix, d, 0x0308)

    def ring(self, suffix=""):
        r = {"": 154, ".case": 142}[suffix] * self.gk
        t = {"": 104, ".case": 98}[suffix] * self.mk
        k = self.b.ten
        cs = [superellipse(0, r, r, r, k.outer), superellipse(0, r, r - t, r - t, k.inner).reversed()]
        return self._place("ringcomb", cs, suffix, 2 * r, 0x030A, gap={"": 110, ".case": 72}[suffix])

    def hungarumlaut(self, suffix=""):
        h = self.h["acute"][suffix] - 10
        ang = math.radians(62 if suffix == "" else 56)
        dx = h / math.tan(ang)
        w_top = (self.t - 4) / math.sin(ang)
        # Keep the Regular gap between the strokes (scaled with the mark
        # width) instead of the Regular spacing, so heavier strokes don't merge.
        w_top0 = (self.t - self.dt - 4) / math.sin(ang)
        sep = w_top + ({"": 200, ".case": 230}[suffix] - w_top0) * self.mw
        w_bot = (self.t - 54) / math.sin(ang)
        sh = -(w_top - w_bot) / 4
        one = polygon([(-dx / 2 - w_bot / 2 + sh, 0), (-dx / 2 + w_bot / 2 + sh, 0), (dx / 2 + w_top / 2 + sh, h), (dx / 2 - w_top / 2 + sh, h)]).oriented(True)
        return self._place("hungarumlautcomb", [one.translated(-sep / 2, 0), one.translated(sep / 2, 0)], suffix, h, 0x030B)

    def caron(self, suffix=""):
        g = self.circumflex(suffix)
        h = self.h["circ"][suffix]
        y0 = (self.X if suffix == "" else self.C) + self.gap[suffix]
        g.contours = [c.mirrored_y(y0 + h / 2).oriented(True) for c in g.contours]
        g.name = "caroncomb" + suffix
        g.unicodes = [0x030C] if suffix == "" else []
        return g

    def _comma_mark(self, scale=0.72):
        """The comma drawing scaled for marks, head centre at the origin."""
        b = self.b
        r = b.sh.dotDiameter * b.st.stemLower / 2
        return [c.translated(-(120 + r), -(r - 2)).scaled(scale) for c in b.comma().contours]

    def commaaccent(self):
        cs = self._comma_mark()
        top = max(c.bounds()[3] for c in cs)
        cs = [c.translated(0, -126 - top) for c in cs]  # top on the dot-below line
        low = min(c.bounds()[1] for c in cs)
        g = Glyph("commaaccentcomb", [0x0326], 0, cs, note="comma x0.72 below the baseline (ș ț ķ ļ ņ)")
        g.anchors = {"_bottom": (0, 0), "bottom": (0, low - 60)}
        return g

    def commaturnedabove(self):
        cs = [c.rotated180(0, 0) for c in self._comma_mark()]
        low = min(c.bounds()[1] for c in cs)
        hgt = max(c.bounds()[3] for c in cs) - low
        g = self._place("commaturnedabovecomb", [c.translated(0, -low) for c in cs], "", hgt)
        g.note = "comma x0.72 turned, above (ģ)"
        return g

    def caron_alt(self):
        # Same height as at Regular: the heavier comma is drawn smaller.
        b = self.b
        d, d0 = b.sh.dotDiameter * b.st.stemLower, b.sys.raw["shapes"]["dotDiameter"] * b.reg.stemLower
        cs = self._comma_mark(0.70 * (d0 + 330) / (d + 330))
        bb = [c.bounds() for c in cs]
        x0, y1 = min(x[0] for x in bb), max(x[3] for x in bb)
        g = Glyph("caroncomb.alt", [], 0, [c.translated(-x0, -y1) for c in cs], note="vertical caron: comma x0.70 beside the stem (ď ľ ť Ľ)")
        g.anchors = {"_topright": (0, 0)}
        return g

    def cedilla(self):
        k, g, m = self.b.ten, self.gk, self.mk
        t, tb, ts = 104 * m, 90 * m, 100 * m
        stub = rect(-t / 2, -128 * g, t / 2, 40)
        c = Contour((-10, -96 * g)).line((10, -96 * g))
        c.curve((128 * g, -200 * g), 0, 270, k.outer)
        c.curve((0, -304 * g), 270, 180, k.outer)
        c.curve((-128 * g, -284 * g), 180, 166, k.outer, 0.6)
        c.line((-128 * g, -284 * g + 84 * m))
        c.curve((0, -304 * g + tb), 346, 0, 0.6, k.inner)
        c.curve((128 * g - ts, -200 * g), 0, 90, k.inner)
        c.curve((10, -96 * g - tb), 90, 180, k.inner)
        c.line((-10, -96 * g - tb))
        g = Glyph("cedillacomb", [0x0327], 0, [stub, c.close().oriented(True)], note="stub + open bowl, terminal cut vertically")
        g.anchors = {"_bottom": (0, 0), "bottom": (0, -360)}
        return g

    def ogonek(self):
        k, g, m = self.b.ten, self.gk, self.mk
        h, rx, ts, tb = 330 * g, 150 * g, 126 * m, 102 * m
        c = Contour((-46 * g, 40))
        c.curve((-rx, -0.55 * h), 240, 270, k.outer)
        c.curve((40 * g, -h), 270, 0, k.outer)
        c.curve((170 * g, -h + 24 * g), 0, 18, 0.55)
        c.line((170 * g, -h + 24 * g + 78 * m))
        c.curve((40 * g, -h + tb), 198, 180, 0.55)
        c.curve((-rx + ts, -0.55 * h), 180, 90, k.inner)
        c.curve((-46 * g + ts + 14, 40), 90, 60, k.inner)
        g = Glyph("ogonekcomb", [0x0328], 0, [c.close().oriented(True)], note="hook below, curling right to a vertical cut")
        g.anchors = {"_ogonek": (0, 0)}
        return g

    # ---------------------------------------------------------- stacked pairs
    def pair(self, first: Glyph, second: Glyph, suffix: str) -> Glyph:
        """Pre-built Vietnamese stack as a composite of two marks.

        After a circumflex, acute/grave/hook sit on its upper right; the
        position is solved so the two marks keep ``pairClearance`` apart.
        Tilde and everything after a breve stack vertically."""
        fname = first.name[: -len(suffix)] if suffix else first.name
        sname = second.name[: -len(suffix)] if suffix else second.name
        g = Glyph(f"{fname}_{sname}{suffix}", [], 0)
        fb = _bounds(first)
        sb = _bounds(second)
        clearance = 44 if suffix == "" else 36
        if fname == "circumflexcomb" and sname != "tildecomb":
            # Second mark's bottom at 92 % (case 60 %) of the circumflex height, then slid
            # left until it is exactly ``clearance`` from the circumflex.
            dy = fb[1] + (fb[3] - fb[1]) * (0.92 if suffix == "" else 0.6) - sb[1]
            dx = fb[2] - sb[0] + 200
            while dx > -400 and _min_distance(first.contours, [c.translated(dx - 4, dy) for c in second.contours]) >= clearance:
                dx -= 4
        else:
            dx = 0
            dy = fb[3] + self.stack_gap[suffix] - sb[1]
        g.components = [(first.name, 0, 0), (second.name, dx, dy)]
        top = max(fb[3], sb[3] + dy)
        base_y = self.X if suffix == "" else self.C
        g.anchors = {"_top": (0, base_y), "top": (0, top + self.gap[suffix])}
        g.note = "Vietnamese stacked pair"
        g._bounds = (min(fb[0], sb[0] + dx), fb[1], max(fb[2], sb[2] + dx), top)
        g._contours = list(first.contours) + [c.translated(dx, dy) for c in second.contours]
        return g

    def build(self) -> dict[str, Glyph]:
        out: dict[str, Glyph] = {}
        for suffix in ["", ".case"]:
            for fn in [self.acute, self.grave, self.circumflex, self.breve, self.tilde, self.hook,
                       self.macron, self.dotaccent, self.dieresis, self.ring, self.hungarumlaut, self.caron]:
                g = fn(suffix)
                out[g.name] = g
        for fn in [self.commaaccent, self.commaturnedabove, self.caron_alt, self.cedilla, self.ogonek]:
            g = fn()
            out[g.name] = g
        out["dotbelowcomb"] = self.dotbelow()
        out["horncomb"] = self.horn()
        out["horncomb.case"] = self.horn(".case")
        for suffix in ["", ".case"]:
            for f in FIRST:
                for s in SECOND:
                    g = self.pair(out[f + suffix], out[s + suffix], suffix)
                    out[g.name] = g
        return out


def _points(contours, steps=24):
    from .geometry import flatten

    pts = []
    for c in contours:
        for seg in c.beziers():
            if len(seg) == 2:
                n = max(2, int(((seg[1][0] - seg[0][0]) ** 2 + (seg[1][1] - seg[0][1]) ** 2) ** 0.5 / 12))
                pts += [(seg[0][0] + (seg[1][0] - seg[0][0]) * i / n, seg[0][1] + (seg[1][1] - seg[0][1]) * i / n) for i in range(n + 1)]
            else:
                pts += flatten(seg, steps)
    return pts


def _min_distance(a, b) -> float:
    """Smallest distance between two outlines (0 if they overlap)."""
    import pathops

    pa, pb = _to_path(a), _to_path(b)
    inter = pathops.op(pa, pb, pathops.PathOp.INTERSECTION)
    if inter.area > 1:
        return 0.0
    import numpy as np

    A = np.array(_points(a))
    B = np.array(_points(b))
    d = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1))
    return float(d.min())


def _to_path(contours):
    import pathops

    path = pathops.Path()
    pen = path.getPen()
    for c in contours:
        c.draw(pen, round_to=0)
    return path


def _bounds(g: Glyph):
    if getattr(g, "_bounds", None):
        return g._bounds
    bs = [c.bounds() for c in g.contours]
    return min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)


# ------------------------------------------------------------------ letters
VIET_BASES = set("aeiouyAEIOUY")


def glyph_name(cp: int) -> str:
    return UV2AGL.get(cp) or f"uni{cp:04X}"


def vietnamese_targets(bases=VIET_BASES):
    """Every Vietnamese precomposed letter whose base is in ``bases``."""
    vowels = "aăâeêioôơuưyAĂÂEÊIOÔƠUƯY"
    tones = ["", "̀", "́", "̉", "̃", "̣"]
    out = []
    for v in vowels:
        for tone in tones:
            ch = unicodedata.normalize("NFC", v + tone)
            if len(ch) != 1:
                continue
            nfd = unicodedata.normalize("NFD", ch)
            if nfd[0] in bases and ch != nfd[0]:
                out.append(ch)
    return out


def horn_base(b: Builder, base: Glyph, marks: dict, name: str, uni: int, suffix: str) -> Glyph:
    """o + horn as real contours (overlaps removed at build)."""
    horn = marks["horncomb" + suffix]
    ax, ay = base.anchors["horn"]
    cs = list(base.contours) + [c.translated(ax, ay) for c in horn.contours]
    hb = [c.translated(ax, ay).bounds() for c in horn.contours][0]
    rsb = 40
    width = max(base.width, hb[2] + rsb)
    g = Glyph(name, [uni], width, cs, note=f"{base.name} + horn")
    g.anchors = {k: v for k, v in base.anchors.items() if k != "horn"}
    return g


def dcroat(b: Builder, d: Glyph) -> Glyph:
    st = b.st
    stem_r = d.width - b.sp.lowerStraight
    stem_l = stem_r - st.stemLower
    yc = (b.xh + b.asc) / 2 + 30
    bar = rect(stem_l - 150, yc - st.barLower / 2, stem_r + 70, yc + st.barLower / 2)
    g = Glyph("dcroat", [0x0111], d.width + 40, list(d.contours) + [bar], note="d + bar at ascender midpoint")
    g.anchors = dict(d.anchors)
    return g


def charset() -> list[int]:
    from .system import ROOT

    path = ROOT / "charset.txt"
    return [int(line.split()[0][2:], 16) for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("U+")]


def compose(cp: int, glyphs: dict[str, Glyph], cmap: dict[int, str]) -> Glyph:
    """A precomposed letter as base + marks placed on anchors."""
    nfd = unicodedata.normalize("NFD", chr(cp))
    base_ch, rest = nfd[0], [ord(c) for c in nfd[1:]]
    suffix = ".case" if base_ch.isupper() else ""
    if HORN in rest:
        base_name = HORN_BASES[base_ch]
        rest = [c for c in rest if c != HORN]
    else:
        base_name = cmap[ord(base_ch)]
    tops = [c for c in rest if c in TOP_MARKS]
    if tops and base_ch in "ij":
        base_name = {"i": "dotlessi", "j": "dotlessj"}[base_ch]
    base = glyphs[base_name]
    comps = [(base_name, 0, 0)]
    width = base.width

    def attach(mark_name, anchor):
        m = glyphs[mark_name]
        bx, by = base.anchors[anchor]
        mx, my = m.anchors["_" + anchor]
        comps.append((mark_name, bx - mx, by - my))
        return m, bx - mx

    if tops == [0x030C] and base_ch in CARON_ALT:
        m, dx = attach("caroncomb.alt", "topright")
        width = max(width, max(c.bounds()[2] for c in m.contours) + dx + 60)
    elif tops:
        names = [TOP_MARKS[c] for c in tops]
        attach("_".join(names) + suffix if len(names) > 1 else names[0] + suffix, "top")
    for c in rest:
        if c == 0x0327 and base_ch in CEDILLA_AS_COMMA:
            attach("commaaccentcomb", "bottom")
        elif c == 0x0327 and base_ch == "g":
            attach("commaturnedabovecomb", "top")
        elif c in BOTTOM_MARKS:
            attach(BOTTOM_MARKS[c], "bottom")
        elif c == OGONEK:
            attach("ogonekcomb", "ogonek")
    g = Glyph(glyph_name(cp), [cp], width, components=comps, note="precomposed (anchor-placed)")
    if any(name in ATTACHED for name, _, _ in comps[1:]):
        # Marks that grow out of the letter overlap it on purpose; keep them
        # as contours so the build merges the overlap (TTF composites cannot).
        g.contours = [c.translated(dx, dy) for name, dx, dy in comps for c in glyphs[name].contours]
        g.components = []
        g.note = "precomposed, attached mark merged into the outline"
    g.anchors = {}
    return g


def spacing_accent(cp: int, mark: Glyph) -> Glyph:
    bb = [c.bounds() for c in mark.contours]
    x0, x1 = min(b[0] for b in bb), max(b[2] for b in bb)
    sb = 90
    width = x1 - x0 + 2 * sb
    g = Glyph(glyph_name(cp), [cp], width, components=[(mark.name, sb - x0, 0)], note=f"spacing {mark.name}")
    g.anchors = {}
    return g


def build_marks_and_letters(b: Builder, glyphs: dict[str, Glyph]) -> dict[str, Glyph]:
    """Marks, horn bases, đ, and every precomposed letter / spacing accent of
    the target character set that is not drawn as contours."""
    mm = MarkMaker(b)
    marks = mm.build()
    out: dict[str, Glyph] = dict(marks)
    out["ohorn"] = horn_base(b, glyphs["o"], marks, "ohorn", 0x01A1, "")
    out["uhorn"] = horn_base(b, glyphs["u"], marks, "uhorn", 0x01B0, "")
    out["Ohorn"] = horn_base(b, glyphs["O"], marks, "Ohorn", 0x01A0, ".case")
    out["Uhorn"] = horn_base(b, glyphs["U"], marks, "Uhorn", 0x01AF, ".case")
    out["dcroat"] = dcroat(b, glyphs["d"])
    del out["horncomb.case"]  # construction only: the capitals carry their horn as contours
    allg = dict(glyphs)
    allg.update(out)
    eth = Glyph("Eth", [0xD0], allg["Dcroat"].width, components=[("Dcroat", 0, 0)], note="= Đ")
    out["Eth"] = allg["Eth"] = eth
    cmap = {u: n for n, g in allg.items() for u in g.unicodes}
    for cp in charset():
        if cp in cmap:
            continue
        if cp in SPACING:
            g = spacing_accent(cp, allg[SPACING[cp]])
        elif len(unicodedata.normalize("NFD", chr(cp))) > 1:
            g = compose(cp, allg, cmap)
        else:
            continue
        out[g.name] = allg[g.name] = g
        cmap[cp] = g.name
    return out


def features(glyphs: dict[str, Glyph]) -> str:
    """ccmp for decomposed input: i/j lose their dot before top marks, case
    marks after capitals, vertical caron and Latvian commas in context,
    Vietnamese stacked pairs, and base+horn ligatures."""
    lc_marks = [n for n in TOP_MARKS.values()]
    case_marks = [n + ".case" for n in lc_marks]
    uppers = sorted(n for n, g in glyphs.items() if g.unicodes and chr(g.unicodes[0]).isupper())
    pairs = []
    for suffix in ["", ".case"]:
        for f in FIRST:
            for s in SECOND:
                pairs.append(f"    sub {f}{suffix} {s}{suffix} by {f}_{s}{suffix};")
    lines = [
        "languagesystem DFLT dflt;",
        "languagesystem latn dflt;",
        "languagesystem latn VIT;",
        "",
        f"@TopMarks = [{' '.join(lc_marks)}];",
        f"@TopMarksCase = [{' '.join(case_marks)}];",
        f"@Uppercase = [{' '.join(uppers)}];",
        "",
        "lookup CaseMarks {",
        "    sub @TopMarks by @TopMarksCase;",
        "} CaseMarks;",
        "",
        "feature ccmp {",
        "    lookup DotlessIJ {",
        "        sub [i j]' @TopMarks by [dotlessi dotlessj];",
        "    } DotlessIJ;",
        "    lookup HornBase {",
        "        sub o horncomb by ohorn;",
        "        sub u horncomb by uhorn;",
        "        sub O horncomb by Ohorn;",
        "        sub U horncomb by Uhorn;",
        "    } HornBase;",
        "    lookup CaronAlt {",
        f"        sub [{' '.join(sorted(CARON_ALT))}] caroncomb' by caroncomb.alt;",
        "    } CaronAlt;",
        "    lookup CedillaComma {",
        f"        sub [{' '.join(sorted(CEDILLA_AS_COMMA))}] cedillacomb' by commaaccentcomb;",
        "        sub g cedillacomb' by commaturnedabovecomb;",
        "    } CedillaComma;",
        "    lookup CaseContext {",
        "        sub @Uppercase @TopMarks' lookup CaseMarks;",
        "        sub @Uppercase @TopMarksCase @TopMarks' lookup CaseMarks;",
        "        sub @Uppercase dotbelowcomb @TopMarks' lookup CaseMarks;",
        "    } CaseContext;",
        "    lookup VietnamesePairs {",
        *pairs,
        "    } VietnamesePairs;",
        "} ccmp;",
        "",
    ]
    return "\n".join(lines)

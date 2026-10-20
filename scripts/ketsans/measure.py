"""Stroke measurement by ray casting on compiled outlines.

Used for KÉT Sans QA (stem/bar consistency) and to calibrate overall colour
against reference fonts; only numbers are read, never outlines."""

from __future__ import annotations

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

from .proof import _record_to_polys


class Outlines:
    def __init__(self, font: TTFont | str):
        self.font = TTFont(font) if isinstance(font, str) else font
        self.gs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm
        self.xh = self.font["OS/2"].sxHeight
        self.cap = self.font["OS/2"].sCapHeight

    def polys(self, char_or_name):
        name = self.cmap.get(ord(char_or_name), char_or_name) if len(char_or_name) == 1 else char_or_name
        rec = DecomposingRecordingPen(self.gs)
        self.gs[name].draw(rec)
        return _record_to_polys(rec.value, lambda p: p, steps=64)

    def crossings(self, ch, value, axis):
        """Sorted coordinates where the outline crosses x=value (axis=0) or y=value (axis=1)."""
        other = 1 - axis
        out = []
        for poly in self.polys(ch):
            for a, b in zip(poly, poly[1:] + poly[:1]):
                if (a[axis] <= value < b[axis]) or (b[axis] <= value < a[axis]):
                    t = (value - a[axis]) / (b[axis] - a[axis])
                    out.append(a[other] + t * (b[other] - a[other]))
        return sorted(out)

    def runs(self, ch, value, axis):
        c = self.crossings(ch, value, axis)
        return [(c[i], c[i + 1]) for i in range(0, len(c) - 1, 2)]

    def bounds(self, ch):
        pts = [p for poly in self.polys(ch) for p in poly]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)


def color_profile(o: Outlines) -> dict:
    """Key stroke weights in font units, normalised to 2048 UPM."""
    s = 2048 / o.upm
    xh, cap = o.xh, o.cap
    res = {}
    r = o.runs("n", 0.3 * xh, 1)
    res["n stem"] = (r[0][1] - r[0][0]) * s
    b = o.bounds("n")
    r = o.runs("n", (b[0] + b[2]) / 2, 0)
    res["n arch top"] = (r[-1][1] - r[-1][0]) * s
    r = o.runs("o", xh / 2, 1)
    res["o side"] = (r[0][1] - r[0][0]) * s
    b = o.bounds("o")
    r = o.runs("o", (b[0] + b[2]) / 2, 0)
    res["o top"] = (r[-1][1] - r[-1][0]) * s
    r = o.runs("H", 0.25 * cap, 1)
    res["H stem"] = (r[0][1] - r[0][0]) * s
    b = o.bounds("H")
    r = o.runs("H", (b[0] + b[2]) / 2, 0)
    res["H bar"] = (r[0][1] - r[0][0]) * s
    r = o.runs("O", cap / 2, 1)
    res["O side"] = (r[0][1] - r[0][0]) * s
    b = o.bounds("O")
    r = o.runs("O", (b[0] + b[2]) / 2, 0)
    res["O top"] = (r[-1][1] - r[-1][0]) * s
    b = o.bounds("e")
    r = o.runs("e", (b[0] + b[2]) / 2, 0)
    res["e bar"] = (r[1][1] - r[1][0]) * s if len(r) > 2 else float("nan")
    res["x-height"] = xh * s
    res["cap"] = cap * s
    return {k: round(v, 1) for k, v in res.items()}

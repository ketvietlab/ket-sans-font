"""ufo2ft post-filter, run by fontmake after overlap removal.

The pathops union keeps points that carry no shape: an on-curve point between
two collinear line segments (where the top of the Œ bowl runs into the E bar)
and the end of a line that rounds to zero length (¶, where the bowl meets
the stem 0.07 units below the top).  Dropping them leaves every outline as
it compiles and keeps FontBakery's outline checks clean.
"""

from __future__ import annotations

from fontTools.misc.roundTools import otRound
from ufo2ft.filters import BaseFilter

EPS = 1e-6


def _redundant(prev, pt, nxt) -> bool:
    if pt.type != "line" or prev.type is None:
        return False
    if (otRound(prev.x), otRound(prev.y)) == (otRound(pt.x), otRound(pt.y)):
        return True  # a line into pt that the binary rounds to zero length
    if nxt.type != "line":
        return False
    ax, ay = pt.x - prev.x, pt.y - prev.y
    bx, by = nxt.x - pt.x, nxt.y - pt.y
    # collinear and pointing the same way (a point inside a straight run)
    return abs(ax * by - ay * bx) <= EPS * max(1.0, abs(ax) + abs(ay)) * max(1.0, abs(bx) + abs(by)) and ax * bx + ay * by > 0


def clean(contour) -> bool:
    pts = contour.points
    changed = False
    i = 0
    while len(pts) > 3 and i < len(pts):
        n = len(pts)
        if _redundant(pts[i - 1], pts[i], pts[(i + 1) % n]):
            del pts[i]
            changed = True
            i = max(i - 1, 0)
        else:
            i += 1
    return changed


class CleanupFilter(BaseFilter):
    def filter(self, glyph) -> bool:
        return any([clean(c) for c in glyph])

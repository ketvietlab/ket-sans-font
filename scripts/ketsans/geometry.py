"""Vector construction kit for KÉT Sans.

Every glyph is drawn with the same small vocabulary:

* ``Contour`` – a closed path of lines and cubic curves.
* ``Contour.curve`` – a curve described by its two tangent directions and a
  tension.  Handles are placed on the tangent lines at ``tension`` times the
  distance to the point where the tangents cross.  A quarter circle has a
  tension of 0.5523; KÉT Sans uses a slightly firmer value from the design
  system so that bowls, shoulders and terminals share one curvature language.
* Helpers to cut a contour along a horizontal or vertical line (terminals are
  always cut on the grid, never on a diagonal) and to transform contours.

Coordinates are font units (UPM 2048).  Angles are degrees, 0 = +x, 90 = +y.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from fontTools.misc.bezierTools import (
    splitCubicAtT,
    solveCubic,
)

Point = tuple[float, float]


def vec(angle: float) -> Point:
    rad = math.radians(angle)
    return (math.cos(rad), math.sin(rad))


def add(a: Point, b: Point) -> Point:
    return (a[0] + b[0], a[1] + b[1])


def sub(a: Point, b: Point) -> Point:
    return (a[0] - b[0], a[1] - b[1])


def mul(a: Point, s: float) -> Point:
    return (a[0] * s, a[1] * s)


def lerp(a: Point, b: Point, t: float) -> Point:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def dist(a: Point, b: Point) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def cross(a: Point, b: Point) -> float:
    return a[0] * b[1] - a[1] * b[0]


def line_intersection(p: Point, d: Point, q: Point, e: Point) -> tuple[float, float] | None:
    """Return (s, u) so that p + s*d == q + u*e, or None when parallel."""
    den = cross(d, e)
    if abs(den) < 1e-9:
        return None
    w = sub(q, p)
    return cross(w, e) / den, cross(w, d) / den


def tension_handles(p0: Point, a0: float, p3: Point, a3: float, k0: float, k3: float | None = None) -> tuple[Point, Point]:
    """Handles for a curve leaving p0 in direction a0 and arriving at p3 in
    direction a3.  ``k`` is measured against the tangent intersection."""
    if k3 is None:
        k3 = k0
    d0 = vec(a0)
    d3 = vec(a3)
    hit = line_intersection(p0, d0, p3, mul(d3, -1))
    chord = dist(p0, p3)
    if hit is None or hit[0] <= 1e-6 or hit[1] <= 1e-6:
        # Tangents do not meet in front of the segment (S-shaped or straight):
        # fall back to chord-relative handles.
        l0 = chord * k0 * 0.6
        l3 = chord * k3 * 0.6
    else:
        l0 = hit[0] * k0
        l3 = hit[1] * k3
    return add(p0, mul(d0, l0)), sub(p3, mul(d3, l3))


@dataclass
class Contour:
    """Closed contour. ``segments`` holds ('line', pt) or ('curve', c1, c2, pt);
    the start point is ``start`` and the contour closes back to it."""

    start: Point
    segments: list = field(default_factory=list)

    @property
    def current(self) -> Point:
        return self.segments[-1][-1] if self.segments else self.start

    def line(self, pt: Point) -> "Contour":
        if dist(self.current, pt) > 1e-6:
            self.segments.append(("line", pt))
        return self

    def curve(self, pt: Point, a0: float, a1: float, k: float, k1: float | None = None) -> "Contour":
        c1, c2 = tension_handles(self.current, a0, pt, a1, k, k1)
        self.segments.append(("curve", c1, c2, pt))
        return self

    def cubic(self, c1: Point, c2: Point, pt: Point) -> "Contour":
        self.segments.append(("curve", c1, c2, pt))
        return self

    def close(self) -> "Contour":
        if self.segments and self.segments[-1][0] == "line" and dist(self.segments[-1][1], self.start) < 1e-6:
            self.segments.pop()
        return self

    # ------------------------------------------------------------------ geometry
    def beziers(self):
        """Yield every segment as a list of points, including the closing line."""
        p = self.start
        for seg in self.segments:
            if seg[0] == "line":
                yield [p, seg[1]]
                p = seg[1]
            else:
                yield [p, seg[1], seg[2], seg[3]]
                p = seg[3]
        if dist(p, self.start) > 1e-6:
            yield [p, self.start]

    def signed_area(self) -> float:
        # Green's theorem on the flattened curve; accurate enough for winding.
        area = 0.0
        for seg in self.beziers():
            pts = flatten(seg, 16)
            for a, b in zip(pts, pts[1:]):
                area += a[0] * b[1] - b[0] * a[1]
        return area / 2

    def reversed(self) -> "Contour":
        segs = list(self.beziers())
        out = Contour(segs[-1][-1])
        for seg in reversed(segs):
            if len(seg) == 2:
                out.segments.append(("line", seg[0]))
            else:
                out.segments.append(("curve", seg[2], seg[1], seg[0]))
        return out.close()

    def oriented(self, counter_clockwise: bool) -> "Contour":
        ccw = self.signed_area() > 0
        return self if ccw == counter_clockwise else self.reversed()

    def transformed(self, fn) -> "Contour":
        out = Contour(fn(self.start))
        for seg in self.segments:
            out.segments.append((seg[0], *[fn(p) for p in seg[1:]]))
        return out

    def translated(self, dx: float, dy: float) -> "Contour":
        return self.transformed(lambda p: (p[0] + dx, p[1] + dy))

    def mirrored_x(self, axis: float) -> "Contour":
        return self.transformed(lambda p: (2 * axis - p[0], p[1])).reversed()

    def mirrored_y(self, axis: float) -> "Contour":
        return self.transformed(lambda p: (p[0], 2 * axis - p[1])).reversed()

    def rotated180(self, cx: float, cy: float) -> "Contour":
        return self.transformed(lambda p: (2 * cx - p[0], 2 * cy - p[1]))

    def rotated(self, angle: float, cx: float, cy: float) -> "Contour":
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        return self.transformed(lambda p: (cx + (p[0] - cx) * c - (p[1] - cy) * s, cy + (p[0] - cx) * s + (p[1] - cy) * c))

    def scaled(self, sx: float, sy: float | None = None, cx: float = 0.0, cy: float = 0.0) -> "Contour":
        sy = sx if sy is None else sy
        out = self.transformed(lambda p: (cx + (p[0] - cx) * sx, cy + (p[1] - cy) * sy))
        return out if sx * sy > 0 else out.reversed()

    def offset(self, d: float) -> "Contour":
        """Move every edge ``d`` units to its right (outwards for a
        counter-clockwise outer contour, into the counter for a clockwise
        one), i.e. embolden by ``d`` per side.  Control polygons are offset
        and re-intersected (Tiller–Hanson); good for the small offsets used to
        keep scaled-down forms (superiors, symbols) at stroke weight."""
        segs = [s for s in self.beziers() if dist(s[0], s[-1]) > 1e-6 or len(s) == 4]
        n = len(segs)

        def edges(seg):
            out = []
            for a, b in zip(seg, seg[1:]):
                if dist(a, b) > 1e-6:
                    out.append((a, b))
            return out or [(seg[0], seg[-1])]

        def shift(edge):
            a, b = edge
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1.0
            nx, ny = dy / ln * d, -dx / ln * d
            return (a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny)

        def meet(e1, e2, fallback):
            a1, b1 = e1
            a2, b2 = e2
            hit = line_intersection(a1, sub(b1, a1), a2, sub(b2, a2))
            if hit is None:
                return fallback
            p = add(a1, mul(sub(b1, a1), hit[0]))
            return p if dist(p, fallback) < 4 * abs(d) + 1 else fallback

        offs = [[shift(e) for e in edges(seg)] for seg in segs]
        starts = []
        for i in range(n):
            prev_last, cur_first = offs[i - 1][-1], offs[i][0]
            starts.append(meet(prev_last, cur_first, cur_first[0]))
        out = Contour(starts[0])
        for i, seg in enumerate(segs):
            end = starts[(i + 1) % n]
            if len(seg) == 2:
                out.line(end)
                continue
            p0, p1, p2, p3 = seg
            raw = [(p0, p1), (p1, p2), (p2, p3)]
            sh = [shift(e) if dist(*e) > 1e-6 else None for e in raw]
            e0 = sh[0] or sh[1] or sh[2]
            e2 = sh[2] or sh[1] or sh[0]
            q1 = meet(e0, sh[1], e0[1]) if sh[0] and sh[1] else (e0[1] if sh[0] else starts[i])
            q2 = meet(sh[1], e2, e2[0]) if sh[2] and sh[1] else (e2[0] if sh[2] else end)
            out.cubic(q1, q2, end)
        return out.close()

    def bounds(self):
        xs, ys = [], []
        for seg in self.beziers():
            for p in flatten(seg, 24):
                xs.append(p[0])
                ys.append(p[1])
        return min(xs), min(ys), max(xs), max(ys)

    def draw(self, pen, round_to: float = 1.0):
        r = (lambda p: (round(p[0] / round_to) * round_to, round(p[1] / round_to) * round_to)) if round_to else (lambda p: p)
        pen.moveTo(r(self.start))
        for seg in self.segments:
            if seg[0] == "line":
                pen.lineTo(r(seg[1]))
            else:
                pen.curveTo(r(seg[1]), r(seg[2]), r(seg[3]))
        pen.closePath()


def flatten(seg, steps: int = 16):
    if len(seg) == 2:
        return [seg[0], seg[1]]
    p0, p1, p2, p3 = seg
    out = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1 - t
        out.append(
            (
                mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0],
                mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1],
            )
        )
    return out


def cubic_point(seg, t: float) -> Point:
    return flatten_at(seg, t)


def flatten_at(seg, t: float) -> Point:
    p0, p1, p2, p3 = seg
    mt = 1 - t
    return (
        mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0],
        mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1],
    )


def cubic_derivative(seg, t: float) -> Point:
    p0, p1, p2, p3 = seg
    mt = 1 - t
    return (
        3 * mt * mt * (p1[0] - p0[0]) + 6 * mt * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0]),
        3 * mt * mt * (p1[1] - p0[1]) + 6 * mt * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1]),
    )


def cubic_t_at(seg, value: float, axis: int) -> list[float]:
    """Parameters t in [0, 1] where the cubic crosses ``value`` on ``axis``."""
    p0, p1, p2, p3 = (p[axis] for p in seg)
    a = -p0 + 3 * p1 - 3 * p2 + p3
    b = 3 * p0 - 6 * p1 + 3 * p2
    c = -3 * p0 + 3 * p1
    d = p0 - value
    roots = solveCubic(a, b, c, d) if abs(a) > 1e-12 else _solve_quadratic(b, c, d)
    return sorted(t for t in roots if -1e-9 <= t <= 1 + 1e-9)


def _solve_quadratic(a, b, c):
    if abs(a) < 1e-12:
        return [] if abs(b) < 1e-12 else [-c / b]
    disc = b * b - 4 * a * c
    if disc < 0:
        return []
    r = math.sqrt(disc)
    return [(-b - r) / (2 * a), (-b + r) / (2 * a)]


def split_cubic(seg, t: float):
    a, b = splitCubicAtT(*seg, t)
    return list(a), list(b)


def tangent_angle(seg, t: float) -> float:
    d = cubic_derivative(seg, t)
    return math.degrees(math.atan2(d[1], d[0]))


# --------------------------------------------------------------------- shapes
def rect(x0: float, y0: float, x1: float, y1: float) -> Contour:
    """Counter-clockwise rectangle."""
    return Contour((x0, y0)).line((x1, y0)).line((x1, y1)).line((x0, y1)).close()


def polygon(points) -> Contour:
    c = Contour(points[0])
    for p in points[1:]:
        c.line(p)
    return c.close()


def superellipse(cx: float, cy: float, rx: float, ry: float, kx: float, ky: float | None = None) -> Contour:
    """Counter-clockwise oval with four on-curve extremes.

    ``kx`` is the tension of the handles that lie on horizontal tangents (top
    and bottom extremes), ``ky`` of those on vertical tangents (left/right)."""
    if ky is None:
        ky = kx
    r = (cx + rx, cy)
    t = (cx, cy + ry)
    l = (cx - rx, cy)
    b = (cx, cy - ry)
    c = Contour(r)
    c.cubic((cx + rx, cy + ry * ky), (cx + rx * kx, cy + ry), t)
    c.cubic((cx - rx * kx, cy + ry), (cx - rx, cy + ry * ky), l)
    c.cubic((cx - rx, cy - ry * ky), (cx - rx * kx, cy - ry), b)
    c.cubic((cx + rx * kx, cy - ry), (cx + rx, cy - ry * ky), r)
    return c.close()


def oval_quadrants(cx, cy, rx, ry, kx, ky=None):
    """The four quadrant cubics of an oval, counter-clockwise from the right
    extreme: [right->top, top->left, left->bottom, bottom->right]."""
    c = superellipse(cx, cy, rx, ry, kx, ky)
    return list(c.beziers())


def stroke_polygon(p: Point, q: Point, width: float) -> list[Point]:
    """Four corners of a straight stroke of perpendicular ``width`` from p to q."""
    d = sub(q, p)
    n = mul((-d[1], d[0]), width / 2 / math.hypot(*d))
    return [add(p, n), sub(p, n), sub(q, n), add(q, n)]


def stroke(p: Point, q: Point, width: float, cut="h") -> Contour:
    """Straight stroke of perpendicular ``width`` along the centre line p->q.

    Ends are cut on the grid: ``"h"`` horizontally (at the y of the end
    point), ``"v"`` vertically, ``"p"`` perpendicular to the stroke (for ends
    hidden inside another stroke).  ``cut`` may be one value or a pair
    (cut at p, cut at q)."""
    d = sub(q, p)
    ln = math.hypot(*d)
    ux, uy = d[0] / ln, d[1] / ln
    nx, ny = -uy, ux  # left normal
    h = width / 2
    cp, cq = (cut, cut) if isinstance(cut, str) else cut

    def end(pt, kind):
        if kind == "p":
            return (pt[0] + nx * h, pt[1] + ny * h), (pt[0] - nx * h, pt[1] - ny * h)
        if kind == "h":
            hw = h / abs(uy)
            return (pt[0] - hw * (1 if uy > 0 else -1), pt[1]), (pt[0] + hw * (1 if uy > 0 else -1), pt[1])
        hh = h / abs(ux)
        return (pt[0], pt[1] + hh * (1 if ux > 0 else -1)), (pt[0], pt[1] - hh * (1 if ux > 0 else -1))

    pl, pr = end(p, cp)  # left / right of the centre line
    ql, qr = end(q, cq)
    return polygon([pl, pr, qr, ql]).oriented(True)


def offset_cubic(seg, d: float):
    """Cubic ``seg`` offset by ``d`` along its left normal (Tiller–Hanson):
    control-polygon edges are shifted and re-intersected."""
    p0, p1, p2, p3 = seg

    def shift(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        n = (-dy / ln * d, dx / ln * d)
        return add(a, n), add(b, n)

    e0, e1, e2 = shift(p0, p1), shift(p1, p2), shift(p2, p3)

    def meet(a, b):
        hit = line_intersection(a[0], sub(a[1], a[0]), b[0], sub(b[1], b[0]))
        return a[1] if hit is None else add(a[0], mul(sub(a[1], a[0]), hit[0]))

    return [e0[0], meet(e0, e1), meet(e1, e2), e2[1]]


def offset_line(p: Point, q: Point, off: float):
    """Line through p->q shifted by ``off`` along its left normal."""
    d = sub(q, p)
    n = mul((-d[1], d[0]), off / math.hypot(*d))
    return add(p, n), add(q, n)


def intersect_lines(p1: Point, p2: Point, q1: Point, q2: Point) -> Point:
    hit = line_intersection(p1, sub(p2, p1), q1, sub(q2, q1))
    if hit is None:
        raise ValueError("parallel lines")
    return add(p1, mul(sub(p2, p1), hit[0]))


def x_at_y(p: Point, q: Point, y: float) -> float:
    return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])


def with_corner(c: "Contour", p: Point) -> "Contour":
    """A straight stroke with an extra corner at ``p``, a point on one of its
    edges.  Another outline that meets the edge there then rounds to the same
    integer point, so the overlap union leaves no sub-unit step."""
    pts = [c.start] + [seg[-1] for seg in c.segments]
    assert all(seg[0] == "line" for seg in c.segments), "a straight stroke"
    for i, (a, b) in enumerate(zip(pts, pts[1:] + pts[:1])):
        if min(a[1], b[1]) < p[1] < max(a[1], b[1]) and abs(x_at_y(a, b, p[1]) - p[0]) < 1e-6:
            return polygon(pts[: i + 1] + [p] + pts[i + 1 :]).oriented(True)
    raise AssertionError("the corner is not on an edge")


def with_foot(c: "Contour", y: float, xl: float, xr: float) -> "Contour":
    """A straight stroke whose two corners on the horizontal cut at ``y``
    move to ``xl`` and ``xr``."""
    pts = [c.start] + [seg[-1] for seg in c.segments]
    on = sorted(p for p in pts if abs(p[1] - y) < 1e-6)
    assert len(on) == 2 and all(seg[0] == "line" for seg in c.segments), "a straight stroke cut at y"
    moved = {on[0]: (xl, y), on[1]: (xr, y)}
    return polygon([moved.get(p, p) for p in pts]).oriented(True)


def shared_foot(strokes: list, y: float = 0) -> list:
    """Strokes ending on one horizontal cut at ``y`` (a W or w vertex) share
    the whole cut.  Cuts of different slopes end a unit apart otherwise, and
    the union keeps a 1-2 unit step at the foot."""
    on = [p for c in strokes for p in [c.start] + [seg[-1] for seg in c.segments] if abs(p[1] - y) < 1e-6]
    xl, xr = min(p[0] for p in on), max(p[0] for p in on)
    return [with_foot(c, y, xl, xr) for c in strokes]


def untangled(contour: "Contour") -> list:
    """The contour itself, or, if an offset folded it over itself, the clean
    outline of the area it covers (pathops simplify)."""
    import pathops

    path = pathops.Path()
    contour.draw(path.getPen())
    simple = pathops.simplify(path)
    if len(list(simple.contours)) == 1 and abs(abs(simple.area) - abs(path.area)) <= 1:
        return [contour]
    return _contours_from(simple)


def united(groups: list) -> list:
    """The contours of ``groups`` (lists of contours, counters with their
    outlines) as they are when one union of all of them works, as ufo2ft
    will run at compile time; otherwise their union built group by group.
    Outlines that share an exact curve (the § ring and its s bowls) can make
    the one-shot union fail at some weights."""
    import pathops

    def path(cs):
        p = pathops.Path()
        for c in cs:
            c.draw(p.getPen())
        return p

    flat = [c for g in groups for c in g]
    try:
        pathops.simplify(path(flat))
        return flat
    except pathops.PathOpsError:
        acc = pathops.simplify(path(groups[0]))
        for g in groups[1:]:
            acc = pathops.op(acc, path(g), pathops.PathOp.UNION)
        return _contours_from(acc)


def _contours_from(simple) -> list:
    import pathops

    out, c = [], None
    for verb, pts in simple:
        if verb == pathops.PathVerb.MOVE:
            c = Contour(pts[0])
        elif verb == pathops.PathVerb.LINE:
            c.line(pts[0])
        elif verb == pathops.PathVerb.CUBIC:
            c.cubic(*pts)
        elif verb == pathops.PathVerb.QUAD:
            p0 = c.current
            q, p = pts
            c.cubic((p0[0] + 2 / 3 * (q[0] - p0[0]), p0[1] + 2 / 3 * (q[1] - p0[1])), (p[0] + 2 / 3 * (q[0] - p[0]), p[1] + 2 / 3 * (q[1] - p[1])), p)
        elif verb == pathops.PathVerb.CLOSE:
            out.append(c.close())
    return out

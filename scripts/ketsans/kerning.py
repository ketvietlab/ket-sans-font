"""Kerning groups and pairs for KÉT Sans.

Spacing does the heavy lifting (sidebearings by edge shape, see the design
system); kerning only corrects meetings that sidebearings cannot: diagonals,
open arms (T F L P), overhanging quotes and low punctuation.  Groups are named
by edge shape.  Every precomposed letter joins the groups of its base so marks
never break the kerning; letters whose mark changes an edge (horn, vertical
caron, slashes) keep only the unchanged side.

Figures are tabular and are deliberately not kerned.
"""

from __future__ import annotations

import unicodedata

import numpy as np

from .geometry import flatten
from .glyphs import Glyph

MIN_GAP = 60  # kerning never brings two outlines (marks included) closer than this

# Right edge of the first glyph (kern1).
KERN1 = {
    "H": ["H", "I", "M", "N", "J", "U"],
    "O": ["O", "D", "Q", "G", "B", "Thorn", "Oslash", "Dcroat"],
    "C": ["C"],
    "E": ["E", "AE", "OE"],
    "F": ["F"],
    "P": ["P"],
    "R": ["R"],
    "K": ["K", "X"],
    "L": ["L"],
    "T": ["T"],
    "V": ["V", "W"],
    "Y": ["Y"],
    "A": ["A"],
    "S": ["S"],
    "Z": ["Z"],
    "n": ["n", "h", "m"],
    "u": ["u", "d", "a", "q", "i", "l", "g", "j", "dotlessi", "dotlessj", "dcroat"],
    "o": ["o", "b", "p", "e", "c", "thorn", "oe", "ae", "oslash", "eth"],
    "r": ["r"],
    "f": ["f"],
    "t": ["t"],
    "k": ["k", "x"],
    "v": ["v", "w", "y"],
    "z": ["z"],
    "s": ["s"],
    "period": ["period", "comma", "ellipsis", "quotesinglbase", "quotedblbase"],
    "quote": ["quoteright", "quotedblright", "quoteleft", "quotedblleft", "quotesingle", "quotedbl"],
    "hyphen": ["hyphen", "endash", "emdash"],
}
# Left edge of the second glyph (kern2).
KERN2 = {
    "H": ["H", "I", "E", "F", "K", "L", "M", "N", "P", "R", "B", "D", "U", "Thorn", "Dcroat"],
    "O": ["O", "C", "G", "Q", "OE", "Oslash"],
    "A": ["A", "AE"],
    "T": ["T"],
    "V": ["V", "W"],
    "Y": ["Y"],
    "J": ["J"],
    "S": ["S"],
    "X": ["X"],
    "Z": ["Z"],
    "n": ["n", "m", "r", "p", "b", "h", "k", "l", "i", "u", "j", "dotlessi", "dotlessj", "thorn", "germandbls"],
    "o": ["o", "c", "e", "d", "q", "g", "a", "oe", "ae", "oslash", "eth", "dcroat"],
    "s": ["s"],
    "v": ["v", "w", "y"],
    "x": ["x"],
    "z": ["z"],
    "f": ["f", "t"],
    "period": ["period", "comma", "ellipsis", "quotesinglbase", "quotedblbase"],
    "quote": ["quoteright", "quotedblright", "quoteleft", "quotedblleft", "quotesingle", "quotedbl"],
    "hyphen": ["hyphen", "endash", "emdash"],
}

PAIRS = {
    # diagonal and open capitals
    ("A", "T"): -110, ("A", "V"): -118, ("A", "Y"): -124, ("A", "O"): -26, ("A", "v"): -48, ("A", "quote"): -130,
    ("T", "A"): -110, ("V", "A"): -118, ("Y", "A"): -124, ("O", "A"): -30,
    ("O", "T"): -24, ("O", "V"): -40, ("O", "Y"): -46, ("O", "X"): -30,
    ("T", "O"): -24, ("V", "O"): -40, ("Y", "O"): -46, ("K", "O"): -46,
    ("F", "A"): -70, ("P", "A"): -90, ("P", "J"): -50, ("F", "J"): -40,
    ("L", "T"): -150, ("L", "V"): -130, ("L", "Y"): -150, ("L", "O"): -36, ("L", "v"): -60, ("L", "quote"): -200, ("L", "hyphen"): -80,
    ("R", "T"): -24, ("R", "V"): -30, ("R", "Y"): -36, ("R", "O"): -12,
    ("E", "o"): -16, ("C", "O"): -10,
    # capital + lowercase
    ("T", "o"): -150, ("T", "s"): -140, ("T", "n"): -110, ("T", "v"): -110, ("T", "x"): -110, ("T", "z"): -110,
    ("V", "o"): -96, ("V", "s"): -80, ("V", "n"): -40, ("V", "v"): -30,
    ("Y", "o"): -140, ("Y", "s"): -120, ("Y", "n"): -90, ("Y", "v"): -60,
    ("F", "o"): -40, ("P", "o"): -40, ("K", "o"): -40, ("K", "v"): -40,
    # lowercase
    ("r", "period"): -120, ("r", "o"): -12, ("f", "period"): -80, ("f", "o"): -20, ("f", "quote"): 60,
    ("v", "period"): -110, ("v", "o"): -16, ("o", "v"): -16, ("o", "x"): -20, ("k", "o"): -24,
    # punctuation
    ("T", "period"): -170, ("V", "period"): -150, ("Y", "period"): -170, ("F", "period"): -170, ("P", "period"): -200,
    ("period", "T"): -150, ("period", "V"): -150, ("period", "Y"): -160, ("period", "quote"): -120,
    ("quote", "A"): -130, ("quote", "o"): -60,
    ("T", "hyphen"): -120, ("V", "hyphen"): -60, ("Y", "hyphen"): -100, ("K", "hyphen"): -80,
    ("hyphen", "T"): -120, ("hyphen", "V"): -60, ("hyphen", "Y"): -100,
}

HORN = "̛"
KEEP_LEFT_ONLY = {"ď", "ľ", "ť", "Ľ"}


def _base_char(glyph: Glyph) -> str | None:
    if not glyph.unicodes:
        return None
    nfd = unicodedata.normalize("NFD", chr(glyph.unicodes[0]))
    return nfd[0] if len(nfd) > 1 else None


def build(glyphs: dict[str, Glyph]) -> tuple[dict, dict]:
    cmap = {chr(u): n for n, g in glyphs.items() for u in g.unicodes}
    member1: dict[str, str] = {}
    member2: dict[str, str] = {}
    for table, member in ((KERN1, member1), (KERN2, member2)):
        for gname, items in table.items():
            for n in items:
                if n in glyphs:
                    member[n] = gname
    for n, g in glyphs.items():
        if n in member1 or n in member2:
            continue
        b = _base_char(g)
        if b is None:
            continue
        ch = chr(g.unicodes[0])
        nfd = unicodedata.normalize("NFD", ch)
        base = cmap.get(b)
        if base is None:
            continue
        if base in member2:
            member2[n] = member2[base]
        if HORN not in nfd and ch not in KEEP_LEFT_ONLY and base in member1:
            member1[n] = member1[base]
    groups: dict[str, list[str]] = {}
    for n, k in member1.items():
        groups.setdefault(f"public.kern1.{k}", []).append(n)
    for n, k in member2.items():
        groups.setdefault(f"public.kern2.{k}", []).append(n)
    groups = {k: sorted(v) for k, v in sorted(groups.items())}
    kerning = {}
    for (left, right), value in PAIRS.items():
        lk, rk = f"public.kern1.{left}", f"public.kern2.{right}"
        if lk in groups and rk in groups:
            kerning[(lk, rk)] = value
    kerning.update(collision_exceptions(glyphs, groups, kerning))
    return groups, kerning


# ------------------------------------------------------------ collisions
YS = np.arange(-520, 2100, 16) + 0.5


def _polys(name, glyphs, dx=0.0, dy=0.0, steps=12):
    g = glyphs[name]
    out = []
    for c in g.contours:
        pts = []
        for seg in c.beziers():
            pts += flatten(seg, steps)[:-1] if len(seg) == 4 else [seg[0]]
        out.append(np.array(pts) + (dx, dy))
    for base, cx, cy in g.components:
        out += _polys(base, glyphs, dx + cx, dy + cy, steps)
    return out


def _profile(name, glyphs, ys=YS, steps=12):
    """Leftmost / rightmost ink at every sampled height (inf where empty)."""
    left = np.full(len(ys), np.inf)
    right = np.full(len(ys), -np.inf)
    Y = ys[None, :]
    for P in _polys(name, glyphs, steps=steps):
        Q = np.roll(P, -1, axis=0)
        x0, y0, x1, y1 = P[:, :1], P[:, 1:], Q[:, :1], Q[:, 1:]
        mask = ((y0 <= Y) & (Y < y1)) | ((y1 <= Y) & (Y < y0))
        dy = np.where(y1 == y0, 1, y1 - y0)
        X = x0 + (Y - y0) / dy * (x1 - x0)
        left = np.minimum(left, np.where(mask, X, np.inf).min(0))
        right = np.maximum(right, np.where(mask, X, -np.inf).max(0))
    return left, right


def collision_exceptions(glyphs, groups, kerning) -> dict:
    """Glyph-pair exceptions that ease a group value just enough to keep
    ``MIN_GAP`` (e.g. T + ĩ, where the mark would hit the T arm); where the
    pair collides even unkerned the exception is positive."""
    cache = {}

    def prof(n):
        if n not in cache:
            cache[n] = _profile(n, glyphs)
        return cache[n]

    out = {}
    for (g1, g2), value in kerning.items():
        for a in groups[g1]:
            ra = prof(a)[1]
            for b in groups[g2]:
                lb = prof(b)[0]
                ok = np.isfinite(ra) & np.isfinite(lb)
                if not ok.any():
                    continue
                gap = (glyphs[a].width + value + lb[ok] - ra[ok]).min()
                if gap < MIN_GAP:
                    # May turn positive: T + ĩ collide even unkerned.
                    out[(a, b)] = int(np.ceil(value + MIN_GAP - gap))
    return out


def optical_exceptions(text, display, groups, text_kerning, display_kerning, minimum_gap):
    """Do not introduce or worsen collisions as spacing tightens.

    Inspect every encoded letter/punctuation pair, including pairs with no
    Text kerning (Fĩ, brackets + accented capitals, f/, etc.). Existing narrow
    gaps stay at least as wide as Text; otherwise retain minimum_gap. The
    geometry only translates, so endpoint safety also covers interpolation.
    """
    names = [name for name, glyph in text.items() if glyph.unicodes and glyph.width
             and unicodedata.category(chr(glyph.unicodes[0]))[0] in "LP"]
    left_groups = {name: group for group, members in groups.items()
                   if group.startswith("public.kern1.") for name in members}
    right_groups = {name: group for group, members in groups.items()
                    if group.startswith("public.kern2.") for name in members}

    def value(a, b, table):
        left, right = left_groups.get(a, a), right_groups.get(b, b)
        return table.get((a, b), table.get((a, right), table.get((left, b), table.get((left, right), 0))))

    # Fine sampling catches a narrow tilde/brace meeting (ĩ}) that the static
    # 16-unit profile can miss. Keep the static builder's existing resolution.
    ys = np.arange(-520, 2100, 4) + 0.5
    before = {name: _profile(name, text, ys, 32) for name in names}
    after = {name: _profile(name, display, ys, 32) for name in names}
    result = {}
    for a in names:
        for b in names:
            ok = np.isfinite(before[a][1]) & np.isfinite(before[b][0])
            if not ok.any():
                continue
            original = (text[a].width + before[b][0][ok] - before[a][1][ok]).min() + value(a, b, text_kerning)
            current = (display[a].width + after[b][0][ok] - after[a][1][ok]).min() + value(a, b, display_kerning)
            floor = min(minimum_gap, original)
            if current < floor - 1e-6:
                result[(a, b)] = value(a, b, display_kerning) + int(np.ceil(floor - current))
    return result

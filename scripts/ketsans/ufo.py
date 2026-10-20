"""Write a KÉT Sans master to UFO3."""

from __future__ import annotations

from pathlib import Path

import ufoLib2

from .glyphs import Glyph
from .system import System

GLYPH_ORDER_HEAD = [".notdef", "space"]


def font_info(font: ufoLib2.Font, system: System, style: str) -> None:
    m, meta = system.m, system.meta
    info = font.info
    info.familyName = meta.familyName
    info.styleName = style
    # Regular and Bold link as one style-map family; other weights (Medium)
    # are their own family on Windows and group by the typographic names.
    linked = style in ("Regular", "Bold")
    info.styleMapFamilyName = meta.familyName if linked else f"{meta.familyName} {style}"
    info.styleMapStyleName = style.lower() if linked else "regular"
    info.versionMajor, info.versionMinor = (int(x) for x in meta.version.split("."))
    info.copyright = meta.copyright
    info.trademark = "KÉT is a trademark of Két Việt."
    info.openTypeNameDesigner = meta.designer
    info.openTypeNameManufacturer = meta.designer
    info.openTypeNameLicense = meta.license
    info.openTypeNameDescription = "KÉT Sans — neutral neo-grotesque for Vietnamese interfaces. " + meta.phase
    info.openTypeOS2VendorID = meta.vendorID
    info.openTypeOS2WeightClass = system.wght
    info.openTypeOS2WidthClass = 5
    info.openTypeOS2Type = []  # installable embedding
    info.openTypeOS2Selection = [7]  # USE_TYPO_METRICS
    info.postscriptFontName = f"{meta.postscriptFamily}-{style.replace(' ', '')}"
    info.postscriptFullName = f"{meta.familyName} {style}"
    info.unitsPerEm = m.unitsPerEm
    info.xHeight = m.xHeight
    info.capHeight = m.capHeight
    info.ascender = m.ascender
    info.descender = m.descender
    info.italicAngle = 0
    line = m.line
    info.openTypeOS2TypoAscender = line.typoAscender
    info.openTypeOS2TypoDescender = line.typoDescender
    info.openTypeOS2TypoLineGap = line.typoLineGap
    info.openTypeHheaAscender = line.typoAscender
    info.openTypeHheaDescender = line.typoDescender
    info.openTypeHheaLineGap = line.typoLineGap
    o = m.overshoot
    info.postscriptBlueValues = [
        -o.capRound, 0,
        m.xHeight, m.xHeight + o.lowercaseRound,
        m.capHeight, m.capHeight + o.capRound,
        m.ascender, m.ascender + 8,
    ]
    info.postscriptOtherBlues = [m.descender, m.descender + 8]
    info.postscriptStemSnapH = [system.st.barLower, system.st.barUpper]
    info.postscriptStemSnapV = [system.st.stemLower, system.st.stemUpper]
    info.postscriptUnderlinePosition = -200
    # One underline for the whole family (style-linked fonts must agree).
    info.postscriptUnderlineThickness = system.raw["masters"]["Regular"]["stroke"]["barLower"] - 40
    info.openTypeOS2StrikeoutPosition = int(0.47 * m.xHeight + system.st.barLower / 2)
    info.openTypeOS2StrikeoutSize = system.st.barLower - 30


def add_glyph(font: ufoLib2.Font, g: Glyph) -> None:
    glyph = font.newGlyph(g.name)
    glyph.width = round(g.width)
    glyph.unicodes = list(g.unicodes)
    pen = glyph.getPen()
    for contour in g.contours:
        contour.draw(pen)
    for base, dx, dy in g.components:
        pen.addComponent(base, (1, 0, 0, 1, round(dx), round(dy)))
    for name, (x, y) in sorted(g.anchors.items()):
        glyph.appendAnchor({"name": name, "x": round(x), "y": round(y)})
    if g.note:
        glyph.lib["vn.ketviet.construction"] = g.note


def write_master(glyphs: dict[str, Glyph], system: System, style: str, path: Path, features: str = "", groups=None, kerning=None) -> ufoLib2.Font:
    font = ufoLib2.Font()
    font_info(font, system, style)
    order = GLYPH_ORDER_HEAD + [n for n in glyphs if n not in GLYPH_ORDER_HEAD]
    for name in order:
        add_glyph(font, glyphs[name])
    font.lib["public.glyphOrder"] = order
    cats = {}
    for name, g in glyphs.items():
        if any(a.startswith("_") for a in g.anchors) or name.endswith("comb") or "comb_" in name or "comb." in name:
            cats[name] = "mark"
        elif g.unicodes or g.components:
            cats[name] = "base"
    font.lib["public.openTypeCategories"] = cats
    # Production names stay within the 31-character legacy limit.
    font.lib["public.postscriptNames"] = {
        n: n.replace("comb_", "").replace("abovecomb", "comb") for n in glyphs if len(n) > 31
    }
    font.features.text = features
    if groups:
        font.groups.update(groups)
    if kerning:
        font.kerning.update(kerning)
    if path.exists():
        import shutil

        shutil.rmtree(path)
    font.save(path)
    return font

"""Spacing-only optical masters, generated from KÉT's own glyph recipes.

Translate whole glyphs; never scale or reshape their contours. Accented letters
inherit their base's bearing reductions, including the dotless alternates used
by ccmp. Compensate component translations so marks stay attached to the body.
All design values live in design-system.json.
"""

from __future__ import annotations

import unicodedata
from functools import lru_cache

from fontTools.pens.boundsPen import BoundsPen


def display_spacing(glyphs, system):
    config = system.raw["opticalSizing"]["display"]
    cmap = {cp: name for name, glyph in glyphs.items() for cp in glyph.unicodes}

    @lru_cache(None)
    def base(name):
        glyph = glyphs[name]
        for component, _, _ in glyph.components:
            if glyphs[component].width > 0:
                return base(component)
        if glyph.unicodes:
            char = chr(glyph.unicodes[0])
            decomposed = unicodedata.normalize("NFD", char)[0]
            parent = cmap.get(ord(decomposed))
            if parent and parent != name:
                return base(parent)
        return name

    @lru_cache(None)
    def reduction(name):
        glyph = glyphs[name]
        if glyph.width == 0 or name == ".notdef":
            return 0, 0
        parent = base(name)
        if parent != name:
            return reduction(parent)
        char = chr(glyph.unicodes[0]) if glyph.unicodes else ""
        if char == " ":
            return 0, round(glyph.width) - config["spaceAdvance"]
        if char and char in config["tabularCharacters"]:
            total = config["tabularAdvanceReduction"]
            return total // 2, total - total // 2
        category = unicodedata.category(char) if char else ""
        if category in ("Lu", "Lt"):
            key = "upperRound" if char in config["upperRoundLetters"] else "upper"
        elif category == "Ll":
            key = "lowerRound" if char in config["lowerRoundLetters"] else "lower"
        elif category.startswith("P"):
            key = "punctuation"
        else:
            return 0, 0
        scale = config[key + "SidebearingScale"]
        pen = BoundsPen(None)
        for contour in glyph.contours:
            contour.draw(pen)
        if pen.bounds is None:
            return 0, 0
        left, _, right, _ = pen.bounds
        # Retain existing overhangs; only reduce positive outside whitespace.
        return round(max(0, left) * (1 - scale)), round(max(0, glyph.width - right) * (1 - scale))

    reductions = {name: reduction(name) for name in glyphs}
    for name, glyph in glyphs.items():
        left, right = reductions[name]
        glyph.shifted(-left)
        glyph.components = [
            (component, dx - left + reductions[component][0], dy)
            for component, dx, dy in glyph.components
        ]
        glyph.width -= left + right
    return reductions

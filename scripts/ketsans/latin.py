"""The full Latin builder: Phase 2 masters plus every recipe module."""

from __future__ import annotations

from .glyphs import Builder, Glyph
from .figures import FIGURES, FigureMixin
from .lower import LOWER, LowerMixin
from .punct import PUNCT, PunctMixin
from .upper import UPPER, UpperMixin


class Latin(UpperMixin, LowerMixin, FigureMixin, PunctMixin, Builder):
    pass


RECIPES = list(UPPER) + list(LOWER) + list(FIGURES) + list(PUNCT)


def build_latin(builder: Latin) -> dict[str, Glyph]:
    out = {}
    for method in RECIPES:
        g = getattr(builder, method)()
        out[g.name] = g
    return out

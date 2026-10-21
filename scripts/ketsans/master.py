"""Assemble one KÉT Sans master: glyphs, Vietnamese marks, kerning, features."""

from __future__ import annotations

from pathlib import Path
from copy import deepcopy

from . import glyphs as G
from . import kerning as K
from . import latin as L
from . import marks as M
from .system import load
from .ufo import write_master


def assemble(master: str = "Regular", optical: str | None = None):
    system = load(master)
    builder = L.Latin(system)
    glyphs = G.build_core(builder)
    glyphs.update(L.build_latin(builder))
    glyphs.update(M.build_marks_and_letters(builder, glyphs))
    if optical == "Display":
        from .optical import display_spacing

        text_glyphs = deepcopy(glyphs)
        _, text_kerning = K.build(text_glyphs)
        display_spacing(glyphs, system)
    if optical:
        system.raw["meta"]["familyName"] += " Optical"
        system.raw["meta"]["postscriptFamily"] += "Optical"
    groups, kerning = K.build(glyphs)
    if optical == "Display":
        kerning.update(K.optical_exceptions(
            text_glyphs, glyphs, groups, text_kerning, kerning,
            system.raw["opticalSizing"]["display"]["minimumPairGap"],
        ))
    return system, glyphs, groups, kerning


def write(path: Path, master: str = "Regular", optical: str | None = None):
    system, glyphs, groups, kerning = assemble(master, optical)
    font = write_master(glyphs, system, master, path, features=M.features(glyphs), groups=groups, kerning=kerning)
    return font, glyphs

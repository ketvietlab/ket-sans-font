"""Assemble one KÉT Sans master: glyphs, Vietnamese marks, kerning, features."""

from __future__ import annotations

from pathlib import Path

from . import glyphs as G
from . import kerning as K
from . import latin as L
from . import marks as M
from .system import load
from .ufo import write_master


def assemble(master: str = "Regular"):
    system = load(master)
    builder = L.Latin(system)
    glyphs = G.build_core(builder)
    glyphs.update(L.build_latin(builder))
    glyphs.update(M.build_marks_and_letters(builder, glyphs))
    groups, kerning = K.build(glyphs)
    return system, glyphs, groups, kerning


def write(path: Path, master: str = "Regular"):
    system, glyphs, groups, kerning = assemble(master)
    font = write_master(glyphs, system, master, path, features=M.features(glyphs), groups=groups, kerning=kerning)
    return font, glyphs

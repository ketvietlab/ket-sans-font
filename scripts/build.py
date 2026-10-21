"""Build KÉT Sans from the design system.

    .venv/bin/python scripts/build.py

1. design-system.json  -> sources/KETSans-<Master>.ufo  (generated, committed;
                          one per weight: Light, Regular, Medium, Bold)
2. fontmake            -> TTF (quadratic) and OTF (CFF), overlaps removed
                          (then ketsans.cleanup drops shapeless points),
                          nested components flattened
3. ttfautohint         -> hinted TTF for Windows/Linux small sizes
4. fontTools           -> WOFF2 from the hinted TTF
5. win metrics from the real glyph bounds of the whole family (the same in
   every weight), fixed timestamps (reproducible)
6. Text/Display spacing -> one opsz-only TTF/WOFF2 per fixed weight; static
   hinted fonts remain available alongside the optical files
"""

from __future__ import annotations

import os
from copy import deepcopy
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fontTools.ttLib import TTFont, newTable  # noqa: E402
from fontTools.ttLib.tables.ttProgram import Program  # noqa: E402
from fontTools.designspaceLib import DesignSpaceDocument  # noqa: E402
from fontTools.otlLib.builder import buildStatTable  # noqa: E402

from ketsans import master  # noqa: E402
from ketsans.system import ROOT, load  # noqa: E402

VENV_BIN = Path(sys.executable).parent
# 2026-10-20 00:00:00 UTC: fixed so identical sources give identical binaries.
SOURCE_DATE_EPOCH = "1792454400"


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def fix_metrics(path: Path, y_max: int, y_min: int) -> None:
    font = TTFont(path, recalcTimestamp=False)
    os2, hhea = font["OS/2"], font["hhea"]
    os2.usWinAscent = max(y_max, os2.sTypoAscender)
    os2.usWinDescent = max(-y_min, -os2.sTypoDescender)
    hhea.ascent = os2.sTypoAscender
    hhea.descent = os2.sTypoDescender
    hhea.lineGap = os2.sTypoLineGap
    font.save(path)


def main() -> None:
    styles = load().masters
    raw = {style: compile_master(style) for style in styles}
    # One set of win metrics for the family, so weights share a line box.
    heads = [TTFont(path)["head"] for pair in raw.values() for path in pair]
    y_max, y_min = max(h.yMax for h in heads), min(h.yMin for h in heads)
    for style in styles:
        finish_master(style, *raw[style], y_max, y_min)
        build_optical(style, y_max, y_min)
    run([sys.executable, ROOT / "scripts" / "specimen_data.py"])
    run([sys.executable, ROOT / "scripts" / "document.py"])


def compile_master(style: str) -> tuple[Path, Path]:
    system = load(style)
    family = system.meta.postscriptFamily
    src = ROOT / "sources" / f"{family}-{style}.ufo"
    src.parent.mkdir(parents=True, exist_ok=True)
    master.write(src, style)
    print("wrote", src.relative_to(ROOT))

    tmp = ROOT / "build" / "fontmake" / style
    shutil.rmtree(tmp, ignore_errors=True)
    # scripts/ on the path so fontmake can load the post-overlap cleanup filter.
    env = dict(os.environ, SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH, PYTHONPATH=str(ROOT / "scripts"))
    # One fontmake call per format: a combined "-o ttf otf" run lets the CFF
    # decomposition leak into the TTF, turning every Vietnamese composite into
    # re-approximated contours (caught by the NFC/NFD pixel check).
    for fmt in ("ttf", "otf"):
        run(
            [
                VENV_BIN / "fontmake", "-u", src, "-o", fmt,
                "--output-dir", tmp, "--overlaps-backend", "pathops",
                "--filter", "ketsans.cleanup::CleanupFilter",
                "--flatten-components", "--verbose", "WARNING",
            ],
            env=env,
            cwd=ROOT,
        )
    return tmp / f"{family}-{style}.ttf", tmp / f"{family}-{style}.otf"


def finish_master(style: str, raw_ttf: Path, raw_otf: Path, y_max: int, y_min: int) -> None:
    family = load(style).meta.postscriptFamily
    fonts = ROOT / "fonts"
    for sub in ("ttf", "otf", "woff2"):
        (fonts / sub).mkdir(parents=True, exist_ok=True)
    otf = fonts / "otf" / f"{family}-{style}.otf"
    ttf = fonts / "ttf" / f"{family}-{style}.ttf"
    shutil.copy(raw_otf, otf)
    fix_metrics(raw_ttf, y_max, y_min)
    fix_metrics(otf, y_max, y_min)

    import ttfautohint

    ttfautohint.ttfautohint(
        in_file=str(raw_ttf),
        out_file=str(ttf),
        hinting_range_min=8,
        hinting_range_max=50,
        hinting_limit=200,
        default_script="latn",
        fallback_script="none",
        increase_x_height=14,
        windows_compatibility=True,
        no_info=True,
    )
    # ttfautohint rewrites tables; restore the fixed timestamp.
    for path in (ttf, otf):
        f = TTFont(path, recalcTimestamp=False)
        f["head"].modified = f["head"].created
        if path == ttf:
            f["head"].flags |= 1 << 3  # hinted: round ppem to integers
        f.save(path, reorderTables=True)

    woff2 = fonts / "woff2" / f"{family}-{style}.woff2"
    f = TTFont(ttf, recalcTimestamp=False)
    f.flavor = "woff2"
    f.save(woff2)
    for p in (ttf, otf, woff2):
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size:,} bytes")


def build_optical(style: str, y_max: int, y_min: int) -> None:
    """One opsz-only variable font per weight; no cross-weight interpolation.

    These fonts are unhinted. Keep the existing hinted static TTF/WOFF2 set for
    clients which need it. Optical masters translate whole glyphs, so outline
    topology remains identical within each designspace.
    """
    system = load(style)
    settings = system.raw["opticalSizing"]["axis"]
    family = system.meta.postscriptFamily + "Optical"
    source_dir = ROOT / "build" / "optical-sources"
    source_dir.mkdir(parents=True, exist_ok=True)
    ds = DesignSpaceDocument()
    ds.addAxisDescriptor(
        name="Optical Size", tag="opsz", minimum=settings["minimum"],
        default=settings["default"], maximum=settings["maximum"],
        map=[tuple(pair) for pair in settings["map"]],
    )
    for label, coord in (("Text", settings["default"]), ("Display", settings["maximum"])):
        path = source_dir / f"{family}-{style}-{label}.ufo"
        font, glyphs = master.write(path, style, optical=label)
        # Union once, then translate the same contours at Display. Independent
        # pathops unions can choose different start points or round a joined
        # cedilla/ogonek differently, even for translated input.
        from ufo2ft.filters.removeOverlaps import RemoveOverlapsFilter
        from ketsans.cleanup import CleanupFilter
        from ketsans.optical import display_spacing

        if label == "Text":
            reductions = display_spacing(glyphs, system)
            RemoveOverlapsFilter(backend="pathops")(font)
            CleanupFilter()(font)
            text_font = font
        else:
            for glyph in font:
                glyph.clearContours()
                for source in text_font[glyph.name].contours:
                    contour = deepcopy(source)
                    for point in contour.points:
                        point.x -= reductions[glyph.name][0]
                    glyph.appendContour(contour)
        font.save(path, overwrite=True)
        ds.addSourceDescriptor(
            path=str(path), name=f"{style} {label}",
            familyName=system.meta.familyName + " Optical", styleName=style,
            location={"Optical Size": coord},
            copyInfo=label == "Text", copyLib=label == "Text",
            copyFeatures=label == "Text",
        )
        ds.addInstanceDescriptor(
            name=f"{style} {label}", familyName=system.meta.familyName + " Optical",
            styleName=style if label == "Text" else style + " Display",
            userLocation={"Optical Size": settings["default"] if label == "Text" else settings["display"]},
        )
    ds_path = source_dir / f"{family}-{style}.designspace"
    ds.write(ds_path)
    dest = ROOT / "fonts" / "variable"
    dest.mkdir(parents=True, exist_ok=True)
    ttf = dest / f"{family}-{style}.ttf"
    run([
        VENV_BIN / "fontmake", "-m", ds_path, "-o", "variable",
        "--output-path", ttf, "--overlaps-backend", "pathops",
        "--filter", "ketsans.cleanup::CleanupFilter", "--flatten-components",
        "--verbose", "WARNING",
    ], env=dict(os.environ, SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH, PYTHONPATH=str(ROOT / "scripts")), cwd=ROOT)
    fix_metrics(ttf, y_max, y_min)
    font = TTFont(ttf, recalcTimestamp=False)
    # Static weight axis in STAT helps applications group the four opsz files.
    buildStatTable(font, [
        {"tag": "wght", "name": "Weight", "ordering": 0,
         "values": [{"value": system.wght, "name": style, "flags": 2 if style == "Regular" else 0}]},
        {"tag": "opsz", "name": "Optical Size", "ordering": 1,
         "values": [
             {"nominalValue": settings["default"], "rangeMinValue": settings["minimum"],
              "rangeMaxValue": settings["default"], "name": "Text", "flags": 2},
             {"value": settings["display"], "name": "Display"},
         ]},
    ], macNames=False)
    # Smart dropout for monochrome rasterizers, not stem/grid hinting.
    font["prep"] = newTable("prep")
    font["prep"].program = Program()
    font["prep"].program.fromAssembly(["PUSHW[ ]", "511", "SCANCTRL[ ]", "PUSHB[ ]", "4", "SCANTYPE[ ]"])
    font["maxp"].maxStackElements = max(font["maxp"].maxStackElements, 1)
    font["head"].modified = font["head"].created
    font.save(ttf, reorderTables=True)
    font.flavor = "woff2"
    woff2 = ttf.with_suffix(".woff2")
    font.save(woff2)
    for path in (ttf, woff2):
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()

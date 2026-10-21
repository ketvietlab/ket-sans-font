"""Check the four opsz fonts: geometry, spacing, shaping, marks and sanitization.

    .venv/bin/python scripts/verify_optical.py

No reference-font data is used. Temporary static instances exercise the actual
variable GPOS/HVAR/gvar data, including forced NFD instead of cmap recomposition.
"""

from __future__ import annotations

import json
import tempfile
import unicodedata
from pathlib import Path

import numpy as np
import ots
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from ketsans.proof import Face, _record_to_polys
from ketsans.system import ROOT, load
from verify import Report, TABULAR, raster


def outline(font, name):
    gs = font.getGlyphSet()
    pen = DecomposingRecordingPen(gs)
    gs[name].draw(pen)
    return [op for op, _ in pen.value], np.array([p for _, pts in pen.value for p in pts], dtype=float)


def advance(face, text):
    return sum(pos.x_advance for _, pos in face.shape(text))


def pair_gap(font, face, text):
    """Measure compiled quadratic outlines after actual HarfBuzz positioning."""
    gs, order = font.getGlyphSet(), font.getGlyphOrder()
    y = np.arange(-520, 2100, 8)[None, :] + 0.5
    edges = []
    pen_x = 0
    for info, position in face.shape(text):
        rec = DecomposingRecordingPen(gs)
        gs[order[info.codepoint]].draw(rec)
        left, right = np.full(y.shape[1], np.inf), np.full(y.shape[1], -np.inf)
        for poly in _record_to_polys(rec.value, lambda p: p, steps=32):
            points = np.array(poly)
            following = np.roll(points, -1, axis=0)
            x0, y0 = points[:, :1], points[:, 1:]
            x1, y1 = following[:, :1], following[:, 1:]
            hit = ((y0 <= y) & (y < y1)) | ((y1 <= y) & (y < y0))
            xs = x0 + (y - y0) / np.where(y1 == y0, 1, y1 - y0) * (x1 - x0)
            left = np.minimum(left, np.where(hit, xs, np.inf).min(0))
            right = np.maximum(right, np.where(hit, xs, -np.inf).max(0))
        edges.append((left + pen_x + position.x_offset, right + pen_x + position.x_offset))
        pen_x += position.x_advance
    assert len(edges) == 2
    common = np.isfinite(edges[0][1]) & np.isfinite(edges[1][0])
    return float((edges[1][0][common] - edges[0][1][common]).min())


def main():
    report = Report()
    settings = load().raw["opticalSizing"]["axis"]
    metrics = {}
    for style in load().masters:
        report.prefix = style + ": "
        path = ROOT / "fonts" / "variable" / f"KETSansOptical-{style}.ttf"
        vf = TTFont(path)
        old = TTFont(ROOT / "fonts" / "ttf" / f"KETSans-{style}.ttf")
        axis = vf["fvar"].axes
        report.check("optical", "opsz axis and fixed weight", len(axis) == 1 and axis[0].axisTag == "opsz"
                     and (axis[0].minValue, axis[0].defaultValue, axis[0].maxValue)
                     == tuple(settings[k] for k in ("minimum", "default", "maximum"))
                     and vf["OS/2"].usWeightClass == load(style).wght)
        report.check("optical", "full charset and glyph order", vf.getBestCmap() == old.getBestCmap()
                     and vf.getGlyphOrder() == old.getGlyphOrder())
        report.check("optical", "embedding and line metrics preserved", vf["OS/2"].fsType == 0 and
                     all(getattr(vf["hhea"], k) == getattr(old["hhea"], k) for k in ("ascent", "descent", "lineGap")))
        report.check("optical", "fixed-weight names and style flags match the static face",
                     vf["head"].macStyle == old["head"].macStyle and
                     vf["OS/2"].fsSelection == old["OS/2"].fsSelection and
                     (vf["name"].getDebugName(17) or vf["name"].getDebugName(2)) == style)
        report.check("optical", "Text and Display named instances use the fixed weight",
                     [(vf["name"].getDebugName(i.subfamilyNameID), i.coordinates["opsz"])
                      for i in vf["fvar"].instances]
                     == [(style, settings["default"]), (style + " Display", settings["display"])])
        for fmt in ("ttf", "woff2"):
            target = path.with_suffix("." + fmt)
            result = ots.sanitize(str(target), capture_output=True)
            report.check("optical", f"OTS {fmt}", result.returncode == 0,
                         result.stderr.decode() if result.returncode else "")
        web = TTFont(path.with_suffix(".woff2"))
        report.check("optical", "WOFF2 tables equal TTF", all(
            vf.getTableData(tag) == web.getTableData(tag) for tag in vf.keys() if tag not in ("GlyphOrder", "head")))
        probes = [chr(cp) for cp in vf.getBestCmap()
                  if len(unicodedata.normalize("NFD", chr(cp))) > 1]
        words = ["Nguyễn Thị Mỹ Hằng", "Đường Nguyễn Huệ", "ẤN ĐỘ", "Ưu đãi",
                 "Thưởng 85.740.000 ₫", "ấ ầ ẩ ẫ ậ ế ề ể ễ ệ ố ồ ổ ỗ ộ",
                 "Ģirts Ķekava", "Šťastný"]
        default_outlines = {n: outline(vf, n) for n in vf.getGlyphOrder()}
        difficult = ("ĩ}", "Fĩ", "/Ī", "[Î", "f/", "AV", "Ty", "LT", "r.", "ẤV")
        default_face = Face(path, {"opsz": 16})
        baseline_gaps = {pair: pair_gap(vf, default_face, pair) for pair in difficult}
        metrics[style] = {}
        with tempfile.TemporaryDirectory(prefix="ketsans-opsz-check-") as folder:
            for coordinate in (8, 13, 16, 24, 32, 48, 72):
                instance = instantiateVariableFont(vf, {"opsz": coordinate}, inplace=False)
                dest = Path(folder) / f"opsz-{coordinate}.ttf"
                instance.save(dest)
                face = Face(dest)
                contacts = {pair: round(pair_gap(instance, face, pair), 2)
                            for pair in difficult
                            if pair_gap(instance, face, pair) < min(0, baseline_gaps[pair]) - 2}
                report.check("optical", f"opsz {coordinate}: difficult pairs avoid new contact (compiled + HarfBuzz)",
                             not contacts, str(contacts) if contacts else "")
                changed_shapes = []
                for name in vf.getGlyphOrder():
                    ops, points = outline(instance, name)
                    base_ops, base_points = default_outlines[name]
                    if ops != base_ops or points.shape != base_points.shape:
                        changed_shapes.append(name)
                    elif len(points):
                        difference = points - base_points
                        if np.max(np.abs(difference[:, 1])) > 1.01 or np.ptp(difference[:, 0]) > 1.01:
                            changed_shapes.append(name)
                report.check("optical", f"opsz {coordinate}: every glyph only translates horizontally",
                             not changed_shapes, ", ".join(changed_shapes[:12]))
                if coordinate <= 16:
                    report.check("optical", f"opsz {coordinate}: all Text advances unchanged",
                                 instance["hmtx"].metrics == old["hmtx"].metrics)
                cmap = instance.getBestCmap()
                widths = [advance(face, char) for char in TABULAR]
                report.check("optical", f"opsz {coordinate}: tabular figures/currency/math",
                             len(set(widths)) == 1, str(sorted(set(widths))))
                metrics[style][coordinate] = {
                    text: advance(face, text)
                    for text in ("nnnn", "oooo", "HHHH", "Khách hàng", "Nguyễn Thị Mỹ Hằng",
                                 "Đơn hàng đang xử lý", "HN-0012", "85.740.000 ₫", "AV", "Ty", "LT", "r.", "f/")
                }
                if coordinate not in (16, 32, 48):
                    continue
                stripped = TTFont(dest)
                for table in stripped["cmap"].tables:
                    table.cmap = {cp: name for cp, name in table.cmap.items()
                                  if len(unicodedata.normalize("NFD", chr(cp))) == 1}
                nfd_path = Path(folder) / f"nfd-{coordinate}.ttf"
                stripped.save(nfd_path)
                nfd_face = Face(nfd_path)
                mismatches = []
                for text in probes + words:
                    nfd = unicodedata.normalize("NFD", text)
                    a, b = raster(face, text), raster(nfd_face, nfd)
                    # Unioned cedilla/ogonek curves are re-approximated. At
                    # Display's translated pixel phase Bold Ų differs along
                    # five pixels of one ogonek edge at 96px (below baseline).
                    # Shape invariance across opsz is checked separately above.
                    allowance = 6 if ("\u0327" in nfd or "\u0328" in nfd) else 0
                    if a.shape != b.shape or (a != b).sum() > allowance:
                        mismatches.append(text)
                report.check("optical", f"opsz {coordinate}: NFC = forced base + GPOS marks ({len(probes)} letters)",
                             not mismatches, repr(mismatches[:12]) if mismatches else "")
                # All ink stays within the common Windows clipping bounds.
                ys = [point[1] for name in cmap.values() for point in outline(instance, name)[1]]
                report.check("optical", f"opsz {coordinate}: vertical metrics cover marks",
                             max(ys) <= vf["OS/2"].usWinAscent and min(ys) >= -vf["OS/2"].usWinDescent)
        values = list(metrics[style].values())
        report.check("optical", "all probe widths monotonically tighten; Display plateau",
                     all(all(a[text] >= b[text] for a, b in zip(values, values[1:])) for text in values[0])
                     and metrics[style][48] == metrics[style][72])
    out = ROOT / "build" / "qa"
    out.mkdir(parents=True, exist_ok=True)
    (out / "verify-optical.json").write_text(json.dumps(report.rows, ensure_ascii=False, indent=2))
    (out / "optical-widths.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2))
    passed = sum(row["ok"] is True for row in report.rows)
    print(f"\n{passed} passed, {len(report.failed)} failed")
    raise SystemExit(bool(report.failed))


if __name__ == "__main__":
    main()

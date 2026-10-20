"""KÉT Sans verification: structural, typographic, composition and Vietnamese checks.

    .venv/bin/python scripts/verify.py

Runs on the generated UFO and on the built TTF/OTF/WOFF2 of every master
(Regular, Medium, Bold), then checks the family as a whole.  Prints a report and
writes build/qa/verify.json (ignored by git).  Exit code 1 if any check fails.
"""

from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import ots  # noqa: E402
import pathops  # noqa: E402
import ufoLib2  # noqa: E402
from fontTools.pens.recordingPen import DecomposingRecordingPen  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402

from ketsans import marks as M  # noqa: E402
from ketsans.measure import Outlines  # noqa: E402
from ketsans.proof import Face, _fill_nonzero, _record_to_polys  # noqa: E402
from ketsans.system import ROOT, load  # noqa: E402

SYSTEM = load("Regular")
FAM = SYSTEM.meta.postscriptFamily
UFO = TTF = OTF = WOFF2 = None


def use(style: str) -> None:
    """Point the checks at one master's source and binaries."""
    global SYSTEM, UFO, TTF, OTF, WOFF2
    SYSTEM = load(style)
    UFO = ROOT / "sources" / f"{FAM}-{style}.ufo"
    TTF = ROOT / "fonts" / "ttf" / f"{FAM}-{style}.ttf"
    OTF = ROOT / "fonts" / "otf" / f"{FAM}-{style}.otf"
    WOFF2 = ROOT / "fonts" / "woff2" / f"{FAM}-{style}.woff2"

TABULAR = "0123456789$¢£¥€₫#+−×÷=<>"
REQUIRED_STRINGS = [
    "Tiếng Việt", "Quản lý", "Hệ thống", "Đường dẫn", "Người dùng", "Nguyễn",
    "Thương mại", "Cộng hòa", "Số lượng", "Dữ liệu",
]


class Report:
    def __init__(self):
        self.rows = []
        self.prefix = ""

    def check(self, group, name, ok, detail=""):
        name = self.prefix + name
        self.rows.append({"group": group, "check": name, "ok": bool(ok), "detail": detail})
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))

    def info(self, group, name, detail):
        name = self.prefix + name
        self.rows.append({"group": group, "check": name, "ok": None, "detail": detail})
        print(f"  [INFO] {name} — {detail}")

    @property
    def failed(self):
        return [r for r in self.rows if r["ok"] is False]


def path_of(contours_pen_value):
    path = pathops.Path()
    pen = path.getPen()
    from fontTools.pens.recordingPen import replayRecording

    replayRecording(contours_pen_value, pen)
    return path


def glyph_path(gs, name):
    rec = DecomposingRecordingPen(gs)
    gs[name].draw(rec)
    return path_of(rec.value), rec.value


# ------------------------------------------------------------------ structural
def structural(r: Report, ufo, fonts):
    print("\nStructural")
    required = M.charset()
    for label, f in fonts.items():
        cmap = f.getBestCmap()
        missing = [f"U+{cp:04X}" for cp in required if cp not in cmap]
        r.check("structural", f"coverage {label}: {len(required)} codepoints of charset.txt (GF Latin Core + Vietnamese + ₫)", not missing, ", ".join(missing[:10]))
    seen = {}
    dups = []
    for g in ufo:
        for u in g.unicodes:
            if u in seen:
                dups.append(f"U+{u:04X} {seen[u]}/{g.name}")
            seen[u] = g.name
    r.check("structural", "unicode mapping unique in source", not dups, ", ".join(dups))
    cm_t = fonts["TTF"].getBestCmap()
    cm_o = fonts["OTF"].getBestCmap()
    r.check("structural", "TTF and OTF cmaps identical", set(cm_t) == set(cm_o))

    open_c, tiny, nonint, selfx = [], [], [], []
    for g in ufo:
        for ci, c in enumerate(g.contours):
            pts = list(c)
            if pts and pts[0].type == "move":
                open_c.append(g.name)
            if len([p for p in pts if p.type]) < 2:
                tiny.append(g.name)
            if any(p.x != int(p.x) or p.y != int(p.y) for p in pts):
                nonint.append(g.name)
            path = pathops.Path()
            c.draw(path.getPen())
            simp = pathops.simplify(path)
            if len(list(simp.contours)) != 1 or abs(abs(simp.area) - abs(path.area)) > 1:
                selfx.append(f"{g.name}#{ci}")
    r.check("structural", "all source contours closed", not open_c, ", ".join(sorted(set(open_c))))
    r.check("structural", "no degenerate source contours", not tiny, ", ".join(sorted(set(tiny))))
    r.check("structural", "integer coordinates in source", not nonint, ", ".join(sorted(set(nonint))))
    r.check("structural", "no self-intersecting source contours", not selfx, ", ".join(selfx))

    bad_ref = [f"{g.name}->{c.baseGlyph}" for g in ufo for c in g.components if c.baseGlyph not in ufo]
    r.check("structural", "composite references resolve", not bad_ref, ", ".join(bad_ref))
    glyf = fonts["TTF"]["glyf"]
    nested = [n for n in glyf.keys() if glyf[n].isComposite() and any(glyf[c.glyphName].isComposite() for c in glyf[n].components)]
    scaled = [n for n in glyf.keys() if glyf[n].isComposite() and any(hasattr(c, "transform") for c in glyf[n].components)]
    r.check("structural", "TTF composites flat and translation-only", not nested and not scaled, ", ".join(nested + scaled))

    # Compiled outlines: overlaps removed, no self-intersections, winding ok.
    for label in ("OTF", "TTF"):
        f = fonts[label]
        gs = f.getGlyphSet()
        bad = []
        for name in f.getGlyphOrder():
            path, _ = glyph_path(gs, name)
            if not path.area:
                continue
            simp = pathops.simplify(path)
            if abs(abs(simp.area) - abs(path.area)) > 2 or (label == "OTF" and len(list(simp.contours)) != len(list(path.contours))):
                bad.append(name)
        r.check("structural", f"{label} outlines clean (no overlaps/self-intersections)", not bad, ", ".join(bad[:12]))

    f = fonts["TTF"]
    need = ["cmap", "head", "hhea", "hmtx", "maxp", "name", "OS/2", "post", "GDEF", "GPOS", "GSUB", "gasp", "glyf", "loca"]
    r.check("structural", "required TTF tables present", all(t in f for t in need), ", ".join(t for t in need if t not in f))
    gsub_feats = {fr.FeatureTag for fr in f["GSUB"].table.FeatureList.FeatureRecord}
    gpos_feats = {fr.FeatureTag for fr in f["GPOS"].table.FeatureList.FeatureRecord}
    r.check("structural", "GSUB ccmp, GPOS kern/mark/mkmk present", "ccmp" in gsub_feats and {"kern", "mark", "mkmk"} <= gpos_feats, f"GSUB={sorted(gsub_feats)} GPOS={sorted(gpos_feats)}")
    for label, path in (("TTF", TTF), ("OTF", OTF), ("WOFF2", WOFF2)):
        res = ots.sanitize(str(path), capture_output=True)
        r.check("structural", f"OpenType Sanitizer (browser validator) {label}", res.returncode == 0, (res.stderr or b"").decode()[:200])
    head, os2 = f["head"], f["OS/2"]
    r.check("structural", "win metrics cover all glyph bounds", os2.usWinAscent >= head.yMax and os2.usWinDescent >= -head.yMin, f"yMax={head.yMax} winAscent={os2.usWinAscent} yMin={head.yMin} winDescent={os2.usWinDescent}")
    r.check("structural", "installable (fsType 0) and USE_TYPO_METRICS", os2.fsType == 0 and bool(os2.fsSelection & (1 << 7)))


# ----------------------------------------------------------------- typographic
def typographic(r: Report, fonts):
    print("\nTypographic")
    m, st, sp, sh = SYSTEM.m, SYSTEM.st, SYSTEM.sp, SYSTEM.sh
    o = Outlines(fonts["OTF"])
    X, C, A, D = m.xHeight, m.capHeight, m.ascender, m.descender
    ov = m.overshoot

    def b(ch):
        return [round(v) for v in o.bounds(ch)]

    expectations = []
    F = m.figureHeight
    for ch in "HIENAVBDFKLMPRTUWXYZJ1457":
        expectations.append((ch, "yMax", C))
    for ch in "HIENAVBDEFKLMPRTWXYZnhmrilkvwxz1247":
        expectations.append((ch, "yMin", 0))
    for ch in "OCGSQ":
        expectations.append((ch, "yMax", C + ov.capRound))
    for ch in "OCGSUJ":
        expectations.append((ch, "yMin", -ov.capRound))
    for ch in "03689":
        expectations += [(ch, "yMax", F + ov.figureRound), (ch, "yMin", -ov.figureRound)]
    expectations.append(("5", "yMin", -ov.figureRound))
    for ch in "oecsa":
        expectations += [(ch, "yMax", X + ov.lowercaseRound), (ch, "yMin", -ov.lowercaseRound)]
    for ch in "nmhr":
        expectations.append((ch, "yMax", (A if ch == "h" else X + ov.arch)))
    for ch in "bdhlkþ":
        expectations.append((ch, "yMax", A))
    for ch in "pqyþ":
        expectations.append((ch, "yMin", D))
    for ch in "gj":
        expectations.append((ch, "yMin", D - ov.lowercaseRound))
    expectations += [("f", "yMax", A + ov.lowercaseRound), ("ß", "yMax", A + ov.arch), ("g", "yMax", X + ov.lowercaseRound)]
    for ch in "vwxyz":
        expectations.append((ch, "yMax", X))
    expectations += [("u", "yMax", X), ("u", "yMin", -ov.arch), ("dotlessi", "yMax", X), ("ȷ", "yMax", X)]
    bad = []
    for ch, key, want in expectations:
        bb = b(ch)
        got = bb[1] if key == "yMin" else bb[3]
        if abs(got - want) > 1:
            bad.append(f"{ch}.{key}={got}≠{want}")
    r.check("typographic", f"vertical alignment & overshoot ({len(expectations)} expectations)", not bad, ", ".join(bad))

    def run_w(ch, y, idx):
        runs = o.runs(ch, y, 1)
        return round(runs[idx][1] - runs[idx][0])

    def run_h(ch, x, idx):
        runs = o.runs(ch, x, 0)
        return round(runs[idx][1] - runs[idx][0])

    def mid(ch):
        bb = o.bounds(ch)
        return (bb[0] + bb[2]) / 2

    stems = {
        "n left": (run_w("n", 0.3 * X, 0), st.stemLower),
        "n right": (run_w("n", 0.3 * X, -1), st.stemLowerRight),
        "h left": (run_w("h", 0.3 * X, 0), st.stemLower),
        "m left": (run_w("m", 0.3 * X, 0), st.stemM),
        "i": (run_w("i", 0.3 * X, 0), st.stemLower),
        "l": (run_w("l", 0.3 * X, 0), st.stemLower),
        "dotlessi": (run_w("dotlessi", 0.3 * X, 0), st.stemLower),
        "r": (run_w("r", 0.3 * X, 0), st.stemLower),
        "d stem": (run_w("d", 0.5 * X, -1), st.stemLower),
        "b stem": (run_w("b", 0.5 * X, 0), st.stemLower),
        "p stem": (run_w("p", 0.5 * X, 0), st.stemLower),
        "q stem": (run_w("q", 0.5 * X, -1), st.stemLower),
        "u right": (run_w("u", 0.6 * X, -1), st.stemLower),
        "t": (run_w("t", 0.6 * X, 0), st.stemLower),
        "H left": (run_w("H", 0.25 * C, 0), st.stemUpper),
        "H right": (run_w("H", 0.25 * C, -1), st.stemUpper),
        "I": (run_w("I", 0.25 * C, 0), st.stemUpper),
        "E": (run_w("E", 0.25 * C, 0), st.stemUpper),
        "N left": (run_w("N", 0.5 * C, 0), st.stemN),
        "1": (run_w("1", 0.4 * C, 0), st.figureStem),
        "o side": (run_w("o", X / 2, 0), st.roundLowerSide),
        "O side": (run_w("O", C / 2, 0), st.roundUpperSide),
        "0 side": (run_w("0", C / 2, 0), st.figureSide),
        "6 bowl side": (run_w("6", 0.3 * C, -1), st.figureSide),
        "6 rising stroke": (run_w("6", 0.6 * C, 0), st.figureSide),
        "9 bowl side": (run_w("9", 0.7 * C, 0), st.figureSide),
        "B stem": (run_w("B", 0.25 * C, 0), st.stemUpper),
        "D stem": (run_w("D", 0.5 * C, 0), st.stemUpper),
        "F stem": (run_w("F", 0.25 * C, 0), st.stemUpper),
        "K stem": (run_w("K", 0.8 * C, 0), st.stemUpper),
        "L stem": (run_w("L", 0.5 * C, 0), st.stemUpper),
        "P stem": (run_w("P", 0.25 * C, 0), st.stemUpper),
        "R stem": (run_w("R", 0.25 * C, 0), st.stemUpper),
        "T stem": (run_w("T", 0.5 * C, 0), st.stemUpper),
        "J stem": (run_w("J", 0.7 * C, 0), st.stemUpper),
        "U left": (run_w("U", 0.7 * C, 0), st.stemUpper - 4),
        "M left": (run_w("M", 0.3 * C, 0), st.stemN),
        "C side": (run_w("C", C / 2, 0), st.roundUpperSide),
        "G side": (run_w("G", C / 2, 0), st.roundUpperSide),
        "k stem": (run_w("k", 1.2 * X, 0), st.stemLower),
        "f stem": (run_w("f", 0.3 * X, 0), st.stemLower),
        "j stem": (run_w("j", 0.5 * X, 0), st.stemLower),
        "g stem": (run_w("g", 0.5 * X, -1), st.stemLower),
        "4 stem": (run_w("4", 0.6 * C, -1), st.figureStem),
    }
    bars = {
        "H bar": (run_h("H", mid("H"), 0), st.barUpper),
        "E top arm": (run_h("E", (o.bounds("E")[0] + o.bounds("E")[2]) * 0.6, -1), st.barUpper),
        "e bar": (run_h("e", mid("e"), 1), st.barE),
        "t bar": (run_h("t", o.bounds("t")[0] + 40, -1), st.barLower),
        "hyphen": (run_h("hyphen", mid("hyphen"), 0), st.barLower),
        "o top": (run_h("o", mid("o"), -1), st.roundLowerTop),
        "O top": (run_h("O", mid("O"), -1), st.roundUpperTop),
        "0 top": (run_h("0", mid("0"), -1), st.figureTop),
        "6 bowl top": (run_h("6", mid("6") + 40, 1), st.figureTop),
        "n arch top": (run_h("n", mid("n") + 40, -1), st.archTop),
        "T bar": (run_h("T", o.bounds("T")[0] + 60, -1), st.barUpper),
        "F top arm": (run_h("F", o.bounds("F")[2] - 60, -1), st.barUpper),
        "L bar": (run_h("L", o.bounds("L")[2] - 60, 0), st.barUpper + 6),
        "D top arm": (run_h("D", mid("D"), -1), st.barUpper),
        "z bar": (run_h("z", o.bounds("z")[2] - 40, 0), st.barLower + 4),
        "f bar": (run_h("f", o.bounds("f")[0] + 40, -1), st.barLower),
        "5 bar": (run_h("5", o.bounds("5")[2] - 60, -1), st.figureTop + 4),
    }
    for label, table in (("stems", stems), ("horizontals & round", bars)):
        bad = [f"{k}={v}≠{w}" for k, (v, w) in table.items() if abs(v - w) > 3]
        r.check("typographic", f"{label} match the stroke system ({len(table)} measurements)", not bad, ", ".join(bad))
    r.info("typographic", "contrast (horizontal/vertical)", f"H {st.barUpper / st.stemUpper:.2f}, O {st.roundUpperTop / st.roundUpperSide:.2f}, o {st.roundLowerTop / st.roundLowerSide:.2f}, n arch {st.archTop / st.stemLower:.2f}")

    # Sidebearings by edge shape.
    f = fonts["OTF"]
    hmtx = f["hmtx"]
    cmap = f.getBestCmap()

    def sb(ch, side, y=None):
        # Measured on a horizontal ray through the body (ignores dots/marks):
        # low on straight stems, at mid-height on round sides, or at the
        # given height where the edge sits elsewhere (bowls, arms, diagonals).
        name = cmap[ord(ch)]
        adv = hmtx[name][0]
        straight = (side == 0 and ch in "nhmribpluk") or (side == 1 and ch in "nhmil")
        if y is None:
            y = (C if ch.isupper() else X) * (0.3 if straight else 0.5)
        cr = o.crossings(ch, y, 1)
        return round(cr[0]) if side == 0 else round(adv - cr[-1])

    groups = {
        "upper straight": ([("H", 0), ("H", 1), ("I", 0), ("I", 1), ("E", 0), ("N", 0), ("N", 1)] + [(c, 0) for c in "BDFKLPRM"] + [("M", 1)], sp.upperStraight, 6),
        "upper round": ([("O", 0), ("O", 1), ("C", 0), ("G", 0), ("Q", 0), ("D", 1)], sp.upperRound, 2),
        # S: left edge at the lower terminal cut, right edge at the lower bowl extreme (both from the shape system).
        "upper bowl": ([("B", 1, 0.27 * C), ("P", 1, 0.7 * C), ("S", 0, sh.sExtremeLower * C - sh.sTerminalLower * (sh.sExtremeLower * C + m.overshoot.capRound) - 2), ("S", 1, sh.sExtremeLower * C)], sp.upperBowl, 3),
        "upper cup": ([("U", 0), ("U", 1)], sp.upperCup, 2),
        "upper open": ([("T", 0, C - 60), ("T", 1, C - 60)], sp.upperOpen, 2),
        "lower straight left": ([(c, 0) for c in "nhmribplkj"] + [("i", 1), ("l", 1), ("j", 1)], sp.lowerStraight, 2),
        "lower straight right": ([(c, 1) for c in "nhm"], sp.lowerStraightRight, 2),
        "lower round": ([("o", 0), ("o", 1), ("d", 0), ("q", 0), ("b", 1), ("p", 1), ("c", 0), ("e", 0), ("g", 0)], sp.lowerRound, 2),
        "lower diagonal": ([("v", 0, X - 8), ("v", 1, X - 8), ("y", 0, X - 8), ("w", 0, X - 8), ("w", 1, X - 8)], sp.lowerDiagonal, 3),
    }
    for label, (items, want, tol) in groups.items():
        vals = {f"{it[0]}{'LR'[it[1]]}": sb(*it) for it in items}
        bad = {k: v for k, v in vals.items() if abs(v - want) > tol}
        r.check("typographic", f"sidebearings {label} = {want}", not bad, ", ".join(f"{k}={v}" for k, v in bad.items()))
    r.info("typographic", "advance widths", ", ".join(f"{c}={hmtx[cmap[ord(c)]][0]}" for c in "HOAVNnoaecs"))

    face = Face(TTF)

    def adv(text):
        return sum(p.x_advance for _, p in face.shape(text))

    def single(text):
        return sum(adv(c) for c in text)

    kerned = {t: adv(t) - single(t) for t in ["AV", "VA", "Vo", "Va", "V.", "r.", "ẤV", "VỚ", "Vớ", "To", "Tô", "Yo", "LT", "L’", "P.", "AT"]}
    r.check("typographic", "kerning applied, incl. Vietnamese letters via base groups", all(v < 0 for v in kerned.values()), ", ".join(f"{k}:{v}" for k, v in kerned.items()))
    flat = {t: adv(t) - single(t) for t in ["HH", "nn", "oo", "11", "00", "88", "HO", "nu", "ďa"]}
    r.check("typographic", "no kerning between straight/round pairs or tabular figures", all(v == 0 for v in flat.values()), ", ".join(f"{k}:{v}" for k, v in flat.items()))
    figs = {c: hmtx[cmap[ord(c)]][0] for c in TABULAR}
    r.check("typographic", f"figures, currency and math share one tabular advance ({len(TABULAR)} glyphs)", len(set(figs.values())) == 1, str(sorted(set(figs.values()))))

    # Kerning never makes neighbours touch: horizontal profiles of every
    # kerned group pair (drawn and precomposed members) keep >= 50 units.
    src = ufoLib2.Font.open(UFO)
    ys = list(range(-520, 2100, 16))
    prof = {}

    def profile(name):
        if name not in prof:
            left, right = {}, {}
            for y in ys:
                cr = o.crossings(name, y + 0.5, 1)
                if cr:
                    left[y], right[y] = cr[0], cr[-1]
            prof[name] = (left, right)
        return prof[name]

    prod = {g.name: cmap[g.unicodes[0]] for g in src if g.unicodes}
    effective = {}
    for (g1, g2), value in src.kerning.items():
        if g1.startswith("public.kern1.") and g2.startswith("public.kern2."):
            for a in src.groups[g1]:
                for b in src.groups[g2]:
                    effective[(a, b)] = value
    effective.update({k: v for k, v in src.kerning.items() if not k[0].startswith("public.") and not k[1].startswith("public.")})
    worst = []
    for (a, b), value in effective.items():
        a, b = prod[a], prod[b]
        ra, lb = profile(a)[1], profile(b)[0]
        gaps = [hmtx[a][0] + value + lb[y] - ra[y] for y in ys if y in ra and y in lb]
        if gaps and min(gaps) < 50:
            worst.append(f"{a}+{b}={min(gaps):.0f}")
    r.check("typographic", f"kerned pairs keep >= 50 units apart ({len(effective)} glyph pairs, exceptions applied)", not worst, ", ".join(worst[:12]))


# ------------------------------------------------------------------ Vietnamese
def _overlaps(gs, parts):
    """True if positioned component outlines share any area."""
    paths = []
    for name, dx, dy in parts:
        rec = DecomposingRecordingPen(gs)
        gs[name].draw(rec)
        from fontTools.pens.transformPen import TransformPen

        path = pathops.Path()
        from fontTools.pens.recordingPen import replayRecording

        replayRecording(rec.value, TransformPen(path.getPen(), (1, 0, 0, 1, dx, dy)))
        paths.append(path)
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            if abs(pathops.op(paths[i], paths[j], pathops.PathOp.INTERSECTION).area) > 0.5:
                return True
    return False


def raster(face: Face, text: str, px=96):
    from PIL import Image

    scale = px / face.upem
    nfc = unicodedata.normalize("NFC", text)
    img = Image.new("RGB", (int(px * (len(nfc) + 2) * 1.1) + 40, int(px * 2.6)), "white")
    gs = face_glyphset(face)
    x = 20.0
    base = px * 1.8
    polys = []
    for info, pos in face.shape(text):
        name = face_order(face)[info.codepoint]
        rec = DecomposingRecordingPen(gs)
        gs[name].draw(rec)
        gx = x + pos.x_offset * scale
        gy = base - pos.y_offset * scale
        polys += _record_to_polys(rec.value, lambda p, gx=gx, gy=gy: (gx + p[0] * scale, gy - p[1] * scale))
        x += pos.x_advance * scale
    _fill_nonzero(img, polys)
    return np.array(img.convert("L"))


_GS = {}


def face_glyphset(face):
    if face.path not in _GS:
        _GS[face.path] = TTFont(face.path)
    return _GS[face.path].getGlyphSet()


def face_order(face):
    return _GS[face.path].getGlyphOrder()


def composition(r: Report, ufo, fonts):
    print("\nComposition (marks, precomposed letters, ccmp)")
    face = Face(TTF)
    order = TTFont(TTF).getGlyphOrder()

    def names(text, f=face):
        o = TTFont(f.path).getGlyphOrder() if f is not face else order
        return [o[i.codepoint] for i, _ in f.shape(text)]

    probes = [chr(cp) for cp in M.charset() if len(unicodedata.normalize("NFD", chr(cp))) > 1]
    words = ["Việt", "dẫn", "mại", "hòa", "liệu", "Hệ", "ẤN", "ỘI", "Ở", "ặ", "ẳ", "ữ", "ợ", "Ưu", "Ỹ", "Łódź", "Ærøskøbing", "Šťastný", "Ģirts", "Ķekava"]
    # HarfBuzz would recompose NFD into the precomposed glyph, which makes the
    # comparison trivial.  Shape NFD with a copy whose cmap has no precomposed
    # letters, forcing base + marks through ccmp and GPOS anchors.
    import tempfile

    stripped = TTFont(TTF)
    for table in stripped["cmap"].tables:
        table.cmap = {cp: n for cp, n in table.cmap.items() if len(unicodedata.normalize("NFD", chr(cp))) == 1}
    tmp = Path(tempfile.mkdtemp()) / "decomposed.ttf"
    stripped.save(tmp)
    face_nfd = Face(tmp)
    mismatch = []
    for t in probes + words:
        nfd = unicodedata.normalize("NFD", t)
        if nfd == t:
            continue
        a, b = raster(face, t), raster(face_nfd, nfd)
        # Cedilla and ogonek are merged into the letter, which re-approximates
        # the curves at the join: allow a few pixels there, none elsewhere.
        allowed = 4 if ("\u0327" in nfd or "\u0328" in nfd) else 0
        if a.shape != b.shape or (a != b).sum() > allowed:
            mismatch.append(t)
    r.check("composition", f"precomposed (NFC) and GPOS-positioned NFD render pixel-identical ({len(probes)} letters + {len(words)} words; ≤ 4 px at cedilla/ogonek joins)", not mismatch, " ".join(mismatch[:20]))
    # HarfBuzz recomposes NFD into a precomposed glyph whenever the font has
    # one, so ccmp is exercised with sequences that have no precomposed form,
    # or on the copy without precomposed letters.
    cases = {
        "NFD with precomposed glyph recomposes": ("e\u0302\u0301", ["uni1EBF"], face),
        "i + top marks → dotless i + pair": ("i\u0306\u0301", ["dotlessi", "brevecomb_acutecomb"], face),
        "j + top mark → dotless j": ("j\u0302", ["dotlessj", "circumflexcomb"], face),
        "capital → case mark": ("H\u0301", ["H", "acutecomb.case"], face),
        "lowercase stack → pair": ("n\u0306\u0303", ["n", "brevecomb_tildecomb"], face),
        "capital stack → case pair": ("H\u0302\u0300", ["H", "circumflexcomb_gravecomb.case"], face),
        "o + horn → ơ": ("o\u031b", ["ohorn"], face),
        "U + horn → Ư": ("U\u031b", ["Uhorn"], face_nfd),
        "d + caron → vertical caron": ("d\u030c", ["d", "caroncomb.alt"], face_nfd),
        "L + caron → vertical caron, not case": ("L\u030c", ["L", "caroncomb.alt"], face_nfd),
        "K + cedilla → comma below": ("K\u0327", ["K", "commaaccentcomb"], face_nfd),
        "g + cedilla → turned comma above": ("g\u0327", ["g", "commaturnedabovecomb"], face_nfd),
        "C + cedilla stays cedilla": ("C\u0327", ["C", "cedillacomb"], face_nfd),
    }
    bad = []
    for label, (text, want, f) in cases.items():
        got = names(text, f)
        if got != want:
            bad.append(f"{label}: {got}")
    r.check("composition", f"ccmp substitutions ({len(cases)} cases)", not bad, "; ".join(bad))

    # Geometry of precomposed letters from the source.
    gs_ufo = ufo
    clear_base, clear_mark, center = [], [], []
    tallest = (None, -1e9)
    deepest = (None, 1e9)
    for g in ufo:
        if not g.unicodes or not g.components:
            continue
        ch = chr(g.unicodes[0])
        if len(unicodedata.normalize("NFD", ch)) < 2:
            continue
        parts = []
        for comp in g.components:
            rec = DecomposingRecordingPen(gs_ufo)
            gs_ufo[comp.baseGlyph].draw(rec)
            dx, dy = comp.transformation[4], comp.transformation[5]
            pts = [(x + dx, y + dy) for poly in _record_to_polys(rec.value, lambda p: p, steps=24) for (x, y) in poly]
            parts.append((comp.baseGlyph, np.array(pts), dx))
        base_name, base_pts, _ = parts[0]
        for mname, mpts, dx in parts[1:]:
            d = np.sqrt(((base_pts[::3, None, :] - mpts[None, ::2, :]) ** 2).sum(-1)).min()
            limit = 40 if mname == "caroncomb.alt" else 70  # the vertical caron sits beside the stem
            comps = {c.baseGlyph: c.transformation for c in g.components}
            if _overlaps(gs_ufo, [(base_name, 0, 0), (mname, comps[mname][4], comps[mname][5])]):
                d = 0
            if d < limit:
                clear_base.append(f"{ch}:{mname}={d:.0f}")
            if mname.removesuffix(".case") in M.TOP_MARKS.values():
                anchor = gs_ufo[base_name].anchors
                top = next(a for a in anchor if a.name == "top")
                cx = (mpts[:, 0].min() + mpts[:, 0].max()) / 2
                if abs(cx - top.x) > 6:
                    center.append(f"{ch}:{cx - top.x:+.0f}")
            ymax = mpts[:, 1].max()
            ymin = mpts[:, 1].min()
            if ymax > tallest[1]:
                tallest = (ch, ymax)
            if ymin < deepest[1]:
                deepest = (ch, ymin)
    for g in ufo:
        if "comb_" in g.name:
            pts = []
            for comp in g.components:
                rec = DecomposingRecordingPen(gs_ufo)
                gs_ufo[comp.baseGlyph].draw(rec)
                dx, dy = comp.transformation[4], comp.transformation[5]
                pts.append(np.array([(x + dx, y + dy) for poly in _record_to_polys(rec.value, lambda p: p, steps=24) for (x, y) in poly]))
            d = np.sqrt(((pts[0][:, None, :] - pts[1][None, :, :]) ** 2).sum(-1)).min()
            if _overlaps(gs_ufo, [(c.baseGlyph, c.transformation[4], c.transformation[5]) for c in g.components]):
                d = 0
            if d < 34:
                clear_mark.append(f"{g.name}={d:.0f}")
    r.check("composition", "marks clear of their base (≥ 70 units; cedilla/ogonek join on purpose)", not clear_base, ", ".join(clear_base[:12]))
    r.check("composition", "stacked marks never touch (≥ 34 units)", not clear_mark, ", ".join(clear_mark))
    r.check("composition", "single marks centred on the base's top anchor (±6)", not center, ", ".join(center[:12]))
    vietnamese(r, fonts, tallest)


def vietnamese(r: Report, fonts, tallest):
    print("\nVietnamese")
    os2 = fonts["TTF"]["OS/2"]
    r.info("vietnamese", "tallest mark stack", f"{tallest[0]} reaches {tallest[1]:.0f} (typoAscender {os2.sTypoAscender}, winAscent {os2.usWinAscent})")
    r.check("vietnamese", "tallest stack within 1.0 em above baseline", tallest[1] <= SYSTEM.m.unitsPerEm, f"{tallest[1]:.0f}")
    cmap = fonts["TTF"].getBestCmap()
    for s in REQUIRED_STRINGS:
        miss = sorted({c for c in s if ord(c) not in cmap and c != " "})
        if miss:
            r.info("vietnamese", f"required string “{s}”", f"waits for Phase 4 glyphs: {' '.join(miss)}")
        else:
            r.check("vietnamese", f"required string “{s}” fully covered", True)


def family(r: Report, styles):
    """Weights belong to one family: same glyphs and line box, style linking,
    and every master heavier than the one before it."""
    print("\nFamily")
    r.prefix = ""
    fonts = {}
    for style in styles:
        use(style)
        fonts[style] = TTFont(TTF)
    ref = fonts[styles[0]]
    r.check("family", f"same glyph order and cmap in {', '.join(styles)}",
            all(f.getGlyphOrder() == ref.getGlyphOrder() and f.getBestCmap() == ref.getBestCmap() for f in fonts.values()))
    keys = lambda f: (f["OS/2"].sTypoAscender, f["OS/2"].sTypoDescender, f["OS/2"].sTypoLineGap, f["hhea"].ascent, f["hhea"].descent,
                      f["hhea"].lineGap, f["OS/2"].usWinAscent, f["OS/2"].usWinDescent, f["head"].unitsPerEm, f["OS/2"].sxHeight, f["OS/2"].sCapHeight)
    r.check("family", "vertical metrics identical across weights", len({keys(f) for f in fonts.values()}) == 1,
            "; ".join(f"{s}={keys(f)}" for s, f in fonts.items()))
    bad = []
    for style, f in fonts.items():
        want = load(style).wght
        sel, mac = f["OS/2"].fsSelection, f["head"].macStyle
        bold = style == "Bold"
        if f["OS/2"].usWeightClass != want or bool(sel & (1 << 5)) != bold or bool(sel & (1 << 6)) == bold or bool(mac & 1) != bold:
            bad.append(f"{style}: wght {f['OS/2'].usWeightClass}, fsSelection {sel:#06x}, macStyle {mac}")
        # Regular and Bold link in one style-map family; other weights are the
        # Regular of their own (name 1/2) and group by typographic names (16/17).
        fam = SYSTEM.meta.familyName
        names = tuple(f["name"].getDebugName(i) for i in (1, 2, 16, 17))
        want_names = (fam, style, None, None) if style in ("Regular", "Bold") else (f"{fam} {style}", "Regular", fam, style)
        if names != want_names:
            bad.append(f"{style}: name 1/2/16/17 {names}")
    r.check("family", "style linking: weight class, fsSelection, macStyle and names", not bad, "; ".join(bad))
    stems = {}
    for style in styles:
        use(style)
        o = Outlines(TTFont(OTF))
        X, C = SYSTEM.m.xHeight, SYSTEM.m.capHeight
        stems[style] = {ch: (lambda runs: runs[0][1] - runs[0][0])(o.runs(ch, y, 1)) for ch, y in (("n", 0.3 * X), ("H", 0.25 * C), ("o", X / 2), ("O", C / 2))}
    heavier = all(stems[b][ch] > stems[a][ch] for a, b in zip(styles, styles[1:]) for ch in stems[a])
    r.check("family", "each weight heavier than the previous (n H o O)", heavier,
            "; ".join(f"{s} " + " ".join(f"{ch}={v:.0f}" for ch, v in d.items()) for s, d in stems.items()))


def main():
    r = Report()
    styles = SYSTEM.masters
    for style in styles:
        use(style)
        r.prefix = f"{style}: "
        ufo = ufoLib2.Font.open(UFO)
        fonts = {"TTF": TTFont(TTF), "OTF": TTFont(OTF), "WOFF2": TTFont(WOFF2)}
        print(f"\n===== KÉT Sans {style} {SYSTEM.meta.version} — {len(ufo)} source glyphs, {len(fonts['TTF'].getGlyphOrder())} compiled")
        structural(r, ufo, fonts)
        typographic(r, fonts)
        composition(r, ufo, fonts)
    family(r, styles)
    r.prefix = ""
    print("\nDocumentation")
    import document

    doc = document.DOC.read_text(encoding="utf-8")
    fresh = document.render(doc) == doc
    r.check("documentation", "FONT-DESIGN-SYSTEM.md tables match design-system.json and the built font", fresh, "" if fresh else "run scripts/document.py")
    out = ROOT / "build" / "qa"
    out.mkdir(parents=True, exist_ok=True)
    (out / "verify.json").write_text(json.dumps(r.rows, ensure_ascii=False, indent=2))
    passed = sum(1 for x in r.rows if x["ok"] is True)
    print(f"\n{passed} passed, {len(r.failed)} failed, {sum(1 for x in r.rows if x['ok'] is None)} info")
    sys.exit(1 if r.failed else 0)


if __name__ == "__main__":
    main()

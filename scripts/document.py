"""Regenerate the parameter tables in FONT-DESIGN-SYSTEM.md.

    .venv/bin/python scripts/document.py          # rewrite the generated block
    .venv/bin/python scripts/document.py --check  # exit 1 if it is stale

Everything between the GENERATED markers comes from design-system.json and
from measurements of the built OTF, so the document cannot drift from the font.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fontTools.ttLib import TTFont  # noqa: E402

from ketsans.measure import Outlines  # noqa: E402
from ketsans.system import ROOT, load  # noqa: E402

DOC = ROOT / "FONT-DESIGN-SYSTEM.md"
START = "<!-- GENERATED:START (scripts/document.py) -->"
END = "<!-- GENERATED:END -->"


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(" --- " for _ in head) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def generated() -> str:
    s = load("Regular")
    b = load("Bold")
    i = load("Medium")  # interpolated instance, see design-system.json "instances"
    li = load("Light")
    m, st, k, sh, w, sp = s.m, s.st, s.k, s.sh, s.w, s.sp
    bst, bsh, bw, bsp = b.st, b.sh, b.w, b.sp
    ist, ish, iw, isp = i.st, i.sh, i.w, i.sp
    lst, lsh, lw, lsp = li.st, li.sh, li.w, li.sp
    upm = m.unitsPerEm
    em = lambda v: f"{v / upm:.3f} em"
    parts = []
    parts.append("### A. Vertical metrics\n")
    parts.append(table(["Thông số", "Giá trị", "Tỷ lệ", "Quan hệ"], [
        ["UPM", upm, "1.000 em", "lưới TrueType chuẩn, đủ mịn cho overshoot và dấu"],
        ["Baseline", m.baseline, "0", "mọi chân nét phẳng đứng đúng 0"],
        ["x-height", m.xHeight, em(m.xHeight), f"x/cap = {m.xHeight / m.capHeight:.3f}"],
        ["Cap height", m.capHeight, em(m.capHeight), "chữ hoa, số lining"],
        ["Ascender (b d h l)", m.ascender, em(m.ascender), f"cao hơn cap {m.ascender - m.capHeight} để tách l khỏi I"],
        ["Descender (p q)", m.descender, em(-m.descender), ""],
        ["Overshoot tròn hoa / số", m.overshoot.capRound, f"{m.overshoot.capRound / m.capHeight:.1%} cap", "O, 0"],
        ["Overshoot tròn thường", m.overshoot.lowercaseRound, f"{m.overshoot.lowercaseRound / m.xHeight:.1%} x", "o c e s a b d p q"],
        ["Overshoot vai", m.overshoot.arch, f"{m.overshoot.arch / m.xHeight:.1%} x", "đỉnh vai n h m r, đáy u"],
        ["Typo ascender / descender / gap", f"{m.line.typoAscender} / {m.line.typoDescender} / {m.line.typoLineGap}",
         f"{(m.line.typoAscender - m.line.typoDescender) / upm:.3f} em", "line box mặc định; win metrics lấy từ bounds thật"],
    ]))
    parts.append("\n\n### B. Stroke system (Light, Regular, Medium, Bold)\n")
    S, BS = st.stemLower, bst.stemLower
    rows = [[key, lst[key], f"×{lst[key] / val:.2f}", val, f"{val / S:.3f}", ist[key], bst[key], f"{bst[key] / BS:.3f}", f"×{bst[key] / val:.2f}"]
            for key, val in st.items()]
    parts.append(table(["Tham số", "Light", "Light ÷ Regular", "Regular", "÷ stemLower", "Medium", "Bold", "÷ stemLower", "Bold ÷ Regular"], rows))
    for label, x in (("Light", lst), ("Regular", st), ("Medium", ist), ("Bold", bst)):
        parts.append(f"\n\n{label} — tương phản ngang/dọc: H {x.barUpper / x.stemUpper:.2f}, O {x.roundUpperTop / x.roundUpperSide:.2f}, "
                     f"o {x.roundLowerTop / x.roundLowerSide:.2f}, vai n {x.archTop / x.stemLower:.2f}. "
                     f"Bù quang học cạnh tròn: O +{x.roundUpperSide / x.stemUpper - 1:.1%} so với stem hoa, "
                     f"o +{x.roundLowerSide / x.stemLower - 1:.1%} so với stem thường.")
    parts.append(f"\n\nLight: {s.raw['masters']['Light']['comment']}")
    parts.append(f"\n\nBold: {s.raw['masters']['Bold']['comment']}")
    parts.append(f"\n\nMedium: {s.raw['instances']['comment']}")
    parts.append("\n\n### C. Curve tension\n")
    parts.append(table(["Tham số", "Giá trị", "Ghi chú"], [[key, val, ""] for key, val in k.items() if key != "comment"]))
    parts.append(f"\n\n{k.comment}")
    parts.append("\n\n### D. Shape ratios\n")
    same = lambda x, v: x if x != v else "="
    parts.append(table(["Tham số", "Light", "Regular", "Medium", "Bold"], [[key, same(lsh[key], val), val, same(ish[key], val), same(bsh[key], val)]
                                                                      for key, val in sh.items() if key != "comment"]))
    parts.append(f"\n\n{sh.comment}")
    parts.append("\n\n### E. Proportions (bề rộng thân)\n")
    parts.append(table(["Glyph/nhóm", "Light", "Regular", "÷ H", "÷ n", "Medium", "Bold", "Bold − Regular"], [
        [key, lw[key], val, f"{val / w.H:.3f}", f"{val / w.n:.3f}", iw[key], bw[key], f"{bw[key] - val:+d}"] for key, val in w.items() if key != "comment"
    ]))
    parts.append("\n\n### F. Spacing (sidebearing theo hình dạng cạnh)\n")
    groups = [("upperStraight", "upperStraight", "upperStraight"), ("upperRound", "upperRound", "upperStraight"),
              ("upperDiagonal", "upperDiagonal", "upperStraight"), ("lowerStraight (trái)", "lowerStraight", "lowerStraight"),
              ("lowerStraightRight (phải n h m)", "lowerStraightRight", "lowerStraight"), ("lowerRound", "lowerRound", "lowerStraight"),
              ("lowerTerminal (c)", "lowerTerminal", "lowerStraight")]
    parts.append(table(["Nhóm cạnh", "Light", "Regular", "÷ thẳng cùng loại", "Medium", "Bold", "÷ thẳng cùng loại"], [
        [label, lsp[key], sp[key], f"{sp[key] / sp[base]:.2f}", isp[key], bsp[key], f"{bsp[key] / bsp[base]:.2f}"] for label, key, base in groups
    ]))
    parts.append("\n\n### G. Đo trên font đã build (OTF)\n")
    for style in s.masters:
        otf = ROOT / "fonts" / "otf" / f"{s.meta.postscriptFamily}-{style}.otf"
        if not otf.exists():
            continue
        f = TTFont(otf)
        o = Outlines(f)
        cmap, hmtx = f.getBestCmap(), f["hmtx"]
        rows = []
        for ch in "HOIEAVNnohpdbqaecsrtumil012":
            name = cmap[ord(ch)]
            adv = hmtx[name][0]
            bb = o.bounds(ch)
            rows.append([ch, adv, round(bb[0]), round(adv - bb[2]), round(bb[1]), round(bb[3])])
        parts.append(f"\n{style}\n\n" + table(["Glyph", "Advance", "LSB", "RSB", "yMin", "yMax"], rows) + "\n")
    parts.append("\n\n### H. Đặc điểm nhận diện\n")
    parts.append(table(["Đặc điểm", "Quy tắc"], [[t["trait"], t["rule"]] for t in s.raw["identity"]]))
    return "\n".join(parts) + "\n"


def render(text: str) -> str:
    a, b = text.index(START) + len(START), text.index(END)
    return text[:a] + "\n\n" + generated() + "\n" + text[b:]


def main(argv) -> int:
    text = DOC.read_text(encoding="utf-8")
    new = render(text)
    if "--check" in argv:
        if new != text:
            print("FONT-DESIGN-SYSTEM.md is stale: run scripts/document.py")
            return 1
        print("FONT-DESIGN-SYSTEM.md is up to date")
        return 0
    DOC.write_text(new, encoding="utf-8")
    print(f"updated {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

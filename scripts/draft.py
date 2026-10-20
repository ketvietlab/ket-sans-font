"""Fast design loop: system -> UFO -> TTF (in-process) -> PNG proofs.

    .venv/bin/python scripts/draft.py [glyph names...]
    KETSANS_MASTER=Bold .venv/bin/python scripts/draft.py   (default Regular; also Medium)

Writes build/draft/ (ignored by git).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ufo2ft  # noqa: E402

from ketsans import glyphs as G  # noqa: E402
from ketsans import master, proof  # noqa: E402
from ketsans.system import ROOT  # noqa: E402

# Optional reference rows, e.g. KETSANS_REFS="SF=/tmp/sf.ttf,Inter=/tmp/inter.ttf" (static instances).
REFS = [tuple(item.split("=", 1)) for item in os.environ.get("KETSANS_REFS", "").split(",") if "=" in item]


def main(argv):
    out = ROOT / "build" / "draft"
    out.mkdir(parents=True, exist_ok=True)
    style = os.environ.get("KETSANS_MASTER", "Regular")
    font, _ = master.write(out / f"KETSans-{style}.ufo", style)
    ttf = ufo2ft.compileTTF(font, removeOverlaps=True, overlapsBackend="pathops", useProductionNames=False)
    ttf_path = out / f"KETSans-{style}.ttf"
    ttf.save(ttf_path)
    names = argv or [n for n in G.CORE if n not in (".notdef", "space")]
    names = [n for n in names if n in ttf.getGlyphOrder()]
    proof.glyph_sheet(ttf_path, names, out / "glyphs.png", cols=8)
    refs = [(label, proof.Face(path)) for label, path in REFS if Path(path).exists()]
    proof.text_proof(ttf_path, out / "text.png", sizes=(12, 14, 16, 24, 40), refs=refs)
    proof.text_proof(
        ttf_path, out / "viet.png", sizes=(16, 24, 56), refs=refs,
        lines=["Việt dẫn mại hòa liệu ỗ ợ ừ ặ ẳ đi", "ẦẤẨẪẬ ẰẮẲẴẶ ỒỐỔỖỘ ỜỚỞỠỢ ÉÈẺẼẸ ÍÌ"],
    )
    proof.text_proof(ttf_path, out / "kern.png", sizes=(48,), lines=["AVA VOV AVo Va Vo. r. HOHOH nonon"])
    print(out / "glyphs.png")


if __name__ == "__main__":
    main(sys.argv[1:])

"""Zip the built fonts with the licence for download.

    .venv/bin/python scripts/package.py      (after scripts/build.py)

Writes build/dist/KETSans-<version>.zip:

    KETSans-<version>/LICENSE.txt, README.txt, OTF/, TTF/, WOFF2/

Entries are sorted and stamped with the build's SOURCE_DATE_EPOCH, so the
same fonts give the same zip.  Sources stay out: the font is free to use,
not open source.
"""

from __future__ import annotations

import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build import SOURCE_DATE_EPOCH  # noqa: E402
from ketsans.system import ROOT, load  # noqa: E402

FORMATS = {"OTF": "otf", "TTF": "ttf", "WOFF2": "woff2"}


def main() -> None:
    version = load().meta.version
    top = f"KETSans-{version}"
    stamp = time.gmtime(int(SOURCE_DATE_EPOCH))[:6]
    files = {f"{top}/LICENSE.txt": (ROOT / "LICENSE.txt").read_bytes(),
             f"{top}/README.txt": (ROOT / "package" / "README.txt").read_text().replace("{version}", version).encode()}
    for folder, ext in FORMATS.items():
        for path in sorted((ROOT / "fonts" / ext).glob(f"*.{ext}")):
            files[f"{top}/{folder}/{path.name}"] = path.read_bytes()
    assert sum(name.endswith((".otf", ".ttf", ".woff2")) for name in files) == 12, "build all four weights first"
    out = ROOT / "build" / "dist" / f"{top}.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, stamp)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, files[name], compresslevel=9)
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size:,} bytes, {len(files)} files")


if __name__ == "__main__":
    main()

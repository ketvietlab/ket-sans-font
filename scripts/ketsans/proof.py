"""PNG proofs rendered from the real compiled font (FreeType + HarfBuzz).

Reference fonts are only rasterised side by side for comparison; nothing is
read from their outlines into KÉT Sans.
"""

from __future__ import annotations

from pathlib import Path

import freetype
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

LABEL_FONT = "/System/Library/Fonts/SFNSMono.ttf"


def _label_font(size=13):
    try:
        return ImageFont.truetype(LABEL_FONT, size)
    except OSError:  # pragma: no cover
        return ImageFont.load_default()


class Face:
    """A font loaded for shaping and rasterising, optionally at a variation."""

    def __init__(self, path: Path | str, variations: dict | None = None, index: int = 0):
        self.path = str(path)
        self.blob = hb.Blob.from_file_path(self.path)
        self.hb_face = hb.Face(self.blob, index)
        self.hb_font = hb.Font(self.hb_face)
        self.ft = freetype.Face(self.path, index)
        self.upem = self.hb_face.upem
        self.variations = variations or {}
        if self.variations:
            self.hb_font.set_variations(self.variations)
            axes = self.ft.get_variation_info().axes
            coords = []
            for ax in axes:
                tag = ax.tag if isinstance(ax.tag, str) else ax.tag.decode()
                coords.append(self.variations.get(tag, ax.default))
            self.ft.set_var_design_coords(coords)

    def shape(self, text: str, features: dict | None = None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb_font, buf, features or {"kern": True, "liga": True})
        return list(zip(buf.glyph_infos, buf.glyph_positions))

    def render_line(self, img: Image.Image, text: str, x: float, baseline: float, px: float, color=(17, 17, 17), hinting=False):
        scale = px / self.upem
        self.ft.set_char_size(int(px * 64), 0, 72, 72)
        flags = freetype.FT_LOAD_RENDER | (freetype.FT_LOAD_TARGET_LIGHT if hinting else freetype.FT_LOAD_NO_HINTING)
        pen_x = x
        for info, pos in self.shape(text):
            gx = pen_x + pos.x_offset * scale
            gy = baseline - pos.y_offset * scale
            # Sub-pixel x positioning via FreeType transform.
            frac = gx - int(gx)
            self.ft.set_transform(freetype.Matrix(0x10000, 0, 0, 0x10000), freetype.Vector(int(frac * 64), 0))
            self.ft.load_glyph(info.codepoint, flags)
            bm = self.ft.glyph.bitmap
            if bm.width and bm.rows:
                mask = Image.frombytes("L", (bm.width, bm.rows), bytes(bm.buffer)) if bm.pitch == bm.width else _bitmap_to_image(bm)
                left = int(gx) + self.ft.glyph.bitmap_left
                top = int(round(gy)) - self.ft.glyph.bitmap_top
                img.paste(Image.new("RGB", mask.size, color), (left, top), mask)
            pen_x += pos.x_advance * scale
        self.ft.set_transform(freetype.Matrix(0x10000, 0, 0, 0x10000), freetype.Vector(0, 0))
        return pen_x - x


def _bitmap_to_image(bm):
    rows = [bytes(bm.buffer[r * bm.pitch : r * bm.pitch + bm.width]) for r in range(bm.rows)]
    return Image.frombytes("L", (bm.width, bm.rows), b"".join(rows))


# --------------------------------------------------------------- glyph sheet
def glyph_sheet(ttf_path: Path, names, out: Path, cols=8, cell_em=0.13, show_points=True):
    font = TTFont(ttf_path)
    os2 = font["OS/2"]
    asc, desc = 1700, -560
    scale = cell_em
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]
    widths = [hmtx[n][0] for n in names]
    cell_w = int(max(widths) * scale) + 24
    cell_h = int((asc - desc) * scale) + 34
    rows = (len(names) + cols - 1) // cols
    img = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(img)
    lf = _label_font(12)
    xh, ch = os2.sxHeight, os2.sCapHeight
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    for i, name in enumerate(names):
        cx0 = (i % cols) * cell_w + 12
        cy0 = (i // cols) * cell_h + 22
        base = cy0 + asc * scale
        adv = hmtx[name][0]
        for y, col in [(0, (90, 140, 255)), (xh, (255, 160, 80)), (ch, (120, 200, 120)), (1520, (200, 200, 200)), (-420, (200, 200, 200))]:
            yy = base - y * scale
            draw.line([(cx0, yy), (cx0 + adv * scale, yy)], fill=col, width=1)
        draw.rectangle([cx0, cy0, cx0 + adv * scale, base - desc * scale], outline=(225, 225, 225))
        rec = DecomposingRecordingPen(gs)
        gs[name].draw(rec)
        polys = _record_to_polys(rec.value, lambda p: (cx0 + p[0] * scale, base - p[1] * scale))
        _fill_nonzero(img, polys)
        if show_points:
            _draw_points(draw, rec.value, lambda p: (cx0 + p[0] * scale, base - p[1] * scale))
        draw.text((cx0, cy0 - 18), f"{name} {adv}", fill=(80, 80, 80), font=lf)
    img.save(out)
    return out


def _record_to_polys(value, tf, steps=24):
    polys, cur = [], []
    last = None
    for op, args in value:
        if op == "moveTo":
            cur = [tf(args[0])]
            last = args[0]
        elif op == "lineTo":
            cur.append(tf(args[0]))
            last = args[0]
        elif op == "curveTo":
            p0 = last
            p1, p2, p3 = args
            for s in range(1, steps + 1):
                t = s / steps
                mt = 1 - t
                x = mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0]
                y = mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1]
                cur.append(tf((x, y)))
            last = p3
        elif op == "qCurveTo":
            # TrueType quadratic spline: expand implied on-curve points.
            pts = [last] + list(args)
            offs = pts[1:-1]
            on_pts = [pts[0]]
            segs = []
            for j, off in enumerate(offs):
                nxt = pts[-1] if j == len(offs) - 1 else ((off[0] + offs[j + 1][0]) / 2, (off[1] + offs[j + 1][1]) / 2)
                segs.append((on_pts[-1], off, nxt))
                on_pts.append(nxt)
            for a, b, c in segs:
                for s in range(1, steps + 1):
                    t = s / steps
                    mt = 1 - t
                    cur.append(tf((mt * mt * a[0] + 2 * mt * t * b[0] + t * t * c[0], mt * mt * a[1] + 2 * mt * t * b[1] + t * t * c[1])))
            last = pts[-1]
        elif op in ("closePath", "endPath"):
            if cur:
                polys.append(cur)
            cur = []
    return polys


def _fill_nonzero(img, polys, color=(20, 20, 20)):
    """Non-zero fill using a winding-number scanline (small, exact enough)."""
    if not polys:
        return
    import numpy as np

    w, h = img.size
    ys = [p[1] for poly in polys for p in poly]
    y0, y1 = max(0, int(min(ys))), min(h - 1, int(max(ys)) + 1)
    arr = np.array(img)
    edges = []
    for poly in polys:
        for a, b in zip(poly, poly[1:] + poly[:1]):
            if a[1] != b[1]:
                edges.append((a, b))
    for y in range(y0, y1 + 1):
        sy = y + 0.5
        xs = []
        for a, b in edges:
            if (a[1] <= sy < b[1]) or (b[1] <= sy < a[1]):
                x = a[0] + (sy - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
                xs.append((x, 1 if b[1] > a[1] else -1))
        xs.sort()
        wind = 0
        for j, (x, d) in enumerate(xs):
            prev = wind
            wind += d
            if prev == 0 and wind != 0:
                start = x
            elif prev != 0 and wind == 0:
                xa, xb = int(round(start)), int(round(x))
                arr[y, max(0, xa) : min(w, xb)] = color
    img.paste(Image.fromarray(arr))


def _draw_points(draw, value, tf):
    last = None
    for op, args in value:
        if op == "moveTo" or op == "lineTo":
            p = tf(args[0])
            draw.rectangle([p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2], fill=(230, 60, 60))
            last = args[0]
        elif op == "curveTo":
            p1, p2, p3 = (tf(a) for a in args)
            l0 = tf(last)
            draw.line([l0, p1], fill=(80, 170, 255), width=1)
            draw.line([p3, p2], fill=(80, 170, 255), width=1)
            for c in (p1, p2):
                draw.ellipse([c[0] - 2, c[1] - 2, c[0] + 2, c[1] + 2], outline=(80, 170, 255))
            draw.ellipse([p3[0] - 2.5, p3[1] - 2.5, p3[0] + 2.5, p3[1] + 2.5], fill=(230, 60, 60))
            last = args[-1]


# ---------------------------------------------------------------- text proofs
CORE_WORDS = [
    "Hamburg nonhoh odobop hamburgefontsiv",
    "minimum nhân viên học bạn đọc",
    "dashboard pitch notes adds",
    "HAVEN NOVA OVEN 1200 2021",
]


def text_proof(ttf_path: Path, out: Path, lines=None, sizes=(11, 12, 13, 14, 16, 20, 24, 32, 48), refs=None):
    lines = lines or ["nonhoh adhesion dapper", "doanh thu tuan nay", "HAVEN NOVA 1210 2012"]
    faces = [("KÉT", Face(ttf_path))] + list(refs or [])
    lf = _label_font(11)
    rows = []
    for px in sizes:
        for label, face in faces:
            rows.append((px, label, face))
    height = sum(int(px * 1.6) + 6 for px, _, _ in rows) + 20
    img = Image.new("RGB", (1500, height), "white")
    draw = ImageDraw.Draw(img)
    y = 10
    for px, label, face in rows:
        lh = int(px * 1.6) + 6
        baseline = y + px * 1.15
        draw.text((8, y + 2), f"{label} {px}", fill=(150, 150, 150), font=lf)
        face.render_line(img, "  ".join(lines), 110, baseline, px)
        y += lh
    img.save(out)
    return out

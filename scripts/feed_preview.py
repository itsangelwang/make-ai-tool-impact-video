#!/usr/bin/env python3
"""Show covers at the size viewers actually see them in a feed, next to the platform's title text.

Usage:
  python3 feed_preview.py qa/cover-9x16.png@108 qa/cover-3x4.png@95 \
      --title "ChatGPT just added …" -o qa/feed-preview.png

- Each argument is a cover file, optionally `label=path` and `@N`, where N is the height in
  pixels of one headline line's letters in the 1080-wide cover (about 0.72 x the font size for
  English capitals, 0.92 x for Chinese). With it the report says how big that line appears in
  each slot and how it compares with the title text beside it.
- 9:16 covers go into the YouTube Shorts shelf and the TikTok / Instagram profile grids (which
  crop the centre 3:4); 3:4 covers go into the Xiaohongshu feed (a 9:16 cover is centre-cropped
  there when no 3:4 cover is given). Other ratios are skipped.
- The sheet is drawn at 2x, so on a Retina screen it is close to real size.

Slot sizes below are estimates for a 393-point-wide phone (2026-11), not measurements. Re-measure
in the live apps when a platform changes its layout, and update the constants.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

K = 2  # pixels per point
# (name, width in points, crop, title size in points or None when the slot shows no title)
SLOTS_916 = [
    ("YouTube Shorts shelf", 180, "9:16", 14),
    ("TikTok profile grid", 130, "3:4", None),
    ("Instagram profile grid", 130, "3:4", None),
]
SLOT_34 = ("Xiaohongshu feed", 190, "3:4", 14)
COMPARE_TITLE_PT = 14  # grids without a title are compared with ordinary 14-point UI text
FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/SFNS.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def parse_cover(arg: str):
    label, _, rest = arg.rpartition("=") if "=" in arg else ("", "", arg)
    path, _, ink = rest.partition("@")
    path = Path(path)
    return (label or path.stem), path, (float(ink) if ink else None)


def ratio_of(image: Image.Image) -> str | None:
    r = image.width / image.height
    if abs(r - 9 / 16) < 0.02:
        return "9:16"
    if abs(r - 3 / 4) < 0.02:
        return "3:4"
    return None


def crop_34(image: Image.Image) -> Image.Image:
    """Centre 3:4 band of a taller cover, the part profile grids show."""
    h = round(image.width * 4 / 3)
    if image.height <= h:
        return image
    top = (image.height - h) // 2
    return image.crop((0, top, image.width, top + h))


def apparent_pt(ink_px: float, source_width: int, slot_width_pt: float) -> float:
    """How tall one line's letters look, in points, at the slot's width."""
    return ink_px * slot_width_pt / source_width


def plan(covers):
    """List (label, slot name, slot width, crop, title pt, image, ink) for every cover and slot it fits."""
    rows = []
    have_34 = any(ratio_of(img) == "3:4" for _, img, _ in covers)
    for label, img, ink in covers:
        r = ratio_of(img)
        if r == "9:16":
            for name, width, crop, title in SLOTS_916:
                rows.append((label, name, width, crop, title, img, ink))
            if not have_34:
                rows.append((label, *SLOT_34, img, ink))
        elif r == "3:4":
            rows.append((label, *SLOT_34, img, ink))
    return rows


def report_line(label, name, width, title, img, ink) -> str:
    if ink is None:
        return f"{label} · {name}: {width} pt wide"
    pt = apparent_pt(ink, img.width, width)
    ref = title or COMPARE_TITLE_PT
    flag = "ok" if pt >= ref * 1.3 else "TOO SMALL: make it clearly bigger than the title text"
    return f"{label} · {name}: headline letters ≈ {pt:.1f} pt, {pt / ref:.1f}× the {ref} pt title text ({flag})"


def load_font(size: int, path: str | None):
    for candidate in ([path] if path else []) + FONT_CANDIDATES:
        try:
            return ImageFont.truetype(candidate, size)
        except (OSError, TypeError):
            continue
    return ImageFont.load_default()


def draw_sheet(rows, title_text: str, font_path: str | None) -> Image.Image:
    pad = 24 * K
    cells = []
    for label, name, width, crop, title, img, _ in rows:
        shown = crop_34(img) if crop == "3:4" else img
        w = width * K
        h = round(w * shown.height / shown.width)
        thumb = shown.convert("RGB").resize((w, h), Image.LANCZOS)
        cells.append((label, name, title, thumb))
    col_w = max(c[3].width for c in cells) + pad
    height = max(c[3].height for c in cells) + 110 * K
    sheet = Image.new("RGB", (pad + col_w * len(cells), height + pad), "white")
    draw = ImageDraw.Draw(sheet)
    small = load_font(11 * K, font_path)
    for i, (label, name, title, thumb) in enumerate(cells):
        x = pad + i * col_w
        draw.text((x, pad // 2), f"{name} · {label}", fill="#555", font=small)
        y = pad + 18 * K
        sheet.paste(thumb, (x, y))
        if title:
            font = load_font(title * K, font_path)
            text = title_text
            while text and draw.textlength(text, font=font) > thumb.width:
                text = text[:-2] + "…" if len(text) > 2 else ""
            draw.text((x, y + thumb.height + 6 * K), text, fill="#111", font=font)
    return sheet


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("covers", nargs="+", help="cover image, as [label=]path[@ink_px]")
    parser.add_argument("--title", default="Video title shown next to the cover", help="title text drawn beside the cover")
    parser.add_argument("--font", help="font file for the title text")
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)

    covers = []
    for arg in args.covers:
        label, path, ink = parse_cover(arg)
        if not path.is_file():
            print(f"Missing cover: {path}", file=sys.stderr)
            return 2
        img = Image.open(path)
        if ratio_of(img) is None:
            print(f"Skipped {path}: not 9:16 or 3:4 ({img.width}×{img.height})", file=sys.stderr)
            continue
        covers.append((label, img, ink))
    rows = plan(covers)
    if not rows:
        print("No 9:16 or 3:4 cover to preview.", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    draw_sheet(rows, args.title, args.font).save(args.output)
    small = False
    for label, name, width, _, title, img, ink in rows:
        line = report_line(label, name, width, title, img, ink)
        small = small or "TOO SMALL" in line
        print(line)
    print(f"Preview: {args.output}")
    return 1 if small else 0


if __name__ == "__main__":
    raise SystemExit(main())

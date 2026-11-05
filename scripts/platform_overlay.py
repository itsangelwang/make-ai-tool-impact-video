#!/usr/bin/env python3
"""Lay rough YouTube Shorts, TikTok and Instagram Reels interface zones over 9:16 stills.

Usage:
  python3 platform_overlay.py qa/still-s3.png qa/still-s5.png -o qa/platform-overlay.png

For each still it draws one panel per platform with the top bar, the right-hand button rail
and the bottom account/caption area shaded, and prints how much of each zone is covered by
non-background pixels (a hint, not a verdict: look at the sheet). The overlay never goes into
the video.

Zones are estimates in 1080×1920 pixels (2026-11), not official safe areas. Re-check them
against the live apps when a platform changes its layout, and update ZONES.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

# (label, x0, y0, x1, y1) in 1080×1920
ZONES = {
    "YouTube Shorts": [("top bar", 0, 0, 1080, 170), ("buttons", 920, 880, 1080, 1700), ("title & channel", 0, 1480, 920, 1760), ("nav", 0, 1760, 1080, 1920)],
    "TikTok": [("top tabs", 0, 0, 1080, 200), ("buttons", 900, 860, 1080, 1640), ("account & caption", 0, 1460, 900, 1780), ("nav", 0, 1780, 1080, 1920)],
    "Instagram Reels": [("top bar", 0, 0, 1080, 180), ("buttons", 920, 1000, 1080, 1720), ("account & caption", 0, 1540, 920, 1790), ("nav", 0, 1790, 1080, 1920)],
}
SIZE = (1080, 1920)


def busy_share(image: Image.Image, box) -> float:
    """Share of a zone whose pixels differ clearly from the zone's most common colour."""
    region = image.crop(box[1:]).convert("RGB").resize((max(1, (box[3] - box[1]) // 8), max(1, (box[4] - box[2]) // 8)))
    colours = region.getcolors(region.width * region.height) or []
    if not colours:
        return 0.0
    _, background = max(colours)
    diff = ImageChops.difference(region, Image.new("RGB", region.size, background)).convert("L")
    busy = sum(diff.histogram()[41:])
    return busy / (region.width * region.height)


def label_font():
    try:
        return ImageFont.load_default(size=40)
    except TypeError:  # Pillow older than 10.1
        return ImageFont.load_default()


def panel(image: Image.Image, platform: str) -> Image.Image:
    base = image.convert("RGBA").resize(SIZE)
    layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font = label_font()
    for label, x0, y0, x1, y1 in ZONES[platform]:
        draw.rectangle((x0, y0, x1, y1), fill=(230, 40, 60, 70), outline=(230, 40, 60, 220), width=4)
        draw.text((x0 + 14, y0 + 10), label, fill=(160, 0, 20, 255), font=font)
    draw.text((24, SIZE[1] // 2), platform, fill=(160, 0, 20, 255), font=font)
    return Image.alpha_composite(base, layer).convert("RGB")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stills", nargs="+", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)

    panels = []
    for path in args.stills:
        if not path.is_file():
            print(f"Missing still: {path}", file=sys.stderr)
            return 2
        image = Image.open(path)
        if abs(image.width / image.height - 9 / 16) > 0.02:
            print(f"Skipped {path}: not 9:16", file=sys.stderr)
            continue
        scaled = image.convert("RGB").resize(SIZE)
        for platform, zones in ZONES.items():
            panels.append(panel(image, platform))
            for zone in zones:
                if zone[0] == "nav":
                    continue
                share = busy_share(scaled, zone)
                if share > 0.05:
                    print(f"{path.name} · {platform} · {zone[0]}: {share:.0%} of the zone has content under it")
    if not panels:
        print("No 9:16 still to check.", file=sys.stderr)
        return 2
    scale = 0.3
    w, h = round(SIZE[0] * scale), round(SIZE[1] * scale)
    per_row = len(ZONES)
    rows = (len(panels) + per_row - 1) // per_row
    sheet = Image.new("RGB", (per_row * (w + 16) + 16, rows * (h + 16) + 16), "white")
    for i, item in enumerate(panels):
        sheet.paste(item.resize((w, h)), (16 + (i % per_row) * (w + 16), 16 + (i // per_row) * (h + 16)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    print(f"Overlay sheet: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

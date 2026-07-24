#!/usr/bin/env python3
"""Extract a dominant-color palette (with hex + role hints) from a UI screenshot.

Usage:
    python3 extract_colors.py IMAGE_PATH [--colors N]

The script quantizes colors, ranks them by frequency, and labels each by a simple
luminance/saturation heuristic (background / surface / primary / text / accent) so the
caller can wire exact hex values into a generated UI prompt.
"""
import argparse
import collections
import sys


def ensure_pil():
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def hex_of(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def label(rgb, sat):
    r, g, b = rgb
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if lum >= 235:
        return "background（背景/留白）"
    if lum >= 200:
        return "surface（浅色面/卡片）"
    if lum <= 60:
        return "text（文字/深描边）"
    if sat >= 60:
        return "accent（强调色）"
    return "primary（主色/中性面）"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--colors", type=int, default=6)
    args = ap.parse_args()

    if not ensure_pil():
        print("ERROR: Pillow is required. Install it first with `python3 -m pip install pillow`.")
        sys.exit(1)

    from PIL import Image

    img = Image.open(args.image).convert("RGB")
    # Downscale for speed; color distribution is enough at small size.
    small = img.resize((max(1, img.width // 4), max(1, img.height // 4)))
    pixels = list(small.getdata())
    total = len(pixels)

    # Quantize to 5 bits per channel (32 levels) to merge near-identical colors.
    buckets = collections.defaultdict(lambda: [0, 0, 0, 0])  # count, r, g, b
    for r, g, b in pixels:
        key = (r // 8 * 8 + 4, g // 8 * 8 + 4, b // 8 * 8 + 4)
        bk = buckets[key]
        bk[0] += 1
        bk[1] += r
        bk[2] += g
        bk[3] += b

    averaged = []
    for (rr, gg, bb), (cnt, sr, sg, sb) in buckets.items():
        averaged.append((cnt, (sr // cnt, sg // cnt, sb // cnt)))

    averaged.sort(key=lambda x: x[0], reverse=True)
    top = averaged[: args.colors]

    print(f"Palette for: {args.image}  (sampled {total} px, top {len(top)})\n")
    for i, (cnt, rgb) in enumerate(top, 1):
        pct = 100.0 * cnt / total
        r, g, b = rgb
        mx = max(r, g, b)
        mn = min(r, g, b)
        sat = 0 if mx == 0 else int(255 * (mx - mn) / mx)
        print(
            f"{i}. {hex_of(rgb)}  rgb({r:>3},{g:>3},{b:>3})  "
            f"占比 {pct:5.1f}%  -> {label(rgb, sat)}"
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Convert a black/white halftone raster image into an SVG made of exact
square rects -- one per pixel run -- instead of vector-tracing curves.

This preserves pixel-perfect square edges (no smoothing, no curve fitting).

Usage:
    python halftone_to_svg.py input.png output.svg [--threshold 128] [--scale 1] [--invert]

By default: pixels considered "on" (kept, drawn) are the WHITE ones,
matching "white is the color I want to keep." Use --invert if your
image has that backwards.
"""

import sys
import argparse
from PIL import Image


def build_svg(img: Image.Image, threshold: int, scale: int, invert: bool) -> str:
    img = img.convert("L")  # grayscale
    w, h = img.size
    px = img.load()

    # Decide "on" mask: True = keep/draw this pixel
    def is_on(x, y):
        v = px[x, y]
        on = v >= threshold  # white-ish
        return (not on) if invert else on

    rects = []
    for y in range(h):
        x = 0
        while x < w:
            if is_on(x, y):
                run_start = x
                while x < w and is_on(x, y):
                    x += 1
                run_len = x - run_start
                rects.append(
                    f'<rect x="{run_start * scale}" y="{y * scale}" '
                    f'width="{run_len * scale}" height="{scale}"/>'
                )
            else:
                x += 1

    svg_w = w * scale
    svg_h = h * scale

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}" '
        f'shape-rendering="crispEdges">\n'
        f'<g fill="#ffffff">\n' + "\n".join(rects) + "\n</g>\n</svg>\n"
    )
    return svg


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--threshold", type=int, default=128,
                     help="Grayscale cutoff (0-255) for 'white'. Default 128.")
    ap.add_argument("--scale", type=int, default=1,
                     help="Size of each pixel's square in output SVG units. Default 1.")
    ap.add_argument("--invert", action="store_true",
                     help="Invert which color counts as 'on' (use if black should be kept instead).")
    args = ap.parse_args()

    img = Image.open(args.input)
    svg = build_svg(img, args.threshold, args.scale, args.invert)

    with open(args.output, "w") as f:
        f.write(svg)

    print(f"Wrote {args.output} ({img.size[0]}x{img.size[1]} source pixels)")


if __name__ == "__main__":
    main()

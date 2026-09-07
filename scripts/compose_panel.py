#!/usr/bin/env python3
"""Pixel-preserving sizing and 50:50 composition for Bollywood Panel.

This script never invents the design. It only:
  - resizes a finished raster to an exact size
  - composites a source photograph with a design half at a strict 50:50 split
  - audits whether an existing comparison image is split 50:50
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.stderr.write("Pillow is required: python3 -m pip install pillow\n")
    raise SystemExit(1)


RATIOS = {
    "1:1": (1, 1),
    "3:4": (3, 4),
    "4:3": (4, 3),
    "4:5": (4, 5),
    "5:4": (5, 4),
    "2:3": (2, 3),
    "3:2": (3, 2),
    "9:16": (9, 16),
    "16:9": (16, 9),
    "21:9": (21, 9),
    "5:7": (5, 7),
    "7:5": (7, 5),
}


def parse_size(value: str) -> tuple[int, int]:
    if "x" in value.lower():
        width_s, height_s = value.lower().split("x", 1)
        return int(width_s), int(height_s)
    if value not in RATIOS:
        raise argparse.ArgumentTypeError(f"unknown size {value!r}")
    rw, rh = RATIOS[value]
    long_edge = 2048
    if rw >= rh:
        width = long_edge
        height = round(long_edge * rh / rw)
    else:
        height = long_edge
        width = round(long_edge * rw / rh)
    return width, height


def cover_resize(image: Image.Image, width: int, height: int) -> Image.Image:
    source = image.convert("RGBA")
    scale = max(width / source.width, height / source.height)
    resized = source.resize(
        (max(1, round(source.width * scale)), max(1, round(source.height * scale))),
        Image.Resampling.LANCZOS,
    )
    left = max(0, (resized.width - width) // 2)
    top = max(0, (resized.height - height) // 2)
    return resized.crop((left, top, left + width, top + height))


def compose(args: argparse.Namespace) -> None:
    source = Image.open(args.source)
    design = Image.open(args.design)
    width, height = parse_size(args.size) if args.size else (
        (source.width, source.height * 2)
        if args.mode == "top-bottom"
        else (source.width * 2, source.height)
    )

    canvas = Image.new("RGBA", (width, height))
    if args.mode == "top-bottom":
        half = height // 2
        canvas.paste(cover_resize(source, width, half), (0, 0))
        canvas.paste(cover_resize(design, width, height - half), (0, half))
    else:
        half = width // 2
        canvas.paste(cover_resize(source, half, height), (0, 0))
        canvas.paste(cover_resize(design, width - half, height), (half, 0))

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, "PNG")
    print(output)


def resize(args: argparse.Namespace) -> None:
    image = Image.open(args.input)
    width, height = parse_size(args.size)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    cover_resize(image, width, height).convert("RGB").save(output, "PNG")
    print(output)


def audit(args: argparse.Namespace) -> None:
    image = Image.open(args.input)
    width, height = image.size
    if args.mode == "top-bottom":
        expected = height / 2
        print(f"height={height} midpoint={expected:.1f} exact={height % 2 == 0}")
    else:
        expected = width / 2
        print(f"width={width} midpoint={expected:.1f} exact={width % 2 == 0}")
    print(f"ratio={width}:{height} file={args.input}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    compose_p = sub.add_parser("compose", help="Strict 50:50 source + design composite")
    compose_p.add_argument("--mode", choices=("top-bottom", "left-right"), required=True)
    compose_p.add_argument("--source", required=True)
    compose_p.add_argument("--design", required=True)
    compose_p.add_argument("--out", required=True)
    compose_p.add_argument("--size", help="ratio like 3:4 or pixels like 1536x2048")
    compose_p.set_defaults(func=compose)

    resize_p = sub.add_parser("resize", help="Cover-resize a finished raster")
    resize_p.add_argument("--input", required=True)
    resize_p.add_argument("--size", required=True)
    resize_p.add_argument("--out", required=True)
    resize_p.set_defaults(func=resize)

    audit_p = sub.add_parser("audit", help="Read-only split and size report")
    audit_p.add_argument("--mode", choices=("top-bottom", "left-right"), required=True)
    audit_p.add_argument("--input", required=True)
    audit_p.set_defaults(func=audit)

    return parser


def main() -> None:
    parser = build_parser()
    # Also accept the flat flag form used in SKILL.md
    raw = sys.argv[1:]
    if raw and not raw[0] in {"compose", "resize", "audit"} and "--source" in raw:
        sys.argv = [sys.argv[0], "compose", *raw]
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

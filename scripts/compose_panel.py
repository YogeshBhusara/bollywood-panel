#!/usr/bin/env python3
"""Pixel-preserving sizing, 50:50 composition, and audits for Bollywood Panel.

This script never invents the design. Subcommands:

  half     Report the canvas and design-half geometry for a mode + size, plus the
           closest GenerateImage aspect ratio to request for the design half.
  compose  Place the untouched source photograph and a generated design half on
           one canvas at an exact 50:50 split.
  resize   Cover-resize a finished raster to an exact ratio or pixel size.
  audit    Read-only: measure where the visual seam actually is versus the
           midpoint, and report the canvas ratio.

Requires Pillow. HEIC/HEIF sources additionally need pillow-heif.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageOps, UnidentifiedImageError
except ImportError:  # pragma: no cover - dependency guard
    sys.stderr.write("Pillow is required: python3 -m pip install -r scripts/requirements.txt\n")
    raise SystemExit(1)

try:  # optional HEIC support
    import pillow_heif  # type: ignore

    pillow_heif.register_heif_opener()
except ImportError:  # pragma: no cover - optional
    pillow_heif = None


DEFAULT_LONG_EDGE = 2048
COMPARISON_MODES = ("top-bottom", "left-right")
GENERATE_IMAGE_RATIOS = {
    "1:1": 1.0,
    "4:3": 4 / 3,
    "3:4": 3 / 4,
    "16:9": 16 / 9,
    "9:16": 9 / 16,
}


class PanelError(Exception):
    """User-facing failure with a clean message and no traceback."""


# --------------------------------------------------------------------------- geometry


def parse_ratio(value: str) -> tuple[int, int]:
    """Accept any 'W:H' ratio of positive integers."""
    try:
        w_s, h_s = value.split(":", 1)
        w, h = int(w_s), int(h_s)
    except ValueError:
        raise PanelError(f"size {value!r} must look like 3:4 or 1536x2048")
    if w <= 0 or h <= 0:
        raise PanelError(f"ratio {value!r} must use positive integers")
    return w, h


def parse_size(value: str, long_edge: int = DEFAULT_LONG_EDGE) -> tuple[int, int]:
    """'WxH' returns exact pixels; 'W:H' scales the ratio to the long edge."""
    lowered = value.lower().strip()
    if "x" in lowered:
        try:
            w_s, h_s = lowered.split("x", 1)
            width, height = int(w_s), int(h_s)
        except ValueError:
            raise PanelError(f"pixel size {value!r} must look like 1536x2048")
        if width <= 0 or height <= 0:
            raise PanelError(f"pixel size {value!r} must be positive")
        return width, height

    rw, rh = parse_ratio(lowered)
    if rw >= rh:
        return long_edge, max(1, round(long_edge * rh / rw))
    return max(1, round(long_edge * rw / rh)), long_edge


def snap_even(width: int, height: int, mode: str) -> tuple[int, int, bool]:
    """Force the split axis to an even length so the midpoint is a whole pixel."""
    if mode == "top-bottom" and height % 2:
        return width, height - 1, True
    if mode == "left-right" and width % 2:
        return width - 1, height, True
    return width, height, False


def reduced_ratio(width: int, height: int) -> str:
    g = math.gcd(width, height)
    return f"{width // g}:{height // g}"


def closest_generate_ratio(width: int, height: int) -> tuple[str, float]:
    """Return the GenerateImage aspect_ratio nearest to width/height and the crop loss."""
    target = width / height
    best = min(GENERATE_IMAGE_RATIOS.items(), key=lambda kv: abs(math.log(kv[1]) - math.log(target)))
    name, ratio = best
    # Fraction of the generated image lost when cover-cropping to the target ratio.
    loss = 1 - min(ratio / target, target / ratio)
    return name, loss


def half_geometry(mode: str, size: str, long_edge: int) -> dict:
    width, height = parse_size(size, long_edge)
    width, height, snapped = snap_even(width, height, mode)
    if mode == "top-bottom":
        half_w, half_h = width, height // 2
    elif mode == "left-right":
        half_w, half_h = width // 2, height
    else:
        half_w, half_h = width, height
    aspect, loss = closest_generate_ratio(half_w, half_h)
    return {
        "mode": mode,
        "canvas": {"width": width, "height": height, "ratio": reduced_ratio(width, height)},
        "design_region": {"width": half_w, "height": half_h, "ratio": reduced_ratio(half_w, half_h)},
        "generate_image_aspect_ratio": aspect,
        "cover_crop_loss": round(loss, 3),
        "snapped_even": snapped,
    }


# --------------------------------------------------------------------------- raster io


def open_image(path: str) -> Image.Image:
    file = Path(path).expanduser()
    if not file.is_file():
        raise PanelError(f"file not found: {file}")
    try:
        image = Image.open(file)
        image.load()
    except UnidentifiedImageError:
        hint = ""
        if file.suffix.lower() in {".heic", ".heif"} and pillow_heif is None:
            hint = " (HEIC needs: python3 -m pip install pillow-heif)"
        raise PanelError(f"cannot decode {file}{hint}")
    # Respect camera orientation so phone photos are not composed rotated.
    return ImageOps.exif_transpose(image) or image


def cover_resize(image: Image.Image, width: int, height: int) -> Image.Image:
    """Scale to fill width x height, then centre-crop. Never stretches."""
    source = image.convert("RGBA")
    scale = max(width / source.width, height / source.height)
    resized = source.resize(
        (max(width, round(source.width * scale)), max(height, round(source.height * scale))),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def save_png(image: Image.Image, out: str, icc_profile: bytes | None) -> Path:
    output = Path(out).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"icc_profile": icc_profile} if icc_profile else {}
    image.convert("RGB").save(output, "PNG", **kwargs)
    return output


# --------------------------------------------------------------------------- commands


def cmd_half(args: argparse.Namespace) -> None:
    print(json.dumps(half_geometry(args.mode, args.size, args.long_edge), indent=2))


def cmd_compose(args: argparse.Namespace) -> None:
    source = open_image(args.source)
    design = open_image(args.design)

    if args.size:
        width, height = parse_size(args.size, args.long_edge)
    elif args.mode == "top-bottom":
        width, height = source.width, source.height * 2
    else:
        width, height = source.width * 2, source.height
    width, height, snapped = snap_even(width, height, args.mode)

    canvas = Image.new("RGBA", (width, height))
    if args.mode == "top-bottom":
        half = height // 2
        canvas.paste(cover_resize(source, width, half), (0, 0))
        canvas.paste(cover_resize(design, width, half), (0, half))
    else:
        half = width // 2
        canvas.paste(cover_resize(source, half, height), (0, 0))
        canvas.paste(cover_resize(design, half, height), (half, 0))

    output = save_png(canvas, args.out, source.info.get("icc_profile"))
    report = {
        "out": str(output),
        "canvas": {"width": width, "height": height, "ratio": reduced_ratio(width, height)},
        "split_at": half,
        "snapped_even": snapped,
    }
    print(json.dumps(report, indent=2))


def cmd_resize(args: argparse.Namespace) -> None:
    image = open_image(args.input)
    width, height = parse_size(args.size, args.long_edge)
    output = save_png(cover_resize(image, width, height), args.out, image.info.get("icc_profile"))
    print(json.dumps({"out": str(output), "width": width, "height": height}, indent=2))


def detect_seam(image: Image.Image, mode: str) -> tuple[int, float]:
    """Return (boundary_index, confidence) for the strongest row/column discontinuity."""
    grey = image.convert("L")
    if mode == "top-bottom":
        # Collapse width so each row is one mean value, then diff adjacent rows.
        strip = grey.resize((1, grey.height), Image.Resampling.BOX)
        a = strip.crop((0, 0, 1, strip.height - 1))
        b = strip.crop((0, 1, 1, strip.height))
    else:
        strip = grey.resize((grey.width, 1), Image.Resampling.BOX)
        a = strip.crop((0, 0, strip.width - 1, 1))
        b = strip.crop((1, 0, strip.width, 1))
    diffs = list(ImageChops.difference(a, b).getdata())
    if not diffs:
        return 0, 0.0
    peak = max(range(len(diffs)), key=diffs.__getitem__)
    ordered = sorted(diffs)
    median = ordered[len(ordered) // 2] or 1
    return peak + 1, diffs[peak] / median


def cmd_audit(args: argparse.Namespace) -> None:
    image = open_image(args.input)
    width, height = image.size
    report: dict = {
        "file": str(Path(args.input).expanduser()),
        "width": width,
        "height": height,
        "ratio": reduced_ratio(width, height),
    }
    if args.mode in COMPARISON_MODES:
        axis_len = height if args.mode == "top-bottom" else width
        seam, confidence = detect_seam(image, args.mode)
        expected = axis_len // 2
        offset = seam - expected
        report.update(
            {
                "mode": args.mode,
                "expected_midpoint": expected,
                "detected_seam": seam,
                "offset_px": offset,
                "seam_confidence": round(confidence, 1),
                "axis_even": axis_len % 2 == 0,
                "ok": axis_len % 2 == 0 and abs(offset) <= args.tolerance,
            }
        )
    else:
        report.update({"mode": args.mode, "ok": True})
    print(json.dumps(report, indent=2))
    if not report["ok"]:
        raise SystemExit(3)


# --------------------------------------------------------------------------- cli


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--long-edge",
        type=int,
        default=DEFAULT_LONG_EDGE,
        help=f"long edge in pixels when a ratio is given (default {DEFAULT_LONG_EDGE})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    half_p = sub.add_parser("half", help="geometry of the design region for a mode + size")
    half_p.add_argument("--mode", choices=(*COMPARISON_MODES, "design-only"), required=True)
    half_p.add_argument("--size", required=True, help="ratio like 3:4 or pixels like 1536x2048")
    half_p.set_defaults(func=cmd_half)

    compose_p = sub.add_parser("compose", help="exact 50:50 source + design composite")
    compose_p.add_argument("--mode", choices=COMPARISON_MODES, required=True)
    compose_p.add_argument("--source", required=True, help="original photograph")
    compose_p.add_argument("--design", required=True, help="generated Bollywood design half")
    compose_p.add_argument("--out", required=True)
    compose_p.add_argument("--size", help="ratio like 3:4 or pixels like 1536x2048")
    compose_p.set_defaults(func=cmd_compose)

    resize_p = sub.add_parser("resize", help="cover-resize a finished raster")
    resize_p.add_argument("--input", required=True)
    resize_p.add_argument("--size", required=True)
    resize_p.add_argument("--out", required=True)
    resize_p.set_defaults(func=cmd_resize)

    audit_p = sub.add_parser("audit", help="read-only seam and size report")
    audit_p.add_argument("--mode", choices=(*COMPARISON_MODES, "design-only"), required=True)
    audit_p.add_argument("--input", required=True)
    audit_p.add_argument("--tolerance", type=int, default=1, help="allowed seam offset in px")
    audit_p.set_defaults(func=cmd_audit)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except PanelError as exc:
        sys.stderr.write(f"error: {exc}\n")
        raise SystemExit(2)


if __name__ == "__main__":
    main()

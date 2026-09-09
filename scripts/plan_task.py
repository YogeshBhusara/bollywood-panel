#!/usr/bin/env python3
"""Inventory sources and create one fresh task directory with collision-safe filenames.

Given a single image or a directory, this script:
  - lists supported rasters recursively in stable (sorted) order
  - reads each source's oriented width/height
  - resolves 'auto' and 'source' sizes per image
  - creates ONE flat task directory under the output root
  - prints a JSON plan: every source x mode x size (x device) with its output
    filename and the GenerateImage aspect ratio to request

It never generates images and never reads or writes anything outside the task
directory it creates.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compose_panel import (  # noqa: E402
    COMPARISON_MODES,
    PanelError,
    half_geometry,
    open_image,
    reduced_ratio,
)

SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp", ".heic", ".heif"}
MODES = (*COMPARISON_MODES, "design-only", "wallpaper-pack")
DEVICES = {"phone": "9:16", "tablet": "4:3", "desktop": "16:9", "watch": "1:1"}
DEFAULT_ROOT = Path("~/Desktop/bollywood-panel")


def slug(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return cleaned or "image"


def split_list(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        out.extend(v.strip() for v in value.split(",") if v.strip())
    # de-duplicate while preserving order
    return list(dict.fromkeys(out))


def inventory(source: Path) -> list[Path]:
    source = source.expanduser()
    if source.is_file():
        if source.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise PanelError(f"unsupported image type: {source.suffix}")
        return [source]
    if source.is_dir():
        files = [
            p
            for p in sorted(source.rglob("*"))
            if p.is_file()
            and p.suffix.lower() in SUPPORTED_SUFFIXES
            and not any(part.startswith(".") for part in p.relative_to(source).parts)
        ]
        if not files:
            raise PanelError(f"no supported images under {source}")
        return files
    raise PanelError(f"source not found: {source}")


def resolve_size(size: str, mode: str, width: int, height: int) -> str:
    """Turn 'auto'/'source' into a concrete ratio or pixel size for this image."""
    if size == "auto":
        if abs(width - height) / max(width, height) < 0.05:
            return "1:1"
        return "3:4" if height > width else "16:9"
    if size == "source":
        # For comparison modes 'source' means keep every source pixel: the photo
        # half is the source at native size and the design half matches it.
        if mode == "top-bottom":
            return f"{width}x{height * 2}"
        if mode == "left-right":
            return f"{width * 2}x{height}"
        return reduced_ratio(width, height)
    return size


def fresh_task_dir(root: Path, name: str) -> Path:
    root = root.expanduser()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = root / f"{stamp}-{slug(name)}"
    candidate, n = base, 2
    while candidate.exists():
        candidate = base.with_name(f"{base.name}-{n}")
        n += 1
    return candidate


def plan(args: argparse.Namespace) -> dict:
    files = inventory(Path(args.source))
    modes = split_list(args.mode) or ["top-bottom"]
    sizes = split_list(args.size) or ["auto"]
    for mode in modes:
        if mode not in MODES:
            raise PanelError(f"unknown mode {mode!r}; choose from {', '.join(MODES)}")

    sources = []
    for index, file in enumerate(files, start=1):
        image = open_image(str(file))
        sources.append(
            {
                "index": index,
                "path": str(file),
                "stem": slug(file.stem),
                "width": image.width,
                "height": image.height,
                "ratio": reduced_ratio(image.width, image.height),
            }
        )

    outputs = []
    for src in sources:
        prefix = f"source-{src['index']:03d}-{src['stem']}"
        for mode in modes:
            if mode == "wallpaper-pack":
                for device, ratio in DEVICES.items():
                    geo = half_geometry("design-only", ratio, args.long_edge)
                    outputs.append(
                        {
                            "source_index": src["index"],
                            "mode": mode,
                            "device": device,
                            "size": ratio,
                            "generate_image_aspect_ratio": geo["generate_image_aspect_ratio"],
                            "file": f"{prefix}-wallpaper-{args.wallpaper}-{device}-{slug(ratio)}.png",
                        }
                    )
                continue
            for size in sizes:
                resolved = resolve_size(size, mode, src["width"], src["height"])
                geo = half_geometry(mode, resolved, args.long_edge)
                entry = {
                    "source_index": src["index"],
                    "mode": mode,
                    "size": resolved,
                    "canvas": geo["canvas"],
                    "design_region": geo["design_region"],
                    "generate_image_aspect_ratio": geo["generate_image_aspect_ratio"],
                    "file": f"{prefix}-{mode}-{slug(resolved)}.png",
                }
                if mode in COMPARISON_MODES:
                    entry["design_file"] = f"{prefix}-{mode}-{slug(resolved)}-design.png"
                outputs.append(entry)

    task_dir = fresh_task_dir(Path(args.output_root), Path(args.source).expanduser().stem or "task")
    if not args.dry_run:
        task_dir.mkdir(parents=True, exist_ok=False)

    return {
        "task_dir": str(task_dir),
        "created": not args.dry_run,
        "settings": {
            "modes": modes,
            "sizes": sizes,
            "text": args.text,
            "locale": args.locale,
            "wallpaper": args.wallpaper,
        },
        "source_count": len(sources),
        "sources": sources,
        "output_count": len(outputs),
        "outputs": outputs,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", help="image file or directory")
    p.add_argument("--mode", action="append", default=[], help="repeatable or comma-separated")
    p.add_argument("--size", action="append", default=[], help="auto, source, W:H, or WxH; repeatable")
    p.add_argument("--text", choices=("prompt", "exact", "none"), default="prompt")
    p.add_argument("--locale", default="en-IN")
    p.add_argument("--wallpaper", choices=("linked", "independent"), default="independent")
    p.add_argument("--output-root", default=str(DEFAULT_ROOT))
    p.add_argument("--long-edge", type=int, default=2048)
    p.add_argument("--dry-run", action="store_true", help="plan only; do not create the task directory")
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        result = plan(args)
    except PanelError as exc:
        sys.stderr.write(f"error: {exc}\n")
        raise SystemExit(2)
    print(json.dumps(result, indent=2))
    sys.stderr.write(
        f"{result['source_count']} source(s) -> {result['output_count']} output(s) in {result['task_dir']}\n"
    )


if __name__ == "__main__":
    main()

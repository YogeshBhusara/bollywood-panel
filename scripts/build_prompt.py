#!/usr/bin/env python3
"""Assemble the exact generation prompt for one Bollywood Panel output.

Order is fixed and matches SKILL.md:
  1. the complete verbatim brief from references/original-prompt.md
  2. a short delivery preamble
  3. exactly one mode contract
  4. exactly one text contract
  5. the user's explicit non-style extras, if any

The script only reads the brief; it never edits or paraphrases it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BRIEF = SKILL_ROOT / "references" / "original-prompt.md"

MODES = ("top-bottom", "left-right", "design-only", "wallpaper-pack")
TEXT_MODES = ("prompt", "exact", "none")
STRATEGIES = ("compose", "one-shot")
DEVICES = {
    "phone": "9:16",
    "tablet": "4:3",
    "desktop": "16:9",
    "watch": "1:1",
}

PREAMBLE = (
    "Delivery notes for this single output. These notes change only layout, "
    "text handling, and delivery variables. Every aesthetic instruction in the "
    "brief above stays in force."
)

# Used when the compositor will place the real photograph next to the design.
DESIGN_REGION_CONTRACT = (
    "Layout: produce ONLY the Bollywood restage. Fill the entire canvas with the "
    "design; do not include the original photograph, a before/after split, a "
    "frame, border, divider, caption strip, or empty margin. The reference image "
    "is an identity, pose, and colour source only. This design will later be "
    "placed {placement} the untouched original photograph at an exact 50:50 "
    "split, so keep the subject clear of the {edge} edge where the two halves "
    "will meet."
)

ONE_SHOT_CONTRACTS = {
    "top-bottom": (
        "Layout: the entire canvas is two full-width bands of exactly equal height. "
        "The original photograph, identity-true and only lightly graded, fills the "
        "top 50%. The Bollywood restage fills the bottom 50%. No divider line, no "
        "third band, no caption strip."
    ),
    "left-right": (
        "Layout: the entire canvas is two full-height bands of exactly equal width. "
        "The original photograph, identity-true and only lightly graded, fills the "
        "left 50%. The Bollywood restage fills the right 50%. Wherever the brief "
        "says upper or lower, read left and right instead. Do not rotate this into "
        "a stacked layout."
    ),
}

DESIGN_ONLY_CONTRACT = (
    "Layout: the full canvas is the Bollywood restage. The reference photograph "
    "is an invisible identity, pose, and colour reference only; do not show it, "
    "split the canvas, or add a frame."
)

WALLPAPER_CONTRACT = (
    "Layout: this is one complete {device} wallpaper at {ratio}. The full canvas "
    "is the Bollywood restage; the reference photograph is an invisible identity "
    "reference only. Keep the subject and key action inside the central safe area "
    "so system UI does not cover them. {family}"
)

WALLPAPER_LINKED = (
    "A second reference image is the anchor wallpaper already made from this "
    "source; match its costume, palette, and set so the family reads as one song."
)
WALLPAPER_INDEPENDENT = "Treat this device as its own standalone artwork."

TEXT_CONTRACTS = {
    "prompt": (
        "Text: include a small amount of filmi copy in {locale}, grown from this "
        "photograph's subject, place, or mood. Follow the brief for type, scale, "
        "and placement. Do not invent a real film title, star name, or studio logo."
    ),
    "exact": (
        "Text: render exactly this string and nothing else: \u201c{exact}\u201d. Do "
        "not translate, correct, expand, or add a title around it. Follow the brief "
        "for type, scale, and placement."
    ),
    "none": (
        "Text: none. No letters, numbers, logos, labels, watermarks, or fake "
        "lettering anywhere in the image."
    ),
}


def read_brief(path: Path) -> str:
    if not path.is_file():
        sys.exit(f"error: brief not found at {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        sys.exit(f"error: brief at {path} is empty")
    return text


def mode_contract(args: argparse.Namespace) -> str:
    if args.mode == "design-only":
        return DESIGN_ONLY_CONTRACT
    if args.mode == "wallpaper-pack":
        if not args.device:
            sys.exit("error: --device is required for wallpaper-pack")
        family = WALLPAPER_LINKED if args.wallpaper == "linked" else WALLPAPER_INDEPENDENT
        return WALLPAPER_CONTRACT.format(
            device=args.device, ratio=DEVICES[args.device], family=family
        )
    if args.strategy == "one-shot":
        return ONE_SHOT_CONTRACTS[args.mode]
    if args.mode == "top-bottom":
        return DESIGN_REGION_CONTRACT.format(placement="directly below", edge="top")
    return DESIGN_REGION_CONTRACT.format(placement="directly to the right of", edge="left")


def text_contract(args: argparse.Namespace) -> str:
    if args.text == "exact":
        if not args.exact_text:
            sys.exit("error: --exact-text is required when --text exact")
        return TEXT_CONTRACTS["exact"].format(exact=args.exact_text)
    if args.text == "prompt":
        return TEXT_CONTRACTS["prompt"].format(locale=args.locale)
    return TEXT_CONTRACTS["none"]


def build(args: argparse.Namespace) -> str:
    parts = [read_brief(args.brief), PREAMBLE, mode_contract(args), text_contract(args)]
    if args.extra:
        parts.append("User requirements: " + " ".join(e.strip() for e in args.extra if e.strip()))
    return "\n\n".join(parts) + "\n"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mode", choices=MODES, required=True)
    p.add_argument(
        "--strategy",
        choices=STRATEGIES,
        default="compose",
        help="comparison modes only: 'compose' generates the design half for the "
        "compositor (default, exact 50:50); 'one-shot' asks the model for the whole canvas",
    )
    p.add_argument("--text", choices=TEXT_MODES, default="prompt")
    p.add_argument("--locale", default="en-IN", help="locale for prompt text (default en-IN)")
    p.add_argument("--exact-text", help="verbatim copy when --text exact")
    p.add_argument("--device", choices=tuple(DEVICES), help="wallpaper-pack device")
    p.add_argument("--wallpaper", choices=("linked", "independent"), default="independent")
    p.add_argument("--extra", action="append", default=[], help="explicit non-style user requirement (repeatable)")
    p.add_argument("--brief", type=Path, default=DEFAULT_BRIEF, help="path to the canonical brief")
    p.add_argument("--out", type=Path, help="write the prompt here instead of stdout")
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    prompt = build(args)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(prompt, encoding="utf-8")
        print(args.out)
    else:
        sys.stdout.write(prompt)


if __name__ == "__main__":
    main()

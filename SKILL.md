---
name: bollywood-panel
description: >-
  Convert any photograph into an Indian Bollywood-style picture that is vibrant
  in color and chaos but fun. Preserves the source subject's identity while
  restaging them as a masala film still or song-sequence poster. Use when the
  user invokes bollywood-panel, asks for Bollywood, filmi, masala, Hindi cinema,
  or Indian movie-poster treatment of an image, or wants a chaotic colorful
  song-and-dance restage of a photo.
---

# Bollywood Panel

Create finished PNG artwork from the user-supplied photograph or image directory. `references/original-prompt.md` is the sole creative and aesthetic authority. Never paraphrase it; `scripts/build_prompt.py` injects it verbatim.

All script paths below are relative to this skill's directory. Run them with `python3`. They need Pillow (`python3 -m pip install -r scripts/requirements.txt`); HEIC sources also need `pillow-heif`.

## Delivery contract

- One source photograph produces its own isolated outputs. Never combine sources or reuse another source's subject, copy, or result.
- Canonical presentation: 3:4 portrait, reality above, Bollywood restage below, exactly 50:50.
- Modes: `top-bottom`, `left-right`, `design-only`, `wallpaper-pack`. Comparison modes have exactly two equal regions: reality above or left, design below or right. No header, footer, inset, grid, or third band.
- A directory is explicit batch intent: inventory recursively in stable order, report the count, resolve shared settings once, generate each source independently, account for every success and failure.
- Resolve mode(s), size(s), text mode, locale, wallpaper relationship, and output root before generating. Never infer a silent ratio or locale.

## Preflight

Skip anything the user already stated. Otherwise ask once, using real host widgets when available (never fake checkboxes):

1. Mode(s): `top-bottom` (default), `left-right`, `design-only`, `wallpaper-pack`. Multi-select allowed.
2. Size(s): `auto` (default: `3:4` portrait, `16:9` landscape, `1:1` square), `source` (keep every source pixel), any `W:H`, or exact `WxH`.
3. Text: `prompt` (default, locale defaults to `en-IN`), `exact` (collect the verbatim string), or `none`.
4. Wallpaper relationship, only if wallpaper mode is on: `linked` or `independent`.

## Workflow

### 1. Plan

```bash
python3 scripts/plan_task.py SOURCE --mode top-bottom --size auto --text prompt --locale en-IN
```

`SOURCE` is one image or a directory. The script validates inputs, creates one fresh flat task directory under `~/Desktop/bollywood-panel/` (or `--output-root`), and prints a JSON plan. Each entry in `outputs` gives you the `file` name, the `generate_image_aspect_ratio` to request, and for comparison modes a `design_file` name. Report `source_count` to the user before generating a batch. Add `--dry-run` to preview without creating the directory.

### 2. Build the prompt for each output

```bash
python3 scripts/build_prompt.py --mode top-bottom --text prompt --locale en-IN
python3 scripts/build_prompt.py --mode design-only --text exact --exact-text "SATURDAY NIGHT CHAOS"
python3 scripts/build_prompt.py --mode wallpaper-pack --device phone --wallpaper linked --text none
```

Output order is fixed: verbatim brief, delivery preamble, one mode contract, one text contract, then `--extra` user requirements (repeatable, non-style only). Use the printed text as the `GenerateImage` description without editing it.

Comparison modes default to `--strategy compose`: the prompt asks for the design half only, and step 4 places the real photograph beside it. This keeps identity pixel-true and the split exactly 50:50. Use `--strategy one-shot` only when the user explicitly wants the model to also re-grade or extend the photo half.

### 3. Generate

Call `GenerateImage` once per output with:

- `description`: the text from step 2
- `reference_image_paths`: the source photograph (plus the anchor wallpaper for `linked` devices after the first)
- `aspect_ratio`: the plan's `generate_image_aspect_ratio`
- `filename`: the plan's `design_file` for compose strategy, otherwise `file`

Move the result into the task directory. Never feed a stylised result, another style's output, or a sample back through a second pass.

### 4. Compose comparison modes

```bash
python3 scripts/compose_panel.py compose --mode top-bottom \
  --source SOURCE.jpg --design TASK/design_file.png \
  --out TASK/file.png --size 3:4
```

Omit `--size` to keep every source pixel (photo at native size, design matched to it). The source is EXIF-corrected and cover-cropped, never stretched; its ICC profile is preserved. Odd split axes snap to even and the report says so.

Use `python3 scripts/compose_panel.py half --mode top-bottom --size 3:4` if you need the design-region geometry on its own.

### 5. Audit and accept

```bash
python3 scripts/compose_panel.py audit --mode top-bottom --input TASK/file.png
```

Non-zero exit means the detected seam is off the midpoint; fix with `compose` rather than regenerating. Then look at every image at full and thumbnail size. Accept only when:

- the subject is still recognisably the person or thing from the source;
- the restage follows the brief: saturated masala colour, joyful chaos, filmi lighting, maximal composition, no grim or exotic clichés;
- text matches the chosen mode and locale, with no invented real film title or logo;
- no watermark, UI chrome, border, third band, or second-pass artefact.

Regenerate only the failing output. Report each final path with a one-line read of what the restage did.

## Wallpaper pack

Plan once with `--mode wallpaper-pack --wallpaper linked|independent`. For `linked`, generate the phone canvas first as the anchor, then generate each remaining device with the source and the anchor both in `reference_image_paths`. For `independent`, every device receives only the source.

## References

- `references/original-prompt.md` — canonical runtime brief
- `references/runtime-adapter.md` — delivery variable notes
- `scripts/plan_task.py` — inventory, task directory, filenames, aspect ratios
- `scripts/build_prompt.py` — verbatim brief + contracts → prompt text
- `scripts/compose_panel.py` — `half`, `compose`, `resize`, `audit`
- `examples.md` — invocation examples

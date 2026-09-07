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

Create finished PNG artwork from the current user-supplied photograph or image directory. Read `references/original-prompt.md` completely immediately before every generation. That brief is the sole creative and aesthetic authority; never summarise, blend, or replace it with this file, the README, or a sample.

## Delivery contract

- One source photograph produces its own isolated outputs. Never combine source photographs or reuse another source's subject, wording, or result.
- The canonical presentation is a 3:4 portrait canvas with reality above and the Bollywood restage below, exactly 50:50.
- Support `top-bottom`, `left-right`, `design-only`, and `wallpaper-pack`. Comparison modes always have exactly two equal regions: reality above or left, design below or right. Never add a header, footer, inset panel, grid, or third band.
- A directory is explicit batch intent. Inventory supported raster files recursively in stable order, report the count, resolve shared settings once, generate each source independently, and account for every success and failure.
- Resolve mode(s), size(s), text mode, locale, wallpaper relationship, device sizes, and output root before generation. Do not infer a silent ratio or locale.

## Prompt authority

For each output, concatenate the complete verbatim original brief, then a short delivery preamble, exactly one selected mode contract, exactly one text contract, and only the user's explicit non-style requirements. Runtime additions may change delivery variables only.

In `left-right`, override the brief's upper/lower positional terms with left/right, preserving its aesthetic instructions and strict equal halves. In `design-only` and `wallpaper-pack`, the design occupies the entire canvas and the source is not displayed. Never add an outer palette lecture, title card that is not part of the artwork, or aesthetic theory.

Text modes are `prompt`, `exact`, and `none`. Resolve the target locale explicitly. Exact text is passed verbatim; text-free output contains no letters, numbers, logos, labels, or pseudo-text. In prompt text mode, generate only a small amount of source-grounded filmi copy in the resolved locale, following the original brief's typography and placement instructions.

Prefer the built-in image tool (`GenerateImage`) and make one complete-canvas generation per distinct output. Pass the source photograph in `reference_image_paths`. Never feed an intermediate stylisation, another style's result, or a sample back through a second transformation pass. If no compatible image route is available, ask the user to enable one or voluntarily provide an API key; never expose secrets. Use `scripts/compose_panel.py` only for exact raster sizing, pixel-preserving 50:50 composition, or read-only audits, never to invent the design.

## Output and acceptance

Write final PNGs directly inside one fresh task directory under `~/Desktop/bollywood-panel/` or the explicit output root. Use collision-safe filenames; do not create source, mode, or size subdirectories and do not generate an automatic contact sheet.

Inspect every result at full and thumbnail size. Accept only when:

- the source identity is still recognisable (face, body type, key clothing cues unless the brief restyles costume);
- the ratio and source visibility are correct;
- for comparison modes, the split direction and exact 50:50 midpoint are correct;
- the transformed region follows the complete original brief: saturated masala colour, fun chaos, filmi lighting, maximal but joyful composition;
- text follows the chosen mode and locale;
- there is no watermark, SVG substitute, UI chrome, third band, grim exoticism, or second-pass artefact.

If a comparison split is close but not exact, repair geometry with `scripts/compose_panel.py` using the original source pixels for the reality half. Do not regenerate the design half unless the aesthetic itself failed.

For linked wallpapers, create one anchor from the original source, then independently recompose each remaining device using the original source plus that anchor. Independent wallpapers receive only the original source.

## Preflight

If the user did not specify settings, ask once (real host widgets when available; otherwise a short numbered question, never fake checkboxes):

1. Mode(s): `top-bottom` (default), `left-right`, `design-only`, `wallpaper-pack` — multi-select allowed.
2. Size(s): `3:4` (default for portrait), `16:9` (default for landscape), `1:1`, `9:16`, `auto`, `source`, or exact pixels. Map the closest supported `GenerateImage` aspect ratio (`1:1`, `4:3`, `3:4`, `16:9`, `9:16`) and correct leftover geometry with the compose script if needed.
3. Text: `prompt` (default), `exact`, or `none`. If `prompt`, resolve locale (default `en-IN` unless the user specifies another). If `exact`, collect the verbatim string.
4. Wallpaper relationship only when wallpaper mode is on: `linked` or `independent`.

Skip questions the user already answered in the invocation.

## Generation recipe

1. Read `references/original-prompt.md` in full.
2. Confirm the source file exists and is a supported raster (`png`, `jpg`, `jpeg`, `webp`, `tif`, `tiff`, `heic` if the host can decode it).
3. Build one prompt per output: original brief + mode contract + text contract + user extras.
4. Call `GenerateImage` with `reference_image_paths` set to the source, a collision-safe `filename`, and the mapped `aspect_ratio`.
5. Save the PNG into the task directory. Filename pattern: `source-NNN-stem-mode-ratio.png`.
6. Inspect. If the comparison split is inexact, run:

```bash
python3 scripts/compose_panel.py \
  --mode top-bottom \
  --source SOURCE.png \
  --design DESIGN.png \
  --out OUTPUT.png
```

7. Report each output path and a one-line read of what the restage did.

## Mode contracts (append one)

**top-bottom.** Entire canvas is two full-width bands of equal height. Original photograph, identity-true, occupies the top 50%. Bollywood restage occupies the bottom 50%. No divider line, no third band.

**left-right.** Entire canvas is two full-height bands of equal width. Original photograph on the left 50%. Bollywood restage on the right 50%. Do not rotate this into a stacked layout.

**design-only.** Full canvas is the Bollywood restage. The photograph is an invisible identity reference only.

**wallpaper-pack.** Same as design-only, one complete canvas per device. Default devices: phone `9:16`, tablet `4:3`, desktop `16:9`, watch `1:1`.

## Text contracts (append one)

**prompt.** A little source-grounded filmi copy in the resolved locale. Follow the original brief for type, scale, and placement.

**exact.** Render the user's string verbatim. Do not translate, correct, or add a title around it.

**none.** No letters, numbers, logos, labels, or fake lettering.

## References

- `references/original-prompt.md` — canonical runtime brief
- `references/runtime-adapter.md` — delivery adapter notes
- `scripts/compose_panel.py` — pixel-exact sizing and 50:50 composition
- `examples.md` — invocation examples

# Examples

Paths below assume the skill directory is the working directory.

## Single portrait, default comparison

User: `Turn this into Bollywood` plus `photo.jpg`

```bash
python3 scripts/plan_task.py photo.jpg --mode top-bottom --size auto
python3 scripts/build_prompt.py --mode top-bottom --text prompt --locale en-IN
# GenerateImage(description=<prompt>, reference_image_paths=[photo.jpg], aspect_ratio="4:3",
#               filename="source-001-photo-top-bottom-3-4-design.png")
python3 scripts/compose_panel.py compose --mode top-bottom --source photo.jpg \
  --design TASK/source-001-photo-top-bottom-3-4-design.png \
  --out TASK/source-001-photo-top-bottom-3-4.png --size 3:4
python3 scripts/compose_panel.py audit --mode top-bottom --input TASK/source-001-photo-top-bottom-3-4.png
```

## Landscape diptych, no text, every source pixel kept

```text
/bollywood-panel street.jpg --mode left-right --size source --text none
```

The plan resolves `source` to `WxH` doubled in width; `compose` runs without `--size`.

## Full poster from a group photo with exact copy

```text
/bollywood-panel friends.png --mode design-only --size 3:4 --text exact
```

```bash
python3 scripts/build_prompt.py --mode design-only --text exact --exact-text "SATURDAY NIGHT CHAOS"
```

No compose step. Faces stay the friends in the photo.

## Directory batch in Hindi

```text
/bollywood-panel ./holiday-snaps --mode design-only --size 3:4 --text prompt --locale hi-IN
```

`plan_task.py` lists every raster recursively, reports the count, and names every output in one flat task folder. Generate each independently.

## Linked wallpaper family

```bash
python3 scripts/plan_task.py me.jpg --mode wallpaper-pack --wallpaper linked --text none
python3 scripts/build_prompt.py --mode wallpaper-pack --device phone --wallpaper linked --text none
# generate phone first -> anchor
python3 scripts/build_prompt.py --mode wallpaper-pack --device desktop --wallpaper linked --text none
# GenerateImage(..., reference_image_paths=[me.jpg, TASK/<phone anchor>.png], aspect_ratio="16:9")
```

# Examples

## Single portrait, default comparison

User: `Turn this into Bollywood` plus `photo.jpg`

Agent:

1. Read `references/original-prompt.md`
2. Mode `top-bottom`, size `3:4`, text `prompt`, locale `en-IN`
3. Generate one canvas with the photo in `reference_image_paths`
4. Save `~/Desktop/bollywood-panel/<task>/source-001-photo-top-bottom-3x4.png`

## Landscape diptych, no text

```text
/bollywood-panel street.jpg --mode left-right --size 16:9 --text none
```

Reality left, restage right. No lettering in either half.

## Full poster from a group photo

```text
/bollywood-panel friends.png --mode design-only --size 3:4 --text exact --locale en-IN
```

Exact copy supplied by the user, for example `SATURDAY NIGHT CHAOS`. Faces stay the friends in the photo.

## Directory batch

```text
/bollywood-panel ./holiday-snaps --mode design-only --size 3:4 --text prompt --locale hi-IN
```

Inventory every raster, report the count, generate independently, write every PNG into one fresh task folder.

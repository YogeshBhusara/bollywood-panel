# Bollywood Panel runtime adapter

The canonical source brief is `references/original-prompt.md`. This adapter records delivery variables only and never replaces the original aesthetic instructions.

- Modes: `top-bottom`, `left-right`, `design-only`, `wallpaper-pack`
- Comparison modes use a strict 50:50 split: reality above for top-bottom and reality left for left-right.
- Text: `prompt`, `exact`, or `none`; resolve the target locale explicitly. Default locale for prompt text is `en-IN`.
- Sizes: `auto`, `source`, common ratios, custom ratios, or exact pixels.
- Inputs: one image or an isolated directory batch.

Append this adapter after the complete verbatim original brief. For `left-right`, replace only its upper/lower delivery coordinates with left/right, preserving the same aesthetic and a strict 50:50 division. For `design-only` or `wallpaper-pack`, use the full canvas for the designed region and keep the source photograph invisible. Text modes and the resolved locale override only language and exact wording, never the original image–text composition principles. No third band, header, footer, inset panel, or second stylisation pass.

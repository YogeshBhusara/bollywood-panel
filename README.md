# Bollywood Panel

A Cursor / Codex skill that turns any photograph into an **Indian Bollywood-style picture: vibrant in color and chaos but fun.**

The source person stays themselves. Wardrobe, set, lighting, extras, and colour become a masala song sequence.

Inspired by the numbered XXD Panel soldier-skill pattern (one locked aesthetic brief, isolated sources, four delivery modes). This project is original work and is not affiliated with XXD.

## Install

```bash
git clone https://github.com/YogeshBhusara/bollywood-panel.git
```

Then copy or symlink into your agent skills folder:

```bash
mkdir -p ~/.cursor/skills
ln -s "$(pwd)/bollywood-panel" ~/.cursor/skills/bollywood-panel
```

Restart the agent session and invoke `$bollywood-panel`.

## Invocation

```text
/bollywood-panel photo.jpg
/bollywood-panel photo.jpg --mode top-bottom --size 3:4 --text prompt --locale en-IN
/bollywood-panel photo.jpg --mode left-right --size 16:9 --text none
/bollywood-panel photo.jpg --mode design-only --size 9:16
/bollywood-panel ./photos --mode design-only --size 3:4 --text prompt --locale hi-IN
```

If settings are missing, the skill asks once, then generates.

## Four output modes

- `top-bottom` — reality on top, Bollywood restage below, exact 50:50 (default).
- `left-right` — reality left, restage right, exact 50:50.
- `design-only` — full-canvas restage; the photo is an invisible identity reference.
- `wallpaper-pack` — phone, tablet, desktop, and watch canvases, `linked` or `independent`.

## What the restage does

Read the subject → keep identity → restyle costume and set → flood the frame with festive chaos → push saturated masala colour and theatrical light → add a little filmi copy if text is on.

It will not replace the person with a celebrity, flatten the photo into a colour filter, or lean on grim / exotic clichés.

## Files

- [SKILL.md](SKILL.md) — runtime contract
- [references/original-prompt.md](references/original-prompt.md) — canonical aesthetic brief
- [references/runtime-adapter.md](references/runtime-adapter.md) — delivery variables
- [scripts/compose_panel.py](scripts/compose_panel.py) — pixel-exact 50:50 composition

## License

MIT. See [LICENSE](LICENSE).

# Ninna Cao Slides

An Agent Skill for Claude (and other assistants that load Agent Skills) that builds image-rich presentations: a meaningful visual on every slide, photographs that fade softly into the background, a visual direction chosen for each brief, clear diagrams, automatic motion, and matching HTML, PDF, PowerPoint and speaking notes.

![Cinematic Night example deck](docs/cinematic-example.jpg)

*The bundled Cinematic Night example (`ninna-cao-slides/assets/example-cinematic-deck.json`). Photos: Wikimedia Commons contributors, CC0 / CC BY / CC BY-SA; see the deck's credits slide.*

## What's in v3

- **A visual on every slide.** The skill plans a picture, diagram or chart for each slide and finds openly licensed images on the web when your material runs out (`find_images.py`, `fetch_image.py`), recording creator, license and source. A sources-and-credits slide is generated automatically.
- **Image fades.** Pictures sit on one side and dissolve into the stage (`backdrop.place`: right, left, top, top-right, bottom, full). Works with every style.
- **Cinematic Night.** Condensed headlines, typewriter labels, a warm charcoal stage with soft light pools and one brand accent. Fonts bundled.
- **Checks that look at the render.** `qa_render.py` flags overlapping or clipped text, broken or upscaled images and slides with no visual, and makes a contact sheet. The PDF exporter is pixel-exact by default, so fades survive.
- **Chinese decks.** CJK font subsetting and typography rules.

See [CHANGELOG](ninna-cao-slides/CHANGELOG.md) for details.

## Install

**Claude Code:** copy the `ninna-cao-slides` folder into `~/.claude/skills/` (or a project's `.claude/skills/`).

**Claude apps:** download the release ZIP (or run `tools/package.sh`) and upload it under **Customize > Skills > Upload a skill**.

Optional Python packages for the scripts: `pip install pillow playwright fonttools brotli` (the builder itself needs only Python 3.10+).

## Quick start

```bash
cd ninna-cao-slides
python3 scripts/build_deck.py assets/example-cinematic-deck.json /tmp/cinematic.html
python3 scripts/check_deck.py /tmp/cinematic.html
python3 scripts/qa_render.py /tmp/cinematic.html /tmp/qa
python3 scripts/export_pdf.py /tmp/cinematic.html /tmp/cinematic.pdf
```

Or just ask Claude: *"Use Ninna Cao Slides to make a 15-slide talk on … — a visual on every slide, photos fading into the background, HTML and PDF."*

## Package a release

```bash
tools/package.sh   # → dist/Ninna_Cao_Slides_v<version>.zip
```

## Licence

[MIT](LICENSE), copyright 2026 Ninna Cao. Third-party parts keep their own licences: [Frontend Slides](https://github.com/zarazhangrui/frontend-slides) by Zara Zhang (MIT), the bundled fonts (SIL Open Font License) and the example photographs (CC0 / CC BY / CC BY-SA). Full provenance in [references/credits.md](ninna-cao-slides/references/credits.md).

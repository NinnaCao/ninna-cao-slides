# Visual Slides

**Presentations that look designed, not generated.** An open-source Agent Skill for Claude that turns a brief, a document or an old deck into a polished presentation: a strong real image on every slide, and a look that comes from your topic, not a template.

[![License: MIT](https://img.shields.io/badge/license-MIT-black)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Claude%20%7C%20Claude%20Code-black)](https://code.claude.com/docs/en/skills)
[![Release](https://img.shields.io/github/v/release/NinnaCao/visual-slides?color=black)](https://github.com/NinnaCao/visual-slides/releases/latest)

![A deck about green roofs made with Visual Slides: palette and typefaces taken from its own photos](docs/topic-example.jpg)

## Why

Most AI-made decks look the same: one template, walls of bullets, generic stock photos, text overflowing its box. Visual Slides works the way a designer does:

1. **It reads everything first.** Before choosing a single image, it reads the whole deck or brief and decides where the pictures should come from.
2. **It finds the right images.** A brand or product deck uses the brand's own website imagery. A topic deck gets real, documentary photos from the web. Your own work uses your own photos. Every image is credited automatically.
3. **Every topic gets its own look.** The palette is taken from the deck's own photos (or your brand colours) and the typefaces fit the subject's mood: a green-roof talk, an elder-care story and an AI launch never share a template.
4. **Every slide gets an excellent visual.** Photos fade softly into the background instead of sitting in hard boxes. Diagrams and text-heavy slides still get a photo, dimmed behind the content.
5. **It checks its own work.** Every slide is rendered in a real browser and checked for overlapping or clipped text, broken or blurry images, and slides without a visual, before you ever see it.

## One topic, three directions

When you have not picked a look, it makes three from the same photos and shows you the real opening slide in each:

![The same cover in three themes made from the same photos: nature serif on paper, clinical teal, bold condensed on dark](docs/three-directions.jpg)

## Made with Visual Slides

![Every Story: a business update for an AI memoir service for older adults](docs/every-story.jpg)

![Sound you can see: an audio design talk in the Cinematic Night look](docs/example-deck.jpg)

## Get started

**Claude Code:** copy the `visual-slides` folder into `~/.claude/skills/` (or your project's `.claude/skills/`).

**Claude (web and desktop apps):** download the ZIP from the [latest release](https://github.com/NinnaCao/visual-slides/releases/latest), then go to **Customize > Skills > Upload a skill**.

Then just ask:

> Use Visual Slides to turn this report into a 12-slide talk for our leadership team. HTML and PDF.

> Make a 15-slide deck about AI in elderly care. Find real photos for every slide.

> Make a deck about urban farming. Show me three looks first.

> Redesign this deck (attached) for a product launch. Use our brand's website imagery.

## What you get

| | |
| --- | --- |
| **Outputs** | Single-file HTML deck (works offline, scales to any screen), pixel-exact PDF, PowerPoint, speaker notes |
| **Looks** | Made from each topic: palette from its own photos or your brand, typefaces from ten moods (editorial, warm, tech, corporate, playful, luxury, nature, bold, clinical, cinematic), light or dark; plus 46 more directions for inspiration |
| **Images** | Brand websites, Openverse, Wikimedia Commons, Unsplash and Pexels (with a key); licenses checked, credits slide generated |
| **Motion** | Staged entrances, traced diagrams, photos that settle in; optional autoplay; respects reduced motion |
| **Languages** | English and Chinese, with proper CJK typography and font subsetting |
| **Quality checks** | Static checks plus a rendered pass over every slide, with a contact sheet |

## How it works

```
read the whole content → content brief + image plan → find & credit images for this topic
→ make a theme from those images (palette + typefaces) → build the deck (fades, diagrams, motion)
→ render & check every slide → export HTML / PDF / PPTX
```

Under the hood it is a set of instructions plus small, dependency-light Python scripts you can also run yourself:

```bash
cd visual-slides
python3 scripts/make_theme.py --mood nature --images assets/media/green-roofs --out /tmp/theme --preview  # theme from photos
python3 scripts/build_deck.py assets/example-topic-deck.json /tmp/deck.html       # build
python3 scripts/check_deck.py /tmp/deck.html                                      # static checks
python3 scripts/qa_render.py /tmp/deck.html /tmp/qa                               # render + check every slide
python3 scripts/export_pdf.py /tmp/deck.html /tmp/deck.pdf                        # pixel-exact PDF
python3 scripts/find_images.py "night train" --out media/candidates/train         # open-licence image search
python3 scripts/collect_page_images.py https://brand.example/product --out media/candidates/brand
```

The builder needs only Python 3.10+. Optional: `pip install pillow playwright fonttools brotli` for themes, image conversion, rendering checks, PDF export and font subsetting.

## FAQ

**Can I use the images in my deck?** The skill keeps only images whose license fits (CC0, CC BY, CC BY-SA, Unsplash, Pexels, or brand imagery for presentations about that brand) and lists every source on a generated credits slide. Brand website imagery is for presentations about that company; check the brand's terms before publishing such a deck.

**Does it work without Claude?** The scripts run on their own, and the instructions work in other assistants that load Agent Skills.

**Is it free?** Yes. MIT licensed.

## Credits

Created by [Ninna Cao](https://github.com/NinnaCao). The fixed 16:9 browser stage builds on [Frontend Slides](https://github.com/zarazhangrui/frontend-slides) by Zara Zhang (MIT). The complete original is included in `visual-slides/assets/source/` and `visual-slides/references/frontend-slides/`. Fonts: open-licence families from [Google Fonts](https://github.com/google/fonts) (SIL Open Font License), including Barlow Condensed, Manrope and Courier Prime for Cinematic Night. Example photos: Wikimedia Commons contributors (CC0, CC BY, CC BY-SA). See [NOTICE](visual-slides/NOTICE.md) and [credits](visual-slides/references/credits.md).

## License

[MIT](LICENSE) © 2026 Ninna Cao. Third-party parts keep their own licenses (see NOTICE).

Release notes: [CHANGELOG](visual-slides/CHANGELOG.md). To build a release ZIP: `tools/package.sh`.

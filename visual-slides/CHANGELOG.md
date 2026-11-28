# Changelog — Visual Slides

## 4.1.0 — the look comes from the topic (28 Nov 2026)

Direction: every deck should look like its own subject. Stop reusing one font and colour set (Cinematic Night) for every topic, and search images for each deck's own topic.

- **Topic themes:** `scripts/make_theme.py` makes a theme from the deck's own images or brand colours: page and text tinted towards the photos, an accent from the vivid colour that recurs across the set, a second accent from another hue, contrast checked (text ≥ 7:1, accent ≥ 3.2:1). Options: `--brand`, `--hue`, `--mode`, `--cjk`, `--font`, `--radius`, `--preview`.
- **Ten moods** (`assets/themes/moods.json`): editorial, warm, tech, corporate, playful, luxury, nature, bold, clinical and cinematic, each with an open-licence type pairing from the Google Fonts repository, a type scale, corner radius and a light or dark default. Fonts are downloaded once, subset to Latin and shipped with their OFL licence.
- **`adaptive` preset:** `assets/adaptive.css` is a token-only component system (no hard-coded colour or typeface) that works in light and dark themes. `style: {"preset": "adaptive", "theme": "theme/theme.json"}` embeds the theme's fonts, subset to the deck's text.
- **Cinematic Night is now one theme** (`assets/themes/cinematic.css` on top of `adaptive.css`), pixel-identical to 4.0.0, used when chosen rather than by default.
- **SKILL.md step 5 rewritten:** design brief → mood → theme from this deck's images → optional three theme previews (`preview_styles.py` now takes theme files) → build. New reference `references/themes.md`.
- **Sameness checks:** `check_deck.py` warns on stock Cinematic Night nobody chose and on bundled example photos reused in a user deck. Step 4 says to search fresh images for every deck.
- **New example** `assets/example-topic-deck.json`: green roofs in dense cities, six Wikimedia Commons photos found with `find_images.py`, a light `nature` theme made from them (Young Serif, DM Sans, moss accent), a drawn layer diagram and a dark alternate slide.
- `cover_top` type token for display moods whose cover titles run to three lines.

## 4.0.0 — renamed to Visual Slides (26 Nov 2026)

- **New name:** the skill is now **Visual Slides** (`visual-slides`), formerly "Ninna Cao Slides". The skill folder, ZIP name, GitHub repository (`NinnaCao/visual-slides`; the old URL redirects) and all documentation use the new name. Created by Ninna Cao; copyright unchanged.
- **Breaking for installs:** replace `~/.claude/skills/ninna-cao-slides` with `~/.claude/skills/visual-slides`.
- Preset stylesheets renamed `cinematic.css`, `editorial.css`, `light.css`; animation names use a neutral `vs-` prefix.
- The deck controller exposes `window.slideDeck`; `window.ninnaDeck` stays as an alias, so v3 decks still work with the QA and PDF scripts.
- Docs written in a neutral, product voice; new README for first-time users.
- Frontend Slides by Zara Zhang is still included in full: the original repository as a ZIP (all 163 files, byte-identical to upstream) and the unpacked guides, presets and templates in `references/frontend-slides/`.

## 3.1.0 — content-first images (26 Nov 2026)

Direction: understand the whole deck before choosing images; take brand images from the brand's own website (SteelSeries from steelseries.com, Dyson from dyson.com) and topic images from the web; every slide needs an excellent real image, in the background if it is not needed in front.

- **New step 1 in SKILL.md:** read the whole content, write a content brief and an image plan (brand site / web search / user's own work / official sources, per section).
- **Real image on every main slide:** diagrams and illustrations no longer count on their own. `check_deck.py` and `qa_render.py` fail a main slide without a photo, render or screenshot.
- **Ambient backgrounds:** `backdrop.place: "ambient"` puts a dimmed, vignetted full-slide photo behind diagrams, charts and text (`opacity`, `at`, `blur`).
- **`scripts/collect_page_images.py`:** collects candidate images from official brand pages (srcset, picture, share and structured-data images), with `--render` for JavaScript sites, saved-page input, a numbered contact sheet and `fetch_image.py` compatibility. Sites that refuse automated access are reported, never worked around (dyson.com refuses; steelseries.com works).
- **Quality bar** and brand-image rights in `references/web-visuals.md`.
- Fade boxes now override preset backdrop frames, so fades look the same in every style; the generated credits slide is styled in every preset.
- Examples: the editorial and light decks use real workshop photos (Wikimedia Commons, credited) instead of only SVG illustrations; diagram slides gain ambient backgrounds.
- Contact sheets show the width when the height is unknown; no false "preview" warning for Wikimedia's 1920 px renders.

## 3.0.1 — open licence (26 Nov 2026)

- Released under the MIT License (`LICENSE.txt`, repo `LICENSE`), copyright 2026 Ninna Cao. Frontend Slides, the bundled fonts and the example photographs keep their own licences, listed in `NOTICE.md` and `references/credits.md`.

## 3.0.0 — visual-first (26 Nov 2026)

Direction: every slide needs a visual, found on the web when her material runs out, and photographs should fade into the background. The look of an approved dark editorial deck (AI for Marketing, Nov 2026) is recorded as a reusable style.

**New rules (SKILL.md)**
- A visual on every main slide: photo, product image, screenshot, diagram, chart or video. Text-only slides only in the appendix, with a stated reason.
- Hero pictures fade into the stage by default; crisp frames only for images the audience must inspect.
- Visual source planned per slide in the content map; web images credited.

**Cinematic Night preset** (`style.preset: "cinematic"`, `references/cinematic-night.md`)
- Barlow Condensed headlines, Manrope body, Courier Prime labels (OFL, bundled as WOFF2, embedded automatically).
- Warm charcoal stage with named light pools (`glow`), one brand accent (`style.accent`) from which label, paper and glow colours derive, paper slides for rhythm.
- Layouts: cover, divider (outlined numeral), statement; components: cards, flow, rows, tiles, frame, stats, marks, takeaway, numbered kicker chip.
- Headers flow, so a wrapping title pushes its subtitle down instead of colliding.
- CJK support: Noto Sans SC in the stacks, no negative tracking, looser leading for `lang="zh-CN"`.

**Image fades for every preset** (`assets/deck-layout.css`)
- `backdrop.place`: `right`, `left`, `top`, `top-right`, `bottom`, `full`, with `start`, `height`, `fade`, `focus`, `brightness`, `scrim`.
- `.fade-plate` for the same treatment inside slide bodies; a one-time settle on entry.

**Finding images on the web** (`references/web-visuals.md`)
- `scripts/find_images.py`: Openverse and Wikimedia Commons without a key, Unsplash and Pexels with one; license filter, provider interleaving, numbered contact sheet.
- `scripts/fetch_image.py`: slide-ready WebP without metadata, credit written into the manifest, polite retry on 429, no workaround on refusals, warning when a library serves a preview.
- Builder generates a **Sources and image credits** appendix slide from `credits` and `sources`, listing which slide uses each image.

**Builder** (`scripts/build_deck.py`)
- New fields: `backdrop`, `glow`, `section_number`, `number_label`, `visual_exempt`, layouts `divider` and `statement`, `style.accent`, `style.bundled_fonts`, `credits`, `sources`, `credits_slide`, `lang`.
- Font subsetting (`subset: true` / `subset_fonts`) for large CJK fonts.

**Checks and export**
- `check_deck.py`: fails a main slide without a visual; Chinese character density; warns when photos have no credits ledger.
- New `qa_render.py`: renders every slide in Chrome; fails on overlapping, overflowing or clipped text, broken images and slides with no visible visual; warns on upscaled photos and tiny text; writes screenshots and a contact sheet.
- `export_pdf.py`: new default `screens` engine, pixel-exact and keeping fades (Chrome print drops CSS masks), with clickable links; uses the installed Chrome.
- `export_pptx.py` accounts for generated credit slides; `preview_styles.py` offers `cinematic`.
- Trace animation tolerates Chrome's imprecise curve lengths (the end of curved paths no longer goes undrawn).

**Examples**
- `assets/example-cinematic-deck.json`: seven slides plus generated credits, nine openly licensed Wikimedia Commons photos.
- The editorial example's text-only slide gains a feedback-loop diagram.

**Packaging**: `agents/openai.yaml`, `references/claude-use.md` and an updated `references/credits.md` restored from v1; `VERSION` file.

## 2.0.0 — portable version (24 Nov 2026)

Style catalog of 46 directions, the complete Frontend Slides library, PowerPoint reading, PDF/PPTX export, share preparation and style previews; usable across assistants.

## 1.0.0 — first Claude Code install (23 Nov 2026)

Brief-led visual direction, content and evidence guidance, portable builder, controller, notes helper and neutral examples on the Frontend Slides fixed stage.

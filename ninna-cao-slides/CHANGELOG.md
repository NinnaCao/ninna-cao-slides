# Changelog — Ninna Cao Slides

## 3.0.0 — visual-first (26 Nov 2026)

Ninna's direction: every slide needs a visual, found on the web when her material runs out, and photographs should fade into the background. The look of an approved dark editorial deck (AI for Marketing, Nov 2026) is recorded as a reusable style.

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

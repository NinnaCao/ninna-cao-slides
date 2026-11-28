---
name: visual-slides
description: Create image-rich presentations whose look comes from the topic. Every deck gets its own palette and typefaces: colours taken from the deck's own topic images or the brand, fonts chosen for the subject's mood (editorial, warm, tech, nature, luxury, clinical and more), so no two topics look alike. Reads the whole content first, then sources images for it - the brand's own website for company and product decks, web and open-library search for topics - and credits them. Every slide has an excellent real image, in front or behind diagrams and text, and photos fade softly into the page. Includes clear diagrams, automatic motion, render QA, and HTML, PowerPoint, PDF and speaking-note outputs. Cinematic Night (dark, condensed, glowing) stays available as one look among many.
---

# Visual Slides

Create presentations that help an audience understand an idea and how it is applied. These standards carry across projects: a meaningful visual on every slide, photographs that fade into the stage, clear explanations and measured motion. Derive the typography and palette from each deck's own topic and images (never from a previous deck or a bundled example), and the composition from its content, audience, brand and setting. Apply the same standard of visual evidence and export quality to every look.

Read [visual-system.md](references/visual-system.md), [web-visuals.md](references/web-visuals.md) and [content-and-evidence.md](references/content-and-evidence.md) before building. Read [themes.md](references/themes.md) before choosing the look, [images-and-diagrams.md](references/images-and-diagrams.md) when choosing visuals, and [cinematic-night.md](references/cinematic-night.md) only when the user chooses that look. The complete original Frontend Slides library is available through [original-workflow.md](references/original-workflow.md). Follow the user's instructions for the current deck above these defaults.

Use the tools available in the current assistant. If you only have this file, apply its instructions directly. See [portable-use.md](references/portable-use.md) for other assistants and [claude-use.md](references/claude-use.md) for installing in Claude.

## Working principles

1. **Understand the content before choosing a single image.** Read the whole source deck or brief first. Name the subject, brand, products, people, places and tone, then decide where the images should come from (see step 1).
2. **A look made for this topic.** Each deck's palette comes from its own images or brand and its typefaces from the subject's mood. Do not reuse the font and colours of the last deck, an example or a default preset unless the user or brand asks for them.
3. **An excellent real image on every slide.** Every main slide carries at least one real image: a photograph, product render or screenshot. Diagrams, charts and text-led slides still get one, placed in the background (`backdrop.place: "ambient"`) if it is not needed in front. Every image must be excellent: sharp, on-subject, on-brand and well cropped. Never present stock or generated images as the user's real work.
4. **Let photographs melt into the stage.** For covers, dividers, concept and closing slides, place the picture on one side and fade the edges that face the text into the background. Use crisp frames only when the audience must inspect the image.
5. **Preserve context.** Keep enough explanation for someone unfamiliar with the source to follow the presentation.
6. **Show the work.** Use photographs of interviews, observation, workshops, sketches and tests to explain what people actually do. Keep faces, hands, prototypes and other focal details sharp and visible.
7. **Design a coherent story.** Establish the main concept, explain the framework, show its application, then close with the takeaway. Fit the sequence to the actual brief.
8. **Respect approved work.** Start from the latest approved version. Preserve locked slides, wording, order and visual treatments. Make targeted improvements.
9. **Let motion run.** Run staged entrances automatically when a slide opens. Use one advance per slide and make timed autoplay optional.
10. **Keep deliverables aligned.** Use the same current content, image choices, slide numbers, appendix and notes across requested formats.

## 1 Understand the whole content first

Before designing, read every slide of a supplied deck (and its notes) or the whole brief, end to end. Write a short content brief:

- **Subject and purpose:** what the deck is about and what the audience should do or believe afterwards.
- **Who and what appears:** organisations and brands, product names and models, people, places, events, data.
- **Tone and setting:** internal or public, formal or energetic, room or screen.

Then write the **image plan**: where each kind of image will come from.

| The content is about | Get images from |
| --- | --- |
| A company, brand or its products (e.g. SteelSeries, Dyson) | The brand's own website first: product pages, newsroom, press or media kit. Exact products, models and colours. `scripts/collect_page_images.py` |
| A topic, market or idea (e.g. AI for elderly care) | Web search and open libraries for real, authentic photos of the subject. `scripts/find_images.py` |
| The user's own work, research or team | The user's photos, screenshots and files first |
| Real people, places or events | Official or press sources, or openly licensed photos with credit |
| A mix | Decide per section |

Use the plan for every slide. See [web-visuals.md](references/web-visuals.md).

## 2 Determine scope from the existing conversation and files

Identify creation, conversion or revision first. See [workflow.md](references/workflow.md) for visual discovery, density, conversion and the delivery sequence.

- Identify the topic, audience, purpose, primary sources, brand, delivery setting, desired formats, duration, speaker split and approved reference version. Ask only for missing information that materially changes the result.
- Continue a scoped revision in the visual direction of the latest approved deck. For a new deck, derive a direction from its own brief and the references the user selected for it.
- Inspect supplied HTML/PPTX/PDF files and images before editing. Render the approved reference where possible.
- Record any protected slide range. A request such as "only my part" is a scope constraint. Do not renumber protected slides or insert new slides inside them without a reason grounded in the current request.
- Treat a request for a format conversion as a conversion task. Preserve the content and design unless the user also asks for edits.

## 3 Build the content and visual map together

For each slide, record its purpose, plain-language point, supporting evidence, **chosen visual and where it comes from** (user file, official source, open library, or a diagram you draw), and the sentence that explains the connection. Use a canonical deck manifest or an equivalent content map.

- Begin a teaching presentation with the topic or question. Introduce the workplace application after the audience has enough conceptual grounding.
- Map every required reading concept, example and process to a main slide or appendix location. Explain each number with a label, unit, period, denominator or comparison as needed.
- Make framework applications explicit: **what people did, what they learned, and what decision it informed**. Avoid a feature-by-feature product pitch when the purpose is to explain a process.
- Distinguish documented events, the presenter's interpretation, illustrative possibilities and proposed next steps. Do not present a suggested test or rollout as completed work.
- For a case drawn across several products, state that the photos illustrate practices across projects.
- Use a physical prop or a brief audience question when it strengthens the explanation. Do not add a giveaway by default.

## 4 Find the images

Follow [web-visuals.md](references/web-visuals.md) and the image plan from step 1.

- **Brand and product decks:** collect from the brand's own pages with `scripts/collect_page_images.py <url>` (add `--render` for sites that build images with JavaScript). If a site refuses automated access, view it in a real browser, use its press kit, or ask the user. Never work around the block.
- **Topic decks:** search the web and open libraries with `scripts/find_images.py`. Prefer authentic, documentary photos over staged stock that feels generic or AI-made.
- **The user's work:** their own photos and screenshots first.
- Draw diagrams and charts yourself. Then give each diagram or text-led slide a background photo (`ambient`).
- Search open libraries with `scripts/find_images.py` (Openverse and Wikimedia Commons without a key; Unsplash and Pexels with a key). Open the contact sheet, then the full image, before choosing.
- Fetch with `scripts/fetch_image.py --manifest deck.json`: it saves a slide-ready WebP and adds the creator, license and source to the manifest's `credits`. The builder turns them into a sources and image credits slide.
- Hold every image to the quality bar in web-visuals.md: look at three or more candidates per slide, open the full image, reject anything soft, generic, off-brand, watermarked or badly cropped.
- Choose pictures for the planned treatment: a dark or plain background with the subject away from the text for fades, a clear subject that survives the crop for tiles and frames, and enough pixels for the displayed size.
- If a site refuses a download, do not work around it; use the source page, ask the user or choose another image. Use only licenses that allow the deck's purpose.
- Search fresh for every deck, with the deck's own subjects as queries. Never reuse photos from an earlier deck or the bundled examples (`assets/media/`); `check_deck.py` flags them.

## 5 Make the look from the topic

Read [themes.md](references/themes.md). The look follows the subject: a deck about green roofs, one about elder care and one about an AI launch should not share a palette or typefaces.

1. **Write a one-line design brief** from step 1: subject, audience, room (dim or daylight, screen or print) and tone. Choose a mood that fits it (`python3 scripts/make_theme.py --list`): editorial, warm, tech, corporate, playful, luxury, nature, bold, clinical, or cinematic.
2. **Make the theme from this deck's own images** (step 4) or the brand's colours:

   ```bash
   python3 scripts/make_theme.py --mood nature --images media/ --out theme --preview
   ```

   It takes the palette from the photos (page tinted towards them, an accent from the vivid colour that recurs across the set, a second accent from another hue), pairs open-licence typefaces for the mood, checks contrast and writes `theme/theme.json` with the fonts. Use `--brand "#hex"` for a brand colour, `--hue green` to steer the accent to the colour the topic is about, `--mode dark|light` for the room, and `--cjk sans|serif` for Chinese.
3. **Set** `"style": {"preset": "adaptive", "theme": "theme/theme.json"}`. Open `theme/theme-preview.jpg` and adjust `theme.json` by hand if the accent or type does not suit the subject.
4. **When the look is open,** make three themes from the same images (two fitting moods and one contrast) and show the real opening slide in each with `scripts/preview_styles.py deck.json previews a/theme.json b/theme.json c/theme.json`. Continue in the one the user picks. Skip this when the user, the brand or an approved deck already sets the look.

- Follow a supplied brand guide or an approved deck over the mood table: use its colours (`--brand`) and its typefaces (`--font`, or embed the brand's licensed fonts through `style.fonts`).
- **Cinematic Night** (`style.preset: "cinematic"`) is one recorded look (condensed headlines, typewriter labels, glowing dark stage, orange accent). Use it when the user asks for it or continues a deck made with it, not as a default. See [cinematic-night.md](references/cinematic-night.md). Its accent can still come from the topic (`style.accent`).
- The [style catalog](references/style-index.md) and the [complete source library](references/original-workflow.md) hold 46 further directions for inspiration.
- Author HTML at **1920 × 1080** and scale the entire stage uniformly, including on phones.
- For Chinese decks follow the CJK rules in [visual-system.md](references/visual-system.md); the builder subsets CJK fonts to the deck's characters.
- Start with approximately **55–100 visible words** on an explanatory slide; around 110–125 where a framework needs context.
- Keep a clear hierarchy between the headline, orienting sentence, evidence and captions. Choose one main visual action per slide and vary the composition across the story.
- Fade hero pictures with `backdrop.place` (`right`, `left`, `top-right`, `top`, `bottom`, `full`) or `.fade-plate`. Check the fade never cuts through the subject and the text sits on the quiet side. Fades work on light and dark pages.
- Behind a diagram, chart, table or text-led slide, use `backdrop.place: "ambient"` (a dimmed, vignetted full-slide photo; tune `opacity` 0.2–0.4 and `at`) so the slide still has a real image.
- Alternate surfaces with `"theme": "alt"` on a slide (dark on a light theme, light on a dark theme) about once every six to eight slides. Light pools (`glow`) take their colours from the theme.

## 6 Implement HTML and motion

Build a self-contained HTML deck when browser slides are requested. Read [implementation.md](references/implementation.md) for the manifest, stage, playback, print and export behavior, and [motion.md](references/motion.md) for pacing.

```bash
python3 scripts/build_deck.py deck.json presentation.html
```

- Inline CSS, JavaScript, images and fonts in the downloadable HTML. Do not depend on a development server, CDN or an online font request.
- Keep semantic `.slide` sections and use visibility, opacity and pointer-events for switching. Do not use display-based slide switching.
- Give images meaningful alt text. Keep exact diagrams as SVG or native shapes with legible labels.
- Reveal useful content within about 1.5–2 seconds. Keep the settled reading state visually quiet; nothing loops behind text.
- Support keyboard, mouse wheel and swipe navigation, visible controls, fullscreen, reduced motion and private notes, outside the slide canvas.
- If autoplay is enabled, derive timings from the talk, stop on the last main slide, never advance into the appendix, and pause when the tab is hidden.
- Make the print state show all content in its final state, one slide per page, with controls and notes hidden.
- Offer inline text editing for local drafts. Leave edit mode off when the file opens; use a button or E, autosave locally and offer a downloadable edited copy. Omit editing from locked distribution copies.

## 7 Prepare the talk and requested exports

Read [notes-and-engagement.md](references/notes-and-engagement.md) for notes, timing, audience participation or multiple presenters, and [exports-and-qa.md](references/exports-and-qa.md) before delivery.

- Write short spoken sentences with one idea each. Key notes to visible slide numbers. Use Chinese for the speaker's understanding when requested rather than adding bilingual paragraphs to the audience's slides.
- Preserve the user's speaker split. Do not assume a fixed split, slide count or duration from a previous project.
- If a one-page speaking sheet is requested, use distinct pale colors for slide headings and bold yellow highlights for memorable phrases.
- Create requested PPTX, PDF or DOCX files with the environment's format tools. Preserve editable text, diagrams and pictures in PPTX where practical; say plainly when slides are image-only. Rebuild native motion if requested and do not claim a PowerPoint check that did not happen.
- Export PDF from the final complete state, including the appendix.

## 8 Verify before delivery

```bash
python3 scripts/check_deck.py presentation.html
python3 scripts/qa_render.py presentation.html qa
```

1. Both checks pass, and `check_deck.py` shows no sameness warning (stock Cinematic Night that nobody chose, or reused example photos). They fail a main slide without a real image (photo, render or screenshot); `qa_render` also renders every slide and fails on overlapping, overflowing or clipped text and broken images. Fix defects; do not exempt main slides.
2. Open `qa/contact-sheet.jpg` and the full-size slides. Check fades (no hard photo edge, subject intact, text on the quiet side), crops, focal sharpness, contrast, label spacing and rhythm across the deck.
3. Check concept and process coverage against the actual source, and each caption against what its picture shows.
4. Compare changed slides with the approved version and check protected ranges for unintended edits.
5. Confirm every web image appears in the credits ledger with creator, license and source.
6. Test navigation, entrances, autoplay stop, reduced motion, notes and print where the environment supports them, and check a 1280 × 720 and a phone viewport.
7. Compare requested formats against the same final revision, then give actual links to the files. Describe any check that could not run.

## Resources

- [web-visuals.md](references/web-visuals.md): the image-per-slide rule, content-first image plan, brand websites, web search, quality bar, licenses, credits.
- [themes.md](references/themes.md): topic themes: moods, typefaces, palette from images or brand, previews.
- [cinematic-night.md](references/cinematic-night.md): the Cinematic Night recipe, one recorded look, used when chosen.
- [visual-system.md](references/visual-system.md): direction, scale, photo treatments, image fades, Chinese typography, motion.
- [images-and-diagrams.md](references/images-and-diagrams.md): photo evidence, accurate mapping and diagram patterns.
- [content-and-evidence.md](references/content-and-evidence.md): source coverage, context, workplace application and scope control.
- [style-index.md](references/style-index.md): the adaptive preset, Cinematic Night and 46 further visual directions.
- [workflow.md](references/workflow.md): creation, PowerPoint conversion, enhancement and visual discovery.
- [implementation.md](references/implementation.md): content plan, manifest fields, HTML stage and exports.
- [motion.md](references/motion.md), [notes-and-engagement.md](references/notes-and-engagement.md), [exports-and-qa.md](references/exports-and-qa.md), [examples.md](references/examples.md), [publishing.md](references/publishing.md).
- [original-workflow.md](references/original-workflow.md): the full Frontend Slides styles, motion patterns, conversion and publishing tools.
- [portable-use.md](references/portable-use.md), [claude-use.md](references/claude-use.md), [credits.md](references/credits.md).

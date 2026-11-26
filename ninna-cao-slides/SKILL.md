---
name: ninna-cao-slides
description: Create image-rich presentations where every slide has a visual, photos fade softly into the background, and the visual direction fits each brief. Finds and credits openly licensed images on the web when the user's material runs out. Includes the Cinematic Night style (condensed headlines, typewriter labels, glowing dark stage), clear diagrams, automatic motion, render QA, and HTML, PowerPoint, PDF and speaking-note outputs.
---

# Ninna Cao Slides

Create presentations that help an audience understand an idea and how it is applied. Ninna's preferences carry across projects: a meaningful visual on every slide, photographs that fade into the stage, clear explanations and measured motion. Choose the typography, palette and composition from the specific content, audience, brand and setting. Apply the same standard of visual evidence and export quality to every style.

Read [visual-system.md](references/visual-system.md), [web-visuals.md](references/web-visuals.md) and [content-and-evidence.md](references/content-and-evidence.md) before building. Read [images-and-diagrams.md](references/images-and-diagrams.md) when choosing visuals and [cinematic-night.md](references/cinematic-night.md) when that direction fits. The complete original Frontend Slides library is available through [original-workflow.md](references/original-workflow.md). Follow the user's instructions for the current deck above these defaults.

Use the tools available in the current assistant. If you only have this file, apply its instructions directly. See [portable-use.md](references/portable-use.md) for other assistants and [claude-use.md](references/claude-use.md) for installing in Claude.

## Working principles

1. **A visual on every slide.** Each main slide carries a photograph, product image, screenshot, diagram, chart or video that explains its point. When the user's material does not cover a slide, find a suitable image on the web, check its license and record its source. Never present stock or generated images as the user's real work.
2. **Let photographs melt into the stage.** For covers, dividers, concept and closing slides, place the picture on one side and fade the edges that face the text into the background. Use crisp frames only when the audience must inspect the image.
3. **Preserve context.** Keep enough explanation for someone unfamiliar with the source to follow the presentation.
4. **Show the work.** Use photographs of interviews, observation, workshops, sketches and tests to explain what people actually do. Keep faces, hands, prototypes and other focal details sharp and visible.
5. **Design a coherent story.** Establish the main concept, explain the framework, show its application, then close with the takeaway. Fit the sequence to the actual brief.
6. **Respect approved work.** Start from the latest approved version. Preserve locked slides, wording, order and visual treatments. Make targeted improvements.
7. **Let motion run.** Run staged entrances automatically when a slide opens. Use one advance per slide and make timed autoplay optional.
8. **Keep deliverables aligned.** Use the same current content, image choices, slide numbers, appendix and notes across requested formats.

## 1 Determine scope from the existing conversation and files

Identify creation, conversion or revision first. See [workflow.md](references/workflow.md) for visual discovery, density, conversion and the delivery sequence.

- Identify the topic, audience, purpose, primary sources, brand, delivery setting, desired formats, duration, speaker split and approved reference version. Ask only for missing information that materially changes the result.
- Continue a scoped revision in the visual direction of the latest approved deck. For a new deck, derive a direction from its own brief and the references the user selected for it.
- Inspect supplied HTML/PPTX/PDF files and images before editing. Render the approved reference where possible.
- Record any protected slide range. A request such as "only my part" is a scope constraint. Do not renumber protected slides or insert new slides inside them without a reason grounded in the current request.
- Treat a request for a format conversion as a conversion task. Preserve the content and design unless the user also asks for edits.

## 2 Build the content and visual map together

For each slide, record its purpose, plain-language point, supporting evidence, **chosen visual and where it comes from** (user file, official source, open library, or a diagram you draw), and the sentence that explains the connection. Use a canonical deck manifest or an equivalent content map.

- Begin a teaching presentation with the topic or question. Introduce the workplace application after the audience has enough conceptual grounding.
- Map every required reading concept, example and process to a main slide or appendix location. Explain each number with a label, unit, period, denominator or comparison as needed.
- Make framework applications explicit: **what people did, what they learned, and what decision it informed**. Avoid a feature-by-feature product pitch when the purpose is to explain a process.
- Distinguish documented events, the presenter's interpretation, illustrative possibilities and proposed next steps. Do not present a suggested test or rollout as completed work.
- For a case drawn across several products, state that the photos illustrate practices across projects.
- Use a physical prop or a brief audience question when it strengthens the explanation. Do not add a giveaway by default.

## 3 Find the visuals

Follow [web-visuals.md](references/web-visuals.md).

- Use the user's own images first, then official sources for real products, places and events, then open libraries for atmosphere. Draw diagrams and charts instead of searching for them.
- Search open libraries with `scripts/find_images.py` (Openverse and Wikimedia Commons without a key; Unsplash and Pexels with a key). Open the contact sheet, then the full image, before choosing.
- Fetch with `scripts/fetch_image.py --manifest deck.json`: it saves a slide-ready WebP and adds the creator, license and source to the manifest's `credits`. The builder turns them into a sources and image credits slide.
- Choose pictures for the planned treatment: a dark or plain background with the subject away from the text for fades, a clear subject that survives the crop for tiles and frames, and enough pixels for the displayed size.
- If a site refuses a download, do not work around it; use the source page, ask the user or choose another image. Use only licenses that allow the deck's purpose.

## 4 Choose and apply the visual direction

Use the topic, audience, brand, delivery setting and applicable references to choose typography, palette, image treatment and slide compositions. Follow the supplied brand or approved direction when it applies. Explore the [Ninna presets and style catalog](references/style-index.md), the [complete source library](references/original-workflow.md) or a project-specific direction. When the style is open, show three authentic title-slide previews using the user's real content, then continue the chosen direction through the whole deck.

- **Cinematic Night** (`style.preset: "cinematic"`) records the dark editorial look Ninna approved in November 2026: Barlow Condensed headlines, Manrope body, Courier Prime labels, a warm charcoal stage with soft light pools, one accent (`style.accent`) and photos fading into the dark. It is a strong first candidate for product, marketing and technology talks in a dim room. See [cinematic-night.md](references/cinematic-night.md).
- Author HTML at **1920 × 1080** and scale the entire stage uniformly, including on phones.
- Choose typefaces suited to the brief. Embed bundled or supplied fonts with redistribution permission. For Chinese decks follow the CJK rules in [visual-system.md](references/visual-system.md) and subset CJK fonts.
- Start with approximately **55–100 visible words** on an explanatory slide; around 110–125 where a framework needs context.
- Keep a clear hierarchy between the headline, orienting sentence, evidence and captions. Choose one main visual action per slide and vary the composition across the story.
- Fade hero pictures with `backdrop.place` (`right`, `left`, `top-right`, `top`, `bottom`, `full`) or `.fade-plate`. Check the fade never cuts through the subject and the text sits on the quiet side.

## 5 Implement HTML and motion

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

## 6 Prepare the talk and requested exports

Read [notes-and-engagement.md](references/notes-and-engagement.md) for notes, timing, audience participation or multiple presenters, and [exports-and-qa.md](references/exports-and-qa.md) before delivery.

- Write short spoken sentences with one idea each. Key notes to visible slide numbers. Use Chinese for the speaker's understanding when requested rather than adding bilingual paragraphs to the audience's slides.
- Preserve the user's speaker split. Do not assume a fixed split, slide count or duration from a previous project.
- If a one-page speaking sheet is requested, use distinct pale colors for slide headings and bold yellow highlights for memorable phrases.
- Create requested PPTX, PDF or DOCX files with the environment's format tools. Preserve editable text, diagrams and pictures in PPTX where practical; say plainly when slides are image-only. Rebuild native motion if requested and do not claim a PowerPoint check that did not happen.
- Export PDF from the final complete state, including the appendix.

## 7 Verify before delivery

```bash
python3 scripts/check_deck.py presentation.html
python3 scripts/qa_render.py presentation.html qa
```

1. Both checks pass. `check_deck` fails a main slide without a visual; `qa_render` renders every slide and fails on overlapping, overflowing or clipped text, broken images and slides with no visible visual. Fix defects; do not exempt main slides.
2. Open `qa/contact-sheet.jpg` and the full-size slides. Check fades (no hard photo edge, subject intact, text on the quiet side), crops, focal sharpness, contrast, label spacing and rhythm across the deck.
3. Check concept and process coverage against the actual source, and each caption against what its picture shows.
4. Compare changed slides with the approved version and check protected ranges for unintended edits.
5. Confirm every web image appears in the credits ledger with creator, license and source.
6. Test navigation, entrances, autoplay stop, reduced motion, notes and print where the environment supports them, and check a 1280 × 720 and a phone viewport.
7. Compare requested formats against the same final revision, then give actual links to the files. Describe any check that could not run.

## Resources

- [web-visuals.md](references/web-visuals.md): the visual-per-slide rule, where to look, search and fetch scripts, licenses, credits.
- [cinematic-night.md](references/cinematic-night.md): the Cinematic Night recipe, fades, layouts and rhythm.
- [visual-system.md](references/visual-system.md): direction, scale, photo treatments, image fades, Chinese typography, motion.
- [images-and-diagrams.md](references/images-and-diagrams.md): photo evidence, accurate mapping and diagram patterns.
- [content-and-evidence.md](references/content-and-evidence.md): source coverage, context, workplace application and scope control.
- [style-index.md](references/style-index.md): Ninna presets and 46 further visual directions.
- [workflow.md](references/workflow.md): creation, PowerPoint conversion, enhancement and visual discovery.
- [implementation.md](references/implementation.md): content plan, manifest fields, HTML stage and exports.
- [motion.md](references/motion.md), [notes-and-engagement.md](references/notes-and-engagement.md), [exports-and-qa.md](references/exports-and-qa.md), [examples.md](references/examples.md), [publishing.md](references/publishing.md).
- [original-workflow.md](references/original-workflow.md): the full Frontend Slides styles, motion patterns, conversion and publishing tools.
- [portable-use.md](references/portable-use.md), [claude-use.md](references/claude-use.md), [credits.md](references/credits.md).

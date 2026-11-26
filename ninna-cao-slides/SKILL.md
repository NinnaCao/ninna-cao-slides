---
name: ninna-cao-slides
description: Create image-rich presentations with a visual direction chosen for each brief, clear diagrams, useful context and automatic motion. Use for HTML, PowerPoint, PDF and speaking notes.
---

# Ninna Cao Slides

Create polished presentations that help an audience understand an idea and how it is applied. Ninna's presentation preferences carry across projects. The typography, palette, atmosphere and composition follow each brief. This skill includes the fixed-stage Frontend Slides foundation by Zara Zhang.

Read [visual-system.md](references/visual-system.md) and [content-and-evidence.md](references/content-and-evidence.md) before building. Read [images-and-diagrams.md](references/images-and-diagrams.md) when choosing visuals. Keep the user's current instructions above these defaults.

## Working principles

1. **Preserve context.** Keep enough explanation for someone unfamiliar with the source to follow the presentation.
2. **Show the work.** Use photographs of interviews, observation, workshops, sketches and tests to explain what people actually do. Give each visual a clear relationship to the idea being taught.
3. **Choose visuals for the brief.** Use clear diagrams, meaningful images and intentional composition. Keep faces, hands, prototypes and other focal details sharp and visible.
4. **Design a coherent story.** Establish the main concept, explain the framework, show its application, then close with the takeaway. Fit the sequence to the actual brief.
5. **Respect approved work.** Start from the latest approved version. Preserve locked slides, wording, order and visual treatments. Make targeted improvements.
6. **Let motion run.** Run staged entrances automatically when a slide opens. Use one advance per slide and make timed autoplay optional.
7. **Keep deliverables aligned.** Use the same current content, image choices, slide numbers, appendix and notes across requested formats.

## 1 Determine scope from the existing conversation and files

- Identify the topic, audience, purpose, primary sources, brand, delivery setting, desired formats, duration, speaker split and approved reference version. Ask only for missing information that materially changes the result.
- Continue a scoped revision in the visual direction of the latest approved deck. For a new deck, derive a direction from its own brief and the references the user selected for it.
- Inspect supplied HTML/PPTX/PDF files and images before editing. Render the approved reference where possible.
- Record any protected slide range. A request such as "only my part" is a scope constraint. Do not renumber protected slides or insert new slides inside them without a reason grounded in the current request.
- Treat a request for a format conversion as a conversion task. Preserve the content and design unless the user also asks for edits.

## 2 Build the content and visual map together

For each slide, record its purpose, plain-language point, supporting evidence, chosen visual and the sentence that explains the connection. Use a canonical deck manifest or an equivalent content map.

- Begin a teaching presentation with the topic or question. Introduce the workplace application after the audience has enough conceptual grounding.
- Map every required reading concept, example and process to a main slide or appendix location. Keep essential ideas in the main talk. Explain each number with a label, unit, period, denominator or comparison as needed.
- Make framework applications explicit: **what people did, what they learned, and what decision it informed**. Avoid a feature-by-feature product pitch when the purpose is to explain a process.
- Distinguish documented events, the presenter's interpretation, illustrative possibilities and proposed next steps. Do not present a suggested test or rollout as completed work.
- For a case drawn across several products, state that the photos illustrate practices across projects. Do not imply that a keyboard interview or headset fit test proves a specific mouse outcome.
- Use a physical prop or a brief audience question when it strengthens the explanation. Connect a giveaway to the learning point if the user asks for one. Do not add a giveaway by default.

## 3 Choose and apply the visual direction

Use the topic, audience, brand, delivery setting and applicable references to choose typography, palette, image treatment and slide compositions. For example, a projected workshop may call for high-contrast sans typography and crisp image panels. A reflective talk may call for quieter type and an atmospheric photograph. Follow the supplied brand system when it applies. When the context gives a clear direction, carry it into the deck directly.

- Author HTML at **1920 × 1080** and scale the entire stage uniformly, including on phones.
- Choose and embed licensed typefaces suited to the brief and delivery conditions. Each starter preset is an explicit selection. Use project CSS for a different direction.
- Start with approximately **55–100 visible words** on an explanatory slide. Allow around 110–125 where a framework needs context. Adjust the density to the content, audience and presentation distance.
- Keep a clear hierarchy between the headline, orienting sentence, evidence and captions. Choose one main visual action per slide and vary the composition across the story.
- Pair a photo with an explanation, connect observations in a diagram, sequence an activity in photos or compare distinct prototype forms as the slide requires.
- Choose whether a photo works best in a crisp frame, as a full image, as part of a sequence or blended into the stage. Use a gradient when it supports the direction and makes the reading area clearer.

See [visual-system.md](references/visual-system.md) for choosing the direction and composition. See [images-and-diagrams.md](references/images-and-diagrams.md) for photo selection and diagram recipes.

## 4 Implement HTML and motion

Use `assets/deck-shell.html`, `assets/viewport-base.css`, the shared layout and runtime, and `assets/deck-controller.js`. Apply one chosen preset or the project's own stylesheet. Keep the full MIT-licensed Frontend Slides viewport base and attribution.

The optional portable builder accepts a deck manifest with authored slide body HTML:

```bash
python3 scripts/build_deck.py assets/example-deck.json /path/to/deck.html
python3 scripts/check_deck.py /path/to/deck.html
```

Read [implementation.md](references/implementation.md) for the manifest, presets and project styling. Each sample demonstrates a different composition for its particular brief.

- Inline CSS, JavaScript, images and fonts in the downloadable HTML. Do not depend on a development server, CDN or an online font request.
- Keep semantic `.slide` sections and use visibility, opacity and pointer-events for switching. Do not use display-based slide switching.
- Give images meaningful alt text. Keep exact diagrams as SVG or native shapes with legible labels.
- Use restrained automatic fades, 8–16 px translations and sequential SVG tracing. Reveal useful content within about 1.5–2 seconds. Do not loop decorative motion behind reading text.
- Support keyboard navigation, visible navigation controls, fullscreen, reduced motion, and private notes. Keep controls outside the authored slide canvas.
- If autoplay is enabled, derive timings from the actual talk and stop on the last main slide. Do not advance automatically into the appendix. Pause when the tab is hidden.
- Make the print state show all content in its final state, one slide per page, with controls and private notes hidden.
- Add optional text editing only if it is useful; keep it off during normal presenting. Treat it as an extra feature, not a reason to delay an otherwise complete deck.

## 5 Prepare the talk and requested exports

Read [notes-and-engagement.md](references/notes-and-engagement.md) when notes, timing, audience participation or multiple presenters are involved. Read [exports-and-qa.md](references/exports-and-qa.md) before delivery.

- Write short spoken English with one clear idea per sentence. Keep notes keyed to visible slide numbers. Use Chinese for the speaker's understanding when requested, rather than adding bilingual paragraphs to the audience's slides.
- Preserve the user's speaker split. Do not assume a fixed split, slide count or duration from a previous project.
- If a one-page speaking sheet is requested, use distinct pale colors for slide headings and bold yellow highlights for the memorable phrases. Keep the English script and Chinese memory cues together. Do not add a page break after every slide.
- Use the format tools available in the current environment to create requested PPTX, PDF or DOCX files. Apply this skill's content and design rules together with the environment's format-specific instructions.
- Preserve editable text, diagrams and pictures in PPTX where practical. Explain a material fallback such as image-only slides instead of implying they are fully editable.
- Rebuild native PowerPoint motion if requested. CSS animations do not transfer automatically. Do not claim a working PowerPoint preview unless it was actually checked there.
- Export PDF from the final complete state. Check the entire deck and appendix, not just the currently active HTML slide.

## 6 Verify before delivery

Run the bundled static check on generated HTML. It is an audit aid, not visual proof.

1. Check concept and process coverage against the actual source.
2. Inspect rendered slides at 1280 × 720 and a phone viewport. Verify uniform scaling, readable captions, image loading, sharp focal subjects, contrast, label spacing and absence of overlap.
3. Compare changed slides with the approved version. Check protected ranges for unintended edits.
4. Check that each process photo has an accurate caption and supports the process stage claimed for it.
5. Test navigation, automatic entrances, optional autoplay stop, reduced motion, hidden-tab pause, notes and the print state when the environment supports them.
6. Compare requested formats against the same final revision. Check content parity, slide count, order, images, appendix boundary and notes.
7. Open or validate the final files and give actual download links. If a preview or native-app check could not run, describe only that limitation and what was checked.

## Resources

- [visual-system.md](references/visual-system.md) for choosing typography, palette, image treatment and composition.
- [images-and-diagrams.md](references/images-and-diagrams.md): photo evidence, accurate mapping and reusable diagram patterns.
- [content-and-evidence.md](references/content-and-evidence.md): source coverage, context, workplace application and scope control.
- [notes-and-engagement.md](references/notes-and-engagement.md): scripts, timing, speaker split and audience participation.
- [implementation.md](references/implementation.md): portable builder, manifest and runtime contract.
- [exports-and-qa.md](references/exports-and-qa.md): HTML/PPTX/PDF/DOCX parity and final checks.
- [claude-use.md](references/claude-use.md): upload and invocation instructions.
- [credits.md](references/credits.md): foundation, fonts and attribution.

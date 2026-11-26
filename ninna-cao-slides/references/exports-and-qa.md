# Exports and QA

## Maintain one final revision

Keep the current slide content map, source assets and notes together. For requested HTML, PPTX, PDF and DOCX outputs, compare titles, meaning, evidence, image choices, slide order and numbers before delivery. An HTML export with an old deck's PowerPoint is not a matching set just because the filenames are similar.

Use the user's latest approved deck as the visual reference. Preserve locked sections and scope. If an export is the only request, do not redesign the presentation or rewrite its argument.

For a new deck, check the typography, color, image treatment and compositions against its brief. Check that each requested format carries that direction through.

## Visual checks (v3)

Run both checks on every HTML deck before delivery, then look at the contact sheet yourself:

```bash
python3 scripts/check_deck.py presentation.html     # structure, visuals per slide, credits ledger
python3 scripts/qa_render.py presentation.html qa  # renders each slide; overlaps, overflow, clipping, image resolution
```

- Every main slide has a real image (photo, render or screenshot), in front or as an ambient background. Fix a failure by adding one, not by exempting the slide.
- Every image meets the quality bar in web-visuals.md: on-subject, on-brand, sharp, well cropped, authentic.
- No text overlaps other text, leaves the stage or is clipped. Treat each `qa_render` error as a real defect.
- Fades: no visible photo edge, the subject is not cut by the fade, body text sits on the quiet side, contrast is comfortable.
- Images are not shown larger than their pixels on hero placements.
- The sources and image credits slide lists every image found online, with creator, license and source.

## HTML

- Deliver one HTML file with embedded fonts, CSS, JavaScript and local images where practical.
- Open it without a development server or network connection when the environment permits.
- Check the 1920 × 1080 stage at 1280 × 720 and at a portrait phone viewport. Letterboxing is expected. Content reflow is not.
- Verify the image focal region, sharpness, contrast, label spacing, notes, keyboard controls and animation final state.
- Verify that a hidden tab pauses autoplay and that autoplay stops before the appendix.
- Keep private notes and editing controls out of print.

## PowerPoint

Use the presentation and file tools available in the current environment. Apply this skill's visual and content guidance to the native PowerPoint generation or conversion workflow.

Rebuild text, diagrams and photos as editable objects where feasible. Keep fonts, geometry, photo crops and the content hierarchy. A browser-only mask or tracing effect may require a native substitute. CSS motion does not become PowerPoint animation by changing the extension.

Use restrained native fades or suitable transitions if animation is requested. Set automatic entrance groups so that opening a slide does not require repeated clicks. Keep slide advance manual unless the user requests timed playback. Keep the appendix out of the automatic talk sequence.

If a file is image-only, say so. Do not describe it as fully editable. Check the package structure, relationships, slide count, image embedding, notes and any animation targets, and render the slides. Do not say it was tested in PowerPoint unless the native app was actually used.

## PDF

Render the final complete HTML or the corresponding final PowerPoint into a static PDF. Use the final-state print styling when exporting HTML. Wait for images and fonts to load, and include every main and appendix slide.

Use `scripts/export_pdf.py` (default `--engine screens`): it renders each slide's final state in Chrome and builds a pixel-exact PDF with web links kept clickable. Browser print ignores CSS masks, so the `browser` engine shows hard edges on faded photos; use it only when selectable text matters more than fades, and inspect it. If no browser is available, use the `static` fallback, inspect its output, and describe the limitation. Do not keep retrying a blocked browser or silently substitute an outdated PDF.

Check one slide per page, correct 16:9 dimensions, text clarity, photographs, diagrams and appendix boundary. Check the whole export, not just the first page. A PDF correctly loses animation and interactivity; its content must remain complete.

## Speaking documents

Use the final slide numbers and current speaker split. Keep colored headings and highlighted phrases intact. Render Word documents to inspect spacing, page count and Chinese glyph support. Do not create an additional document for every language when the user wants English and Chinese together.

## Review sequence

1. Read the deck as an audience member. Can someone understand the topic without the conversation that created it?
2. Trace the required source concepts, processes and examples to their locations.
3. Inspect image and diagram mappings. Is each claimed activity visible or explained accurately?
4. Render the whole deck (`qa_render.py`). Use the contact sheet for sequence and visual rhythm, and individual full-size views for fit, fades and clarity.
5. Compare changed slides to the approved reference and inspect protected sections for drift.
6. Test interaction and print behavior where supported. Keep structural checks separate from native-app execution claims.
7. Compare formats for the current revision and deliver only requested final files with working links.

Use structural checks alongside visual review, fact checking and interaction checks.

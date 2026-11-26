# Original Frontend Slides workflow

Ninna Cao Slides includes the complete Frontend Slides source by Zara Zhang. The original distribution is in [frontend-slides](frontend-slides/README.md) with its [MIT license and copyright notice](frontend-slides/LICENSE). Use this guide to select and apply its resources inside the Ninna Cao Slides workflow.

## Choose a direction from the brief

A user may bring an existing deck, a brand system, a named original style or a specific aesthetic. Apply that choice directly when the brief is clear. When style is open, show three covers with the same real content and assets. Include one broadly readable direction, an expressive direction from the source library or Ninna catalog, and a third direction that gives the audience a useful comparison. Open previews through the available preview surface and provide direct links.

- To select from the source library, read its [12 preset specifications](frontend-slides/STYLE_PRESETS.md) and [34-template index](frontend-slides/bold-template-pack/selection-index.json).
- For a shortlisted template, use its small preview card. Read the selected template's full design files from the same directory once the direction is settled. Carry its typography, palette, composition, distinctive details and motion through the entire deck.
- Use the [Ninna catalog](style-index.md) or a project-specific direction when either fits the brief. Retain the selected direction across HTML, PDF and PowerPoint.

## Generate, convert and enhance

| Job | Source reference or helper |
| --- | --- |
| Create or redesign a deck | [Original workflow](frontend-slides/WORKFLOW.md), [HTML structure and interactions](frontend-slides/html-template.md), and [fixed stage](frontend-slides/viewport-base.css). |
| Use a design from the 34-template pack | [Pack instructions](frontend-slides/bold-template-pack/README.md), the selected design and the [stage runtime](frontend-slides/bold-template-pack/deck-stage.js). |
| Choose effects | [Motion patterns](frontend-slides/animation-patterns.md) for entrances, ambient effects and interactions. Select effects that serve the audience and delivery. |
| Import a PowerPoint | [Original extractor](frontend-slides/scripts/extract-pptx.py), or the expanded inventory tool in [implementation.md](implementation.md). Verify order, notes, images and source content. |
| Export the original HTML to PDF | [Original PDF helper](frontend-slides/scripts/export-pdf.sh) with standard or compact output. See [exports-and-qa.md](exports-and-qa.md) for visual verification. |
| Publish an audience copy | [Original deployment helper](frontend-slides/scripts/deploy.sh) or the available host. Follow [publishing.md](publishing.md) when the user has asked for a live link. |

Use the unpacked references and tools for normal work. The downloadable universal package also carries the byte-identical original source ZIP under `assets/source/Frontend_Slides_Original.zip`, including both original distribution layouts and their metadata. Keep original credits and license text with redistributions of the source.

## Preserve behavior and apply enhancements

Keep the 1920 × 1080 authored stage, keyboard, mouse wheel and swipe, edit toggle and persistent local draft, and downloadable edited copy when supported by the browser. Use optional atmospheric or interactive effects only when they strengthen the slide. Honor reduced motion. For an approved exact design, follow the original design and runtime conventions.

Use Ninna's presentation workflow whether the selected direction comes from either library or the brief itself. Keep photos relevant and intentional, show the relationship or process with a diagram, preserve meaningful context and approved scope, and start slide entrances automatically. When requested, prepare timed playback, accessible notes, an appendix and matched HTML, PDF, PowerPoint and Word files. Native editable PowerPoint and animation rely on the chosen platform's presentation tools. Keep speaking notes out of the shared audience edition unless the user asks to include them.

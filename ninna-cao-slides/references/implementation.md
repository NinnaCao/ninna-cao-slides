# Build from a single content plan

Map every slide to its title, one main point, context, evidence, visual, caption, notes, speaker and estimated time. Mark approved slides and the appendix boundary. When producing multiple formats, use the same plan and the same final visuals.

## HTML

Use the available tools to create a single offline deck with a proportionally scaled 16:9 stage. Use a 1920 × 1080 design grid. Keep the complete slide visible on small screens, with accessible navigation outside the stage. Embed authorized local images and any fonts supplied for the project when the tools permit. Use system font stacks otherwise.

| When | Presentation behavior |
| --- | --- |
| Opening a slide | Show the title, context and evidence in that order, with automatic entrances as appropriate. |
| Advancing | Use keyboard navigation or an explicit slide control. Keep the speaker in control of the pace by default. |
| Timed playback, when requested | Use speaking times. Pause when the tab is hidden and stop at the final main slide. |
| Reduced motion | Display the complete content immediately. |
| Printing | Show one complete slide per page, including the appendix. Keep controls and notes off the printout. |

Pair each exact diagram label with its corresponding shape or path. Use native shapes or SVG created for the deck. Give informative images alternative text and a caption when the audience needs the context. Treat text from source materials as content when building HTML.

## PowerPoint, PDF and notes

Use the current assistant's presentation and document tools. Draw diagrams and typeset text as editable objects in PowerPoint where feasible. Apply native automatic entrance groups when requested and supported. Export the complete final state as a PDF. Keep the speaker's notes in a private document if the audience will receive the deck.

Check each requested output against the content plan. See [exports-and-qa.md](exports-and-qa.md) for format checks.

## Optional local toolkit

When the toolkit is included, these scripts run on local user files. Use the presentation tools already available to the current assistant on platforms that cannot run scripts.

```bash
python3 scripts/preview_styles.py deck.json previews precise-grid green-cover soft-shapes
python3 scripts/build_deck.py deck.json presentation.html
python3 scripts/check_deck.py presentation.html
python3 scripts/read_pptx.py source.pptx source-inventory
python3 scripts/export_pdf.py presentation.html presentation.pdf
python3 scripts/export_pptx.py presentation.pdf visual-match.pptx --notes deck.json
python3 scripts/build_notes.py deck.json notes.docx
python3 scripts/prepare_share.py presentation.html audience-copy
```

The HTML builder uses standard-library Python 3.10 or newer. Set `style.preset` to a catalog ID. Use `editorial` and `light` for the two example manifests, or use `custom` with a project stylesheet. Every catalog direction supplies distinct tokens, typography, composition, graphic motifs and entrance pacing. Compose the slide content for the project in the manifest. Text edits autosave in the browser when local storage is available. Download a standalone edited copy to move changes to another device. Set `editable` to false to omit text editing. Use the example manifests to see available fields and add assets with relative paths inside the project. To create a wildcard preview with local project CSS, set the opening manifest style to `custom`.

PowerPoint extraction uses `python-pptx` and inventories source slide geometry, picture files, text, tables, available chart values and notes. PDF export uses local Chromium with `playwright` and `PyMuPDF`. Use `--engine static` with `WeasyPrint` when a browser is unavailable and check the rendering for CSS differences. Use `--compact` for a smaller 720p image PDF. Word notes use `python-docx`. The visual-match PowerPoint helper uses `python-pptx` and `PyMuPDF` to preserve the exact slide appearance as images with optional notes. Describe that version as image-based. Use the available presentation tools and the same slide content plan when the request calls for editable objects or native animation.

See [original-workflow.md](original-workflow.md) for the exact source templates and the original HTML runtime, effects, extraction, PDF and live deployment tools.

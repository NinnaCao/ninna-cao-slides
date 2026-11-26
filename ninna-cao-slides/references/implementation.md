# Portable implementation

`scripts/build_deck.py` combines authored slide HTML, the full fixed-stage viewport base, shared layout, the selected style, fonts and the controller into one file. It uses the Python 3 standard library.

The manifest is a common content map for HTML, speaking notes and native exports. Use the available format tools for an editable PowerPoint or related export.

```bash
python3 scripts/build_deck.py assets/example-deck.json /path/to/editorial.html
python3 scripts/build_deck.py assets/example-light-deck.json /path/to/light.html
python3 scripts/check_deck.py /path/to/light.html
python3 scripts/build_notes.py assets/example-light-deck.json /path/to/notes.docx
```

The two examples select different visual directions explicitly. `build_notes.py` uses `python-docx`. Render the result with the available document tools to check page count and fit.

## Manifest

```json
{
  "title": "Presentation title",
  "author": "Presenter",
  "style": { "preset": "light" },
  "slides": [
    {
      "id": "slide-1",
      "title": "The subject",
      "section": "Concept",
      "speaker": "Presenter",
      "duration_seconds": 45,
      "subtitle": "One sentence orienting the audience.",
      "body_html": "<div class=\"text-region\"><p>Authored content.</p></div>",
      "notes_en": "The spoken explanation.",
      "notes_zh": "中文记忆提示",
      "key_phrases": ["spoken explanation"],
      "sources": []
    }
  ]
}
```

Choose `style.preset` from `editorial`, `light` and `custom` to match the brief. Choose `layout: "cover"` for the large opening composition. Regular slides use `layout: "content"`. Place any `appendix: true` slides after the last main slide.

| Slide field | Use |
| --- | --- |
| `theme` | Optional lowercase variant name emitted as `theme-<name>`. Editorial provides `warm` and its base cool palette. Light provides `highlight`. Define brand variants in project CSS. |
| `slide_class` | Optional class names for a stage-level composition. |
| `body_class` | Optional class names for the body region. |
| `title_html` | Authored headline markup for deliberate line breaks. |
| `title_lines` | `2` moves the subtitle and body down on regular content slides. |
| `body_top` | Optional fixed-stage pixel position in the range 300–850. The chosen stylesheet sets the usual positions. |
| `background_image` | Path to decorative backdrop imagery, interpreted by the selected stylesheet. |
| `background_position` | CSS object position, such as `"70% 40%"`. |
| `source_credit` | Short visible credit. Keep detailed provenance in `sources` and the appendix. |

Use trusted authored HTML in `body_html` and `title_html`. Escape any source text you insert. Use `{{asset:path/to/file.jpg}}` in image tags, SVG image references or CSS `url()` to embed an image, video or audio file. Paths resolve from the manifest directory. Give substantive images meaningful alternative text and visible captions. Decorative backdrops are hidden from assistive technology.

The sample SVGs illustrate possible layouts and activities. Use available documentary media for claims about actual interviews, workshops or tests.

## Project styling

`style.css` embeds a local stylesheet after the preset. The `custom` preset requires it and starts with shared neutral layout helpers. It embeds only the fonts listed in `style.fonts`. Supply project assets and licensed local fonts alongside the manifest.

```json
{
  "preset": "custom",
  "css": "styles/brand.css",
  "fonts": [
    {
      "family": "Project Sans",
      "file": "fonts/project-sans.woff2",
      "weight": "100 900",
      "style": "normal"
    }
  ]
}
```

Place this object under `style`. Font files can be TTF, OTF, WOFF or WOFF2. Set the weight for each static face or a range for a variable font. Paths stay within the project directory. Use system font stacks when a supplied font is unnecessary. Use local asset tokens in project CSS to keep the output self-contained.

```css
:root {
  --heading-font: "Project Sans", Arial, sans-serif;
  --body-font: "Project Sans", Arial, sans-serif;
  --stage-bg: #202f27;
}
.slide {
  --slide-bg: #f5f3e9;
  --text: #25372c;
  --muted: #3e5648;
  --accent: #24583e;
  --secondary: #8b431f;
  --rule: #88a492;
  --slide-margin: 130px;
}
.slide.theme-field { --slide-bg: #e4efe4; }
.slide.image-led .slide-title { width: 830px; font-size: 74px; }
.slide.image-led .slide-body { right: 900px; }
.slide.image-led .backdrop { inset: 115px 130px 118px auto; width: 700px; }
```

Use `theme: "field"` and `slide_class: "image-led"` on a slide built for those styles. Design a clean reading area when using a backdrop. Override type, header, body, footer, image geometry or an authored figure as the brief requires. Preserve the stage size, runtime classes, slide visibility and final print state.

## Shared HTML helpers

- `.slide-header` groups the optional `.kicker`, title and optional subtitle.
- `.columns-2` and `.columns-3` create fixed-stage columns with a gap. Override column sizes to reflect hierarchy.
- `.display` styles a short statement in the chosen heading face. `.label` provides an orientation label. `.caption` explains a figure.
- `.photo-frame` crops an image inside a region with an explicit height. Add `.screen` to fit the whole image.
- `.reveal` triggers an entrance when the slide opens. Set `style="--delay:240ms"` to sequence a related group.
- `.trace` and `pathLength="1"` trace a path in an inline SVG.

For SVG labels, give `text` elements explicit `fill` and `font-family` values that fit the deck. Some PDF engines handle embedded SVG and CSS variables differently from browsers.

## Browser controls and exports

The controller scales the stage and activates each slide, including its automatic entrances. It leaves navigation keys available to inputs and editable regions.

| Key | Action |
| --- | --- |
| Right Arrow, Page Down, Space | Next slide |
| Left Arrow, Page Up | Previous slide |
| Home, End | First slide or last main slide |
| P | Toggle timed autoplay |
| N | Toggle private notes |
| Q | Open the appendix |
| F | Toggle fullscreen when supported |
| Escape | Close notes |

Autoplay uses the slide's `duration_seconds`. It pauses when the tab is hidden or notes open and stops on the last main slide. Click the controls or use a horizontal swipe on touch devices to navigate. Slides print in final state at one per 1920 × 1080 page, with notes and controls hidden.

The `deck-manifest` and `deck-notes` JSON blocks are backstage material inside the file. They are accessible to anyone with the HTML. Review them before distributing the HTML to an audience.

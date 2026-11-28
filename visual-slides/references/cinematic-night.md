# Cinematic Night

A dark editorial direction recorded from an approved product-marketing deck (November 2026): photographs and product renders dissolve into a warm charcoal stage, condensed headlines hit hard, typewriter labels keep order, and one hot accent carries attention. It is one recorded look, not the default: use it when the user asks for it or continues a deck made with it. For every other deck, make the look from the topic (see [themes.md](themes.md)); the fade and visual rules still apply.

`style.preset: "cinematic"` in a manifest applies it (the adaptive component system with the token theme `assets/themes/cinematic.css`), with the fonts embedded automatically. `style.accent` swaps the orange for a colour from the topic. See `assets/example-cinematic-deck.json` for every layout below.

## Type

| Role | Face | Size at 1920 × 1080 |
| --- | --- | --- |
| Cover title | Barlow Condensed 800, line-height .84, tracking −.039em | 200–236 px |
| Divider / statement title | Barlow Condensed 800, line-height .86 | 147–177 px |
| Slide title | Barlow Condensed 700, line-height .94, tracking −.025em | 96–112 px |
| Display numbers and card numerals | Barlow Condensed 800 | 46–300 px |
| Subtitle (deck line) | Manrope 500, muted | 30–37 px |
| Body and card text | Manrope 500–800 | 24–31 px |
| Kickers, labels, folio | Courier Prime 700, uppercase, tracking .1–.12em | 16–21 px |

Keep titles to one or two lines. Emphasis is accent colour (`<em>` is not italic). End a cover title with an accent full stop: `<span class="dot">.</span>`.

## Colour

- Stage `#0e0f13`, text `#f4f0e9`, muted `#cdc7c1`, hairlines `#ffffff2e`, cards `#1d1f29e8`.
- One accent, default orange `#ff7338`. Set the brand's with `style.accent`; the lighter label colour (`--accent-ink`), paper-slide accent and glows derive from it.
- Light pools: every slide has two soft radial glows. Pick one per slide with `glow`: `ember` (accent), `rust`, `indigo`, `violet`, `plum`, `steel`, `teal`, `none`, plus `left` to mirror. Vary them through a section so consecutive slides do not look identical.
- Paper slides (`theme: "paper"`, `#f0ece5`) for one calm or reading-heavy slide in every six to eight. Product shots on white backgrounds melt into paper with `class="multiply"`.

## Image fades

Every hero picture sits on one side and fades toward the text. Use `backdrop` in the manifest:

```json
"backdrop": {"image": "media/hero.webp", "place": "right", "start": 40, "fade": 28,
             "focus": "30% 40%", "brightness": 1.2, "alt": "What the picture shows"}
```

| place | Use | Defaults |
| --- | --- | --- |
| `right` | Cover, divider, concept slide with text on the left | starts at 36%, left 34% of the picture fades |
| `left` | Mirror of `right` | |
| `top-right` | Title top-left, cards or a flow across the bottom | starts at 52%, 58% tall, fades left and down |
| `top` | Wide scene above a row of content | 64% tall, fades down |
| `bottom` | Scene under a statement | |
| `full` | Closing or statement slide; scrim on the left (or `scrim: "bottom"`) | |
| `ambient` | Behind a diagram, chart, table or text-led slide, so every slide still has a real image | full slide, opacity 0.32, vignette toward `at` (default `80% 35%`); optional `blur` |

- `start` moves the picture's left edge (percent of the slide), `height` sets its height for top and bottom places, `fade` sets the fade length, `focus` is `object-position`, `brightness` lifts dark photos (1.1–1.3 is typical).
- Put the subject at least 200 px clear of the nearest text. Check the crop at full size: the fade must never cut through a face or the product's key detail.
- Use `<figure class="fade-plate place-right settle" style="left:…;top:…;width:…;height:…">` for the same effect inside the slide body.
- The picture settles from 103.5% to 100% scale when the slide opens. Print shows the settled state.

## Layouts

| Layout | Build | Notes |
| --- | --- | --- |
| Cover | `layout: "cover"`, backdrop `right`, presenter and `.meta` line in the body | Brand mark in `section` or the body |
| Agenda | `.tiles` with three or four image tiles | Image fades into the text below; big accent numerals |
| Section divider | `layout: "divider"`, `number_label`, backdrop `right`, `.marks` list | Outlined numeral, title 168 px |
| Concept with picture | backdrop `right` or `top-right`, `.rows` or `.cards` | Add `slide_class: "narrow"` to keep the title off the picture |
| Steps or guardrails | backdrop `top-right`, `.cards` with `label` "01 · READ" | Optional `.takeaway` line at the bottom |
| Flow | `.flow` (arrows between steps) or an SVG diagram | The diagram is the slide's visual |
| Numbers | `.stats` beside a related picture | Label what each number counts |
| Inspectable image | `.frame` with mono caption bar | For screenshots, renders, UI |
| Statement or closing | `layout: "statement"`, backdrop `right` or `full`, `.marks` | Three takeaways at most |
| Sources | Generated from `credits` and `sources` | Appendix, text-only by design |

Kicker: `section` text with `section_number` ("01", "Part 02") in an accent chip. Footer folio: deck title and section on the left (`source_credit`), page number on the right.

## Rhythm for a 20–40 slide talk

Cover → agenda tiles → for each part: divider, three to six content slides (alternate picture-led and diagram-led), one paper slide where reading helps → closing statement with takeaways → appendix divider → appendix → sources and credits.

## Motion

Entrances 650 ms with `cubic-bezier(.19, 1, .22, 1)`, 100–130 ms between related groups, the headline first. Diagram paths trace after their nodes appear. Pictures settle once. Nothing loops behind text.

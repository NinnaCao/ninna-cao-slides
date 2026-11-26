# Visual direction and composition

## Define the direction for this brief

Start with the audience, what they need to learn or decide, the subject, brand, viewing distance or reading context, and any reference selected for this deck. For a scoped revision, continue the approved direction. For a new deck, make fresh choices from this brief.

| What the brief tells you | What to choose |
| --- | --- |
| A live session in a large or bright room | Strong foreground contrast, large labels and diagrams with generous spacing |
| A deck people will read on their own | Clear section hierarchy, explanatory figure captions and context that survives export |
| A brand or approved reference applies | Its type, colors, image treatment and layout conventions |
| Human action is the evidence | A crop that shows the person, setting and relevant behavior |
| A relationship or decision is the evidence | A labeled diagram with space around the steps, comparisons or feedback paths |

Write down the direction in a sentence while planning the deck. Choose type, palette, visual treatments and a few compositions that fit together. Proceed directly when the brief makes the choice clear. Use style exploration when the user asks for options or when a material decision remains open.

See [style-index.md](style-index.md) for the style library and [examples.md](examples.md) for two directions extended across several slides. An earlier deck supplies a visual precedent when the user carries that reference into the new brief.

## Scale and hierarchy

Use the fixed 1920 × 1080 stage for HTML. For a common exposition slide, 90–110 px side margins, 70–100 px titles, 28–36 px body and 22–28 px captions offer starting proportions. Test the chosen type and layout at the intended viewing distance. Move the content region when the headline wraps. Give the title, orientation, evidence and supporting labels distinct weight and space.

Keep strong alignment through a section. Use open space to show relationships. Let the composition change when the evidence changes, such as moving from a full photographic moment to an exact diagram or a sequence of prototype forms.

## Treat photographs according to their job

Every slide has a visual ([web-visuals.md](web-visuals.md)). Decide each one's job:

- **Atmosphere, subject or hero picture: fade it into the stage.** This is Ninna's preferred treatment for covers, dividers, concept slides and closings. Place the picture on one side and let the edges that face the text dissolve into the slide background, so there is no hard photo edge and the glow of the slide shows through. See *Image fades* below.
- **Evidence the audience must inspect** (a screenshot, a research photo, a prototype): a crisp frame, diptych or sequence with a caption.
- **Several parts or options:** image tiles whose lower edge fades into the label below.
- **Diagram, chart, table or text in front:** the photo goes behind it as an ambient background (`place: "ambient"`): full slide, dimmed to roughly 20–40% and vignetted toward one corner, so it sets the scene without competing with the content.

Preserve the sharpness of the face, hands, object or activity that matters, and keep it clear of the fade.

## Image fades

The recipe, implemented as `backdrop.place` and `.fade-plate` in `assets/deck-layout.css` for every preset:

1. Put the picture in a box on one side (`right`, `left`, `top-right`, `top`, `bottom`) or full-bleed.
2. Mask the box with a linear gradient from transparent to opaque over roughly the first third facing the text (`mask-image`). The slide's own background and glows show through the transparent part.
3. Add a scrim in the slide's background colour on the text side and along the bottom, inside the masked box, to deepen shadows.
4. Lift dark photos slightly (`brightness` 1.1–1.3) so the subject reads after the fade.
5. Let the picture settle once (scale 1.035 → 1) when the slide opens.

Pictures that fade well have a dark or plain background and the subject on the far side from the text. Check at full size that the fade never cuts through a face or the subject's key detail, that body text sits on the quiet part of the slide, and that the picture edge is invisible. A full-bleed picture needs a stronger scrim behind the text.

Place dense diagram labels on a quiet, high-contrast surface. Preserve the photo's proportions and choose a crop for the action. Show a screenshot at a size that lets the audience inspect the relevant controls, text or interface state.

## Choose a composition for the content

| Content need | Composition |
| --- | --- |
| Introduce a concept | Title, short explanation and one meaningful image or diagram |
| Explain a framework | Large labeled diagram and a short description of what happens at each stage |
| Connect observations | Two evidence areas converging into one shared question |
| Explain a workshop | A photo sequence captioned with activity and output |
| Compare prototype forms | Tangibly different forms and a learning question for each |
| Explain a rollout | Small-group learning, the decision it informs and a visible feedback route |
| Supply detail for discussion | Appendix divider and supporting material after the main sequence |

## Chinese and mixed-language decks

- Headlines: a serif CJK face such as Noto Serif SC (600) or a heavy sans such as Noto Sans SC (700–900) to match the Latin display face. Body: the Latin body face followed by Noto Sans SC (`"Manrope", "Noto Sans SC"`), so Latin and numerals keep the deck's character.
- Keep large numerals and prices in the Latin display face.
- Do not use `font-feature-settings: "palt"` on Chinese text: it compresses full-width punctuation. Keep punctuation full-width.
- No full stop at the end of titles. Emphasise with the accent colour, never with fake italics.
- Allow 1.6–1.75 line-height for Chinese body text, `line-break: strict`, `text-wrap: balance` on titles, and hand-break a line that would leave one character alone.
- CJK font files are large. Supply them in `style.fonts` with `"subset": true`; the builder keeps only the characters the deck uses (needs `fontTools` and `brotli`).
- Write the Chinese version natively rather than translating line by line, and check each slide again: Chinese runs about 1.6 characters per English word of space.

## Motion

Reveal the title, orientation and evidence in the order people need them. Keep related labels and visuals together. Use 400–700 ms fades or small translations with approximately 100–180 ms between related groups. Land the principal entrance within roughly two seconds. Trace diagram paths with their labels where it clarifies the explanation. Show the final state in print and honor reduced motion.

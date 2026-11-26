# A visual on every slide

Every slide carries a visual: a photograph, product image, screenshot, diagram, chart, map, video or illustration that helps the audience understand the point. Text-only slides are not allowed in the main talk. When the user's material does not cover a slide, find a suitable visual on the web, record where it came from, and use it honestly.

The appendix may hold text-only reference slides (sources, glossaries, data tables). Mark them with `visual_exempt` and a reason so the checks know it was a decision.

## Plan the visual with the slide

Add a **visual** column to the content map before writing slide HTML. For each slide write what the picture must show and why, then decide where it comes from.

| Slide job | Visual that works | Usual source |
| --- | --- | --- |
| Cover, section divider, closing | One strong subject on a dark or simple ground, fading into the stage | Brand or product imagery, then open libraries |
| Agenda | Three or four image tiles, one per part | Open libraries, the user's photos |
| Concept or definition | A photograph of the thing, or a labelled diagram | Diagram you draw; product or reference photo |
| Process, framework, flow | Exact SVG diagram | Draw it |
| Evidence of people doing something | The user's research photos | User only. Never stock photos presented as the project |
| Product, tool or interface | Official product imagery or a real screenshot | Brand press kit, product page, the tool itself |
| Numbers | Chart, or big numbers beside a related picture | Chart from the data; supporting photo |
| Comparison | Side-by-side pictures or a table with thumbnails | Official imagery, screenshots |
| Quote or reflection | Portrait or atmospheric photo | Open libraries; a licensed portrait of the speaker |

Use the user's own images first, then official sources, then open libraries. Draw diagrams and charts instead of searching for them.

## Where to look

1. **The user's files and brand.** Research photos, product renders, screenshots, approved decks, press kits.
2. **Official sources for real products, places, events and people.** Company newsroom and press-kit pages, product pages, museum or government media pages. Check that the page allows reuse in a presentation (press kits usually allow editorial use).
3. **Open libraries for atmosphere and generic subjects.** Search with `scripts/find_images.py`:
   - Openverse (Creative Commons and public-domain images from Flickr, StockSnap, Wikimedia, museums and more), no key needed;
   - Wikimedia Commons, no key needed, served at its pre-rendered 1920 px size;
   - Unsplash and Pexels when `UNSPLASH_ACCESS_KEY` or `PEXELS_API_KEY` is set.
4. **Web search** for anything specific the libraries miss. Open the source page, read its license, and download only from that page.

Generated images are allowed only as clearly labelled illustration. Never present one as a real customer, product, place, event or result.

## Search and choose

```bash
python3 scripts/find_images.py "studio microphone" --out media/candidates/mic --photos-only
python3 scripts/find_images.py "night train" --out media/candidates/train --orientation wide --min-width 2000
```

- Search with one to three concrete nouns. Run several short searches rather than one sentence.
- Open `contact-sheet.jpg`. Pick by index, then look at the full image before deciding.
- Choose for the treatment you plan:
  - **Fading into a dark stage:** dark or plain background, the subject on one side, space toward the text.
  - **Fading into a light stage:** light or white background, or an object cut-out; `multiply` melts white into paper.
  - **Tiles and frames:** a clear subject that survives a crop to the tile's ratio.
- Resolution: at least the displayed width (a full-bleed or right-half image needs 1600–2000 px). `qa_render.py` warns when an image is shown larger than its pixels.
- Keep faces, hands, products and any legible text sharp, uncropped and away from the fade.
- Reject images with watermarks, visible brand logos that imply endorsement, recognisable people in sensitive contexts, or captions that contradict how you will use them.

## Fetch and record

```bash
python3 scripts/fetch_image.py --candidates media/candidates/mic/candidates.json --pick 3 media/mic.webp --manifest deck.json
python3 scripts/fetch_image.py https://example.org/photo.jpg media/hero.webp --creator "Name" --license "CC BY 4.0" --page https://example.org/photo --manifest deck.json
```

The script saves a metadata-free WebP (long edge 2600 px by default) inside the project and adds a `credits` entry (file, title, creator, license, source page) to the manifest. The builder turns `credits` and `sources` into a **Sources and image credits** appendix slide that lists which slide uses each image.

- If a site refuses the download (for example HTTP 403), do not work around it. Download from the source page yourself, ask the user, or choose another image.
- If a site asks you to slow down (HTTP 429), the script waits as asked and retries. Space out batches.
- Openverse lists some providers' original sizes but serves a ~1024 px preview (rawpixel). The fetch reports when the saved image is much smaller than listed; use those only for small placements.

## Licenses

| License | Use in a shared deck | What to do |
| --- | --- | --- |
| CC0, public domain | Yes | Credit anyway; it costs nothing and helps others trace the source |
| CC BY | Yes | Credit creator, title, license, source |
| CC BY-SA | Yes for showing in a deck | Credit; if you publish the edited image itself, share it under the same license |
| Unsplash, Pexels license | Yes | Credit is appreciated; do not sell the image unaltered |
| CC BY-NC, BY-NC-SA | Internal, non-commercial decks only | Pass `--allow-nc` deliberately; never for client or commercial work |
| ND (no derivatives) | Only unaltered | Avoid when you will crop, fade or recolour heavily |
| Press kit / editorial | News and commentary about that company | Follow the kit's terms; do not imply endorsement |
| Unknown | No | Choose another image |

Fading, cropping and brightness changes are edits. CC BY and BY-SA allow them; note "cropped and blended" in the credit when the change is significant.

## Captions and honesty

- Caption what the picture shows, not what you wish it proved. A stock photo of a workshop illustrates workshops; it is not the team's workshop.
- When atmosphere photos stand in for a real project, say so in the caption or on the credits slide ("Illustrative images").
- Keep project and personal names off slides when the user asks for that, including in captions and credits pulled from sources.

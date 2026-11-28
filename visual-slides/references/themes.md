# Topic themes

Every deck gets its own look, taken from its own topic. Two decks on different subjects should not share a palette or a typeface pairing unless a brand or the user asks for it. Never fall back to the look of a previous deck or of a bundled example.

## The rule

1. **Images first.** Find this deck's images for this topic (step 4 of SKILL.md). The palette comes from them.
2. **Mood from the subject.** Pick the mood that fits the subject, audience and room (table below). The mood sets the typefaces, type scale, corner radius and light or dark default.
3. **Colours from the images or the brand.** `make_theme.py` reads the deck's own photos: a near-neutral page tinted towards them, an accent from the colour that is vivid *and* recurs across the set (a sky in two shots loses to the subject that appears in all of them), and a second accent from another hue in the set. A brand's colours override the accent.
4. **Check, then build.** Read the contrast report, open `theme-preview.jpg`, build, and look at the render.

```bash
python3 scripts/make_theme.py --list
python3 scripts/make_theme.py --mood nature --images media/ --out theme --preview
python3 scripts/make_theme.py --mood tech --brand "#00a3e0" --images media/ --out theme
python3 scripts/make_theme.py --mood warm --images media/ --hue amber --cjk sans --out theme
```

Then in the manifest:

```json
"style": { "preset": "adaptive", "theme": "theme/theme.json" }
```

The builder embeds the theme's fonts (subset to the deck's text) and turns its colours into the tokens in `assets/adaptive.css`. Every layout, glow, fade, card, flow, tile and diagram works in light and dark themes.

## Moods

| Mood | Typefaces (heading / body / label) | Default | Suits |
| --- | --- | --- | --- |
| `editorial` | Fraunces / Work Sans / IBM Plex Mono | light | culture, research, policy, publishing, design reviews |
| `warm` | Instrument Serif / Figtree | light | family, elder care, community, heritage, healthcare stories |
| `tech` | Sora / IBM Plex Sans / JetBrains Mono | dark | AI, software, data, startups, product launches |
| `corporate` | IBM Plex Serif / IBM Plex Sans / IBM Plex Mono | light | strategy, finance, consulting, board and investor decks |
| `playful` | Fredoka / Nunito | light | children, schools, consumer fun, workshops |
| `luxury` | Cormorant Garamond / Jost | dark | fashion, beauty, hospitality, art |
| `nature` | Young Serif / DM Sans / DM Mono | light | sustainability, food, outdoors, wellness, cities, climate |
| `bold` | Anton / Archivo | dark | sports, launches, events, gaming, campaigns |
| `clinical` | Spectral / Atkinson Hyperlegible | light | health, science, public services, accessibility, training |
| `cinematic` | Barlow Condensed / Manrope / Courier Prime (bundled) | dark | the approved Cinematic Night look; use when the user chose it |

All typefaces are SIL Open Font License families from the Google Fonts repository. `make_theme.py` downloads them once (cached in `~/.cache/visual-slides`), subsets them to Latin and copies each licence next to the font. `--cjk sans|serif` adds Noto Sans SC or Noto Serif SC, which the builder subsets to the characters the deck uses.

The table is a starting point, not a fence. A climate-finance board deck may want `corporate` with a palette from field photos. A children's hospital fundraiser may want `warm` rather than `clinical`. Choose from the subject, audience and room.

## Options

- `--mode light|dark` overrides the mood's default. Use dark for a dim room or a product on black, and light for daylight rooms, reading decks and print.
- `--hue green` (or `amber`, `teal`, `blue`, `red`… or degrees) steers the accent towards the colour family the topic is about. It is still taken from the images.
- `--brand "#hex" ["#hex"]` sets the brand accent, and optionally a second colour. The brand colour is kept exactly; if it is low-contrast on the chosen surface, the script switches light/dark when that helps and says so.
- `--font heading=ofl/<dir>/<file>.ttf[:serif]` swaps one typeface for any OFL family in the Google Fonts repository (for example `ofl/playfairdisplay/PlayfairDisplay[wght].ttf`).
- `--radius 0..48` overrides the corner radius.

`theme.json` is plain JSON. Edit colours, `type` sizes (`cover_size`, `cover_top`, `title_size`…), weights and radius by hand when the render asks for it. The builder re-checks contrast: text must reach 7:1 on its background; the accent is moved to at least 3.2:1 unless it is a kept brand colour.

## Showing directions

When the user has not chosen a look, make three themes for the same topic from the same images: usually two moods that fit, plus one contrasting option (light versus dark, serif versus grotesk). Render the real opening slide in each:

```bash
python3 scripts/preview_styles.py deck.json previews theme-a/theme.json theme-b/theme.json theme-c/theme.json
```

Show the three previews, then build the whole deck in the chosen one. When the user has already chosen, or a brand or approved deck sets the look, skip the previews.

## What `check_deck.py` flags

- **Stock Cinematic Night:** the cinematic preset with its default orange and no reason recorded. Use it only when the user picked it; otherwise make a topic theme.
- **Bundled example photos** in a user deck: find images for this topic instead.

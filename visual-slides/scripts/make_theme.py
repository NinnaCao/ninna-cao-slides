#!/usr/bin/env python3
"""Make a deck theme from its own topic: palette from the deck's topic images (or the brand's
colours), typefaces from a mood that fits the subject. Writes theme.json plus embedded-ready
fonts (OFL, from the Google Fonts repository) for build_deck.py (`style.theme`).

  python3 scripts/make_theme.py --list
  python3 scripts/make_theme.py --mood warm --images media/ --out theme --preview
  python3 scripts/make_theme.py --mood tech --brand "#00a3e0" --images media/ --out theme
"""
import argparse
import json
import logging
import math
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

from theme_tokens import contrast, from_oklch, hue_distance, theme_css, to_oklch

SKILL = Path(__file__).resolve().parents[1]
MOODS = SKILL / "assets" / "themes" / "moods.json"
RAW = "https://raw.githubusercontent.com/google/fonts/main/"
CACHE = Path.home() / ".cache" / "visual-slides" / "google-fonts"
IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}
# Unicode ranges kept for Latin text fonts (Basic Latin, Latin-1, Latin Extended A/B,
# punctuation, currency, arrows, maths, symbols used in decks).
LATIN = [(0x20, 0x7E), (0xA0, 0x24F), (0x2000, 0x206F), (0x20A0, 0x20BF), (0x2100, 0x215F),
         (0x2190, 0x21FF), (0x2212, 0x2212), (0x2215, 0x2215), (0x25A0, 0x25FF), (0x2713, 0x2717)]
# Fallback accent hue per mood when the topic images are nearly grey.
MOOD_HUE = {"editorial": 30, "warm": 45, "tech": 250, "corporate": 245, "playful": 20,
            "luxury": 75, "nature": 140, "bold": 25, "clinical": 220, "cinematic": 45}


def moods():
    return json.loads(MOODS.read_text(encoding="utf-8"))


# ---------- palette from images ----------
def image_files(items):
    files = []
    for item in items or []:
        path = Path(item)
        if path.is_dir():
            files += sorted(p for p in path.rglob("*") if p.suffix.lower() in IMAGE_TYPES and "candidates" not in p.parts)
        elif path.is_file() and path.suffix.lower() in IMAGE_TYPES:
            files.append(path)
        else:
            raise SystemExit(f"Not an image or folder: {item}")
    return files


HUES = {"red": 25, "orange": 55, "amber": 70, "yellow": 100, "lime": 125, "green": 145, "teal": 185,
        "cyan": 205, "blue": 250, "indigo": 275, "violet": 300, "purple": 315, "magenta": 340, "pink": 0}


def sample_colors(files, per_image=None):
    """Quantise each image to 10 colours; every image carries equal weight."""
    from PIL import Image
    pool = defaultdict(float)
    for path in files:
        seen = []
        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail((220, 220))
            quant = image.quantize(colors=10, method=Image.Quantize.MEDIANCUT)
            palette = quant.getpalette()
            counts = quant.getcolors() or []
            total = sum(count for count, _ in counts) or 1
            for count, index in counts:
                r, g, b = palette[index * 3:index * 3 + 3]
                pool[f"#{r:02x}{g:02x}{b:02x}"] += count / total / len(files)
                if count / total >= 0.02:
                    seen.append(f"#{r:02x}{g:02x}{b:02x}")
        if per_image is not None:
            per_image.append([to_oklch(c) for c in seen])
    return sorted(((share, color) for color, share in pool.items()), reverse=True)


def presence(hue, per_image):
    """Share of the images that contain a colourful patch near this hue."""
    if not per_image:
        return 1.0
    return sum(any(C >= 0.035 and hue_distance(H, hue) <= 28 for _, C, H in colors) for colors in per_image) / len(per_image)


def circular_mean(pairs):
    x = sum(w * math.cos(math.radians(h)) for h, w in pairs)
    y = sum(w * math.sin(math.radians(h)) for h, w in pairs)
    return math.degrees(math.atan2(y, x)) % 360 if (x or y) else None


def palette(samples, mode, mood, brand, per_image=None, hue_hint=None):
    stats = [(share, color, *to_oklch(color)) for share, color in samples]
    tinted = [(H, share * C) for share, _, L, C, H in stats if C > 0.02]
    base_hue = circular_mean(tinted)
    notes = []

    # Accent: the most vivid colour that matters in the pictures, or the brand colour.
    if brand:
        accent = brand[0]
        notes.append(f"Accent is the brand colour {brand[0]}.")
    else:
        # Score: vivid × present × recurring across the set (a sky in a few shots loses to the
        # subject that appears in all of them). A --hue hint narrows the choice to that family.
        candidates = [(math.sqrt(share) * C * presence(H, per_image) ** 1.5, color, L, C, H)
                      for share, color, L, C, H in stats if C >= 0.04 and 0.25 <= L <= 0.92]
        if hue_hint is not None:
            near = [c for c in candidates if hue_distance(c[4], hue_hint) <= 35]
            if not near:
                notes.append(f"No colour near hue {hue_hint}° in the images; used the hint directly.")
                candidates = [(1, f"hue {hue_hint}", 0.6, 0.12, hue_hint)]
            else:
                candidates = near
        if candidates:
            _, picked, L, C, H = max(candidates)
            accent = from_oklch(0.72 if mode == "dark" else 0.54, min(0.19, max(0.12, C * 1.25)), H)
            notes.append(f"Accent from the images ({picked}, hue {H:.0f}°), made vivid enough for headline accents.")
        else:
            H = MOOD_HUE.get(mood, 40) if base_hue is None else base_hue
            accent = from_oklch(0.72 if mode == "dark" else 0.55, 0.13, H)
            notes.append("Images are nearly neutral; accent hue " + ("from the mood." if base_hue is None else "from their faint tint."))
    a_L, a_C, a_H = to_oklch(accent)
    if base_hue is None:
        base_hue = a_H

    # Second accent: another hue in the images, at least 40° away (used for glows and charts).
    if len(brand) > 1:
        accent2 = brand[1]
    else:
        others = [(math.sqrt(share) * C * presence(H, per_image), H, C) for share, _, L, C, H in stats
                  if C >= 0.03 and hue_distance(H, a_H) >= 40]
        H2 = max(others)[1] if others else (a_H + 150) % 360
        accent2 = from_oklch(0.46 if mode == "dark" else 0.52, 0.08, H2)

    # Surfaces: near-black or paper, tinted towards the pictures' hue so photos sit in the page.
    tint = min(0.022, max(0.006, (sum(w for _, w in tinted) or 0) * 0.08))
    if mode == "dark":
        bg = from_oklch(0.17, tint, base_hue)
        text = from_oklch(0.955, 0.012, base_hue)
        stage = from_oklch(0.12, tint * 0.8, base_hue)
    else:
        bg = from_oklch(0.968, tint * 0.8, base_hue)
        text = from_oklch(0.235, min(0.03, tint * 1.4), base_hue)
        stage = from_oklch(0.92, tint * 0.8, base_hue)
    return {"bg": bg, "text": text, "accent": accent, "accent2": accent2, "stage": stage}, notes


# ---------- fonts ----------
def fetch(path):
    """Download one file from the Google Fonts repository into the local cache."""
    target = CACHE / path
    if target.is_file() and target.stat().st_size:
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    url = RAW + urllib.parse.quote(path)
    request = urllib.request.Request(url, headers={"User-Agent": "visual-slides-theme/4.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    target.write_bytes(data)
    return target


def latin_woff2(source, target):
    from fontTools import subset
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    options = subset.Options()
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.notdef_outline = True
    try:
        import brotli  # noqa: F401
        options.flavor = "woff2"
    except ImportError:
        options.flavor = "woff"
        target = target.with_suffix(".woff")
    font = subset.load_font(str(source), options)
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=[c for lo, hi in LATIN for c in range(lo, hi + 1)])
    subsetter.subset(font)
    subset.save_font(font, str(target), options)
    return target


def font_meta(path):
    """Family name, weight range and generic class guessed from a font file."""
    from fontTools.ttLib import TTFont
    font = TTFont(str(path), lazy=True)
    names = font["name"]
    family = (names.getDebugName(16) or names.getDebugName(1) or path.stem).strip()
    weight = str(font["OS/2"].usWeightClass)
    if "fvar" in font:
        for axis in font["fvar"].axes:
            if axis.axisTag == "wght":
                weight = f"{int(axis.minValue)} {int(axis.maxValue)}"
    panose = font["OS/2"].panose.bFamilyType if hasattr(font["OS/2"], "panose") else 0
    serif_style = font["OS/2"].panose.bSerifStyle if panose == 2 else 0
    generic = "monospace" if font["post"].isFixedPitch else ("serif" if 2 <= serif_style <= 10 else "sans-serif")
    return family, weight, generic


def custom_font(spec):
    """--font heading=ofl/playfairdisplay/PlayfairDisplay[wght].ttf[:serif]"""
    role, _, rest = spec.partition("=")
    path, _, generic = rest.partition(":")
    if role not in ("heading", "body", "label") or not path.startswith(("ofl/", "apache/", "ufl/")):
        raise SystemExit("Use --font heading|body|label=ofl/<dir>/<file>.ttf[:serif|sans-serif|monospace]")
    local = fetch(path)
    family, weight, guess = font_meta(local)
    folder = path.rsplit("/", 1)[0]
    license_path = next((p for p in (folder + "/OFL.txt", folder + "/LICENSE.txt") if _exists(p)), None)
    return role, {"family": family, "generic": generic or guess, "files": [{"path": path, "weight": weight}],
                  "license": license_path}


def _exists(path):
    try:
        fetch(path)
        return True
    except Exception:
        return False


def install_fonts(specs, cjk, out):
    folder = out / "fonts"
    folder.mkdir(parents=True, exist_ok=True)
    fonts, credits, previews = {}, [], {}
    for role in ("heading", "body", "label"):
        spec = specs[role]
        entry = {"family": spec["family"], "generic": spec["generic"], "files": []}
        for item in spec["files"]:
            source = fetch(item["path"])
            weight = str(item["weight"])
            stem = spec["family"].replace(" ", "") + "-" + ("Variable" if " " in weight else weight)
            target = latin_woff2(source, folder / (stem + ".woff2"))
            entry["files"].append({"file": f"fonts/{target.name}", "weight": item["weight"], "subset": True})
            previews.setdefault(role, source)
        if spec.get("license"):
            license_file = folder / (spec["family"].replace(" ", "") + "-OFL.txt")
            shutil.copyfile(fetch(spec["license"]), license_file)
            credits.append({"family": spec["family"], "license": "SIL Open Font License 1.1",
                            "source": "https://github.com/google/fonts/tree/main/" + spec["license"].rsplit("/", 1)[0],
                            "file": f"fonts/{license_file.name}"})
        if not entry["files"]:
            previews[role] = previews.get("body")
        fonts[role] = entry
    if cjk:
        spec = moods()["cjk"][cjk]
        source = fetch(spec["path"])
        target = folder / Path(spec["path"]).name.replace("[wght]", "-Variable")
        shutil.copyfile(source, target)
        shutil.copyfile(fetch(spec["license"]), folder / (spec["family"].replace(" ", "") + "-OFL.txt"))
        fonts["cjk"] = {"family": spec["family"], "generic": "serif" if cjk == "serif" else "sans-serif",
                        "files": [{"file": f"fonts/{target.name}", "weight": spec["weight"], "subset": True}]}
        credits.append({"family": spec["family"], "license": "SIL Open Font License 1.1",
                        "source": "https://github.com/google/fonts/tree/main/" + spec["license"].rsplit("/", 1)[0]})
    return fonts, credits, previews


# ---------- preview ----------
def preview(theme, colors, files, previews, target):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1600, 900
    sheet = Image.new("RGB", (W, H), colors["bg"])
    draw = ImageDraw.Draw(sheet)
    strip = files[:5]
    if strip:
        cell = W // len(strip)
        for i, path in enumerate(strip):
            with Image.open(path) as image:
                image = image.convert("RGB")
                scale = max(cell / image.width, 360 / image.height)
                image = image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))))
                left, top = (image.width - cell) // 2, (image.height - 360) // 2
                sheet.paste(image.crop((left, top, left + cell, top + 360)), (i * cell, H - 360))

    def face(role, size):
        try:
            font = ImageFont.truetype(str(previews.get(role)), size)
            try:
                weights = {"heading": theme["type"].get("display_weight", 700), "body": 400, "label": 600}
                font.set_variation_by_axes([weights[role]])
            except Exception:
                pass
            return font
        except Exception:
            return ImageFont.load_default()

    draw.text((80, 64), "SECTION 01 · " + theme["mood_label"].upper(), fill=colors["accent"], font=face("label", 26))
    draw.text((80, 116), "A deck about the topic", fill=colors["text"], font=face("heading", 96))
    draw.text((80, 250), "Body copy explains the idea in a calm, readable voice.", fill=colors["muted"], font=face("body", 34))
    x = 80
    for key in ("bg", "text", "muted", "accent", "accent2", "alt_bg", "stage"):
        draw.rectangle((x, 330, x + 150, 450), fill=colors[key], outline=colors["muted"])
        draw.text((x, 458), key, fill=colors["text"], font=face("label", 20))
        x += 180
    sheet.save(target, quality=88)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="List the moods and what each suits.")
    parser.add_argument("--mood", help="Mood that fits the topic (see --list).")
    parser.add_argument("--images", nargs="*", help="The deck's own topic images or their folder (the palette source).")
    parser.add_argument("--brand", nargs="*", default=[], help="Brand colours (#rrggbb); the first becomes the accent.")
    parser.add_argument("--mode", choices=("light", "dark"), help="Override the mood's light/dark default.")
    parser.add_argument("--hue", help="Steer the accent to a colour family the topic is about "
                        "(" + ", ".join(HUES) + ", or degrees 0-359), still taken from the images.")
    parser.add_argument("--cjk", choices=("sans", "serif"), help="Add a Chinese font (subset to the deck's text at build).")
    parser.add_argument("--font", action="append", default=[], help="Swap a typeface: heading=ofl/<dir>/<file>.ttf[:serif]")
    parser.add_argument("--radius", type=float, help="Corner radius in px (overrides the mood).")
    parser.add_argument("--name", help="Theme name for the file header.")
    parser.add_argument("--out", default="theme", help="Folder for theme.json and fonts/ (inside the deck project).")
    parser.add_argument("--preview", action="store_true", help="Also write theme-preview.jpg.")
    args = parser.parse_args()
    library = moods()
    if args.list:
        for key, mood in library["moods"].items():
            print(f"{key:10} {mood.get('mode', ''):5}  {mood['label']}: {mood['use_for']}")
        return
    if args.mood not in library["moods"]:
        parser.error("Choose --mood from: " + ", ".join(library["moods"]))
    for color in args.brand:
        if not (len(color) == 7 and color.startswith("#")):
            parser.error("Brand colours must be #rrggbb.")
    mood = library["moods"][args.mood]
    files = image_files(args.images)
    if not files and not args.brand:
        parser.error("Give --images (the deck's own topic images) or --brand colours: the palette comes from the topic.")
    mode = args.mode or mood["mode"]
    brand = [c.lower() for c in args.brand]
    if brand and not args.mode:
        light_ok = contrast(brand[0], "#f6f3ee") >= 3
        dark_ok = contrast(brand[0], "#121316") >= 3
        if mode == "light" and not light_ok and dark_ok:
            mode = "dark"
        elif mode == "dark" and not dark_ok and light_ok:
            mode = "light"
    per_image = []
    samples = sample_colors(files, per_image) if files else []
    hue_hint = None
    if args.hue:
        hue_hint = HUES.get(args.hue.lower()) if not args.hue.isdigit() else int(args.hue) % 360
        if hue_hint is None:
            parser.error("--hue takes a colour family (" + ", ".join(HUES) + ") or degrees 0-359.")
    colors, notes = palette(samples, mode, args.mood, brand, per_image, hue_hint)
    if args.mood == "cinematic":
        style = {"preset": "cinematic", "accent": colors["accent"] if not brand else brand[0]}
        print(json.dumps({"style": style, "notes": notes + ["Cinematic Night is a preset: use this style block."]}, indent=2))
        return

    specs = dict(mood["fonts"])
    for spec in args.font:
        role, custom = custom_font(spec)
        specs[role] = custom
    if specs["label"].get("files") == [] and specs["label"]["family"] != specs["body"]["family"]:
        specs["label"] = specs["body"]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    fonts, font_credits, previews = install_fonts(specs, args.cjk, out)
    theme = {
        "name": args.name or f"{mood['label']} · {mode} · palette from {len(files)} topic image(s)" + (" and brand" if brand else ""),
        "mood": args.mood,
        "mood_label": mood["label"],
        "mode": mode,
        "source": {"images": [str(p) for p in files], "brand": brand},
        "colors": colors,
        "keep_accent": bool(brand),
        "fonts": fonts,
        "type": mood["type"],
        "shape": {"radius": args.radius if args.radius is not None else mood["shape"]["radius"]},
        "font_credits": font_credits,
        "guidance": {"images": mood["images"], "layout": mood["layout"]},
    }
    css, final = theme_css(theme)
    theme["colors"] = {k: final[k] for k in ("bg", "text", "muted", "accent", "accent2", "alt_bg", "alt_text", "accent_alt", "stage")}
    theme["contrast"] = {
        "text_on_bg": round(contrast(final["text"], final["bg"]), 1),
        "muted_on_bg": round(contrast(final["muted"], final["bg"]), 1),
        "accent_on_bg": round(contrast(final["accent"], final["bg"]), 1),
        "accent_on_alt": round(contrast(final["accent_alt"], final["alt_bg"]), 1),
    }
    if brand and contrast(final["accent"], final["bg"]) < 3:
        notes.append("Brand colour kept exactly but it is low-contrast on this background: use it for "
                     "rules and fills, and check headline accents in the render.")
    theme["notes"] = notes
    (out / "theme.json").write_text(json.dumps(theme, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.preview:
        preview(theme, final, files, previews, out / "theme-preview.jpg")
    print(json.dumps({"theme": str(out / "theme.json"), "mode": mode, "colors": theme["colors"],
                      "contrast": theme["contrast"], "fonts": {r: f["family"] for r, f in fonts.items()},
                      "notes": notes, "style": {"preset": "adaptive", "theme": str(out / "theme.json")}},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as exc:
        sys.exit(f"Could not download a font from the Google Fonts repository: {exc}. "
                 "Retry later, or pass fonts already on disk in theme.json.")

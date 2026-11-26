#!/usr/bin/env python3
"""Build a portable, single-file Ninna Cao Slides deck from authored JSON."""

import argparse
import base64
import html
import json
import mimetypes
from pathlib import Path
import re

from theme_catalog import css_for, styles

ASSETS = Path(__file__).resolve().parents[1] / "assets"
PRESETS = {
    "cinematic": "ninna-cinematic.css",
    "editorial": "ninna-editorial.css",
    "light": "ninna-light.css",
    "custom": None,
}
# Fonts bundled with a preset (OFL, in assets/fonts) and embedded automatically.
PRESET_FONTS = {
    "cinematic": [
        ("Barlow Condensed", "BarlowCondensed-SemiBold.woff2", "600", "normal"),
        ("Barlow Condensed", "BarlowCondensed-Bold.woff2", "700", "normal"),
        ("Barlow Condensed", "BarlowCondensed-ExtraBold.woff2", "800", "normal"),
        ("Manrope", "Manrope-Variable.woff2", "200 800", "normal"),
        ("Courier Prime", "CourierPrime-Regular.woff2", "400", "normal"),
        ("Courier Prime", "CourierPrime-Bold.woff2", "700", "normal"),
    ],
}
LAYOUTS = ("cover", "content", "divider", "statement")
PLACES = ("right", "left", "top", "top-right", "bottom", "full", "ambient")
NAME = re.compile(r"[a-z][a-z0-9-]*")
HEX = re.compile(r"#[0-9a-fA-F]{6}")
FONT_FORMATS = {
    ".ttf": ("font/ttf", "truetype"),
    ".otf": ("font/otf", "opentype"),
    ".woff": ("font/woff", "woff"),
    ".woff2": ("font/woff2", "woff2"),
}


def safe_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def project_file(value, root):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected a local project file path.")
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", value) or Path(value).is_absolute():
        raise ValueError("Use a path relative to the manifest: " + value)
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("File must stay inside the manifest project directory: " + value)
    if not path.is_file():
        raise ValueError("Missing project file: " + str(path))
    return path


def data_uri(path, mime):
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def local_asset(value, root):
    if value.startswith("data:"):
        return value
    path = project_file(value, root)
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if not mime.startswith(("image/", "video/", "audio/")):
        raise ValueError("Expected an image, video or audio asset: " + value)
    return data_uri(path, mime)


def embed_tokens(markup, root):
    return re.sub(r"\{\{asset:([^}]+)\}\}", lambda m: local_asset(m[1].strip(), root), markup)


def subset_font(path, text):
    """Keep only the glyphs the deck uses. Essential for CJK fonts (10–20 MB → a few hundred KB)."""
    try:
        from fontTools import subset
    except ImportError:
        return None, "fontTools is not installed; embedded the full font."
    options = subset.Options()
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.notdef_outline = True
    try:
        import brotli  # noqa: F401  (needed for WOFF2)
        options.flavor = "woff2"
        mime, css_format = "font/woff2", "woff2"
    except ImportError:
        options.flavor = "woff"
        mime, css_format = "font/woff", "woff"
    font = subset.load_font(str(path), options)
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=text)
    subsetter.subset(font)
    import io
    buffer = io.BytesIO()
    subset.save_font(font, buffer, options)
    return (buffer.getvalue(), mime, css_format), None


def font_face(family, path, weight, style, payload=None):
    if not isinstance(family, str) or not family.strip() or re.search(r"[<>\x00-\x1f]", family):
        raise ValueError("Each font needs a valid CSS family name.")
    weight = str(weight)
    weights = weight.split()
    if not 1 <= len(weights) <= 2 or not all(
        re.fullmatch(r"[1-9][0-9]{0,2}|1000", value) for value in weights
    ) or int(weights[0]) > int(weights[-1]):
        raise ValueError("Font weight must be a number from 1 to 1000 or an ascending range.")
    if style not in ("normal", "italic", "oblique"):
        raise ValueError("Font style must be normal, italic or oblique.")
    file_type = path.suffix.lower()
    if file_type not in FONT_FORMATS:
        raise ValueError("Supply a TTF, OTF, WOFF or WOFF2 font: " + str(path))
    mime, css_format = FONT_FORMATS[file_type]
    if payload:
        data, mime, css_format = payload
        source = f"data:{mime};base64," + base64.b64encode(data).decode("ascii")
    else:
        source = data_uri(path, mime)
    return (
        f"@font-face {{ font-family: {json.dumps(family, ensure_ascii=False)}; "
        f"font-weight: {' '.join(weights)}; font-style: {style}; font-display: block; "
        f'src: url({source}) format("{css_format}"); }}'
    )


def load_style(style, root):
    preset = style.get("preset") if isinstance(style, dict) else None
    if not isinstance(preset, str) or (preset not in PRESETS and preset not in styles()):
        raise ValueError("Choose style.preset as a catalog ID, cinematic, editorial, light, or custom.")
    stylesheet = PRESETS.get(preset)
    css = ""
    if preset in styles():
        css = css_for(preset)
    elif stylesheet:
        css = (ASSETS / stylesheet).read_text(encoding="utf-8")
    accent = style.get("accent")
    if accent:
        if not isinstance(accent, str) or not HEX.fullmatch(accent):
            raise ValueError("Style.accent must be a six-digit hex colour such as #ff7338.")
        css += f"\n.slide {{ --accent: {accent}; }}"
    css_path = style.get("css")
    if preset == "custom" and not css_path:
        raise ValueError("The custom preset requires style.css with a local stylesheet path.")
    if css_path:
        custom = project_file(css_path, root)
        if custom.suffix.lower() != ".css":
            raise ValueError("Style.css must point to a .css stylesheet.")
        project_css = embed_tokens(custom.read_text(encoding="utf-8"), root)
        if re.search(r"</style", project_css, re.I):
            raise ValueError("The project stylesheet contains an HTML style closing tag.")
        css += "\n" + project_css
    fonts = [
        {"family": family, "path": ASSETS / "fonts" / file, "weight": weight, "style": font_style, "subset": False}
        for family, file, weight, font_style in PRESET_FONTS.get(preset, [])
        if style.get("bundled_fonts", True)
    ]
    supplied_fonts = style.get("fonts", [])
    if not isinstance(supplied_fonts, list) or not all(isinstance(font, dict) for font in supplied_fonts):
        raise ValueError("Style.fonts must be a list of local font declarations.")
    for font in supplied_fonts:
        fonts.append({
            "family": font.get("family"),
            "path": project_file(font.get("file"), root),
            "weight": font.get("weight", 400),
            "style": font.get("style", "normal"),
            "subset": bool(font.get("subset", style.get("subset_fonts", False))),
        })
    return preset, css, fonts


def font_css(fonts, text):
    rules, notes = [], []
    for font in fonts:
        payload = None
        if font["subset"]:
            payload, note = subset_font(font["path"], text)
            if note:
                notes.append(note)
        rules.append(font_face(font["family"], font["path"], font["weight"], font["style"], payload))
    return "\n".join(rules), sorted(set(notes))


def visible_text(markup):
    markup = re.sub(r"<(script|style)\b.*?</\1>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"data:[^\"')\s]+", " ", markup)
    return html.unescape(re.sub(r"<[^>]+>", " ", markup))


def percent(value, name, low=0, high=100):
    number = float(value)
    if not low <= number <= high:
        raise ValueError(f"{name} must be between {low} and {high}.")
    return f"{number:g}%"


def render_backdrop(slide, root):
    """Full-slide picture. With `place`, it fades into the slide background (see deck-layout.css)."""
    spec = slide.get("backdrop")
    if spec is None and slide.get("background_image"):
        spec = {
            "image": slide["background_image"],
            "focus": slide.get("background_position", "70% 35%"),
            "alt": slide.get("background_alt", ""),
            "place": slide.get("background_place"),
        }
    if not spec:
        return ""
    if isinstance(spec, str):
        spec = {"image": spec}
    if not isinstance(spec, dict) or not spec.get("image"):
        raise ValueError("Backdrop needs an image path.")
    image = html.escape(local_asset(spec["image"], root), quote=True)
    focus = html.escape(str(spec.get("focus", "60% 40%")), quote=True)
    classes = ["backdrop"]
    place = spec.get("place")
    if place:
        if place not in PLACES:
            raise ValueError("Backdrop place must be one of: " + ", ".join(PLACES))
        classes += ["fade", "place-" + place]
        if spec.get("scrim") == "bottom":
            classes.append("scrim-bottom")
    variables = []
    if "fade" in spec:
        variables.append("--fade-len:" + percent(spec["fade"], "Backdrop fade"))
    if "start" in spec:
        variables.append("--plate-start:" + percent(spec["start"], "Backdrop start"))
    if "height" in spec:
        variables.append("--plate-height:" + percent(spec["height"], "Backdrop height"))
    if "brightness" in spec:
        level = float(spec["brightness"])
        if not 0.4 <= level <= 1.8:
            raise ValueError("Backdrop brightness must be between 0.4 and 1.8.")
        variables.append(f"--img-brightness:{level:g}")
    if "opacity" in spec:
        level = float(spec["opacity"])
        if not 0.05 <= level <= 1:
            raise ValueError("Backdrop opacity must be between 0.05 and 1.")
        variables.append(f"--ambient:{level:g}")
    if "at" in spec:
        at = str(spec["at"])
        if not re.fullmatch(r"\d{1,3}% \d{1,3}%", at):
            raise ValueError("Backdrop 'at' must look like '80% 35%'.")
        variables.append("--ambient-at:" + at)
    if "blur" in spec:
        blur = float(spec["blur"])
        if not 0 <= blur <= 24:
            raise ValueError("Backdrop blur must be between 0 and 24 px.")
        variables.append(f"--ambient-blur:{blur:g}px")
    style = f' style="{";".join(variables)}"' if variables else ""
    alt = html.escape(str(spec.get("alt", "")), quote=True)
    hidden = "" if alt else ' aria-hidden="true"'
    return (
        f'<div class="{" ".join(classes)}"{style}{hidden}>'
        f'<img src="{image}" alt="{alt}" style="object-position:{focus}"></div>'
    )


def render_slide(slide, number, main_count, root, design=None):
    identifier = slide.get("id", f"slide-{number}")
    if identifier != f"slide-{number}":
        raise ValueError(f"Keep stable numbered ids matching the visible order: slide-{number}")
    title = str(slide.get("title", "")).strip()
    if not title:
        raise ValueError(f"Slide {number} needs a title.")

    layout = slide.get("layout", "content")
    if layout not in LAYOUTS:
        raise ValueError("Use layout " + ", ".join(LAYOUTS) + " and customize the composition in CSS.")
    classes = ["slide", layout]
    if design:
        classes.extend(("catalog", "layout-" + design["layout"], "motif-" + design["motif"]))
    if slide.get("background_image") or slide.get("backdrop"):
        classes.append("has-backdrop")
    visual = '<div class="style-visual" aria-hidden="true"></div>' if design and layout == "cover" else ""
    for field, prefix in (("theme", "theme-"), ("glow", "glow-")):
        value = slide.get(field)
        if value:
            for name in str(value).split():
                if not NAME.fullmatch(name):
                    raise ValueError(f"Use lowercase CSS names for slide {field}.")
                classes.append(prefix + name)
    classes.extend(str(slide.get("slide_class", "")).split())
    appendix = bool(slide.get("appendix", False))
    if appendix:
        classes.append("appendix")
    title_lines = int(slide.get("title_lines", 1))
    if title_lines not in (1, 2):
        raise ValueError("Title_lines must be 1 or 2.")
    if title_lines == 2:
        classes.append("two-line")
    if number == 1:
        classes.extend(("active", "visible"))

    position_attribute = ""
    if "body_top" in slide:
        body_top = int(slide["body_top"])
        if not 250 <= body_top <= 900:
            raise ValueError("Body_top must be between 250 and 900 pixels.")
        position_attribute = f' style="--body-top:{body_top}px"'
    duration = float(slide.get("duration_seconds", 45))
    if not 1 <= duration <= 1800:
        raise ValueError("Slide duration must be between 1 and 1800 seconds.")
    class_list = html.escape(" ".join(classes), quote=True)
    title_attribute = html.escape(title, quote=True)
    attributes = (
        f'id="{identifier}" class="{class_list}" data-title="{title_attribute}" '
        f'data-appendix="{str(appendix).lower()}" data-duration-seconds="{duration:g}" '
        f'aria-label="Slide {number}. {title_attribute}" aria-hidden="{str(number != 1).lower()}"'
    )
    if slide.get("visual_exempt"):
        attributes += f' data-visual-exempt="{html.escape(str(slide["visual_exempt"]), quote=True)}"'
    if number != 1:
        attributes += " inert"

    backdrop = render_backdrop(slide, root)
    section = html.escape(str(slide.get("section", "")))
    section_number = html.escape(str(slide.get("section_number", "")))
    kicker = ""
    if section or section_number:
        badge = f'<span class="kicker-num">{section_number}</span>' if section_number else ""
        kicker = f'<p class="kicker">{badge}{section}</p>'
    numeral = ""
    if slide.get("number_label"):
        numeral = (f'<span class="divider-num reveal" style="--delay:0ms" aria-hidden="true">'
                   f'{html.escape(str(slide["number_label"]))}</span>')
    headline = embed_tokens(slide.get("title_html", html.escape(title)), root)
    subtitle = ""
    if slide.get("subtitle"):
        description = html.escape(str(slide["subtitle"]))
        subtitle = f'<p class="slide-subtitle reveal" style="--delay:110ms">{description}</p>'
    body_class = html.escape(str(slide.get("body_class", "")), quote=True)
    body = embed_tokens(str(slide.get("body_html", "")), root)
    credit = html.escape(str(slide.get("source_credit", "")))
    source_credit = f'<span class="source-credit">{credit}</span>' if credit else ""
    page_label = f"Appendix {number - main_count}" if appendix else f"{number:02d} / {main_count:02d}"

    return (
        f'<section {attributes}{position_attribute}>\n{visual}{backdrop}\n'
        f'<header class="slide-header">{kicker}{numeral}'
        f'<h2 class="slide-title reveal" style="--delay:20ms">{headline}</h2>{subtitle}</header>\n'
        f'<div class="slide-body {body_class}">{body}</div>\n'
        f'<footer class="slide-footer">{source_credit}<span class="page-marker">{page_label}</span></footer>\n'
        f"</section>"
    )


def credit_slides(model, slides):
    """Turn manifest `credits` (images) and `sources` (facts) into appendix slides."""
    credits = model.get("credits", []) or []
    sources = model.get("sources", []) or []
    if not isinstance(credits, list) or not isinstance(sources, list):
        raise ValueError("Credits and sources must be lists.")
    if not (credits or sources) or model.get("credits_slide", True) is False:
        return []
    from urllib.parse import urlparse

    def host(url):
        return urlparse(str(url)).netloc.replace("www.", "") if url else ""

    entries = []
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("Each source must be an object.")
        bits = [source.get("publisher"), source.get("date"), host(source.get("url"))]
        entries.append(("Source", source.get("title", "Untitled"), " · ".join(b for b in bits if b), -1))
    for credit in credits:
        if not isinstance(credit, dict) or not credit.get("file"):
            raise ValueError("Each credit needs at least a file path.")
        used = [str(i) for i, slide in enumerate(slides, 1)
                if credit["file"] in json.dumps(slide, ensure_ascii=False)]
        detail = " · ".join(b for b in (credit.get("creator"), credit.get("license"), host(credit.get("source"))) if b)
        where = ("Slide " if len(used) == 1 else "Slides ") + ", ".join(used) if used else "Not placed"
        entries.append((where, credit.get("title") or Path(credit["file"]).stem, detail, int(used[0]) if used else 10**6))
    entries.sort(key=lambda entry: entry[3])  # sources first, then images in slide order
    title = str(model.get("credits_title", "Sources and image credits"))
    per_slide = 15
    generated = []
    for start in range(0, len(entries), per_slide):
        chunk = entries[start:start + per_slide]
        cells = "".join(
            f'<div><span>{html.escape(str(label))}</span><b>{html.escape(str(name))}</b>{html.escape(detail)}</div>'
            for label, name, detail, _ in chunk
        )
        generated.append({
            "title": title if start == 0 else title + " (continued)",
            "section": "Appendix",
            "subtitle": str(model.get("credits_note", "Images are used under the licenses shown. Checked when the deck was built.")),
            "appendix": True,
            "glow": "none",
            "visual_exempt": "Generated list of sources and credits",
            "duration_seconds": 20,
            "body_html": f'<div class="credits-grid reveal" style="--delay:160ms">{cells}</div>',
        })
    return generated


def build(manifest_path, output_path):
    manifest_path = Path(manifest_path).resolve()
    model = json.loads(manifest_path.read_text(encoding="utf-8"))
    slides = model.get("slides", [])
    if not isinstance(slides, list) or not slides:
        raise ValueError("The manifest needs at least one slide.")
    main_count = sum(not slide.get("appendix", False) for slide in slides)
    if main_count < 1:
        raise ValueError("Include at least one main slide before the appendix.")
    if any(slide.get("appendix", False) for slide in slides[:main_count]):
        raise ValueError("All appendix slides must follow the main presentation.")

    root = manifest_path.parent
    preset, style_css, fonts = load_style(model.get("style"), root)
    design = styles().get(preset)
    all_slides = slides + credit_slides(model, slides)
    sections = [
        render_slide(slide, number, main_count, root, design)
        for number, slide in enumerate(all_slides, 1)
    ]
    text = visible_text("\n".join(sections)) + str(model.get("title", "")) + "".join(map(chr, range(32, 127))) + "–—‘’“”…·•→←©®™°×÷±€£¥"
    font_rules, font_notes = font_css(fonts, text)
    notes = [{"en": str(slide.get("notes_en", "")), "zh": str(slide.get("notes_zh", ""))} for slide in all_slides]
    edit_controls = (
        '<button id="toggle-editor" aria-pressed="false">Edit text</button>\n'
        '<button id="save-edited" hidden>Download edited copy</button>'
    ) if model.get("editable", True) else ""
    lang = str(model.get("lang", "en"))
    if not re.fullmatch(r"[a-zA-Z]{2,3}(-[a-zA-Z0-9]{2,8})*", lang):
        raise ValueError("Lang must be a language tag such as en or zh-CN.")
    fields = {
        "LANG": lang,
        "EDIT_CONTROLS": edit_controls,
        "TITLE": html.escape(str(model.get("title", "Presentation"))),
        "AUTHOR": html.escape(str(model.get("author", "")), quote=True),
        "FONT_CSS": font_rules,
        "STAGE_CSS": (ASSETS / "deck-stage.css").read_text(encoding="utf-8"),
        "LAYOUT_CSS": (ASSETS / "deck-layout.css").read_text(encoding="utf-8"),
        "STYLE_PRESET": preset,
        "STYLE_CSS": style_css,
        "RUNTIME_CSS": (ASSETS / "deck-runtime.css").read_text(encoding="utf-8"),
        "CONTROLLER_JS": (ASSETS / "deck-controller.js").read_text(encoding="utf-8") + (
            "\n" + (ASSETS / "deck-editing.js").read_text(encoding="utf-8") if edit_controls else ""
        ),
        "SLIDES": "\n".join(sections),
        "MANIFEST_JSON": safe_json(model),
        "NOTES_JSON": safe_json(notes),
    }
    shell = (ASSETS / "deck-shell.html").read_text(encoding="utf-8")
    rendered = re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: fields[m[1]], shell)
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    return {
        "file": str(output_path),
        "style": preset,
        "main_slides": main_count,
        "appendix_slides": len(all_slides) - main_count,
        "generated_credit_slides": len(all_slides) - len(slides),
        "bytes": output_path.stat().st_size,
        "font_notes": font_notes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="Authored deck JSON with local assets.")
    parser.add_argument("output", help="Destination self-contained HTML file.")
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.manifest, args.output), ensure_ascii=False))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, "Build failed: " + str(exc) + "\n")


if __name__ == "__main__":
    main()

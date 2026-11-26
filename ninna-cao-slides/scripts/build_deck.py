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
    "editorial": "ninna-editorial.css",
    "light": "ninna-light.css",
    "custom": None,
}
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


def font_face(family, path, weight, style):
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
    return (
        f"@font-face {{ font-family: {json.dumps(family, ensure_ascii=False)}; "
        f"font-weight: {' '.join(weights)}; font-style: {style}; font-display: block; "
        f'src: url({data_uri(path, mime)}) format("{css_format}"); }}'
    )


def load_style(style, root):
    preset = style.get("preset") if isinstance(style, dict) else None
    if not isinstance(preset, str) or (preset not in PRESETS and preset not in styles()):
        raise ValueError("Choose style.preset as a catalog ID, editorial, light, or custom.")
    stylesheet = PRESETS.get(preset)
    css = ""
    if preset in styles():
        css = css_for(preset)
    elif stylesheet:
        css = (ASSETS / stylesheet).read_text(encoding="utf-8")
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
    fonts = []
    supplied_fonts = style.get("fonts", [])
    if not isinstance(supplied_fonts, list) or not all(isinstance(font, dict) for font in supplied_fonts):
        raise ValueError("Style.fonts must be a list of local font declarations.")
    for font in supplied_fonts:
        fonts.append(font_face(
            font.get("family"),
            project_file(font.get("file"), root),
            font.get("weight", 400),
            font.get("style", "normal"),
        ))
    return preset, css, "\n".join(fonts)


def render_slide(slide, number, main_count, root, design=None):
    identifier = slide.get("id", f"slide-{number}")
    if identifier != f"slide-{number}":
        raise ValueError(f"Keep stable numbered ids matching the visible order: slide-{number}")
    title = str(slide.get("title", "")).strip()
    if not title:
        raise ValueError(f"Slide {number} needs a title.")

    layout = slide.get("layout", "content")
    if layout not in ("cover", "content"):
        raise ValueError("Use layout cover or content and customize the composition in CSS.")
    classes = ["slide", layout]
    if design:
        classes.extend(("catalog", "layout-" + design["layout"], "motif-" + design["motif"]))
    if slide.get("background_image"):
        classes.append("has-backdrop")
    visual = '<div class="style-visual" aria-hidden="true"></div>' if design and layout == "cover" else ""
    theme = slide.get("theme")
    if theme:
        if not isinstance(theme, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", theme):
            raise ValueError("Use a lowercase CSS name for a slide theme.")
        classes.append(f"theme-{theme}")
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
        if not 300 <= body_top <= 850:
            raise ValueError("Body_top must be between 300 and 850 pixels.")
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
    if number != 1:
        attributes += " inert"

    backdrop = ""
    if slide.get("background_image"):
        image = html.escape(local_asset(slide["background_image"], root), quote=True)
        position = html.escape(str(slide.get("background_position", "70% 35%")), quote=True)
        backdrop = (
            f'<div class="backdrop" aria-hidden="true">'
            f'<img src="{image}" alt="" style="object-position:{position}"></div>'
        )
    section = html.escape(str(slide.get("section", "")))
    kicker = f'<p class="kicker">{section}</p>' if section else ""
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
        f'<header class="slide-header">{kicker}'
        f'<h2 class="slide-title reveal" style="--delay:20ms">{headline}</h2>{subtitle}</header>\n'
        f'<div class="slide-body {body_class}">{body}</div>\n'
        f'<footer class="slide-footer">{source_credit}<span class="page-marker">{page_label}</span></footer>\n'
        f"</section>"
    )


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
    preset, style_css, font_css = load_style(model.get("style"), root)
    design = styles().get(preset)
    sections = [
        render_slide(slide, number, main_count, root, design)
        for number, slide in enumerate(slides, 1)
    ]
    notes = [{"en": str(slide.get("notes_en", "")), "zh": str(slide.get("notes_zh", ""))} for slide in slides]
    edit_controls = (
        '<button id="toggle-editor" aria-pressed="false">Edit text</button>\n'
        '<button id="save-edited" hidden>Download edited copy</button>'
    ) if model.get("editable", True) else ""
    fields = {
        "EDIT_CONTROLS": edit_controls,
        "TITLE": html.escape(str(model.get("title", "Presentation"))),
        "AUTHOR": html.escape(str(model.get("author", "")), quote=True),
        "FONT_CSS": font_css,
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
        "appendix_slides": len(slides) - main_count,
        "bytes": output_path.stat().st_size,
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

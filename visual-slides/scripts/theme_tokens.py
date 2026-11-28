"""Colour maths and theme → CSS tokens for adaptive.css.

A theme is a small JSON document (written by make_theme.py, or by hand):

{
  "name": "Warm & human · from 6 topic images",
  "mode": "light",
  "colors": {"bg": "#f6f1ea", "text": "#2a211b", "accent": "#b4532a", "accent2": "#4f6a5a",
             "alt_bg": "#2a211b", "alt_text": "#f6f1ea", "stage": "#e9e2d8",
             "muted": "#5b5048", "accent_alt": "#e08a5f"},
  "fonts": {"heading": {"family": "Instrument Serif", "generic": "serif",
                        "files": [{"file": "fonts/InstrumentSerif-Regular.woff2", "weight": "400"}]},
            "body": {...}, "label": {...}, "cjk": {...}},
  "type": {"heading_weight": 400, "title_size": 104, ...},
  "shape": {"radius": 18}
}

Only bg, text and accent are required; everything else has a derived default.
"""
import math
import re

HEX = re.compile(r"#[0-9a-fA-F]{6}")
GENERIC = {"serif", "sans-serif", "monospace", "cursive", "system-ui"}
FALLBACKS = {
    "serif": '"Noto Serif SC", "Songti SC", Georgia, serif',
    "sans-serif": '"Noto Sans SC", "PingFang SC", "Helvetica Neue", Arial, sans-serif',
    "monospace": '"Noto Sans SC", "PingFang SC", ui-monospace, "Courier New", monospace',
}
TYPE_KEYS = {
    "heading_weight": ("--heading-weight", "int"), "display_weight": ("--display-weight", "int"),
    "card_title_weight": ("--card-title-weight", "int"), "body_weight": ("--body-weight", "int"),
    "label_weight": ("--label-weight", "int"), "label_case": ("--label-case", "case"),
    "label_tracking": ("--label-tracking", "em"),
    "title_size": ("--title-size", "px"), "title_line": ("--title-line", "num"), "title_tracking": ("--title-tracking", "em"),
    "cover_top": ("--cover-top", "px"), "cover_size": ("--cover-size", "px"), "cover_line": ("--cover-line", "num"), "cover_tracking": ("--cover-tracking", "em"),
    "divider_size": ("--divider-size", "px"), "divider_line": ("--divider-line", "num"),
    "divider_tracking": ("--divider-tracking", "em"), "numeral_size": ("--numeral-size", "px"),
}


# ---------- sRGB, OKLab and contrast ----------
def hex_rgb(color):
    return tuple(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))


def rgb_hex(rgb):
    return "#" + "".join(f"{round(min(1, max(0, c)) * 255):02x}" for c in rgb)


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def luminance(color):
    r, g, b = (_lin(c) for c in hex_rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi + 0.05) / (lo + 0.05)


def to_oklch(color):
    r, g, b = (_lin(c) for c in hex_rgb(color))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360


def _oklch_rgb(L, C, H):
    A, B = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return r, g, b


def from_oklch(L, C, H):
    """OKLCH → hex, reducing chroma until the colour fits in sRGB."""
    L = min(1, max(0, L))
    for _ in range(40):
        rgb = _oklch_rgb(L, C, H)
        if all(-0.0005 <= c <= 1.0005 for c in rgb):
            break
        C *= 0.92
    return rgb_hex(tuple(_gam(min(1, max(0, c))) for c in _oklch_rgb(L, C, H)))


def hue_distance(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def fit_contrast(color, against, target, prefer=None):
    """Move a colour's lightness (keeping hue and as much chroma as fits) until it reaches
    `target` contrast against `against`. `prefer` is 'lighter' or 'darker'; by default the
    direction away from the background."""
    if contrast(color, against) >= target:
        return color
    L, C, H = to_oklch(color)
    if prefer is None:
        prefer = "lighter" if luminance(against) < 0.18 else "darker"
    step = 0.01 if prefer == "lighter" else -0.01
    best = color
    for _ in range(100):
        L += step
        if not 0 <= L <= 1:
            break
        best = from_oklch(L, C, H)
        if contrast(best, against) >= target:
            return best
    return best


def mix(a, b, weight):
    """`weight` of a, rest b (sRGB, like CSS color-mix in srgb)."""
    ra, rb = hex_rgb(a), hex_rgb(b)
    return rgb_hex(tuple(x * weight + y * (1 - weight) for x, y in zip(ra, rb)))


# ---------- theme validation and CSS ----------
def _color(theme_colors, key, required=False):
    value = theme_colors.get(key)
    if value is None:
        if required:
            raise ValueError(f"Theme colors.{key} is required (a #rrggbb hex colour).")
        return None
    if not isinstance(value, str) or not HEX.fullmatch(value):
        raise ValueError(f"Theme colors.{key} must be a #rrggbb hex colour.")
    return value.lower()


def complete_colors(theme):
    """Fill derived colours so every token is explicit and contrast-checked."""
    colors = theme.get("colors")
    if not isinstance(colors, dict):
        raise ValueError("Theme needs a colors object with at least bg, text and accent.")
    bg, text, accent = (_color(colors, k, True) for k in ("bg", "text", "accent"))
    dark = luminance(bg) < 0.18
    if contrast(text, bg) < 7:
        raise ValueError(f"Theme text on bg has contrast {contrast(text, bg):.1f}; it needs at least 7.")
    out = {"bg": bg, "text": text}
    out["accent"] = accent if theme.get("keep_accent") else fit_contrast(accent, bg, 3.2)
    accent2 = _color(colors, "accent2")
    if not accent2:
        L, C, H = to_oklch(out["accent"])
        accent2 = from_oklch(0.42 if dark else 0.55, max(0.05, C * 0.55), (H + 150) % 360)
    out["accent2"] = accent2
    out["muted"] = _color(colors, "muted") or fit_contrast(mix(text, bg, 0.74), bg, 4.6)
    alt_bg = _color(colors, "alt_bg") or (from_oklch(0.95, 0.012, to_oklch(bg)[2]) if dark else text)
    alt_text = _color(colors, "alt_text") or (text if not dark else bg)
    if contrast(alt_text, alt_bg) < 7:
        alt_text = "#141414" if luminance(alt_bg) > 0.18 else "#f7f5f2"
    out["alt_bg"], out["alt_text"] = alt_bg, alt_text
    out["accent_alt"] = _color(colors, "accent_alt") or fit_contrast(out["accent"], alt_bg, 3.0)
    L, C, H = to_oklch(bg)
    out["stage"] = _color(colors, "stage") or from_oklch(max(0.06, L - 0.05) if dark else L - 0.045, C, H)
    # Text on a filled accent (badges): whichever of near-black / near-white reads better.
    ink_dark, ink_light = from_oklch(0.16, 0.02, H), from_oklch(0.98, 0.008, H)
    out["on_accent"] = ink_dark if contrast(ink_dark, out["accent"]) >= contrast(ink_light, out["accent"]) else ink_light
    return out, dark


def font_stack(spec, fallback_generic):
    if not spec:
        return None
    family = spec.get("family")
    if not isinstance(family, str) or not family.strip() or re.search(r'[<>"\\;{}\x00-\x1f]', family):
        raise ValueError("Each theme font needs a plain family name.")
    generic = spec.get("generic", fallback_generic)
    if generic not in GENERIC:
        raise ValueError("Theme font generic must be serif, sans-serif or monospace.")
    return f'"{family}", ' + FALLBACKS.get(generic, generic)


def _type_value(value, kind, key):
    if kind == "int":
        number = int(value)
        if not 100 <= number <= 1000:
            raise ValueError(f"Theme type.{key} must be a weight from 100 to 1000.")
        return str(number)
    if kind == "px":
        number = float(value)
        if not 24 <= number <= 400:
            raise ValueError(f"Theme type.{key} must be between 24 and 400 (px).")
        return f"{number:g}px"
    if kind == "num":
        number = float(value)
        if not 0.6 <= number <= 1.6:
            raise ValueError(f"Theme type.{key} must be between 0.6 and 1.6.")
        return f"{number:g}"
    if kind == "em":
        text = str(value)
        if not re.fullmatch(r"-?\d*\.?\d+em", text):
            raise ValueError(f"Theme type.{key} must look like .12em or -.02em.")
        return text
    if kind == "case":
        if value not in ("uppercase", "none", "lowercase", "capitalize"):
            raise ValueError(f"Theme type.{key} must be uppercase, none, lowercase or capitalize.")
        return value
    raise ValueError(key)


def theme_css(theme):
    colors, dark = complete_colors(theme)
    fonts = theme.get("fonts") or {}
    root = []
    heading = font_stack(fonts.get("heading"), "serif")
    body = font_stack(fonts.get("body"), "sans-serif")
    label = font_stack(fonts.get("label"), "sans-serif") or body
    cjk = fonts.get("cjk")
    if cjk:
        cjk_family = font_stack(cjk, "sans-serif").split(",")[0]
        heading = heading and heading.replace(", ", f", {cjk_family}, ", 1)
        body = body and body.replace(", ", f", {cjk_family}, ", 1)
        label = label and label.replace(", ", f", {cjk_family}, ", 1)
    if heading:
        root.append(f"--heading-font: {heading};")
    if body:
        root.append(f"--body-font: {body};")
    if label:
        root.append(f"--label-font: {label};")
    root.append("--mono-font: var(--label-font);")
    for key, value in (theme.get("type") or {}).items():
        if key not in TYPE_KEYS:
            raise ValueError("Unknown theme type key: " + key)
        token, kind = TYPE_KEYS[key]
        root.append(f"{token}: {_type_value(value, kind, key)};")
    radius = (theme.get("shape") or {}).get("radius")
    if radius is not None:
        radius = float(radius)
        if not 0 <= radius <= 48:
            raise ValueError("Theme shape.radius must be between 0 and 48 (px).")
        root.append(f"--radius: {radius:g}px;")
    root += [f"--stage-bg: {colors['stage']};", f"--alt-bg: {colors['alt_bg']};", f"--alt-text: {colors['alt_text']};"]
    slide = [
        f"--slide-bg: {colors['bg']};", f"--text: {colors['text']};", f"--muted: {colors['muted']};",
        f"--accent: {colors['accent']};", f"--accent-2: {colors['accent2']};", f"--on-accent: {colors['on_accent']};",
    ]
    if not dark:
        # Light stages: soft glows, quieter photo matte, cards slightly darker than the page.
        slide += [
            "--glow-a: color-mix(in srgb, var(--accent) 14%, var(--slide-bg));",
            "--glow-b: color-mix(in srgb, var(--accent-2) 14%, var(--slide-bg));",
            "--card: color-mix(in srgb, var(--text) 5%, var(--slide-bg));",
            "--photo-matte: color-mix(in srgb, var(--text) 7%, var(--slide-bg));",
        ]
    alt = [f"--accent: {colors['accent_alt']};"]
    css = (
        "/* Theme: " + re.sub(r"[^\w .,&·()+-]", "", str(theme.get("name", "custom")))[:120] + " */\n"
        ":root { " + " ".join(root) + " }\n"
        ".slide { " + " ".join(slide) + " }\n"
        ".slide.theme-alt, .slide.theme-paper { " + " ".join(alt) + " }\n"
    )
    if not dark:
        css += (".slide.glow-ember, .slide.glow-accent, .slide.glow-rust, .slide.glow-plum "
                "{ --glow-a: color-mix(in srgb, var(--accent) 18%, var(--slide-bg)); }\n"
                ".slide.glow-alt, .slide.glow-indigo, .slide.glow-steel, .slide.glow-violet, .slide.glow-teal "
                "{ --glow-a: color-mix(in srgb, var(--accent-2) 18%, var(--slide-bg)); }\n")
    return css, colors


def theme_font_files(theme):
    """Yield (family, file, weight, subset) for every font file the theme embeds."""
    for role in ("heading", "body", "label", "cjk"):
        spec = (theme.get("fonts") or {}).get(role)
        if not spec:
            continue
        for item in spec.get("files", []):
            yield spec["family"], item["file"], item.get("weight", "400"), item.get("style", "normal"), bool(
                item.get("subset", True))

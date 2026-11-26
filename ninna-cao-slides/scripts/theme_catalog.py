"""Return the independently authored visual directions and their CSS tokens."""
from functools import lru_cache
from pathlib import Path
import json

ASSETS = Path(__file__).resolve().parents[1] / "assets"
FONTS = {
    "serif": 'Georgia, "Liberation Serif", serif',
    "slab": '"Rockwell", "DejaVu Serif", Georgia, serif',
    "mono": '"DejaVu Sans Mono", "Liberation Mono", monospace',
    "condensed": '"Aptos Narrow", "Liberation Sans Narrow", sans-serif',
    "rounded": '"Trebuchet MS", "DejaVu Sans", sans-serif',
    "humanist": '"Aptos", "Open Sans", system-ui, sans-serif',
    "grotesk": '"Arial", "Liberation Sans", system-ui, sans-serif',
}

@lru_cache(maxsize=1)
def styles():
    rows = json.loads((ASSETS / "styles.json").read_text(encoding="utf-8"))
    return {row["id"]: row for row in rows}


def rgb(color):
    return [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def luminance(color):
    channels = [n / 12.92 if n <= 0.04045 else ((n + 0.055) / 1.055) ** 2.4 for n in rgb(color)]
    return sum(n * weight for n, weight in zip(channels, (0.2126, 0.7152, 0.0722)))


def contrast(first, second):
    lo, hi = sorted((luminance(first), luminance(second)))
    return (hi + 0.05) / (lo + 0.05)


def css_for(key):
    row = styles()[key]
    ink, background, accent = row["ink"], row["surface"], row["accent"]
    visible_accent = accent if contrast(accent, background) >= 4.5 else ink
    duration = {"quick": "340ms", "even": "510ms", "soft": "680ms"}[row["pace"]]
    token_css = f"""
    :root {{
      --heading-font: {FONTS[row["font"]]};
      --body-font: system-ui, "Liberation Sans", sans-serif;
      --stage-bg: {background};
    }}
    .slide {{
      --slide-bg: {background};
      --text: {ink};
      --accent: {visible_accent};
      --secondary: {visible_accent};
      --motif: {accent};
      --detail: {row["detail"]};
      --muted: color-mix(in srgb, {ink} 87%, {background});
      --rule: color-mix(in srgb, {ink} 37%, {background});
      --photo-matte: {row["detail"]};
      --motion-duration: {duration};
    }}
    """
    return (ASSETS / "catalog.css").read_text(encoding="utf-8") + token_css

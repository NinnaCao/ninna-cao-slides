#!/usr/bin/env python3
"""Export a local Visual Slides deck to PDF.

Engines
  screens (default)  Pixel-exact: renders each slide's final state in Chrome and places one
                     image per page, with web links kept clickable. Keeps image fades (CSS
                     masks), glows and blends exactly as on screen. Text is not selectable.
  browser            Chrome's print engine: selectable vector text and a smaller file, but
                     print ignores CSS masks, so faded photos show hard edges. Use it only
                     for decks without fades, and inspect the result.
  static             WeasyPrint, when no browser is available. Inspect for CSS differences.
"""
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory

from check_deck import audit


def print_with_browser(source, target, chromium):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = launch(p, chromium)
        try:
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(source.as_uri())
            page.evaluate("document.fonts.ready")
            page.locator("img").evaluate_all(
                "images => Promise.all(images.map(img => img.decode().catch(() => {})))"
            )
            page.pdf(path=target, prefer_css_page_size=True, print_background=True)
        finally:
            browser.close()


FINAL_STATE_CSS = """
.deck-controls, .notes-panel { display: none !important; }
.slide .reveal, .js .slide .reveal { opacity: 1 !important; animation: none !important; transform: none !important; }
.trace { animation: none !important; stroke-dashoffset: 0 !important; }
.slide img, .backdrop img { animation: none !important; }
"""


def launch(p, chromium):
    if chromium:
        return p.chromium.launch(executable_path=chromium)
    try:  # The installed Chrome avoids a separate browser download.
        return p.chromium.launch(channel="chrome")
    except Exception:
        return p.chromium.launch()


def render_screens(source, target, chromium, scale, quality):
    import fitz
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = launch(p, chromium)
        try:
            page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=scale)
            page.goto(source.as_uri())
            page.evaluate("document.fonts.ready")
            page.add_style_tag(content=FINAL_STATE_CSS)
            count = page.evaluate("document.querySelectorAll('.slide').length")
            with fitz.open() as pdf:
                for index in range(count):
                    page.evaluate("i => (window.slideDeck || window.ninnaDeck).goTo(i)", index)
                    page.locator(f".slide >> nth={index}").locator("img").evaluate_all(
                        "images => Promise.all(images.map(img => img.decode().catch(() => {})))")
                    page.wait_for_timeout(350)
                    image = page.screenshot(type="jpeg", quality=quality)
                    links = page.evaluate("""i => [...document.querySelectorAll('.slide')[i].querySelectorAll('a[href]')]
                        .filter(a => /^(https?:|mailto:)/.test(a.getAttribute('href')))
                        .map(a => { const r = a.getBoundingClientRect(); return {href: a.href, x: r.left, y: r.top, w: r.width, h: r.height}; })""", index)
                    sheet = pdf.new_page(width=1440, height=810)  # 20 × 11.25 in, 16:9
                    sheet.insert_image(sheet.rect, stream=image)
                    ratio = 1440 / 1920
                    for link in links:
                        rect = fitz.Rect(link["x"] * ratio, link["y"] * ratio,
                                         (link["x"] + link["w"]) * ratio, (link["y"] + link["h"]) * ratio)
                        sheet.insert_link({"kind": fitz.LINK_URI, "from": rect, "uri": link["href"]})
                pdf.set_metadata({"title": page.title(), "creator": "Visual Slides"})
                pdf.save(target, deflate=True, garbage=4)
        finally:
            browser.close()


def print_static(source, target):
    from weasyprint import HTML

    HTML(filename=str(source)).write_pdf(str(target))


def verify_and_copy(source, output, count, compact):
    import fitz

    with fitz.open(source) as original:
        if len(original) != count:
            raise ValueError(f"PDF contains {len(original)} pages, expected {count}.")
        for page in original:
            if abs(page.rect.width / page.rect.height - 16 / 9) > 0.004:
                raise ValueError(f"Page {page.number + 1} is outside the 16:9 aspect ratio.")
        if not compact:
            output.write_bytes(source.read_bytes())
            return

        with fitz.open() as smaller:
            for page in original:
                scale = 1280 / page.rect.width
                pixels = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
                destination = smaller.new_page(width=page.rect.width, height=page.rect.height)
                destination.insert_image(destination.rect, stream=pixels.tobytes("jpeg", jpg_quality=87))
            smaller.save(output, deflate=True, garbage=4)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--engine", choices=("screens", "browser", "static"), default="screens")
    parser.add_argument("--scale", type=float, default=1, help="Screens engine: device scale factor (2 = sharper, larger file).")
    parser.add_argument("--quality", type=int, default=88, help="Screens engine: JPEG quality.")
    parser.add_argument("--chromium", help="Path to a local Chromium executable for the browser engine.")
    parser.add_argument("--compact", action="store_true", help="Rasterize pages at 1280 × 720 for a smaller PDF.")
    args = parser.parse_args()
    source = args.source.resolve()
    report = audit(source)
    if report["status"] != "pass":
        parser.error("; ".join(report["errors"]))
    output = args.destination.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as scratch:
        draft = Path(scratch, "rendered.pdf")
        if args.engine == "screens":
            render_screens(source, draft, args.chromium, args.scale, args.quality)
        elif args.engine == "browser":
            print_with_browser(source, draft, args.chromium)
        else:
            print_static(source, draft)
        verify_and_copy(draft, output, report["main_slides"] + report["appendix_slides"], args.compact)
    print(output)


if __name__ == "__main__":
    main()

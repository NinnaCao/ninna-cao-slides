#!/usr/bin/env python3
"""Print a local Ninna deck to PDF, with an optional compact image edition."""
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory

from check_deck import audit


def print_with_browser(source, target, chromium):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        options = {"executable_path": chromium} if chromium else {}
        browser = p.chromium.launch(**options)
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
    parser.add_argument("--engine", choices=("browser", "static"), default="browser")
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
        if args.engine == "browser":
            print_with_browser(source, draft, args.chromium)
        else:
            print_static(source, draft)
        verify_and_copy(draft, output, report["main_slides"] + report["appendix_slides"], args.compact)
    print(output)


if __name__ == "__main__":
    main()

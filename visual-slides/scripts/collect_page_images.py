#!/usr/bin/env python3
"""Collect candidate images from a brand's own web pages (product pages, newsroom, press kit).

Use it when a deck is about a company, brand or product: official imagery shows the exact
product, colour and context, and keeps the deck on-brand.

  python3 scripts/collect_page_images.py https://steelseries.com/gaming-headsets/arctis-nova-pro-omni --out media/candidates/omni
  python3 scripts/collect_page_images.py saved-page.html --base https://www.dyson.com/ --out media/candidates/dyson

Reads <img src/srcset>, <picture><source srcset>, og:image / twitter:image, JSON-LD "image"
and inline style background images; keeps the largest srcset variant; drops icons, sprites,
tracking pixels and tiny images; writes <out>/candidates.json (same format as find_images.py,
so fetch_image.py --candidates ... --pick N works) and a numbered contact-sheet.jpg.

If a site refuses automated requests (403, bot check), do not work around it: open the page in
a browser, save it (or copy its HTML) and pass the file with --base, or ask the user. Official
images are copyrighted. Use them for presentations about that company (internal, editorial,
commentary or education), prefer the press or media kit for anything published, follow the
site's terms, never imply endorsement, and credit "© <Brand>" with the page URL.
"""
from argparse import ArgumentParser
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
import urllib.parse
import urllib.request

USER_AGENT = "deck-image-finder/3.1 (python-urllib; presentation image research)"
SKIP = re.compile(r"(sprite|icon|logo-?mark|favicon|pixel|spacer|placeholder|blank|badge|rating|flag|avatar|payment|loader|\.svg($|\?)|1x1|data:)", re.I)


def size_hint(url, descriptor=""):
    """Best guess of an image's width from a srcset descriptor or common CDN parameters."""
    match = re.match(r"\s*(\d+)w", descriptor or "")
    if match:
        return int(match.group(1))
    for pattern in (r"[?&](?:w|width|wid|imwidth|resize)=(\d+)", r"/(\d{3,4})x\d{2,4}[/_.-]", r"[_-](\d{3,4})w[._-]", r"/w_(\d{3,4})"):
        match = re.search(pattern, url)
        if match:
            return int(match.group(1))
    return 0


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found = []
        self.title = ""
        self._in_title = False
        self._in_jsonld = False
        self._jsonld = ""

    def add(self, url, width=0, alt="", kind="img"):
        if url and not SKIP.search(url):
            self.found.append({"url": url.strip(), "width": width, "alt": (alt or "").strip(), "kind": kind})

    def add_srcset(self, srcset, alt, kind):
        best = None
        for part in (srcset or "").split(","):
            bits = part.strip().split()
            if not bits:
                continue
            width = size_hint(bits[0], bits[1] if len(bits) > 1 else "")
            if best is None or width > best[1]:
                best = (bits[0], width)
        if best:
            self.add(best[0], best[1], alt, kind)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title" and not self.title:
            self._in_title = True
        if tag == "img":
            alt = a.get("alt", "")
            if a.get("srcset") or a.get("data-srcset"):
                self.add_srcset(a.get("srcset") or a.get("data-srcset"), alt, "img")
            source = a.get("src") or a.get("data-src") or a.get("data-lazy-src")
            if source:
                width = int(a["width"]) if str(a.get("width", "")).isdigit() else size_hint(source)
                self.add(source, width, alt, "img")
        elif tag == "source" and (a.get("srcset") or a.get("data-srcset")):
            self.add_srcset(a.get("srcset") or a.get("data-srcset"), "", "picture")
        elif tag == "meta" and (a.get("property") in ("og:image", "og:image:secure_url") or a.get("name") in ("twitter:image", "twitter:image:src")):
            self.add(a.get("content"), 1200, "Share image", "meta")
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._jsonld = ""
        style = a.get("style") or ""
        for match in re.finditer(r"url\((['\"]?)(.*?)\1\)", style):
            self.add(match.group(2), size_hint(match.group(2)), "", "background")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            for match in re.finditer(r'"image"\s*:\s*(\[[^\]]*\]|"[^"]+")', self._jsonld):
                for url in re.findall(r'"(https?://[^"]+)"', match.group(1)):
                    self.add(url, 0, "Structured data image", "jsonld")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_jsonld:
            self._jsonld += data


RENDER_JS = r"""
async () => {
  for (let y = 0; y < document.body.scrollHeight && y < 24000; y += 900) {
    window.scrollTo(0, y); await new Promise(r => setTimeout(r, 180));
  }
  window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 600));
  const out = [];
  document.querySelectorAll('img').forEach(img => {
    const url = img.currentSrc || img.src;
    if (url) out.push({url, width: img.naturalWidth || 0, height: img.naturalHeight || 0, alt: img.alt || '', kind: 'img'});
  });
  document.querySelectorAll('*').forEach(el => {
    const bg = getComputedStyle(el).backgroundImage;
    const m = bg && bg.match(/url\(["']?(.*?)["']?\)/);
    if (m && el.offsetWidth > 300) out.push({url: m[1], width: el.offsetWidth, height: el.offsetHeight, alt: el.getAttribute('aria-label') || '', kind: 'background'});
  });
  const meta = document.querySelector('meta[property="og:image"]');
  if (meta) out.push({url: meta.content, width: 1200, height: 0, alt: 'Share image', kind: 'meta'});
  return {title: document.title, html: document.documentElement.outerHTML.length, images: out};
}
"""


def render_page(url, chromium=None):
    """Load the page in Chrome like a normal visit, so script-built galleries appear."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(executable_path=chromium) if chromium else p.chromium.launch(channel="chrome")
        except Exception:
            browser = p.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1600, "height": 1000})
            response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
            if response and response.status >= 400:
                raise RuntimeError(f"HTTP {response.status}")
            page.wait_for_timeout(2500)
            result = page.evaluate(RENDER_JS)
        finally:
            browser.close()
    return result


def fetch_html(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read(8_000_000).decode(response.headers.get_content_charset() or "utf-8", "replace")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("page", help="Official page URL, or a saved HTML file.")
    parser.add_argument("--base", help="Page URL to resolve relative links when reading a saved file.")
    parser.add_argument("--out", default="media/candidates/official")
    parser.add_argument("--brand", help="Name for the credit line, e.g. SteelSeries. Defaults to the site name.")
    parser.add_argument("--min-width", type=int, default=600, help="Drop images known to be narrower.")
    parser.add_argument("--limit", type=int, default=24)
    parser.add_argument("--render", action="store_true", help="Load the page in Chrome first (for sites that build images with JavaScript). Needs playwright.")
    parser.add_argument("--chromium", help="Chromium executable for --render; default is the installed Chrome.")
    args = parser.parse_args()

    if args.render:
        if not re.match(r"https?://", args.page):
            parser.error("--render needs a URL.")
        base = args.page
        try:
            rendered = render_page(args.page, args.chromium)
        except Exception as exc:
            print(json.dumps({"candidates": 0, "error": str(exc),
                              "advice": "The page did not load for an automated browser. Do not work around it; "
                                        "ask the user for the images or use the brand's press kit."}, indent=2))
            sys.exit(3)
        collector = Collector()
        collector.title = rendered["title"]
        for item in rendered["images"]:
            if not SKIP.search(item["url"]) and (item["width"] or 0) >= 1:
                collector.found.append(item)
        markup = None
    elif re.match(r"https?://", args.page):
        base = args.page
        try:
            markup = fetch_html(args.page)
        except Exception as exc:  # Report refusals; never work around them.
            print(json.dumps({"candidates": 0, "error": str(exc),
                              "advice": "The site refused or failed the request. Open it in a browser, save the page "
                                        "and rerun with the file and --base, or ask the user for the images."}, indent=2))
            sys.exit(3)
    else:
        markup = Path(args.page).read_text(encoding="utf-8", errors="replace")
        base = args.base or ""
    if not args.render and markup is None:
        markup = ""
    if markup is not None:
        collector = Collector()
        collector.feed(markup)
    host = urllib.parse.urlparse(base).netloc.replace("www.", "")
    brand = args.brand or (host.split(".")[0].capitalize() if host else "Brand")

    rows, seen = [], set()
    for item in collector.found:
        url = urllib.parse.urljoin(base, item["url"]) if base else item["url"]
        if not url.startswith("https://"):
            continue
        key = re.sub(r"[?#].*$", "", url)
        key = re.sub(r"[_-]\d{2,4}x\d{2,4}(?=\.)", "", key)
        if key in seen:
            continue
        seen.add(key)
        if item["width"] and item["width"] < args.min_width:
            continue
        rows.append({
            "provider": "official/" + (host or "page"),
            "title": item["alt"] or Path(urllib.parse.urlparse(url).path).stem.replace("-", " ").replace("_", " ")[:80],
            "creator": brand,
            "license": "official",
            "license_label": f"© {brand} (official website)",
            "license_url": "",
            "page": base,
            "image_url": url,
            "thumb_url": url,
            "width": item["width"],
            "height": item.get("height", 0) or 0,
            "alt_hint": item["alt"],
            "note": "Official imagery: use for presentations about the company; follow the site's terms; credit © " + brand,
        })
    # Large and described images first; share images last (often cropped with text).
    rows.sort(key=lambda r: (r["alt_hint"] == "Share image", -(r["width"] or 0), not r["alt_hint"]))
    rows = rows[: args.limit]
    for index, row in enumerate(rows):
        row["index"] = index
        row["query"] = collector.title.strip()[:120]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "candidates.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    sheet = None
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from find_images import contact_sheet
        if contact_sheet(rows, out / "contact-sheet.jpg"):
            sheet = str(out / "contact-sheet.jpg")
    except Exception:
        pass
    print(json.dumps({"page_title": collector.title.strip()[:120], "found": len(collector.found), "candidates": len(rows),
                      "file": str(out / "candidates.json"), "contact_sheet": sheet,
                      "next": "Open the contact sheet, check the full image, then fetch_image.py --candidates ... --pick N --manifest deck.json"},
                     ensure_ascii=False, indent=2))
    sys.exit(0 if rows else 2)


if __name__ == "__main__":
    main()

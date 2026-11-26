#!/usr/bin/env python3
"""Search openly licensed image libraries for slide visuals and save a numbered contact sheet.

Sources that need no key: Openverse (CC and public-domain images from Flickr, museums,
Wikimedia and more) and Wikimedia Commons. Unsplash and Pexels are added automatically
when UNSPLASH_ACCESS_KEY or PEXELS_API_KEY is set in the environment.

Examples
  python3 scripts/find_images.py "gaming headset dark studio" --out media/candidates
  python3 scripts/find_images.py "hands sorting sticky notes" --sources openverse,commons --min-width 2000
  python3 scripts/find_images.py "city night rain" --orientation wide --limit 16

Search with one to three concrete nouns ("headphones", "studio microphone", "hands sketching")
and run several short queries rather than one long sentence: the libraries match keywords.

Writes <out>/candidates.json and, when Pillow is installed, <out>/contact-sheet.jpg with each
candidate's index, size and license. Open the contact sheet, pick by index, then fetch with
scripts/fetch_image.py --candidates <out>/candidates.json --pick N.
"""
import argparse
import html
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from itertools import zip_longest
from pathlib import Path

USER_AGENT = "deck-image-finder/3.0 (python-urllib; presentation image search)"
TIMEOUT = 25
# Known delivery limits seen through Openverse. Listed sizes can exceed what is served.
PROVIDER_NOTES = {
    "rawpixel": "Openverse serves a ~1024 px preview; download the original from the source page for large use.",
    "stocksnap": "Direct downloads may be refused; use the source page's download button if fetch fails.",
}
# Licenses that allow reuse in a presentation shared with others, including commercially.
OPEN_LICENSES = {"cc0", "pdm", "by", "by-sa", "unsplash", "pexels", "public domain"}


def get_json(url, headers=None):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def get_bytes(url, limit=6_000_000):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("thumbnail too large")
    return data


def strip_tags(value):
    return html.unescape(re.sub(r"<[^>]+>", "", value or "")).strip()


def openverse(query, args):
    params = {
        "q": query,
        "page_size": min(args.limit * 2, 20),  # anonymous limit
        "license": "cc0,pdm,by,by-sa" if not args.allow_nc else "cc0,pdm,by,by-sa,by-nc,by-nc-sa",
        "mature": "false",
    }
    if args.min_width >= 1200:
        params["size"] = "large"  # Openverse's own filter; far more usable results than filtering afterwards.
    if args.orientation:
        params["aspect_ratio"] = args.orientation
    if args.photos_only:
        params["category"] = "photograph"
    data = get_json("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params))
    rows = []
    for item in data.get("results", []):
        license_name = (item.get("license") or "").lower()
        version = item.get("license_version") or ""
        rows.append({
            "provider": "openverse/" + (item.get("source") or item.get("provider") or "unknown"),
            "title": item.get("title") or "Untitled",
            "creator": item.get("creator") or "Unknown",
            "license": license_name,
            "license_label": ("CC " + license_name.upper() + " " + version).strip() if license_name not in ("cc0", "pdm") else ("CC0" if license_name == "cc0" else "Public domain"),
            "license_url": item.get("license_url") or "",
            "page": item.get("foreign_landing_url") or "",
            "image_url": item.get("url") or "",
            "thumb_url": item.get("thumbnail") or item.get("url") or "",
            "width": item.get("width") or 0,
            "height": item.get("height") or 0,
            "alt_hint": item.get("title") or "",
            "note": PROVIDER_NOTES.get(item.get("source") or "", ""),
        })
    return rows


def commons(query, args):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": "filetype:bitmap " + query, "gsrnamespace": 6, "gsrlimit": min(args.limit * 2, 40),
        "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 1920,
        # Wikimedia pre-renders 330, 960, 1280, 1920 and 3840 px; asking for those avoids rate limits.
    }
    data = get_json("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params))
    rows = []
    for page in (data.get("query", {}).get("pages", {}) or {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        short = strip_tags(meta.get("LicenseShortName", {}).get("value", ""))
        key = short.lower().replace("cc ", "").replace("cc-", "")
        key = "cc0" if "cc0" in key else "public domain" if "public domain" in key or key == "pd" else re.sub(r"\s*\d.*$", "", key).strip()
        rows.append({
            "provider": "wikimedia-commons",
            "title": strip_tags(meta.get("ObjectName", {}).get("value", "")) or page.get("title", "").replace("File:", ""),
            "creator": strip_tags(meta.get("Artist", {}).get("value", "")) or "Unknown",
            "license": key,
            "license_label": short or "See file page",
            "license_url": strip_tags(meta.get("LicenseUrl", {}).get("value", "")),
            "page": info.get("descriptionurl", ""),
            "image_url": (info.get("thumburl") or info.get("url", "")).split("?")[0],
            "original_url": info.get("url", ""),
            "thumb_url": (info.get("thumburl") or info.get("url", "")).split("?")[0].replace("/1920px-", "/330px-"),
            "width": info.get("width", 0),
            "height": info.get("height", 0),
            "alt_hint": strip_tags(meta.get("ImageDescription", {}).get("value", ""))[:160],
        })
    return rows


def unsplash(query, args):
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        return []
    params = {"query": query, "per_page": min(args.limit * 2, 30), "content_filter": "high"}
    if args.orientation:
        params["orientation"] = {"wide": "landscape", "tall": "portrait", "square": "squarish"}[args.orientation]
    data = get_json("https://api.unsplash.com/search/photos?" + urllib.parse.urlencode(params), {"Authorization": "Client-ID " + key})
    rows = []
    for item in data.get("results", []):
        rows.append({
            "provider": "unsplash",
            "title": item.get("description") or item.get("alt_description") or "Untitled",
            "creator": (item.get("user") or {}).get("name", "Unknown"),
            "license": "unsplash",
            "license_label": "Unsplash License",
            "license_url": "https://unsplash.com/license",
            "page": (item.get("links") or {}).get("html", ""),
            "image_url": (item.get("urls") or {}).get("raw", "") + "&w=2600&q=85&fm=jpg",
            "thumb_url": (item.get("urls") or {}).get("small", ""),
            "download_location": (item.get("links") or {}).get("download_location", ""),
            "width": item.get("width", 0),
            "height": item.get("height", 0),
            "alt_hint": item.get("alt_description") or "",
        })
    return rows


def pexels(query, args):
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        return []
    params = {"query": query, "per_page": min(args.limit * 2, 40)}
    if args.orientation:
        params["orientation"] = {"wide": "landscape", "tall": "portrait", "square": "square"}[args.orientation]
    data = get_json("https://api.pexels.com/v1/search?" + urllib.parse.urlencode(params), {"Authorization": key})
    rows = []
    for item in data.get("photos", []):
        src = item.get("src") or {}
        rows.append({
            "provider": "pexels",
            "title": item.get("alt") or "Untitled",
            "creator": item.get("photographer", "Unknown"),
            "license": "pexels",
            "license_label": "Pexels License",
            "license_url": "https://www.pexels.com/license/",
            "page": item.get("url", ""),
            "image_url": src.get("original", ""),
            "thumb_url": src.get("medium", ""),
            "width": item.get("width", 0),
            "height": item.get("height", 0),
            "alt_hint": item.get("alt") or "",
        })
    return rows


SOURCES = {"openverse": openverse, "commons": commons, "unsplash": unsplash, "pexels": pexels}


def contact_sheet(rows, path):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False
    cell_w, cell_h, label_h, cols = 360, 230, 46, 4
    count = len(rows)
    if not count:
        return False
    sheet_rows = (count + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w, sheet_rows * (cell_h + label_h)), "#16171b")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("Arial.ttf", 15)
        big = ImageFont.truetype("Arial Bold.ttf", 22)
    except OSError:
        font = big = ImageFont.load_default()
    for index, row in enumerate(rows):
        x, y = (index % cols) * cell_w, (index // cols) * (cell_h + label_h)
        try:
            thumb = Image.open(io.BytesIO(get_bytes(row["thumb_url"]))).convert("RGB")
            thumb.thumbnail((cell_w - 8, cell_h - 8))
            sheet.paste(thumb, (x + (cell_w - thumb.width) // 2, y + (cell_h - thumb.height) // 2))
        except Exception:  # A failed thumbnail should not stop the search.
            draw.text((x + 12, y + 100), "thumbnail unavailable", fill="#888", font=font)
        draw.rectangle([x + 6, y + 6, x + 46, y + 36], fill="#ff7338")
        draw.text((x + 12, y + 8), str(index), fill="#111", font=big)
        label = f'{row["width"]}×{row["height"]} · {row["license_label"][:22]} · {row["provider"].split("/")[-1][:14]}'
        draw.text((x + 8, y + cell_h + 6), label, fill="#e8e2da", font=font)
        draw.text((x + 8, y + cell_h + 25), row["title"][:44], fill="#a9a39c", font=font)
    sheet.save(path, quality=82)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query", help="What the picture should show, in plain words.")
    parser.add_argument("--out", default="media/candidates", help="Folder for candidates.json and contact-sheet.jpg.")
    parser.add_argument("--sources", default="openverse,commons,unsplash,pexels", help="Comma list; keyed sources are skipped without a key.")
    parser.add_argument("--limit", type=int, default=12, help="Candidates to keep after filtering.")
    parser.add_argument("--min-width", type=int, default=1600, help="Smallest acceptable pixel width.")
    parser.add_argument("--orientation", choices=["wide", "tall", "square"])
    parser.add_argument("--photos-only", action="store_true", help="Openverse: photographs only.")
    parser.add_argument("--allow-nc", action="store_true", help="Also keep NonCommercial licenses (internal, non-commercial decks only).")
    args = parser.parse_args()

    rows, problems = [], []
    for name in [s.strip() for s in args.sources.split(",") if s.strip()]:
        if name not in SOURCES:
            parser.error("Unknown source: " + name)
        try:
            rows.extend(SOURCES[name](args.query, args))
        except Exception as exc:  # Report and continue with the other libraries.
            problems.append(f"{name}: {exc}")
    allowed = OPEN_LICENSES | ({"by-nc", "by-nc-sa"} if args.allow_nc else set())
    # Interleave providers so one library cannot fill every slot.
    groups = {}
    for row in rows:
        groups.setdefault(row["provider"].split("/")[0], []).append(row)
    rows = [row for batch in zip_longest(*groups.values()) for row in batch if row]
    seen, kept = set(), []
    for row in rows:
        if not row["image_url"] or row["image_url"] in seen:
            continue
        if int(row["width"] or 0) < args.min_width:
            continue
        if row["license"] not in allowed:
            continue
        seen.add(row["image_url"])
        kept.append(row)
    kept = kept[: args.limit]
    for index, row in enumerate(kept):
        row["index"] = index
        row["query"] = args.query

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "candidates.json").write_text(json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8")
    sheet = out / "contact-sheet.jpg"
    made = contact_sheet(kept, sheet)
    print(json.dumps({
        "query": args.query,
        "candidates": len(kept),
        "file": str(out / "candidates.json"),
        "contact_sheet": str(sheet) if made else None,
        "problems": problems,
        "next": "Open the contact sheet, inspect the full image, then run fetch_image.py --candidates ... --pick N",
    }, ensure_ascii=False, indent=2))
    sys.exit(0 if kept else 2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Download one chosen image, save it as a slide-ready WebP and record its credit.

Examples
  python3 scripts/fetch_image.py --candidates media/candidates/candidates.json --pick 3 media/hero.webp --manifest deck.json
  python3 scripts/fetch_image.py https://example.org/photo.jpg media/hero.webp \
      --title "Studio headset" --creator "A. Photographer" --license "CC BY 4.0" \
      --page https://example.org/photo --manifest deck.json

The image is checked as a real raster image, converted to sRGB, resized so its long edge is
at most --max-edge pixels (default 2600, enough for a full 1920 × 1080 slide on a high-density
screen) and saved without metadata. With --manifest, a credit entry is added or updated in the
manifest's "credits" list; the builder turns that list into a sources and image credits slide.
Use --keep-format for a PNG with transparency, such as a product cut-out.
"""
import argparse
import io
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

USER_AGENT = "deck-image-finder/3.0 (python-urllib; presentation image download)"
MAX_BYTES = 40_000_000


def download(url):
    if not url.startswith("https://"):
        raise ValueError("Use an https image URL.")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                kind = response.headers.get("Content-Type", "")
                data = response.read(MAX_BYTES + 1)
            break
        except urllib.error.HTTPError as exc:
            # 429 means "slow down": wait as long as the server asks, then try again.
            if exc.code != 429 or attempt == 3:
                raise
            wait = exc.headers.get("Retry-After", "")
            time.sleep(min(int(wait), 60) if wait.isdigit() else 8 * (attempt + 1))
    if len(data) > MAX_BYTES:
        raise ValueError("Image is larger than 40 MB.")
    if kind and not kind.startswith(("image/", "application/octet-stream", "binary/octet-stream")):
        raise ValueError("The URL did not return an image (" + kind + ").")
    return data


def ping_unsplash(location):
    """Unsplash API terms ask clients to report a download when a photo is used."""
    import os
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not (key and location):
        return
    try:
        request = urllib.request.Request(location, headers={"User-Agent": USER_AGENT, "Authorization": "Client-ID " + key})
        urllib.request.urlopen(request, timeout=20).read(1)
    except Exception:
        pass


def convert(data, output, max_edge, quality, keep_format):
    try:
        from PIL import Image, ImageOps
    except ImportError:
        output.write_bytes(data)
        return {"converted": False, "note": "Pillow is not installed; saved the original bytes."}
    image = Image.open(io.BytesIO(data))
    image.load()
    image = ImageOps.exif_transpose(image)
    width, height = image.size
    has_alpha = image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info)
    image = image.convert("RGBA" if has_alpha else "RGB")
    scale = min(1.0, max_edge / max(width, height))
    if scale < 1:
        image = image.resize((round(width * scale), round(height * scale)), Image.LANCZOS)
    suffix = output.suffix.lower()
    if keep_format or suffix == ".png":
        image.save(output, "PNG", optimize=True)
    elif suffix in (".jpg", ".jpeg"):
        image.convert("RGB").save(output, "JPEG", quality=quality, optimize=True, progressive=True)
    else:
        image.save(output, "WEBP", quality=quality, method=6)
    return {"converted": True, "source_size": [width, height], "saved_size": list(image.size), "alpha": has_alpha}


def update_manifest(path, entry):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    credits = manifest.setdefault("credits", [])
    credits[:] = [c for c in credits if c.get("file") != entry["file"]]
    credits.append(entry)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", nargs="?", help="Image URL (omit when using --candidates).")
    parser.add_argument("output", help="Destination file, normally media/<name>.webp next to the manifest.")
    parser.add_argument("--candidates", help="candidates.json written by find_images.py.")
    parser.add_argument("--pick", type=int, help="Index from the contact sheet.")
    parser.add_argument("--title")
    parser.add_argument("--creator")
    parser.add_argument("--license", dest="license_label")
    parser.add_argument("--page", help="Page where the image and its license are shown.")
    parser.add_argument("--note", help="Why this image is used or how it was changed, e.g. 'cropped'.")
    parser.add_argument("--manifest", help="Deck manifest to receive the credit entry.")
    parser.add_argument("--max-edge", type=int, default=2600)
    parser.add_argument("--quality", type=int, default=84)
    parser.add_argument("--keep-format", action="store_true", help="Keep PNG with transparency.")
    args = parser.parse_args()

    row = None
    if args.candidates:
        if args.pick is None:
            parser.error("--pick is required with --candidates.")
        if args.source and not args.output:
            parser.error("Give only the output path with --candidates.")
        rows = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
        row = next((r for r in rows if r.get("index") == args.pick), None)
        if not row:
            parser.error("No candidate with that index.")
        url = row["image_url"]
        meta = {"title": row.get("title"), "creator": row.get("creator"), "license": row.get("license_label"),
                "license_url": row.get("license_url"), "page": row.get("page"), "provider": row.get("provider")}
        if row.get("provider") == "unsplash":
            ping_unsplash(row.get("download_location"))
    else:
        if not args.source:
            parser.error("Give an image URL or --candidates with --pick.")
        url = args.source
        meta = {"title": args.title, "creator": args.creator, "license": args.license_label,
                "license_url": None, "page": args.page, "provider": None}
    for key, value in (("title", args.title), ("creator", args.creator), ("license", args.license_label), ("page", args.page)):
        if value:
            meta[key] = value

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = download(url)
    except (urllib.error.URLError, ValueError) as exc:
        # Some sites block direct downloads (for example a 403). Respect that: open the source
        # page and use the site's own download button, or choose another candidate.
        print(json.dumps({"saved": None, "error": str(exc), "source_page": meta.get("page"),
                          "advice": "The site refused or failed the download. Do not work around it; "
                                    "download from the source page yourself or pick another candidate."},
                         ensure_ascii=False, indent=2))
        sys.exit(3)
    result = convert(data, output, args.max_edge, args.quality, args.keep_format)
    listed = int((row or {}).get("width") or 0) if args.candidates else 0
    saved = (result.get("source_size") or [0])[0]
    if listed and saved and saved < listed * 0.6:
        result["warning"] = (f"The library listed {listed}px but served {saved}px (a preview). "
                             "Use it only for small placements, or download the original from the source page.")
    entry = {k: v for k, v in {
        "file": None,
        "title": meta.get("title"),
        "creator": meta.get("creator"),
        "license": meta.get("license"),
        "license_url": meta.get("license_url"),
        "source": meta.get("page") or url,
        "provider": meta.get("provider"),
        "note": args.note,
    }.items() if v}
    if args.manifest:
        manifest = Path(args.manifest).resolve()
        try:
            entry["file"] = str(output.resolve().relative_to(manifest.parent))
        except ValueError:
            parser.error("Save the image inside the manifest's project folder so the builder can embed it.")
        update_manifest(manifest, entry)
    else:
        entry["file"] = str(output)
    missing = [k for k in ("creator", "license", "source") if not entry.get(k)]
    print(json.dumps({"saved": str(output), "bytes": output.stat().st_size, **result, "credit": entry,
                      "missing_credit_fields": missing}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Stage an audience edition of a generated deck for a static host."""
from argparse import ArgumentParser
from pathlib import Path
import json
import re

from check_deck import audit


def replace_payload(document, identifier, modify):
    pattern = re.compile(r'(<script id="' + identifier + r'" type="application/json">)(.*?)(</script>)', flags=re.S)

    def patch(match):
        value = modify(json.loads(match[2]))
        safe_text = json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")
        return match[1] + safe_text + match[3]

    result, replacements = pattern.subn(patch, document)
    if replacements != 1:
        raise ValueError(f"Expected one embedded {identifier} block.")
    return result


def audience_model(source):
    slides = []
    for slide in source["slides"]:
        slides.append({key: slide[key] for key in ("title", "appendix") if key in slide})
    return {"title": source.get("title", "Presentation"), "slides": slides}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    report = audit(args.source)
    if report["status"] != "pass":
        parser.error("; ".join(report["errors"]))
    final_path = args.folder / "index.html"
    if final_path.resolve() == args.source.resolve() or final_path.exists():
        parser.error("Choose a new destination folder or a folder without an existing index.html.")
    copy = args.source.read_text(encoding="utf-8")
    copy = replace_payload(copy, "deck-manifest", audience_model)
    copy = replace_payload(copy, "deck-notes", lambda notes: [{} for _ in notes])
    copy = re.sub(r'<button id="(?:toggle-editor|save-edited)"[^>]*>.*?</button>', "", copy)
    copy = copy.replace(
        '<button id="toggle-notes" aria-pressed',
        '<button id="toggle-notes" hidden aria-pressed',
    )
    args.folder.mkdir(parents=True, exist_ok=True)
    final_path.write_text(copy, encoding="utf-8")
    print(final_path)


if __name__ == "__main__":
    main()

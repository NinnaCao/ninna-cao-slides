#!/usr/bin/env python3
"""Build comparison previews from the actual opening slide in a deck manifest."""
from argparse import ArgumentParser
from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile
import json

from build_deck import build
from theme_catalog import styles


def previews(manifest, output, selection):
    model = json.loads(manifest.read_text(encoding="utf-8"))
    if not model.get("slides"):
        raise ValueError("Provide at least one genuine opening slide.")
    output.mkdir(parents=True, exist_ok=True)
    for i, direction in enumerate(selection, 1):
        draft = deepcopy(model)
        draft["editable"] = False
        draft["credits_slide"] = False
        opening = draft["slides"][0]
        opening.pop("id", None)
        opening.pop("notes_en", None)
        opening.pop("notes_zh", None)
        opening["appendix"] = False
        draft["slides"] = [opening]
        original_style = draft.get("style") or {}
        if direction.endswith(".json"):
            # A theme made by make_theme.py for this topic (it must sit inside the deck project).
            theme = Path(direction).resolve()
            draft["style"] = {"preset": "adaptive", "theme": str(theme.relative_to(manifest.parent.resolve())),
                              "fonts": original_style.get("fonts", [])}
        elif direction != "custom":
            draft["style"] = {"preset": direction, "fonts": original_style.get("fonts", [])}
            if original_style.get("accent"):
                draft["style"]["accent"] = original_style["accent"]
        with NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".json", dir=manifest.parent) as payload:
            json.dump(draft, payload, ensure_ascii=False)
            payload.flush()
            yield build(payload.name, output / f"option-{i:02d}.html")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    choices = tuple(styles()) + ("cinematic", "editorial", "light", "custom")
    parser.add_argument("directions", nargs="+",
                        help="Three of: theme.json files from make_theme.py (preferred: made from this topic), "
                             "cinematic, editorial, light, custom, or a catalog ID.")
    args = parser.parse_args()
    for direction in args.directions:
        if not direction.endswith(".json") and direction not in choices:
            parser.error(f"Unknown direction {direction!r}. Use a theme.json or one of: {', '.join(choices)}")
    if len(args.directions) != 3 or len(set(args.directions)) != 3:
        parser.error("Choose three distinct directions.")
    for report in previews(args.manifest.resolve(), args.output.resolve(), args.directions):
        print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()

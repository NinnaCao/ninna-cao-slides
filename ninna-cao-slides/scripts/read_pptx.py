#!/usr/bin/env python3
"""Extract an editable source inventory from a local PowerPoint presentation."""
from argparse import ArgumentParser
from pathlib import Path
import hashlib
import json

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


def save_picture(image, output):
    digest = hashlib.sha256(image.blob).hexdigest()[:16]
    image_path = output / f"{digest}.{image.ext}"
    image_path.write_bytes(image.blob)
    return "media/" + image_path.name


def shape_records(shapes, media):
    records = []
    for shape in shapes:
        record = {
            "name": shape.name,
            "shape_type": str(shape.shape_type),
            "position_emu": {key: int(getattr(shape, key)) for key in ("left", "top", "width", "height")},
        }
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            record["children"] = shape_records(shape.shapes, media)
        if shape.has_text_frame:
            text = shape.text_frame.text
            if text.strip():
                record["text"] = text
        if shape.has_table:
            record["table"] = [[cell.text for cell in row.cells] for row in shape.table.rows]
        if shape.has_chart:
            chart = shape.chart
            record["chart"] = {"type": str(chart.chart_type)}
            if chart.has_title and chart.chart_title.has_text_frame:
                record["chart"]["title"] = chart.chart_title.text_frame.text
            record["chart"]["series"] = [
                {"name": series.name, "values": list(series.values)} for series in chart.series
            ]
        if shape.shape_type in (MSO_SHAPE_TYPE.PICTURE, MSO_SHAPE_TYPE.PLACEHOLDER):
            try:
                image = shape.image
            except (AttributeError, ValueError):
                pass
            else:
                record["image"] = save_picture(image, media)
                record["crop"] = {
                    edge: getattr(shape, "crop_" + edge)
                    for edge in ("left", "right", "top", "bottom")
                }
        records.append(record)
    return records


def extract(source, destination):
    deck = Presentation(str(source))
    destination.mkdir(parents=True, exist_ok=True)
    media = destination / "media"
    media.mkdir(exist_ok=True)
    result = {
        "source_file": source.name,
        "size_emu": {"width": int(deck.slide_width), "height": int(deck.slide_height)},
        "slides": [],
    }
    for i, slide in enumerate(deck.slides, 1):
        notes = slide.notes_slide.notes_text_frame if slide.has_notes_slide else None
        title = slide.shapes.title
        result["slides"].append({
            "number": i,
            "title": title.text if title is not None else "",
            "hidden": slide._element.get("show", "1") == "0",
            "notes": notes.text if notes is not None else "",
            "shapes": shape_records(slide.shapes, media),
        })
    report = destination / "pptx-source.json"
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.source.suffix.lower() != ".pptx":
        parser.error("Supply a modern .pptx file. Convert legacy .ppt files with a presentation application.")
    print(extract(args.source, args.destination))


if __name__ == "__main__":
    main()

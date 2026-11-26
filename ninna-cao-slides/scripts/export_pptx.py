#!/usr/bin/env python3
"""Export a visual-match PowerPoint from the final PDF, optionally with notes."""
from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path
import json

import fitz
from pptx import Presentation
from pptx.util import Inches


def make_powerpoint(pdf, output, model=None):
    presentation = Presentation()
    presentation.slide_width = Inches(13.333333)
    presentation.slide_height = Inches(7.5)
    notes = [] if model is None else model["slides"]
    with fitz.open(pdf) as source:
        if not len(source):
            raise ValueError("The source PDF has no pages.")
        if model is not None and len(source) != len(notes):
            raise ValueError("Notes manifest needs one entry per slide in the PDF.")
        for index, page in enumerate(source):
            if abs(page.rect.width / page.rect.height - 16 / 9) > 0.004:
                raise ValueError(f"Page {index + 1} is outside the 16:9 aspect ratio.")
            scale = 1920 / page.rect.width
            raster = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            slide = presentation.slides.add_slide(presentation.slide_layouts[6])
            pic = slide.shapes.add_picture(
                BytesIO(raster.tobytes("png")), 0, 0,
                width=presentation.slide_width, height=presentation.slide_height,
            )
            info = notes[index] if notes else {}
            if info.get("title"):
                pic._element.nvPicPr.cNvPr.set("descr", str(info["title"]))
            text = "\n\n".join(str(info[key]) for key in ("notes_en", "notes_zh") if info.get(key))
            if text:
                slide.notes_slide.notes_text_frame.text = text
    output.parent.mkdir(parents=True, exist_ok=True)
    presentation.save(output)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--notes", type=Path, help="Matching deck manifest JSON with bilingual speaking notes.")
    args = parser.parse_args()
    model = json.loads(args.notes.read_text(encoding="utf-8")) if args.notes else None
    make_powerpoint(args.pdf, args.output, model)
    print(args.output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render every slide in a real browser, save screenshots and flag layout problems.

  python3 scripts/qa_render.py presentation.html qa/            # uses installed Chrome
  python3 scripts/qa_render.py presentation.html qa/ --chromium /path/to/chromium

Checks each slide in its settled state:
  errors    text blocks that overlap each other, text leaving the 1920 × 1080 stage,
            clipped text boxes, images that failed to load, and main slides with no
            visible picture, diagram or video, or no real image such as a photo,
            render or screenshot (the "every slide has an image" rule).
  warnings  images shown larger than their pixels (soft on a projector), text under
            16 px, and visuals that cover less than 4% of the slide.
Writes qa/slide-NN.png, qa/contact-sheet.jpg (with Pillow) and qa/report.json. This is
evidence for a human look, not a replacement for one: open the contact sheet.
Needs: pip install playwright (and Chrome installed, or a Chromium path).
"""
from argparse import ArgumentParser
from pathlib import Path
import json
import sys

PROBE = r"""
(index) => {
  const slide = document.querySelectorAll('.slide')[index];
  const stage = {w: 1920, h: 1080};
  const root = document.getElementById('deck-stage') || slide.parentElement;
  const origin = root.getBoundingClientRect();
  const scale = origin.width / 1920 || 1;
  const box = (el) => {
    const r = el.getBoundingClientRect();
    return {x: (r.left - origin.left) / scale, y: (r.top - origin.top) / scale,
            w: r.width / scale, h: r.height / scale};
  };
  const visible = (el) => {
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || Number(cs.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1;
  };
  const label = (el) => (el.className && typeof el.className === 'string' ? el.tagName.toLowerCase() + '.' + el.className.trim().split(/\s+/).join('.') : el.tagName.toLowerCase())
    + ' “' + (el.innerText || el.getAttribute('aria-label') || el.alt || '').trim().slice(0, 48) + '”';
  // Text blocks: elements that own a non-empty text node.
  const texts = [];
  slide.querySelectorAll('*').forEach(el => {
    if (el.closest('svg') && el.tagName.toLowerCase() !== 'text') return;
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (own && visible(el)) texts.push(el);
  });
  const errors = [], warnings = [];
  const textBoxes = texts.map(el => {
    // Measure the text itself, not the full block width.
    // Inset each line fragment to its line box: tight display type (line-height < 1)
    // reports font boxes taller than the visible lines and would look "overlapped".
    const range = document.createRange(); range.selectNodeContents(el);
    const cs = getComputedStyle(el);
    const lh = cs.lineHeight === 'normal' ? parseFloat(cs.fontSize) * 1.2 : parseFloat(cs.lineHeight);
    const rects = [...range.getClientRects()].filter(r => r.width > 0 && r.height > 0).map(r => {
      const inset = Math.max(0, (r.height - lh * scale) / 2);
      return {left: r.left, right: r.right, top: r.top + inset, bottom: r.bottom - inset};
    });
    const r = rects.length ? rects.reduce((a, b) => ({
      left: Math.min(a.left, b.left), top: Math.min(a.top, b.top),
      right: Math.max(a.right, b.right), bottom: Math.max(a.bottom, b.bottom)}))
      : el.getBoundingClientRect();
    return {el, x: (r.left - origin.left) / scale, y: (r.top - origin.top) / scale,
            w: (r.right - r.left) / scale, h: (r.bottom - r.top) / scale};
  });
  for (let i = 0; i < textBoxes.length; i++) {
    const a = textBoxes[i];
    if (a.x < -2 || a.y < -2 || a.x + a.w > stage.w + 2 || a.y + a.h > stage.h + 2)
      errors.push('Text leaves the stage: ' + label(a.el));
    const size = parseFloat(getComputedStyle(a.el).fontSize);
    if (size < 16 && !a.el.closest('.slide-footer')) warnings.push(`Text at ${size}px: ` + label(a.el));
    for (let j = i + 1; j < textBoxes.length; j++) {
      const b = textBoxes[j];
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      const ix = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
      const iy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
      if (ix > 4 && iy > 6) errors.push('Overlapping text: ' + label(a.el) + ' × ' + label(b.el));
    }
  }
  slide.querySelectorAll('*').forEach(el => {
    if (!visible(el) || el.closest('svg')) return;
    const cs = getComputedStyle(el);
    if (/(hidden|clip)/.test(cs.overflow + cs.overflowY) && el.innerText && el.innerText.trim()
        && el.scrollHeight > el.clientHeight + 3 && !el.matches('.slide, .backdrop, .fade-plate, figure, .frame'))
      errors.push('Clipped text box: ' + label(el));
  });
  // Visuals: pictures, diagrams, video, canvas.
  let area = 0;
  const visuals = [...slide.querySelectorAll('img, svg, video, canvas, picture')].filter(el => {
    if (el.tagName.toLowerCase() === 'svg' && el.parentElement.closest('svg')) return false;
    return visible(el);
  });
  for (const el of visuals) {
    const b = box(el);
    const w = Math.max(0, Math.min(b.x + b.w, 1920) - Math.max(b.x, 0));
    const h = Math.max(0, Math.min(b.y + b.h, 1080) - Math.max(b.y, 0));
    area += w * h;
    if (el.tagName.toLowerCase() === 'img') {
      if (!el.complete || !el.naturalWidth) errors.push('Image failed to load: ' + label(el));
      else if (!/^data:image\/svg|\.svg($|\?)/i.test(el.currentSrc || el.src)) {  // vectors scale cleanly
        const fit = getComputedStyle(el).objectFit;
        const needW = fit === 'cover' ? Math.max(b.w, b.h * el.naturalWidth / el.naturalHeight) : b.w;
        if (needW > el.naturalWidth * 1.25)
          warnings.push(`Image shown at ${Math.round(needW)}px from ${el.naturalWidth}px: ` + label(el));
      }
    }
  }
  const coverage = area / (1920 * 1080);
  const exempt = slide.dataset.visualExempt;
  const appendix = slide.dataset.appendix === 'true';
  const photos = visuals.filter(el => el.tagName.toLowerCase() === 'video' ||
    (el.tagName.toLowerCase() === 'img' && !/^data:image\/svg|\.svg($|\?)/i.test(el.currentSrc || el.src))).length;
  if (!visuals.length && !exempt) (appendix ? warnings : errors).push('No visible picture, diagram or video on this slide.');
  else if (!photos && !exempt) (appendix ? warnings : errors).push('No real image (photo, render or screenshot). Add one, or use backdrop place "ambient" behind the content.');
  else if (coverage < 0.04 && !exempt) warnings.push(`Visuals cover only ${(coverage * 100).toFixed(1)}% of the slide.`);
  return {title: slide.dataset.title, appendix, visuals: visuals.length, photos,
          coverage: Math.round(coverage * 1000) / 10, errors: [...new Set(errors)], warnings: [...new Set(warnings)]};
}
"""


def contact_sheet(paths, target):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return False
    cols, w, h = 4, 480, 270
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * (h + 26)), "#111")
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(paths):
        image = Image.open(path).convert("RGB").resize((w, h))
        x, y = (i % cols) * w, (i // cols) * (h + 26)
        sheet.paste(image, (x, y))
        draw.text((x + 8, y + h + 6), f"{i + 1:02d}", fill="#eee")
    sheet.save(target, quality=84)
    return True


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--chromium", help="Chromium executable; default is the installed Chrome.")
    parser.add_argument("--settle", type=int, default=2400, help="Milliseconds to wait for entrances.")
    args = parser.parse_args()
    from playwright.sync_api import sync_playwright

    args.out.mkdir(parents=True, exist_ok=True)
    report, shots = [], []
    with sync_playwright() as p:
        options = {"executable_path": args.chromium} if args.chromium else {"channel": "chrome"}
        browser = p.chromium.launch(**options)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        problems = []
        page.on("pageerror", lambda exc: problems.append(str(exc)))
        page.goto(args.html.resolve().as_uri())
        page.evaluate("document.fonts.ready")
        page.add_style_tag(content=".deck-controls{display:none!important}")
        count = page.evaluate("document.querySelectorAll('.slide').length")
        for index in range(count):
            page.evaluate("i => { const d = window.slideDeck || window.ninnaDeck; return d ? d.goTo(i) : null; }", index)
            page.wait_for_timeout(args.settle)
            shot = args.out / f"slide-{index + 1:02d}.png"
            page.screenshot(path=str(shot))
            shots.append(shot)
            result = page.evaluate(PROBE, index)
            result["slide"] = index + 1
            report.append(result)
        browser.close()
    sheet = args.out / "contact-sheet.jpg"
    made = contact_sheet(shots, sheet)
    errors = sum(len(r["errors"]) for r in report) + len(problems)
    summary = {
        "status": "pass" if not errors else "fail",
        "slides": len(report),
        "errors": errors,
        "warnings": sum(len(r["warnings"]) for r in report),
        "script_errors": problems,
        "contact_sheet": str(sheet) if made else None,
        "issues": [r for r in report if r["errors"] or r["warnings"]],
        "claim_boundary": "Geometry checks only. Look at the contact sheet for crops, focal points, contrast and fades.",
    }
    (args.out / "report.json").write_text(json.dumps({"summary": summary, "slides": report}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()

# Use in Claude

## Claude Code

Put the `visual-slides` folder in `~/.claude/skills/` (all projects) or a project's `.claude/skills/`. Keep the whole folder, including `assets`, `references` and `scripts`. Claude Code loads it the next session; ask for "Visual Slides" or describe a presentation.

Optional tools for the scripts:

```bash
pip install pillow playwright fonttools brotli
```

- Pillow: contact sheets and WebP conversion for web images.
- Playwright: `qa_render.py` and PDF export (uses the installed Chrome; no browser download needed).
- fontTools and brotli: subsetting large fonts such as Chinese ones.

The builder, `check_deck.py`, `find_images.py` and `fetch_image.py` run on the Python 3.10+ standard library.

## Claude apps (claude.ai, desktop)

Upload the ZIP that contains the single `visual-slides` folder as a custom skill, then enable it:

1. Enable code execution and file creation in the capabilities settings if needed.
2. Open **Customize > Skills**.
3. Choose **+ > Create skill > Upload a skill**, select the ZIP and enable it.

Labels may change; see https://support.claude.com/en/articles/12512180-use-skills-in-claude and https://code.claude.com/docs/en/skills .

Web image search needs network access in the environment. Where it is not available, Claude can still use the user's images, draw diagrams and leave clearly marked picture slots.

## Starting a deck

> Use Visual Slides for this presentation. Put a meaningful visual on every slide and find openly licensed images when my material runs out. Fade photos into the background. Choose the visual direction from the audience, topic and room. Deliver HTML and PDF with matching notes.

Attach the actual reading, images and meeting notes for each project.

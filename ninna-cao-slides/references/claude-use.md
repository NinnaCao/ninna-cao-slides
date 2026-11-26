# Use in Claude

Upload the ZIP containing the single `ninna-cao-slides` folder as a custom skill, then enable it. The folder contains `SKILL.md`, references, assets and optional scripts. It is standalone; Zara Zhang's skill is not a separate installation requirement.

According to Claude's help documentation checked on 23 November 2026:

1. Enable code execution and file creation in the account's capabilities settings if needed.
2. Open **Customize > Skills**.
3. Choose **+ > Create skill > Upload a skill**.
4. Upload `Ninna_Cao_Slides_Claude.zip` and enable the skill.

The UI may change. Use the current official help page if labels differ:

- https://support.claude.com/en/articles/12512180-use-skills-in-claude
- https://support.claude.com/en/articles/12512198-how-to-create-custom-skills

Start a task with:

> Use Ninna Cao Slides for this presentation. Choose the visual direction from the audience, topic, brand and delivery setting. Preserve any approved sections. Use the supplied process photos and clear diagrams where they help explain the work. Keep enough context for the audience and make the entrances automatic. Deliver the requested formats with matching content and notes.

Attach the actual deck, reading, images and any relevant meeting notes for each new project. This package contains reusable design instructions and neutral examples, not the prior SteelSeries research files or interview photographs.

For Claude Code, place the `ninna-cao-slides` folder in the project's `.claude/skills/` directory or the user's `~/.claude/skills/` directory, following the environment's current skills instructions. Keep the complete folder, including assets and references.

Claude Code documentation: https://code.claude.com/docs/en/skills

Use the built-in presentation and document tools alongside this skill for native PPTX, PDF and DOCX output. The HTML builder uses Python 3's standard library; the optional DOCX helper also needs `python-docx`.

# Notes and engagement

## Match what is on screen

Write notes against the final slide numbers and visible material. Start with the slide's idea, explain how the visual demonstrates it, then give a natural transition. Do not make the speaker memorize a feature walkthrough when the audience needs to understand a framework.

Use simple spoken English, short connected sentences and familiar verbs. Expand acronyms at first use or use the plain expression. Include only the context needed to understand the example. Avoid introducing an unexplained statistic or changing products so often that the audience loses the thread.

When a physical object is used, give the speaker a short private cue to hold it up or let people examine it. Use the object to explain a broader experience when that is the purpose of the talk. A question such as "What would make this worth it to a player?" can connect a price to user value without pretending that the price proves a successful process.

## Multiple speakers and timing

- Use the speaker split supplied by the user. Store the actual owner on every main slide.
- Keep each person's script in a separate document when requested, with English and private Chinese support together within that person's file.
- Plan spoken time and pauses together. Estimate around 95–125 spoken English words per minute initially, then adjust for the speaker's pace, comfort and expected interaction.
- Reserve time for a physical prop, transitions and audience responses. Do not fill a 15-minute allowance with 15 minutes of continuous text and add pauses afterward.
- Treat a one-page sheet as a compact speaking aid. Do not claim a particular duration from word count alone. If a one-page full script would become unreadable, ask for or offer a concise cue sheet or a two-page script rather than silently shrinking the font.

## One-page reference layout

Use a readable body around 11 pt, black text and short paragraphs. Put the slide number, topic and a short Chinese memory cue on one pale-colored heading line. Use distinct colors for quick page lookup. Keep a stable palette so the speaker learns where to look.

Use bold and a light yellow highlight on the phrases the speaker needs to recover at a glance. Highlight the conceptual point, the important action and a crucial audience question. Do not highlight most of the text.

Use Chinese as private understanding or memory support when requested. Do not automatically translate every English paragraph or double the document length. Do not add production notes, revision history or long introductory instructions to a speaking sheet.

The optional helper builds this kind of DOCX from the same deck manifest:

```bash
python3 scripts/build_notes.py deck.json speaking-notes.docx --speaker "Ninna Cao"
```

It requires `python-docx`. Use the environment's document renderer to check the final page count, highlighting, Chinese glyphs and spacing. The helper creates a document; it does not prove that it is one page or that the timing fits.

## Engagement that teaches

Use a few deliberate moments: show a real object, ask which prototype would answer a question, invite the audience to interpret an observation, or return to the opening question at the end. These moments should reinforce the concept.

Make most on-screen motion automatic. Leave the speaker in control of the pause and the slide advance. Do not make a teaching question depend on several tiny controls or reveal a quiz answer immediately if the speaker needs time for responses.

Add a giveaway only when requested. Announce it briefly and connect the ending to the learning point. Avoid inventing eligibility or prize-selection rules on the user's behalf.

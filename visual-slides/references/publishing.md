# Stage a deck for sharing

When requested, use the host and audience access agreed with the user. For example, an available approved static host can supply a presentation URL. Begin with a preview or restricted link when the task calls for it. Publish to production only if the request authorizes that destination.

1. Confirm that the final approved deck is the version to share. Prepare an audience copy of the offline HTML. Remove notes and backstage fields that are meant to stay with the speaker, or share the notes document only with the intended recipients.
2. Put the HTML at the host's entry point. When a source project has separate files, include each required image, video, font and stylesheet with the correct relative paths. A single self-contained HTML is easiest to move between hosts.
3. Use the available site tool or the host's normal authenticated controls. Inspect the returned link in the intended audience view. Verify media, fonts, keyboard navigation, touch and the current revision. Report a link after observing it work.
4. Treat the deck, speaking notes and source files as different deliverables. Confirm the intended access before changing what a previously shared link exposes.

When supplied, the local staging helper creates an audience folder with `index.html` from a generated deck. It prepares the file on the local machine. Use the hosting workflow above to share it.

For an authorized Vercel publish, the [original deployment helper](frontend-slides/scripts/deploy.sh) is included. Use the approved audience copy and an authenticated hosting path, then verify the returned URL in the intended audience view.

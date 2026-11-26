/* Edit text locally, retain a browser draft, and download a separate HTML copy. */
(() => {
  "use strict";
  function draftKey(path, manifest) {
    let hash = 2166136261;
    for (let i = 0; i < manifest.length; i++) {
      hash = Math.imul(hash ^ manifest.charCodeAt(i), 16777619);
    }
    return "visual-slides:draft:" + path + ":" + (hash >>> 0).toString(16);
  }

  function createDraftStore(key, getStorage) {
    return {
      read() {
        try {
          const entries = JSON.parse(getStorage().getItem(key) || "[]");
          return new Map(Array.isArray(entries)
            ? entries.filter(row => Array.isArray(row) && row.length === 2
              && row.every(value => typeof value === "string"))
            : []);
        } catch (_) {
          return new Map();
        }
      },
      write(entries) {
        try {
          if (entries.size) getStorage().setItem(key, JSON.stringify([...entries]));
          else getStorage().removeItem(key);
        } catch (_) {
          // Download remains available when browser storage is blocked or full.
        }
      },
    };
  }

  if (typeof module === "object" && module.exports) module.exports = {draftKey, createDraftStore};
  if (typeof document === "undefined") return;

  const stage = document.getElementById("deck-stage");
  const toggle = document.getElementById("toggle-editor");
  const save = document.getElementById("save-edited");
  if (!stage || !toggle || !save) return;
  const selector = ".slide-title, .slide-subtitle, .slide-body p, .slide-body li, .slide-body h3, figcaption";
  const manifest = document.getElementById("deck-manifest").textContent;
  const store = createDraftStore(draftKey(location.pathname, manifest), () => window.localStorage);
  const draft = store.read();
  const fields = new Map();
  let editing = false;
  let changed = false;

  function updateTitle(slide, node, number) {
    if (!node.classList.contains("slide-title")) return;
    const title = node.textContent.trim();
    if (!title) return;
    slide.dataset.title = title;
    slide.setAttribute("aria-label", "Slide " + number + ". " + title);
  }

  stage.querySelectorAll(".slide").forEach((slide, number) => {
    [...slide.querySelectorAll(selector)]
      .filter(node => !node.querySelector("a, button, img, svg, p, li, [contenteditable]"))
      .forEach((node, index) => {
        const key = slide.id + ":" + index;
        fields.set(node, {key, initial: node.textContent, slide, number: number + 1});
        if (draft.has(key)) {
          node.textContent = draft.get(key);
          updateTitle(slide, node, number + 1);
          changed = true;
        }
      });
  });
  save.hidden = !changed;

  function refreshTargets() {
    stage.querySelectorAll("[contenteditable]").forEach(node => node.removeAttribute("contenteditable"));
    if (!editing) return;
    for (const [node, info] of fields) {
      if (info.slide.getAttribute("aria-hidden") === "false") {
        node.setAttribute("contenteditable", "plaintext-only");
      }
    }
  }

  function setEditing(value) {
    const deck = (window.slideDeck || window.ninnaDeck);
    if (!deck) return;
    editing = value;
    if (editing) deck.playback.pause();
    document.body.classList.toggle("deck-editing", editing);
    toggle.setAttribute("aria-pressed", String(editing));
    toggle.textContent = editing ? "Done editing" : "Edit text";
    save.hidden = !(editing || changed);
    refreshTargets();
  }

  function download() {
    const tree = document.documentElement.cloneNode(true);
    tree.classList.remove("js");
    tree.querySelector("body").classList.remove("deck-editing", "controls-hidden");
    tree.querySelector("#deck-stage").removeAttribute("style");
    const manifest = tree.querySelector("#deck-manifest");
    const model = JSON.parse(manifest.textContent);
    tree.querySelectorAll("[contenteditable]").forEach(node => node.removeAttribute("contenteditable"));
    tree.querySelectorAll(".slide").forEach((slide, i) => {
      slide.classList.toggle("active", i === 0);
      slide.classList.toggle("visible", i === 0);
      slide.classList.remove("entered");
      slide.setAttribute("aria-hidden", String(i !== 0));
      slide.toggleAttribute("inert", i !== 0);
      const titleNode = slide.querySelector(".slide-title");
      const subtitleNode = slide.querySelector(".slide-subtitle");
      const body = slide.querySelector(".slide-body");
      if (titleNode.textContent.trim()) {
        model.slides[i].title = titleNode.textContent.trim();
        slide.dataset.title = model.slides[i].title;
        slide.setAttribute("aria-label", "Slide " + (i + 1) + ". " + model.slides[i].title);
      }
      model.slides[i].title_html = titleNode.innerHTML;
      if (subtitleNode) model.slides[i].subtitle = subtitleNode.textContent;
      model.slides[i].body_html = body.innerHTML;
    });
    manifest.textContent = JSON.stringify(model).replace(/</g, "\\u003c");
    tree.querySelector("#speaker-notes").hidden = true;
    const editor = tree.querySelector("#toggle-editor");
    editor.textContent = "Edit text";
    editor.setAttribute("aria-pressed", "false");
    tree.querySelector("#save-edited").hidden = true;
    tree.querySelector("#toggle-autoplay").textContent = "Autoplay";
    tree.querySelector("#toggle-autoplay").setAttribute("aria-pressed", "false");
    tree.querySelector("#toggle-notes").setAttribute("aria-pressed", "false");
    const blob = new Blob(["<!doctype html>\n", tree.outerHTML], {type: "text/html;charset=utf-8"});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = (document.title.replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-|-$/g, "") || "presentation") + "-edited.html";
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  stage.addEventListener("slidechange", refreshTargets);
  stage.addEventListener("input", event => {
    const node = event.target;
    const field = fields.get(node);
    if (!field || !node.isContentEditable) return;
    const text = node.textContent;
    if (text === field.initial) draft.delete(field.key);
    else draft.set(field.key, text);
    store.write(draft);
    updateTitle(field.slide, node, field.number);
    changed = true;
    save.hidden = false;
  });
  toggle.addEventListener("click", () => setEditing(!editing));
  save.addEventListener("click", download);
  document.addEventListener("keydown", event => {
    const key = event.key.toLowerCase();
    if ((event.ctrlKey || event.metaKey) && key === "s" && (editing || changed)) {
      event.preventDefault();
      download();
    } else if (key === "e" && !event.ctrlKey && !event.metaKey && !event.altKey
        && !event.target?.isContentEditable && !/^(INPUT|TEXTAREA|SELECT)$/.test(event.target?.tagName)
        && document.getElementById("speaker-notes").hidden) {
      event.preventDefault();
      setEditing(!editing);
    }
  });
})();

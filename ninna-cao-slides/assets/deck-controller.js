/* Standalone Ninna Cao Slides controller. No network or library dependency. */
(() => {
  'use strict';
  class NinnaPlayback {
    constructor(durations, mainCount, hooks = {}) {
      this.durations = durations.map(n => Math.max(1, Number(n) || 45) * 1000);
      this.mainCount = mainCount;
      this.index = 0;
      this.playing = false;
      this.remaining = this.durations[0];
      this.timer = null;
      this.now = hooks.now || (() => performance.now());
      this.setTimer = hooks.setTimer || ((fn, ms) => setTimeout(fn, ms));
      this.clearTimer = hooks.clearTimer || (id => clearTimeout(id));
      this.onAdvance = hooks.onAdvance || (() => {});
      this.onState = hooks.onState || (() => {});
    }
    cancel() { if (this.timer !== null) this.clearTimer(this.timer); this.timer = null; }
    arm() {
      this.cancel();
      this.due = this.now() + this.remaining;
      this.timer = this.setTimer(() => {
        this.timer = null;
        if (!this.playing) return;
        if (this.index >= this.mainCount - 1) {
          this.playing = false; this.remaining = 0; this.onState(); return;
        }
        this.index += 1;
        this.remaining = this.durations[this.index];
        this.onAdvance(this.index);
        if (this.playing) this.arm();
        this.onState();
      }, this.remaining);
    }
    play() {
      if (this.index >= this.mainCount) return false;
      if (this.playing) return true;
      if (!(this.remaining > 0)) this.remaining = this.durations[this.index];
      this.playing = true; this.arm(); this.onState(); return true;
    }
    pause() {
      if (this.playing) this.remaining = Math.max(0, this.due - this.now());
      this.cancel(); this.playing = false; this.onState();
    }
    seek(index) {
      if (!Number.isInteger(index) || index < 0 || index >= this.durations.length) return;
      this.cancel(); this.index = index; this.remaining = this.durations[index];
      if (index >= this.mainCount) this.playing = false;
      if (this.playing) this.arm();
      this.onState();
    }
  }
  if (typeof module === 'object' && module.exports) module.exports = { NinnaPlayback };
  if (typeof window === 'undefined' || typeof document === 'undefined') return;
  window.NinnaPlayback = NinnaPlayback;
  function start() {
    const slides = [...document.querySelectorAll('.slide')];
    const stage = document.getElementById('deck-stage');
    if (!slides.length || !stage) return;
    document.documentElement.classList.add('js');
    const notes = JSON.parse(document.getElementById('deck-notes').textContent);
    const mainCount = slides.filter(s => s.dataset.appendix !== 'true').length;
    const previous = document.getElementById('previous-slide');
    const next = document.getElementById('next-slide');
    const autoplay = document.getElementById('toggle-autoplay');
    const noteButton = document.getElementById('toggle-notes');
    const notePanel = document.getElementById('speaker-notes');
    const closeNotes = document.getElementById('close-notes');
    let index = 0;
    let idleTimer = null;
    let touchX = null;
    let touchY = null;
    const playback = new NinnaPlayback(slides.map(s => Number(s.dataset.durationSeconds)), mainCount, {
      onAdvance: n => activate(n, true), onState: () => updateControls()
    });
    function scale() {
      const factor = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
      const x = (window.innerWidth - 1920 * factor) / 2;
      const y = (window.innerHeight - 1080 * factor) / 2;
      stage.style.transform = `translate(${x}px,${y}px) scale(${factor})`;
    }
    function updateControls() {
      previous.disabled = index === 0;
      next.disabled = index === slides.length - 1;
      const label = index < mainCount ? `${index + 1} / ${mainCount}` : `Appendix ${index - mainCount + 1}`;
      document.getElementById('slide-counter').textContent = label;
      autoplay.textContent = playback.playing ? 'Pause' : 'Autoplay';
      autoplay.setAttribute('aria-pressed', String(playback.playing));
      autoplay.disabled = index >= mainCount;
    }
    function refreshNotes() {
      const current = notes[index] || {};
      document.getElementById('notes-title').textContent = `${index + 1}  ${slides[index].dataset.title || ''}`;
      document.getElementById('notes-english').textContent = current.en || '';
      document.getElementById('notes-chinese').textContent = current.zh || '';
    }
    function activate(n, fromClock = false) {
      n = Math.max(0, Math.min(slides.length - 1, n));
      slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === n);
        slide.classList.toggle('visible', i === n);
        slide.classList.remove('entered');
        slide.setAttribute('aria-hidden', String(i !== n));
        slide.inert = i !== n;
      });
      index = n;
      // Restart automatic entrances on deliberate revisits without per-point clicks.
      void slides[n].offsetWidth;
      slides[n].classList.add('entered');
      if (!fromClock) playback.seek(n);
      refreshNotes(); updateControls();
      try { history.replaceState(null, '', `#slide-${n + 1}`); } catch (_) {}
    }
    function showControls() {
      document.body.classList.remove('controls-hidden');
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => document.body.classList.add('controls-hidden'), 2400);
    }
    function toggleNotes(force) {
      const opening = force === undefined ? notePanel.hidden : force;
      if (opening) playback.pause();
      notePanel.hidden = !opening;
      noteButton.setAttribute('aria-pressed', String(opening));
      if (opening) { refreshNotes(); closeNotes.focus(); }
      else noteButton.focus();
      showControls();
    }
    function togglePlayback() {
      if (playback.playing) playback.pause();
      else { if (index === mainCount - 1 && playback.remaining === 0) activate(0); playback.play(); }
      showControls();
    }
    async function fullscreen() {
      try {
        if (document.fullscreenElement) await document.exitFullscreen();
        else await document.documentElement.requestFullscreen();
      } catch (_) { /* Fullscreen may be unavailable in an embedded preview. */ }
    }
    previous.addEventListener('click', () => activate(index - 1));
    next.addEventListener('click', () => activate(index + 1));
    autoplay.addEventListener('click', togglePlayback);
    noteButton.addEventListener('click', () => toggleNotes());
    closeNotes.addEventListener('click', () => toggleNotes(false));
    document.getElementById('toggle-fullscreen').addEventListener('click', fullscreen);
    document.addEventListener('keydown', event => {
      const target = event.target;
      if (target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))) return;
      if (event.key === 'Escape' && !notePanel.hidden) { toggleNotes(false); return; }
      if (event.key === 'Tab' && !notePanel.hidden) { event.preventDefault(); closeNotes.focus(); return; }
      if (!notePanel.hidden) return;
      if (['ArrowRight','PageDown',' '].includes(event.key)) { event.preventDefault(); activate(index + 1); }
      else if (['ArrowLeft','PageUp'].includes(event.key)) { event.preventDefault(); activate(index - 1); }
      else if (event.key === 'Home') { event.preventDefault(); activate(0); }
      else if (event.key === 'End') { event.preventDefault(); activate(mainCount - 1); }
      else if (event.key.toLowerCase() === 'p') togglePlayback();
      else if (event.key.toLowerCase() === 'n') toggleNotes();
      else if (event.key.toLowerCase() === 'q' && mainCount < slides.length) activate(mainCount);
      else if (event.key.toLowerCase() === 'f') fullscreen();
      showControls();
    });
    stage.addEventListener('touchstart', e => { touchX = e.changedTouches[0].clientX; touchY = e.changedTouches[0].clientY; }, {passive:true});
    stage.addEventListener('touchend', e => {
      if (touchX === null) return;
      const dx = e.changedTouches[0].clientX - touchX;
      const dy = e.changedTouches[0].clientY - touchY;
      if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) activate(index + (dx < 0 ? 1 : -1));
      touchX = touchY = null;
    }, {passive:true});
    document.addEventListener('visibilitychange', () => { if (document.hidden) playback.pause(); });
    document.addEventListener('pointermove', showControls, {passive:true});
    document.addEventListener('focusin', showControls);
    window.addEventListener('resize', scale);
    const initial = Number((location.hash.match(/^#slide-(\d+)$/) || [])[1]) - 1;
    scale(); activate(Number.isInteger(initial) && initial >= 0 ? initial : 0); showControls();
    window.ninnaDeck = {goTo: n => activate(n), playback, mainCount, get index() {return index;}};
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();

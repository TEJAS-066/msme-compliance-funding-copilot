/* MSME Copilot shell: guided tour (speech-bubble coach marks) + theme switch + info menu.
 * Runs inside a zero-height Streamlit component iframe and draws into the PARENT page (same origin).
 * Design rules: (1) every load rebuilds the UI from persisted state, so Streamlit reruns/iframe re-creation are harmless;
 * (2) a missing target never breaks the tour - the bubble just centres; (3) no network, no storage of user data.
 * The two config tokens below are filled in by ui/shell.py (do not mention them in comments). */
(function () {
  "use strict";
  var CFG = __CFG__;
  var CSS = __CSS__;

  var P, D;
  try { P = (window.parent && window.parent.document) ? window.parent : window; D = P.document; D.body; } catch (e) { P = window; D = P.document; }

  // ---- tear down any previous instance (iframe re-created on rerun / language change)
  if (P.__msmeShell && typeof P.__msmeShell.destroy === "function") { try { P.__msmeShell.destroy(); } catch (e) {} }

  var cleanups = [], timers = [], alive = true;
  function on(t, ev, fn, opt) { t.addEventListener(ev, fn, opt); cleanups.push(function () { t.removeEventListener(ev, fn, opt); }); }
  function later(fn, ms) { var id = setTimeout(function () { if (alive) fn(); }, ms); timers.push(id); return id; }
  function ss(k, v) { try { if (v === undefined) return P.sessionStorage.getItem("msme_" + k); P.sessionStorage.setItem("msme_" + k, v); } catch (e) {} return null; }
  function ls(k, v) { try { if (v === undefined) return P.localStorage.getItem("msme_" + k); P.localStorage.setItem("msme_" + k, v); } catch (e) {} return null; }
  function h(tag, attrs, kids) {
    var e = D.createElement(tag);
    for (var k in (attrs || {})) {
      if (k === "class") e.className = attrs[k]; else if (k === "text") e.textContent = attrs[k];
      else e.setAttribute(k, attrs[k]);
    }
    (kids || []).forEach(function (c) { if (c) e.appendChild(c); });
    return e;
  }
  function fmt(s, o) { return String(s).replace(/\{(\w+)\}/g, function (_, k) { return o[k]; }); }

  var LANG = CFG.lang, UI = CFG.ui[LANG] || CFG.ui.en, STEPS = CFG.steps || [];
  var root = null, tourEl = null, menuOpen = false;

  // ---------------------------------------------------------------- styles + theme
  function installStyle() {
    var old = D.getElementById("msme-shell-style"); if (old) old.remove();
    var st = h("style", { id: "msme-shell-style" }); st.textContent = CSS; D.head.appendChild(st);
  }
  function theme() { return ls("theme") === "dark" ? "dark" : "light"; }
  function applyTheme(m) {
    D.documentElement.setAttribute("data-msme-theme", m);
    D.documentElement.style.colorScheme = m;
    ls("theme", m);
    var b = D.getElementById("msme-theme");
    if (b) { b.setAttribute("aria-checked", m === "dark" ? "true" : "false"); b.title = m === "dark" ? UI.theme_light : UI.theme_dark; b.setAttribute("aria-label", b.title); }
  }

  // ---------------------------------------------------------------- floating controls (i + theme)
  function buildCluster() {
    var old = D.getElementById("msme-cluster"); if (old) old.remove();
    var info = h("button", { id: "msme-info", class: "msme-i", type: "button", "aria-haspopup": "true", "aria-expanded": "false", title: UI.info, "aria-label": UI.info }, [h("span", { text: "i" })]);
    var sw = h("button", { id: "msme-theme", class: "msme-switch", type: "button", role: "switch", "aria-checked": "false" },
      [h("span", { class: "msme-sun", text: "☀" }), h("span", { class: "msme-track" }, [h("span", { class: "msme-knob" })]), h("span", { class: "msme-moon", text: "☾" })]);
    var menu = h("div", { id: "msme-menu", class: "msme-menu", role: "menu", hidden: "hidden" });
    var go = h("button", { class: "msme-menu-item", type: "button", role: "menuitem", "data-act": "tour", text: "▶  " + UI.tour });
    var about = h("div", { class: "msme-about" }, [h("strong", { text: UI.about }), h("p", { text: CFG.pageInfo || UI.no_info })]);
    menu.appendChild(go); menu.appendChild(about);
    var box = h("div", { id: "msme-cluster", role: "toolbar", "aria-label": UI.info }, [info, sw, menu]);
    D.body.appendChild(box);
    on(info, "click", function (e) { e.stopPropagation(); toggleMenu(); });
    on(sw, "click", function () { applyTheme(theme() === "dark" ? "light" : "dark"); });
    on(go, "click", function () { toggleMenu(false); startTour(0); });
    on(D, "click", function (e) { if (menuOpen && !box.contains(e.target)) toggleMenu(false); });
    applyTheme(theme());
    return box;
  }
  function toggleMenu(force) {
    var m = D.getElementById("msme-menu"), i = D.getElementById("msme-info"); if (!m) return;
    menuOpen = force === undefined ? !menuOpen : !!force;
    if (menuOpen) m.removeAttribute("hidden"); else m.setAttribute("hidden", "hidden");
    i.setAttribute("aria-expanded", menuOpen ? "true" : "false");
  }

  // ---------------------------------------------------------------- finding things in Streamlit's DOM
  function radios() { return D.querySelectorAll('[data-testid="stSidebar"] [data-testid="stRadio"]'); }
  function visible(e) {
    if (!e || !e.isConnected) return false;
    if (CFG.testMode) return true;
    var r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0;
  }
  function find(sels) {
    for (var i = 0; i < (sels || []).length; i++) {
      var s = sels[i], e = null;
      try {
        if (s === "@lang_radio") e = radios()[0] || null;
        else if (s === "@nav_radio") e = radios()[1] || null;
        else e = D.querySelector(s);
      } catch (err) { e = null; }
      if (visible(e)) return e;
    }
    return null;
  }
  function clickRadio(group, idx) {
    var g = radios()[group]; if (!g) return false;
    var labels = g.querySelectorAll("label"); var l = labels[idx]; if (!l) return false;
    l.click(); return true;
  }

  // ---------------------------------------------------------------- the tour
  function stepIdx() { var n = parseInt(ss("step") || "0", 10); return isNaN(n) ? 0 : Math.max(0, Math.min(n, STEPS.length - 1)); }

  function startTour(i) { ss("active", "1"); ss("step", String(i || 0)); ss("done", null); renderStep(); }
  function endTour(markDone) {
    ss("active", "0"); if (markDone) ss("done", "1");
    if (tourEl) { tourEl.remove(); tourEl = null; }
  }

  function renderStep() {
    if (ss("active") !== "1" || !STEPS.length) return;
    var i = stepIdx(), s = STEPS[i];
    // page jump: the step lives on another page -> click that sidebar item and wait for the rerun to rebuild us
    var want = CFG.navKeys.indexOf(s.page);
    if (want >= 0 && CFG.currentNav !== want) {
      if (ss("jump") !== String(i)) {
        ss("jump", String(i));
        showBubble(s, i, null, true);
        if (clickRadio(1, want)) return;
      }
      // jump already attempted (or impossible): carry on without it
    }
    ss("jump", null);
    var tries = 0;
    (function look() {
      var tgt = find(s.sel);
      if (tgt || !s.sel.length || tries >= (CFG.testMode ? 2 : 22)) { showBubble(s, i, tgt, false); return; }
      tries++; later(look, 200);
    })();
  }

  function pill(code, label) {
    var b = h("button", { class: "msme-pill" + (code === LANG ? " on" : ""), type: "button", "data-lang": code, "aria-pressed": code === LANG ? "true" : "false", text: label });
    on(b, "click", function () { if (code !== LANG) clickRadio(0, CFG.langs.map(function (l) { return l[0]; }).indexOf(code)); });
    return b;
  }

  function showBubble(s, i, tgt, waiting) {
    if (tourEl) tourEl.remove();
    tourEl = h("div", { id: "msme-tour", role: "presentation" });
    var dim = h("div", { class: "msme-dim" + (tgt ? " has-target" : "") });
    var spot = h("div", { class: "msme-spot" }); spot.style.display = "none";
    var total = STEPS.length, last = i === total - 1;
    var dots = h("div", { class: "msme-dots", "aria-hidden": "true" });
    for (var d = 0; d < total; d++) dots.appendChild(h("span", { class: d === i ? "on" : (d < i ? "past" : "") }));
    var langs = h("div", { class: "msme-langs", role: "group" }, CFG.langs.map(function (l) { return pill(l[0], l[1]); }));
    var next = h("button", { class: "msme-primary", type: "button", "data-act": "next", text: (last ? UI.finish : UI.next) + (last ? " ✓" : "  ›") });
    var back = h("button", { class: "msme-ghost", type: "button", "data-act": "back", text: "‹  " + UI.back });
    if (i === 0) back.setAttribute("disabled", "disabled");
    var skip = h("button", { class: "msme-link", type: "button", "data-act": "skip", text: UI.skip });
    var tail = h("i", { class: "msme-tail" });
    var bubble = h("div", { class: "msme-bubble", role: "dialog", "aria-modal": "true", "aria-label": s.title }, [
      h("div", { class: "msme-b-top" }, [h("span", { class: "msme-badge", text: fmt(UI.step, { n: i + 1, total: total }) }), langs]),
      h("h3", { class: "msme-b-title", text: s.title }),
      h("p", { class: "msme-b-text", text: waiting ? UI.waiting : s.text }),
      dots,
      h("div", { class: "msme-b-actions" }, [skip, h("span", { class: "msme-sp" }), back, next]),
      tail
    ]);
    tourEl.appendChild(dim); tourEl.appendChild(spot); tourEl.appendChild(bubble); D.body.appendChild(tourEl);

    on(next, "click", function () { if (last) { endTour(true); } else { ss("step", String(i + 1)); renderStep(); } });
    on(back, "click", function () { if (i > 0) { ss("step", String(i - 1)); renderStep(); } });
    on(skip, "click", function () { endTour(true); });
    on(dim, "click", function () { /* clicks outside are swallowed so the page underneath stays still */ });

    var place = function () { positionBubble(bubble, tail, spot, dim, tgt, s.place); };
    if (tgt) { try { tgt.scrollIntoView({ block: "center", behavior: "auto" }); } catch (e) {} }
    place(); later(place, 120); later(place, 450);
    try { next.focus({ preventScroll: true }); } catch (e) {}
  }

  function positionBubble(bubble, tail, spot, dim, tgt, pref) {
    var vw = P.innerWidth || 1024, vh = P.innerHeight || 768, m = 14, gap = 20;
    var bw = bubble.offsetWidth || 340, bh = bubble.offsetHeight || 220;
    tail.style.display = "none"; tail.removeAttribute("data-side");
    if (!tgt) {
      spot.style.display = "none";
      bubble.style.left = Math.max(m, (vw - bw) / 2) + "px"; bubble.style.top = Math.max(m, (vh - bh) / 2) + "px"; return;
    }
    var r = tgt.getBoundingClientRect(), pad = 8;
    spot.style.display = "block";
    spot.style.left = (r.left - pad) + "px"; spot.style.top = (r.top - pad) + "px";
    spot.style.width = (r.width + pad * 2) + "px"; spot.style.height = (r.height + pad * 2) + "px";
    var order = [pref || "bottom", "right", "left", "bottom", "top"].filter(function (v, k, a) { return v !== "center" && a.indexOf(v) === k; });
    var pick = null;
    order.forEach(function (side) {
      if (pick) return;
      var L, T;
      if (side === "right") { L = r.right + pad + gap; T = r.top + r.height / 2 - bh / 2; }
      else if (side === "left") { L = r.left - pad - gap - bw; T = r.top + r.height / 2 - bh / 2; }
      else if (side === "bottom") { T = r.bottom + pad + gap; L = r.left + r.width / 2 - bw / 2; }
      else { T = r.top - pad - gap - bh; L = r.left + r.width / 2 - bw / 2; }
      var fits = (side === "right" || side === "left") ? (L >= m && L + bw <= vw - m) : (T >= m && T + bh <= vh - m);
      if (fits) pick = { side: side, L: L, T: T };
    });
    if (!pick) { bubble.style.left = Math.max(m, (vw - bw) / 2) + "px"; bubble.style.top = Math.max(m, vh - bh - 24) + "px"; return; }
    var L2 = Math.min(Math.max(pick.L, m), vw - bw - m), T2 = Math.min(Math.max(pick.T, m), vh - bh - m);
    bubble.style.left = L2 + "px"; bubble.style.top = T2 + "px";
    // tail points at the target's centre, kept inside the bubble's rounded corners
    var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    tail.style.display = "block"; tail.setAttribute("data-side", pick.side);
    if (pick.side === "right" || pick.side === "left") {
      tail.style.top = Math.min(Math.max(cy - T2 - 9, 26), bh - 44) + "px"; tail.style.left = ""; 
    } else {
      tail.style.left = Math.min(Math.max(cx - L2 - 9, 26), bw - 44) + "px"; tail.style.top = "";
    }
  }

  // ---------------------------------------------------------------- lifecycle
  function reflow() { if (tourEl) renderStepPositionOnly(); }
  function renderStepPositionOnly() {
    var b = tourEl && tourEl.querySelector(".msme-bubble"); if (!b) return;
    var i = stepIdx(), s = STEPS[i], tgt = find(s.sel);
    positionBubble(b, tourEl.querySelector(".msme-tail"), tourEl.querySelector(".msme-spot"), tourEl.querySelector(".msme-dim"), tgt, s.place);
  }
  function onKey(e) {
    if (!tourEl) return;
    if (e.key === "Escape") { endTour(true); }
    else if (e.key === "ArrowRight") { var n = tourEl.querySelector('[data-act="next"]'); if (n) n.click(); }
    else if (e.key === "ArrowLeft") { var b = tourEl.querySelector('[data-act="back"]'); if (b && !b.disabled) b.click(); }
  }

  function destroy() {
    alive = false; timers.forEach(clearTimeout); cleanups.forEach(function (f) { try { f(); } catch (e) {} });
    ["msme-tour", "msme-cluster", "msme-shell-style"].forEach(function (id) { var e = D.getElementById(id); if (e) e.remove(); });
    try { delete P.__msmeShell; } catch (e) { P.__msmeShell = null; }
  }

  installStyle();
  root = buildCluster();
  on(P, "resize", reflow); on(P, "scroll", reflow, true); on(D, "keydown", onKey);
  P.__msmeShell = { destroy: destroy, start: startTour, lang: LANG, version: "1.0" };
  try { var fe = window.frameElement; if (fe) { fe.style.display = "none"; if (fe.parentElement) fe.parentElement.style.display = "none"; } } catch (e) {}

  if (ss("active") === "1") { later(renderStep, CFG.testMode ? 0 : 350); }
  else if (CFG.autostart && !ss("done") && !ss("started")) { ss("started", "1"); later(function () { startTour(0); }, CFG.testMode ? 0 : 900); }
})();

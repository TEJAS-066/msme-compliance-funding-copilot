// Runs ui/assets/shell.js (built by Python with real config) inside jsdom against a fake Streamlit page.
const { test } = require("node:test");
const assert = require("node:assert");
const { JSDOM } = require("jsdom");
const { execFileSync } = require("node:child_process");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..", "..");
const NAV = ["nav_dashboard","nav_profile","nav_documents","nav_schemes","nav_checklist","nav_copilot","nav_channel","nav_forms","nav_tasks","nav_admin"];

function build(lang, current, patch = "") {
  const code = `
import json, sys
sys.path.insert(0, ${JSON.stringify(ROOT)})
from ui import shell
nav = ${JSON.stringify(NAV)}
cfg = shell.build_config(${JSON.stringify(lang)}, nav, ${JSON.stringify(current)}, test_mode=True)
${patch}
sys.stdout.write(shell.build_script(cfg))`;
  return execFileSync("python3", ["-c", code], { encoding: "utf-8" });
}

function page(extra = "") {
  const labels = (n) => Array.from({ length: n }, (_, i) => `<label data-i="${i}">opt${i}</label>`).join("");
  const dom = new JSDOM(`<!doctype html><body>
    <div data-testid="stSidebar"><div data-testid="stRadio" id="langradio">${labels(4)}</div><div data-testid="stRadio" id="navradio">${labels(10)}</div></div>
    <div class="st-key-btn_load_demo"><button>Load</button></div><div class="st-key-tour_stepper"></div>
    <div class="st-key-tour_nba"></div><div class="st-key-tour_agents"></div>${extra}</body>`,
    { url: "http://localhost/", runScripts: "outside-only", pretendToBeVisual: true });
  dom.window.__clicks = [];
  dom.window.document.querySelectorAll("label").forEach((l) => l.addEventListener("click", () => {
    dom.window.__clicks.push([l.parentElement.id, Number(l.dataset.i)]);
  }));
  return dom;
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const run = (dom, js) => dom.window.eval(js);
const q = (dom, sel) => dom.window.document.querySelector(sel);
const title = (dom) => q(dom, ".msme-b-title")?.textContent;

test("auto-starts on first visit with controls and a localised bubble", async () => {
  const dom = page(); run(dom, build("en", "nav_dashboard")); await sleep(40);
  assert.ok(q(dom, "#msme-cluster"), "cluster present");
  assert.ok(q(dom, "#msme-info") && q(dom, "#msme-theme"), "info + theme controls present");
  assert.match(title(dom), /Welcome to MSME Copilot/);
  assert.match(q(dom, ".msme-badge").textContent, /Step 1 of 12/);
  assert.equal(q(dom, ".msme-spot").style.display, "none", "welcome step has no spotlight");
});

test("Next points at the real component and draws a tail", async () => {
  const dom = page(); run(dom, build("en", "nav_dashboard")); await sleep(40);
  q(dom, '[data-act="next"]').click(); await sleep(60);
  assert.match(title(dom), /Pick your language/);
  assert.notEqual(q(dom, ".msme-spot").style.display, "none");
  assert.ok(q(dom, ".msme-tail").getAttribute("data-side"), "tail has a side");
  q(dom, '[data-act="back"]').click(); await sleep(40);
  assert.match(title(dom), /Welcome/);
  assert.ok(q(dom, '[data-act="back"]').disabled, "Back disabled on first step");
});

test("language pill drives the sidebar radio; reinstall resumes in the new language, one tour only", async () => {
  const dom = page(); run(dom, build("en", "nav_dashboard")); await sleep(40);
  q(dom, '[data-act="next"]').click(); await sleep(40);
  q(dom, '.msme-pill[data-lang="ta"]').click();
  assert.deepEqual(dom.window.__clicks.pop(), ["langradio", 1]);
  run(dom, build("ta", "nav_dashboard")); await sleep(60);          // Streamlit rerun -> new iframe -> script re-runs
  assert.match(title(dom), /உங்கள் மொழியைத் தேர்வு/);
  assert.match(q(dom, ".msme-badge").textContent, /படி 2 \/ 12/);
  assert.equal(dom.window.document.querySelectorAll("#msme-tour").length, 1);
  assert.equal(dom.window.document.querySelectorAll("#msme-cluster").length, 1);
  run(dom, build("hi", "nav_dashboard")); await sleep(60);
  assert.match(title(dom), /अपनी भाषा चुनें/);
  run(dom, build("te", "nav_dashboard")); await sleep(60);
  assert.match(title(dom), /మీ భాషను ఎంచుకోండి/);
});

test("steps on other pages click the sidebar item once, then continue after the rerun", async () => {
  const dom = page(); run(dom, build("en", "nav_dashboard")); await sleep(40);
  run(dom, 'sessionStorage.setItem("msme_step","7")');             // 'documents' step (nav index 2)
  run(dom, build("en", "nav_dashboard")); await sleep(60);
  assert.deepEqual(dom.window.__clicks.pop(), ["navradio", 2]);
  assert.equal(dom.window.__clicks.length, 0, "exactly one jump click");
  dom.window.document.body.insertAdjacentHTML("beforeend", '<div data-testid="stFileUploader"></div>');
  run(dom, build("en", "nav_documents")); await sleep(60);        // rerun on the Documents page
  assert.match(title(dom), /Upload → read → confirm/);
  assert.notEqual(q(dom, ".msme-spot").style.display, "none");
  assert.equal(dom.window.__clicks.length, 0, "no second jump");
});

test("a missing target never breaks the tour: bubble centres without spotlight", async () => {
  const dom = page(); run(dom, build("en", "nav_dashboard")); await sleep(40);
  run(dom, 'sessionStorage.setItem("msme_step","9")');             // copilot step; no chat input in DOM
  run(dom, build("en", "nav_copilot")); await sleep(900);
  assert.match(title(dom), /Ask in your language/);
  assert.equal(q(dom, ".msme-spot").style.display, "none");
  assert.equal(q(dom, ".msme-tail").style.display, "none");
});

test("Escape ends the tour and it does not auto-start again; i-menu restarts it", async () => {
  const dom = page(); run(dom, build("en", "nav_dashboard")); await sleep(40);
  dom.window.document.dispatchEvent(new dom.window.KeyboardEvent("keydown", { key: "Escape" }));
  assert.equal(q(dom, "#msme-tour"), null);
  run(dom, build("en", "nav_dashboard")); await sleep(60);
  assert.equal(q(dom, "#msme-tour"), null, "no auto-restart after done");
  q(dom, "#msme-info").click();
  assert.equal(q(dom, "#msme-menu").hasAttribute("hidden"), false);
  assert.match(q(dom, ".msme-about").textContent, /About this page/);
  q(dom, '[data-act="tour"]').click(); await sleep(40);
  assert.match(title(dom), /Welcome/);
});

test("arrow keys navigate; Finish on the last step closes and marks done", async () => {
  const dom = page(); run(dom, build("en", "nav_dashboard")); await sleep(40);
  dom.window.document.dispatchEvent(new dom.window.KeyboardEvent("keydown", { key: "ArrowRight" })); await sleep(50);
  assert.match(title(dom), /Pick your language/);
  run(dom, 'sessionStorage.setItem("msme_step","11")');
  run(dom, build("en", "nav_dashboard")); await sleep(60);
  assert.match(q(dom, '[data-act="next"]').textContent, /Finish/);
  q(dom, '[data-act="next"]').click();
  assert.equal(q(dom, "#msme-tour"), null);
  assert.equal(run(dom, 'sessionStorage.getItem("msme_done")'), "1");
});

test("theme switch toggles the attribute, persists, and survives a reinstall", async () => {
  const dom = page(); run(dom, build("en", "nav_dashboard")); await sleep(40);
  const html = dom.window.document.documentElement;
  assert.equal(html.getAttribute("data-msme-theme"), "light");
  q(dom, "#msme-theme").click();
  assert.equal(html.getAttribute("data-msme-theme"), "dark");
  assert.equal(q(dom, "#msme-theme").getAttribute("aria-checked"), "true");
  assert.equal(run(dom, 'localStorage.getItem("msme_theme")'), "dark");
  run(dom, build("ta", "nav_dashboard")); await sleep(40);
  assert.equal(html.getAttribute("data-msme-theme"), "dark");
  assert.match(q(dom, "#msme-theme").title, /ஒளி/);
});

test("tour text is rendered as text, never as HTML", async () => {
  const dom = page();
  run(dom, build("en", "nav_dashboard", "cfg['steps'][0]['title'] = '<img src=x onerror=window.__pwn=1>'")); await sleep(60);
  assert.equal(title(dom), "<img src=x onerror=window.__pwn=1>");
  assert.equal(dom.window.__pwn, undefined);
  assert.equal(q(dom, ".msme-b-title img"), null);
});

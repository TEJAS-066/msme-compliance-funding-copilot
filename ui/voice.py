"""Experimental browser-side voice input (Web Speech API). NOT verified in this build's test environment.

How it works: the browser's own speech service transcribes; JS then drops the text into Streamlit's chat box.
This app never receives audio. Chrome/Edge only; failure is visible, never silent.
"""
import json

import streamlit.components.v1 as components

from core.i18n import t


def render(lang: str) -> None:
    labels = {"start": t("v_start", lang), "listening": t("v_listening", lang), "heard": t("v_heard", lang, text="__TEXT__"),
              "unsupported": t("v_unsupported", lang)}
    html = """
<div style="font-family:sans-serif;font-size:14px">
  <button id="b" style="padding:6px 12px;font-size:14px;cursor:pointer"></button>
  <span id="s" style="margin-left:8px;color:#444"></span>
</div>
<script>
const L = __LABELS__, LANG = "__LANG__";
const b = document.getElementById('b'), s = document.getElementById('s');
b.textContent = L.start;
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
function fill(text) {
  try {
    const doc = window.parent.document;
    const ta = doc.querySelector('[data-testid="stChatInputTextArea"]') || doc.querySelector('[data-testid="stChatInput"] textarea');
    if (!ta) throw new Error('no chat box');
    const setter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, 'value').set;
    setter.call(ta, text);
    ta.dispatchEvent(new Event('input', { bubbles: true }));
    ta.focus();
  } catch (e) { /* fall through: text is still shown to the user below */ }
}
if (!SR) { b.disabled = true; s.textContent = L.unsupported; }
else {
  b.onclick = () => {
    const r = new SR(); r.lang = LANG; r.interimResults = false; r.maxAlternatives = 1;
    s.textContent = L.listening;
    r.onresult = (e) => { const text = e.results[0][0].transcript; s.textContent = L.heard.replace('__TEXT__', text); fill(text); };
    r.onerror = (e) => { s.textContent = 'Error: ' + e.error; };
    r.onend = () => { if (s.textContent === L.listening) s.textContent = ''; };
    r.start();
  };
}
</script>"""
    html = html.replace("__LABELS__", json.dumps(labels, ensure_ascii=False)).replace("__LANG__", "ta-IN" if lang == "ta" else "en-IN")
    components.html(html, height=48)

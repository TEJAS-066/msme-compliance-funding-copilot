"""Retrieval Agent: catalogue lookup (no vector DB needed at this scale).

WHY no vector DB: with a handful of verified schemes, keyword + structured lookup
is more precise and fully explainable. Add embeddings only once the catalogue
grows past ~20-30 schemes (see roadmap).
"""
from __future__ import annotations

from core.catalogue import get_catalogue, list_schemes, unverified_backlog, L

INTENT_WORDS = {
    "eligibility": ["eligible", "eligibility", "qualify", "can i get", "am i", "தகுதி", "கிடைக்குமா", "தகுதியா"],
    "documents":   ["document", "documents", "papers", "checklist", "certificate", "what do i need", "ஆவண", "சான்றிதழ்", "என்ன வேண்டும்"],
    "amount":      ["limit", "how much", "amount", "maximum", "benefit", "எவ்வளவு", "தொகை", "வரம்பு", "பலன்"],
    "next_steps":  ["next", "what should i do", "steps", "how do i apply", "how to apply", "அடுத்து", "என்ன செய்ய", "எப்படி விண்ணப்ப"],
    "deadline":    ["deadline", "due date", "last date", "reminder", "காலக்கெடு", "கடைசி தேதி"],
    "form":        ["form", "fill", "application", "படிவம்", "விண்ணப்ப"],
    "overview":    ["what is", "explain", "meaning", "tell me about", "என்றால் என்ன", "பற்றி"],
}


def detect_intent(question: str) -> str:
    q = question.lower()
    best, best_hits = "overview", 0
    for intent, words in INTENT_WORDS.items():
        hits = sum(1 for w in words if w in q)
        if hits > best_hits:
            best, best_hits = intent, hits
    return best if best_hits else "unknown"


def match_schemes(question: str, cat: dict | None = None) -> list[str]:
    cat = cat or get_catalogue()
    q = question.lower()
    ids = []
    for s in list_schemes(cat):
        names = [L(s["name"], "en").lower(), L(s["name"], "ta").lower()] + [k.lower() for k in s.get("keywords", [])]
        if any(n and n in q for n in names):
            ids.append(s["id"])
    return ids


def match_backlog(question: str, cat: dict | None = None) -> list[dict]:
    q = question.lower()
    out = []
    for b in unverified_backlog(cat):
        if b["id"].replace("_", " ") in q or b["id"] in q or L(b["name"], "en").split(" ")[0].lower() in q:
            out.append(b)
    return out


def retrieve(question: str, cat: dict | None = None) -> dict:
    cat = cat or get_catalogue()
    return {"intent": detect_intent(question),
            "scheme_ids": match_schemes(question, cat),
            "backlog": match_backlog(question, cat)}

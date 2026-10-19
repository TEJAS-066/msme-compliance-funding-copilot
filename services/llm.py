"""Server-side LLM adapter. Keys come from environment variables ONLY.

If no provider/key is configured, `get_provider()` returns None and the app runs in
deterministic DEMO mode. The HTTP call is injectable (`post=`) so tests never hit the network.
NOTE: the three provider payloads below follow the vendors' public REST docs but were NOT
executed live in the starter build - run scripts/check_llm.py once with your key.
"""
from __future__ import annotations

import os
from typing import Callable

import requests


class LLMError(RuntimeError):
    pass


def get_provider() -> str | None:
    p = (os.environ.get("LLM_PROVIDER") or "").strip().lower()
    keys = {"anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY", "sarvam": "SARVAM_API_KEY"}
    if p:
        return p if (p in keys and os.environ.get(keys[p])) else None
    for prov, env_key in keys.items():
        if os.environ.get(env_key):
            return prov
    return None



def complete(system: str, user: str, provider: str | None = None, post: Callable = requests.post, timeout: int = 30) -> str:
    provider = provider or get_provider()
    if not provider:
        raise LLMError("no LLM provider configured")
    try:
        if provider == "anthropic":
            r = post("https://api.anthropic.com/v1/messages", timeout=timeout,
                     headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"},
                     json={"model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5"), "max_tokens": 700,
                           "system": system, "messages": [{"role": "user", "content": user}]})
            r.raise_for_status()
            return "".join(b.get("text", "") for b in r.json()["content"] if b.get("type") == "text").strip()
        if provider == "gemini":
            model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
            r = post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", timeout=timeout,
                     headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "content-type": "application/json"},
                     json={"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": user}]}]})
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        if provider == "sarvam":
            r = post("https://api.sarvam.ai/v1/chat/completions", timeout=timeout,
                     headers={"api-subscription-key": os.environ["SARVAM_API_KEY"], "content-type": "application/json"},
                     json={"model": os.environ.get("SARVAM_MODEL", "sarvam-30b"),
                           "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
    except LLMError:
        raise
    except Exception as e:  # network, HTTP, JSON shape -> one clean error type
        raise LLMError(f"{provider} call failed: {type(e).__name__}") from e
    raise LLMError(f"unknown provider {provider}")

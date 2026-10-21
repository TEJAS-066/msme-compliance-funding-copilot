"""One place to read settings/secrets: environment variables first, then Streamlit secrets (cloud hosting).

WHY: on Streamlit Community Cloud you paste secrets into the app settings; reading both sources means the same
code works on a laptop (.env / shell variables) and in the cloud. Secrets are NEVER written to logs or the UI.
"""
from __future__ import annotations

import os


def get(name: str, default: str | None = None) -> str | None:
    v = os.environ.get(name)
    if v:
        return v
    try:                                    # only meaningful inside a running Streamlit app
        import streamlit as st
        v = st.secrets.get(name)            # raises if no secrets file exists -> handled below
        if v:
            return str(v)
    except Exception:
        pass
    return default


def load_env_file(path: str | None = None) -> list[str]:
    """Load KEY=VALUE lines from .env into os.environ (never overriding real environment variables).

    Tiny on purpose (no extra dependency). Blank values are ignored so placeholders in .env.example don't
    clobber anything. Returns the NAMES loaded - never the values.
    """
    path = path or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    loaded: list[str] = []
    if not os.path.isfile(path):
        return loaded
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip()
            if val[:1] in ("'", '"') and val.count(val[0]) >= 2:
                val = val[1:val.index(val[0], 1)]
            elif val.startswith("#"):
                val = ""                                  # "KEY=   # comment" means blank
            else:
                val = val.split(" #", 1)[0].strip()
            if key and val and key not in os.environ:
                os.environ[key] = val
                loaded.append(key)
    return loaded

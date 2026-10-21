"""Embed trusted, app-authored HTML/JS (never user content). Uses st.iframe where available (components.v1.html is being removed)."""
import streamlit as st


def run_html(code: str, height: int = 0) -> None:
    if hasattr(st, "iframe"):
        st.iframe(code, height=max(1, height))
    else:                                   # older Streamlit (>=1.40)
        import streamlit.components.v1 as components
        components.html(code, height=height)

"""Shared UI helpers, GovTech clean styling, and 5-stage stepper."""
from __future__ import annotations

import textwrap
import streamlit as st

from core import db
from core import profile as P
from core.i18n import t
from services import llm


def lang() -> str:
    return st.session_state.get("lang", "en")


def get_profile() -> dict:
    if "profile" not in st.session_state:
        st.session_state["profile"] = db.load_profile() or P.empty_profile()
    return st.session_state["profile"]


def save_profile(p: dict) -> None:
    st.session_state["profile"] = p
    db.save_profile(p)


def apply_custom_styles(theme: str | None = None) -> None:
    """Inject clean, human-crafted GovTech & Fintech portal styling with full Light / Dark theme support."""
    theme = theme or st.session_state.get("theme", "light")
    is_dark = "dark" in str(theme).lower() or "🌙" in str(theme)

    if is_dark:
        bg_main = "#0B1120"
        sidebar_bg = "#0F172A"
        sidebar_border = "#1E293B"
        card_bg = "#111827"
        border_col = "#1F2937"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        heading_col = "#FFFFFF"
        metric_bg = "#111827"
        btn_sec_bg = "#1F2937"
        btn_sec_border = "#374151"
        btn_sec_text = "#FFFFFF"
        btn_sec_hover = "#374151"
        input_bg = "#1F2937"
    else:
        bg_main = "#F8FAFC"
        sidebar_bg = "#F1F5F9"
        sidebar_border = "#E2E8F0"
        card_bg = "#FFFFFF"
        border_col = "#E2E8F0"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        heading_col = "#0F172A"
        metric_bg = "#FFFFFF"
        btn_sec_bg = "#FFFFFF"
        btn_sec_border = "#CBD5E1"
        btn_sec_text = "#0F172A"
        btn_sec_hover = "#F1F5F9"
        input_bg = "#FFFFFF"

    css = textwrap.dedent(f"""
    <style>
    /* Full Theme root styling */
    .stApp, div[data-testid="stAppViewContainer"] {{
        background-color: {bg_main} !important;
        color: {text_primary} !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {sidebar_border} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {text_primary} !important;
    }}

    /* Global Text Contrast */
    .stApp p, .stApp span, .stApp label, .stApp li {{
        color: {text_primary} !important;
    }}

    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
        color: {heading_col} !important;
        font-weight: 700 !important;
    }}

    /* Base typography & layout padding */
    .main .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1140px;
    }}
    
    /* Metrics styling */
    div[data-testid="stMetric"] {{
        background-color: {metric_bg} !important;
        border: 1px solid {border_col} !important;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }}
    div[data-testid="stMetricValue"] {{
        font-weight: 700;
        color: {heading_col} !important;
    }}
    div[data-testid="stMetricLabel"] {{
        font-weight: 500;
        color: {text_secondary} !important;
    }}

    /* Container card styling */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {{
        background-color: {card_bg} !important;
        border: 1px solid {border_col} !important;
    }}

    /* Primary buttons - Guaranteed Crisp White Text on Emerald */
    button[data-testid="baseButton-primary"],
    button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button {{
        background-color: #0B6E4F !important;
        background: #0B6E4F !important;
        border-color: #0B6E4F !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}
    button[data-testid="baseButton-primary"] *,
    button[kind="primary"] *,
    div[data-testid="stFormSubmitButton"] > button * {{
        color: #FFFFFF !important;
    }}
    button[data-testid="baseButton-primary"]:hover,
    button[kind="primary"]:hover {{
        background-color: #085039 !important;
        background: #085039 !important;
        border-color: #085039 !important;
        color: #FFFFFF !important;
    }}
    button[data-testid="baseButton-primary"]:hover *,
    button[kind="primary"]:hover * {{
        color: #FFFFFF !important;
    }}

    /* Secondary / Default Buttons - EXPLICIT HIGH CONTRAST & READABLE */
    button[data-testid="baseButton-secondary"],
    button[kind="secondary"],
    div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]):not([kind="primary"]) {{
        background-color: {btn_sec_bg} !important;
        background: {btn_sec_bg} !important;
        border: 1.5px solid {btn_sec_border} !important;
        color: {btn_sec_text} !important;
        font-weight: 600 !important;
    }}
    button[data-testid="baseButton-secondary"] *,
    button[kind="secondary"] *,
    div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]):not([kind="primary"]) * {{
        color: {btn_sec_text} !important;
    }}
    button[data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover,
    div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]):not([kind="primary"]):hover {{
        background-color: {btn_sec_hover} !important;
        background: {btn_sec_hover} !important;
        border-color: #0B6E4F !important;
        color: {heading_col} !important;
    }}
    button[data-testid="baseButton-secondary"]:hover *,
    button[kind="secondary"]:hover *,
    div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]):not([kind="primary"]):hover * {{
        color: {heading_col} !important;
    }}

    /* Inputs, Textareas, Selectboxes */
    input, textarea, div[data-baseweb="input"], div[data-baseweb="base-input"] {{
        background-color: {input_bg} !important;
        border-color: {border_col} !important;
        color: {text_primary} !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        border-color: {border_col} !important;
        color: {text_primary} !important;
    }}
    div[data-baseweb="popover"], ul[role="listbox"] {{
        background-color: {input_bg} !important;
        border: 1px solid {border_col} !important;
    }}
    li[role="option"] {{
        background-color: {input_bg} !important;
        color: {text_primary} !important;
    }}
    li[role="option"]:hover, li[aria-selected="true"] {{
        background-color: {btn_sec_hover} !important;
        color: {heading_col} !important;
    }}

    /* Pixel-Perfect Circular 'i' info button */
    div[data-testid="stPopover"] > button {{
        border-radius: 9999px !important;
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        max-width: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        padding: 0 !important;
        margin: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 1.5px solid {border_col} !important;
        background-color: {card_bg} !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        cursor: pointer !important;
    }}
    div[data-testid="stPopover"] > button * {{
        font-size: 1.15rem !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
        color: {heading_col} !important;
        text-align: center !important;
    }}

    /* Mobile Responsive Optimizations (< 768px) */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-top: 0.8rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-bottom: 2rem !important;
        }}
        div[data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap !important;
            gap: 0.5rem !important;
        }}
        div[data-testid="column"] {{
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }}
        div[data-testid="stMetric"] {{
            margin-bottom: 0.5rem;
            width: 100% !important;
        }}
        div[data-testid="stButton"] > button {{
            width: 100% !important;
            margin-bottom: 0.4rem;
        }}
        div[data-testid="stPopover"] > button {{
            width: 36px !important;
            height: 36px !important;
        }}
    }}
    </style>
    """).strip()
    st.html(css)


def render_page_header(title_key: str, info_key: str) -> None:
    """Standardized page header with title, Day/Night toggle bar, and circular info button."""
    l = lang()
    c_title, c_toggle, c_info = st.columns([4.2, 1.8, 0.6], vertical_alignment="center")
    with c_title:
        st.header(t(title_key, l))
    with c_toggle:
        is_dark = st.session_state.get("dark_mode", False)
        new_val = st.toggle("🌙 Dark" if is_dark else "☀️ Light", value=is_dark, key=f"theme_toggle_{title_key}")
        if new_val != is_dark:
            st.session_state["dark_mode"] = new_val
            st.session_state["theme"] = "dark" if new_val else "light"
            st.rerun()
    with c_info:
        with st.popover("ℹ️", help=t("btn_page_info", l), use_container_width=True):
            st.markdown(f"#### ℹ️ {t(title_key, l)}")
            st.info(t(info_key, l))
            st.caption("GovTech AI • " + t("btn_page_info", l))


def render_spotlight_tour() -> None:
    """Inject interactive client-side spotlight tour that points directly to screen components."""
    force_js = "window.__FORCE_TOUR = true;" if st.session_state.get("trigger_spotlight") else "window.__FORCE_TOUR = false;"
    if st.session_state.get("trigger_spotlight"):
        st.session_state["trigger_spotlight"] = False

    tour_html = f"""
    <div id="msme-spotlight-overlay" style="display: none; position: fixed; inset: 0; z-index: 999999; pointer-events: auto; background: rgba(0, 0, 0, 0.75);">
      <div id="msme-spotlight-box" style="position: absolute; border: 3px solid #10B981; border-radius: 8px; box-shadow: 0 0 25px rgba(16, 185, 129, 0.7), inset 0 0 15px rgba(16, 185, 129, 0.3); transition: all 0.35s ease; pointer-events: none;"></div>
      <div id="msme-spotlight-card" style="position: absolute; width: 340px; max-width: 90vw; background: #0F172A; color: #FFFFFF; border: 1px solid #334155; border-radius: 12px; padding: 18px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); transition: all 0.35s ease; font-family: sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span id="msme-spotlight-step" style="font-size: 0.8rem; font-weight: 700; color: #10B981; text-transform: uppercase; letter-spacing: 0.05em;">Step 1 of 4</span>
          <button onclick="window.msmeTourDone()" style="background: none; border: none; color: #94A3B8; font-size: 1.1rem; cursor: pointer; padding: 0;">✕</button>
        </div>
        <h4 id="msme-spotlight-title" style="margin: 0 0 8px 0; font-size: 1.05rem; color: #FFFFFF;"></h4>
        <p id="msme-spotlight-desc" style="margin: 0 0 16px 0; font-size: 0.88rem; color: #CBD5E1; line-height: 1.45;"></p>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <button id="msme-spotlight-prev" onclick="window.msmeTourPrev()" style="background: #1E293B; border: 1px solid #475569; color: #FFFFFF; border-radius: 6px; padding: 6px 14px; font-size: 0.85rem; cursor: pointer;">⬅ Back</button>
          <button id="msme-spotlight-next" onclick="window.msmeTourNext()" style="background: #059669; border: none; color: #FFFFFF; border-radius: 6px; padding: 6px 16px; font-size: 0.85rem; font-weight: 600; cursor: pointer;">Next ➔</button>
        </div>
      </div>
    </div>
    <script>
    (function() {{
      {force_js}
      const steps = [
        {{
          selector: 'section[data-testid="stSidebar"]',
          title: '1. Navigation & Languages',
          desc: 'Access all 10 specialized GovTech views and switch seamlessly between English, தமிழ், हिन्दी, and తెలుగు.'
        }},
        {{
          selector: 'div[data-testid="stHorizontalBlock"]',
          title: '2. Day/Night Toggle & Circular ℹ️ Guide',
          desc: 'Toggle between ☀️ Light / 🌙 Dark modes at the top, and click the circular ℹ️ button on any page for instant guidance.'
        }},
        {{
          selector: 'div[data-testid="stVerticalBlockBorderWrapper"]',
          title: '3. Stepper & Lakshmi Tour',
          desc: 'Follow the 5-Stage Stepper and run the Document Agent in 1 click on Lakshmi\\'s Tiruppur micro-textiles scenario.'
        }},
        {{
          selector: 'div[data-testid="stMetric"]',
          title: '4. Executive Metrics & AI Agents',
          desc: 'All 6 AI agents operate with 100% deterministic rules, zero hallucinations, and bank-ready PDF dossier generation.'
        }}
      ];

      let currentStep = 0;
      const overlay = document.getElementById('msme-spotlight-overlay');
      const box = document.getElementById('msme-spotlight-box');
      const card = document.getElementById('msme-spotlight-card');
      const stepLabel = document.getElementById('msme-spotlight-step');
      const titleEl = document.getElementById('msme-spotlight-title');
      const descEl = document.getElementById('msme-spotlight-desc');
      const prevBtn = document.getElementById('msme-spotlight-prev');
      const nextBtn = document.getElementById('msme-spotlight-next');

      function updatePosition() {{
        const s = steps[currentStep];
        const el = document.querySelector(s.selector) || document.body;
        const rect = el.getBoundingClientRect();

        box.style.top = Math.max(0, rect.top - 6) + 'px';
        box.style.left = Math.max(0, rect.left - 6) + 'px';
        box.style.width = Math.min(window.innerWidth - rect.left, rect.width + 12) + 'px';
        box.style.height = Math.min(window.innerHeight - rect.top, rect.height + 12) + 'px';

        let cardTop = rect.bottom + 16;
        let cardLeft = Math.max(16, rect.left);
        if (cardTop + 240 > window.innerHeight) {{
          cardTop = Math.max(16, rect.top - 240);
        }}
        if (cardLeft + 360 > window.innerWidth) {{
          cardLeft = window.innerWidth - 370;
        }}
        card.style.top = Math.max(16, cardTop) + 'px';
        card.style.left = Math.max(16, cardLeft) + 'px';

        stepLabel.innerText = `Step ${{currentStep + 1}} of ${{steps.length}}`;
        titleEl.innerText = s.title;
        descEl.innerText = s.desc;
        prevBtn.style.visibility = currentStep === 0 ? 'hidden' : 'visible';
        nextBtn.innerText = currentStep === steps.length - 1 ? 'Finish ✓' : 'Next ➔';
      }}

      window.msmeTourNext = function() {{
        if (currentStep < steps.length - 1) {{
          currentStep++;
          updatePosition();
        }} else {{
          window.msmeTourDone();
        }}
      }};

      window.msmeTourPrev = function() {{
        if (currentStep > 0) {{
          currentStep--;
          updatePosition();
        }}
      }};

      window.msmeTourDone = function() {{
        if (overlay) overlay.style.display = 'none';
        localStorage.setItem('msme_spotlight_completed', 'true');
      }};

      setTimeout(function() {{
        if (!localStorage.getItem('msme_spotlight_completed') || window.__FORCE_TOUR) {{
          if (overlay) {{
            overlay.style.display = 'block';
            updatePosition();
          }}
        }}
      }}, 800);
    }})();
    </script>
    """
    st.html(tour_html)


@st.dialog("🏛️ MSME Copilot — Quick Guided Tour")
def show_onboarding_tour() -> None:
    """Interactive multi-step onboarding tour dialog for new vendors and judges."""
    l = lang()
    step = st.session_state.get("tour_step", 1)

    if step == 1:
        st.markdown(f"#### 🏛️ {t('tour_step_1_title', l)}")
        st.write(t("tour_step_1_desc", l))
        st.info("💡 **Rules decide • AI explains • The owner acts**")
    elif step == 2:
        st.markdown(f"#### 🧭 {t('tour_step_2_title', l)}")
        st.write(t("tour_step_2_desc", l))
        st.caption("1. Understand ➔ 2. Profile ➔ 3. Match ➔ 4. Prepare ➔ 5. Track")
    elif step == 3:
        st.markdown(f"#### 📑 {t('tour_step_3_title', l)}")
        st.write(t("tour_step_3_desc", l))
        st.caption("Udyam • GSTIN Luhn Mod-36 • Anti-Hallucination Triad")
    elif step == 4:
        st.markdown(f"#### 📄 {t('tour_step_4_title', l)}")
        st.write(t("tour_step_4_desc", l))
        st.success("📄 ReportLab PDF Bank Dossier • 📱 Multilingual WhatsApp Simulator")

    st.write("---")
    c_prev, c_ind, c_next = st.columns([1.2, 1.6, 1.2], vertical_alignment="center")
    if step > 1:
        if c_prev.button(t("tour_btn_prev", l), key=f"t_prev_{step}", use_container_width=True):
            st.session_state["tour_step"] = step - 1
            st.rerun()
    else:
        c_prev.write("")

    c_ind.markdown(f"<div style='text-align: center; font-weight: 600; color: #64748B;'>Step {step} of 4</div>", unsafe_allow_html=True)

    if step < 4:
        if c_next.button(t("tour_btn_next", l), key=f"t_next_{step}", type="primary", use_container_width=True):
            st.session_state["tour_step"] = step + 1
            st.rerun()
    else:
        if c_next.button(t("tour_btn_close", l), key="t_close", type="primary", use_container_width=True):
            st.session_state["tour_open"] = False
            st.session_state["tour_step"] = 1
            st.rerun()



def banner() -> None:
    l = lang()
    st.warning(t("demo_banner", l), icon="🧪")
    prov = llm.get_provider()
    if prov:
        st.info(t("ai_mode_llm", l, provider=prov), icon="🤖")
    else:
        st.info(t("ai_mode_demo", l), icon="⚙️")


def completeness(p: dict) -> tuple[int, int]:
    known = sum(1 for v in p["fields"].values() if v["status"] == "known")
    return known, len(p["fields"])


def nba_text(nba: dict, l: str) -> str:
    """Render a core.insights.next_best_action() dict in the user's language."""
    from core.catalogue import L, get_scheme
    from core.i18n import field_label
    k = nba["kind"]
    if k == "overdue":
        return t("nba_overdue", l, title=nba["title"])
    if k == "answer_field":
        names = ", ".join(L(get_scheme(s)["name"], l).split("(")[-1].strip(")") for s in nba["schemes"])
        return t("nba_answer_field", l, field=field_label(nba["field"], l), n=nba["n"], schemes=names)
    if k == "upload_docs":
        return t("nba_upload_docs", l, docs=", ".join(L(d, l) for d in nba["docs"]), scheme=L(get_scheme(nba["scheme"])["name"], l))
    if k == "prepare":
        return t("nba_prepare", l, scheme=L(get_scheme(nba["scheme"])["name"], l))
    return t("nba_" + k, l)


def render_stepper(active_stage: int = 1) -> None:
    """Render the 5-Stage Methodology Stepper natively using Streamlit containers (no raw HTML code leaks)."""
    l = lang()
    stages = [
        (1, t("stage_1_name", l), t("stage_1_desc", l)),
        (2, t("stage_2_name", l), t("stage_2_desc", l)),
        (3, t("stage_3_name", l), t("stage_3_desc", l)),
        (4, t("stage_4_name", l), t("stage_4_desc", l)),
        (5, t("stage_5_name", l), t("stage_5_desc", l)),
    ]
    cols = st.columns(5)
    for idx, (num, name, desc) in enumerate(stages):
        with cols[idx]:
            is_active = (num == active_stage)
            with st.container(border=True):
                st.caption(f":{'green' if is_active else 'grey'}[STAGE {num}]")
                st.markdown(f"**{name}**")
                st.caption(desc)


def render_agent_inspector() -> None:
    """Render the 6 Specialized AI Agents inspector card natively from Slide 5."""
    l = lang()
    agents = [
        (t("agent_doc_name", l), t("agent_doc_desc", l), t("status_active", l)),
        (t("agent_retrieval_name", l), t("agent_retrieval_desc", l), t("status_active", l)),
        (t("agent_elig_name", l), t("agent_elig_desc", l), t("status_active", l)),
        (t("agent_form_name", l), t("agent_form_desc", l), t("status_active", l)),
        (t("agent_deadline_name", l), t("agent_deadline_desc", l), t("status_active", l)),
        (t("agent_monitor_name", l), t("agent_monitor_desc", l), t("status_active", l)),
    ]
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"#### 🤖 {t('agent_inspector_title', l)}")
        with col2:
            st.caption(":green[● 6 Agents Active]")

        cols = st.columns(3)
        for idx, (aname, adesc, astatus) in enumerate(agents):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**{aname}**")
                    st.caption(f":blue[{astatus}] — {adesc}")

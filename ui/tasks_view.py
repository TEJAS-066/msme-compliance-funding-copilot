from datetime import date

import streamlit as st

from core import tasks as T
from core.catalogue import L, get_catalogue, get_scheme, list_schemes
from core.i18n import t
from services.notifications import preview_reminder
from ui.common import lang


def render() -> None:
    l = lang()
    cat = get_catalogue()
    st.header(t("nav_tasks", l))
    ids = [s["id"] for s in list_schemes(cat)]

    with st.form("add_task", clear_on_submit=True):
        st.markdown(f"**{t('tsk_add', l)}**")
        title = st.text_input(t("tsk_title", l), key="tsk_title")
        desc = st.text_area(t("tsk_desc", l), key="tsk_desc")
        c1, c2, c3 = st.columns(3)
        use_due = c1.checkbox(t("tsk_due", l), key="tsk_use_due")
        due = c1.date_input(" ", value=date.today(), key="tsk_due", label_visibility="collapsed")
        sch = c2.selectbox(t("tsk_scheme", l), [None] + ids, key="tsk_scheme",
                           format_func=lambda i: t("tsk_none", l) if i is None else L(get_scheme(i, cat)["name"], l))
        rp = c3.selectbox(t("tsk_reminder", l), list(T.REMINDER_PREFS), index=1, key="tsk_rp", format_func=lambda k: t("rp_" + k, l))
        if st.form_submit_button(t("btn_add", l)):
            if not title.strip():
                st.error(t("tsk_need_title", l))
            else:
                T.add_task(title, desc, sch, due.isoformat() if use_due else None, rp)
                st.rerun()

    tasks = T.list_tasks()
    if not tasks:
        st.write(t("tsk_empty", l))
    for tk in tasks:
        over = T.is_overdue(tk)
        box = st.container(border=True)
        head = f"{'✅' if tk['status'] == 'done' else '🔴' if over else '🕑'} **{tk['title']}** — {t('ts_' + tk['status'], l)}"
        if over:
            head += f" · **{t('tsk_overdue', l)}**"
        box.markdown(head)
        box.caption(f"{tk['due_date'] or t('no_due_date', l)} · {tk['scheme_id'] or ''} · {t('rp_' + tk['reminder_pref'], l)}")
        if tk["description"]:
            box.write(tk["description"])
        if tk["reminder_pref"] != "none" and tk["status"] != "done":
            box.code(preview_reminder(tk, l), language=None)
            box.caption(t("rem_preview_note", l))
        if tk["status"] != "done" and box.button(t("btn_done", l), key=f"done_{tk['id']}"):
            T.complete_task(tk["id"])
            st.rerun()

    st.divider()
    st.subheader(t("app_track_head", l))
    apps = T.list_applications()
    for sid in ids:
        cur = apps.get(sid, {"status": "not_started", "next_action": ""})
        c1, c2, c3 = st.columns([2, 2, 3])
        c1.markdown(f"**{L(get_scheme(sid, cat)['name'], l)}**")
        stt = c2.selectbox(t("app_status", l), list(T.APP_STATUSES), index=T.APP_STATUSES.index(cur["status"]),
                           key=f"as_{sid}", format_func=lambda k: t("as_" + k, l))
        nxt = c3.text_input(t("app_next", l), value=cur["next_action"], key=f"an_{sid}")
        if st.button(t("btn_update", l), key=f"au_{sid}"):
            T.set_application(sid, stt, nxt)
            st.rerun()

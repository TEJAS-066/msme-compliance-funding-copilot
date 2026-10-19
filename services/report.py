"""Application-readiness report: one text file an owner can carry to a bank / Common Service Centre."""
from __future__ import annotations

from datetime import date

from core import eligibility as E
from core import profile as P
from core.catalogue import L, get_catalogue, get_scheme, list_schemes, get_source
from core.i18n import field_label, option_label, t
from services.copilot import _docs_text, _eligibility_text, _fmt_val


def readiness_report(profile: dict, confirmed: set[str], lang: str = "en", cat: dict | None = None,
                     today: date | None = None) -> str:
    cat = cat or get_catalogue()
    today = today or date.today()
    out = [t("rep_title", lang), f"{t('rep_date', lang)}: {today.isoformat()}"]
    if profile.get("is_demo"):
        out.append(t("demo_banner", lang))
    out += ["", t("rep_profile", lang), "-" * 40]
    for fld, meta in P.FIELDS.items():
        v = P.get(profile, fld)
        if v is None:
            continue
        shown = _fmt_val(fld, v, lang)
        out.append(f"- {field_label(fld, lang)}: {shown}")
    unknown = [field_label(f, lang) for f in P.FIELDS if P.get(profile, f) is None]
    if unknown:
        out.append(f"- {t('rep_unknown', lang)}: {', '.join(unknown)}")
    cls, basis = P.enterprise_class(profile, cat)
    if cls:
        out.append("- " + t("derived_class", lang, cls=option_label("cls", cls, lang), basis=t("basis_" + basis, lang)))

    results = E.evaluate_all(profile, cat)
    for sc in list_schemes(cat):
        out += ["", L(sc["name"], lang), "=" * 40, _eligibility_text(sc["id"], profile, cat, lang), "", _docs_text(sc["id"], profile, cat, lang, confirmed)]
        srcs = [get_source(s, cat) for s in sc["source_ids"]]
        out.append(t("ans_sources", lang) + ":")
        out += [f"  • {s['title']} — {s['url']} ({s['tier']}, {s['accessed']})" for s in srcs]
        if sc.get("unresolved"):
            out.append(t("sch_unresolved", lang) + ":")
            out += [f"  ? {u}" for u in sc["unresolved"]]
    out += ["", t("rep_disclaimer", lang)]
    return "\n".join(out)


def generate_pdf_dossier(profile: dict, confirmed_types: set[str], scheme_id: str,
                         cat: dict | None = None, today: date | None = None) -> bytes:
    """Generate an official, bank-ready PDF pre-application dossier for branch presentation."""
    import io
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from core.checklist import build_checklist

    cat = cat or get_catalogue()
    today = today or date.today()
    scheme = get_scheme(scheme_id, cat)
    scheme_name = L(scheme["name"], "en")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=colors.HexColor('#0B6E4F'))
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#475569'))
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=colors.HexColor('#0F172A'), spaceBefore=5, spaceAfter=2)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    cell_bold = ParagraphStyle('CellB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10)
    disclaimer_style = ParagraphStyle('Disc', parent=styles['Italic'], fontName='Helvetica-Oblique', fontSize=7, leading=9, textColor=colors.HexColor('#64748B'))

    elements = []
    elements.append(Paragraph("GOVERNMENT OF INDIA • MSME COMPLIANCE & FUNDING COPILOT", sub_style))
    elements.append(Paragraph(f"BANK LOAN PRE-APPLICATION DOSSIER — {scheme_name.upper()}", header_style))
    elements.append(Paragraph(f"Generated Date: {today.isoformat()} • Team TEJAS066 • Temenos CSR & SASTRA Hackathon 2026 • SDG 9.3", sub_style))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("SECTION A: ENTERPRISE DIGITAL TWIN & BUSINESS IDENTITY", h2_style))
    state_str = str(P.get(profile, "state") or "-")
    dist_str = str(P.get(profile, "district") or "-")
    act_str = str(P.get(profile, "activity") or "-")
    ent_str = str(P.get(profile, "entity_type") or "-")
    cls_str, _ = P.enterprise_class(profile, cat)

    profile_data = [
        [Paragraph("Parameter", cell_bold), Paragraph("Declared / Extracted Value", cell_bold), Paragraph("Verification Source", cell_bold)],
        [Paragraph("Enterprise Name", cell_style), Paragraph(str(P.get(profile, "business_name") or "-"), cell_style), Paragraph("Owner Declared", cell_style)],
        [Paragraph("Owner / Applicant", cell_style), Paragraph(str(P.get(profile, "owner_name") or "-"), cell_style), Paragraph("Owner Declared", cell_style)],
        [Paragraph("State & District", cell_style), Paragraph(f"{state_str} / {dist_str}", cell_style), Paragraph("Owner Declared", cell_style)],
        [Paragraph("Activity & Entity Type", cell_style), Paragraph(f"{act_str} ({ent_str})", cell_style), Paragraph("Owner Declared", cell_style)],
        [Paragraph("Plant & Machinery Investment", cell_style), Paragraph(P.fmt_inr(P.get(profile, "investment_inr")), cell_style), Paragraph("Owner Declared", cell_style)],
        [Paragraph("Annual Turnover", cell_style), Paragraph(P.fmt_inr(P.get(profile, "turnover_inr")), cell_style), Paragraph("Owner Declared", cell_style)],
        [Paragraph("Computed MSME Class", cell_style), Paragraph(str(cls_str or "-").capitalize(), cell_style), Paragraph("Computed (2025 Composite Rule)", cell_style)],
        [Paragraph("Loan Amount Requested", cell_style), Paragraph(P.fmt_inr(P.get(profile, "loan_needed_inr")), cell_style), Paragraph("Target Requirement", cell_style)],
        [Paragraph("Udyam Registration", cell_style), Paragraph(str(P.get(profile, "udyam_number") or P.get(profile, "udyam_status") or "-"), cell_style), Paragraph("Document Agent / Checksum", cell_style)],
        [Paragraph("GSTIN", cell_style), Paragraph(str(P.get(profile, "gstin") or P.get(profile, "gst_status") or "-"), cell_style), Paragraph("Luhn Mod-36 Validated", cell_style)],
    ]
    t1 = Table(profile_data, colWidths=[150, 190, 180])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 5))

    elements.append(Paragraph("SECTION B: STATUTORY ELIGIBILITY & RULE EVALUATION", h2_style))
    res = E.evaluate_scheme(scheme, profile, cat)
    elig_data = [
        [Paragraph("Statutory Rule / Criterion", cell_bold), Paragraph("Requirement", cell_bold), Paragraph("Your Value", cell_bold), Paragraph("Status", cell_bold)],
    ]
    for c in res.criteria:
        elig_data.append([
            Paragraph(L(c.label, "en"), cell_style),
            Paragraph(f"{c.op} {c.target}", cell_style),
            Paragraph(str(c.profile_value if c.profile_value is not None else "Unknown"), cell_style),
            Paragraph(c.status, cell_bold if c.status == E.PASS else cell_style)
        ])
    t2 = Table(elig_data, colWidths=[180, 140, 110, 90])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 5))

    elements.append(Paragraph("SECTION C: DOCUMENTATION CHECKLIST & VERIFICATION", h2_style))
    chk = build_checklist(scheme_id, profile, confirmed_types, cat=cat)
    doc_data = [
        [Paragraph("Document Name", cell_bold), Paragraph("Verification Status", cell_bold), Paragraph("Official Source Basis", cell_bold)],
    ]
    for d in chk:
        doc_data.append([
            Paragraph(L(d["name"], "en"), cell_style),
            Paragraph(d["status"].capitalize(), cell_bold if d["status"] == "confirmed" else cell_style),
            Paragraph("Official Scheme Circular" if d["verified"] else "Commonly Requested (Advisory)", cell_style)
        ])
    t3 = Table(doc_data, colWidths=[200, 120, 200])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(t3)
    elements.append(Spacer(1, 5))

    elements.append(Paragraph("SECTION D: BRANCH ENDORSEMENT & SUBMISSION SIGN-OFF", h2_style))
    applicant_name = str(P.get(profile, "owner_name") or "Applicant")
    sign_data = [
        [Paragraph("Applicant Signature: _______________________", cell_style), Paragraph("Bank Branch / CSC Seal:", cell_style)],
        [Paragraph(f"Name: {applicant_name}", cell_style), Paragraph("Reviewing Officer: _______________________", cell_style)],
        [Paragraph(f"Date: {today.isoformat()}", cell_style), Paragraph("Decision: [  ] Recommended   [  ] Query Raised", cell_style)],
    ]
    t4 = Table(sign_data, colWidths=[260, 260])
    t4.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t4)
    elements.append(Spacer(1, 4))

    elements.append(Paragraph("DISCLAIMER: This document is an application-readiness preparation aid generated by the MSME Compliance & Funding Copilot (Team TEJAS066). It is NOT an official sanction letter, an approval, or a legal guarantee. The lending bank or scheme authority retains full statutory discretion to evaluate, approve, or reject loan applications.", disclaimer_style))

    doc.build(elements)
    return buf.getvalue()


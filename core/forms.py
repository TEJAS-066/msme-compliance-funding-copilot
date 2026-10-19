"""Form assistance = a REVIEWABLE PREPARATION WORKSHEET, not the official bank form.

We have not verified any bank's actual form fields, so this lists the facts a lender
form typically needs, pre-filled ONLY from the owner's confirmed profile. Missing
facts are flagged. Nothing is submitted anywhere.
"""
from __future__ import annotations

from core import profile as P

WORKSHEET = [
    ("applicant_name", "owner_name", {"en": "Applicant / owner name", "ta": "விண்ணப்பதாரர் / உரிமையாளர் பெயர்"},
     {"en": "Full name as on your ID.", "ta": "அடையாள அட்டையில் உள்ள முழுப் பெயர்."}),
    ("business_name", "business_name", {"en": "Business / enterprise name", "ta": "தொழில் பெயர்"},
     {"en": "Same as on your Udyam certificate, if you have one.", "ta": "உத்யம் சான்றிதழில் உள்ளபடி."}),
    ("constitution", "entity_type", {"en": "Constitution (type of organisation)", "ta": "அமைப்பு வகை"},
     {"en": "Proprietorship, partnership, etc.", "ta": "தனிநபர், கூட்டாண்மை போன்றவை."}),
    ("state", "state", {"en": "State", "ta": "மாநிலம்"}, {"en": "State of the business unit.", "ta": "தொழில் அலகு உள்ள மாநிலம்."}),
    ("district", "district", {"en": "District", "ta": "மாவட்டம்"}, {"en": "District of the business unit.", "ta": "தொழில் அலகு உள்ள மாவட்டம்."}),
    ("activity", "activity", {"en": "Nature of activity", "ta": "செயல்பாட்டின் தன்மை"},
     {"en": "Manufacturing, services or trading.", "ta": "உற்பத்தி, சேவை அல்லது வர்த்தகம்."}),
    ("udyam", "udyam_number", {"en": "Udyam registration number", "ta": "உத்யம் பதிவு எண்"},
     {"en": "Lenders usually ask for it; if you don't have one, ask your bank / CSC about registering.", "ta": "கடன் நிறுவனங்கள் பொதுவாகக் கேட்கும்; இல்லையெனில் வங்கி / CSC-யிடம் பதிவு பற்றிக் கேளுங்கள்."}),
    ("gstin", "gstin", {"en": "GSTIN (if registered)", "ta": "GSTIN (பதிவு இருந்தால்)"},
     {"en": "Leave blank if you are not GST-registered.", "ta": "GST பதிவு இல்லையெனில் காலியாக விடவும்."}),
    ("investment", "investment_inr", {"en": "Investment in plant & machinery", "ta": "இயந்திர முதலீடு"},
     {"en": "Used to decide Micro / Small class.", "ta": "நுண் / சிறு வகையை முடிவு செய்ய பயன்படும்."}),
    ("turnover", "turnover_inr", {"en": "Annual turnover", "ta": "ஆண்டு வருவாய்"},
     {"en": "Latest financial year.", "ta": "சமீபத்திய நிதியாண்டு."}),
    ("loan_amount", "loan_needed_inr", {"en": "Loan amount requested", "ta": "கோரும் கடன் தொகை"},
     {"en": "Decides the MUDRA category.", "ta": "MUDRA பிரிவை முடிவு செய்கிறது."}),
]


def prepare_worksheet(profile: dict, lang: str = "en") -> list[dict]:
    rows = []
    for key, fld, label, hint in WORKSHEET:
        v = P.get(profile, fld)
        rows.append({"key": key, "field": fld, "label": label.get(lang, label["en"]), "hint": hint.get(lang, hint["en"]),
                     "value": v, "missing": v is None})
    return rows


def worksheet_text(profile: dict, scheme_name: str, lang: str = "en") -> str:
    head = {"en": f"PREPARATION WORKSHEET (not an official form) - {scheme_name}\nReview every line yourself. Nothing has been submitted.\n",
            "ta": f"தயாரிப்புப் பணித்தாள் (அதிகாரப்பூர்வ படிவம் அல்ல) - {scheme_name}\nஒவ்வொரு வரியையும் நீங்களே சரிபாருங்கள். எதுவும் சமர்ப்பிக்கப்படவில்லை.\n"}[lang]
    miss = {"en": "MISSING - please provide", "ta": "இல்லை - வழங்கவும்"}[lang]
    lines = [head]
    for r in prepare_worksheet(profile, lang):
        val = miss if r["missing"] else (P.fmt_inr(r["value"]) if P.FIELDS[r["field"]]["kind"] == "int" and r["field"] != "employees" else r["value"])
        lines.append(f"- {r['label']}: {val}\n    ({r['hint']})")
    return "\n".join(lines)

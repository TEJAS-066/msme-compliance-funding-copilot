"""Form assistance = a REVIEWABLE PREPARATION WORKSHEET, not the official bank form.

We have not verified any bank's actual form fields, so this lists the facts a lender
form typically needs, pre-filled ONLY from the owner's confirmed profile. Missing
facts are flagged. Nothing is submitted anywhere.
"""
from __future__ import annotations

from core import profile as P

WORKSHEET = [
    ("applicant_name", "owner_name",
     {"en": "Applicant / owner name", "ta": "விண்ணப்பதாரர் / உரிமையாளர் பெயர்", "hi": "आवेदक / मालिक का नाम", "te": "దరఖాస్తుదారు / యజమాని పేరు"},
     {"en": "Full name as on your ID.", "ta": "அடையாள அட்டையில் உள்ள முழுப் பெயர்.", "hi": "आपकी आईडी के अनुसार पूरा नाम।", "te": "మీ గుర్తింపు కార్డులోని పూర్తి పేరు."}),
    ("business_name", "business_name",
     {"en": "Business / enterprise name", "ta": "தொழில் பெயர்", "hi": "व्यवसाय का नाम", "te": "వ్యాపార పేరు"},
     {"en": "Same as on your Udyam certificate, if you have one.", "ta": "உத்யம் சான்றிதழில் உள்ளபடி.", "hi": "यदि आपके पास उद्यम प्रमाण पत्र है तो उसके अनुसार।", "te": "ఉద్యమ్ సర్టిఫికేట్‌లో ఉన్న విధంగా."}),
    ("constitution", "entity_type",
     {"en": "Constitution (type of organisation)", "ta": "அமைப்பு வகை", "hi": "संगठन का प्रकार", "te": "సంస్థ రకం"},
     {"en": "Proprietorship, partnership, etc.", "ta": "தனிநபர், கூட்டாண்மை போன்றவை.", "hi": "एकल स्वामित्व, साझेदारी आदि।", "te": "వ్యక్తిగత యాజమాన్యం, భాగస్వామ్యం మొదలైనవి."}),
    ("state", "state",
     {"en": "State", "ta": "மாநிலம்", "hi": "राज्य", "te": "రాష్ట్రం"},
     {"en": "State of the business unit.", "ta": "தொழில் அலகு உள்ள மாநிலம்.", "hi": "व्यवसाय इकाई का राज्य।", "te": "వ్యాపార విభాగం ఉన్న రాష్ట్రం."}),
    ("district", "district",
     {"en": "District", "ta": "மாவட்டம்", "hi": "ज़िला", "te": "జిల్లా"},
     {"en": "District of the business unit.", "ta": "தொழில் அலகு உள்ள மாவட்டம்.", "hi": "व्यवसाय इकाई का ज़िला।", "te": "వ్యాపార విభాగం ఉన్న జిల్లా."}),
    ("activity", "activity",
     {"en": "Nature of activity", "ta": "செயல்பாட்டின் தன்மை", "hi": "गतिविधि की प्रकृति", "te": "కార్యకలాపం స్వభావం"},
     {"en": "Manufacturing, services or trading.", "ta": "உற்பத்தி, சேவை அல்லது வர்த்தகம்.", "hi": "विनिर्माण, सेवाएं या व्यापार।", "te": "తయారీ, సేవలు లేదా వ్యాపారం."}),
    ("udyam", "udyam_number",
     {"en": "Udyam registration number", "ta": "உத்யம் பதிவு எண்", "hi": "उद्यम पंजीकरण संख्या", "te": "ఉద్యమ్ నమోదు సంఖ్య"},
     {"en": "Lenders usually ask for it; if you don't have one, ask your bank / CSC about registering.",
      "ta": "கடன் நிறுவனங்கள் பொதுவாகக் கேட்கும்; இல்லையெனில் வங்கி / CSC-யிடம் பதிவு பற்றிக் கேளுங்கள்.",
      "hi": "ऋणदाता आमतौर पर यह मांगते हैं; यदि आपके पास नहीं है, तो अपने बैंक / सीएससी से पूछें।",
      "te": "రుణదాతలు సాధారణంగా దీన్ని అడుగుతారు; లేకపోతే బ్యాంక్ / CSC ని సంప్రదించండి."}),
    ("gstin", "gstin",
     {"en": "GSTIN (if registered)", "ta": "GSTIN (பதிவு இருந்தால்)", "hi": "जीएसटीआईएन (यदि पंजीकृत हैं)", "te": "జీఎస్టీఐఎన్ (నమోదై ఉంటే)"},
     {"en": "Leave blank if you are not GST-registered.", "ta": "GST பதிவு இல்லையெனில் காலியாக விடவும்.", "hi": "यदि आप जीएसटी पंजीकृत नहीं हैं तो खाली छोड़ दें।", "te": "జీఎస్టీ నమోదు లేకపోతే ఖాళీగా ఉంచండి."}),
    ("investment", "investment_inr",
     {"en": "Investment in plant & machinery", "ta": "இயந்திர முதலீடு", "hi": "संयंत्र और मशीनरी में निवेश", "te": "ప్లాంట్ & యంత్రాలలో పెట్టుబడి"},
     {"en": "Used to decide Micro / Small class.", "ta": "நுண் / சிறு வகையை முடிவு செய்ய பயன்படும்.", "hi": "सूक्ष्म / लघु श्रेणी तय करने के लिए उपयोग किया जाता है।", "te": "సూక్ష్మ / చిన్న వర్గాన్ని నిర్ణయించడానికి ఉపయోగించబడుతుంది."}),
    ("turnover", "turnover_inr",
     {"en": "Annual turnover", "ta": "ஆண்டு வருவாய்", "hi": "वार्षिक कारोबार", "te": "వార్షిక టర్నోవర్"},
     {"en": "Latest financial year.", "ta": "சமீபத்திய நிதியாண்டு.", "hi": "नवीनतम वित्तीय वर्ष।", "te": "తాజా ఆర్థిక సంవత్సరం."}),
    ("loan_amount", "loan_needed_inr",
     {"en": "Loan amount requested", "ta": "கோரும் கடன் தொகை", "hi": "अनुरोधित ऋण राशि", "te": "కోరిన రుణ మొత్తం"},
     {"en": "Decides the MUDRA category.", "ta": "MUDRA பிரிவை முடிவு செய்கிறது.", "hi": "मुद्रा श्रेणी तय करता है।", "te": "ముద్ర వర్గాన్ని నిర్ణయిస్తుంది."}),
]


def prepare_worksheet(profile: dict, lang: str = "en") -> list[dict]:
    rows = []
    for key, fld, label, hint in WORKSHEET:
        v = P.get(profile, fld)
        rows.append({"key": key, "field": fld, "label": label.get(lang, label["en"]), "hint": hint.get(lang, hint["en"]),
                     "value": v, "missing": v is None})
    return rows


def worksheet_text(profile: dict, scheme_name: str, lang: str = "en") -> str:
    heads = {
        "en": f"PREPARATION WORKSHEET (not an official form) - {scheme_name}\nReview every line yourself. Nothing has been submitted.\n",
        "ta": f"தயாரிப்புப் பணித்தாள் (அதிகாரப்பூர்வ படிவம் அல்ல) - {scheme_name}\nஒவ்வொரு வரியையும் நீங்களே சரிபாருங்கள். எதுவும் சமர்ப்பிக்கப்படவில்லை.\n",
        "hi": f"तैयारी वर्कशीट (आधिकारिक फॉर्म नहीं) - {scheme_name}\nप्रत्येक पंक्ति की स्वयं समीक्षा करें। कुछ भी जमा नहीं किया गया है।\n",
        "te": f"తయారీ వర్క్‌షీట్ (అధికారిక ఫారమ్ కాదు) - {scheme_name}\nప్రతి పంక్తిని మీరే సమీక్షించండి. ఏదీ సమర్పించబడదు.\n",
    }
    misses = {
        "en": "MISSING - please provide",
        "ta": "இல்லை - வழங்கவும்",
        "hi": "लापता - कृपया प्रदान करें",
        "te": "లేదు - దయచేసి అందించండి",
    }
    head = heads.get(lang, heads["en"])
    miss = misses.get(lang, misses["en"])
    lines = [head]
    for r in prepare_worksheet(profile, lang):
        val = miss if r["missing"] else (P.fmt_inr(r["value"]) if P.FIELDS[r["field"]]["kind"] == "int" and r["field"] != "employees" else r["value"])
        lines.append(f"- {r['label']}: {val}\n    ({r['hint']})")
    return "\n".join(lines)

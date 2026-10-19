"""Business profile ("digital twin").

WHY: each field is {value, status, source}. status is 'known' or 'unknown'.
Unknown stays unknown -- the eligibility engine must never treat it as a pass.
"""
from __future__ import annotations

import copy
import json
import os
from typing import Any

from core.catalogue import get_catalogue

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# kind: str | int | select ; options only for select
FIELDS: dict[str, dict] = {
    "owner_name":      {"kind": "str",    "label": {"en": "Owner name", "ta": "உரிமையாளர் பெயர்", "hi": "मालिक का नाम", "te": "యజమాని పేరు"}},
    "business_name":   {"kind": "str",    "label": {"en": "Business name", "ta": "தொழில் பெயர்", "hi": "व्यवसाय का नाम", "te": "వ్యాపార పేరు"}},
    "state":           {"kind": "str",    "label": {"en": "State", "ta": "மாநிலம்", "hi": "राज्य", "te": "రాష్ట్రం"}},
    "district":        {"kind": "str",    "label": {"en": "District", "ta": "மாவட்டம்", "hi": "ज़िला", "te": "జిల్లా"}},
    "activity":        {"kind": "select", "label": {"en": "Business activity", "ta": "தொழில் செயல்பாடு", "hi": "व्यावसायिक गतिविधि", "te": "వ్యాపార కార్యకలాపం"},
                        "options": ["manufacturing", "services", "trading", "agriculture", "education_training"]},
    "sub_sector":      {"kind": "str",    "label": {"en": "Sector / product", "ta": "துறை / தயாரிப்பு", "hi": "क्षेत्र / उत्पाद", "te": "రంగం / ఉత్పత్తి"}},
    "entity_type":     {"kind": "select", "label": {"en": "Type of organisation", "ta": "அமைப்பு வகை", "hi": "संगठन का प्रकार", "te": "సంస్థ రకం"},
                        "options": ["proprietorship", "partnership", "llp", "private_limited", "public_limited", "shg", "educational_institution", "other"]},
    "women_led":       {"kind": "select", "label": {"en": "Women-led enterprise", "ta": "பெண்கள் தலைமையிலான தொழில்", "hi": "महिला नेतृत्व उद्यम", "te": "మహిళా నేతృత్వంలోని సంస్థ"},
                        "options": ["yes", "no"]},
    "udyam_status":    {"kind": "select", "label": {"en": "Udyam registration", "ta": "உத்யம் பதிவு", "hi": "उद्यम पंजीकरण", "te": "ఉద్యమ్ నమోదు"},
                        "options": ["registered", "not_registered"]},
    "udyam_number":    {"kind": "str",    "label": {"en": "Udyam number", "ta": "உத்யம் எண்", "hi": "उद्यम संख्या", "te": "ఉద్యమ్ సంఖ్య"}},
    "enterprise_class_declared": {"kind": "select", "label": {"en": "Enterprise class (as declared / on certificate)", "ta": "தொழில் வகை (அறிவித்தபடி / சான்றிதழில்)", "hi": "उद्यम श्रेणी (घोषित / प्रमाण पत्र के अनुसार)", "te": "సంస్థ వర్గం (ప్రకటించిన ప్రకారం / సర్టిఫికేట్‌లో)"},
                        "options": ["micro", "small", "medium"]},
    "investment_inr":  {"kind": "int",    "label": {"en": "Investment in plant & machinery (Rs)", "ta": "இயந்திர முதலீடு (₹)", "hi": "संयंत्र और मशीनरी में निवेश (₹)", "te": "ప్లాంట్ మరియు యంత్రాలలో పెట్టుబడి (₹)"}},
    "turnover_inr":    {"kind": "int",    "label": {"en": "Annual turnover (Rs)", "ta": "ஆண்டு வருவாய் (₹)", "hi": "वार्षिक कारोबार (₹)", "te": "వార్షిక టర్నోవర్ (₹)"}},
    "employees":       {"kind": "int",    "label": {"en": "Number of employees", "ta": "ஊழியர் எண்ணிக்கை", "hi": "कर्मचारियों की संख्या", "te": "ఉద్యోగుల సంఖ్య"}},
    "gst_status":      {"kind": "select", "label": {"en": "GST registration", "ta": "GST பதிவு", "hi": "जीएसटी पंजीकरण", "te": "జీఎస్టీ నమోదు"},
                        "options": ["registered", "not_registered"]},
    "gstin":           {"kind": "str",    "label": {"en": "GSTIN", "ta": "GSTIN எண்", "hi": "जीएसटीआईएन (GSTIN)", "te": "జీఎస్టీఐఎన్ (GSTIN)"}},
    "loan_needed_inr": {"kind": "int",    "label": {"en": "Loan amount needed (Rs)", "ta": "தேவையான கடன் தொகை (₹)", "hi": "आवश्यक ऋण राशि (₹)", "te": "అవసరమైన రుణ మొత్తం (₹)"}},
    "previous_tarun_repaid": {"kind": "select", "label": {"en": "MUDRA Tarun loan repayment history", "ta": "MUDRA தருண் கடன் திருப்பிச் செலுத்திய வரலாறு", "hi": "मुद्रा तरुण ऋण चुकाने का इतिहास", "te": "ముద్ర తరుణ్ రుణం తిరిగి చెల్లించిన చరిత్ర"},
                        "options": ["yes", "no"]},
}


def empty_profile() -> dict:
    return {"fields": {k: {"value": None, "status": "unknown", "source": None} for k in FIELDS}}


def load_demo_profile() -> dict:
    with open(os.path.join(DATA_DIR, "demo_profile.json"), encoding="utf-8") as f:
        raw = json.load(f)
    p = empty_profile()
    for k, v in raw["fields"].items():
        if k in p["fields"]:
            p["fields"][k] = v
    p["is_demo"] = True
    return p


def set_field(profile: dict, field: str, value: Any, source: str = "user") -> dict:
    """Return a NEW profile with the field set. None/'' => back to unknown."""
    if field not in FIELDS:
        raise KeyError(f"unknown field {field}")
    p = copy.deepcopy(profile)
    if value is None or (isinstance(value, str) and not value.strip()):
        p["fields"][field] = {"value": None, "status": "unknown", "source": None}
        return p
    kind = FIELDS[field]["kind"]
    if kind == "int":
        value = int(value)
        if value < 0:
            raise ValueError("must be >= 0")
    elif kind == "select":
        if value not in FIELDS[field]["options"]:
            raise ValueError(f"{value!r} not allowed for {field}")
    else:
        value = str(value).strip()
    p["fields"][field] = {"value": value, "status": "known", "source": source}
    # Editing the identity fields means it is no longer the synthetic demo person.
    if source != "demo" and field in ("owner_name", "business_name"):
        p["is_demo"] = False
    return p


def get(profile: dict, field: str) -> Any:
    """Value only if KNOWN, else None. This is the only read path the engine uses."""
    f = profile["fields"].get(field)
    if not f or f.get("status") != "known":
        return None
    return f.get("value")


def is_known(profile: dict, field: str) -> bool:
    return get(profile, field) is not None


def compute_class(investment: int, turnover: int, cat: dict | None = None) -> str:
    """Composite rule: an enterprise sits in a category only if it is within BOTH limits;
    exceeding either limit pushes it to the next higher category."""
    cat = cat or get_catalogue()
    lim = cat["classification"]["limits_inr"]
    for name in ("micro", "small", "medium"):
        if investment <= lim[name]["investment"] and turnover <= lim[name]["turnover"]:
            return name
    return "large"


def enterprise_class(profile: dict, cat: dict | None = None) -> tuple[str | None, str | None]:
    """Return (class, basis). basis in {'declared','computed',None}."""
    declared = get(profile, "enterprise_class_declared")
    if declared:
        return declared, "declared"
    inv, turn = get(profile, "investment_inr"), get(profile, "turnover_inr")
    if inv is not None and turn is not None:
        return compute_class(inv, turn, cat), "computed"
    return None, None


def class_mismatch(profile: dict, cat: dict | None = None) -> str | None:
    """If declared class disagrees with the class computed from numbers, return the computed class."""
    declared = get(profile, "enterprise_class_declared")
    inv, turn = get(profile, "investment_inr"), get(profile, "turnover_inr")
    if declared and inv is not None and turn is not None:
        computed = compute_class(inv, turn, cat)
        if computed != declared:
            return computed
    return None


def fmt_inr(n: int | None) -> str:
    """Indian digit grouping: 800000 -> Rs 8,00,000."""
    if n is None:
        return "-"
    s = str(int(n))
    if len(s) <= 3:
        return f"₹{s}"
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return "₹" + ",".join(parts + [tail])

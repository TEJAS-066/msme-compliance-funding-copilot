"""KPI harness.  Run:  python -m evaluation.run_eval

Measures (a) eligibility-engine overall status vs hand-derived labels and
(b) extraction of known fields from the synthetic samples. These are regression checks on
SMALL SYNTHETIC sets - not proof of real-world accuracy.
"""
import json
import os

from core import documents as D
from core import eligibility as E
from core import profile as P

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(os.path.dirname(HERE), "samples")


def _profile(base: str, overrides: dict) -> dict:
    p = P.load_demo_profile() if base == "demo" else P.empty_profile()
    for k, v in overrides.items():
        p = P.set_field(p, k, v, source="eval")
    return p


def run(cases_path: str | None = None) -> dict:
    with open(cases_path or os.path.join(HERE, "cases.json"), encoding="utf-8") as f:
        cases = json.load(f)

    e_ok = e_total = 0
    e_fail = []
    for c in cases["eligibility"]:
        res = E.evaluate_all(_profile(c["base"], c["set"]))
        for sid, want in c["expect"].items():
            e_total += 1
            got = res[sid].overall
            if got == want:
                e_ok += 1
            else:
                e_fail.append({"case": c["name"], "scheme": sid, "want": want, "got": got})

    x_ok = x_total = 0
    x_fail = []
    for c in cases["extraction"]:
        with open(os.path.join(SAMPLES, c["file"]), "rb") as f:
            r = D.extract_text(f.read(), c["file"])
        x_total += 1
        if r.extraction_status == c["status"]:
            x_ok += 1
        else:
            x_fail.append({"file": c["file"], "want": c["status"], "got": r.extraction_status})
        got_fields = {x.field: x.value for x in D.extract_fields(r.text)} if r.text else {}
        for k, v in c["fields"].items():
            x_total += 1
            if got_fields.get(k) == v:
                x_ok += 1
            else:
                x_fail.append({"file": c["file"], "field": k, "want": v, "got": got_fields.get(k)})

    return {"eligibility": {"correct": e_ok, "total": e_total, "accuracy": e_ok / e_total if e_total else 0, "failures": e_fail},
            "extraction": {"correct": x_ok, "total": x_total, "accuracy": x_ok / x_total if x_total else 0, "failures": x_fail}}


if __name__ == "__main__":
    r = run()
    for k in ("eligibility", "extraction"):
        print(f"{k}: {r[k]['correct']}/{r[k]['total']} = {r[k]['accuracy']:.0%}")
        for f in r[k]["failures"]:
            print("   FAIL", f)

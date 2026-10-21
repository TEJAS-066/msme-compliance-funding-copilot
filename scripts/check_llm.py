"""Try the REAL LLM path once and show exactly what happens (run this on a machine with internet + a key).

Run:  python scripts/check_llm.py                 # each provider that has a key
      python scripts/check_llm.py --provider gemini
It asks 3 grounded questions (English, Tamil, out-of-scope), prints the mode/guard result and the answer.
Keys are never printed. Exit code 1 if a configured provider never produced a guarded answer.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import config  # noqa: E402
from core import profile as P  # noqa: E402
from services import copilot  # noqa: E402

QUESTIONS = [("en", "Am I eligible for MUDRA?"), ("ta", "எனக்கு CGTMSE தகுதி உள்ளதா?"),
             ("en", "What is the GST rate on garments?")]
KEYS = {"anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY", "sarvam": "SARVAM_API_KEY"}


def main() -> int:
    config.load_env_file()
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=list(KEYS))
    args = ap.parse_args()
    providers = [args.provider] if args.provider else [p for p, k in KEYS.items() if config.get(k)]
    if not providers:
        print("No provider key found. App runs in deterministic demo mode - nothing to check.\nSet LLM_PROVIDER + a key in .env, then rerun.")
        return 0
    prof = P.load_demo_profile()
    bad = 0
    for prov in providers:
        os.environ["LLM_PROVIDER"] = prov
        print(f"\n==================== {prov} ====================")
        ok = 0
        for lang, q in QUESTIONS:
            a = copilot.answer(q, lang, prof)
            print(f"\nQ ({lang}): {q}\n  mode: {a.mode}   refused: {a.refused}")
            for n in a.notes:
                print("  note:", n)
            print("  answer:", a.text.replace("\n", "\n          ")[:700])
            ok += a.mode.startswith("llm:")
        print(f"\n{prov}: {ok}/{len(QUESTIONS)} answers came from the LLM and passed the guard "
              "(the out-of-scope question SHOULD be a refusal handled without the LLM).")
        if ok == 0:
            bad += 1
            print("  -> every answer fell back to demo mode: check the key, the model name (GEMINI_MODEL etc.), or the notes above.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

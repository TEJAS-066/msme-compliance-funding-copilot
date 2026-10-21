import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import config  # noqa: E402
from services.whatsapp_server import make_server  # noqa: E402

if __name__ == "__main__":
    config.load_env_file()
    port = int(os.environ.get("PORT", "8765"))
    print(f"WhatsApp webhook on http://127.0.0.1:{port}/whatsapp  (health: /health)")
    if not os.environ.get("TWILIO_AUTH_TOKEN") and os.environ.get("WA_ALLOW_UNSIGNED") != "1":
        print("NOTE: no TWILIO_AUTH_TOKEN -> requests will be refused (set WA_ALLOW_UNSIGNED=1 for local dev only).")
    make_server("0.0.0.0", port).serve_forever()

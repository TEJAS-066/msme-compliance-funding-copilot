# WhatsApp channel — what exists, how to switch it on

**Built and tested locally:** webhook logic (`services/whatsapp.py`), a stdlib HTTP server (`scripts/whatsapp_server.py`), Twilio request-signature verification (checked against Twilio's official validator), Tamil/English replies, outbound send function with honest statuses (`services/notifications.py`), and an in-app **simulator** (page "WhatsApp & voice") running the same code.
**NOT tested:** a real message from a real phone. That needs your Twilio account.

## Switch it on (≈20 min)
1. Create a Twilio account → Messaging → Try it out → *WhatsApp sandbox*. Join the sandbox from your phone (send the join code Twilio shows).
2. Put `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM` in `.env` (never commit it).
3. Terminal A: `python scripts/whatsapp_server.py` (port 8765).
4. Terminal B: expose it, e.g. `ngrok http 8765` → copy the https URL.
5. Set `PUBLIC_URL=https://<your-ngrok>/whatsapp` and restart terminal A (signature checks use this exact URL).
6. In Twilio sandbox settings set *When a message comes in* = that same URL, method POST.
7. Message “hi”, then “Am I eligible for MUDRA?” and “எனக்கு MUDRA தகுதி உள்ளதா?”.

## Rules
- With `TWILIO_AUTH_TOKEN` set, unsigned/invalid requests get HTTP 403. Without it the server refuses everything unless `WA_ALLOW_UNSIGNED=1` (local dev only).
- Demo scope: ONE shared profile (the saved app profile, else the demo profile). Never use real customer data. Per-sender profiles, consent and rate limiting are Phase 6.
- Say “Twilio accepted the message” — not “delivered” — unless you have checked the handset.

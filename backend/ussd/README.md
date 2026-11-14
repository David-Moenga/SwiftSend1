# SwiftSend USSD Integration (Africa's Talking)

USSD interface for SwiftSend, integrated into the existing Django backend (`SwiftSend1/backend`) and deployed on Railway. It reuses existing remittance/corridor/exchange-rate models and services (no duplicate transaction systems).

## Architecture

- **Gateway:** Africa's Talking (Sandbox initially), HTTP POST callbacks
- **Backend:** Existing Django app + dedicated `ussd` Django app
- **Database:** Existing PostgreSQL (Railway) / SQLite (dev), reuses `transfers` models (`Corridor`, `Remittance`, `RemittanceEvent`, `USSDSession`)
- **Settlement:** Existing Stellar integration remains separate; **initial USSD flow creates simulated/demo transactions only (no actual money movement)**

### USSD app structure

```
backend/ussd/
  __init__.py
  apps.py
  views.py        # AT callback endpoint (sessionId, serviceCode, phoneNumber, text) -> CON/END
  urls.py         # /api/ussd/ and /api/ussd/callback/
  handlers.py     # Menu/state machine and customer journey
  session.py      # Session lifecycle, TTL/expiry, safe reset, text parsing
  validators.py   # Input sanitization, phone/amount/reference/menu validation, limits
  services.py     # Bridges to existing Corridor.quote, create_remittance, status/account lookups
  tests.py        # Unit/integration tests for full USSD journey
  README.md
```

### Endpoints

- `POST /api/ussd/` (primary, dedicated app)
- `POST /api/ussd/callback/` (alias)
- `POST /api/ussd/webhook/` (compatibility path in `transfers`, delegates to USSD app)

All accept Africa's Talking form/JSON fields: `sessionId`, `serviceCode`, `phoneNumber`, `text` (and common variants). Responses are `text/plain` with `CON`/`END` prefixes. Append `?format=json` for JSON test responses.

## Customer journey (implemented)

**Welcome**
```
Welcome to SwiftSend

Send money across borders, easily.

1. Send Money
2. Exchange Rates
3. Transaction Status
4. My Account
```

- **Send Money:** destination (Nigeria/Uganda/Tanzania, resolved from active KE outbound corridors in backend) → amount in KES (numeric, >0, within limits, business rules) → exchange rate/fee/recipient quote from existing corridor pricing (`Corridor.quote`) → explicit confirmation (1 confirm / 2 cancel) → simulated transaction record with unique `SS...` reference, amount, destination, status (marked **DEMO - no actual money movement**).
- **Exchange Rates:** select destination → current rate/fee from backend corridor config (no hardcoded production rates).
- **Transaction Status:** enter reference → minimal status lookup (no sensitive data exposure).
- **My Account:** basic info associated with verified phone number (masked phone, non-sensitive summary) when linkable; otherwise safe fallback.

## Session, security & validation

- Cumulative AT `text` parsing, menu validation, numeric/KES amount validation, configurable min/max limits (`USSD_MIN_AMOUNT_KES`, `USSD_MAX_AMOUNT_KES`).
- Session TTL/expiry handling, terminal-session reset, safe restart on invalid/expired state, back (`0`) and cancel support.
- Idempotency: one simulated send per USSD session (session-scoped idempotency key + duplicate prevention).
- Explicit confirmation required before transaction creation; no money movement in sandbox.
- Webhook auth hook: optional shared secret (`USSD_WEBHOOK_SECRET` / `SWIFTSEND_INTEGRATIONS["ussd_webhook_secret"]`) via `X-SwiftSend-Signature`/`X-Webhook-Signature`/`Authorization`/payload signature; rejects unauthorized requests when configured.
- Minimal/safe logging (masked MSISDN, no raw sensitive data or secrets).

## Environment variables

Add to Railway/backend environment (never commit real keys):

```env
AT_USERNAME=sandbox
AT_API_KEY=your_sandbox_api_key
USSD_SHORTCODE=*384#
USSD_WEBHOOK_SECRET=                # optional but recommended
USSD_MIN_AMOUNT_KES=100
USSD_MAX_AMOUNT_KES=70000
```

`AT_USERNAME` and `AT_API_KEY` are read by settings for Africa's Talking integration/configuration. The callback flow works with AT Sandbox without requiring server-side outbound AT API calls; keep credentials in env for provider setup and future use.

## Africa's Talking Sandbox configuration

1. Log in to [Africa's Talking Sandbox](https://account.africastalking.com/).
2. Go to **USSD** → create/configure a channel/service code (sandbox).
3. Set the **Callback URL** to your deployed Railway HTTPS endpoint, e.g.:
   - `https://backend-production-3886.up.railway.app/api/ussd/` (recommended)
   - or `https://backend-production-3886.up.railway.app/api/ussd/webhook/` (compatibility)
4. Ensure method is **POST** (AT default) and the endpoint is publicly reachable over HTTPS.
5. Use the **USSD Simulator** in the AT sandbox to dial the service code and test.

## Testing

Run from `SwiftSend1/backend`:

```bash
.venv/bin/python manage.py test ussd transfers accounts swiftsend_api
# or only USSD
.venv/bin/python manage.py test ussd
```

Covers: welcome/destination/amount/rate/confirm/complete flow, simulated transaction creation, status lookup, invalid/empty inputs, cancel/back, duplicate prevention, callback/auth handling, and legacy webhook compatibility.

## Notes / constraints

- Reuses existing `Corridor`, `Remittance`, `RemittanceEvent`, `USSDSession`, `create_remittance`, and pricing logic; does not create duplicate transaction systems.
- Send-money destinations require active **KE → NG/UG/TZ** corridors in backend (seeded by `transfers` migration `0004_seed_ke_outbound_ussd_corridors.py` for sandbox/demo; rates are backend records/config, not hardcoded in flow logic).
- Actual money transfers, production shortcodes, and live network/provider settlement remain disabled pending approvals and production integrations. Stellar settlement stays separate from this simulated USSD milestone.

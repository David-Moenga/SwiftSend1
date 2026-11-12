# SwiftSend 7-day sprint alignment (current state)

This maps the extracted 7-day sprint plan to the current implementation in:
- `SwiftSend1/backend` (Django/DRF remittance API)
- `swiftsend-frontend` (React/Vite client)

> Status legend: **Done** = implemented in some form, **Partial** = present but gaps vs plan, **Missing** = not implemented, **Differs** = implemented differently than plan.

## Day 1 — Architecture, scope and integration setup
- **Corridor focus (KE inbound, e.g. US/UK/AE → KE):** **Done/Differs**. `Corridor` model + seed/config support multiple corridors (US-KE, UK-KE, AE-KE patterns in frontend/tests) with fees/rates/providers/USSD shortcode.
- **Provider/integration decision hooks:** **Partial**. `transfers/integrations.py` has adapter hooks and config-driven mode (`SWIFTSEND_INTEGRATIONS`), mock + Stellar Testnet-capable anchor adapter, mock payout/USSD adapters. Real anchor/on-ramp/payout provider credentials/flows still require configuration and provider-specific implementation.
- **Transfer lifecycle & statuses:** **Partial/Differs**. `Remittance` uses staged statuses (`initiated` → `on_ramp_*` → `stellar_*` → `destination_anchor_pending` → `payout_pending` → `completed`/`failed`) with `RemittanceEvent` evidence trail. Different naming/granularity than plan’s suggested lifecycle; includes audit/evidence events.
- **Env/secrets management:** **Done**. Django settings load env vars; integration config and USSD webhook secret supported; `.env.example` present.
- **Deliverable (architecture doc/diagram):** **Partial**. Code/docs exist, but no single checked-in architecture diagram/lifecycle ownership doc matching sprint artifact.

## Day 2 — Build the core remittance MVP
- **Registration/authentication:** **Done** (separate `accounts` app, JWT auth per project README/settings).
- **Recipient creation/validation:** **Missing as first-class model/UI**. Remittance stores recipient fields inline; no dedicated `Recipient` entity/list/reuse flow as planned.
- **Transfer creation / quote / history / tracking:** **Done/Partial**. Quote endpoint + create remittance + list/detail/track endpoints exist. Frontend `SendMoney`, `History`, `Track` pages wired to APIs.
- **Idempotency keys for duplicate transfer prevention:** **Partial (added)**. Backend now accepts idempotency key (header/body) to safely de-duplicate create requests; client-side adoption can be expanded.
- **Authorization checks:** **Done** for user-scoped remittance reads/mutations and withdrawals; public track/evidence by reference is intentional.
- **Plan-specific models (`Recipient`, `Quote`, `PaymentAttempt`, separate `Payout/Settlement` etc.):** **Differs**. Implemented as `Remittance` + `RemittanceEvent` + corridor quote calculation + provider refs on remittance.
- **Frontend quote/recipient/history/details:** **Partial**. Send flow shows quote and creates transfer; tracking/details+evidence exist; no dedicated recipient management screen.

## Day 3 — Stellar and Anchor integration
- **Testnet environment & adapter:** **Partial/Done (dev-ready)**. `StellarTestnetAnchorAdapter` can submit/record Stellar tx in configured mode with fallback-safe behavior; mock mode available for pilot/demo.
- **Auth with Anchor (SEP flows):** **Missing/Provider-specific**. No SEP-10/24/31 concrete implementation; adapter interfaces are placeholders for real provider APIs.
- **Tx hash/reference storage & status handling:** **Done**. `stellar_tx_hash`, anchor/on-ramp/payout refs and event evidence recorded.
- **Independent on-chain verification UX/tooling:** **Partial**. Hash stored/evidenced; UI/ops verification beyond stored refs can be improved.

## Day 4 — USSD integration
- **Gateway webhook endpoint:** **Done**. `/api/ussd/webhook/` accepts common payloads, optional shared-secret validation hook, returns CON/END text or JSON.
- **Session persistence & evidence:** **Done**. `USSDSession` stored/updated and linked to remittance when reference known.
- **Menu/flow alignment with sprint:** **Partial**. Current mock flow supports track/confirm/help; full sprint “send money” multi-step flow (amount, recipient, quote review, PIN confirmation) not fully implemented end-to-end.
- **PIN handling/rate limiting/abuse protections:** **Partial/Missing**. No PIN capture/verification; gateway-level protections not implemented in app (should be enforced by gateway/backend policy).

## Day 5 — Connect complete cross-border journey
- **Orchestrated E2E flow:** **Done (simulated/integration-hook mode)**. `services.advance_remittance` / `run_to_completion` progress through collection→settlement→payout stages with evidence events; adapters are mock/configurable.
- **Real provider collection/FX/payout confirmation:** **Missing/Config-dependent**. Requires real KES collection/UGX payout (or chosen corridor equivalents) integrations and reconciliation against real provider responses.

## Day 6 — Security, failure handling and testing
- **Idempotency/safe retries:** **Partial**. Idempotency support being added for create; advance/validate operations and provider-side idempotency need continued hardening.
- **Webhook signature verification:** **Partial**. USSD webhook supports shared-secret check; provider callback/webhook verification for payments/anchors not generalized.
- **Structured logs/audit events:** **Partial**. `RemittanceEvent` provides audit trail; broader structured logging/monitoring can be expanded.
- **Negative/edge-case test coverage:** **Partial**. Tests cover core remittance/evidence/USSD basics and withdrawals; more failure/expiry/unauthorized/duplicate cases needed per sprint checklist.

## Day 7 — Final integration, deployment and demonstration
- **Deployment/config readiness:** **Partial**. Settings support env/prod patterns; deployment artifacts exist in repos, but end-to-end deployed demo readiness depends on target environment/provider credentials.
- **Documentation:** **Partial**. READMEs/tests/evidence endpoints exist; sprint-specific runbook/demo script and limitation statements can be tightened.

## Recommended next implementation steps (aligned to sprint)
1. **Harden Day 2 semantics:** expand idempotency usage in frontend, add recipient management (optional model or lightweight saved recipients), and improve transfer history/details UX.
2. **Complete Day 4 USSD send flow:** stateful multi-step menu (corridor/amount/recipient/quote/confirm), secure confirmation strategy, and stronger session validation.
3. **Provider integration readiness:** concrete adapter contracts/config validation for anchor/on-ramp/payout, webhook verification, and reconciliation checks.
4. **Testing (Day 6):** add tests for idempotency, duplicate callbacks, unauthorized access, invalid transitions, and simulated failure paths.
5. **Ops/demo (Day 7):** one-command seed/demo script, evidence checklist, and explicit simulated-vs-real capability reporting.

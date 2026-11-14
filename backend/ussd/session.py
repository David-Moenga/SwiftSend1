"""USSD session management (state, expiry, navigation safety)."""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from transfers.models import USSDSession

from .validators import mask_msisdn, normalize_phone, sanitize_text

# Africa's Talking sessions are short-lived; keep a conservative TTL.
SESSION_TTL_SECONDS = 120
MAX_INPUT_LEN = 160
MAX_TEXT_PARTS = 30


def parse_text(text: str | None) -> list[str]:
    raw = sanitize_text(text)
    if not raw:
        return []
    # Africa's Talking sends cumulative input joined by '*'
    parts = [p.strip() for p in raw.split("*")]
    # Keep empty segments out; AT can include them in some cases.
    parts = [p for p in parts if p != ""]
    return parts[:MAX_TEXT_PARTS]


def current_input(text: str | None) -> str:
    parts = parse_text(text)
    return parts[-1] if parts else ""


def is_back(value: str) -> bool:
    return sanitize_text(value) == "0"


def is_expired(session: USSDSession) -> bool:
    if not session.updated_at:
        return False
    return timezone.now() - session.updated_at > timedelta(seconds=SESSION_TTL_SECONDS)


def get_or_start_session(*, session_id: str, shortcode: str, msisdn: str, network: str, text: str):
    """Load existing session or create/reset as needed.

    Returns (session, is_new_interaction).
    Expired or terminal sessions are reset to start to avoid invalid reuse.
    """
    safe_text = sanitize_text(text)[:MAX_INPUT_LEN]
    phone = normalize_phone(msisdn)
    masked = mask_msisdn(phone)

    session = USSDSession.objects.filter(session_external_id=session_id).order_by("-updated_at").first()
    parts = parse_text(safe_text)
    new_interaction = len(parts) == 0

    if session is None:
        session = USSDSession.objects.create(
            session_external_id=session_id,
            shortcode=shortcode or "*384#",
            msisdn_masked=masked or "unknown",
            network=sanitize_text(network),
            input_text=safe_text,
            state="welcome",
            status=USSDSession.Status.ACTIVE,
            metadata={},
        )
        return session, True

    # Reset on expiry or terminal states (safe re-entry).
    terminal = session.status in (USSDSession.Status.COMPLETED, USSDSession.Status.CANCELLED, USSDSession.Status.FAILED)
    if is_expired(session) or terminal or session.state == "expired":
        session.state = "welcome"
        session.status = USSDSession.Status.ACTIVE
        session.metadata = {}
        session.remittance = None
        session.last_response = ""
        # treat as fresh only if user just dialed in
        if not new_interaction:
            # user sent input after expiry; force restart on this request
            session.metadata["expired_restart"] = True

    session.shortcode = shortcode or session.shortcode or "*384#"
    if masked and (not session.msisdn_masked or session.msisdn_masked.strip("*") == ""):
        session.msisdn_masked = masked
    elif masked and session.msisdn_masked == "unknown":
        session.msisdn_masked = masked
    session.network = sanitize_text(network) or session.network
    session.input_text = safe_text
    session.save()
    return session, new_interaction


def end_session(session: USSDSession, status=USSDSession.Status.COMPLETED):
    session.status = status
    session.save(update_fields=["status", "updated_at"])


def cancel_session(session: USSDSession):
    session.status = USSDSession.Status.CANCELLED
    session.state = "cancelled"
    session.metadata = {}
    session.save(update_fields=["status", "state", "metadata", "updated_at"])

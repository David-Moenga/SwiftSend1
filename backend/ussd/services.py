"""USSD service layer bridging to existing SwiftSend business logic."""

from __future__ import annotations

import logging
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

from transfers.models import Corridor, Remittance, USSDSession
from transfers.services import create_remittance, record_event

from .validators import mask_msisdn, normalize_phone

logger = logging.getLogger(__name__)
User = get_user_model()

# Brief-specified destinations for Kenya-origin send flow.
SEND_DESTINATIONS = [
    {"key": "NG", "label": "Nigeria", "currency": "NGN"},
    {"key": "UG", "label": "Uganda", "currency": "UGX"},
    {"key": "TZ", "label": "Tanzania", "currency": "TZS"},
]


def get_send_destinations():
    """Return destination options with resolved corridors where possible.

    Looks up active corridors from Kenya (KE/KES) to requested destination.
    """
    options = []
    for dest in SEND_DESTINATIONS:
        corridor = (
            Corridor.objects.filter(is_active=True, send_country__iexact="KE", receive_country__iexact=dest["key"])
            .order_by("code")
            .first()
        )
        options.append({**dest, "corridor": corridor})
    return options


def get_destination_corridor(receive_country: str):
    return (
        Corridor.objects.filter(is_active=True, send_country__iexact="KE", receive_country__iexact=receive_country)
        .order_by("code")
        .first()
    )


def get_quote_for_corridor(corridor: Corridor, amount_kes: Decimal):
    # Reuse existing transparent pricing logic.
    return corridor.quote(amount_kes)


def find_user_by_phone(msisdn: str):
    """Best-effort lookup without exposing sensitive info.

    Existing user model may not store phone numbers; try common fields safely.
    """
    phone = normalize_phone(msisdn)
    if not phone:
        return None
    # Try exact/common field names if present in custom user models.
    for field in ("phone_number", "phone", "msisdn", "mobile", "mobile_number"):
        try:
            if field in {f.name for f in User._meta.get_fields()}:
                user = User.objects.filter(**{field: phone}).first()
                if user:
                    return user
        except Exception:
            continue
    # Fallback: match sender_contact on prior remittances tied to a user (verified via prior activity).
    rem = (
        Remittance.objects.filter(owner__isnull=False)
        .filter(Q(sender_contact=phone) | Q(sender_contact=phone.lstrip("+")))
        .select_related("owner")
        .order_by("-created_at")
        .first()
    )
    return rem.owner if rem else None


def get_account_summary(msisdn: str) -> dict:
    user = find_user_by_phone(msisdn)
    masked = mask_msisdn(msisdn)
    if not user:
        return {
            "found": False,
            "masked_phone": masked,
            "message": "No verified account linked to this number.",
        }
    # Basic, non-sensitive info only.
    rem_qs = Remittance.objects.filter(owner=user)
    recent = rem_qs.order_by("-created_at").first()
    return {
        "found": True,
        "masked_phone": masked,
        "name": (user.get_full_name() or "SwiftSend user").split(" ")[0],
        "total_transactions": rem_qs.count(),
        "last_reference": recent.reference if recent else None,
        "last_status": recent.status if recent else None,
    }


def get_transaction_status(reference: str, msisdn: str | None = None) -> dict | None:
    """Lookup minimal status info for a reference.

    Reference knowledge acts as the lookup key; we return minimal fields only.
    """
    if not reference:
        return None
    rem = Remittance.objects.select_related("corridor").filter(reference__iexact=reference).first()
    if not rem:
        return None
    return {
        "reference": rem.reference,
        "status": rem.status,
        "send_amount": str(rem.send_amount),
        "send_currency": rem.send_currency,
        "receive_amount": str(rem.receive_amount),
        "receive_currency": rem.receive_currency,
        "destination": rem.recipient_country,
        "created_at": rem.created_at.isoformat() if rem.created_at else None,
        "is_demo": bool((rem.metadata or {}).get("demo") or (rem.metadata or {}).get("simulated")),
    }


@transaction.atomic
def create_simulated_ussd_remittance(*, session: USSDSession, corridor: Corridor, amount_kes: Decimal, msisdn: str):
    """Create a simulated remittance record (no actual money movement).

    Reuses existing transaction model and create_remittance service.
    Uses session-scoped idempotency to prevent duplicates.
    """
    idem = f"ussd:{session.session_external_id}:send"
    # Avoid duplicate submission for same session.
    existing = Remittance.objects.filter(
        idempotency_key=idem,
        channel=Remittance.Channel.USSD,
    ).first()
    if existing and existing.ussd_sessions.filter(pk=session.pk).exists() or existing and session.remittance_id == existing.id:
        return existing, False

    validated = {
        "channel": Remittance.Channel.USSD,
        "sender_name": f"USSD {mask_msisdn(msisdn)}",
        "sender_contact": normalize_phone(msisdn),
        "sender_country": corridor.send_country,
        "recipient_name": "USSD Recipient (Demo)",
        "recipient_contact": "pending",
        "recipient_country": corridor.receive_country,
        "recipient_payout_method": "mobile_money",
        "send_amount": amount_kes,
        "idempotency_key": idem,
    }
    remittance, created = create_remittance(owner=None, corridor=corridor, validated=validated, idempotency_key=idem)
    if created:
        meta = dict(remittance.metadata or {})
        meta.update({"simulated": True, "demo": True, "channel": "ussd", "sandbox": True, "note": "Simulated USSD transaction - no actual money movement."})
        remittance.metadata = meta
        remittance.save(update_fields=["metadata", "updated_at"])
        record_event(
            remittance,
            stage="ussd_simulated",
            provider="africastalking-sandbox",
            channel="ussd",
            external_reference=session.session_external_id,
            message="Simulated USSD remittance created (sandbox). No actual money movement initiated.",
            payload={"simulated": True, "msisdn_masked": mask_msisdn(msisdn)},
        )
    return remittance, created


def has_recent_duplicate(session: USSDSession) -> bool:
    """Idempotency guard: one send per active session."""
    return bool(session.remittance_id)

"""E2E remittance flow orchestration with evidence hooks (Deliverable 3)."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from .integrations import get_anchor_adapter, get_payout_adapter
from .models import Remittance, RemittanceEvent


class FlowError(Exception):
    pass


def record_event(remittance, *, stage, result=RemittanceEvent.Result.OK, provider="", stellar_tx_hash="",
                 external_reference="", message="", payload=None, channel=""):
    return RemittanceEvent.objects.create(
        remittance=remittance,
        stage=stage,
        result=result,
        provider=provider,
        channel=channel or remittance.channel,
        stellar_tx_hash=stellar_tx_hash or "",
        external_reference=external_reference or "",
        message=message or "",
        payload=payload or {},
    )


@transaction.atomic
def create_remittance(*, owner, corridor, validated, idempotency_key=""):
    key = (idempotency_key or validated.get("idempotency_key") or "").strip()
    if key and owner:
        existing = Remittance.objects.select_for_update().filter(owner=owner, idempotency_key=key).first()
        if existing:
            return existing, False

    quote = corridor.quote(validated["send_amount"])
    remittance = Remittance.objects.create(
        owner=owner,
        corridor=corridor,
        channel=validated.get("channel") or Remittance.Channel.WEB,
        sender_name=validated["sender_name"],
        sender_contact=validated.get("sender_contact", ""),
        sender_country=validated.get("sender_country") or corridor.send_country,
        recipient_name=validated["recipient_name"],
        recipient_contact=validated["recipient_contact"],
        recipient_country=validated.get("recipient_country") or corridor.receive_country,
        recipient_payout_method=validated.get("recipient_payout_method") or "mobile_money",
        send_amount=quote["send_amount"],
        send_currency=quote["send_currency"],
        fee_amount=quote["fee_amount"],
        exchange_rate=quote["exchange_rate"],
        receive_amount=quote["receive_amount"],
        receive_currency=quote["receive_currency"],
        status=Remittance.Status.INITIATED,
        metadata={"quote": quote, "pricing_transparent": True},
        idempotency_key=key,
    )
    record_event(
        remittance,
        stage=Remittance.Status.INITIATED,
        message="Remittance initiated; transparent quote captured.",
        payload=quote,
        provider="swiftsend",
    )
    return remittance, True


@transaction.atomic
def advance_remittance(remittance: Remittance) -> Remittance:
    """Advance one E2E step using configured adapters; records evidence per step.

    Safe for pilot/validation: in mock mode this produces verifiable evidence
    records (including a mock Stellar tx hash). Real adapters plug in via config.
    """
    remittance = Remittance.objects.select_for_update().get(pk=remittance.pk)
    if remittance.status in (Remittance.Status.COMPLETED, Remittance.Status.FAILED):
        return remittance

    anchor = get_anchor_adapter()
    payout = get_payout_adapter()

    try:
        if remittance.status == Remittance.Status.INITIATED:
            remittance.status = Remittance.Status.ON_RAMP_PENDING
            remittance.save(update_fields=["status", "updated_at"])
            record_event(remittance, stage=remittance.status, message="Awaiting on-ramp confirmation.", result=RemittanceEvent.Result.PENDING)

        elif remittance.status == Remittance.Status.ON_RAMP_PENDING:
            res = anchor.confirm_on_ramp(remittance)
            _apply_result(remittance, res, Remittance.Status.ON_RAMP_CONFIRMED, "on_ramp_reference")

        elif remittance.status == Remittance.Status.ON_RAMP_CONFIRMED:
            res = anchor.submit_stellar(remittance)
            _apply_result(remittance, res, Remittance.Status.STELLAR_SUBMITTED, "anchor_reference")
            if res.stellar_tx_hash:
                remittance.stellar_tx_hash = res.stellar_tx_hash
                remittance.save(update_fields=["stellar_tx_hash", "updated_at"])

        elif remittance.status == Remittance.Status.STELLAR_SUBMITTED:
            res = anchor.settle_stellar(remittance)
            _apply_result(remittance, res, Remittance.Status.STELLAR_SETTLED, "anchor_reference")
            if res.stellar_tx_hash:
                remittance.stellar_tx_hash = res.stellar_tx_hash
                remittance.save(update_fields=["stellar_tx_hash", "updated_at"])

        elif remittance.status == Remittance.Status.STELLAR_SETTLED:
            remittance.status = Remittance.Status.DESTINATION_ANCHOR_PENDING
            remittance.save(update_fields=["status", "updated_at"])
            record_event(remittance, stage=remittance.status, message="Destination anchor processing settlement.", result=RemittanceEvent.Result.PENDING,
                         provider=remittance.corridor.anchor_provider)

        elif remittance.status == Remittance.Status.DESTINATION_ANCHOR_PENDING:
            remittance.status = Remittance.Status.PAYOUT_PENDING
            remittance.save(update_fields=["status", "updated_at"])
            record_event(remittance, stage=remittance.status, message="Local KES payout pending.", result=RemittanceEvent.Result.PENDING,
                         provider=remittance.corridor.payout_provider)

        elif remittance.status == Remittance.Status.PAYOUT_PENDING:
            res = payout.send_payout(remittance)
            _apply_result(remittance, res, Remittance.Status.COMPLETED, "payout_reference")
            if remittance.status == Remittance.Status.COMPLETED:
                remittance.completed_at = timezone.now()
                remittance.save(update_fields=["completed_at", "updated_at"])

    except Exception as exc:
        remittance.status = Remittance.Status.FAILED
        remittance.failure_reason = str(exc)
        remittance.save(update_fields=["status", "failure_reason", "updated_at"])
        record_event(remittance, stage=remittance.status, result=RemittanceEvent.Result.FAILED, message=str(exc))
    return remittance


def _apply_result(remittance, res, next_status, ref_field):
    if not res.ok:
        raise FlowError(res.message or "Integration step failed")
    setattr(remittance, ref_field, res.reference or getattr(remittance, ref_field))
    remittance.status = next_status
    remittance.save(update_fields=[ref_field, "status", "updated_at"])
    record_event(
        remittance,
        stage=next_status,
        result=RemittanceEvent.Result.OK,
        provider=res.provider,
        stellar_tx_hash=res.stellar_tx_hash,
        external_reference=res.reference,
        message=res.message,
        payload=res.evidence_payload(),
    )


def run_to_completion(remittance: Remittance, max_steps: int = 12) -> Remittance:
    for _ in range(max_steps):
        before = remittance.status
        remittance = advance_remittance(remittance)
        remittance.refresh_from_db()
        if remittance.status in (Remittance.Status.COMPLETED, Remittance.Status.FAILED) or remittance.status == before:
            break
    return remittance


def build_evidence_report(remittance: Remittance) -> dict:
    events = list(remittance.events.all())
    return {
        "deliverable": "Deliverable 3 - End-to-End Kenya Corridor Validation",
        "reference": remittance.reference,
        "status": remittance.status,
        "channel": remittance.channel,
        "corridor": {
            "code": remittance.corridor.code,
            "name": remittance.corridor.name,
            "route": f"{remittance.sender_country}/{remittance.send_currency} -> {remittance.recipient_country}/{remittance.receive_currency}",
            "anchor_provider": remittance.corridor.anchor_provider,
            "on_ramp_provider": remittance.corridor.on_ramp_provider,
            "payout_provider": remittance.corridor.payout_provider,
            "ussd_shortcode": remittance.corridor.ussd_shortcode,
        },
        "transfer": {
            "sender": {"name": remittance.sender_name, "country": remittance.sender_country},
            "recipient": {"name": remittance.recipient_name, "country": remittance.recipient_country, "contact": remittance.recipient_contact},
            "send_amount": str(remittance.send_amount),
            "send_currency": remittance.send_currency,
            "fee_amount": str(remittance.fee_amount),
            "exchange_rate": str(remittance.exchange_rate),
            "receive_amount": str(remittance.receive_amount),
            "receive_currency": remittance.receive_currency,
            "pricing_transparent": True,
        },
        "verification": {
            "stellar_tx_hash": remittance.stellar_tx_hash,
            "on_ramp_reference": remittance.on_ramp_reference,
            "anchor_reference": remittance.anchor_reference,
            "payout_reference": remittance.payout_reference,
            "completed_at": remittance.completed_at.isoformat() if remittance.completed_at else None,
        },
        "progress": remittance.progress,
        "events": [
            {
                "stage": e.stage,
                "result": e.result,
                "provider": e.provider,
                "channel": e.channel,
                "stellar_tx_hash": e.stellar_tx_hash,
                "external_reference": e.external_reference,
                "message": e.message,
                "payload": e.payload,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
        "ussd_sessions": [
            {
                "shortcode": s.shortcode,
                "session_external_id": s.session_external_id,
                "msisdn_masked": s.msisdn_masked,
                "state": s.state,
                "status": s.status,
                "created_at": s.created_at.isoformat(),
            }
            for s in remittance.ussd_sessions.all()
        ],
        "limitations": [] if remittance.corridor.anchor_provider else [
            "Running in app-side mock/integration mode until real anchor, on-ramp, and KES payout provider credentials are configured.",
            "Stellar tx hashes in mock mode are deterministic evidence placeholders, not on-chain transactions.",
        ],
    }

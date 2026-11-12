import secrets
import string
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Withdrawal(models.Model):
    class Method(models.TextChoices):
        BANK = "bank", "Bank transfer"
        MOBILE = "mobile", "Mobile money"
        CRYPTO = "crypto", "Cryptocurrency"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        PAID = "paid", "Paid"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="withdrawals",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    method = models.CharField(max_length=16, choices=Method.choices)
    account_details = models.CharField(max_length=255)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Withdrawal {self.pk} for {self.owner_id}"


def generate_reference(prefix="SS"):
    alphabet = string.ascii_uppercase + string.digits
    return f"{prefix}{''.join(secrets.choice(alphabet) for _ in range(10))}"


class Corridor(models.Model):
    """Configured remittance corridor (Deliverable 1: app-side integration config)."""

    code = models.SlugField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    send_country = models.CharField(max_length=2, help_text="ISO 3166-1 alpha-2 sender country")
    send_currency = models.CharField(max_length=3)
    receive_country = models.CharField(max_length=2, default="KE")
    receive_currency = models.CharField(max_length=3, default="KES")
    anchor_provider = models.CharField(max_length=120, blank=True)
    on_ramp_provider = models.CharField(max_length=120, blank=True)
    payout_provider = models.CharField(max_length=120, blank=True)
    ussd_shortcode = models.CharField(max_length=16, blank=True, default="*384#")
    fee_flat = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    exchange_rate = models.DecimalField(
        max_digits=18, decimal_places=8, default=Decimal("1.00000000"),
        help_text="Units of receive currency per 1 send currency (transparent pricing).",
    )
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["send_country", "code"]

    def __str__(self):
        return f"{self.code} ({self.send_currency}->{self.receive_currency})"

    def quote(self, send_amount):
        amount = Decimal(str(send_amount))
        fee = (self.fee_flat + (amount * self.fee_percent / Decimal("100"))).quantize(Decimal("0.01"))
        net_send = amount - fee
        if net_send < 0:
            net_send = Decimal("0.00")
        receive_amount = (net_send * self.exchange_rate).quantize(Decimal("0.01"))
        return {
            "send_amount": str(amount.quantize(Decimal("0.01"))),
            "send_currency": self.send_currency,
            "fee_amount": str(fee),
            "fee_currency": self.send_currency,
            "exchange_rate": str(self.exchange_rate),
            "net_send_amount": str(net_send.quantize(Decimal("0.01"))),
            "receive_amount": str(receive_amount),
            "receive_currency": self.receive_currency,
            "pricing_transparent": True,
            "corridor": self.code,
        }


class Remittance(models.Model):
    class Channel(models.TextChoices):
        WEB = "web", "Web"
        MOBILE = "mobile", "Mobile"
        USSD = "ussd", "USSD"

    class Status(models.TextChoices):
        INITIATED = "initiated", "Initiated"
        ON_RAMP_PENDING = "on_ramp_pending", "On-ramp pending"
        ON_RAMP_CONFIRMED = "on_ramp_confirmed", "On-ramp confirmed"
        STELLAR_SUBMITTED = "stellar_submitted", "Stellar submitted"
        STELLAR_SETTLED = "stellar_settled", "Stellar settled"
        DESTINATION_ANCHOR_PENDING = "destination_anchor_pending", "Destination anchor pending"
        PAYOUT_PENDING = "payout_pending", "KES payout pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    # Ordered E2E stages for Deliverable 3 validation
    STAGE_ORDER = [
        Status.INITIATED,
        Status.ON_RAMP_PENDING,
        Status.ON_RAMP_CONFIRMED,
        Status.STELLAR_SUBMITTED,
        Status.STELLAR_SETTLED,
        Status.DESTINATION_ANCHOR_PENDING,
        Status.PAYOUT_PENDING,
        Status.COMPLETED,
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="remittances", null=True, blank=True,
    )
    corridor = models.ForeignKey(Corridor, on_delete=models.PROTECT, related_name="remittances")
    reference = models.CharField(max_length=32, unique=True, default=generate_reference, db_index=True)
    channel = models.CharField(max_length=16, choices=Channel.choices, default=Channel.WEB)

    sender_name = models.CharField(max_length=120)
    sender_contact = models.CharField(max_length=120, blank=True)
    sender_country = models.CharField(max_length=2)
    recipient_name = models.CharField(max_length=120)
    recipient_contact = models.CharField(max_length=120)
    recipient_country = models.CharField(max_length=2, default="KE")
    recipient_payout_method = models.CharField(max_length=64, default="mobile_money")

    send_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    send_currency = models.CharField(max_length=3)
    fee_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal("1.00000000"))
    receive_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    receive_currency = models.CharField(max_length=3, default="KES")

    status = models.CharField(max_length=32, choices=Status.choices, default=Status.INITIATED, db_index=True)
    stellar_tx_hash = models.CharField(max_length=128, blank=True)
    on_ramp_reference = models.CharField(max_length=128, blank=True)
    anchor_reference = models.CharField(max_length=128, blank=True)
    payout_reference = models.CharField(max_length=128, blank=True)
    failure_reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=128, blank=True, default="", db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "idempotency_key"],
                condition=~models.Q(idempotency_key=""),
                name="uniq_remittance_owner_idempotency_key",
            )
        ]

    def __str__(self):
        return f"{self.reference} {self.status}"

    @property
    def progress(self):
        order = [s for s in self.STAGE_ORDER]
        if self.status == self.Status.FAILED:
            return {"stages": [s.value for s in order], "current": self.status, "failed": True}
        try:
            idx = order.index(self.status)
        except ValueError:
            idx = 0
        return {
            "stages": [s.value for s in order],
            "current": self.status,
            "completed_stages": [s.value for s in order[: idx + 1]],
            "failed": False,
        }


class RemittanceEvent(models.Model):
    """Evidence hook for Deliverable 3: records every E2E step with verifiable refs."""

    class Result(models.TextChoices):
        PENDING = "pending", "Pending"
        OK = "ok", "OK"
        FAILED = "failed", "Failed"

    remittance = models.ForeignKey(Remittance, on_delete=models.CASCADE, related_name="events")
    stage = models.CharField(max_length=32)
    result = models.CharField(max_length=16, choices=Result.choices, default=Result.OK)
    provider = models.CharField(max_length=120, blank=True)
    channel = models.CharField(max_length=16, blank=True)
    stellar_tx_hash = models.CharField(max_length=128, blank=True)
    external_reference = models.CharField(max_length=128, blank=True)
    message = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.remittance.reference}:{self.stage}:{self.result}"


class USSDSession(models.Model):
    """Deliverable 2 (app-side hook): USSD *384# access pilot sessions."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        FAILED = "failed", "Failed"

    shortcode = models.CharField(max_length=16, default="*384#")
    session_external_id = models.CharField(max_length=128, db_index=True)
    msisdn_masked = models.CharField(max_length=32)
    network = models.CharField(max_length=64, blank=True)
    input_text = models.TextField(blank=True)
    state = models.CharField(max_length=64, default="start")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    remittance = models.ForeignKey(
        Remittance, on_delete=models.SET_NULL, null=True, blank=True, related_name="ussd_sessions",
    )
    last_response = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"USSD {self.shortcode} {self.session_external_id} ({self.status})"

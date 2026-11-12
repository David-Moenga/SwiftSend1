from decimal import Decimal
from rest_framework import serializers

from .models import Corridor, Remittance, RemittanceEvent, USSDSession, Withdrawal


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ("id", "amount", "method", "account_details", "status", "created_at")
        read_only_fields = ("id", "status", "created_at")


class CorridorSerializer(serializers.ModelSerializer):
    route = serializers.SerializerMethodField()

    class Meta:
        model = Corridor
        fields = (
            "id", "code", "name", "send_country", "send_currency", "receive_country", "receive_currency",
            "anchor_provider", "on_ramp_provider", "payout_provider", "ussd_shortcode",
            "fee_flat", "fee_percent", "exchange_rate", "is_active", "route",
        )

    def get_route(self, obj):
        return f"{obj.send_country}/{obj.send_currency} -> {obj.receive_country}/{obj.receive_currency}"


class QuoteSerializer(serializers.Serializer):
    corridor = serializers.SlugField()
    send_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))


class RemittanceEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RemittanceEvent
        fields = (
            "stage", "result", "provider", "channel", "stellar_tx_hash",
            "external_reference", "message", "payload", "created_at",
        )


class USSDSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = USSDSession
        fields = (
            "shortcode", "session_external_id", "msisdn_masked", "network", "state",
            "status", "last_response", "metadata", "created_at", "updated_at",
        )


class RemittanceSerializer(serializers.ModelSerializer):
    corridor_code = serializers.CharField(source="corridor.code", read_only=True)
    corridor_name = serializers.CharField(source="corridor.name", read_only=True)
    progress = serializers.ReadOnlyField()
    events = RemittanceEventSerializer(many=True, read_only=True)
    ussd_sessions = USSDSessionSerializer(many=True, read_only=True)

    class Meta:
        model = Remittance
        fields = (
            "id", "reference", "channel", "status", "corridor", "corridor_code", "corridor_name",
            "sender_name", "sender_contact", "sender_country",
            "recipient_name", "recipient_contact", "recipient_country", "recipient_payout_method",
            "send_amount", "send_currency", "fee_amount", "exchange_rate", "receive_amount", "receive_currency",
            "stellar_tx_hash", "on_ramp_reference", "anchor_reference", "payout_reference",
            "failure_reason", "metadata", "progress", "events", "ussd_sessions",
            "created_at", "updated_at", "completed_at",
        )
        read_only_fields = (
            "id", "reference", "status", "corridor_code", "corridor_name",
            "send_currency", "fee_amount", "exchange_rate", "receive_amount", "receive_currency",
            "stellar_tx_hash", "on_ramp_reference", "anchor_reference", "payout_reference",
            "failure_reason", "metadata", "progress", "events", "ussd_sessions",
            "created_at", "updated_at", "completed_at",
        )


class RemittanceCreateSerializer(serializers.Serializer):
    corridor = serializers.SlugField()
    channel = serializers.ChoiceField(choices=Remittance.Channel.choices, default=Remittance.Channel.WEB)
    sender_name = serializers.CharField(max_length=120)
    sender_contact = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")
    sender_country = serializers.CharField(max_length=2, required=False, allow_blank=True)
    recipient_name = serializers.CharField(max_length=120)
    recipient_contact = serializers.CharField(max_length=120)
    recipient_country = serializers.CharField(max_length=2, required=False, default="KE")
    recipient_payout_method = serializers.CharField(max_length=64, required=False, default="mobile_money")
    send_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    idempotency_key = serializers.CharField(max_length=128, required=False, allow_blank=True, default="")


class USSDWebhookSerializer(serializers.Serializer):
    # Common aggregator fields (app-side hook; maps what's available)
    sessionId = serializers.CharField(required=False, allow_blank=True, default="")
    session_id = serializers.CharField(required=False, allow_blank=True, default="")
    serviceCode = serializers.CharField(required=False, allow_blank=True, default="")
    shortcode = serializers.CharField(required=False, allow_blank=True, default="")
    phoneNumber = serializers.CharField(required=False, allow_blank=True, default="")
    msisdn = serializers.CharField(required=False, allow_blank=True, default="")
    text = serializers.CharField(required=False, allow_blank=True, default="")
    networkCode = serializers.CharField(required=False, allow_blank=True, default="")
    network = serializers.CharField(required=False, allow_blank=True, default="")

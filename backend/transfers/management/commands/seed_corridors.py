from decimal import Decimal

from django.core.management.base import BaseCommand

from transfers.models import Corridor


CORRIDORS = [
    {
        "code": "UK-KE",
        "name": "United Kingdom → Kenya",
        "send_country": "GB",
        "send_currency": "GBP",
        "receive_country": "KE",
        "receive_currency": "KES",
        "fee_flat": Decimal("2.99"),
        "fee_percent": Decimal("0.50"),
        "exchange_rate": Decimal("162.50000000"),
        "ussd_shortcode": "*384#",
        "on_ramp_provider": "mock-onramp",
        "anchor_provider": "stellar-testnet-anchor",
        "payout_provider": "mock-kes-payout",
    },
    {
        "code": "US-KE",
        "name": "United States → Kenya",
        "send_country": "US",
        "send_currency": "USD",
        "receive_country": "KE",
        "receive_currency": "KES",
        "fee_flat": Decimal("2.50"),
        "fee_percent": Decimal("0.40"),
        "exchange_rate": Decimal("129.80000000"),
        "ussd_shortcode": "*384#",
        "on_ramp_provider": "mock-onramp",
        "anchor_provider": "stellar-testnet-anchor",
        "payout_provider": "mock-kes-payout",
    },
    {
        "code": "AE-KE",
        "name": "United Arab Emirates → Kenya",
        "send_country": "AE",
        "send_currency": "AED",
        "receive_country": "KE",
        "receive_currency": "KES",
        "fee_flat": Decimal("2.75"),
        "fee_percent": Decimal("0.45"),
        "exchange_rate": Decimal("35.32000000"),
        "ussd_shortcode": "*384#",
        "on_ramp_provider": "mock-onramp",
        "anchor_provider": "stellar-testnet-anchor",
        "payout_provider": "mock-kes-payout",
    },
]


class Command(BaseCommand):
    help = "Seed SwiftSend Kenya corridors (UK/US/UAE -> KE)."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for data in CORRIDORS:
            obj, was_created = Corridor.objects.update_or_create(code=data["code"], defaults=data)
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Corridors seeded: {created} created, {updated} updated."))

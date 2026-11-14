from decimal import Decimal

from django.db import migrations


def seed_ke_outbound_corridors(apps, schema_editor):
    Corridor = apps.get_model("transfers", "Corridor")
    # Demo/sandbox corridors for USSD send flow (Kenya -> destinations).
    # Rates/fees are configurable records in backend (not hardcoded in app logic).
    defaults = [
        dict(
            code="KE-NG",
            name="Kenya to Nigeria (NGN)",
            send_country="KE",
            send_currency="KES",
            receive_country="NG",
            receive_currency="NGN",
            ussd_shortcode="*384#",
            fee_flat=Decimal("50.00"),
            fee_percent=Decimal("1.00"),
            exchange_rate=Decimal("11.25000000"),
            is_active=True,
        ),
        dict(
            code="KE-UG",
            name="Kenya to Uganda (UGX)",
            send_country="KE",
            send_currency="KES",
            receive_country="UG",
            receive_currency="UGX",
            ussd_shortcode="*384#",
            fee_flat=Decimal("30.00"),
            fee_percent=Decimal("0.80"),
            exchange_rate=Decimal("28.50000000"),
            is_active=True,
        ),
        dict(
            code="KE-TZ",
            name="Kenya to Tanzania (TZS)",
            send_country="KE",
            send_currency="KES",
            receive_country="TZ",
            receive_currency="TZS",
            ussd_shortcode="*384#",
            fee_flat=Decimal("30.00"),
            fee_percent=Decimal("0.80"),
            exchange_rate=Decimal("19.75000000"),
            is_active=True,
        ),
    ]
    for item in defaults:
        Corridor.objects.get_or_create(code=item["code"], defaults=item)


class Migration(migrations.Migration):

    dependencies = [
        ("transfers", "0003_remittance_idempotency_key"),
    ]

    operations = [
        migrations.RunPython(seed_ke_outbound_corridors, migrations.RunPython.noop),
    ]

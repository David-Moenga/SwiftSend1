from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from transfers.models import Corridor, Remittance
from transfers.services import advance_remittance, build_evidence_report, create_remittance, run_to_completion


class Command(BaseCommand):
    help = "Run E2E validation for UK/US/UAE -> KE corridors and output evidence JSON."

    def add_arguments(self, parser):
        parser.add_argument("--owner-email", dest="owner_email", default="")
        parser.add_argument("--dry-run", action="store_true", dest="dry_run", default=False)

    def handle(self, *args, **options):
        User = get_user_model()
        owner = None
        if options.get("owner_email"):
            owner = User.objects.filter(email=options["owner_email"]).first()
        if not owner and User.objects.exists():
            owner = User.objects.first()

        corridors = Corridor.objects.filter(code__in=["UK-KE", "US-KE", "AE-KE"], is_active=True)
        amounts = {"UK-KE": "100.00", "US-KE": "100.00", "AE-KE": "367.00"}
        for corridor in corridors:
            validated = {
                "send_amount": amounts.get(corridor.code, "100.00"),
                "sender_name": "Test Sender",
                "sender_contact": "test@example.com",
                "sender_country": corridor.send_country,
                "recipient_name": "Test Recipient",
                "recipient_contact": "+254700000000",
                "recipient_country": "KE",
                "recipient_payout_method": "mobile_money",
                "channel": "web",
            }
            rem = create_remittance(owner=owner, corridor=corridor, validated=validated)
            rem = run_to_completion(rem)
            report = build_evidence_report(rem)
            self.stdout.write(self.style.SUCCESS(f"{corridor.code}: {rem.reference} -> {rem.status}"))
            self.stdout.write(self.style.HTTP_INFO(f"evidence: {report}"))
            self.stdout.write("")

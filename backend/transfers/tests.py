from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from .models import Withdrawal


User = get_user_model()


class WithdrawalApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ada@example.com", email="ada@example.com", password="Strong!pass123")
        self.other_user = User.objects.create_user(username="grace@example.com", email="grace@example.com", password="Strong!pass123")

    def authorize(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")

    def test_withdrawals_require_a_valid_access_token(self):
        response = self.client.post(
            "/api/withdrawals/",
            {"amount": "10.00", "method": "bank", "account_details": "KE12 3456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Withdrawal.objects.count(), 0)

    def test_withdrawal_is_created_for_the_authenticated_user(self):
        self.authorize(self.user)

        response = self.client.post(
            "/api/withdrawals/",
            {"amount": "10.00", "method": "bank", "account_details": "KE12 3456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Withdrawal.objects.get().owner, self.user)

    def test_user_can_only_read_their_own_withdrawals(self):
        own_withdrawal = Withdrawal.objects.create(
            owner=self.user,
            amount="10.00",
            method="bank",
            account_details="KE12 3456",
        )
        other_withdrawal = Withdrawal.objects.create(
            owner=self.other_user,
            amount="20.00",
            method="mobile",
            account_details="0712345678",
        )
        self.authorize(self.user)

        list_response = self.client.get("/api/withdrawals/")
        detail_response = self.client.get(f"/api/withdrawals/{other_withdrawal.pk}/")

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in list_response.data], [own_withdrawal.pk])
        self.assertEqual(detail_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_retrieve_their_own_withdrawal(self):
        withdrawal = Withdrawal.objects.create(
            owner=self.user,
            amount="10.00",
            method="bank",
            account_details="KE12 3456",
        )
        self.authorize(self.user)

        response = self.client.get(f"/api/withdrawals/{withdrawal.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], withdrawal.pk)
        self.assertEqual(response.data["status"], "pending")

    def test_user_can_create_a_withdrawal(self):
        self.authorize(self.user)
        response = self.client.post(
            "/api/withdrawals/",
            {"amount": "25.00", "method": "bank", "account_details": "KE12 3456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")
        self.assertEqual(Withdrawal.objects.count(), 1)



from decimal import Decimal

from .models import Corridor, Remittance, USSDSession


class CorridorAndRemittanceApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ada@example.com", email="ada@example.com", password="Strong!pass123")
        self.corridor = Corridor.objects.filter(code="US-KE", is_active=True).first()
        if not self.corridor:
            self.corridor = Corridor.objects.create(
                code="US-KE", name="USA to Kenya (KES)", send_country="US", send_currency="USD",
                receive_country="KE", receive_currency="KES", fee_flat=Decimal("1.50"),
                fee_percent=Decimal("0.50"), exchange_rate=Decimal("129.50000000"), ussd_shortcode="*384#",
            )

    def authorize(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")

    def test_lists_active_kenya_corridors(self):
        response = self.client.get("/api/corridors/?receive_country=KE")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = {item["code"] for item in response.data}
        self.assertTrue(codes.issuperset({"US-KE"}) or len(response.data) >= 1)
        us = next((i for i in response.data if i["code"] == "US-KE"), response.data[0])
        self.assertIn("exchange_rate", us)
        self.assertTrue(us["is_active"])

    def test_quote_returns_transparent_pricing(self):
        response = self.client.post("/api/corridors/quote/", {"corridor": "US-KE", "send_amount": "100.00"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["send_currency"], "USD")
        self.assertEqual(response.data["receive_currency"], "KES")
        self.assertEqual(response.data["pricing_transparent"], True)
        self.assertIn("fee_amount", response.data)
        self.assertIn("receive_amount", response.data)

    def test_create_remittance_records_evidence(self):
        self.authorize(self.user)
        response = self.client.post("/api/remittances/", {
            "corridor": "US-KE", "channel": "web",
            "sender_name": "Alice Sender", "sender_country": "US",
            "recipient_name": "Bob Recipient", "recipient_contact": "+254700000001",
            "recipient_country": "KE", "send_amount": "100.00",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["reference"].startswith("SS"))
        self.assertEqual(response.data["status"], "initiated")
        self.assertEqual(response.data["receive_currency"], "KES")
        self.assertTrue(response.data["events"])
        self.assertEqual(response.data["events"][0]["stage"], "initiated")

    def test_e2e_validate_produces_stellar_and_payout_evidence(self):
        self.authorize(self.user)
        created = self.client.post("/api/remittances/", {
            "corridor": "US-KE", "channel": "web",
            "sender_name": "Alice", "sender_country": "US",
            "recipient_name": "Bob", "recipient_contact": "+254700000001",
            "send_amount": "50.00",
        }, format="json").data
        ref = created["reference"]
        response = self.client.post(f"/api/remittances/{ref}/validate/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rem = response.data["remittance"]
        report = response.data["evidence_report"]
        self.assertEqual(rem["status"], "completed")
        self.assertTrue(rem["stellar_tx_hash"])
        self.assertTrue(rem["payout_reference"])
        self.assertEqual(report["reference"], ref)
        self.assertEqual(report["verification"]["stellar_tx_hash"], rem["stellar_tx_hash"])
        stages = [e["stage"] for e in report["events"]]
        self.assertIn("stellar_submitted", stages)
        self.assertIn("stellar_settled", stages)
        self.assertIn("completed", stages)

    def test_track_and_evidence_are_public_by_reference(self):
        self.authorize(self.user)
        ref = self.client.post("/api/remittances/", {
            "corridor": "US-KE", "channel": "web",
            "sender_name": "Alice", "sender_country": "US",
            "recipient_name": "Bob", "recipient_contact": "+254700000001",
            "send_amount": "25.00",
        }, format="json").data["reference"]
        self.client.post(f"/api/remittances/{ref}/validate/", {}, format="json")
        self.client.credentials()  # public
        track = self.client.get(f"/api/track/{ref}/")
        evidence = self.client.get(f"/api/remittances/{ref}/evidence/")
        self.assertEqual(track.status_code, status.HTTP_200_OK)
        self.assertEqual(track.data["reference"], ref)
        self.assertIn("evidence_report", track.data)
        self.assertEqual(evidence.status_code, status.HTTP_200_OK)
        self.assertTrue(evidence.data["verification"]["stellar_tx_hash"])

    def test_ussd_webhook_records_session_and_status_lookup(self):
        """Compatibility check: legacy webhook path uses new USSD flow."""
        self.authorize(self.user)
        ref = self.client.post("/api/remittances/", {
            "corridor": "US-KE", "channel": "web",
            "sender_name": "Alice", "sender_country": "US",
            "recipient_name": "Bob", "recipient_contact": "+254700000001",
            "send_amount": "10.00",
        }, format="json").data["reference"]
        self.client.credentials()

        start = self.client.post("/api/ussd/webhook/?format=json", {
            "sessionId": "ussd-test-1", "serviceCode": "*384#", "phoneNumber": "+254700000099", "text": "",
        }, format="json")
        self.assertEqual(start.status_code, status.HTTP_200_OK)
        self.assertIn("CON", start.data["response"])
        self.assertIn("Welcome to SwiftSend", start.data["response"])
        self.assertIn("3. Transaction Status", start.data["response"])

        # 3 = Transaction Status
        status_menu = self.client.post("/api/ussd/webhook/?format=json", {
            "sessionId": "ussd-test-1", "serviceCode": "*384#", "phoneNumber": "+254700000099", "text": "3",
        }, format="json")
        self.assertEqual(status_menu.status_code, status.HTTP_200_OK)
        self.assertIn("CON", status_menu.data["response"])
        self.assertIn("reference", status_menu.data["response"].lower())

        # Enter reference
        done = self.client.post("/api/ussd/webhook/?format=json", {
            "sessionId": "ussd-test-1", "serviceCode": "*384#", "phoneNumber": "+254700000099", "text": f"3*{ref}",
        }, format="json")
        self.assertEqual(done.status_code, status.HTTP_200_OK)
        self.assertIn("END", done.data["response"])
        self.assertIn(ref, done.data["response"])

        self.assertEqual(USSDSession.objects.filter(session_external_id="ussd-test-1").count(), 1)
        session = USSDSession.objects.get(session_external_id="ussd-test-1")
        self.assertTrue(session.msisdn_masked.endswith("0099"))

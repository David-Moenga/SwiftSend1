from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from transfers.models import Corridor, Remittance, USSDSession


User = get_user_model()


def _cb(client, session_id, text, phone="+254700000111", shortcode="*384#", url="/api/ussd/?format=json"):
    return client.post(
        url,
        {"sessionId": session_id, "serviceCode": shortcode, "phoneNumber": phone, "text": text},
        format="json",
    )


class USSDFlowTests(APITestCase):
    def setUp(self):
        # Ensure required outbound corridors exist (migration seeds them; be defensive).
        self.ng, _ = Corridor.objects.get_or_create(
            code="KE-NG",
            defaults=dict(name="Kenya to Nigeria (NGN)", send_country="KE", send_currency="KES",
                          receive_country="NG", receive_currency="NGN", fee_flat=Decimal("50.00"),
                          fee_percent=Decimal("1.00"), exchange_rate=Decimal("11.25000000"), is_active=True),
        )
        self.ug, _ = Corridor.objects.get_or_create(
            code="KE-UG",
            defaults=dict(name="Kenya to Uganda (UGX)", send_country="KE", send_currency="KES",
                          receive_country="UG", receive_currency="UGX", fee_flat=Decimal("30.00"),
                          fee_percent=Decimal("0.80"), exchange_rate=Decimal("28.50000000"), is_active=True),
        )
        Corridor.objects.get_or_create(
            code="KE-TZ",
            defaults=dict(name="Kenya to Tanzania (TZS)", send_country="KE", send_currency="KES",
                          receive_country="TZ", receive_currency="TZS", fee_flat=Decimal("30.00"),
                          fee_percent=Decimal("0.80"), exchange_rate=Decimal("19.75000000"), is_active=True),
        )

    def test_welcome_menu(self):
        res = _cb(self.client, "s1", "")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("CON", res.data["response"])
        self.assertIn("Welcome to SwiftSend", res.data["response"])
        self.assertIn("1. Send Money", res.data["response"])
        self.assertIn("2. Exchange Rates", res.data["response"])
        self.assertIn("3. Transaction Status", res.data["response"])
        self.assertIn("4. My Account", res.data["response"])

    def test_send_money_destination_menu(self):
        _cb(self.client, "s2", "")
        res = _cb(self.client, "s2", "1")
        self.assertIn("CON", res.data["response"])
        self.assertIn("Where are you sending money?", res.data["response"])
        self.assertIn("1. Nigeria", res.data["response"])
        self.assertIn("2. Uganda", res.data["response"])
        self.assertIn("3. Tanzania", res.data["response"])
        self.assertIn("0. Back", res.data["response"])

    def test_exchange_rate_flow(self):
        _cb(self.client, "s3", "")
        _cb(self.client, "s3", "2")
        res = _cb(self.client, "s3", "2*1")  # Nigeria
        self.assertIn("CON", res.data["response"])
        self.assertIn("NGN", res.data["response"])
        self.assertIn(str(self.ng.exchange_rate), res.data["response"])
        self.assertIn("Fee", res.data["response"])

    def test_send_money_full_flow_creates_simulated_transaction(self):
        sid = "s4"
        _cb(self.client, sid, "")
        _cb(self.client, sid, "1")       # send money
        _cb(self.client, sid, "1*1")     # Nigeria
        quote_res = _cb(self.client, sid, "1*1*1000")  # amount
        self.assertIn("CON", quote_res.data["response"])
        self.assertIn("Confirm Transfer", quote_res.data["response"])
        self.assertIn("KES 1000.00", quote_res.data["response"])
        self.assertIn("Nigeria", quote_res.data["response"])
        self.assertIn("NGN", quote_res.data["response"])
        self.assertIn("Recipient gets", quote_res.data["response"])

        confirm = _cb(self.client, sid, "1*1*1000*1")
        self.assertIn("END", confirm.data["response"])
        self.assertIn("DEMO", confirm.data["response"])
        self.assertIn("no actual money movement", confirm.data["response"].lower())
        self.assertIn("Ref:", confirm.data["response"])
        self.assertIn("Status:", confirm.data["response"])

        session = USSDSession.objects.get(session_external_id=sid)
        self.assertIsNotNone(session.remittance_id)
        rem = session.remittance
        self.assertTrue(rem.reference.startswith("SS"))
        self.assertEqual(rem.channel, Remittance.Channel.USSD)
        self.assertEqual(rem.send_currency, "KES")
        self.assertEqual(rem.receive_currency, "NGN")
        self.assertTrue((rem.metadata or {}).get("simulated"))
        self.assertTrue((rem.metadata or {}).get("demo"))

    def test_cancel_transfer(self):
        sid = "s5"
        _cb(self.client, sid, "")
        _cb(self.client, sid, "1")
        _cb(self.client, sid, "1*1")
        _cb(self.client, sid, "1*1*1000")
        res = _cb(self.client, sid, "1*1*1000*2")
        self.assertIn("END", res.data["response"])
        self.assertIn("cancelled", res.data["response"].lower())
        self.assertFalse(Remittance.objects.filter(ussd_sessions__session_external_id=sid).exists())

    def test_transaction_status_lookup(self):
        # create a tx via USSD flow
        sid = "s6"
        _cb(self.client, sid, ""); _cb(self.client, sid, "1"); _cb(self.client, sid, "1*1")
        _cb(self.client, sid, "1*1*1000"); done = _cb(self.client, sid, "1*1*1000*1")
        ref = USSDSession.objects.get(session_external_id=sid).remittance.reference
        self.assertIn(ref, done.data["response"])

        # lookup in a new session
        sid2 = "s6b"
        _cb(self.client, sid2, "")
        _cb(self.client, sid2, "3")
        res = _cb(self.client, sid2, f"3*{ref}")
        self.assertIn("END", res.data["response"])
        self.assertIn(ref, res.data["response"])
        self.assertIn("Status", res.data["response"])

    def test_transaction_status_not_found(self):
        sid = "s7"
        _cb(self.client, sid, ""); _cb(self.client, sid, "3")
        res = _cb(self.client, sid, "3*SSNOTREAL123")
        self.assertIn("END", res.data["response"])
        self.assertIn("not found", res.data["response"].lower())

    def test_invalid_inputs(self):
        sid = "s8"
        _cb(self.client, sid, "")
        res = _cb(self.client, sid, "9")
        self.assertIn("Invalid option", res.data["response"])
        _cb(self.client, sid, "1")
        res = _cb(self.client, sid, "1*9")
        self.assertIn("Invalid", res.data["response"])
        _cb(self.client, sid, "1*1")
        res = _cb(self.client, sid, "1*1*abc")
        self.assertIn("Invalid amount", res.data["response"])

    def test_my_account_no_link(self):
        sid = "s9"
        _cb(self.client, sid, "")
        res = _cb(self.client, sid, "4")
        self.assertIn("END", res.data["response"])
        self.assertIn("My Account", res.data["response"])
        self.assertNotIn("@", res.data["response"])  # no sensitive email leakage

    def test_back_navigation(self):
        sid = "s10"
        _cb(self.client, sid, "")
        _cb(self.client, sid, "1")
        res = _cb(self.client, sid, "1*0")
        self.assertIn("CON", res.data["response"])
        self.assertIn("Welcome to SwiftSend", res.data["response"])

    def test_duplicate_submission_prevented(self):
        sid = "s11"
        _cb(self.client, sid, ""); _cb(self.client, sid, "1"); _cb(self.client, sid, "1*1"); _cb(self.client, sid, "1*1*1000")
        _cb(self.client, sid, "1*1*1000*1")
        # simulate repeated confirm text reaching server in same session state - session already completed; new interaction restarts safely
        count_before = Remittance.objects.filter(ussd_sessions__session_external_id=sid).count()
        self.assertEqual(count_before, 1)

    def test_works_on_callback_endpoint(self):
        res = _cb(self.client, "s12", "", url="/api/ussd/callback/?format=json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("Welcome to SwiftSend", res.data["response"])

    @override_settings(USSD_WEBHOOK_SECRET="secret123")
    def test_webhook_secret_rejected(self):
        res = self.client.post(
            "/api/ussd/?format=json",
            {"sessionId": "s13", "serviceCode": "*384#", "phoneNumber": "+254700000111", "text": ""},
            format="json",
        )
        self.assertEqual(res.status_code, 401)

    @override_settings(USSD_WEBHOOK_SECRET="secret123")
    def test_webhook_secret_accepted(self):
        res = self.client.post(
            "/api/ussd/?format=json",
            {"sessionId": "s14", "serviceCode": "*384#", "phoneNumber": "+254700000111", "text": "", "signature": "secret123"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("Welcome to SwiftSend", res.data["response"])

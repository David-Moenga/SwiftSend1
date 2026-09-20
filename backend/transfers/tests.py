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

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthenticationApiTests(APITestCase):
    def test_register_creates_user_with_hashed_password_and_tokens(self):
        response = self.client.post(
            "/api/auth/register/",
            {"name": "Ada Lovelace", "email": "ada@example.com", "password": "Strong!pass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        user = User.objects.get(email="ada@example.com")
        self.assertTrue(user.check_password("Strong!pass123"))
        self.assertNotEqual(user.password, "Strong!pass123")

    def test_login_rejects_invalid_credentials(self):
        User.objects.create_user(username="ada@example.com", email="ada@example.com", password="Strong!pass123")

        response = self.client.post(
            "/api/auth/login/",
            {"email": "ada@example.com", "password": "incorrect-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_the_refresh_token(self):
        registration_response = self.client.post(
            "/api/auth/register/",
            {"name": "Ada Lovelace", "email": "ada@example.com", "password": "Strong!pass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {registration_response.data['access']}")

        logout_response = self.client.post(
            "/api/auth/logout/",
            {"refresh": registration_response.data["refresh"]},
            format="json",
        )
        refresh_response = self.client.post(
            "/api/auth/refresh/",
            {"refresh": registration_response.data["refresh"]},
            format="json",
        )

        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

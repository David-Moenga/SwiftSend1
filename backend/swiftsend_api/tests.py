from unittest import mock

from django.db import connections
from django.db import DatabaseError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase


class HealthCheckTests(TestCase):
    def test_root_url_returns_ok(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

    def test_root_url_reports_database_status(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['database'], 'ok')

    def test_root_url_reports_unreachable_database(self):
        with mock.patch.object(
            connections['default'], 'ensure_connection', side_effect=Exception('db down')
        ):
            response = self.client.get('/')

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['status'], 'error')
        self.assertEqual(response.json()['database'], 'unreachable')


class DatabaseErrorHandlingTests(APITestCase):
    def test_register_returns_503_when_the_database_is_unavailable(self):
        with mock.patch(
            "accounts.serializers.RegisterSerializer.save",
            side_effect=DatabaseError("database unavailable"),
        ):
            response = self.client.post(
                "/api/auth/register/",
                {
                    "name": "Ada Lovelace",
                    "email": "ada@example.com",
                    "password": "Strong!pass123",
                },
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data.get("status"), "error")

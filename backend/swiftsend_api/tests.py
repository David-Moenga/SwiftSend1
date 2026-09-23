from django.test import TestCase


class HealthCheckTests(TestCase):
    def test_root_url_returns_ok(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

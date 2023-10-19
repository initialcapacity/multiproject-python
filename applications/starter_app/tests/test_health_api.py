from unittest import TestCase

from starter_app.health_api import health_api
from tests.blueprint_test_support import test_client


class TestHealthApi(TestCase):
    def test_get_message(self) -> None:
        client = test_client(health_api())

        response = client.get("/health")

        self.assertEqual(200, response.status_code)
        self.assertEqual({"status": "UP"}, response.json)

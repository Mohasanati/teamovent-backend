
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Sport


class SportAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.active_sport = Sport.objects.create(
            name="Test Sport",
            slug="test-sport",
            description="Sport created for testing",
            is_active=True,
        )

        cls.inactive_sport = Sport.objects.create(
            name="Inactive Sport",
            slug="inactive-sport",
            description="Inactive sport for testing",
            is_active=False,
        )

    def setUp(self):
        self.client = APIClient()

    def test_sports_returns_only_active_sports(self):
        response = self.client.get("/api/sports/")

        self.assertEqual(response.status_code, 200)

        returned_ids = {item["id"] for item in response.data}

        self.assertIn(self.active_sport.id, returned_ids)
        self.assertNotIn(self.inactive_sport.id, returned_ids)

    def test_sport_response_contains_expected_fields(self):
        response = self.client.get("/api/sports/")

        self.assertEqual(response.status_code, 200)

        sport_data = next(
            item
            for item in response.data
            if item["id"] == self.active_sport.id
        )

        self.assertEqual(sport_data["name"], self.active_sport.name)
        self.assertEqual(sport_data["slug"], self.active_sport.slug)
        self.assertEqual(
            sport_data["description"],
            self.active_sport.description,
        )


from django.test import TestCase
from rest_framework.test import APIClient

from .models import Province, City


class LocationAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.province = Province.objects.create(
            name="Test Province",
            slug="test-province",
            is_active=True,
        )

        cls.inactive_province = Province.objects.create(
            name="Inactive Province",
            slug="inactive-province",
            is_active=False,
        )

        cls.city = City.objects.create(
            province=cls.province,
            name="Test City",
            slug="test-city",
            is_active=True,
        )

        cls.inactive_city = City.objects.create(
            province=cls.province,
            name="Inactive City",
            slug="inactive-city",
            is_active=False,
        )

    def setUp(self):
        self.client = APIClient()

    def test_provinces_returns_only_active_provinces(self):
        response = self.client.get("/api/locations/provinces/")

        self.assertEqual(response.status_code, 200)

        returned_ids = {item["id"] for item in response.data}

        self.assertIn(self.province.id, returned_ids)
        self.assertNotIn(self.inactive_province.id, returned_ids)

    def test_cities_are_filtered_by_province(self):
        response = self.client.get(
            "/api/locations/cities/",
            {"province": self.province.id},
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = {item["id"] for item in response.data}

        self.assertEqual(returned_ids, {self.city.id})

    def test_cities_exclude_inactive_cities(self):
        response = self.client.get(
            "/api/locations/cities/",
            {"province": self.province.id},
        )

        returned_ids = {item["id"] for item in response.data}

        self.assertNotIn(self.inactive_city.id, returned_ids)

    def test_cities_require_province_parameter(self):
        response = self.client.get("/api/locations/cities/")

        self.assertEqual(response.status_code, 400)
        self.assertIn("province", response.data)

    def test_cities_for_inactive_province_are_empty(self):
        response = self.client.get(
            "/api/locations/cities/",
            {"province": self.inactive_province.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

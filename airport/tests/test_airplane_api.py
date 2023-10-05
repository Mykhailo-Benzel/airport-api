import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework import status

from airport.models import AirplaneType, Airplane
from rest_framework.test import APIClient

from airport.serializers import AirplaneSerializer

AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")
AIRPLANE_URL = reverse("airport:airplane-list")


def sample_airplane(**params):

    defaults = {
        "name": "Airplane",
        "rows": 5,
        "seats_in_row": 5,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def sample_airplane_type(**params):
    defaults = {
        "name": "Test",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def image_upload_url(airplane_id):
    """Return URL for recipe image upload"""
    return reverse("airport:airplane-upload-image", args=[airplane_id])


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test1234",
        )
        self.client.force_authenticate(self.user)

    def test_list_airplane(self):
        sample_airplane()

        res = self.client.get(AIRPLANE_URL)

        airplane = Airplane.objects.all()
        serializer = AirplaneSerializer(airplane, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_airplane_by_airplane_type(self):
        airplane1 = sample_airplane(airplane_type=sample_airplane_type(name="test1"))
        airplane2 = sample_airplane(airplane_type=sample_airplane_type(name="test2"))

        res = self.client.get(AIRPLANE_URL, {"airplane_type": 1})

        serializer1 = AirplaneSerializer(airplane1)
        serializer2 = AirplaneSerializer(airplane2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_airplane_detail(self):
        airplane = sample_airplane()

        url = detail_url(airplane.id)
        res = self.client.get(url)

        serializer = AirplaneSerializer(airplane)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "Airplane",
            "rows": 5,
            "seats_in_row": 5,
        }
        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "test1234", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        payload = {
            "name": "Test",
            "rows": 10,
            "seats_in_row": 9,
        }
        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_airplane_with_type(self):
        airplane_type = sample_airplane_type(name="test")
        payload = {
            "name": "Airplane",
            "rows": 5,
            "seats_in_row": 5,
            "airplane_type": airplane_type.id
        }
        res = self.client.post(AIRPLANE_URL, payload)

        airplane = Airplane.objects.get(id=res.data["id"])
        airplane_type = airplane.airplane_type

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(airplane_type.name, "test")

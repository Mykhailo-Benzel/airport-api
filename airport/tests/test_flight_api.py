from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.urls import reverse

from django.test import TestCase
from rest_framework import status

from airport.models import (
    Airport,
    Route,
    Airplane,
    AirplaneType,
    Flight
)
from rest_framework.test import APIClient

from airport.serializers import (
    FlightListSerializer,
    FlightDetailSerializer,
)

FLIGHT_URL = reverse("airport:flight-list")


def sample_airport(**params):
    defaults = {
        "name": "Test",
        "closest_big_city": "Airport"
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


def sample_route(**params):
    source = sample_airport(name="airport1")
    destination = sample_airport(name="airport2")
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 1000
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_airplane_type(**params):
    defaults = {
        "name": "Test",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):

    defaults = {
        "name": "Airplane",
        "rows": 5,
        "seats_in_row": 5,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def sample_flight(**params):
    route = sample_route()
    airplane = sample_airplane()
    departure_time = "2023-09-20T19:16:44Z"
    arrival_time = "2023-09-20T21:00:00Z"

    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": departure_time,
        "arrival_time": arrival_time
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)


def detail_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_flight(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test1234",
        )
        self.client.force_authenticate(self.user)

    def test_list_flight(self):
        sample_flight()
        res = self.client.get(FLIGHT_URL)

        flight = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
            )
        )
        serializer = FlightListSerializer(flight, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_flights_by_route(self):
        flight1 = sample_flight()
        flight2 = sample_flight(route=sample_route(source=sample_airport(name="test1")))

        res = self.client.get(FLIGHT_URL, {"route": 1})

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)

        for data in res.data:
            data.pop("tickets_available", None)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_flights_by_departure_time(self):
        flight1 = sample_flight()
        flight2 = sample_flight(departure_time="2023-10-20T21:00:00Z")

        res = self.client.get(FLIGHT_URL, {"departure_time": "2023-09-20"})

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)

        for data in res.data:
            data.pop("tickets_available", None)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_flight_detail(self):
        flight = sample_flight()

        url = detail_url(flight.id)
        res = self.client.get(url)

        serializer = FlightDetailSerializer(flight)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        route = sample_route()
        airplane = sample_airplane()
        payload = {
            "route": route,
            "airplane": airplane,
            "departure_time": "2023-09-20T19:16:44Z",
            "arrival_time": "2023-10-01T22:37:18Z",
        }
        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "test1234",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight(self):
        airplane = sample_airplane()
        route = sample_route()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2022-06-02T14:00:00Z",
            "arrival_time": "2023-09-20T21:00:00Z",
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_flight_without_route(self):
        airplane = sample_airplane()
        payload = {
            "airplane": airplane.id,
            "departure_time": "2022-06-02T14:00:00Z",
            "arrival_time": "2023-09-20T21:00:00Z",
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_flight_without_airplane(self):
        route = sample_route()
        payload = {
            "route": route.id,
            "departure_time": "2022-06-02T14:00:00Z",
            "arrival_time": "2023-09-20T21:00:00Z",
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


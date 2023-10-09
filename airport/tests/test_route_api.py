from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Route, Airport
from airport.serializers import RouteSerializer, RouteDetailSerializer, RouteListSerializer

ROUTE_URL = reverse("airport:route-list")


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


def detail_url(route_id):
    return reverse("airport:route-detail", args=[route_id])


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test1234",
        )
        self.client.force_authenticate(self.user)

    def test_list_route(self):
        sample_route()

        res = self.client.get(ROUTE_URL)

        route = Route.objects.all()
        serializer = RouteListSerializer(route, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_route_by_source(self):
        route1 = sample_route(source=sample_airport(name="test1"))
        route2 = sample_route(source=sample_airport(name="test2"))

        res = self.client.get(ROUTE_URL, {"source": 1})

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_route_by_destination(self):
        route1 = sample_route(destination=sample_airport(name="test1"))
        route2 = sample_route(destination=sample_airport(name="test2"))

        res = self.client.get(ROUTE_URL, {"destination": 1})

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_route_detail(self):
        route = sample_route()

        url = detail_url(route.id)
        res = self.client.get(url)

        serializer = RouteDetailSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        source = sample_airport(name="airport1")
        destination = sample_airport(name="airport2")
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 1000
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "test1234", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        source = sample_airport(name="Airport1")
        destination = sample_airport(name="Airport2")
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 100
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_route_without_source(self):
        destination = sample_airport()
        payload = {
            "destination": destination,
            "distance": 1000
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_route_without_destination(self):
        source = sample_airport()
        payload = {
            "destination": source,
            "distance": 1000
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_airport_without_distance(self):
        source = sample_airport(name="Airport1")
        destination = sample_airport(name="Airport2")
        payload = {
            "source": source,
            "destination": destination,
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_route_not_allowed(self):
        route = sample_route()
        url = detail_url(route.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

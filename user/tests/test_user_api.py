from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


CREATE_USER_URL = reverse("user:create")
TOKEN_OBTAIN_URL = reverse("user:token_obtain_pair")
TOKEN_REFRESH_URL = reverse("user:token_refresh")
TOKEN_VERIFY_URL = reverse("user:token_verify")
MANAGE_URL = reverse("user:manage")


class UserTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="test1234"
        )

    def test_create_valid_user_success(self):
        payload = {
            "email": "test1@test.com",
            "password": "test1234",
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_token_obtaining(self):
        payload = {
            "email": "test@test.com",
            "password": "test1234",
        }
        response = self.client.post(TOKEN_OBTAIN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("access"))
        self.assertIsNotNone(response.data.get("refresh"))

    def test_token_refresh(self):
        payload = {
            "email": "test@test.com",
            "password": "test1234",
        }
        response_obtain_token = self.client.post(
            TOKEN_OBTAIN_URL, payload
        )
        refresh_token = response_obtain_token.data.get("refresh")

        response = self.client.post(TOKEN_REFRESH_URL, {"refresh": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("access"))

    def test_token_verification(self):
        payload = {
            "email": "test@test.com",
            "password": "test1234",
        }
        response_obtain_token = self.client.post(
            TOKEN_OBTAIN_URL, payload
        )
        access_token = response_obtain_token.data.get("access")
        response = self.client.post(TOKEN_VERIFY_URL, {"token": access_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manage_user_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(MANAGE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, response.data.get("email"))

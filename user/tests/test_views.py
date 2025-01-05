from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:user-register")
MANAGE_USER_URL = reverse("user:user-manage")
TOKEN_URL = reverse("user:token-obtain-pair")


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "test@test.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        res = self.client.post(CREATE_USER_URL, self.user_data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test creating user that already exists fails"""
        get_user_model().objects.create_user(**self.user_data)

        res = self.client.post(CREATE_USER_URL, self.user_data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more than 8 characters"""
        self.user_data["password"] = "pw"
        res = self.client.post(CREATE_USER_URL, self.user_data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = (
            get_user_model().objects.filter(email=self.user_data["email"]).exists()
        )
        self.assertFalse(user_exists)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(MANAGE_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(res.data["first_name"], self.user.first_name)

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""
        res = self.client.post(MANAGE_USER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {"first_name": "Updated", "password": "newpass123"}

        res = self.client.patch(MANAGE_USER_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertTrue(self.user.check_password(payload["password"]))

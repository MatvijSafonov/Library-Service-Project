from django.contrib.auth import get_user_model
from django.test import TestCase


class UserManagerTest(TestCase):
    """Test UserManager model manager."""

    def setUp(self):
        self.email = "testuser@test.com"
        self.password = "testpass123"
        self.extra_fields = {"first_name": "Test", "last_name": "User"}

    def test_create_user(self):
        """Test creating a regular user."""
        user = get_user_model()
        user = user.objects.create_user(
            email=self.email, password=self.password, **self.extra_fields
        )
        self.assertEqual(user.email, self.email)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(self.password))

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model()
        user = user.objects.create_superuser(
            email=self.email, password=self.password, **self.extra_fields
        )
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password(self.password))

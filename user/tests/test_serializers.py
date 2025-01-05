from django.test import TestCase
from django.contrib.auth import get_user_model
from user.serializers import UserSerializer


class UserSerializerTests(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@test.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_serializer_with_valid_data(self):
        """Test serializer with valid data"""
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_password_write_only(self):
        """Test that password field is write-only"""
        user = get_user_model().objects.create_user(**self.user_data)
        serializer = UserSerializer(user)
        self.assertNotIn("password", serializer.data)

    def test_create_user_with_serializer(self):
        """Test creating user with serializer"""
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))

    def test_update_user_with_serializer(self):
        """Test updating user with serializer"""
        user = get_user_model().objects.create_user(**self.user_data)

        update_data = {"first_name": "Updated", "password": "newpass123"}

        serializer = UserSerializer(user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()
        self.assertEqual(updated_user.first_name, "Updated")
        self.assertTrue(updated_user.check_password("newpass123"))

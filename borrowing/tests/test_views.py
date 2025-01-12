from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Borrowing
from library.models import Author, Book

BORROWING_URL = reverse("borrowing:borrowing-list")


def create_user(email="test@test.com", password="testpass123"):
    """
    Helper function to create a user with the given email and password.
    """
    return get_user_model().objects.create_user(email=email, password=password)


class PublicBorrowingApiTests(TestCase):
    """
    Test cases for unauthenticated access to the Borrowing API.
    """

    def setUp(self):
        """
        Set up the API client for unauthenticated requests.
        """
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that authentication is required to access the borrowing list endpoint.
        """
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBorrowingApiTests(TestCase):
    """
    Test cases for authenticated access to the Borrowing API.
    """

    def setUp(self):
        """
        Set up the API client and create test data, including users, authors, and books.
        """
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

        self.admin_user = create_user(email="admin@test.com", password="testpass123")
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.author = Author.objects.create(first_name="Test", last_name="Author")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            cover="soft",
            inventory=5,
            daily_fee=10.00,
        )

    def test_list_borrowings(self):
        """
        Test that authenticated users can retrieve a list of borrowings.
        """
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=14),
        )
        res = self.client.get(BORROWING_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    @patch("borrowing.views.PaymentService.create_payment_for_borrowing")
    def test_create_borrowing(self, mock_payment):
        """
        Test that authenticated users can create a borrowing and that a payment URL is returned.
        """
        mock_payment.return_value.session_url = "http://test.com/payment"
        payload = {
            "book": self.book.id,
            "expected_return_date": (
                timezone.now().date() + timezone.timedelta(days=14)
            ).isoformat(),
        }

        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("payment_url", res.data)

    def test_filter_borrowings_by_is_active(self):
        """
        Test filtering borrowings by their active status.
        """
        borrowing_active = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=14),
            actual_return_date=None,
        )
        borrowing_returned = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=14),
            actual_return_date=timezone.now().date(),
        )

        res = self.client.get(BORROWING_URL, {"is_active": "true"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    def test_filter_borrowings_by_user_id_for_admin(self):
        """
        Test that admin users can filter borrowings by user ID.
        """
        other_user = create_user(email="other_user@test.com")
        Borrowing.objects.create(
            user=other_user,
            book=self.book,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=14),
            actual_return_date=None,
        )

        self.client.force_authenticate(self.admin_user)
        res = self.client.get(BORROWING_URL, {"user_id": other_user.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    def test_filter_borrowings_by_user_id_for_non_admin(self):
        """
        Test that non-admin users cannot filter borrowings by user ID.
        """
        other_user = create_user(email="other_user@test.com")
        Borrowing.objects.create(
            user=other_user,
            book=self.book,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=14),
            actual_return_date=None,
        )

        res = self.client.get(BORROWING_URL, {"user_id": other_user.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 0)

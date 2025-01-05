from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Borrowing
from library.models import Book, Author

BORROWING_URL = reverse("borrowing:borrowing-list")


def create_user(email="test@test.com", password="testpass123"):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

        self.author = Author.objects.create(first_name="Test", last_name="Author")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            cover="soft",  # Змінено з Book.CoverChoices.SOFT на "soft"
            inventory=5,
            daily_fee=10.00,
        )

    def test_list_borrowings(self):
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

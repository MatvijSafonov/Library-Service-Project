from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.urls import reverse

from borrowing.models import Borrowing

BORROW_RETURN_URL = lambda pk: reverse("borrowing:borrowing-return-borrowing", args=[pk])


class AuthenticatedBorrowingsApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "t1e2s3t4",
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date="2025-01-01",
            expected_return_date="2025-01-10",
        )

    def test_return_borrowing_success(self):
        """
        Test successful return of a borrowing.
        """
        url = BORROW_RETURN_URL(self.borrowing.id)
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 11)  # Inventory incremented by 1

    def test_return_borrowing_already_returned(self):
        """
        Test attempting to return a borrowing that has already been returned.
        """
        self.borrowing.actual_return_date = "2025-01-05"
        self.borrowing.save()
        url = BORROW_RETURN_URL(self.borrowing.id)
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)
        self.assertEqual(res.data["error"], "This borrowing is already returned.")

    def test_return_borrowing_by_unauthorized_user(self):
        """
        Test that a borrowing cannot be returned by a user who is not the owner.
        """
        other_user = get_user_model().objects.create_user(
            "other@test.com",
            "otherpassword",
        )
        self.client.force_authenticate(other_user)
        url = BORROW_RETURN_URL(self.borrowing.id)
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)  # Borrowing not found for this user

    def test_return_borrowing_nonexistent(self):
        """
        Test attempting to return a borrowing that does not exist.
        """
        url = BORROW_RETURN_URL(9999)  # Non-existent borrowing ID
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_return_borrowing_invalid_method(self):
        """
        Test that using an invalid HTTP method (GET) returns an error.
        """
        url = BORROW_RETURN_URL(self.borrowing.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


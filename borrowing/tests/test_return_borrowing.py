from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from borrowing.models import Borrowing
from library.models import Book

User = get_user_model()


def get_return_url(borrowing_id: int) -> str:
    """Helper function to get the return URL for a borrowing"""
    return reverse(
        "borrowing:borrowing-return",
        kwargs={"pk": borrowing_id}
    )


class ReturnBorrowingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            cover='soft',
            inventory=5,
            daily_fee=1.00
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=14)
        )
        self.return_url = get_return_url(self.borrowing.pk)

    def test_return_borrowing_success(self):
        """Test successful return of a borrowing"""
        self.client.force_authenticate(user=self.user)
        initial_inventory = self.book.inventory
        response = self.client.post(self.return_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the book's inventory has increased
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, initial_inventory + 1)

        # Check that the borrowing's actual_return_date has been set
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)

    def test_return_already_returned_borrowing(self):
        """Test attempting to return an already returned borrowing"""
        self.client.force_authenticate(user=self.user)
        # First, return the borrowing
        self.borrowing.actual_return_date = timezone.now().date()
        self.borrowing.save()

        # Try to return it again
        response = self.client.post(self.return_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "This book has already been returned."
        )

    def test_return_nonexistent_borrowing(self):
        """Test attempting to return a nonexistent borrowing"""
        self.client.force_authenticate(user=self.user)
        non_existent_url = get_return_url(99999)
        response = self.client.post(non_existent_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_return_borrowing_unauthenticated(self):
        """Test that unauthenticated user cannot return a borrowing"""
        response = self.client.post(self.return_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_return_borrowing_wrong_user(self):
        """Test that a user cannot return another user's borrowing"""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpass123'
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.post(self.return_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You don't have permission to return this book."
        )

    def test_return_borrowing_by_admin(self):
        """Test that admin can return any borrowing"""
        admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=admin_user)
        response = self.client.post(self.return_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)

    def test_return_borrowing_method_not_allowed(self):
        """Test that only POST method is allowed"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.return_url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import IntegrityError

from borrowing.models import Borrowing
from library.models import Book, Author


class BorrowingModelTests(TestCase):
    """
    Test suite for the Borrowing model.
    """
    def setUp(self):
        """
        Set up test data, including a test user, an author, and a book.
        """
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpass123"
        )
        self.author = Author.objects.create(first_name="Test", last_name="Author")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            cover="soft",
            inventory=5,
            daily_fee=10.00,
        )

    def test_borrowing_str_representation(self):
        """
        Test the string representation of a Borrowing instance.
        """
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=14),
        )
        expected_str = f"ID - {borrowing.id} ({borrowing.borrow_date} - {borrowing.expected_return_date})"
        self.assertEqual(str(borrowing), expected_str)

    def test_borrowing_create_with_valid_dates(self):
        """
        Test that a Borrowing instance can be created with valid dates.
        """
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=14),
        )
        self.assertIsNotNone(borrowing.pk)
        self.assertIsNotNone(borrowing.borrow_date)
        self.assertIsNone(borrowing.actual_return_date)

    def test_borrowing_constraint_expected_after_borrow(self):
        """
        Test that creating a Borrowing instance with an expected return date
        before or equal to the borrow date raises an IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            Borrowing.objects.create(
                user=self.user,
                book=self.book,
                expected_return_date=timezone.now().date(),  # Same day, should fail
            )

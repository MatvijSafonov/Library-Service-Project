from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import IntegrityError

from borrowing.models import Borrowing
from library.models import Book, Author

class BorrowingModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass123"
        )
        self.author = Author.objects.create(
            first_name="Test",
            last_name="Author"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            cover="soft",
            inventory=5,
            daily_fee=10.00
        )

    def test_borrowing_str_representation(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=14)
        )
        expected_str = f"ID - {borrowing.id} ({borrowing.borrow_date} - {borrowing.expected_return_date})"
        self.assertEqual(str(borrowing), expected_str)

    def test_borrowing_create_with_valid_dates(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=14)
        )
        self.assertIsNotNone(borrowing.pk)
        self.assertIsNotNone(borrowing.borrow_date)
        self.assertIsNone(borrowing.actual_return_date)

    def test_borrowing_constraint_expected_after_borrow(self):
        with self.assertRaises(IntegrityError):
            Borrowing.objects.create(
                user=self.user,
                book=self.book,
                expected_return_date=timezone.now().date()  # Same day, should fail
            )
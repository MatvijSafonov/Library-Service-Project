from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from borrowing.serializers import BorrowingSerializer, BorrowingDetailSerializer
from borrowing.models import Borrowing
from library.models import Book, Author


class BorrowingSerializerTests(TestCase):
    def setUp(self):
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

        self.borrowing_data = {
            "book": self.book.id,
            "expected_return_date": (
                timezone.now().date() + timezone.timedelta(days=14)
            ).isoformat(),
        }

    def test_serializer_with_valid_data(self):
        serializer = BorrowingSerializer(data=self.borrowing_data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_with_invalid_return_date(self):
        # Set date to yesterday to test validation
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        self.borrowing_data["expected_return_date"] = yesterday.isoformat()

        serializer = BorrowingSerializer(data=self.borrowing_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "Expected return date should be greater than borrow date",
            str(serializer.errors["non_field_errors"]),
        )

    def test_detail_serializer_includes_book_info(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=14),
        )
        serializer = BorrowingDetailSerializer(borrowing)
        data = serializer.data

        self.assertIn("book", data)
        self.assertEqual(data["book"]["title"], self.book.title)
        self.assertIn("payments", data)

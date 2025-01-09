from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from borrowing.models import Borrowing
from library.models import Author, Book
from payment.models import Payment


class PaymentModelTests(TestCase):
    """
    Test suite for the Payment model.
    """

    def setUp(self):
        """
        Set up initial test data including a user, author, book, and borrowing instance.
        """
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpass123"
        )
        self.author = Author.objects.create(first_name="Test", last_name="Author")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            cover="HARD",
            inventory=5,
            daily_fee=10.00,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=14),
        )

    def test_payment_str_representation(self):
        """
        Test the string representation of a Payment instance.
        """
        payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            money_to_pay=Decimal("140.00"),
        )
        expected_str = (
            f"{payment.type} payment for borrowing {self.borrowing} - {payment.status}"
        )
        self.assertEqual(str(payment), expected_str)

    def test_payment_creation_with_valid_data(self):
        """
        Test that a Payment instance is created successfully with valid data.
        """
        payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            money_to_pay=Decimal("140.00"),
        )
        self.assertIsNotNone(payment.pk)
        self.assertEqual(payment.status, Payment.StatusChoices.PENDING)
        self.assertEqual(payment.type, Payment.TypeChoices.PAYMENT)
        self.assertEqual(payment.money_to_pay, Decimal("140.00"))

    def test_payment_validation_money_to_pay(self):
        """
        Test that a ValidationError is raised if money_to_pay is zero.
        """
        with self.assertRaises(ValidationError):
            payment = Payment(
                status=Payment.StatusChoices.PENDING,
                type=Payment.TypeChoices.PAYMENT,
                borrowing=self.borrowing,
                money_to_pay=Decimal("0.00"),
            )
            payment.full_clean()

    def test_payment_validation_paid_status_without_session_id(self):
        """
        Test that a ValidationError is raised if a paid Payment does not have a session_id.
        """
        with self.assertRaises(ValidationError):
            payment = Payment(
                status=Payment.StatusChoices.PAID,
                type=Payment.TypeChoices.PAYMENT,
                borrowing=self.borrowing,
                money_to_pay=Decimal("140.00"),
            )
            payment.full_clean()

    def test_payment_creation_with_session_data(self):
        """
        Test that a Payment instance is created successfully with session data.
        """
        payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            money_to_pay=Decimal("140.00"),
            session_url="https://test.url",
            session_id="test_session_id",
        )
        self.assertEqual(payment.session_url, "https://test.url")
        self.assertEqual(payment.session_id, "test_session_id")

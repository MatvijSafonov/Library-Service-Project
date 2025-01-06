from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from borrowing.models import Borrowing
from library.models import Author, Book
from payment.models import Payment
from payment.services.calculation import PaymentCalculationService
from payment.services.payment import PaymentService


class PaymentCalculationServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpass123"
        )
        self.author = Author.objects.create(first_name="Test", last_name="Author")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            cover="HARD",
            inventory=5,
            daily_fee=Decimal("10.00"),
        )
        self.calculation_service = PaymentCalculationService()

    def test_calculate_payment_amount(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
        )
        amount = self.calculation_service.calculate_payment_amount(borrowing)
        expected_amount = Decimal("70.00")  # 7 days * 10.00 daily fee
        self.assertEqual(amount, expected_amount)

    def test_calculate_fine_amount(self):
        borrow_date = timezone.now().date()
        expected_return_date = borrow_date + timezone.timedelta(days=7)
        actual_return_date = expected_return_date + timezone.timedelta(days=3)

        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=borrow_date,
            expected_return_date=expected_return_date,
            actual_return_date=actual_return_date,
        )
        amount = self.calculation_service.calculate_fine_amount(borrowing)
        expected_amount = (
            Decimal(3)
            * Decimal("10.00")
            * Decimal(str(settings.FINE_MULTIPLIER)).quantize(Decimal("0.01"))
        )
        self.assertEqual(amount, expected_amount)


class PaymentServiceTests(TestCase):
    @patch("payment.services.stripe.StripeService")
    def setUp(self, MockStripeService):
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpass123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author=Author.objects.create(first_name="Test", last_name="Author"),
            cover="HARD",
            inventory=5,
            daily_fee=Decimal("10.00"),
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
        )
        self.mock_stripe = MockStripeService.return_value
        self.payment_service = PaymentService()

        # Mock stripe.checkout.Session.create
        self.stripe_session_patcher = patch("stripe.checkout.Session.create")
        self.mock_stripe_session = self.stripe_session_patcher.start()
        self.mock_stripe_session.return_value = {
            "url": "https://checkout.stripe.com/c/pay/test_session",
            "id": "cs_test_mock_session_id",
        }

    def tearDown(self):
        self.stripe_session_patcher.stop()

    @patch("django.conf.settings.PAYMENT_SUCCESS_URL", "http://localhost/success/")
    @patch("django.conf.settings.PAYMENT_CANCEL_URL", "http://localhost/cancel/")
    def test_create_payment_for_borrowing(self):
        mock_request = MagicMock()
        mock_request.build_absolute_uri.return_value = "http://localhost/"
        self.mock_stripe.create_payment_session.return_value = (
            "https://checkout.stripe.com/c/pay/test_session",
            "cs_test_mock_session_id",
        )

        payment = self.payment_service.create_payment_for_borrowing(
            borrowing=self.borrowing, request=mock_request
        )

        self.assertEqual(payment.type, Payment.TypeChoices.PAYMENT)
        self.assertEqual(payment.status, Payment.StatusChoices.PENDING)
        self.assertIn("https://checkout.stripe.com", payment.session_url)
        self.assertEqual(payment.session_id, "cs_test_mock_session_id")

    @patch("django.conf.settings.PAYMENT_SUCCESS_URL", "http://localhost/success/")
    @patch("django.conf.settings.PAYMENT_CANCEL_URL", "http://localhost/cancel/")
    def test_create_fine_for_borrowing(self):
        mock_request = MagicMock()
        mock_request.build_absolute_uri.return_value = "http://localhost/"
        self.mock_stripe.create_payment_session.return_value = (
            "https://checkout.stripe.com/c/pay/test_session",
            "cs_test_mock_session_id",
        )

        self.borrowing.actual_return_date = (
            self.borrowing.expected_return_date + timezone.timedelta(days=3)
        )
        self.borrowing.save()

        payment = self.payment_service.create_fine_for_borrowing(
            borrowing=self.borrowing, request=mock_request
        )

        self.assertEqual(payment.type, Payment.TypeChoices.FINE)
        self.assertEqual(payment.status, Payment.StatusChoices.PENDING)
        self.assertIn("https://checkout.stripe.com", payment.session_url)
        self.assertEqual(payment.session_id, "cs_test_mock_session_id")

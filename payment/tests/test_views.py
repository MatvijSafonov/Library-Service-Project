from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Borrowing
from library.models import Author, Book
from payment.models import Payment


class PaymentViewSetTests(TestCase):
    """
    Test suite for the PaymentViewSet class, covering the payment-related endpoints.
    """

    def setUp(self):
        """
        Set up initial test data, including users, book, borrowing, and payment instances.
        """
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpass123"
        )
        self.staff_user = get_user_model().objects.create_user(
            email="staff@test.com", password="staffpass123", is_staff=True
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
        self.payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            money_to_pay=Decimal("70.00"),
            session_id="test_session_id",
            session_url="http://test.url",
        )

    def test_list_payments_authenticated(self):
        """
        Test that authenticated users can list their payments.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("payment:payment-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_payments_staff(self):
        """
        Test that staff users can list all payments.
        """
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(reverse("payment:payment-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch("payment.services.stripe.StripeService.verify_session")
    def test_payment_success(self, mock_verify_session):
        """
        Test that the payment status is updated to 'PAID' when the payment is successful.
        """
        self.client.force_authenticate(user=self.user)
        mock_verify_session.return_value = True
        url = reverse("payment:payment-success")
        response = self.client.get(
            f"{url}?payment_id={self.payment.id}&session_id={self.payment.session_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.StatusChoices.PAID)

    def test_payment_cancel(self):
        """
        Test that the payment status remains 'PENDING' when the payment is canceled.
        """
        self.client.force_authenticate(user=self.user)
        url = reverse("payment:payment-cancel")
        response = self.client.get(
            f"{url}?payment_id={self.payment.id}&session_id={self.payment.session_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.StatusChoices.PENDING)

    @patch("payment.services.stripe.StripeService.create_payment_session")
    def test_renew_session(self, mock_create_session):
        """
        Test that the payment session URL and ID are updated when a session is renewed.
        """
        mock_create_session.return_value = ("https://new.test.url", "new_session_id")
        self.client.force_authenticate(user=self.user)
        url = reverse("payment:payment-renew-session", args=[self.payment.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.session_url, "https://new.test.url")
        self.assertEqual(self.payment.session_id, "new_session_id")

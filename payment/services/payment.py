import stripe
from django.db import transaction
from rest_framework.request import Request

from borrowing.models import Borrowing
from payment.models import Payment
from payment.services.calculation import PaymentCalculationService
from payment.services.stripe import StripeService


class PaymentService:
    """Service for handling payment operations."""

    def __init__(self):
        self.stripe_service = StripeService()
        self.calculation_service = PaymentCalculationService()

    @transaction.atomic
    def create_payment_for_borrowing(
        self,
        borrowing: Borrowing,
        request: Request,
    ) -> Payment:
        """Create a new payment for borrowing and initialize Stripe session."""
        try:
            amount = self.calculation_service.calculate_payment_amount(borrowing)
            payment = Payment.objects.create(
                borrowing=borrowing,
                money_to_pay=amount,
                type=Payment.TypeChoices.PAYMENT,
            )

            session_url, session_id = self.stripe_service.create_payment_session(
                borrowing=borrowing,
                request=request,
            )

            payment.session_url = session_url
            payment.session_id = session_id
            payment.save(update_fields=["session_url", "session_id"])

            return payment
        except stripe.error.StripeError:
            raise

    @transaction.atomic
    def create_fine_for_borrowing(
        self,
        borrowing: Borrowing,
        request: Request,
    ) -> Payment:
        """Create a fine payment for overdue borrowing."""
        try:
            amount = self.calculation_service.calculate_fine_amount(borrowing)
            payment = Payment.objects.create(
                borrowing=borrowing,
                money_to_pay=amount,
                type=Payment.TypeChoices.FINE,
            )

            session_url, session_id = self.stripe_service.create_payment_session(
                borrowing=borrowing,
                request=request,
                is_fine=True,
            )

            payment.session_url = session_url
            payment.session_id = session_id
            payment.save(update_fields=["session_url", "session_id"])

            return payment
        except stripe.error.StripeError:
            raise

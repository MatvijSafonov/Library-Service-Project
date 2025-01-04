import stripe
from django.db import transaction
from rest_framework.request import Request

from borrowing.models import Borrowing
from payment.models import Payment
from payment.services.stripe import StripeService


class PaymentService:
    """Service for handling payment operations."""

    def __init__(self):
        self.stripe_service = StripeService()

    @transaction.atomic
    def create_payment_for_borrowing(
        self,
        borrowing: Borrowing,
        request: Request,
    ) -> Payment:
        """Create a new payment for borrowing and initialize Stripe session."""
        try:
            session_url, session_id = self.stripe_service.create_payment_session(
                borrowing=borrowing,
                request=request,
            )
            return Payment.objects.get(session_id=session_id)
        except stripe.error.StripeError:
            raise

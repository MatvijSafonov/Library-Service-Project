from decimal import Decimal

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
        daily_fee = borrowing.book.daily_fee
        days = (borrowing.expected_return_date - borrowing.borrow_date).days
        total_amount = Decimal(str(daily_fee * days))

        payment = Payment.objects.create(
            borrowing=borrowing,
            type=Payment.TypeChoices.PAYMENT,
            money_to_pay=total_amount,
            status=Payment.StatusChoices.PENDING,
        )

        session_url, session_id = self.stripe_service.create_payment_session(
            amount=total_amount,
            payment_id=payment.id,
            borrowing_id=borrowing.id,
            request=request,
        )

        try:
            payment.session_url = session_url
            payment.session_id = session_id
            payment.save(update_fields=["session_url", "session_id"])

            return payment
        except stripe.error.StripeError:
            payment.delete()
            raise

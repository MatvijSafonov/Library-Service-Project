import time

import stripe
from django.conf import settings
from django.urls import reverse
from rest_framework.request import Request

from borrowing.models import Borrowing
from payment.models import Payment
from payment.services.calculation import PaymentCalculationService


class StripeService:
    """Service for handling Stripe payments integration."""

    CURRENCY = "usd"
    PAYMENT_EXPIRATION_HOURS = 24

    def __init__(self):
        """Initialize Stripe service with API key from settings."""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.calculation_service = PaymentCalculationService()

    def create_payment_session(
        self,
        borrowing: Borrowing,
        request: Request,
        is_fine: bool = False,
    ) -> tuple[str, str]:
        """Create new Stripe payment session for payment processing."""
        if is_fine:
            amount = self.calculation_service.calculate_fine_amount(borrowing)
            payment_name = f"Fine for overdue book: {borrowing.book.title}"
        else:
            amount = self.calculation_service.calculate_payment_amount(borrowing)
            payment_name = f"Borrowing book: {borrowing.book.title}"

        payment = Payment.objects.create(
            borrowing=borrowing,
            money_to_pay=amount,
            type=Payment.TypeChoices.FINE if is_fine else Payment.TypeChoices.PAYMENT,
            status=Payment.StatusChoices.PENDING,
        )

        base_success_url = request.build_absolute_uri(
            reverse("payment:payment-success")
        )
        success_url = f"{base_success_url}?payment_id={payment.id}"

        base_cancel_url = request.build_absolute_uri(reverse("payment:payment-cancel"))
        cancel_url = f"{base_cancel_url}?payment_id={payment.id}"

        amount_cents = int(amount * 100)
        expires_at = int(time.time() + 30 * 60)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": self.CURRENCY,
                        "product_data": {"name": payment_name},
                        "unit_amount": amount_cents,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url + "&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url + "&session_id={CHECKOUT_SESSION_ID}",
            expires_at=expires_at,
        )

        payment.session_url = session.url
        payment.session_id = session.id
        payment.save(update_fields=["session_url", "session_id"])

        return session.url, session.id

    def verify_session(self, session_id: str) -> bool:
        """Verify if Stripe payment session was successful."""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session.payment_status == "paid"
        except stripe.error.InvalidRequestError:
            return False

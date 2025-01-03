import time
from decimal import Decimal

import stripe
from django.conf import settings
from django.urls import reverse
from rest_framework.request import Request


class StripeService:
    """Service for handling Stripe payments integration."""

    CURRENCY = "usd"
    PAYMENT_EXPIRATION_HOURS = 24

    def __init__(self):
        """Initialize Stripe service with API key from settings."""
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment_session(
        self,
        amount: Decimal,
        payment_id: int,
        borrowing_id: int,
        request: Request,
    ) -> tuple[str, str]:
        """Create new Stripe payment session for payment processing."""
        base_success_url = request.build_absolute_uri(
            reverse("payment:payment-success")
        )
        success_url = f"{base_success_url}?payment_id={payment_id}"

        base_cancel_url = request.build_absolute_uri(reverse("payment:payment-cancel"))
        cancel_url = f"{base_cancel_url}?payment_id={payment_id}"

        amount_cents = int(amount * 100)
        expires_at = int(time.time() + 30 * 60)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": self.CURRENCY,
                        "product_data": {
                            "name": f"Payment for borrowing #{borrowing_id}"
                        },
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
        return session.url, session.id

    def verify_session(self, session_id: str) -> bool:
        """Verify if Stripe payment session was successful."""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session.payment_status == "paid"
        except stripe.error.InvalidRequestError:
            return False

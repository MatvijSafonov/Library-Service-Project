from payment.models import Payment
from payment.services.stripe import StripeService


def check_payment_sessions():
    """Check all pending payments for expired sessions."""
    stripe_service = StripeService()
    pending_payments = Payment.objects.filter(status=Payment.StatusChoices.PENDING)

    for payment in pending_payments:
        status = stripe_service.check_session_status(payment.session_id)

        if status == "expired":
            payment.status = Payment.StatusChoices.EXPIRED
            payment.save(update_fields=["status"])

        elif status == "paid":
            payment.status = Payment.StatusChoices.PAID
            payment.save(update_fields=["status"])

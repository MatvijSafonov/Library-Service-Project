from django.db import transaction
from rest_framework.request import Request

from borrowing.models import Borrowing
from payment.models import Payment
from payment.services.calculation import PaymentCalculationService
from payment.services.stripe import StripeService


class PaymentService:
    """Service for handling payment operations."""

    def __init__(self):
        """Initialize payment service with required dependencies."""
        self.stripe_service = StripeService()
        self.calculation_service = PaymentCalculationService()

    def _create_payment(
        self,
        borrowing: Borrowing,
        payment_type: Payment.TypeChoices = Payment.TypeChoices.PAYMENT,
    ) -> Payment:
        """Create a new payment instance."""
        amount = (
            self.calculation_service.calculate_fine_amount(borrowing)
            if payment_type == Payment.TypeChoices.FINE
            else self.calculation_service.calculate_payment_amount(borrowing)
        )

        return Payment.objects.create(
            borrowing=borrowing,
            money_to_pay=amount,
            type=payment_type,
        )

    def _init_stripe_session(
        self,
        payment: Payment,
        borrowing: Borrowing,
        request: Request,
        is_fine: bool = False,
    ) -> None:
        """Initialize Stripe session for payment."""
        session_url, session_id = self.stripe_service.create_payment_session(
            borrowing=borrowing,
            request=request,
            is_fine=is_fine,
        )
        payment.session_url = session_url
        payment.session_id = session_id
        payment.save(update_fields=["session_url", "session_id"])

    @transaction.atomic
    def create_payment_for_borrowing(
        self,
        borrowing: Borrowing,
        request: Request,
    ) -> Payment:
        """Create a new payment for borrowing and initialize Stripe session."""
        payment = self._create_payment(
            borrowing=borrowing,
            payment_type=Payment.TypeChoices.PAYMENT,
        )

        self._init_stripe_session(payment, borrowing, request)
        return payment

    @transaction.atomic
    def create_fine_for_borrowing(
        self,
        borrowing: Borrowing,
        request: Request,
    ) -> Payment:
        """Create a fine payment for overdue borrowing."""
        payment = self._create_payment(
            borrowing=borrowing,
            payment_type=Payment.TypeChoices.FINE,
        )

        self._init_stripe_session(payment, borrowing, request, is_fine=True)
        return payment

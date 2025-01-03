import stripe
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from payment.models import Payment
from payment.serializers import PaymentSerializer
from payment.services import StripeService


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for managing payment operations.

    Provides functionality for:
    - Listing payments (filtered by user for non-staff).
    - Retrieving payment details.
    - Processing successful payments.
    - Handling cancelled payments.
    - Renewing payment sessions.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    stripe_service = StripeService()

    def get_queryset(self) -> QuerySet[Payment]:
        """Filter payments based on user permissions."""
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)
        return queryset

    def _validate_payment_session(
        self,
        session_id: str | None,
        payment_id: str | None,
    ) -> tuple[Response | None, Payment | None]:
        """Validate payment session parameters and get payment object."""
        if not session_id or not payment_id:
            return (
                Response(
                    {"error": "Missing session_id or payment_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                ),
                None,
            )

        try:
            payment = get_object_or_404(Payment, id=payment_id)
        except Payment.DoesNotExist:
            return (
                Response(
                    {"error": "Invalid payment_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                ),
                None,
            )

        if payment.status == Payment.StatusChoices.PAID:
            return (
                Response(
                    {"message": "Payment already processed"},
                    status=status.HTTP_200_OK,
                ),
                None,
            )

        return None, payment

    @action(
        methods=["GET"],
        detail=False,
        url_path="success",
        permission_classes=[],
    )
    def success(self, request: Request) -> Response:
        """
        Handle successful payment.

        Verifies the payment session and updates payment status if successful.
        Returns payment details and confirmation message.
        """
        session_id = request.query_params.get("session_id")
        payment_id = request.query_params.get("payment_id")

        error_response, payment = self._validate_payment_session(session_id, payment_id)

        if error_response:
            return error_response

        if self.stripe_service.verify_session(session_id):
            payment.status = Payment.StatusChoices.PAID
            payment.session_id = session_id
            payment.save(update_fields=["status", "session_id"])

            return Response(
                {
                    "message": "Payment successful",
                    "payment_id": payment.id,
                    "amount": payment.money_to_pay,
                    "borrowing_id": payment.borrowing.id,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Payment verification failed"},
            status=status.HTTP_400_BAD_REQUEST,
        )


    @action(
        methods=["GET"],
        detail=False,
        url_path="cancel",
        permission_classes=[],
    )
    def cancel(self, request: Request) -> Response:
        """
        Handle canceled payment.

        Returns payment details and information about session expiration.
        """
        payment_id = request.query_params.get("payment_id")

        if payment_id:
            try:
                payment = get_object_or_404(Payment, id=payment_id)
                return Response(
                    {
                        "message": (
                            "Payment cancelled. You can try again by creating "
                            "a new payment. Note: this payment session will expire in "
                            f"{StripeService.PAYMENT_EXPIRATION_HOURS} hours."
                        ),
                        "payment_id": payment.id,
                        "amount": payment.money_to_pay,
                        "borrowing_id": payment.borrowing.id,
                    },
                    status=status.HTTP_200_OK,
                )
            except Payment.DoesNotExist:
                pass

        return Response(
            {"message": "Payment cancelled"},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="renew",
    )
    def renew_session(self, request: Request, pk: int = None) -> Response:
        """
        Renew payment session.

        Creates a new Stripe payment session for an existing payment.
        Returns new session URL and payment details.
        """
        payment = self.get_object()

        if payment.status == Payment.StatusChoices.PAID:
            return Response(
                {"error": "Payment already processed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session_url, session_id = self.stripe_service.create_payment_session(
                amount=payment.money_to_pay,
                payment_id=payment.id,
                borrowing_id=payment.borrowing.id,
                request=request,
            )
            payment.session_url = session_url
            payment.session_id = session_id
            payment.save(update_fields=["session_url", "session_id"])

            return Response(
                {
                    "session_url": session_url,
                    "payment_id": payment.id,
                    "borrowing_id": payment.borrowing.id,
                },
                status=status.HTTP_200_OK,
            )
        except stripe.error.StripeError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

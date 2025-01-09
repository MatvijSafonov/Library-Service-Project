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
from payment.services.stripe import StripeService


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

    @action(
        methods=["GET"],
        detail=False,
        url_path="success",
        permission_classes=[],
    )
    def success(self, request: Request) -> Response:
        """
        Handle successful payment.

        This endpoint is called by Stripe after successful payment.
        Requires payment_id and session_id in query parameters.
        Verifies the payment session and updates payment status if successful.
        """
        session_id = request.query_params.get("session_id")
        payment_id = request.query_params.get("payment_id")

        if not payment_id or not session_id:
            return Response(
                {
                    "error": (
                        "Missing required parameters. "
                        "This endpoint should only be accessed via Stripe redirect."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = get_object_or_404(Payment, id=payment_id)

            if payment.session_id != session_id:
                return Response(
                    {"error": "Invalid session ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if payment.status == Payment.StatusChoices.PAID:
                return Response(
                    {
                        "message": "Payment already processed",
                        "payment_id": payment.id,
                        "amount": payment.money_to_pay,
                        "borrowing_id": payment.borrowing.id,
                    },
                    status=status.HTTP_200_OK,
                )

            if self.stripe_service.verify_session(session_id):
                payment.status = Payment.StatusChoices.PAID
                payment.save(update_fields=["status"])

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

        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND,
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

        This endpoint is called by Stripe after payment cancellation.
        Requires payment_id and session_id in query parameters.
        """
        payment_id = request.query_params.get("payment_id")
        session_id = request.query_params.get("session_id")

        if not payment_id or not session_id:
            return Response(
                {
                    "error": (
                        "Missing required parameters. "
                        "This endpoint should only be accessed via Stripe redirect."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = get_object_or_404(Payment, id=payment_id)
            if payment.session_id != session_id:
                return Response(
                    {"error": "Invalid session ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "message": (
                        "Payment cancelled. You can try again by using the same "
                        f"payment URL within {StripeService.SESSION_LIFETIME_MINUTES} "
                        "minutes."
                    ),
                    "payment_id": payment_id,
                    "amount": payment.money_to_pay,
                    "borrowing_id": payment.borrowing.id,
                    "session_url": payment.session_url,
                },
                status=status.HTTP_200_OK,
            )
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(
        methods=["POST"],
        detail=True,
        url_path="renew",
    )
    def renew_session(self, request: Request, pk: int = None) -> Response:
        """
        Renew payment session.

        Updates the existing payment with a new Stripe session
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
                borrowing=payment.borrowing,
                request=request,
            )
            payment.session_url = session_url
            payment.session_id = session_id
            payment.status = Payment.StatusChoices.PENDING
            payment.save(update_fields=["session_url", "session_id", "status"])

            return Response(
                {
                    "message": "Payment session renewed successfully",
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

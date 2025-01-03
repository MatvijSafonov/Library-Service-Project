import datetime
from typing import Type

import stripe
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.serializers import Serializer
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
)
from payment.services.payment import PaymentService


class BorrowingPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 20


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BorrowingPagination
    payment_service = PaymentService()

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return BorrowingSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.all()

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        is_active = self.request.query_params.get("is_active")
        if is_active:
            queryset = queryset.filter(actual_return_date=None)

        user_id = self.request.query_params.get("user_id")
        if user.is_staff and user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if Borrowing.objects.filter(user=user, actual_return_date=None).exists():
            raise ValidationError("You already have an active borrowing.")

        book = serializer.validated_data.get("book")

        if not book:
            raise ValidationError("Book is required")

        if book.inventory == 0:
            raise ValidationError(
                f'Book "{book.title}" is not available (inventory is 0)'
            )

        book.inventory -= 1
        book.save(update_fields=["inventory"])

        borrowing = serializer.save(user=user)

        try:
            payment = self.payment_service.create_payment_for_borrowing(
                borrowing=borrowing,
                request=self.request,
            )
            self.payment_session_url = payment.session_url
        except stripe.error.StripeError as error:
            book.inventory += 1
            book.save(update_fields=["inventory"])
            borrowing.delete()
            raise ValidationError(f"Failed to create payment: {str(error)}")

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Create borrowing with payment session URL in response."""
        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            response.data["payment_url"] = self.payment_session_url

        return response

    @action(detail=True, methods=["GET", "POST"])
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date:
            raise ValidationError("This borrowing has already been returned.")

        borrowing.actual_return_date = datetime.date.today()
        borrowing.save()

        book = borrowing.book
        book.inventory += 1
        book.save(update_fields=["inventory"])

        return Response(
            {"message": "Borrowing returned successfully."},
            status=status.HTTP_200_OK,
        )

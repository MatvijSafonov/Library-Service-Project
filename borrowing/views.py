import datetime
from typing import Type

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import Serializer
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer
)


class BorrowingPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 20


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    # permission_classes = (IsAuthenticated, )
    pagination_class = BorrowingPagination

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return BorrowingSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return self.serializer_class

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

        books = serializer.validated_data.get("book")
        for book in books:
            if book.inventory == 0:
                raise ValidationError("Book inventory is 0.")
            book.inventory -= 1
            book.save()

        serializer.save(user=user)

    @action(detail=True, methods=["GET", "POST"])
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date:
            raise ValidationError("This borrowing has already been returned.")

        borrowing.actual_return_date = datetime.date.today()
        borrowing.save()

        for book in borrowing.book.all():
            book.inventory += 1
            book.save()

        return Response("Borrowing returned successfully.")

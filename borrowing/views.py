from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from borrowing.serializers import (
    BorrowingCreateSerializer,
    BorrowingSerializer
)
from borrowing.models import Borrowing

class BorrowingView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Borrowing.objects
        return Borrowing.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    @action(
        methods=["post"],
        detail=True,
        url_path="return",
        permission_classes=[IsAuthenticated]
    )
    def return_borrowing(self, request, pk=None):
        try:
            borrowing = self.get_object()

            borrowing.actual_return_date = now().date()
            borrowing.book.inventory += 1
            borrowing.book.save()
            borrowing.save()
        except Borrowing.DoesNotExist:
            return Response(
                {"error": "Borrowing not found."}
            )

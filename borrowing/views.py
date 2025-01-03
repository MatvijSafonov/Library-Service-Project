from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Borrowing instances.
    """
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def return_borrowing(self, request, pk=None):
        """
        Handles returning of a borrowing instance.
        Updates the actual return date and book inventory within a transaction.
        """
        borrowing = self.get_object()
        try:
            borrowing.mark_as_returned()
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"message": "Borrowing returned successfully."},
            status=status.HTTP_200_OK,
        )



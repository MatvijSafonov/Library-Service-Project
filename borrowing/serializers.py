from datetime import date
from rest_framework import serializers

from library.serializers import BookBorrowingSerializer
from .models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )
        read_only_fields = ("actual_return_date",)

    def validate(self, data):
        borrow_date = date.today()
        expected_return_date = data.get("expected_return_date")

        if expected_return_date and expected_return_date < borrow_date:
            raise serializers.ValidationError(
                "Expected return date should be greater than or equal to borrow date."
            )

        return data


class BorrowingDetailSerializer(BorrowingSerializer):
    book_id = BookBorrowingSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user_id",
            "borrow_date",
            "expected_date",
            "actual_date",
            "book_id",
        )

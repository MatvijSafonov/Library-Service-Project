from datetime import date
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from library.serializers import BookBorrowingSerializer
from borrowing.models import Borrowing

class BorrowingSerializer(serializers.ModelSerializer):

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
        read_only_fields = (
            "user",
            "borrow_date",
            "actual_return_date",
        )

    def validate(self, data):
        borrow_date = date.today()
        expected_return_date = data.get("expected_return_date")

        if expected_return_date and expected_return_date < borrow_date:
            raise serializers.ValidationError(_(
                "Expected return date should be greater than borrow date."
            ))

        return data


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookBorrowingSerializer(read_only=True)

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

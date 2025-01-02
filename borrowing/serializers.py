from django.db import transaction
from rest_framework import serializers


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "expected_return_date",
            "book",
        )

    def validate(self, data):
        """
        Validate book inventory is not 0.
        """
        if data["book"].inventory == 0:
            raise serializers.ValidationError(
                "This book is not available for borrowing."
            )
        return data

    def create(self, validated_data):
        """
        Create borrowing and decrease inventory by 1 for book.
        """
        with transaction.atomic():
            book = validated_data["book"]
            book.inventory -= 1
            book.save()

            borrowing = Borrowing.objects.create(**validated_data)
            return borrowing

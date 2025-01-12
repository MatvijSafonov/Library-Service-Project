from decimal import Decimal

from rest_framework import serializers

from borrowing.models import Borrowing
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model."""

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "session_url",
            "session_id",
            "created_at",
            "updated_at",
        )

    def validate_money_to_pay(self, value: Decimal) -> Decimal:
        """Validate the money_to_pay field."""
        if value <= 0:
            raise serializers.ValidationError(
                {"money_to_pay": "Payment amount must be greater than 0."}
            )
        return value

    def validate_borrowing(self, value: Borrowing) -> Borrowing:
        """Validate the borrowing field."""
        if (
            not self.instance
            and value.payments.filter(status=Payment.StatusChoices.PENDING).exists()
        ):
            raise serializers.ValidationError(
                {"borrowing": "This borrowing already has a pending payment."}
            )
        return value

    def validate(self, attrs: dict) -> dict:
        """Validate the complete serializer data."""
        if attrs.get("status") == Payment.StatusChoices.PAID and not attrs.get(
            "session_id"
        ):
            raise serializers.ValidationError(
                {"status": "Paid payment must have a session ID."}
            )
        return attrs

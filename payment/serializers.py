from rest_framework import serializers

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

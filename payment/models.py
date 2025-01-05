from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from borrowing.models import Borrowing


class Payment(models.Model):
    """
    Model representing a payment in the system.

    This model stores information about payments for book borrowings,
    including both regular payments and fines.
    """

    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        EXPIRED = "EXPIRED", "Expired"

    class TypeChoices(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    status = models.CharField(
        max_length=7,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True,
        help_text="Current status of the payment.",
    )
    type = models.CharField(
        max_length=7,
        choices=TypeChoices.choices,
        default=TypeChoices.PAYMENT,
        db_index=True,
        help_text="Type of payment (regular payment or fine).",
    )
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments",
        help_text="The borrowing this payment is for.",
    )
    session_url = models.URLField(
        max_length=511,
        null=True,
        blank=True,
        help_text="URL for the payment session.",
    )
    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Unique identifier of the payment session.",
    )
    money_to_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Amount to be paid.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of payment creation.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of last payment update.",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return string representation of the payment."""
        return f"{self.type} payment for borrowing {self.borrowing} - {self.status}"

    def clean(self) -> None:
        """Validate the payment instance."""
        super().clean()
        if self.money_to_pay <= 0:
            raise ValidationError(
                {"money_to_pay": "Payment amount must be greater than 0."}
            )
        if self.status == self.StatusChoices.PAID and not self.session_id:
            raise ValidationError(
                {"status": "Paid payment must have a session ID."}
            )

    def save(self, *args, **kwargs) -> None:
        """Save the payment instance with validation."""
        super().save(*args, **kwargs)

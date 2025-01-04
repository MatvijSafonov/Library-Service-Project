from decimal import Decimal

from django.conf import settings

from borrowing.models import Borrowing


class PaymentCalculationService:
    """Service for calculating payment amounts."""

    @staticmethod
    def calculate_fine_amount(borrowing: Borrowing) -> Decimal:
        """Calculate fine amount for overdue borrowing."""
        overdue_days = (
            borrowing.actual_return_date - borrowing.expected_return_date
        ).days
        return (
            Decimal(str(borrowing.book.daily_fee))
            * overdue_days
            * settings.FINE_MULTIPLIER
        )

    @staticmethod
    def calculate_payment_amount(borrowing: Borrowing) -> Decimal:
        """Calculate regular payment amount for borrowing."""
        days = (borrowing.expected_return_date - borrowing.borrow_date).days
        return Decimal(str(borrowing.book.daily_fee * days))

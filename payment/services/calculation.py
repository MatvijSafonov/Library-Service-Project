from decimal import Decimal

from django.conf import settings

from borrowing.models import Borrowing


class PaymentCalculationService:
    """Service for calculating payment amounts."""

    MAX_FINE_DAYS = 180

    @staticmethod
    def calculate_fine_amount(borrowing: Borrowing) -> Decimal:
        """Calculate fine amount for overdue borrowing."""
        overdue_days = min(
            (borrowing.actual_return_date - borrowing.expected_return_date).days,
            PaymentCalculationService.MAX_FINE_DAYS,
        )

      #  daily_fee = Decimal(str(borrowing.book.daily_fee))
      #  fine_multiplier = Decimal(str(settings.FINE_MULTIPLIER))
      #  return (daily_fee * overdue_days * fine_multiplier).quantize(Decimal("0.01"))
        
        fine_multiplier = Decimal(str(settings.FINE_MULTIPLIER))
        daily_fee = borrowing.book.daily_fee
        
        return (
            daily_fee
            * Decimal(str(overdue_days))
            * fine_multiplier
        ).quantize(Decimal("0.01"))


    @staticmethod
    def calculate_payment_amount(borrowing: Borrowing) -> Decimal:
        """Calculate regular payment amount for borrowing."""
        days = (borrowing.expected_return_date - borrowing.borrow_date).days
        return (
            borrowing.book.daily_fee 
            * Decimal(str(days))
        ).quantize(Decimal("0.01"))

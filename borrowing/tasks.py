from celery import shared_task
from django.utils import timezone
from .models import Borrowing
from .services import BorrowingService

@shared_task
def check_overdue_borrowings():
    today = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True,
        expected_return_date__lt=today
    )

    for borrowing in overdue_borrowings:
        BorrowingService.notify_about_overdue(borrowing)
    
    return f"Checked {overdue_borrowings.count()} overdue borrowings"
from celery import shared_task
from django.utils.timezone import now
from django.contrib.auth import get_user_model

from borrowing.models import Borrowing
from borrowing.services import send_telegram_message


@shared_task
def check_overdue_borrowings():
    """
    Checks for borrowings that are overdue for each user and sends a notification
    to a Telegram chat if they have overdue borrowings.
    """
    today = now().date()
    users_with_overdue_borrowings = (
        Borrowing.objects.filter(
            expected_return_date__lte=today, actual_return_date__isnull=True
        ).values_list(
            "user", flat=True
        ).distinct()
    )

    if not users_with_overdue_borrowings:
        return

    for user_id in users_with_overdue_borrowings:
        user = get_user_model().objects.get(id=user_id)
        if not user.telegram_chat_id:
            continue

        user_overdue_borrowings = Borrowing.objects.filter(
            user=user,
            expected_return_date__lte=today,
            actual_return_date__isnull=True
        )

        message = "Overdue borrowings:\n"
        for borrowing in user_overdue_borrowings:
            message += (
                f"\n-📕 Book: {borrowing.book.title}\n"
                f"🗓 Expected return date: {borrowing.expected_return_date}\n"
                f"💰 Daily fee: {borrowing.book.daily_fee}\n"
            )

        send_telegram_message(user.telegram_chat_id, message)

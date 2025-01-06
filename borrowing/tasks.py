import os

import requests
from celery import shared_task
from django.utils.timezone import now
from requests.exceptions import RequestException

from borrowing.models import Borrowing

TELEGRAM_API_URL = (
    f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
)
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram_message(message):
    """
    Sends a message to a predefined Telegram chat.
    """
    try:
        response = requests.post(
            TELEGRAM_API_URL, data={"chat_id": CHAT_ID, "text": message}
        )
        response.raise_for_status()
    except RequestException as e:
        print(f"Error sending message to Telegram: {e}")


@shared_task
def check_overdue_borrowings():
    """
    Checks for borrowings that are overdue and sends a notification
    to a Telegram chat for each overdue borrowing. If no overdue
    borrowings are found, sends a notification indicating this.
    """
    today = now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today, actual_return_date__isnull=True
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            message = (
                f"Overdue borrowing:\n"
                f"Book: {borrowing.book.title}\n"
                f"Borrowed by: {borrowing.user.email}\n"
                f"Expected return date: {borrowing.expected_return_date}\n"
                f"Daily fee: {borrowing.book.daily_fee}"
            )
            send_telegram_message(message)
    else:
        send_telegram_message("No borrowings overdue today!")

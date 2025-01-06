import requests
import logging
from django.utils import timezone
from django.conf import settings
from .models import Borrowing

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id: str, message: str, payment_url: str = None) -> dict:
    """
    Function for sending messages to users via Telegram with optional payment button.
    """
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    if payment_url:
        payload["reply_markup"] = {
            "inline_keyboard": [[{"text": "💳 Pay Now", "url": payment_url}]]
        }

    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    response = requests.post(url, json=payload)
    logger.info(f"Telegram API response: {response.json()}")
    return response.json()


class BorrowingService:
    @staticmethod
    def notify_about_borrowing(borrowing: Borrowing) -> None:
        logger.info(f"Starting notification for borrowing {borrowing.id}")

        if not borrowing.user.telegram_chat_id:
            logger.warning(f"No telegram_chat_id for user {borrowing.user.id}")
            return

        payment = borrowing.payments.select_related("borrowing").first()
        logger.info(f"Found payment: {payment}")

        if not payment:
            logger.error(f"No payment found for borrowing {borrowing.id}")
            return

        message = (
            f"✅ New borrowing created:\n"
            f"📕 Book: {borrowing.book.title}\n"
            f"🗓 Return date: {borrowing.expected_return_date}\n"
            f"💰 Amount to pay: ${payment.money_to_pay}\n\n"
            f"Please use the button below to pay"
        )

        logger.info(f"Sending message to {borrowing.user.telegram_chat_id}")
        response = send_telegram_message(
            borrowing.user.telegram_chat_id, message, payment_url=payment.session_url
        )
        logger.info(f"Message sent: {response}")

    @staticmethod
    def notify_about_regular_return(borrowing: Borrowing) -> None:
        """Notification about successful on-time book return"""
        if not borrowing.user.telegram_chat_id:
            return

        message = (
            f"✅ Returned successfully:\n"
            f"📕 Book: {borrowing.book.title}\n"
            f"🗓 Return date: {borrowing.actual_return_date}\n"
        )

        send_telegram_message(borrowing.user.telegram_chat_id, message)

    @staticmethod
    def notify_about_overdue_return(borrowing: Borrowing) -> None:
        """Notification about overdue book return with fine"""
        if not borrowing.user.telegram_chat_id:
            return

        fine_payment = (
            borrowing.payments.filter(type="FINE").select_related("borrowing").first()
        )
        if not fine_payment:
            return

        message = (
            f"✅ Returned successfully:\n"
            f"📕 Book: {borrowing.book.title}\n"
            f"🗓 Return date: {borrowing.actual_return_date}\n"
            f"⚠️ Book returned late!\n"
            f"💰 Fine amount: ${fine_payment.money_to_pay}\n"
            f"Please use the button below to pay the fine"
        )

        send_telegram_message(
            borrowing.user.telegram_chat_id,
            message,
            payment_url=fine_payment.session_url,
        )

    @staticmethod
    def notify_about_overdue(borrowing: Borrowing) -> None:
        if borrowing.user.telegram_chat_id:
            days_overdue = (timezone.now().date() - borrowing.expected_return_date).days
            message = (
                f"⚠️ Book return overdue:\n"
                f"📕Book: {borrowing.book.title}\n"
                f"❗️Overdue by: {days_overdue} days\n"
                f"🗓Expected return date was: {borrowing.expected_return_date}"
            )
            send_telegram_message(borrowing.user.telegram_chat_id, message)

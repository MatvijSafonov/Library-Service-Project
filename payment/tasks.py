from celery import shared_task

from payment.models import Payment
from payment.services.stripe import StripeService


# TELEGRAM_API_URL = (
#     f"https://api.telegram.org/bot" f"{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
# )
# CHAT_ID = os.getenv("CHAT_ID")


# def send_telegram_message(message):
#     try:
#         response = requests.post(
#             TELEGRAM_API_URL, data={"chat_id": CHAT_ID, "text": message}
#         )
#         response.raise_for_status()
#     except RequestException as e:
#         print(f"Error sending message to Telegram: {e}")


# @shared_task
# def check_overdue_borrowings():
#     today = now().date()
#     overdue_borrowings = Borrowing.objects.filter(
#         expected_return_date__lte=today, actual_return_date__isnull=True
#     )

#     if overdue_borrowings.exists():
#         for borrowing in overdue_borrowings:
#             message = (
#                 f"Overdue borrowing:\n"
#                 f"Book: {borrowing.book.title}\n"
#                 f"Borrowed by: {borrowing.user.email}\n"
#                 f"Expected return date: {borrowing.expected_return_date}\n"
#                 f"Daily fee: {borrowing.book.daily_fee}"
#             )
#             send_telegram_message(message)
#     else:
#         send_telegram_message("No borrowings overdue today!")


@shared_task
def check_payment_sessions():
    """Check all pending payments for expired sessions."""
    stripe_service = StripeService()
    pending_payments = Payment.objects.filter(status=Payment.StatusChoices.PENDING)

    for payment in pending_payments:
        if not payment.session_id:
            continue

        status = stripe_service.check_session_status(payment.session_id)

        if status == "expired":
            payment.status = Payment.StatusChoices.EXPIRED
            payment.save(update_fields=["status"])

        elif status == "paid":
            payment.status = Payment.StatusChoices.PAID
            payment.save(update_fields=["status"])

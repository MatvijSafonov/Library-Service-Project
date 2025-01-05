import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-overdue-borrowings-every-day": {
        "task": "borrowing.services.tasks.check_overdue_borrowings",
        "schedule": crontab(hour=7, minute=0),
    },
    "check-payment-sessions": {
        "task": "payment.tasks.check_payment_sessions",
        "schedule": crontab(minute="*"),
    },
}

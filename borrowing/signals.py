from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from borrowing.models import Borrowing
from borrowing.services import BorrowingService


@receiver(post_save, sender=Borrowing)
def borrowing_post_save(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: BorrowingService.notify_about_borrowing(instance))

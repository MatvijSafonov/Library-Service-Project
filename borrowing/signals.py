from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Borrowing
from .services import BorrowingService


@receiver(post_save, sender=Borrowing)
def borrowing_post_save(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: BorrowingService.notify_about_borrowing(instance))

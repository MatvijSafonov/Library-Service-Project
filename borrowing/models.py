from django.db import models
from django.conf import settings
from django.utils.timezone import now

from library.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(expected_return_date__gt=models.F("borrow_date")),
                name="check_expected_after_borrow"
            )
        ]

    def mark_as_returned(self):
        """
        Marks the borrowing as returned. Updates the actual return date
        and increments the book inventory.
        """
        if self.actual_return_date:
            raise ValueError("This borrowing is already returned.")
        self.actual_return_date = now().date()
        self.book.inventory += 1
        self.book.save()
        self.save()

    def __str__(self):
        return f"ID - {self.id} ({self.borrow_date} - {self.expected_return_date})"

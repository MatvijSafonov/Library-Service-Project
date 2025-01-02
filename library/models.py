from django.db import models


class Book(models.Model):
    COVER_CHOICES = (
        ("soft", "Soft"),
        ("hard", "Hard"),
    )

    title = models.CharField(max_length=63)
    author = models.CharField(max_length=63)
    cover = models.CharField(choices=COVER_CHOICES, max_length=7)
    inventory = models.PositiveIntegerField()
    dayly_fee = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ("title",)
        constraints = [
            models.UniqueConstraint(
                fields=["title", "author"], name="unique_title_author"
            )
        ]

    def __str__(self):
        return f"{self.title} by {self.author} ({self.dayly_fee})"

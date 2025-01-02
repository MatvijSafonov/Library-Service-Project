from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=31)
    last_name = models.CharField(max_length=31)
    pseudonym = models.CharField(max_length=31, blank=True)

    class Meta:
        ordering = ("last_name", "first_name")
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name"], name="unique_author"
            )
        ]
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name()


class Book(models.Model):
    COVER_CHOICES = (
        ("soft", "Soft"),
        ("hard", "Hard"),
    )

    title = models.CharField(max_length=63)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    cover = models.CharField(choices=COVER_CHOICES, max_length=7)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ("title",)
        constraints = [
            models.UniqueConstraint(
                fields=["title", "author"], name="unique_title_author"
            )
        ]

    def __str__(self):
        return f"{self.title} by {self.author} ({self.daily_fee})"

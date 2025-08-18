from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Comment(models.Model):
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Rating must be at least 1"),
            MaxValueValidator(5, message="Rating cannot exceed 5"),
        ],
        help_text="Rating from 1 to 5",
    )
    content = models.TextField(blank=True, null=True, help_text="Comment content")
    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.CASCADE,
        related_name="comments",
        db_column="account_id",
    )
    book = models.ForeignKey(
        "books.Book",
        on_delete=models.CASCADE,
        related_name="comments",
        db_column="book_id",
    )
    comment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comments"
        ordering = ["-comment_date"]
        unique_together = ["account", "book"]

    def __str__(self):
        return f"{self.account} - {self.book.title} ({self.rating})"

    def clean(self):
        """Additional model validation."""
        from django.core.exceptions import ValidationError

        super().clean()

        if self.rating is not None:
            if isinstance(self.rating, str):
                raise ValidationError(
                    {"rating": "Rating must be an integer, not a string."}
                )

            if self.rating < 1 or self.rating > 5:
                raise ValidationError({"rating": "Rating must be between 1 and 5."})

    def save(self, *args, **kwargs):
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)

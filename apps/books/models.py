from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.categories.models import Category


class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    author_name = models.CharField(max_length=255)
    publisher_name = models.CharField(max_length=255, null=True)
    published_date = models.DateField(null=True)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    photo_path = models.CharField(max_length=255, null=True)

    total_rating_value = models.IntegerField(default=0)
    total_rating_count = models.IntegerField(default=0)

    # One-to-Many: One category can have many books
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="books"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books"
        ordering = ["-created_at", "-updated_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["author_name"]),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """Model validation."""
        from django.core.exceptions import ValidationError

        super().clean()

        errors = {}

        if self.title and not self.title.strip():
            errors["title"] = "Title cannot be empty or contain only spaces."

        if self.author_name and not self.author_name.strip():
            errors["author_name"] = (
                "Author name cannot be empty or contain only spaces."
            )

        if errors:
            raise ValidationError(errors)

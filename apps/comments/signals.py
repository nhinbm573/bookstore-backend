from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, Count
from .models import Comment


@receiver(post_save, sender=Comment)
def update_book_ratings_on_save(sender, instance, created, **kwargs):
    """Update book ratings when a comment is added or updated."""
    book = instance.book

    # Aggregate all ratings for this book
    ratings = book.comments.aggregate(
        total_value=Sum("rating"), total_count=Count("rating")
    )

    book.total_rating_value = ratings["total_value"] or 0
    book.total_rating_count = ratings["total_count"] or 0
    book.save(update_fields=["total_rating_value", "total_rating_count"])


@receiver(post_delete, sender=Comment)
def update_book_ratings_on_delete(sender, instance, **kwargs):
    """Update book ratings when a comment is deleted."""
    book = instance.book

    # Recalculate ratings after deletion
    ratings = book.comments.aggregate(
        total_value=Sum("rating"), total_count=Count("rating")
    )

    book.total_rating_value = ratings["total_value"] or 0
    book.total_rating_count = ratings["total_count"] or 0
    book.save(update_fields=["total_rating_value", "total_rating_count"])

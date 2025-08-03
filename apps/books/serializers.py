from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    authorName = serializers.CharField(source="author_name", read_only=True)
    unitPrice = serializers.DecimalField(
        source="unit_price", max_digits=10, decimal_places=2, default=0, read_only=True
    )
    photoPath = serializers.CharField(source="photo_path", read_only=True)
    totalRatingValue = serializers.IntegerField(
        source="total_rating_value", default=0, read_only=True
    )
    totalRatingCount = serializers.IntegerField(
        source="total_rating_count", default=0, read_only=True
    )

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "authorName",
            "unitPrice",
            "photoPath",
            "totalRatingValue",
            "totalRatingCount",
        ]

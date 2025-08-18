from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author_name",
            "unit_price",
            "photo_path",
            "total_rating_value",
            "total_rating_count",
        ]

class BookSerializer:
    @staticmethod
    def serialize(book):
        return {
            "id": book.id,
            "title": book.title,
            "authorName": book.author_name,
            "unitPrice": float(book.unit_price) if book.unit_price else 0,
            "photoPath": book.photo_path if hasattr(book, "photo_path") else None,
            "totalRatingValue": (
                book.total_rating_value if hasattr(book, "total_rating_value") else 0
            ),
            "totalRatingCount": (
                book.total_rating_count if hasattr(book, "total_rating_count") else 0
            ),
        }

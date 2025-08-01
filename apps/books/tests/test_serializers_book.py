import pytest
from apps.books.serializers import BookSerializer


@pytest.mark.unit
def test_serialize_book_with_all_fields(book_factory):
    """Test serializing a book with all fields populated"""
    book = book_factory.build(
        id=1,
        title="Test Book",
        author_name="Test Author",
        unit_price=29.99,
        photo_path="/images/test-book.jpg",
        total_rating_value=4.5,
        total_rating_count=10,
    )

    result = BookSerializer.serialize(book)

    assert result == {
        "id": 1,
        "title": "Test Book",
        "authorName": "Test Author",
        "unitPrice": 29.99,
        "photoPath": "/images/test-book.jpg",
        "totalRatingValue": 4.5,
        "totalRatingCount": 10,
    }


@pytest.mark.unit
def test_serialize_book_with_null_unit_price(book_factory):
    """Test serializing a book with null unit_price"""
    book = book_factory.build(
        id=2,
        title="Free Book",
        author_name="Free Author",
        unit_price=None,
        photo_path="/images/free-book.jpg",
        total_rating_value=5.0,
        total_rating_count=20,
    )

    result = BookSerializer.serialize(book)

    assert result["unitPrice"] == 0
    assert result["id"] == 2
    assert result["title"] == "Free Book"
    assert result["authorName"] == "Free Author"


@pytest.mark.unit
def test_serialize_book_decimal_unit_price(book_factory):
    """Test serializing a book with Decimal unit_price"""
    book = book_factory.build(
        id=4,
        title="Decimal Book",
        author_name="Decimal Author",
        unit_price="99.95",
        photo_path="/images/decimal-book.jpg",
        total_rating_value=3.7,
        total_rating_count=15,
    )

    result = BookSerializer.serialize(book)

    assert result["unitPrice"] == 99.95
    assert isinstance(result["unitPrice"], float)
    assert result["id"] == 4
    assert result["title"] == "Decimal Book"

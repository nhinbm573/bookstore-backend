import pytest
from decimal import Decimal
from apps.books.serializers import BookSerializer


@pytest.mark.unit
def test_book_serializer_fields(book_factory):
    """Test that BookSerializer has correct fields"""
    book = book_factory.build()
    serializer = BookSerializer(instance=book)

    expected_fields = [
        "id",
        "title",
        "author_name",
        "unit_price",
        "photo_path",
        "total_rating_value",
        "total_rating_count",
    ]

    assert set(serializer.data.keys()) == set(expected_fields)


@pytest.mark.unit
def test_book_serializer_data(book_factory):
    """Test BookSerializer returns correct data"""
    book = book_factory.build(
        title="Test Book",
        author_name="John Doe",
        unit_price=Decimal("29.99"),
        photo_path="https://example.com/book.jpg",
        total_rating_value=45,
        total_rating_count=10,
    )

    serializer = BookSerializer(instance=book)
    data = serializer.data

    assert data["id"] == book.id
    assert data["title"] == "Test Book"
    assert data["author_name"] == "John Doe"
    assert Decimal(data["unit_price"]) == Decimal("29.99")
    assert data["photo_path"] == "https://example.com/book.jpg"
    assert data["total_rating_value"] == 45
    assert data["total_rating_count"] == 10


@pytest.mark.unit
def test_book_serializer_multiple_books(book_factory, category_factory):
    """Test BookSerializer with multiple books"""
    category = category_factory()

    books = []
    for _ in range(3):
        books.append(book_factory.build(category=category))

    serializer = BookSerializer(books, many=True)

    assert len(serializer.data) == 3
    for i, book_data in enumerate(serializer.data):
        assert book_data["id"] == books[i].id
        assert book_data["title"] == books[i].title

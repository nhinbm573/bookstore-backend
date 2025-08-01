import pytest
from apps.books.models import Book
from apps.books.tests.factories import BookFactory
from apps.categories.tests.factories import CategoryFactory


@pytest.fixture
def book_model(db):
    """Get the Book model class for testing model configuration."""
    return Book


@pytest.fixture
def book_factory(db):
    """Get the BookFactory model class for testing model configuration."""
    return BookFactory


@pytest.fixture
def category_factory(db):
    """Get the BookFactory model class for testing model configuration."""
    return CategoryFactory

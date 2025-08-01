import pytest

from apps.categories.tests.factories import CategoryFactory
from apps.comments.models import Comment
from apps.comments.tests.factories import CommentFactory
from apps.accounts.tests.factories import AccountFactory
from apps.books.tests.factories import BookFactory


@pytest.fixture
def comment_model(db):
    """Get the Comment model class for testing model configuration."""
    return Comment


@pytest.fixture
def comment_factory(db):
    """Get the CommentFactory model class for testing model configuration."""
    return CommentFactory


@pytest.fixture
def book_factory(db):
    """Get the BookFactory model class for testing model configuration."""
    return BookFactory


@pytest.fixture
def account_factory(db):
    """Get the AccountFactory model class for testing model configuration."""
    return AccountFactory


@pytest.fixture
def category_factory(db):
    """Get the CategoryFactory model class for testing model configuration."""
    return CategoryFactory

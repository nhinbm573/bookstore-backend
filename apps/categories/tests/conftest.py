import pytest
from apps.categories.models import Category
from apps.categories.tests.factories import CategoryFactory


@pytest.fixture
def category_model(db):
    """Provide access to the Category model class."""
    return Category


@pytest.fixture
def category_factory(db):
    """Create access to the CategoryFactory model class."""
    return CategoryFactory


@pytest.fixture(autouse=True)
def reset_factory_sequences():
    """Resets the sequence counter for CategoryFactory before each test."""
    CategoryFactory.reset_sequence()

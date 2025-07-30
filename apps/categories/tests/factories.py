import factory
from factory.django import DjangoModelFactory
from apps.categories.models import Category


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category
        skip_postgeneration_save = True

    name = factory.Sequence(lambda n: f"Category {n}")
    sort_order = factory.Sequence(lambda n: n * 10)


def create_batch_categories(size=5, **kwargs):
    """Create multiple category instances."""
    return CategoryFactory.create_batch(size, **kwargs)


def create_test_categories_set():
    """Create a standard set of test categories with predictable data."""
    categories = {
        "business": CategoryFactory(
            name="Business",
            sort_order=10,
        ),
        "fiction": CategoryFactory(
            name="Fiction",
            sort_order=20,
        ),
        "non-fiction": CategoryFactory(
            name="Non-Fiction",
            sort_order=30,
        ),
        "career": CategoryFactory(
            name="Career",
            sort_order=40,
        ),
        "technology": CategoryFactory(
            name="Technology",
            sort_order=50,
        ),
        "history": CategoryFactory(
            name="History",
            sort_order=60,
        ),
    }
    return categories

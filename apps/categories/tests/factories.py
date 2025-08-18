import factory
from factory.django import DjangoModelFactory
from apps.categories.models import Category
import random

CATEGORY_NAMES = [
    "Business",
    "Fiction",
    "Non-Fiction",
    "Career",
    "Technology",
    "History",
    "Science",
    "Art",
]


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.LazyFunction(lambda: random.choice(CATEGORY_NAMES))  # type: ignore
    sort_order = factory.Sequence(lambda n: n * 10)


def create_batch_categories(size=5, **kwargs):
    """Create multiple category instances."""
    return CategoryFactory.create_batch(size, **kwargs)

import pytest
from django.db import transaction
from apps.categories.models import Category
from apps.categories.tests.factories import CategoryFactory, create_test_categories_set

@pytest.fixture
def category_model():
    """Provide access to the Category model class."""
    return Category


@pytest.fixture
def category():
    """Create a single category instance."""
    return CategoryFactory()


@pytest.fixture
def category_with_custom_sort():
    """Create a category with custom sort_order."""
    return CategoryFactory(sort_order=100)


@pytest.fixture
def categories_batch():
    """Create a batch of 5 categories."""
    return CategoryFactory.create_batch(5)


@pytest.fixture
def categories_test_set():
    """Create standard test categories set."""
    return create_test_categories_set()


@pytest.fixture
def category_business(categories_test_set):
    """Get business category from test set."""
    return categories_test_set["business"]


@pytest.fixture
def category_fiction(categories_test_set):
    """Get fiction category from test set."""
    return categories_test_set["fiction"]


@pytest.fixture
def category_technology(categories_test_set):
    """Get technology category from test set."""
    return categories_test_set["technology"]


@pytest.fixture
def empty_categories_db(db):
    """Ensure categories table is empty."""
    Category.objects.all().delete()
    return None


@pytest.fixture
def categories_ordered_by_sort():
    """Create categories with specific sort orders for testing ordering."""
    categories = [
        CategoryFactory(name="Third", sort_order=30),
        CategoryFactory(name="First", sort_order=10),
        CategoryFactory(name="Second", sort_order=20),
        CategoryFactory(name="Fourth", sort_order=30),
    ]
    return categories


@pytest.fixture
def category_max_length_name():
    """Create a category with maximum allowed name length."""
    max_length_name = "A" * 255
    return CategoryFactory(name=max_length_name)


@pytest.fixture
def categories_with_unicode():
    """Create categories with unicode characters."""
    return [
        CategoryFactory(name="=838"),
        CategoryFactory(name="��"),
        CategoryFactory(name="'DC*("),
        CategoryFactory(name="=� Books"),
    ]


@pytest.fixture
def categories_with_special_chars():
    """Create categories with special characters."""
    return [
        CategoryFactory(name="Science & Technology"),
        CategoryFactory(name="Children's Books"),
        CategoryFactory(name="How-To / DIY"),
        CategoryFactory(name="Art + Design"),
    ]


@pytest.fixture
def category_factory_class():
    """Return the CategoryFactory class for use in tests."""
    return CategoryFactory


@pytest.fixture
def transactional_db(db):
    """Use transactional database for tests that need rollback."""
    with transaction.atomic():
        yield


@pytest.fixture
def large_category_dataset():
    """Create a large dataset of categories for performance testing."""
    categories = []
    for i in range(100):
        categories.append(Category(
            name=f"Category {i:03d}",
            sort_order=(i % 10) * 10
        ))
    Category.objects.bulk_create(categories)
    return Category.objects.all()


@pytest.fixture
def categories_same_sort_order():
    """Create multiple categories with the same sort_order."""
    sort_order = 50
    return [
        CategoryFactory(name="Alpha", sort_order=sort_order),
        CategoryFactory(name="Beta", sort_order=sort_order),
        CategoryFactory(name="Gamma", sort_order=sort_order),
    ]


@pytest.fixture
def category_edge_cases():
    """Create categories with edge case values."""
    return {
        "negative_sort": CategoryFactory(name="Negative", sort_order=-100),
        "zero_sort": CategoryFactory(name="Zero", sort_order=0),
        "large_sort": CategoryFactory(name="Large", sort_order=999999),
    }


@pytest.fixture(autouse=True)
def cleanup_categories(db):
    """Automatically clean up categories after each test."""
    yield
    Category.objects.all().delete()
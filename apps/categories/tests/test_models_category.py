import pytest
from django.db.utils import IntegrityError
from django.db import models, transaction
from django.core.exceptions import ValidationError

from apps.categories.models import Category
from apps.categories.tests.factories import CategoryFactory


# Model Field Tests


# ID Field Tests
@pytest.mark.unit
def test_id_field_is_auto_field(category_model):
    """Test id field is AutoField with primary_key=True."""
    id_field = category_model._meta.get_field("id")
    assert isinstance(id_field, models.AutoField)
    assert id_field.primary_key is True


@pytest.mark.unit
@pytest.mark.django_db
def test_id_auto_generation(category):
    """Test id is automatically generated on creation."""
    assert category.id is not None
    assert isinstance(category.id, int)


@pytest.mark.unit
@pytest.mark.django_db
def test_id_uniqueness(categories_batch):
    """Test each category has a unique id."""
    ids = [cat.id for cat in categories_batch]
    assert len(ids) == len(set(ids))


# Name Field Tests
@pytest.mark.unit
def test_name_field_configuration(category_model):
    """Test name field max_length=255 and unique=True."""
    name_field = category_model._meta.get_field("name")
    assert isinstance(name_field, models.CharField)
    assert name_field.max_length == 255
    assert name_field.unique is True


@pytest.mark.unit
@pytest.mark.django_db
def test_name_uniqueness_constraint(category):
    """Test database enforces unique names."""
    with transaction.atomic():
        with pytest.raises(IntegrityError):
            CategoryFactory(name=category.name)


@pytest.mark.unit
def test_name_field_type(category_model):
    """Test name field is CharField type."""
    name_field = category_model._meta.get_field("name")
    assert isinstance(name_field, models.CharField)


@pytest.mark.unit
def test_name_required(category_model):
    """Test name cannot be null or blank."""
    name_field = category_model._meta.get_field("name")
    assert name_field.null is False
    assert name_field.blank is False


@pytest.mark.unit
@pytest.mark.django_db
def test_name_max_length_boundary(category_max_length_name):
    """Test with exactly 255 characters."""
    assert len(category_max_length_name.name) == 255
    category_max_length_name.full_clean()  # Should not raise


@pytest.mark.unit
def test_name_over_max_length():
    """Test validation error with 256+ characters."""
    long_name = "A" * 256
    category = CategoryFactory.build(name=long_name)
    with pytest.raises(ValidationError) as exc_info:
        category.full_clean()
    assert "name" in exc_info.value.message_dict


# Sort Order Field Tests
@pytest.mark.unit
def test_sort_order_field_type(category_model):
    """Test sort_order field is IntegerField."""
    sort_order_field = category_model._meta.get_field("sort_order")
    assert isinstance(sort_order_field, models.IntegerField)


@pytest.mark.unit
def test_sort_order_default_value(category_model):
    """Test sort_order default=0 configuration."""
    sort_order_field = category_model._meta.get_field("sort_order")
    assert sort_order_field.default == 0


@pytest.mark.unit
def test_sort_order_not_null(category_model):
    """Test sort_order cannot be null."""
    sort_order_field = category_model._meta.get_field("sort_order")
    assert sort_order_field.null is False


@pytest.mark.unit
@pytest.mark.django_db
def test_sort_order_with_negative_values(category_edge_cases):
    """Test negative integers are accepted."""
    negative_cat = category_edge_cases["negative_sort"]
    assert negative_cat.sort_order == -100
    negative_cat.full_clean()  # Should not raise


@pytest.mark.unit
@pytest.mark.django_db
def test_sort_order_with_zero(category_edge_cases):
    """Test zero is accepted."""
    zero_cat = category_edge_cases["zero_sort"]
    assert zero_cat.sort_order == 0
    zero_cat.full_clean()  # Should not raise


@pytest.mark.unit
def test_sort_order_index(category_model):
    """Test db_index=True for performance."""
    sort_order_field = category_model._meta.get_field("sort_order")
    assert sort_order_field.db_index is True


# Model Configuration Tests
@pytest.mark.unit
def test_meta_db_table(category_model):
    """Test table name is 'categories'."""
    assert category_model._meta.db_table == "categories"


@pytest.mark.unit
def test_meta_ordering(category_model):
    """Test default ordering is ['sort_order', 'name']."""
    assert category_model._meta.ordering == ["sort_order", "name"]


# Model Method Tests
@pytest.mark.unit
@pytest.mark.django_db
def test_str_method(category):
    """Test __str__ method returns category name."""
    assert str(category) == category.name


@pytest.mark.unit
@pytest.mark.django_db
def test_str_with_unicode(categories_with_unicode):
    """Test __str__ with unicode characters in name."""
    for cat in categories_with_unicode:
        assert str(cat) == cat.name


@pytest.mark.unit
@pytest.mark.django_db
def test_str_with_special_characters(categories_with_special_chars):
    """Test __str__ with symbols and special chars."""
    for cat in categories_with_special_chars:
        assert str(cat) == cat.name


# Model Instance Tests
@pytest.mark.unit
@pytest.mark.django_db
def test_model_instance_creation():
    """Test creating instance with all fields."""
    category = CategoryFactory(name="Test Category", sort_order=10)
    assert category.name == "Test Category"
    assert category.sort_order == 10


@pytest.mark.unit
@pytest.mark.django_db
def test_field_value_persistence():
    """Test saved values match input."""
    category = CategoryFactory(name="Books", sort_order=20)
    category.refresh_from_db()
    assert category.name == "Books"
    assert category.sort_order == 20


@pytest.mark.unit
@pytest.mark.django_db
def test_sort_order_updates(category):
    """Test changing sort_order values."""
    original_sort = category.sort_order
    category.sort_order = 100
    category.save()
    category.refresh_from_db()
    assert category.sort_order == 100
    assert category.sort_order != original_sort


@pytest.mark.unit
@pytest.mark.django_db
def test_name_updates(category):
    """Test updating category names."""
    original_name = category.name
    category.name = "Updated Category"
    category.save()
    category.refresh_from_db()
    assert category.name == "Updated Category"
    assert category.name != original_name


# Uniqueness Constraint Tests
@pytest.mark.unit
@pytest.mark.django_db
def test_duplicate_name_creation(category):
    """Test IntegrityError on duplicate names."""
    with transaction.atomic():
        with pytest.raises(IntegrityError):
            CategoryFactory(name=category.name)


@pytest.mark.unit
@pytest.mark.django_db
def test_case_sensitive_uniqueness():
    """Test if 'Electronics' and 'electronics' are different."""
    from django.db import transaction

    CategoryFactory(name="Electronics")
    # This should work if case-sensitive
    try:
        with transaction.atomic():
            CategoryFactory(name="electronics")
    except IntegrityError:
        pytest.skip("Database uses case-insensitive collation")


@pytest.mark.unit
@pytest.mark.django_db
def test_update_to_existing_name(category_business, category_fiction):
    """Test cannot update to already used name."""
    with transaction.atomic():
        with pytest.raises(IntegrityError):
            category_fiction.name = category_business.name
            category_fiction.save()


@pytest.mark.unit
@pytest.mark.django_db
def test_uniqueness_with_whitespace():
    """Test if ' Electronics ' vs 'Electronics' are different."""
    from django.db import transaction

    CategoryFactory(name="Electronics")
    # This should work if whitespace matters
    try:
        with transaction.atomic():
            CategoryFactory(name=" Electronics ")
    except IntegrityError:
        pytest.skip("Database strips whitespace in unique constraint")


# Sort Order Behavior Tests
@pytest.mark.unit
@pytest.mark.django_db
def test_duplicate_sort_order_allowed(categories_same_sort_order):
    """Test multiple categories can have same sort_order."""
    sort_orders = [cat.sort_order for cat in categories_same_sort_order]
    assert all(s == 50 for s in sort_orders)
    assert len(categories_same_sort_order) == 3


@pytest.mark.unit
@pytest.mark.django_db
def test_sort_order_range(category_edge_cases):
    """Test with very large positive and negative integers."""
    assert category_edge_cases["negative_sort"].sort_order == -100
    assert category_edge_cases["large_sort"].sort_order == 999999
    # Both should be valid
    category_edge_cases["negative_sort"].full_clean()
    category_edge_cases["large_sort"].full_clean()


@pytest.mark.unit
@pytest.mark.django_db
def test_queryset_ordering(categories_ordered_by_sort):
    """Test categories are returned in correct order."""
    ordered = Category.objects.all().order_by("sort_order", "name")
    names = list(ordered.values_list("name", flat=True))
    assert names[0] == "First"
    assert names[1] == "Second"
    # Third and Fourth both have sort_order=30, so ordered by name
    assert names[2] == "Fourth"
    assert names[3] == "Third"


@pytest.mark.unit
@pytest.mark.django_db
def test_ordering_with_same_sort_order(categories_same_sort_order):
    """Test name is used as secondary sort."""
    ordered = Category.objects.filter(sort_order=50).order_by("sort_order", "name")
    names = list(ordered.values_list("name", flat=True))
    assert names == ["Alpha", "Beta", "Gamma"]


# Boundary Tests
@pytest.mark.unit
def test_empty_string_name():
    """Test validation error with empty string."""
    category = CategoryFactory.build(name="")
    with pytest.raises(ValidationError) as exc_info:
        category.full_clean()
    assert "name" in exc_info.value.message_dict


@pytest.mark.unit
def test_name_with_only_spaces():
    """Test behavior with whitespace-only names."""
    category = CategoryFactory.build(name="   ")
    with pytest.raises(ValidationError) as exc_info:
        category.full_clean()
    assert "name" in exc_info.value.message_dict


@pytest.mark.unit
def test_extremely_long_names():
    """Test with names at and beyond limit."""
    # At limit (255)
    category_at_limit = CategoryFactory.build(name="A" * 255)
    category_at_limit.full_clean()
    # Beyond limit (256)
    category_beyond = CategoryFactory.build(name="A" * 256)
    with pytest.raises(ValidationError) as exc_info:
        category_beyond.full_clean()
    assert "name" in exc_info.value.message_dict


# Special Character Tests
@pytest.mark.unit
@pytest.mark.django_db
def test_sql_injection_in_name():
    """Test proper escaping of SQL characters."""
    sql_injection_attempts = [
        "'; DROP TABLE categories; --",
        '" OR 1=1 --',
        "' UNION SELECT * FROM users --",
    ]
    for attempt in sql_injection_attempts:
        category = CategoryFactory(name=attempt)
        category.refresh_from_db()
        assert category.name == attempt


@pytest.mark.unit
@pytest.mark.django_db
def test_html_in_name():
    """Test with HTML tags in category name."""
    html_names = [
        "<script>alert('XSS')</script>",
        "<b>Bold Category</b>",
        "&lt;encoded&gt;",
    ]
    for html_name in html_names:
        category = CategoryFactory(name=html_name)
        category.refresh_from_db()
        assert category.name == html_name


# Factory Tests
@pytest.mark.unit
@pytest.mark.django_db
def test_category_factory_creates_valid_instances(category):
    """Test all fields are populated correctly."""
    assert category.name is not None
    assert category.sort_order is not None
    assert category.pk is not None
    category.full_clean()  # Should not raise


@pytest.mark.unit
@pytest.mark.django_db
def test_factory_sequence_generation():
    """Test unique sequential names."""
    categories = CategoryFactory.create_batch(3)
    names = [cat.name for cat in categories]
    assert len(names) == len(set(names))  # All unique
    # Names should follow pattern "Category N"
    for cat in categories:
        assert cat.name.startswith("Category ")


@pytest.mark.unit
@pytest.mark.django_db
def test_factory_sort_order_sequence():
    """Test sort_order increments properly."""
    categories = CategoryFactory.create_batch(3)
    sort_orders = [cat.sort_order for cat in categories]
    # Should increment by 10
    assert sort_orders[1] == sort_orders[0] + 10
    assert sort_orders[2] == sort_orders[1] + 10


@pytest.mark.unit
@pytest.mark.django_db
def test_factory_build_vs_create():
    """Test build() doesn't save to DB."""
    built_category = CategoryFactory.build(name="Not Saved")
    assert built_category.pk is None

    created_category = CategoryFactory.create(name="Saved")
    assert created_category.pk is not None


@pytest.mark.unit
@pytest.mark.django_db
def test_factory_with_custom_values():
    """Test overriding default factory values."""
    custom_category = CategoryFactory(name="Custom Name", sort_order=999)
    assert custom_category.name == "Custom Name"
    assert custom_category.sort_order == 999


@pytest.mark.unit
@pytest.mark.django_db
def test_batch_creation(categories_batch):
    """Test creating multiple categories at once."""
    assert len(categories_batch) == 5
    # All should be saved
    for cat in categories_batch:
        assert cat.pk is not None
    # All should have unique names
    names = [cat.name for cat in categories_batch]
    assert len(names) == len(set(names))


# Query Performance Tests
@pytest.mark.unit
@pytest.mark.django_db
def test_bulk_operations(empty_categories_db):
    """Test create/update many categories efficiently."""
    # Bulk create
    categories = []
    for i in range(50):
        categories.append(Category(name=f"Bulk {i}", sort_order=i))
    Category.objects.bulk_create(categories)

    assert Category.objects.count() == 50

    # Bulk update
    Category.objects.filter(name__startswith="Bulk").update(sort_order=100)
    assert Category.objects.filter(sort_order=100).count() == 50


@pytest.mark.unit
@pytest.mark.django_db
def test_filter_by_name(categories_test_set):
    """Test various name-based queries."""
    # Exact match
    result = Category.objects.filter(name="Technology")
    assert result.count() == 1
    assert result.first().name == "Technology"

    # Case-insensitive contains
    result = Category.objects.filter(name__icontains="fiction")
    assert result.count() == 2  # Fiction and Non-Fiction

    # Starts with
    result = Category.objects.filter(name__startswith="Non")
    assert result.count() == 1
    assert result.first().name == "Non-Fiction"


@pytest.mark.unit
@pytest.mark.django_db
def test_filter_by_sort_order(large_category_dataset):
    """Test range queries on sort_order."""
    # Exact match
    result = Category.objects.filter(sort_order=50)
    assert result.exists()

    # Range query
    result = Category.objects.filter(sort_order__gte=30, sort_order__lte=70)
    assert result.exists()

    # Less than
    result = Category.objects.filter(sort_order__lt=20)
    assert result.exists()


@pytest.mark.unit
@pytest.mark.django_db
def test_complex_queries(categories_test_set):
    """Test combining multiple filters."""
    # Name contains AND sort_order range
    result = Category.objects.filter(name__icontains="e", sort_order__gte=30)
    assert result.exists()

    # OR query using Q objects
    from django.db.models import Q

    result = Category.objects.filter(Q(name="Fiction") | Q(name="History"))
    assert result.count() == 2


# Save method tests
@pytest.mark.unit
@pytest.mark.django_db
def test_save_method_auto_sort_order():
    """Test auto-generation of sort_order when None."""
    # Create first category with explicit sort_order
    CategoryFactory(name="First", sort_order=100)

    # Create category without sort_order (simulate None)
    category = Category(name="Auto Sort")
    category.sort_order = None
    category.save()

    # Should be max + 10 = 110
    assert category.sort_order == 110


@pytest.mark.unit
@pytest.mark.django_db
def test_save_method_preserves_explicit_sort_order():
    """Test that explicit sort_order is not overwritten."""
    category = CategoryFactory(name="Explicit", sort_order=50)
    original_sort = category.sort_order

    category.name = "Updated Name"
    category.save()

    assert category.sort_order == original_sort

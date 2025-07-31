import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction


#######################################
# BASIC MODEL CREATION AND VALIDATION #
#######################################


@pytest.mark.unit
def test_create_category_with_valid_name(category_factory):
    """Test creating a category with a valid name."""
    category = category_factory.create(name="Science Fiction")
    assert category.id is not None
    assert category.name == "Science Fiction"


@pytest.mark.unit
def test_create_category_default_sort_order(category_factory):
    """Test creating a category without sort_order uses default value of 0."""
    category = category_factory.build(name="Mystery")
    assert category.sort_order == 0


@pytest.mark.unit
def test_category_name_unique_constraint(category_factory):
    """Test that creating two categories with the same name fails."""
    category_factory.create(name="Horror")
    with pytest.raises(IntegrityError):
        category_factory.create(name="Horror")


@pytest.mark.unit
def test_category_name_max_length_valid(category_factory):
    """Test creating a category with a 255 character name."""
    long_name = "A" * 255
    category = category_factory.build(name=long_name)
    assert category.name == long_name
    assert len(category.name) == 255


@pytest.mark.unit
def test_category_name_max_length_exceeded(category_factory):
    """Test that creating a category with 256+ character name fails."""
    long_name = "A" * 256
    with pytest.raises(Exception):
        category_factory.create(name=long_name)


@pytest.mark.unit
def test_create_category_without_name(category_model):
    """Test that creating a category without name field fails."""
    with pytest.raises(Exception):
        category_model.create()


@pytest.mark.unit
def test_create_category_with_null_name(category_factory):
    """Test that creating a category with name=None fails."""
    with pytest.raises(IntegrityError):
        category_factory.create(name=None)


@pytest.mark.unit
def test_create_category_with_custom_sort_order(category_factory):
    """Test creating a category with a custom sort_order value."""
    category = category_factory.build(name="Philosophy", sort_order=100)
    assert category.sort_order == 100


############################
# MODEL CLEAN METHOD TESTS #
############################


@pytest.mark.unit
def test_clean_method_empty_string_name(category_factory):
    """Test that clean method raises ValidationError for empty string name."""
    category = category_factory.build(name="")
    with pytest.raises(ValidationError) as exc_info:
        category.clean()
    assert "name" in exc_info.value.message_dict
    assert exc_info.value.message_dict["name"][0] == "This field cannot be blank."


@pytest.mark.unit
def test_clean_method_whitespace_only_name(category_factory):
    """Test that clean method raises ValidationError for whitespace-only name."""
    category = category_factory.build(name="   ")
    with pytest.raises(ValidationError) as exc_info:
        category.clean()
    assert "name" in exc_info.value.message_dict
    assert exc_info.value.message_dict["name"][0] == "This field cannot be blank."


@pytest.mark.unit
def test_clean_method_name_with_spaces(category_factory):
    """Test that clean method accepts name with leading/trailing spaces."""
    category = category_factory.build(name="  Valid Name  ")
    category.clean()


@pytest.mark.unit
def test_clean_method_single_space_name(category_factory):
    """Test that clean method raises ValidationError for single space name."""
    category = category_factory.build(name=" ")
    with pytest.raises(ValidationError) as exc_info:
        category.clean()
    assert "name" in exc_info.value.message_dict
    assert exc_info.value.message_dict["name"][0] == "This field cannot be blank."


@pytest.mark.unit
def test_clean_method_tab_character_name(category_factory):
    """Test that clean method raises ValidationError for tab character name."""
    category = category_factory.build(name="\t")
    with pytest.raises(ValidationError) as exc_info:
        category.clean()
    assert "name" in exc_info.value.message_dict
    assert exc_info.value.message_dict["name"][0] == "This field cannot be blank."


@pytest.mark.unit
def test_clean_method_newline_character_name(category_factory):
    """Test that clean method raises ValidationError for newline character name."""
    category = category_factory.build(name="\n")
    with pytest.raises(ValidationError) as exc_info:
        category.clean()
    assert "name" in exc_info.value.message_dict
    assert exc_info.value.message_dict["name"][0] == "This field cannot be blank."


@pytest.mark.unit
def test_clean_validation_error_message(category_factory):
    """Test that ValidationError has correct message."""
    category = category_factory.build(name="   ")
    with pytest.raises(ValidationError) as exc_info:
        category.clean()
    assert exc_info.value.message_dict["name"][0] == "This field cannot be blank."


##############################
# SAVE METHOD OVERRIDE TESTS #
##############################


@pytest.mark.unit
def test_save_with_none_sort_order_first_category(category_factory):
    """Test saving first category with sort_order=None sets it to 10."""
    category = category_factory.create(name="First Category", sort_order=None)
    assert category.sort_order == 10


@pytest.mark.unit
def test_save_with_none_sort_order_second_category(category_factory):
    """Test saving second category with sort_order=None sets it to 20."""
    category_factory.create(name="First Category", sort_order=10)
    second = category_factory.create(name="Second Category", sort_order=None)
    second.save()
    assert second.sort_order == 20


@pytest.mark.unit
def test_save_with_none_sort_order_after_existing(category_factory):
    """Test saving category with sort_order=None after existing category with sort_order=50."""
    category_factory.create(name="Existing Category", sort_order=50)
    new_category = category_factory.create(name="New Category", sort_order=None)
    assert new_category.sort_order == 60


@pytest.mark.unit
def test_save_preserves_explicit_sort_order(category_factory):
    """Test that save preserves explicitly set sort_order."""
    category = category_factory.create(name="Explicit Order", sort_order=5)
    assert category.sort_order == 5


@pytest.mark.unit
def test_save_with_zero_sort_order(category_factory):
    """Test that save preserves sort_order=0."""
    category = category_factory.create(name="Zero Order", sort_order=0)
    assert category.sort_order == 0


@pytest.mark.unit
def test_save_with_negative_sort_order(category_factory):
    """Test that save preserves negative sort_order."""
    category = category_factory.create(name="Negative Order", sort_order=-10)
    assert category.sort_order == -10


@pytest.mark.unit
def test_save_multiple_none_sort_orders(category_factory):
    """Test saving multiple categories with sort_order=None."""
    first = category_factory.create(name="First", sort_order=None)
    assert first.sort_order == 10

    second = category_factory.create(name="Second", sort_order=None)
    assert second.sort_order == 20

    third = category_factory.create(name="Third", sort_order=None)
    assert third.sort_order == 30


############################
# MODEL META OPTIONS TESTS #
############################


@pytest.mark.unit
def test_db_table_name(category_model):
    """Test that Meta.db_table is 'categories'."""
    assert category_model._meta.db_table == "categories"


@pytest.mark.unit
def test_default_ordering_by_sort_order(category_factory, category_model):
    """Test that categories are ordered by sort_order by default."""
    category_factory.create(name="Third", sort_order=30)
    category_factory.create(name="First", sort_order=10)
    category_factory.create(name="Second", sort_order=20)

    categories = list(category_model.objects.all())
    assert categories[0].sort_order == 10
    assert categories[1].sort_order == 20
    assert categories[2].sort_order == 30


@pytest.mark.unit
def test_default_ordering_by_name_when_same_sort_order(
    category_factory, category_model
):
    """Test that categories with same sort_order are ordered by name."""
    category_factory.create(name="Zebra", sort_order=10)
    category_factory.create(name="Apple", sort_order=10)
    category_factory.create(name="Middle", sort_order=10)

    categories = list(category_model.objects.filter(sort_order=10))
    assert categories[0].name == "Apple"
    assert categories[1].name == "Middle"
    assert categories[2].name == "Zebra"


@pytest.mark.unit
def test_ordering_combines_sort_order_and_name(category_factory, category_model):
    """Test that ordering works correctly with mixed sort_orders and names."""
    category_factory.create(name="Zebra", sort_order=20)
    category_factory.create(name="Apple", sort_order=10)
    category_factory.create(name="Beta", sort_order=10)
    category_factory.create(name="Alpha", sort_order=20)

    categories = list(category_model.objects.all())

    assert categories[0].name == "Apple" and categories[0].sort_order == 10
    assert categories[1].name == "Beta" and categories[1].sort_order == 10
    assert categories[2].name == "Alpha" and categories[2].sort_order == 20
    assert categories[3].name == "Zebra" and categories[3].sort_order == 20


#########################
# DATABASE INDEX TESTS  #
#########################


@pytest.mark.unit
def test_sort_order_db_index(category_model):
    """Test that sort_order field has database index."""
    sort_order_field = category_model._meta.get_field("sort_order")
    assert sort_order_field.db_index is True


@pytest.mark.unit
def test_name_unique_index(category_model):
    """Test that name field has unique index."""
    name_field = category_model._meta.get_field("name")
    assert name_field.unique is True


#########################################
# FULL CLEAN TESTS (MODEL VALIDATION)   #
#########################################


@pytest.mark.unit
def test_full_clean_valid_category(category_factory):
    """Test that full_clean() passes for a valid category."""
    category = category_factory.build(name="Valid Category", sort_order=10)
    category.full_clean()


@pytest.mark.unit
def test_full_clean_empty_name(category_factory):
    """Test that full_clean() raises ValidationError for empty name."""
    category = category_factory.build(name="", sort_order=10)
    with pytest.raises(ValidationError) as exc_info:
        category.full_clean()
    assert "name" in exc_info.value.message_dict
    assert exc_info.value.message_dict["name"][0] == "This field cannot be blank."


@pytest.mark.unit
def test_full_clean_whitespace_name(category_factory):
    """Test that full_clean() raises ValidationError for whitespace name."""
    category = category_factory.build(name="   ", sort_order=10)
    with pytest.raises(ValidationError) as exc_info:
        category.full_clean()
    assert "name" in exc_info.value.message_dict
    assert exc_info.value.message_dict["name"][0] == "This field cannot be blank."


@pytest.mark.unit
def test_full_clean_before_save(category_factory):
    """Test that clean() is called during full_clean()."""
    category = category_factory.build(name="  ", sort_order=10)
    with pytest.raises(ValidationError) as exc_info:
        category.full_clean()
    assert "name" in exc_info.value.message_dict
    assert exc_info.value.message_dict["name"][0] == "This field cannot be blank."


#################
# UPDATE TESTS  #
#################


@pytest.mark.unit
def test_update_category_name(category_factory):
    """Test updating an existing category name."""
    category = category_factory.create(name="Original Name")
    original_id = category.id
    category.name = "Updated Name"
    category.save()
    category.refresh_from_db()
    assert category.id == original_id
    assert category.name == "Updated Name"


@pytest.mark.unit
def test_update_category_name_to_existing(category_factory):
    """Test updating name to an already existing name fails."""
    category_factory.create(name="Existing Name")
    category2 = category_factory.create(name="Another Name")
    category2.name = "Existing Name"
    with pytest.raises(IntegrityError):
        category2.save()


@pytest.mark.unit
def test_update_sort_order(category_factory):
    """Test updating an existing category sort_order."""
    category = category_factory.create(name="Test Category", sort_order=10)
    original_id = category.id
    category.sort_order = 50
    category.save()
    category.refresh_from_db()
    assert category.id == original_id
    assert category.sort_order == 50


@pytest.mark.unit
def test_update_sort_order_to_none(category_factory):
    """Test updating existing sort_order to None keeps current value."""
    category = category_factory.create(name="Test Category", sort_order=25)
    original_sort_order = category.sort_order
    category.sort_order = None
    category.save()
    category.refresh_from_db()
    assert category.sort_order == (original_sort_order + 10)


@pytest.mark.unit
def test_update_name_to_empty(category_factory):
    """Test updating existing name to empty string fails."""
    category = category_factory.create(name="Valid Name")
    category.name = ""
    with pytest.raises(ValidationError) as exc_info:
        category.full_clean()
        category.save()
    assert "name" in exc_info.value.message_dict
    assert exc_info.value.message_dict["name"][0] == "This field cannot be blank."


##########################
# BULK OPERATIONS TESTS  #
##########################


@pytest.mark.unit
def test_bulk_create_respects_sort_order(category_model):
    """Test bulk_create with explicit sort_orders."""
    categories_data = [
        category_model(name="Category 1", sort_order=10),
        category_model(name="Category 2", sort_order=20),
        category_model(name="Category 3", sort_order=30),
    ]

    created = category_model.objects.bulk_create(categories_data)

    assert len(created) == 3
    assert created[0].sort_order == 10
    assert created[1].sort_order == 20
    assert created[2].sort_order == 30


@pytest.mark.unit
def test_bulk_create_none_sort_order(category_model):
    """Test bulk_create with None sort_orders (note: save() method not called)."""
    categories_data = [
        category_model(name="Category A"),
        category_model(name="Category B"),
        category_model(name="Category C"),
    ]

    created = category_model.objects.bulk_create(categories_data)

    assert len(created) == 3
    assert all(cat.sort_order == 0 for cat in created)


@pytest.mark.unit
def test_bulk_update_sort_orders(category_factory, category_model):
    """Test bulk_update for multiple categories' sort_orders."""
    cat1 = category_factory.create(name="Cat 1", sort_order=10)
    cat2 = category_factory.create(name="Cat 2", sort_order=20)
    cat3 = category_factory.create(name="Cat 3", sort_order=30)

    cat1.sort_order = 100
    cat2.sort_order = 200
    cat3.sort_order = 300

    category_model.objects.bulk_update([cat1, cat2, cat3], ["sort_order"])
    updated_cats = category_model.objects.filter(
        name__in=["Cat 1", "Cat 2", "Cat 3"]
    ).order_by("name")
    assert updated_cats[0].sort_order == 100
    assert updated_cats[1].sort_order == 200
    assert updated_cats[2].sort_order == 300


######################
# TRANSACTION TESTS  #
######################


@pytest.mark.unit
def test_concurrent_none_sort_order_saves(category_model):
    """Test simulating concurrent saves with None sort_order."""
    cat1 = category_model(name="Concurrent 1", sort_order=None)
    cat1.save()
    assert cat1.sort_order == 10

    cat2 = category_model(name="Concurrent 2", sort_order=None)
    cat2.save()
    assert cat2.sort_order == 20

    cat3 = category_model(name="Concurrent 3", sort_order=None)
    cat3.save()
    assert cat3.sort_order == 30

    assert cat1.sort_order != cat2.sort_order
    assert cat2.sort_order != cat3.sort_order
    assert cat1.sort_order != cat3.sort_order


@pytest.mark.unit
def test_atomic_save_with_validation_error(category_factory):
    """Test save within transaction that fails validation."""
    category = category_factory.create(name="Valid Category")

    try:
        with transaction.atomic():
            category.name = "Updated Name"
            category.save()

            category.name = ""
            category.full_clean()
            category.save()
    except ValidationError:
        pass

    category.refresh_from_db()
    assert category.name == "Valid Category"

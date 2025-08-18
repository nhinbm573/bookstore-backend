import pytest
from decimal import Decimal
from django.db import IntegrityError
from apps.categories.tests.factories import CategoryFactory

########################################
# BASIC MODEL CREATION AND VALIDATION  #
########################################


@pytest.mark.unit
def test_create_book_with_all_required_fields(book_factory, category_factory):
    """Test creating a book with all required fields."""
    category = category_factory()
    book = book_factory.create(
        title="Test Book",
        author_name="John Doe",
        unit_price=Decimal("29.99"),
        category=category,
    )

    assert book.title == "Test Book"
    assert book.author_name == "John Doe"
    assert book.unit_price == Decimal("29.99")
    assert book.category == category
    assert book.pk is not None


@pytest.mark.unit
def test_create_book_minimum_required_fields_only(book_model, category_factory):
    """Test creating a book with only required fields, verify nullable fields are None."""
    category = category_factory()
    book = book_model.objects.create(
        title="Minimal Book",
        author_name="Jane Smith",
        unit_price=Decimal("19.99"),
        category=category,
    )

    assert book.title == "Minimal Book"
    assert book.author_name == "Jane Smith"
    assert book.unit_price == Decimal("19.99")
    assert book.category == category
    assert book.description is None
    assert book.publisher_name is None
    assert book.published_date is None
    assert book.photo_path is None


@pytest.mark.unit
def test_create_book_without_title(book_model):
    """Test creating a book without title should fail."""
    with pytest.raises(IntegrityError):
        book_model.objects.create(
            author_name="John Doe",
            unit_price=Decimal("29.99"),
        )


@pytest.mark.unit
def test_create_book_without_author_name(book_model):
    """Test creating a book without author_name should fail."""
    with pytest.raises(IntegrityError):
        book_model.objects.create(
            title="Test Book",
            unit_price=Decimal("29.99"),
        )


@pytest.mark.unit
def test_create_book_without_unit_price(book_model):
    """Test creating a book without unit_price should fail."""
    with pytest.raises(IntegrityError):
        book_model.objects.create(
            title="Test Book",
            author_name="John Doe",
        )


@pytest.mark.unit
def test_create_book_without_category(book_model):
    """Test creating a book without category should fail with IntegrityError."""
    with pytest.raises(IntegrityError):
        book_model.objects.create(
            title="Test Book", author_name="John Doe", unit_price=Decimal("29.99")
        )


@pytest.mark.unit
def test_create_book_with_all_optional_fields(book_factory):
    """Test creating a book with all optional fields."""
    category = CategoryFactory()
    book = book_factory(
        title="Complete Book",
        author_name="John Doe",
        unit_price=Decimal("39.99"),
        category=category,
        description="This is a comprehensive book description.",
        publisher_name="Test Publisher",
        published_date="2023-01-15",
        photo_path="/path/to/photo.jpg",
    )

    assert book.title == "Complete Book"
    assert book.author_name == "John Doe"
    assert book.unit_price == Decimal("39.99")
    assert book.category == category
    assert book.description == "This is a comprehensive book description."
    assert book.publisher_name == "Test Publisher"
    assert str(book.published_date) == "2023-01-15"
    assert book.photo_path == "/path/to/photo.jpg"


########################################
# FIELD VALIDATION TESTS               #
########################################


@pytest.mark.unit
def test_title_max_length_valid(book_factory):
    """Test creating book with 255 character title."""
    title = "A" * 255
    book = book_factory.build(title=title)
    assert book.title == title
    assert len(book.title) == 255


@pytest.mark.unit
def test_title_max_length_exceeded(book_model):
    """Test creating book with 256+ character title should fail."""
    from django.db import DataError

    title = "A" * 256
    with pytest.raises(DataError):
        book_model.objects.create(
            title=title,
            author_name="John Doe",
            unit_price=Decimal("29.99"),
        )


@pytest.mark.unit
def test_author_name_max_length_valid(book_factory):
    """Test creating book with 255 character author_name."""
    author_name = "A" * 255
    book = book_factory.create(author_name=author_name)
    assert book.author_name == author_name
    assert len(book.author_name) == 255


@pytest.mark.unit
def test_author_name_max_length_exceeded(book_factory):
    """Test creating book with 256+ character author_name should fail."""
    from django.db import DataError

    author_name = "A" * 256
    with pytest.raises(DataError):
        book_factory.create(
            title="Test Book",
            author_name=author_name,
            unit_price=Decimal("29.99"),
        )


@pytest.mark.unit
def test_publisher_name_max_length_valid(book_factory):
    """Test creating book with 255 character publisher_name."""
    publisher_name = "A" * 255
    book = book_factory.create(publisher_name=publisher_name)
    assert book.publisher_name == publisher_name
    assert len(book.publisher_name) == 255


@pytest.mark.unit
def test_publisher_name_max_length_exceeded(book_factory):
    """Test creating book with 256+ character publisher_name should fail."""
    from django.db import DataError

    publisher_name = "A" * 256
    with pytest.raises(DataError):
        book_factory.create(
            title="Test Book",
            author_name="John Doe",
            publisher_name=publisher_name,
            unit_price=Decimal("29.99"),
        )


@pytest.mark.unit
def test_photo_path_max_length_valid(book_factory):
    """Test creating book with 255 character photo_path."""
    photo_path = "A" * 255
    book = book_factory.create(photo_path=photo_path)
    assert book.photo_path == photo_path
    assert len(book.photo_path) == 255


@pytest.mark.unit
def test_photo_path_max_length_exceeded(book_factory):
    """Test creating book with 256+ character photo_path should fail."""
    from django.db import DataError

    photo_path = "A" * 256
    with pytest.raises(DataError):
        book_factory.create(
            title="Test Book",
            author_name="John Doe",
            photo_path=photo_path,
            unit_price=Decimal("29.99"),
        )


########################################
# UNIT PRICE VALIDATION TESTS          #
########################################


@pytest.mark.unit
def test_unit_price_positive_value(book_factory):
    """Test creating book with positive unit_price value."""
    book = book_factory.build(unit_price=Decimal("10.99"))
    assert book.unit_price == Decimal("10.99")


@pytest.mark.unit
def test_unit_price_zero_value(book_factory):
    """Test creating book with unit_price=0.00."""
    book = book_factory.build(unit_price=Decimal("0.00"))
    assert book.unit_price == Decimal("0.00")


@pytest.mark.unit
def test_unit_price_negative_value(book_factory, category_factory):
    """Test creating book with negative unit_price should fail with ValidationError."""
    from django.core.exceptions import ValidationError

    book = book_factory.build(
        title="Test Book",
        author_name="John Doe",
        unit_price=Decimal("-1.00"),
        category=category_factory(),
    )
    with pytest.raises(ValidationError) as exc_info:
        book.full_clean()
    assert "unit_price" in exc_info.value.message_dict


@pytest.mark.unit
def test_unit_price_max_digits_valid(book_factory):
    """Test creating book with unit_price at max digits (8 digits + 2 decimals = 10 total)."""
    book = book_factory.build(unit_price=Decimal("99999999.99"))
    assert book.unit_price == Decimal("99999999.99")


@pytest.mark.unit
def test_unit_price_max_digits_exceeded(book_factory):
    """Test creating book with unit_price exceeding max digits should fail."""
    from django.db import DataError

    with pytest.raises(DataError):
        book_factory.create(unit_price=Decimal("999999999.99"))


@pytest.mark.unit
def test_unit_price_decimal_places_valid(book_factory):
    """Test creating book with valid 2 decimal places."""
    book = book_factory.build(unit_price=Decimal("10.99"))
    assert book.unit_price == Decimal("10.99")


@pytest.mark.unit
def test_unit_price_min_value_validator(book_factory, category_factory):
    """Test unit_price validator rejects negative values using full_clean()."""
    from django.core.exceptions import ValidationError

    book = book_factory.build(
        title="Test Book",
        author_name="John Doe",
        unit_price=Decimal("-0.01"),
        category=category_factory(),
    )
    with pytest.raises(ValidationError) as exc_info:
        book.full_clean()
    assert "unit_price" in exc_info.value.message_dict
    assert any(
        "greater than or equal to" in str(msg)
        for msg in exc_info.value.message_dict["unit_price"]
    )


########################################
# CLEAN METHOD TESTS                   #
########################################


@pytest.mark.unit
def test_clean_title_empty_string(book_factory):
    """Test creating book with empty title should fail with ValidationError."""
    from django.core.exceptions import ValidationError

    book = book_factory.build(
        title="",
        author_name="John Doe",
        unit_price=Decimal("29.99"),
    )
    with pytest.raises(ValidationError) as exc_info:
        book.full_clean()
    assert "title" in exc_info.value.message_dict
    assert "This field cannot be blank." in str(exc_info.value.message_dict["title"][0])


@pytest.mark.unit
def test_clean_title_whitespace_only(book_factory):
    """Test creating book with whitespace-only title should fail with ValidationError."""
    from django.core.exceptions import ValidationError

    book = book_factory.create(
        title="   ",
        author_name="John Doe",
        unit_price=Decimal("29.99"),
    )
    with pytest.raises(ValidationError) as exc_info:
        book.full_clean()
    assert "title" in exc_info.value.message_dict
    assert "Title cannot be empty or contain only spaces." in str(
        exc_info.value.message_dict["title"][0]
    )


@pytest.mark.unit
def test_clean_title_with_spaces(book_factory):
    """Test creating book with title containing leading/trailing spaces - should be allowed."""
    book = book_factory.build(
        title="  Valid Title  ",
    )
    assert book.title == "  Valid Title  "


@pytest.mark.unit
def test_clean_author_name_empty_string(book_factory):
    """Test creating book with empty author_name should fail with ValidationError."""
    from django.core.exceptions import ValidationError

    book = book_factory.build(
        title="Test Book",
        author_name="",
        unit_price=Decimal("29.99"),
    )
    with pytest.raises(ValidationError) as exc_info:
        book.full_clean()
    assert "author_name" in exc_info.value.message_dict
    assert "This field cannot be blank." in str(
        exc_info.value.message_dict["author_name"][0]
    )


@pytest.mark.unit
def test_clean_author_name_whitespace_only(book_factory):
    """Test creating book with whitespace-only author_name should fail with ValidationError."""
    from django.core.exceptions import ValidationError

    book = book_factory.build(
        title="Test Book",
        author_name="   ",
        unit_price=Decimal("29.99"),
    )
    with pytest.raises(ValidationError) as exc_info:
        book.full_clean()
    assert "author_name" in exc_info.value.message_dict
    assert "cannot be empty" in str(exc_info.value.message_dict["author_name"][0])


@pytest.mark.unit
def test_clean_author_name_with_spaces(book_factory):
    """Test creating book with author_name containing leading/trailing spaces"""
    book = book_factory.build(
        author_name="  John Doe  ",
    )
    assert book.author_name == "  John Doe  "


@pytest.mark.unit
def test_clean_validation_messages(book_factory):
    """Test exact error messages for title and author_name validation."""
    from django.core.exceptions import ValidationError

    book = book_factory.create(
        title="   ",
        author_name="   ",
        unit_price=Decimal("29.99"),
    )
    with pytest.raises(ValidationError) as exc_info:
        book.full_clean()

    errors = exc_info.value.message_dict
    assert "title" in errors
    assert "author_name" in errors
    assert "Title cannot be empty or contain only spaces." in str(errors["title"])
    assert "Author name cannot be empty or contain only spaces." in str(
        errors["author_name"]
    )


########################################
# NULLABLE FIELDS TESTS                #
########################################


@pytest.mark.unit
def test_description_null(book_factory):
    """Test creating book with description=None."""
    book = book_factory.build(description=None)
    assert book.description is None


@pytest.mark.unit
def test_description_empty_string(book_factory):
    """Test creating book with empty description."""
    book = book_factory.build(description="")
    assert book.description == ""


@pytest.mark.unit
def test_publisher_name_null(book_factory):
    """Test creating book with publisher_name=None."""
    book = book_factory.build(publisher_name=None)
    assert book.publisher_name is None


@pytest.mark.unit
def test_publisher_name_empty_string(book_factory):
    """Test creating book with empty publisher_name."""
    book = book_factory.build(publisher_name="")
    assert book.publisher_name == ""


@pytest.mark.unit
def test_published_date_null(book_factory):
    """Test creating book with published_date=None."""
    book = book_factory.build(published_date=None)
    assert book.published_date is None


@pytest.mark.unit
def test_photo_path_null(book_factory):
    """Test creating book with photo_path=None."""
    book = book_factory.build(photo_path=None)
    assert book.photo_path is None


########################################
# RATING FIELDS TESTS                  #
########################################


@pytest.mark.unit
def test_total_rating_value_default(book_factory):
    """Test book created without setting rating value has default=0."""
    book = book_factory.build()
    assert book.total_rating_value == 0


@pytest.mark.unit
def test_total_rating_count_default(book_factory):
    """Test book created without setting rating count has default=0."""
    book = book_factory.build()
    assert book.total_rating_count == 0


@pytest.mark.unit
def test_update_rating_values(book_factory):
    """Test updating total_rating_value and total_rating_count."""
    book = book_factory.create()
    book.total_rating_value = 45
    book.total_rating_count = 10
    book.save()

    book.refresh_from_db()
    assert book.total_rating_value == 45
    assert book.total_rating_count == 10


@pytest.mark.unit
def test_negative_rating_value(book_factory):
    """Test setting negative total_rating_value - allowed as no validator."""
    book = book_factory.build(total_rating_value=-1)
    assert book.total_rating_value == -1


@pytest.mark.unit
def test_negative_rating_count(book_factory):
    """Test setting negative total_rating_count - allowed as no validator."""
    book = book_factory.build(total_rating_count=-1)
    assert book.total_rating_count == -1


########################################
# FOREIGN KEY TESTS                    #
########################################


@pytest.mark.unit
def test_book_category_relationship(book_factory, category_factory):
    """Test book-category relationship."""
    category = category_factory.build(name="Fiction")
    book = book_factory.build(title="Test Book", category=category)

    assert book.category == category
    assert book.category.name == "Fiction"


@pytest.mark.unit
@pytest.mark.django_db(transaction=True)
def test_book_with_nonexistent_category(book_model):
    """Test creating book with invalid category_id should fail."""
    from django.db import IntegrityError
    from django.db import connection

    book = book_model(
        title="Test Book",
        author_name="John Doe",
        unit_price=Decimal("29.99"),
        category_id=99999,
    )

    with pytest.raises(IntegrityError):
        book.save()
        if "postgresql" in connection.vendor:
            with connection.cursor() as cursor:
                cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")


@pytest.mark.unit
def test_category_protect_on_delete(book_factory, category_factory):
    """Test that deleting a category with books fails with ProtectedError."""
    from django.db.models import ProtectedError

    category = category_factory.create()
    book_factory.create(category=category)

    with pytest.raises(ProtectedError):
        category.delete()


@pytest.mark.unit
def test_category_books_reverse_relation(book_factory, category_factory):
    """Test accessing books through category's reverse relation."""
    category = category_factory.create()
    book1 = book_factory.create(title="Book 1", category=category)
    book2 = book_factory.create(title="Book 2", category=category)

    books = list(category.books.all())
    assert len(books) == 2
    assert book1 in books
    assert book2 in books


@pytest.mark.unit
def test_book_category_null(book_factory):
    """Test creating book with category=None should fail."""
    from django.db import IntegrityError

    with pytest.raises(IntegrityError):
        book_factory.create(
            title="Test Book",
            author_name="John Doe",
            unit_price=Decimal("29.99"),
            category=None,
        )


########################################
# TIMESTAMP TESTS                      #
########################################


@pytest.mark.unit
def test_created_at_auto_set(book_factory):
    """Test that created_at is automatically set when creating a book."""
    from django.utils import timezone

    before = timezone.now()
    book = book_factory.create()
    after = timezone.now()

    assert book.created_at is not None
    assert before <= book.created_at <= after


@pytest.mark.unit
def test_updated_at_auto_set(book_factory):
    """Test that updated_at is automatically set when creating a book."""
    from django.utils import timezone

    before = timezone.now()
    book = book_factory.create()
    after = timezone.now()

    assert book.updated_at is not None
    assert before <= book.updated_at <= after


@pytest.mark.unit
def test_updated_at_changes_on_update(book_factory):
    """Test that updated_at changes when updating a book."""
    import time

    book = book_factory.create()
    original_updated_at = book.updated_at
    time.sleep(0.1)

    book.title = "Updated Title"
    book.save()

    assert book.updated_at > original_updated_at


@pytest.mark.unit
def test_created_at_unchanged_on_update(book_factory):
    """Test that created_at stays the same when updating a book."""
    book = book_factory.create()
    original_created_at = book.created_at

    book.title = "Updated Title"
    book.save()

    assert book.created_at == original_created_at


########################################
# MODEL META TESTS                     #
########################################


@pytest.mark.unit
def test_db_table_name(book_model):
    """Test that the database table name is 'books'."""
    assert book_model._meta.db_table == "books"


@pytest.mark.unit
def test_default_ordering(book_factory, category_factory):
    """Test that books are ordered by -created_at, -updated_at by default."""
    import time

    # Create a single category to avoid duplicate name errors
    category = category_factory.create()

    book1 = book_factory.create(title="Book 1", category=category)
    time.sleep(0.1)
    book2 = book_factory.create(title="Book 2", category=category)
    time.sleep(0.1)
    book3 = book_factory.create(title="Book 3", category=category)

    books = list(book_factory._meta.model.objects.all())

    assert books[0].id == book3.id
    assert books[1].id == book2.id
    assert books[2].id == book1.id


@pytest.mark.unit
def test_title_index_exists(book_model):
    """Test that database index exists on title field."""
    indexes = book_model._meta.indexes

    title_index_exists = any("title" in index.fields for index in indexes)

    assert title_index_exists, "Index on 'title' field not found"


@pytest.mark.unit
def test_author_name_index_exists(book_model):
    """Test that database index exists on author_name field."""
    indexes = book_model._meta.indexes

    author_index_exists = any("author_name" in index.fields for index in indexes)

    assert author_index_exists, "Index on 'author_name' field not found"


########################################
# STRING REPRESENTATION TESTS          #
########################################


@pytest.mark.unit
def test_str_method_returns_title(book_factory):
    """Test that str(book) returns the book title."""
    book = book_factory.create(title="The Great Gatsby")
    assert str(book) == "The Great Gatsby"


@pytest.mark.unit
def test_str_method_unicode_title(book_factory):
    """Test that str(book) works with unicode titles."""
    book = book_factory.create(title="本のタイトル")
    assert str(book) == "本のタイトル"


@pytest.mark.unit
def test_str_method_special_characters(book_factory):
    """Test that str(book) works with special characters."""
    title_with_special = 'Book\'s Title: "Special" Characters! @#$%'
    book = book_factory.create(title=title_with_special)
    assert str(book) == title_with_special


########################################
# DATE FIELD TESTS                     #
########################################


@pytest.mark.unit
def test_published_date_valid_date(book_factory):
    """Test creating book with valid published_date."""
    from datetime import date

    pub_date = date(2023, 6, 15)
    book = book_factory.create(published_date=pub_date)
    assert book.published_date == pub_date


@pytest.mark.unit
def test_published_date_future_date(book_factory):
    """Test creating book with future published_date."""
    from datetime import date, timedelta

    future_date = date.today() + timedelta(days=365)
    book = book_factory.create(published_date=future_date)
    assert book.published_date == future_date


@pytest.mark.unit
def test_published_date_past_date(book_factory):
    """Test creating book with past published_date."""
    from datetime import date

    past_date = date(1900, 1, 1)
    book = book_factory.create(published_date=past_date)
    assert book.published_date == past_date


@pytest.mark.unit
def test_published_date_invalid_format(book_factory):
    """Test creating book with invalid date format should fail."""
    from django.core.exceptions import ValidationError

    book = book_factory.build()
    book.published_date = "invalid-date"

    with pytest.raises(ValidationError):
        book.full_clean()


########################################
# EDGE CASES                           #
########################################


@pytest.mark.unit
def test_very_long_description(book_factory):
    """Test creating book with very long description."""
    long_description = "A" * 10000
    book = book_factory.create(description=long_description)
    assert book.description == long_description
    assert len(book.description) == 10000


@pytest.mark.unit
def test_unit_price_very_small(book_factory):
    """Test creating book with very small unit_price."""
    book = book_factory.create(unit_price=Decimal("0.01"))
    assert book.unit_price == Decimal("0.01")


@pytest.mark.unit
def test_unit_price_boundary(book_factory):
    """Test creating book with unit_price at boundary."""
    book = book_factory.create(unit_price=Decimal("99999999.99"))
    assert book.unit_price == Decimal("99999999.99")


@pytest.mark.unit
def test_unicode_in_all_text_fields(book_factory):
    """Test creating book with unicode in all text fields."""
    book = book_factory.create(
        title="日本語のタイトル",
        author_name="山田太郎",
        publisher_name="出版社名",
        description="これは日本語の説明です。",
    )
    assert book.title == "日本語のタイトル"
    assert book.author_name == "山田太郎"
    assert book.publisher_name == "出版社名"
    assert book.description == "これは日本語の説明です。"


@pytest.mark.unit
def test_special_characters_in_text_fields(book_factory):
    """Test creating book with special characters in all text fields."""
    book = book_factory.create(
        title="Title with 'quotes' and \"double quotes\"",
        author_name="O'Brien & Smith",
        publisher_name="Publisher & Co., Ltd.",
        description="Description with special chars: !@#$%^&*()",
    )
    assert book.title == "Title with 'quotes' and \"double quotes\""
    assert book.author_name == "O'Brien & Smith"
    assert book.publisher_name == "Publisher & Co., Ltd."
    assert book.description == "Description with special chars: !@#$%^&*()"


########################################
# UPDATE TESTS                         #
########################################


@pytest.mark.unit
def test_update_book_title(book_factory):
    """Test updating existing book title."""
    book = book_factory.create(title="Original Title")
    book.title = "Updated Title"
    book.save()

    book.refresh_from_db()
    assert book.title == "Updated Title"


@pytest.mark.unit
def test_update_book_category(book_factory, category_factory):
    """Test changing book to different category."""
    category1 = category_factory.create(name="Fiction")
    category2 = category_factory.create(name="Non-Fiction")

    book = book_factory.create(category=category1)
    assert book.category == category1

    book.category = category2
    book.save()

    book.refresh_from_db()
    assert book.category == category2


@pytest.mark.unit
def test_update_book_unit_price(book_factory):
    """Test updating book price."""
    book = book_factory.create(unit_price=Decimal("19.99"))
    book.unit_price = Decimal("24.99")
    book.save()

    book.refresh_from_db()
    assert book.unit_price == Decimal("24.99")


@pytest.mark.unit
def test_update_book_to_invalid_price(book_factory):
    """Test updating book to negative price should fail."""
    from django.core.exceptions import ValidationError

    book = book_factory.create(unit_price=Decimal("19.99"))
    book.unit_price = Decimal("-5.00")

    with pytest.raises(ValidationError):
        book.full_clean()


@pytest.mark.unit
def test_bulk_update_books(book_factory, category_factory):
    """Test bulk updating multiple books at once."""
    category = category_factory.create()

    books = [
        book_factory.create(unit_price=Decimal("10.00"), category=category)
        for _ in range(3)
    ]

    for book in books:
        book.unit_price = Decimal("15.00")

    book_factory._meta.model.objects.bulk_update(books, ["unit_price"])

    for book in books:
        book.refresh_from_db()
        assert book.unit_price == Decimal("15.00")


########################################
# QUERY TESTS                          #
########################################


@pytest.mark.unit
def test_filter_books_by_category(book_factory, category_factory):
    """Test filtering books by specific category."""
    fiction = category_factory.create(name="Fiction")

    fiction_books = [book_factory.create(category=fiction) for _ in range(3)]

    result = list(book_factory._meta.model.objects.filter(category=fiction))
    assert len(result) == 3
    for book in fiction_books:
        assert book in result


@pytest.mark.unit
def test_filter_books_by_author_name(book_factory, category_factory):
    """Test filtering books by author_name."""
    category = category_factory.create()

    author_books = [
        book_factory.create(author_name="Stephen King", category=category)
        for _ in range(2)
    ]

    result = list(book_factory._meta.model.objects.filter(author_name="Stephen King"))
    assert len(result) == 2
    for book in author_books:
        assert book in result


@pytest.mark.unit
def test_filter_books_by_price_range(book_factory, category_factory):
    """Test filtering books by unit_price range."""
    category = category_factory.create()

    cheap_book = book_factory.create(unit_price=Decimal("9.99"), category=category)
    medium_book = book_factory.create(unit_price=Decimal("19.99"), category=category)
    expensive_book = book_factory.create(unit_price=Decimal("29.99"), category=category)

    result = list(
        book_factory._meta.model.objects.filter(
            unit_price__gte=Decimal("10.00"), unit_price__lte=Decimal("25.00")
        )
    )

    assert len(result) == 1
    assert medium_book in result
    assert cheap_book not in result
    assert expensive_book not in result


@pytest.mark.unit
def test_search_books_by_title_icontains(book_factory, category_factory):
    """Test searching books with title__icontains."""
    category = category_factory.create()

    python_books = [
        book_factory.create(title="Learning Python", category=category),
        book_factory.create(title="Python Cookbook", category=category),
        book_factory.create(title="Advanced PYTHON Programming", category=category),
    ]
    other_book = book_factory.create(title="Java Programming", category=category)

    result = list(book_factory._meta.model.objects.filter(title__icontains="python"))

    assert len(result) == 3
    for book in python_books:
        assert book in result
    assert other_book not in result

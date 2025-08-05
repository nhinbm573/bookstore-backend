import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
import time


########################################
# BASIC MODEL CREATION AND VALIDATION  #
########################################


@pytest.mark.unit
def test_create_comment_with_all_fields(comment_factory, account_factory, book_factory):
    """Test creating comment with rating, content, account, book."""
    account = account_factory.create()
    book = book_factory.create()

    comment = comment_factory.create(
        rating=4, content="This is a great book!", account=account, book=book
    )

    assert comment.rating == 4
    assert comment.content == "This is a great book!"
    assert comment.account == account
    assert comment.book == book
    assert comment.pk is not None


@pytest.mark.unit
def test_create_comment_without_content(comment_factory, account_factory, book_factory):
    """Test creating comment with rating, account, book (content=null)."""
    account = account_factory.create()
    book = book_factory.create()

    comment = comment_factory.create(rating=3, content=None, account=account, book=book)

    assert comment.rating == 3
    assert comment.content is None
    assert comment.account == account
    assert comment.book == book


@pytest.mark.unit
def test_create_comment_without_rating(comment_model, account_factory, book_factory):
    """Test creating comment without rating should fail."""
    account = account_factory.create()
    book = book_factory.create()

    with pytest.raises(ValidationError):
        comment_model.objects.create(content="Great book!", account=account, book=book)


@pytest.mark.unit
def test_create_comment_without_account(comment_model, book_factory):
    """Test creating comment without account should fail with IntegrityError."""
    book = book_factory.create()

    with pytest.raises(ValidationError):
        comment_model.objects.create(rating=4, content="Great book!", book=book)


@pytest.mark.unit
def test_create_comment_without_book(comment_model, account_factory):
    """Test creating comment without book should fail with IntegrityError."""
    account = account_factory.create()

    with pytest.raises(ValidationError):
        comment_model.objects.create(rating=4, content="Great book!", account=account)


@pytest.mark.unit
def test_comment_date_auto_set(comment_factory):
    """Test that comment_date is set automatically when creating a comment."""
    before = timezone.now()
    comment = comment_factory.create()
    after = timezone.now()

    assert comment.comment_date is not None
    assert before <= comment.comment_date <= after


########################################
# RATING VALIDATION TESTS              #
########################################


@pytest.mark.unit
def test_rating_value_1(comment_factory):
    """Test creating comment with rating=1."""
    comment = comment_factory.create(rating=1)
    comment.full_clean()
    assert comment.rating == 1


@pytest.mark.unit
def test_rating_value_2(comment_factory):
    """Test creating comment with rating=2."""
    comment = comment_factory.create(rating=2)
    comment.full_clean()
    assert comment.rating == 2


@pytest.mark.unit
def test_rating_value_3(comment_factory):
    """Test creating comment with rating=3."""
    comment = comment_factory.create(rating=3)
    comment.full_clean()
    assert comment.rating == 3


@pytest.mark.unit
def test_rating_value_4(comment_factory):
    """Test creating comment with rating=4."""
    comment = comment_factory.create(rating=4)
    comment.full_clean()
    assert comment.rating == 4


@pytest.mark.unit
def test_rating_value_5(comment_factory):
    """Test creating comment with rating=5."""
    comment = comment_factory.create(rating=5)
    comment.full_clean()
    assert comment.rating == 5


@pytest.mark.unit
def test_rating_value_0(comment_factory):
    """Test creating comment with rating=0 should fail with ValidationError."""
    comment = comment_factory.build(rating=0)

    with pytest.raises(ValidationError) as exc_info:
        comment.full_clean()

    assert "rating" in exc_info.value.message_dict


@pytest.mark.unit
def test_rating_value_6(comment_factory):
    """Test creating comment with rating=6 should fail with ValidationError."""
    comment = comment_factory.build(rating=6)

    with pytest.raises(ValidationError) as exc_info:
        comment.full_clean()

    assert "rating" in exc_info.value.message_dict


@pytest.mark.unit
def test_rating_value_negative(comment_factory):
    """Test creating comment with rating=-1 should fail with ValidationError."""
    comment = comment_factory.build(rating=-1)

    with pytest.raises(ValidationError) as exc_info:
        comment.full_clean()

    assert "rating" in exc_info.value.message_dict


@pytest.mark.unit
def test_rating_min_validator_message(comment_factory):
    """Test error message for rating below minimum."""
    comment = comment_factory.build(rating=0)

    with pytest.raises(ValidationError) as exc_info:
        comment.full_clean()

    assert "Rating must be at least 1" in str(exc_info.value.message_dict["rating"])


@pytest.mark.unit
def test_rating_max_validator_message(comment_factory):
    """Test error message for rating above maximum."""
    comment = comment_factory.build(rating=6)

    with pytest.raises(ValidationError) as exc_info:
        comment.full_clean()

    assert "Rating cannot exceed 5" in str(exc_info.value.message_dict["rating"])


########################################
# CLEAN METHOD VALIDATION TESTS        #
########################################


@pytest.mark.unit
def test_clean_rating_string_value(comment_factory):
    """Test creating comment with rating as string should fail."""
    comment = comment_factory.build()
    comment.rating = "abc"

    with pytest.raises(ValidationError) as exc_info:
        comment.full_clean()

    assert "rating" in exc_info.value.message_dict


@pytest.mark.unit
def test_clean_rating_float_value(comment_factory):
    """Test creating comment with rating=3.5 gets converted to 3."""
    comment = comment_factory.create()
    comment.rating = 3.5
    comment.full_clean()
    assert comment.rating == 3


@pytest.mark.unit
def test_clean_rating_decimal_value(comment_factory):
    """Test creating comment with rating=4.0 (is_integer returns True)."""
    comment = comment_factory.create()
    comment.rating = 4.0
    comment.full_clean()
    assert comment.rating == 4.0


@pytest.mark.unit
def test_clean_rating_out_of_range_message(comment_factory):
    """Test error message for rating out of range."""
    comment = comment_factory.build()
    comment.rating = 10

    with pytest.raises(ValidationError) as exc_info:
        comment.full_clean()

    assert "Rating must be between 1 and 5." in str(
        exc_info.value.message_dict["rating"]
    )


@pytest.mark.unit
def test_clean_rating_float_1_0(comment_factory):
    """Test creating comment with rating=1.0."""
    comment = comment_factory.create()
    comment.rating = 1.0
    comment.full_clean()
    assert comment.rating == 1.0


@pytest.mark.unit
def test_clean_rating_float_5_0(comment_factory):
    """Test creating comment with rating=5.0."""
    comment = comment_factory.create()
    comment.rating = 5.0
    comment.full_clean()
    assert comment.rating == 5.0


@pytest.mark.unit
def test_clean_rating_none_value(comment_model, account_factory, book_factory):
    """Test creating comment with rating=None should fail."""
    comment = comment_model(
        rating=None,
        content="Test",
        account=account_factory.create(),
        book=book_factory.create(),
    )

    with pytest.raises(ValidationError):
        comment.full_clean()


########################################
# CONTENT FIELD TESTS                  #
########################################


@pytest.mark.unit
def test_content_null(comment_factory):
    """Test creating comment with content=None."""
    comment = comment_factory.create(content=None)
    assert comment.content is None


@pytest.mark.unit
def test_content_empty_string(comment_factory):
    """Test creating comment with content=''."""
    comment = comment_factory.create(content="")
    assert comment.content == ""


@pytest.mark.unit
def test_content_blank_true(comment_factory):
    """Test that blank=True allows empty string."""
    comment = comment_factory.create(content="")
    comment.full_clean()  # Should not raise
    assert comment.content == ""


@pytest.mark.unit
def test_content_long_text(comment_factory):
    """Test creating comment with 5000+ character content."""
    long_content = "A" * 5000
    comment = comment_factory.create(content=long_content)
    assert comment.content == long_content
    assert len(comment.content) == 5000


@pytest.mark.unit
def test_content_unicode_text(comment_factory):
    """Test creating comment with unicode content."""
    unicode_content = "S�oƹ�gY"
    comment = comment_factory.create(content=unicode_content)
    assert comment.content == unicode_content


@pytest.mark.unit
def test_content_special_characters(comment_factory):
    """Test creating comment with special characters in content."""
    special_content = "Great book! @#$%^&*() 'quotes' \"double quotes\""
    comment = comment_factory.create(content=special_content)
    assert comment.content == special_content


########################################
# FOREIGN KEY RELATIONSHIP TESTS       #
########################################


@pytest.mark.unit
def test_account_cascade_delete(comment_factory, account_factory):
    """Test that deleting account also deletes its comments."""
    account = account_factory.create()
    comment = comment_factory.create(account=account)
    comment_id = comment.id

    account.delete()

    assert not comment_factory._meta.model.objects.filter(id=comment_id).exists()


@pytest.mark.unit
def test_book_cascade_delete(comment_factory, book_factory):
    """Test that deleting book also deletes its comments."""
    book = book_factory.create()
    comment = comment_factory.create(book=book)
    comment_id = comment.id

    book.delete()

    assert not comment_factory._meta.model.objects.filter(id=comment_id).exists()


@pytest.mark.unit
def test_account_comments_reverse_relation(
    comment_factory, account_factory, category_factory
):
    """Test accessing comments through account's reverse relation."""
    account = account_factory.create()
    category = category_factory()
    comment1 = comment_factory.create(account=account, book__category=category)
    comment2 = comment_factory.create(account=account, book__category=category)

    comments = list(account.comments.all())
    assert len(comments) == 2
    assert comment1 in comments
    assert comment2 in comments


@pytest.mark.unit
def test_book_comments_reverse_relation(comment_factory, book_factory):
    """Test accessing comments through book's reverse relation."""
    book = book_factory.create()
    comment1 = comment_factory.create(book=book, rating=5)
    comment2 = comment_factory.create(book=book, rating=4)

    comments = list(book.comments.all())
    assert len(comments) == 2
    assert comment1 in comments
    assert comment2 in comments


@pytest.mark.unit
def test_comment_with_deleted_account(comment_factory, account_factory):
    """Test accessing comment.account after account deletion."""
    account = account_factory.create()
    comment = comment_factory.create(account=account)

    account.delete()

    # Comment should be deleted due to CASCADE
    with pytest.raises(comment_factory._meta.model.DoesNotExist):
        comment_factory._meta.model.objects.get(id=comment.id)


@pytest.mark.unit
def test_comment_with_deleted_book(comment_factory, book_factory):
    """Test accessing comment.book after book deletion."""
    book = book_factory.create()
    comment = comment_factory.create(book=book)

    book.delete()

    # Comment should be deleted due to CASCADE
    with pytest.raises(comment_factory._meta.model.DoesNotExist):
        comment_factory._meta.model.objects.get(id=comment.id)


@pytest.mark.unit
def test_db_column_account_id(comment_model):
    """Test that foreign key column name is 'account_id'."""
    account_field = comment_model._meta.get_field("account")
    assert account_field.db_column == "account_id"


@pytest.mark.unit
def test_db_column_book_id(comment_model):
    """Test that foreign key column name is 'book_id'."""
    book_field = comment_model._meta.get_field("book")
    assert book_field.db_column == "book_id"


########################################
# UNIQUE TOGETHER CONSTRAINT TESTS     #
########################################


@pytest.mark.unit
def test_unique_together_constraint(comment_factory, account_factory, book_factory):
    """Test that same account cannot comment on same book twice."""
    account = account_factory.create()
    book = book_factory.create()

    # Create first comment
    comment_factory.create(account=account, book=book, rating=4)

    # Try to create duplicate comment
    with pytest.raises(ValidationError):
        comment_factory.create(account=account, book=book, rating=5)


@pytest.mark.unit
def test_same_account_different_books(
    comment_factory, account_factory, book_factory, category_factory
):
    """Test that same account can comment on different books."""
    category = category_factory()
    account = account_factory.create()
    book1 = book_factory.create(category=category)
    book2 = book_factory.create(category=category)

    comment1 = comment_factory.create(account=account, book=book1)
    comment2 = comment_factory.create(account=account, book=book2)

    assert comment1.account == comment2.account
    assert comment1.book != comment2.book


@pytest.mark.unit
def test_different_accounts_same_book(comment_factory, account_factory, book_factory):
    """Test that different accounts can comment on same book."""
    account1 = account_factory.create()
    account2 = account_factory.create()
    book = book_factory.create()

    comment1 = comment_factory.create(account=account1, book=book)
    comment2 = comment_factory.create(account=account2, book=book)

    assert comment1.book == comment2.book
    assert comment1.account != comment2.account


@pytest.mark.unit
def test_update_comment_maintain_uniqueness(comment_factory):
    """Test updating existing comment rating and content."""
    comment = comment_factory.create(rating=3, content="Good")

    comment.rating = 5
    comment.content = "Excellent!"
    comment.save()

    comment.refresh_from_db()
    assert comment.rating == 5
    assert comment.content == "Excellent!"


@pytest.mark.unit
def test_unique_constraint_database_level(comment_model, account_factory, book_factory):
    """Test unique constraint at database level."""
    account = account_factory.create()
    book = book_factory.create()

    comment_model.objects.create(rating=4, account=account, book=book)

    with pytest.raises(ValidationError):
        comment_model.objects.create(rating=5, account=account, book=book)


########################################
# MODEL META TESTS                     #
########################################


@pytest.mark.unit
def test_db_table_name(comment_model):
    """Test that the database table name is 'comments'."""
    assert comment_model._meta.db_table == "comments"


@pytest.mark.unit
def test_default_ordering_newest_first(comment_factory, category_factory):
    """Test that comments are ordered by -comment_date by default."""
    category = category_factory()

    comment1 = comment_factory.create(book__category=category)
    time.sleep(0.1)
    comment2 = comment_factory.create(book__category=category)
    time.sleep(0.1)
    comment3 = comment_factory.create(book__category=category)

    comments = list(comment_factory._meta.model.objects.all())

    # Newest first
    assert comments[0].id == comment3.id
    assert comments[1].id == comment2.id
    assert comments[2].id == comment1.id


@pytest.mark.unit
def test_ordering_comment_date_descending(comment_factory, category_factory):
    """Test that older comments appear last."""
    import time

    category = category_factory()

    old_comment = comment_factory.create(book__category=category)
    time.sleep(0.1)

    new_comment = comment_factory.create(book__category=category)
    comments = list(comment_factory._meta.model.objects.all())

    assert comments[0].id == new_comment.id
    assert comments[1].id == old_comment.id
    assert new_comment.comment_date > old_comment.comment_date


########################################
# STRING REPRESENTATION TESTS          #
########################################


@pytest.mark.unit
def test_str_method_format(comment_factory, account_factory, book_factory):
    """Test __str__ method format."""
    account = account_factory.create(email="test@example.com")
    book = book_factory.create(title="Test Book")
    comment = comment_factory.create(account=account, book=book, rating=4)

    expected = f"{account} - Test Book (4)"
    assert str(comment) == expected


@pytest.mark.unit
def test_str_method_rating_1_star(comment_factory):
    """Test __str__ with rating=1."""
    comment = comment_factory.create(rating=1)
    str_repr = str(comment)
    assert "(1)" in str_repr


@pytest.mark.unit
def test_str_method_rating_5_stars(comment_factory):
    """Test __str__ with rating=5."""
    comment = comment_factory.create(rating=5)
    str_repr = str(comment)
    assert "(5)" in str_repr


@pytest.mark.unit
def test_str_method_unicode_book_title(comment_factory, book_factory):
    """Test __str__ with unicode book title."""
    book = book_factory.create(title=",n����")
    comment = comment_factory.create(book=book)
    str_repr = str(comment)
    assert ",n����" in str_repr


@pytest.mark.unit
def test_str_method_long_book_title(comment_factory, book_factory):
    """Test __str__ with very long book title."""
    long_title = "A" * 200
    book = book_factory.create(title=long_title)
    comment = comment_factory.create(book=book)
    str_repr = str(comment)
    assert long_title in str_repr


########################################
# TIMESTAMP TESTS                      #
########################################


@pytest.mark.unit
def test_comment_date_auto_now_add(comment_factory):
    """Test that comment_date is automatically set on creation."""
    comment = comment_factory.create()
    assert comment.comment_date is not None


@pytest.mark.unit
def test_comment_date_not_editable(comment_factory):
    """Test that comment_date is set on creation and doesn't change on updates."""
    comment = comment_factory.create()
    original_date = comment.comment_date

    comment.rating = 5
    comment.content = "Updated content"
    comment.save()

    comment.refresh_from_db()
    assert comment.comment_date == original_date
    assert comment.rating == 5
    assert comment.content == "Updated content"


@pytest.mark.unit
def test_comment_date_timezone_aware(comment_factory):
    """Test that comment_date is timezone-aware."""
    comment = comment_factory.create()
    assert timezone.is_aware(comment.comment_date)


@pytest.mark.unit
def test_comment_date_precision(comment_factory):
    """Test that comment_date includes microseconds."""
    comment = comment_factory.create()
    assert comment.comment_date.microsecond is not None


########################################
# EDGE CASES                           #
########################################


@pytest.mark.unit
def test_rating_boundary_1(comment_factory):
    """Test exact boundary rating=1."""
    comment = comment_factory.create(rating=1)
    comment.full_clean()
    assert comment.rating == 1


@pytest.mark.unit
def test_rating_boundary_5(comment_factory):
    """Test exact boundary rating=5."""
    comment = comment_factory.create(rating=5)
    comment.full_clean()  # Should not raise
    assert comment.rating == 5


@pytest.mark.unit
def test_rating_just_below_min(comment_factory):
    """Test rating=0.99 should fail."""
    comment = comment_factory.build()
    comment.rating = 0.99

    with pytest.raises(ValidationError):
        comment.full_clean()


@pytest.mark.unit
def test_rating_just_above_max(comment_factory):
    """Test rating=5.01 should fail."""
    comment = comment_factory.build()
    comment.rating = 5.01

    with pytest.raises(ValidationError):
        comment.full_clean()


@pytest.mark.unit
def test_rating_very_large_number(comment_factory):
    """Test rating=999999 should fail."""
    comment = comment_factory.build(rating=999999)

    with pytest.raises(ValidationError):
        comment.full_clean()


@pytest.mark.unit
def test_rating_very_small_number(comment_factory):
    """Test rating=-999999 should fail."""
    comment = comment_factory.build(rating=-999999)

    with pytest.raises(ValidationError):
        comment.full_clean()


########################################
# FULL CLEAN TESTS                     #
########################################


@pytest.mark.unit
def test_full_clean_valid_comment(comment_factory):
    """Test full_clean() on valid comment."""
    comment = comment_factory.create(rating=3, content="Good book")
    comment.full_clean()  # Should not raise


@pytest.mark.unit
def test_full_clean_invalid_rating_type(comment_factory):
    """Test full_clean() with string rating."""
    comment = comment_factory.build()
    comment.rating = "five"

    with pytest.raises(ValidationError):
        comment.full_clean()


@pytest.mark.unit
def test_full_clean_invalid_rating_range(comment_factory):
    """Test full_clean() with rating=10."""
    comment = comment_factory.build(rating=10)

    with pytest.raises(ValidationError):
        comment.full_clean()


@pytest.mark.unit
def test_full_clean_without_required_fields(comment_model):
    """Test full_clean() without account/book."""
    comment = comment_model(rating=4)

    with pytest.raises(ValidationError) as exc_info:
        comment.full_clean()

    assert "account" in exc_info.value.message_dict
    assert "book" in exc_info.value.message_dict


@pytest.mark.unit
def test_model_save_calls_clean(comment_factory):
    """Test that clean() is called during model save."""
    comment = comment_factory.create()
    comment.rating = "invalid"

    # Save should fail because clean() is called
    with pytest.raises(ValidationError):
        comment.save()


########################################
# UPDATE TESTS                         #
########################################


@pytest.mark.unit
def test_update_comment_rating(comment_factory):
    """Test updating existing comment rating from 3 to 5."""
    comment = comment_factory.create(rating=3)

    comment.rating = 5
    comment.save()

    comment.refresh_from_db()
    assert comment.rating == 5


@pytest.mark.unit
def test_update_comment_content(comment_factory):
    """Test updating existing comment content."""
    comment = comment_factory.create(content="Original content")

    comment.content = "Updated content"
    comment.save()

    comment.refresh_from_db()
    assert comment.content == "Updated content"


@pytest.mark.unit
def test_update_comment_invalid_rating(comment_factory):
    """Test updating existing comment rating to 0."""
    comment = comment_factory.create(rating=4)
    comment.rating = 0

    with pytest.raises(ValidationError):
        comment.full_clean()


@pytest.mark.unit
def test_update_comment_to_duplicate(
    comment_factory, account_factory, book_factory, category_factory
):
    """Test updating comment to create duplicate account/book combination."""
    account = account_factory.create()
    category = category_factory()

    book1 = book_factory.create(category=category)
    book2 = book_factory.create(category=category)

    comment_factory.create(account=account, book=book1)
    comment2 = comment_factory.create(account=account, book=book2)
    comment2.book = book1

    with pytest.raises(ValidationError):
        comment2.save()


@pytest.mark.unit
def test_bulk_update_comments(comment_factory, category_factory):
    """Test bulk updating multiple comments at once."""
    category = category_factory()

    comments = [
        comment_factory.create(rating=3, book__category=category) for _ in range(3)
    ]

    for comment in comments:
        comment.rating = 5

    comment_factory._meta.model.objects.bulk_update(comments, ["rating"])

    for comment in comments:
        comment.refresh_from_db()
        assert comment.rating == 5


########################################
# QUERY TESTS                          #
########################################


@pytest.mark.unit
def test_filter_comments_by_rating(comment_factory, category_factory):
    """Test filtering comments with rating=5."""
    category = category_factory()

    comment_factory.create(rating=5, book__category=category)
    comment_factory.create(rating=5, book__category=category)
    comment_factory.create(rating=3, book__category=category)
    comment_factory.create(rating=4, book__category=category)

    five_star_comments = list(comment_factory._meta.model.objects.filter(rating=5))
    assert len(five_star_comments) == 2


@pytest.mark.unit
def test_filter_comments_by_account(comment_factory, account_factory, category_factory):
    """Test filtering all comments by specific account."""
    category = category_factory()

    account1 = account_factory.create()
    account2 = account_factory.create()

    comment_factory.create(account=account1, book__category=category)
    comment_factory.create(account=account1, book__category=category)
    comment_factory.create(account=account2, book__category=category)

    account1_comments = list(
        comment_factory._meta.model.objects.filter(account=account1)
    )
    assert len(account1_comments) == 2


@pytest.mark.unit
def test_filter_comments_by_book(comment_factory, book_factory):
    """Test filtering all comments by specific book."""
    book1 = book_factory.create()
    book2 = book_factory.create()

    comment_factory.create(book=book1, rating=5)
    comment_factory.create(book=book1, rating=4)
    comment_factory.create(book=book2, rating=3)

    book1_comments = list(comment_factory._meta.model.objects.filter(book=book1))
    assert len(book1_comments) == 2


@pytest.mark.unit
def test_filter_comments_by_date_range(comment_factory, category_factory):
    """Test filtering comments within date range."""
    from datetime import timedelta

    now = timezone.now()
    week_ago = now - timedelta(days=7)
    category = category_factory()

    old_comment = comment_factory.create(book__category=category)

    comment_factory._meta.model.objects.filter(id=old_comment.id).update(
        comment_date=now - timedelta(days=10)
    )
    old_comment.refresh_from_db()

    recent_comment = comment_factory.create(book__category=category)

    recent_comments = list(
        comment_factory._meta.model.objects.filter(comment_date__gte=week_ago)
    )

    assert recent_comment in recent_comments
    assert old_comment not in recent_comments


@pytest.mark.unit
def test_aggregate_average_rating(comment_factory, book_factory):
    """Test calculating average rating for a book."""
    from django.db.models import Avg

    book = book_factory.create()
    comment_factory.create(book=book, rating=5)
    comment_factory.create(book=book, rating=4)
    comment_factory.create(book=book, rating=3)

    avg_rating = comment_factory._meta.model.objects.filter(book=book).aggregate(
        avg=Avg("rating")
    )["avg"]

    assert avg_rating == 4.0


########################################
# INTEGRATION TESTS                    #
########################################


@pytest.mark.unit
def test_comment_with_account_and_book(comment_factory):
    """Test that comment relationships work correctly."""
    comment = comment_factory.create()

    assert comment.account is not None
    assert comment.book is not None
    assert comment.account.comments.filter(id=comment.id).exists()
    assert comment.book.comments.filter(id=comment.id).exists()


@pytest.mark.unit
def test_comment_prevents_duplicate_review(
    comment_factory, account_factory, book_factory
):
    """Test that user cannot review same book twice."""
    account = account_factory.create()
    book = book_factory.create()

    comment_factory.create(account=account, book=book)

    with pytest.raises(ValidationError):
        comment_factory.create(account=account, book=book)


@pytest.mark.unit
def test_comment_allows_edit_existing(comment_factory):
    """Test that user can update their existing comment."""
    comment = comment_factory.create(rating=3, content="Initial review")

    comment.rating = 5
    comment.content = "Updated review - loved it!"
    comment.save()

    comment.refresh_from_db()
    assert comment.rating == 5
    assert comment.content == "Updated review - loved it!"


@pytest.mark.unit
def test_cascade_delete_behavior(comment_factory, account_factory, book_factory):
    """Test that cascade deletes work properly."""
    account = account_factory.create()
    book = book_factory.create()
    comment = comment_factory.create(account=account, book=book)
    comment_id = comment.id

    # Delete account - comment should be deleted
    account.delete()
    assert not comment_factory._meta.model.objects.filter(id=comment_id).exists()

    # Create new comment
    account2 = account_factory.create()
    comment2 = comment_factory.create(account=account2, book=book)
    comment2_id = comment2.id

    # Delete book - comment should be deleted
    book.delete()
    assert not comment_factory._meta.model.objects.filter(id=comment2_id).exists()


@pytest.mark.unit
def test_help_text_fields(comment_model):
    """Test help_text for rating and content fields."""
    rating_field = comment_model._meta.get_field("rating")
    content_field = comment_model._meta.get_field("content")

    assert rating_field.help_text == "Rating from 1 to 5"
    assert content_field.help_text == "Comment content"


########################################
# PERFORMANCE TESTS                    #
########################################


@pytest.mark.unit
def test_unique_together_index_performance(comment_model):
    """Test that unique_together creates an index for performance."""
    assert ["account", "book"] in comment_model._meta.unique_together or (
        "account",
        "book",
    ) in comment_model._meta.unique_together


@pytest.mark.unit
def test_ordering_by_date_performance(comment_model):
    """Test that ordering by comment_date is configured."""
    assert comment_model._meta.ordering == ["-comment_date"]


@pytest.mark.unit
def test_foreign_key_join_performance(comment_factory):
    """Test querying with select_related for performance."""
    comment = comment_factory.create()

    # Efficient query with select_related
    comment_with_relations = comment_factory._meta.model.objects.select_related(
        "account", "book"
    ).get(id=comment.id)

    # Access without additional queries
    assert comment_with_relations.account.email is not None
    assert comment_with_relations.book.title is not None

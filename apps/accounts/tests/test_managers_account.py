import pytest
from django.db import DataError
from datetime import date, timedelta

from apps.accounts.models import Account, AccountManager
from apps.accounts.tests.factories import AccountFactory


# Create User Method Tests
@pytest.mark.unit
@pytest.mark.django_db
def test_create_user_with_valid_data(account_model, valid_account_data):
    """Test user creation with all required fields."""
    user = account_model.objects.create_user(**valid_account_data)

    assert user.email == valid_account_data["email"]
    assert user.phone == valid_account_data["phone"]
    assert user.full_name == valid_account_data["full_name"]
    assert user.birthday == valid_account_data["birthday"]
    assert user.check_password(valid_account_data["password"])
    assert user.is_active is False
    assert user.is_admin is False


@pytest.mark.unit
@pytest.mark.django_db
@pytest.mark.parametrize(
    "input_email,expected_email",
    [
        ("TEST@EXAMPLE.COM", "TEST@example.com"),
        ("Test@Example.com", "Test@example.com"),
        ("  test@example.com  ", "test@example.com"),
    ],
)
def test_create_user_email_normalization(
    account_model, minimal_account_data, input_email, expected_email
):
    """Test email is lowercased/normalized."""
    data = minimal_account_data.copy()
    data["email"] = input_email
    data["password"] = "testpass123"

    user = account_model.objects.create_user(**data)
    assert user.email == expected_email


@pytest.mark.unit
@pytest.mark.django_db
def test_create_user_password_hashing(account_model, valid_account_data):
    """Test password is hashed, not stored plain."""
    password = valid_account_data["password"]
    user = account_model.objects.create_user(**valid_account_data)

    assert user.password != password
    assert user.password.startswith("pbkdf2_sha256$")
    assert user.check_password(password) is True


@pytest.mark.unit
def test_create_user_without_email(account_model, minimal_account_data):
    """Test raises ValueError when email is missing."""
    data = minimal_account_data.copy()
    data["email"] = ""

    with pytest.raises(ValueError, match="The Email field must be set"):
        account_model.objects.create_user(**data)


@pytest.mark.unit
@pytest.mark.django_db
def test_create_user_without_password(account_model, minimal_account_data):
    """Test user creation without password."""
    # Don't include password in data
    user = account_model.objects.create_user(**minimal_account_data)

    assert user.password
    assert not user.has_usable_password()


@pytest.mark.unit
@pytest.mark.parametrize(
    "field_to_remove,error_pattern",
    [
        ("phone", "The Phone field must be set"),
        ("full_name", "The Full Name field must be set"),
        ("birthday", "The Birthday field must be set"),
    ],
)
def test_create_user_missing_required_fields(
    account_model, valid_account_data, field_to_remove, error_pattern
):
    """Test errors for missing required fields."""
    data = valid_account_data.copy()
    data.pop(field_to_remove)

    with pytest.raises(
        (ValueError, TypeError),
        match=error_pattern if field_to_remove != "phone" else None,
    ):
        account_model.objects.create_user(**data)


@pytest.mark.unit
@pytest.mark.django_db
def test_create_user_sets_defaults(account_model, minimal_account_data):
    """Test is_active and is_admin default values."""
    user = account_model.objects.create_user(**minimal_account_data)

    assert user.is_active is False
    assert user.is_admin is False


@pytest.mark.unit
def test_create_user_rejects_is_admin_true(account_model, valid_account_data):
    """Test regular user cannot have is_admin=True."""
    data = valid_account_data.copy()
    data["is_admin"] = True

    with pytest.raises(ValueError, match="Regular user cannot have is_admin=True"):
        account_model.objects.create_user(**data)


# Create Superuser Method Tests
@pytest.mark.unit
@pytest.mark.django_db
def test_create_superuser_creation(account_model, superuser_data):
    """Test superuser creation with all fields."""
    superuser = account_model.objects.create_superuser(**superuser_data)

    assert superuser.email == superuser_data["email"]
    assert superuser.phone == superuser_data["phone"]
    assert superuser.full_name == superuser_data["full_name"]
    assert superuser.birthday == superuser_data["birthday"]
    assert superuser.check_password(superuser_data["password"])
    assert superuser.is_admin is True
    assert superuser.is_active is True


@pytest.mark.unit
@pytest.mark.django_db
def test_create_superuser_flags(account_model, superuser_data):
    """Test superuser has correct flags set."""
    superuser = account_model.objects.create_superuser(**superuser_data)

    assert superuser.is_admin is True
    assert superuser.is_active is True
    assert superuser.is_staff is True  # Should be True via property


@pytest.mark.unit
@pytest.mark.parametrize(
    "flag,value,error_pattern",
    [
        ("is_active", False, "Superuser must have is_active=True"),
        ("is_admin", False, "Superuser must have is_admin=True"),
    ],
)
def test_create_superuser_requires_flags(
    account_model, superuser_data, flag, value, error_pattern
):
    """Test superuser must have required flags."""
    data = superuser_data.copy()
    data[flag] = value

    with pytest.raises(ValueError, match=error_pattern):
        account_model.objects.create_superuser(**data)


@pytest.mark.unit
@pytest.mark.parametrize(
    "field_to_remove,error_pattern",
    [
        ("email", "The Email field must be set"),
        ("phone", "The Phone field must be set"),
        ("full_name", "The Full Name field must be set"),
        ("birthday", "The Birthday field must be set"),
    ],
)
def test_create_superuser_missing_fields(
    account_model, superuser_data, field_to_remove, error_pattern
):
    """Test superuser creation with missing required fields."""
    data = superuser_data.copy()
    data.pop(field_to_remove)

    with pytest.raises(
        (ValueError, TypeError),
        match=error_pattern if field_to_remove != "email" else None,
    ):
        account_model.objects.create_superuser(**data)


# Manager QuerySet Methods Tests
@pytest.mark.unit
def test_manager_filter_active_users(db):
    """Test filtering active users using factory."""
    # Create users with factory
    active_users = AccountFactory.create_batch(3, active=True)
    inactive_users = AccountFactory.create_batch(2, inactive=True)

    # Query active users
    queryset = Account.objects.filter(is_active=True)

    assert queryset.count() == 3
    assert all(user in queryset for user in active_users)
    assert not any(user in queryset for user in inactive_users)


@pytest.mark.unit
def test_manager_filter_admin_users(db):
    """Test filtering admin users using factory."""
    # Create users with factory
    admin_users = AccountFactory.create_batch(2, admin=True)
    regular_users = AccountFactory.create_batch(3, is_admin=False)

    # Query admin users
    queryset = Account.objects.filter(is_admin=True)

    assert queryset.count() == 2
    assert all(user in queryset for user in admin_users)
    assert not any(user in queryset for user in regular_users)


@pytest.mark.unit
def test_manager_instance_type(account_model):
    """Test that the manager is correct type."""
    assert isinstance(account_model.objects, AccountManager)
    assert hasattr(account_model.objects, "create_user")
    assert hasattr(account_model.objects, "create_superuser")


# Field Validation Tests
@pytest.mark.unit
@pytest.mark.django_db
def test_phone_length_validation(
    account_model, minimal_account_data, invalid_field_data
):
    """Test phone field respects max_length at database level."""
    data = minimal_account_data.copy()
    data["phone"] = invalid_field_data["long_phone"]

    with pytest.raises((DataError, ValueError)):
        account_model.objects.create_user(**data)


@pytest.mark.unit
@pytest.mark.django_db
def test_full_name_length_validation(
    account_model, minimal_account_data, invalid_field_data
):
    """Test full_name field respects max_length at database level."""
    data = minimal_account_data.copy()
    data["full_name"] = invalid_field_data["long_name"]

    with pytest.raises((DataError, ValueError)):
        account_model.objects.create_user(**data)


@pytest.mark.unit
@pytest.mark.django_db
def test_birthday_accepts_valid_dates(account_model, minimal_account_data):
    """Test birthday accepts various valid date formats."""
    test_dates = [
        date(1990, 1, 1),
        date(2000, 12, 31),
        date.today() - timedelta(days=365 * 25),  # 25 years ago
    ]

    for idx, test_date in enumerate(test_dates):
        data = minimal_account_data.copy()
        data["birthday"] = test_date
        data["email"] = f"user_{idx}_{test_date.year}@example.com"

        user = account_model.objects.create_user(**data)
        assert user.birthday == test_date


@pytest.mark.unit
@pytest.mark.django_db
def test_future_birthday_accepted_by_manager(
    account_model, minimal_account_data, invalid_field_data
):
    """Test manager accepts future dates (validation should be in forms/serializers)."""
    data = minimal_account_data.copy()
    data["birthday"] = invalid_field_data["future_birthday"]

    # Manager will accept this
    user = account_model.objects.create_user(**data)
    assert user.birthday == invalid_field_data["future_birthday"]

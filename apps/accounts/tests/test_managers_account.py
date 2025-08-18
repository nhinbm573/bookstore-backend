import pytest
from datetime import date
from django.core.exceptions import ValidationError

#####################################
# ACCOUNTMANAGER CREATE_USER METHOD TESTS #
#####################################


@pytest.mark.unit
def test_create_user_success(account_model):
    """Test creating a regular user with all fields succeeds."""
    account = account_model.objects.create_user(
        email="newuser@example.com",
        phone="+1234567890",
        full_name="New User",
        birthday=date(1990, 1, 1),
        password="password123",
    )

    assert account.email == "newuser@example.com"
    assert account.phone == "+1234567890"
    assert account.full_name == "New User"
    assert account.birthday == date(1990, 1, 1)
    assert account.check_password("password123")
    assert account.is_active is False
    assert account.is_admin is False


@pytest.mark.unit
def test_create_user_default_inactive(account_model):
    """Test that created user has is_active=False by default."""
    account = account_model.objects.create_user(
        email="newuser@example.com",
        phone="+1234567890",
        full_name="New User",
        birthday=date(1990, 1, 1),
        password="password123",
    )

    assert account.is_active is False


@pytest.mark.unit
def test_create_user_default_not_admin(account_model):
    """Test that created user has is_admin=False by default."""
    account = account_model.objects.create_user(
        email="newuser@example.com",
        phone="+1234567890",
        full_name="New User",
        birthday=date(1990, 1, 1),
        password="password123",
    )

    assert account.is_admin is False


@pytest.mark.unit
def test_create_user_with_is_admin_true(account_model):
    """Test that creating regular user with is_admin=True raises ValueError."""
    with pytest.raises(ValueError, match="Regular user cannot have is_admin=True"):
        account_model.objects.create_user(
            email="newuser@example.com",
            phone="+1234567890",
            full_name="New User",
            birthday=date(1990, 1, 1),
            password="password123",
            is_admin=True,
        )


@pytest.mark.unit
def test_email_normalization_uppercase(account_model):
    """Test that email is normalized when uppercase."""
    account = account_model.objects.create_user(
        email="TEST@EXAMPLE.COM",
        phone="+1234567890",
        full_name="Test User",
        birthday=date(1990, 1, 1),
        password="password123",
    )

    assert account.email == "TEST@example.com"


@pytest.mark.unit
def test_email_normalization_mixed_case(account_model):
    """Test that email is normalized when mixed case."""
    account = account_model.objects.create_user(
        email="TeSt@ExAmPlE.com",
        phone="+1234567890",
        full_name="Test User",
        birthday=date(1990, 1, 1),
        password="password123",
    )

    assert account.email == "TeSt@example.com"


############################################
# ACCOUNTMANAGER CREATE_SUPERUSER METHOD TESTS #
############################################


@pytest.mark.unit
def test_create_superuser_success(account_model):
    """Test creating a superuser with all fields succeeds."""
    account = account_model.objects.create_superuser(
        email="admin@example.com",
        phone="+1234567890",
        full_name="Admin User",
        birthday=date(1990, 1, 1),
        password="adminpass123",
    )

    assert account.email == "admin@example.com"
    assert account.phone == "+1234567890"
    assert account.full_name == "Admin User"
    assert account.birthday == date(1990, 1, 1)
    assert account.check_password("adminpass123")
    assert account.is_active is True
    assert account.is_admin is True


@pytest.mark.unit
def test_create_superuser_is_active_true(account_model):
    """Test that created superuser has is_active=True by default."""
    account = account_model.objects.create_superuser(
        email="admin@example.com",
        phone="+1234567890",
        full_name="Admin User",
        birthday=date(1990, 1, 1),
        password="adminpass123",
    )

    assert account.is_active is True


@pytest.mark.unit
def test_create_superuser_is_admin_true(account_model):
    """Test that created superuser has is_admin=True by default."""
    account = account_model.objects.create_superuser(
        email="admin@example.com",
        phone="+1234567890",
        full_name="Admin User",
        birthday=date(1990, 1, 1),
        password="adminpass123",
    )

    assert account.is_admin is True


@pytest.mark.unit
def test_create_superuser_with_is_active_false(account_model):
    """Test that creating superuser with is_active=False raises ValueError."""
    with pytest.raises(ValueError, match="Superuser must have is_active=True"):
        account_model.objects.create_superuser(
            email="admin@example.com",
            phone="+1234567890",
            full_name="Admin User",
            birthday=date(1990, 1, 1),
            password="adminpass123",
            is_active=False,
        )


@pytest.mark.unit
def test_create_superuser_with_is_admin_false(account_model):
    """Test that creating superuser with is_admin=False raises ValueError."""
    with pytest.raises(ValueError, match="Superuser must have is_admin=True"):
        account_model.objects.create_superuser(
            email="admin@example.com",
            phone="+1234567890",
            full_name="Admin User",
            birthday=date(1990, 1, 1),
            password="adminpass123",
            is_admin=False,
        )


#################################
# MANAGER VALIDATION TESTS #
#################################


@pytest.mark.unit
def test_create_user_with_invalid_email_format(account_model):
    """Test creating user with invalid email format succeeds (no validation)."""
    account = account_model.objects.create_user(
        email="notanemail",
        phone="+1234567890",
        full_name="Test User",
        birthday=date(1990, 1, 1),
        password="password123",
    )

    assert account.email == "notanemail"


@pytest.mark.unit
def test_create_user_with_future_birthday(account_model):
    """Test that creating user with future birthday succeeds."""
    from datetime import timedelta
    from django.utils import timezone

    tomorrow = timezone.now().date() + timedelta(days=1)

    account = account_model.objects.create_user(
        email="future@example.com",
        phone="+1234567890",
        full_name="Future User",
        birthday=tomorrow,
        password="password123",
    )

    assert account.birthday == tomorrow


@pytest.mark.unit
def test_create_user_with_invalid_date_format(account_model):
    """Test that creating user with invalid date format fails."""
    with pytest.raises(ValidationError):
        account_model.objects.create_user(
            email="test@example.com",
            phone="+1234567890",
            full_name="Test User",
            birthday="not-a-date",
            password="password123",
        )

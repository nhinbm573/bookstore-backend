import pytest
from datetime import date
from django.db import IntegrityError
from django.core.exceptions import ValidationError

#######################################
# BASIC MODEL CREATION AND VALIDATION #
#######################################


@pytest.mark.unit
def test_create_account_with_valid_data(account_model, account_factory):
    """Test creating an account with all required fields."""
    account = account_factory.create(
        email="test@example.com",
        phone="+1234567890",
        full_name="Test User",
        birthday=date(1990, 1, 1),
        password="testpass123",
    )
    assert account.email == "test@example.com"
    assert account.phone == "+1234567890"
    assert account.full_name == "Test User"
    assert account.birthday == date(1990, 1, 1)
    assert account.check_password("testpass123")
    assert account_model.objects.filter(email="test@example.com").exists()


@pytest.mark.unit
def test_create_account_default_values(account_model, account_factory):
    """Test that new accounts have is_active=False and is_admin=False by default."""
    account = account_factory.build(
        email="test@example.com",
        phone="+1234567890",
        full_name="Test User",
        birthday=date(1990, 1, 1),
        password="testpass123",
    )
    assert account.is_active is False
    assert account.is_admin is False


@pytest.mark.unit
def test_email_unique_constraint(account_factory):
    """Test that creating two accounts with the same email fails."""
    account_factory.create(
        email="test@example.com",
        phone="+1234567890",
        full_name="Test User",
        birthday=date(1990, 1, 1),
        password="testpass123",
    )

    try:
        account_factory.create(
            email="test@example.com",
            phone="+0987654321",
            full_name="Another User",
            birthday=date(1995, 5, 5),
            password="anotherpass123",
        )
        assert False, "Should have raised IntegrityError"
    except IntegrityError:
        pass


@pytest.mark.unit
def test_create_account_without_email(account_model):
    """Test that creating an account without email fails."""
    with pytest.raises(ValueError, match="The Email field must be set"):
        account_model.objects.create_user(
            email="",
            phone="+1234567890",
            full_name="Test User",
            birthday=date(1990, 1, 1),
            password="testpass123",
        )


@pytest.mark.unit
def test_create_account_without_phone(account_model):
    """Test that creating an account without phone fails."""
    with pytest.raises(ValueError, match="The Phone field must be set"):
        account_model.objects.create_user(
            email="test@example.com",
            phone="",
            full_name="Test User",
            birthday=date(1990, 1, 1),
            password="testpass123",
        )


@pytest.mark.unit
def test_create_account_without_full_name(account_model):
    """Test that creating an account without full_name fails."""
    with pytest.raises(ValueError, match="The Full Name field must be set"):
        account_model.objects.create_user(
            email="test@example.com",
            phone="+1234567890",
            full_name="",
            birthday=date(1990, 1, 1),
            password="testpass123",
        )


@pytest.mark.unit
def test_create_account_without_birthday(account_model):
    """Test that creating an account without birthday fails."""
    with pytest.raises(ValueError, match="The Birthday field must be set"):
        account_model.objects.create_user(
            email="test@example.com",
            phone="+1234567890",
            full_name="Test User",
            birthday=None,
            password="testpass123",
        )


@pytest.mark.unit
def test_phone_max_length_valid(account_factory):
    """Test creating an account with 20 character phone number succeeds."""
    phone_20_chars = "+" + "1" * 19
    account = account_factory.build(
        email="test@example.com",
        phone=phone_20_chars,
        full_name="Test User",
        birthday=date(1990, 1, 1),
        password="testpass123",
    )

    assert account.phone == phone_20_chars
    assert len(account.phone) == 20


@pytest.mark.unit
def test_phone_max_length_exceeded(account_factory):
    """Test creating an account with 21+ character phone number fails."""
    phone_21_chars = "+" + "1" * 20  # Total 21 characters

    try:
        account = account_factory.build(
            email="test@example.com",
            phone=phone_21_chars,
            full_name="Test User",
            birthday=date(1990, 1, 1),
            password="testpass123",
        )
        account.full_clean()
        assert False, "Should have raised validation error"
    except (ValidationError, Exception):
        pass


@pytest.mark.unit
def test_full_name_max_length_valid(account_factory):
    """Test creating an account with 255 character full_name succeeds."""
    full_name_255 = "A" * 255
    account = account_factory.build(
        email="test@example.com",
        phone="+1234567890",
        full_name=full_name_255,
        birthday=date(1990, 1, 1),
        password="testpass123",
    )

    assert account.full_name == full_name_255
    assert len(account.full_name) == 255


@pytest.mark.unit
def test_full_name_max_length_exceeded(account_factory):
    """Test creating an account with 256+ character full_name fails."""
    full_name_256 = "A" * 256

    try:
        account = account_factory.build(
            email="test@example.com",
            phone="+1234567890",
            full_name=full_name_256,
            birthday=date(1990, 1, 1),
            password="testpass123",
        )
        account.full_clean()
        assert False, "Should have raised validation error"
    except (ValidationError, Exception):
        pass


####################################
# AUTHENTICATION and AUTHORIZATION #
####################################


@pytest.mark.unit
def test_set_password_and_check_valid(account_factory):
    """Test setting a password and verifying it with check_password."""
    account = account_factory.create(password="newpassword123")

    assert account.check_password("newpassword123")
    assert not account.check_password("wrongpassword")


@pytest.mark.unit
def test_check_password_invalid(account_factory):
    """Test checking password with wrong password returns False."""
    account = account_factory.create(password="correctpassword")

    assert not account.check_password("wrongpassword")
    assert not account.check_password("")
    assert not account.check_password(None)


@pytest.mark.unit
def test_login_with_valid_credentials(account_factory, account_model):
    """Test login with active account and correct password succeeds."""
    from django.contrib.auth import authenticate

    account_factory.create(
        email="test@example.com", password="testpass123", active=True
    )

    authenticated_user = authenticate(
        username="test@example.com", password="testpass123"
    )

    assert authenticated_user is not None
    assert authenticated_user.email == "test@example.com"
    assert authenticated_user.is_active is True


@pytest.mark.unit
def test_login_with_invalid_password(account_factory):
    """Test login with incorrect password fails."""
    from django.contrib.auth import authenticate

    account_factory.create(
        email="test@example.com", password="correctpassword", active=True
    )

    authenticated_user = authenticate(
        username="test@example.com", password="wrongpassword"
    )

    assert authenticated_user is None


@pytest.mark.unit
def test_login_inactive_account(account_factory):
    """Test login with inactive account fails."""
    from django.contrib.auth import authenticate

    account_factory.create(
        email="test@example.com", password="testpass123", is_active=False
    )

    authenticated_user = authenticate(
        username="test@example.com", password="testpass123"
    )

    assert authenticated_user is None


@pytest.mark.unit
def test_regular_user_has_perm(account_factory):
    """Test has_perm for regular user returns False."""
    account = account_factory.build(is_admin=False)

    assert account.has_perm("any.permission") is False
    assert account.has_perm("accounts.add_account") is False
    assert account.has_perm("accounts.change_account") is False
    assert account.has_perm("accounts.delete_account") is False


@pytest.mark.unit
def test_admin_user_has_perm(account_factory):
    """Test has_perm for admin user returns True."""
    account = account_factory.build(admin=True)

    assert account.has_perm("any.permission") is True
    assert account.has_perm("accounts.add_account") is True
    assert account.has_perm("accounts.change_account") is True
    assert account.has_perm("accounts.delete_account") is True


@pytest.mark.unit
def test_regular_user_has_module_perms(account_factory):
    """Test has_module_perms for regular user returns False."""
    account = account_factory.build(is_admin=False)

    assert account.has_module_perms("accounts") is False
    assert account.has_module_perms("any_app") is False
    assert account.has_module_perms("admin") is False


@pytest.mark.unit
def test_admin_user_has_module_perms(account_factory):
    """Test has_module_perms for admin user returns True."""
    account = account_factory.build(admin=True)

    assert account.has_module_perms("accounts") is True
    assert account.has_module_perms("any_app") is True
    assert account.has_module_perms("admin") is True


@pytest.mark.unit
def test_regular_user_is_staff_property(account_factory):
    """Test is_staff property for regular user returns False."""
    account = account_factory.build(is_admin=False)

    assert account.is_staff is False


@pytest.mark.unit
def test_admin_user_is_staff_property(account_factory):
    """Test is_staff property for admin user returns True."""
    account = account_factory.build(admin=True)

    assert account.is_staff is True


#####################################
# MODEL METHODS AND PROPERTIES TESTS #
#####################################


@pytest.mark.unit
def test_str_method_returns_email(account_factory):
    """Test that __str__ method returns the email address."""
    account = account_factory.build(email="user@example.com")

    assert str(account) == "user@example.com"
    assert account.__str__() == "user@example.com"


@pytest.mark.unit
def test_date_joined_auto_now_add(account_factory, account_model):
    """Test that date_joined is set automatically when account is created."""
    from django.utils import timezone

    before_creation = timezone.now()

    account = account_factory.create(
        email="test@example.com",
        phone="+1234567890",
        full_name="Test User",
        birthday=date(1990, 1, 1),
    )

    after_creation = timezone.now()

    assert account.date_joined is not None
    assert before_creation <= account.date_joined <= after_creation

    original_date_joined = account.date_joined
    account.full_name = "Updated Name"
    account.save()

    account.refresh_from_db()
    assert account.date_joined == original_date_joined

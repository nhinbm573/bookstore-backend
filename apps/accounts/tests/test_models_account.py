import pytest
from django.db.utils import IntegrityError
from django.db import models
from datetime import date
from freezegun import freeze_time

from apps.accounts.tests.factories import AccountFactory
from apps.accounts.models import AccountManager


@pytest.mark.unit
def test_email_field_is_unique(account_model):
    """Test email field is configured as unique."""
    email_field = account_model._meta.get_field('email')
    assert email_field.unique is True


@pytest.mark.unit
def test_email_uniqueness_constraint(account):
    """Test database enforces unique email at model level."""
    with pytest.raises(IntegrityError):
        AccountFactory(email=account.email)


@pytest.mark.unit
def test_email_field_type(account_model):
    """Test email field is EmailField type."""
    email_field = account_model._meta.get_field('email')
    assert isinstance(email_field, models.EmailField)


# Phone Field Tests
@pytest.mark.unit
def test_phone_field_max_length(account_model):
    """Test phone field max_length=20."""
    phone_field = account_model._meta.get_field('phone')
    assert phone_field.max_length == 20


@pytest.mark.unit
def test_phone_field_type(account_model):
    """Test phone field is CharField type."""
    phone_field = account_model._meta.get_field('phone')
    assert isinstance(phone_field, models.CharField)


# Full Name Field Tests
@pytest.mark.unit
def test_full_name_field_max_length(account_model):
    """Test full_name field max_length=255."""
    full_name_field = account_model._meta.get_field('full_name')
    assert full_name_field.max_length == 255


@pytest.mark.unit
def test_full_name_field_type(account_model):
    """Test full_name field is CharField type."""
    full_name_field = account_model._meta.get_field('full_name')
    assert isinstance(full_name_field, models.CharField)


# Birthday Field Tests
@pytest.mark.unit
def test_birthday_field_type(account_model):
    """Test birthday field is DateField type."""
    birthday_field = account_model._meta.get_field('birthday')
    assert isinstance(birthday_field, models.DateField)


# Boolean Fields Tests
@pytest.mark.unit
def test_is_active_default(account_model):
    """Test is_active default=False configuration."""
    is_active_field = account_model._meta.get_field('is_active')
    assert is_active_field.default is False


@pytest.mark.unit
def test_is_admin_default(account_model):
    """Test is_admin default=False configuration."""
    is_admin_field = account_model._meta.get_field('is_admin')
    assert is_admin_field.default is False


# Date Joined Field Tests
@pytest.mark.unit
def test_date_joined_auto_now_add(account_model):
    """Test date_joined auto_now_add=True is set."""
    date_joined_field = account_model._meta.get_field('date_joined')
    assert date_joined_field.auto_now_add is True


# Model Configuration Tests
@pytest.mark.unit
def test_meta_db_table(account_model):
    """Test table name is 'accounts'."""
    assert account_model._meta.db_table == 'accounts'


@pytest.mark.unit
def test_username_field(account_model):
    """Test USERNAME_FIELD = 'email'."""
    assert account_model.USERNAME_FIELD == 'email'


@pytest.mark.unit
def test_required_fields(account_model):
    """Test REQUIRED_FIELDS contains ['phone', 'full_name', 'birthday']."""
    expected_fields = ['phone', 'full_name', 'birthday']
    assert set(account_model.REQUIRED_FIELDS) == set(expected_fields)


@pytest.mark.unit
def test_custom_manager_assignment(account_model):
    """Test objects = AccountManager()."""
    assert isinstance(account_model.objects, AccountManager)


# Model Method Tests
@pytest.mark.unit
def test_str_method(account):
    """Test __str__ method returns email address."""
    assert str(account) == account.email


@pytest.mark.unit
@pytest.mark.parametrize("is_admin,expected", [
    (False, False),
    (True, True),
])
def test_has_perm_method(account, is_admin, expected):
    """Test has_perm returns correct value based on is_admin."""
    account.is_admin = is_admin
    account.save()
    assert account.has_perm('any_permission') is expected


@pytest.mark.unit
@pytest.mark.parametrize("is_admin,expected", [
    (False, False),
    (True, True),
])
def test_has_module_perms(account, is_admin, expected):
    """Test has_module_perms returns correct value based on is_admin."""
    account.is_admin = is_admin
    account.save()
    assert account.has_module_perms('any_app') is expected


@pytest.mark.unit
@pytest.mark.parametrize("is_admin,expected", [
    (False, False),
    (True, True),
])
def test_is_staff_property(account, is_admin, expected):
    """Test is_staff returns correct value based on is_admin."""
    account.is_admin = is_admin
    account.save()
    assert account.is_staff is expected


# Model Instance Tests
@pytest.mark.unit
@pytest.mark.django_db
def test_model_instance_creation(minimal_account_data, account_model):
    """Test creating instance with all required fields."""
    account = account_model.objects.create_user(**minimal_account_data)

    assert account.email == minimal_account_data['email']
    assert account.phone == minimal_account_data['phone']
    assert account.full_name == minimal_account_data['full_name']
    assert account.birthday == minimal_account_data['birthday']
    assert account.pk is not None


@pytest.mark.unit
@pytest.mark.django_db
def test_field_value_persistence(minimal_account_data, account_model):
    """Test saved values match input."""
    account = account_model.objects.create_user(**minimal_account_data)
    account.refresh_from_db()

    assert account.email == minimal_account_data['email']
    assert account.phone == minimal_account_data['phone']
    assert account.full_name == minimal_account_data['full_name']
    assert account.birthday == minimal_account_data['birthday']


@pytest.mark.unit
def test_boolean_field_updates(account):
    """Test changing is_active and is_admin."""
    # Initial state
    assert account.is_active is False
    assert account.is_admin is False

    # Update is_active
    account.is_active = True
    account.save()
    account.refresh_from_db()
    assert account.is_active is True

    # Update is_admin
    account.is_admin = True
    account.save()
    account.refresh_from_db()
    assert account.is_admin is True


@pytest.mark.unit
@pytest.mark.django_db
@freeze_time("2023-07-15 10:30:00")
def test_date_joined_auto_population(minimal_account_data, account_model):
    """Test timestamp is set on creation."""
    account = account_model.objects.create_user(**minimal_account_data)

    assert account.date_joined is not None
    assert account.date_joined.date() == date(2023, 7, 15)
    assert account.date_joined.hour == 10
    assert account.date_joined.minute == 30

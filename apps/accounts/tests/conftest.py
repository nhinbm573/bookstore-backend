import pytest
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from apps.accounts.tests.factories import AccountFactory, create_test_accounts_set

Account = get_user_model()


@pytest.fixture
def account_model():
    """Provide access to the Account model class."""
    return Account


@pytest.fixture
def account(db):
    """Create and return a single account instance."""
    return AccountFactory()


@pytest.fixture
def test_accounts(db):
    """Create and return the standard test account set."""
    return create_test_accounts_set()


@pytest.fixture
def minimal_account_data():
    """Provide minimal required data for account creation."""
    return {
        'email': 'minimal@example.com',
        'phone': '+1000000000',
        'full_name': 'Minimal User',
        'birthday': date(2000, 1, 1)
    }


@pytest.fixture
def valid_account_data():
    """Provide valid account data with password for manager tests."""
    return {
        'email': 'test@example.com',
        'phone': '+1234567890',
        'full_name': 'Test User',
        'birthday': date(1990, 1, 1),
        'password': 'testpass123'
    }


@pytest.fixture
def superuser_data():
    """Provide data for creating superuser."""
    return {
        'email': 'admin@example.com',
        'phone': '+1987654321',
        'full_name': 'Admin User',
        'birthday': date(1985, 5, 15),
        'password': 'adminpass123'
    }


@pytest.fixture
def invalid_field_data():
    """Provide various invalid field data for testing."""
    return {
        'long_phone': '+' + '1' * 25,  # Exceeds max_length of 20
        'long_name': 'A' * 260,  # Exceeds max_length of 255
        'future_birthday': date.today() + timedelta(days=365),
        'past_birthday': date(1900, 1, 1),
    }


@pytest.fixture
def email_variations():
    """Provide email variations for normalization testing."""
    return [
        ('Test@Example.com', 'test@example.com'),
        ('test@EXAMPLE.COM', 'test@example.com'),
        ('  test@example.com  ', 'test@example.com'),
        ('USER@DOMAIN.COM', 'user@domain.com'),
    ]


@pytest.fixture(autouse=True)
def reset_factory_sequence():
    """Reset factory sequence counter between tests."""
    AccountFactory.reset_sequence()

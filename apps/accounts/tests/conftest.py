import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.accounts.tests.factories import AccountFactory

Account = get_user_model()


@pytest.fixture
def account_model(db):
    """Provide access to the Account model class."""
    return Account


@pytest.fixture
def account_factory(db):
    """Provide access to the AccountFactory class."""
    return AccountFactory


@pytest.fixture
def valid_account(db):
    return {
        "email": "newuser@example.com",
        "password": "StrongPass123",
        "phone": "+1234567890",
        "full_name": "John Doe",
        "birthday": "1990-01-01",
    }


@pytest.fixture
def invalid_password_account(db):
    return {
        "email": "test@example.com",
        "password": "12345",
        "phone": "+1234567890",
        "full_name": "Test User",
        "birthday": "1990-01-01",
    }


@pytest.fixture
def invalid_email_account(db):
    return {
        "email": "invalid-email",
        "password": "ValidPass123",
        "phone": "+1234567890",
        "full_name": "Test User",
        "birthday": "1990-01-01",
    }


@pytest.fixture
def invalid_birthday_account(db):
    return {
        "email": "invalid-email",
        "password": "ValidPass123",
        "phone": "+1234567890",
        "full_name": "Test User",
        "birthday": "invalid-date",
    }


@pytest.fixture
def api_client(db):
    return APIClient()


@pytest.fixture
def active_account(db, account_factory):
    """Create an active account for testing."""
    account = account_factory.create(
        email="active@example.com", full_name="Active User", is_active=True
    )
    account.set_password("TestPassword123!")
    account.save()
    return account


@pytest.fixture
def inactive_account(db, account_factory):
    """Create an inactive account for testing."""
    account = account_factory.create(
        email="inactive@example.com", full_name="Inactive User", is_active=False
    )
    account.set_password("TestPassword123!")
    account.save()
    return account

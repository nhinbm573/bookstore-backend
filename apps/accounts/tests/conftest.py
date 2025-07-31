import pytest
from django.contrib.auth import get_user_model

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

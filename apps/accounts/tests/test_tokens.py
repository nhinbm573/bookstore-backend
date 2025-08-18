import pytest
from apps.accounts.tokens import account_activation_token


@pytest.mark.unit
def test_token_generation_and_validation(account_factory):
    """Test that a generated token can be validated for the same user."""
    user = account_factory(is_active=False)

    token = account_activation_token.make_token(user)
    is_valid = account_activation_token.check_token(user, token)

    assert token is not None
    assert is_valid is True


@pytest.mark.unit
def test_token_invalid_for_different_user(account_factory):
    """Test that a token for one user doesn't work for another user."""
    user1 = account_factory(is_active=False, email="user1@example.com")
    user2 = account_factory(is_active=False, email="user2@example.com")

    token = account_activation_token.make_token(user1)
    is_valid = account_activation_token.check_token(user2, token)

    assert is_valid is False


@pytest.mark.unit
def test_token_invalidated_after_activation(account_factory):
    """Test that token becomes invalid after user is activated."""
    user = account_factory(is_active=False)

    token = account_activation_token.make_token(user)

    user.is_active = True
    user.save()

    is_valid = account_activation_token.check_token(user, token)
    assert is_valid is False

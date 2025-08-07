import pytest
from unittest.mock import patch
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from apps.accounts.tokens import account_activation_token


@pytest.fixture
def inactive_user(account_factory):
    """Create an inactive user for activation testing."""
    return account_factory(is_active=False)


@pytest.fixture
def active_user(account_factory):
    """Create an already active user."""
    return account_factory(is_active=True)


@pytest.mark.unit
def test_account_activate_success(api_client, inactive_user):
    """Test successful account activation with valid token."""
    uid = urlsafe_base64_encode(force_bytes(inactive_user.pk))
    token = account_activation_token.make_token(inactive_user)
    url = reverse("account-activate", kwargs={"uidb64": uid, "token": token})

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["message"]
        == "Account activated successfully! You can now log in."
    )
    assert response.data["status"] == 200

    inactive_user.refresh_from_db()
    assert inactive_user.is_active is True


@pytest.mark.unit
def test_account_activate_already_active(api_client, active_user):
    """Test activation attempt on already active account."""
    uid = urlsafe_base64_encode(force_bytes(active_user.pk))
    token = account_activation_token.make_token(active_user)
    url = reverse("account-activate", kwargs={"uidb64": uid, "token": token})

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Account already activated."
    assert response.data["status"] == 200

    active_user.refresh_from_db()
    assert active_user.is_active is True


@pytest.mark.unit
def test_account_activate_invalid_token(api_client, inactive_user):
    """Test activation with invalid token."""
    uid = urlsafe_base64_encode(force_bytes(inactive_user.pk))
    invalid_token = "invalid-token-12345"
    url = reverse("account-activate", kwargs={"uidb64": uid, "token": invalid_token})

    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Activation link is invalid or has expired."
    assert response.data["status"] == 400

    inactive_user.refresh_from_db()
    assert inactive_user.is_active is False


@pytest.mark.unit
def test_account_activate_invalid_uid(api_client):
    """Test activation with invalid base64 uid."""
    invalid_uid = "invalid-uid-!!!"
    token = "some-token"
    url = reverse("account-activate", kwargs={"uidb64": invalid_uid, "token": token})

    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Activation link is invalid or has expired."
    assert response.data["status"] == 400


@pytest.mark.unit
def test_account_activate_nonexistent_user(api_client):
    """Test activation with uid pointing to non-existent user."""
    non_existent_uid = urlsafe_base64_encode(force_bytes(99999))
    token = "some-token"
    url = reverse(
        "account-activate", kwargs={"uidb64": non_existent_uid, "token": token}
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Activation link is invalid or has expired."
    assert response.data["status"] == 400


@pytest.mark.unit
def test_account_activate_expired_token(api_client, inactive_user):
    """Test activation with expired token."""
    uid = urlsafe_base64_encode(force_bytes(inactive_user.pk))

    with patch(
        "apps.accounts.tokens.account_activation_token.check_token"
    ) as mock_check_token:
        mock_check_token.return_value = False
        url = reverse(
            "account-activate", kwargs={"uidb64": uid, "token": "expired-token"}
        )

        response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Activation link is invalid or has expired."
    assert response.data["status"] == 400

    inactive_user.refresh_from_db()
    assert inactive_user.is_active is False


@pytest.mark.unit
def test_account_activate_method_not_allowed(api_client, inactive_user):
    """Test that only GET method is allowed for activation."""
    uid = urlsafe_base64_encode(force_bytes(inactive_user.pk))
    token = account_activation_token.make_token(inactive_user)
    url = reverse("account-activate", kwargs={"uidb64": uid, "token": token})

    # Test POST
    response = api_client.post(url, {})
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # Test PUT
    response = api_client.put(url, {})
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # Test DELETE
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # Test PATCH
    response = api_client.patch(url, {})
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # Verify user remains inactive (no activation occurred)
    inactive_user.refresh_from_db()
    assert inactive_user.is_active is False


@pytest.mark.unit
def test_account_activate_malformed_uid(api_client):
    """Test activation with malformed (non-base64) uid."""
    malformed_uid = "not-base64-encoded"
    token = "some-token"
    url = reverse("account-activate", kwargs={"uidb64": malformed_uid, "token": token})

    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Activation link is invalid or has expired."
    assert response.data["status"] == 400

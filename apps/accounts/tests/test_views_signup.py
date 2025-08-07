import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from apps.accounts.models import Account


@pytest.mark.unit
def test_signup_view_success(api_client, valid_account):
    """Test successful user registration with valid data."""
    url = reverse("signup")

    with patch("apps.accounts.views.send_activation_email.delay") as mock_send_email:
        response = api_client.post(url, valid_account, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert (
        response.data["message"]
        == "Registration successful. Please check your email to activate your account."
    )
    assert response.data["status"] == 201

    user = Account.objects.get(email=valid_account["email"])
    assert user.email == valid_account["email"]
    assert user.phone == valid_account["phone"]
    assert user.full_name == valid_account["full_name"]
    assert user.is_active is False

    mock_send_email.assert_called_once()


@pytest.mark.unit
def test_signup_view_duplicate_email(api_client, valid_account, account_factory):
    """Test registration fails with duplicate email."""
    account_factory(email=valid_account["email"])

    url = reverse("signup")
    response = api_client.post(url, valid_account, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.unit
def test_signup_view_invalid_password(api_client, invalid_password_account):
    """Test registration fails with password less than 6 characters."""
    url = reverse("signup")
    response = api_client.post(url, invalid_password_account, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data
    assert not Account.objects.filter(email=invalid_password_account["email"]).exists()


@pytest.mark.unit
def test_signup_view_invalid_email_format(api_client, invalid_email_account):
    """Test registration fails with invalid email format."""
    url = reverse("signup")
    response = api_client.post(url, invalid_email_account, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
    assert not Account.objects.filter(email=invalid_email_account["email"]).exists()


@pytest.mark.unit
def test_signup_view_missing_required_fields(api_client):
    """Test registration fails when required fields are missing."""
    url = reverse("signup")
    incomplete_data = {"email": "test@example.com", "password": "ValidPass123"}
    response = api_client.post(url, incomplete_data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "phone" in response.data
    assert "full_name" in response.data
    assert "birthday" in response.data


@pytest.mark.unit
def test_signup_view_invalid_birthday_format(api_client, invalid_birthday_account):
    """Test registration fails with invalid birthday format."""
    url = reverse("signup")
    response = api_client.post(url, invalid_birthday_account, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "birthday" in response.data


@pytest.mark.unit
def test_signup_view_empty_request_body(api_client):
    """Test registration fails with empty request body."""
    url = reverse("signup")
    response = api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
    assert "password" in response.data
    assert "phone" in response.data
    assert "full_name" in response.data
    assert "birthday" in response.data


@pytest.mark.unit
def test_signup_view_activation_email_sent(api_client, valid_account):
    """Test that activation email is sent with correct parameters."""
    url = reverse("signup")

    with (
        patch("apps.accounts.views.send_activation_email.delay") as mock_send_email,
        patch(
            "apps.accounts.views.account_activation_token.make_token"
        ) as mock_make_token,
    ):

        mock_make_token.return_value = "test-token"
        response = api_client.post(url, valid_account, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    mock_send_email.assert_called_once()
    call_args = mock_send_email.call_args[0]
    user = Account.objects.get(email=valid_account["email"])
    assert call_args[0] == user.id
    assert "/activate/" in call_args[1]
    assert "test-token" in call_args[1]


@pytest.mark.unit
def test_signup_view_method_not_allowed(api_client):
    """Test that only POST method is allowed for signup."""
    url = reverse("signup")

    response = api_client.get(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = api_client.put(url, {}, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = api_client.delete(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = api_client.patch(url, {}, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

import pytest
from unittest.mock import patch
from django.urls import reverse
from django.conf import settings
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_success_new_user(mock_verify, api_client):
    """Test successful Google Sign-In for a new user."""
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "newuser@gmail.com",
        "email_verified": True,
        "name": "New User",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(
            url, {"credential": "valid-google-token"}, format="json"
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Google Sign-In successful."
    assert response.data["status"] == 200
    assert "data" in response.data
    assert "access" in response.data["data"]
    assert "account" in response.data["data"]
    assert response.data["data"]["account"]["email"] == "newuser@gmail.com"
    assert response.data["data"]["account"]["full_name"] == "New User"
    assert response.data["data"]["account"]["is_google_user"] is True
    assert response.data["data"]["account"]["phone"] is None
    assert response.data["data"]["account"]["birthday"] is None


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_success_existing_user(
    mock_verify, api_client, account_factory
):
    """Test successful Google Sign-In for an existing Google user."""
    existing_user = account_factory.create(
        email="existinguser@gmail.com",
        is_google_user=True,
        google_id="123456789",
        is_active=True,
    )

    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "existinguser@gmail.com",
        "email_verified": True,
        "name": "Existing User",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(
            url, {"credential": "valid-google-token"}, format="json"
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Google Sign-In successful."
    assert response.data["data"]["account"]["id"] == existing_user.id
    assert response.data["data"]["account"]["email"] == existing_user.email


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_link_existing_email(
    mock_verify, api_client, account_factory
):
    """Test linking an existing email account to Google Sign-In."""
    existing_user = account_factory.create(
        email="user@gmail.com", is_google_user=False, google_id=None, is_active=True
    )

    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
        "name": "User Name",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(
            url, {"credential": "valid-google-token"}, format="json"
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Google Sign-In successful."

    existing_user.refresh_from_db()
    assert existing_user.is_google_user is True
    assert existing_user.google_id == "123456789"


@pytest.mark.unit
@pytest.mark.django_db
def test_google_signin_view_missing_credential(api_client):
    """Test Google Sign-In fails when credential is missing."""
    url = reverse("google-signin")
    response = api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Google Sign-In failed" in response.data["message"]


@pytest.mark.unit
@pytest.mark.django_db
def test_google_signin_view_empty_credential(api_client):
    """Test Google Sign-In fails when credential is empty."""
    url = reverse("google-signin")
    response = api_client.post(url, {"credential": ""}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Google Sign-In failed" in response.data["message"]


@pytest.mark.unit
@pytest.mark.django_db
def test_google_signin_view_not_configured(api_client):
    """Test error when GOOGLE_CLIENT_ID is not configured."""
    with patch.object(settings, "GOOGLE_CLIENT_ID", ""):
        url = reverse("google-signin")
        response = api_client.post(url, {"credential": "some-token"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["status"] == 400


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_invalid_issuer(mock_verify, api_client):
    """Test error when token issuer is invalid."""
    mock_verify.return_value = {
        "iss": "invalid-issuer.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(url, {"credential": "invalid-token"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid token issuer" in response.data["message"]


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_invalid_audience(mock_verify, api_client):
    """Test error when token audience doesn't match client ID."""
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "different-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(url, {"credential": "invalid-token"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid token audience" in response.data["message"]


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_unverified_email(mock_verify, api_client):
    """Test error when Google email is not verified."""
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": False,
        "name": "User Name",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(url, {"credential": "invalid-token"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email not verified" in response.data["message"]


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_conflict_google_id(
    mock_verify, api_client, account_factory
):
    """Test error when email is already linked to different Google account."""
    account_factory.create(
        email="user@gmail.com",
        is_google_user=True,
        google_id="987654321",
        is_active=True,
    )

    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
        "name": "User Name",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(
            url, {"credential": "valid-google-token"}, format="json"
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "different Google account" in response.data["message"]


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_token_verification_error(mock_verify, api_client):
    """Test handling of token verification errors."""
    mock_verify.side_effect = ValueError("Token expired")

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(url, {"credential": "expired-token"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid token" in response.data["message"]


@pytest.mark.unit
@pytest.mark.django_db
def test_google_signin_view_method_not_allowed(api_client):
    """Test that only POST method is allowed for Google Sign-In."""
    url = reverse("google-signin")

    response = api_client.get(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = api_client.put(url, {}, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = api_client.delete(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = api_client.patch(url, {}, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_updates_last_login(
    mock_verify, api_client, account_factory
):
    """Test that successful Google Sign-In updates the user's last_login field."""
    existing_user = account_factory.create(
        email="user@gmail.com",
        is_google_user=True,
        google_id="123456789",
        is_active=True,
    )
    existing_user.last_login = None
    existing_user.save()

    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
        "name": "User Name",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(
            url, {"credential": "valid-google-token"}, format="json"
        )

    assert response.status_code == status.HTTP_200_OK

    existing_user.refresh_from_db()
    assert existing_user.last_login is not None


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_jwt_tokens_valid(mock_verify, api_client):
    """Test that JWT tokens returned are valid and can be decoded."""
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
        "name": "User Name",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(
            url, {"credential": "valid-google-token"}, format="json"
        )

    assert response.status_code == status.HTTP_200_OK

    # Check refresh token in cookie
    assert "refresh_token" in response.cookies
    refresh_token = response.cookies["refresh_token"].value
    RefreshToken(refresh_token)

    # Check access token in response
    assert "access" in response.data["data"]
    access_token = response.data["data"]["access"]
    assert access_token is not None


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_cookie_settings(mock_verify, api_client):
    """Test that refresh token cookie has correct settings."""
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
        "name": "User Name",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(
            url, {"credential": "valid-google-token"}, format="json"
        )

    assert response.status_code == status.HTTP_200_OK

    # Check cookie settings
    cookie = response.cookies["refresh_token"]
    assert cookie["httponly"] is True
    assert cookie["samesite"] == "Lax"
    assert cookie["max-age"] == 60 * 60 * 24 * 7  # 7 days
    assert cookie["secure"] is True


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_response_structure(mock_verify, api_client):
    """Test the structure of successful Google Sign-In response."""
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
        "name": "User Name",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(
            url, {"credential": "valid-google-token"}, format="json"
        )

    assert response.status_code == status.HTTP_200_OK

    # Check response structure
    assert "message" in response.data
    assert "status" in response.data
    assert "data" in response.data

    # Check data structure
    data = response.data["data"]
    assert "access" in data
    assert "account" in data

    # Check account structure
    account = data["account"]
    expected_fields = [
        "id",
        "email",
        "full_name",
        "phone",
        "birthday",
        "is_google_user",
    ]
    for field in expected_fields:
        assert field in account


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_view_without_name(mock_verify, api_client):
    """Test Google Sign-In when name is not provided in token."""
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
        # No name field
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        url = reverse("google-signin")
        response = api_client.post(
            url, {"credential": "valid-google-token"}, format="json"
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["data"]["account"]["full_name"] == ""

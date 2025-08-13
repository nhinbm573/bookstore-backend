import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.unit
def test_login_view_success(api_client, account_factory):
    """Test successful login with valid credentials."""
    password = "TestPass123"
    account = account_factory.create(
        email="user@example.com", password=password, is_active=True
    )

    url = reverse("login")
    response = api_client.post(
        url, {"email": account.email, "password": password}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Login successful."
    assert response.data["status"] == 200
    assert "data" in response.data
    assert "access" in response.data["data"]
    assert "account" in response.data["data"]
    assert response.data["data"]["account"]["email"] == account.email
    assert response.data["data"]["account"]["id"] == account.id


@pytest.mark.unit
def test_login_view_invalid_credentials(api_client, account_factory):
    """Test login fails with invalid credentials."""
    account = account_factory.create(
        email="user@example.com", password="CorrectPass123", is_active=True
    )

    url = reverse("login")
    response = api_client.post(
        url, {"email": account.email, "password": "WrongPass123"}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Invalid credentials."
    assert response.data["status"] == 400


@pytest.mark.unit
def test_login_view_inactive_user(api_client, account_factory):
    """Test login fails for inactive user."""
    password = "TestPass123"
    account = account_factory.create(
        email="inactive@example.com", password=password, is_active=False
    )

    url = reverse("login")
    response = api_client.post(
        url, {"email": account.email, "password": password}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Invalid credentials."


@pytest.mark.unit
def test_login_view_nonexistent_user(api_client):
    """Test login fails for non-existent user."""
    url = reverse("login")
    response = api_client.post(
        url,
        {"email": "nonexistent@example.com", "password": "TestPass123"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Invalid credentials."


@pytest.mark.unit
def test_login_view_captcha_required_after_failed_attempts(api_client, account_factory):
    """Test that captcha is required after 3 failed login attempts."""
    account = account_factory.create(
        email="user@example.com", password="CorrectPass123", is_active=True
    )

    url = reverse("login")
    cache.clear()

    for i in range(3):
        response = api_client.post(
            url, {"email": account.email, "password": "WrongPassword"}, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        if i == 2:
            assert (
                response.data["message"]
                == "Invalid credentials. Captcha required for next attempt."
            )

    response = api_client.post(
        url, {"email": account.email, "password": "CorrectPass123"}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Captcha verification required" in response.data["message"]
    assert response.data.get("captcha_required") is True


@pytest.mark.unit
def test_login_view_with_valid_captcha(api_client, account_factory):
    """Test login succeeds with valid captcha after failed attempts."""
    password = "CorrectPass123"
    account = account_factory.create(
        email="user@example.com", password=password, is_active=True
    )

    url = reverse("login")
    cache.clear()

    for _ in range(3):
        api_client.post(
            url, {"email": account.email, "password": "WrongPassword"}, format="json"
        )

    with patch(
        "apps.accounts.serializers.LoginSerializer.verify_captcha"
    ) as mock_verify:
        mock_verify.return_value = True

        response = api_client.post(
            url,
            {
                "email": account.email,
                "password": password,
                "captcha": "valid-captcha-token",
            },
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Login successful."
    assert "data" in response.data
    assert "access" in response.data["data"]


@pytest.mark.unit
def test_login_view_with_invalid_captcha(api_client, account_factory):
    """Test login fails with invalid captcha."""
    password = "CorrectPass123"
    account = account_factory.create(
        email="user@example.com", password=password, is_active=True
    )

    url = reverse("login")
    cache.clear()

    for _ in range(3):
        api_client.post(
            url, {"email": account.email, "password": "WrongPassword"}, format="json"
        )

    with patch(
        "apps.accounts.serializers.LoginSerializer.verify_captcha"
    ) as mock_verify:
        mock_verify.return_value = False

        response = api_client.post(
            url,
            {
                "email": account.email,
                "password": password,
                "captcha": "invalid-captcha-token",
            },
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid captcha" in response.data["message"]
    assert response.data.get("captcha_required") is True


@pytest.mark.unit
def test_login_view_clears_failed_attempts_on_success(api_client, account_factory):
    """Test that failed attempts counter is cleared after successful login."""
    password = "CorrectPass123"
    account = account_factory.create(
        email="user@example.com", password=password, is_active=True
    )

    url = reverse("login")
    cache.clear()

    for _ in range(2):
        api_client.post(
            url, {"email": account.email, "password": "WrongPassword"}, format="json"
        )

    response = api_client.post(
        url, {"email": account.email, "password": password}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    response = api_client.post(
        url, {"email": account.email, "password": "WrongPassword"}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Invalid credentials."
    assert "captcha_required" not in response.data


@pytest.mark.unit
def test_login_view_missing_email(api_client):
    """Test login fails when email is missing."""
    url = reverse("login")
    response = api_client.post(url, {"password": "TestPass123"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.unit
def test_login_view_missing_password(api_client):
    """Test login fails when password is missing."""
    url = reverse("login")
    response = api_client.post(url, {"email": "user@example.com"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.unit
def test_login_view_empty_request_body(api_client):
    """Test login fails with empty request body."""
    url = reverse("login")
    response = api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.unit
def test_login_view_method_not_allowed(api_client):
    """Test that only POST method is allowed for login."""
    url = reverse("login")

    response = api_client.get(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = api_client.put(url, {}, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = api_client.delete(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = api_client.patch(url, {}, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.unit
def test_login_view_updates_last_login(api_client, account_factory):
    """Test that successful login updates the user's last_login field."""
    password = "TestPass123"
    account = account_factory.create(
        email="user@example.com", password=password, is_active=True
    )
    account.last_login = None
    account.save()

    url = reverse("login")
    response = api_client.post(
        url, {"email": account.email, "password": password}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    account.refresh_from_db()
    assert account.last_login is not None


@pytest.mark.unit
def test_login_view_jwt_tokens_valid(api_client, account_factory):
    """Test that JWT tokens returned are valid and can be decoded."""
    password = "TestPass123"
    account = account_factory.create(
        email="user@example.com", password=password, is_active=True
    )

    url = reverse("login")
    response = api_client.post(
        url, {"email": account.email, "password": password}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    assert "refresh_token" in response.cookies
    refresh_token = response.cookies["refresh_token"].value
    refresh = RefreshToken(refresh_token)
    assert refresh["user_id"] == account.id

    assert "access" in response.data["data"]
    access_token = response.data["data"]["access"]
    assert access_token is not None


@pytest.mark.unit
def test_verify_captcha_with_google_api(api_client):
    """Test captcha verification with Google reCAPTCHA API."""
    from apps.accounts.serializers import LoginSerializer

    serializer = LoginSerializer()

    with patch("apps.accounts.serializers.settings.RECAPTCHA_SECRET_KEY", ""):
        assert serializer.verify_captcha("any-token") is True

    with patch(
        "apps.accounts.serializers.settings.RECAPTCHA_SECRET_KEY", "test-secret"
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}

        with patch(
            "apps.accounts.serializers.requests.post", return_value=mock_response
        ) as mock_post:
            assert serializer.verify_captcha("valid-token") is True
            mock_post.assert_called_once_with(
                "https://www.google.com/recaptcha/api/siteverify",
                data={"secret": "test-secret", "response": "valid-token"},
                timeout=5,
            )

        mock_response.json.return_value = {"success": False}
        with patch(
            "apps.accounts.serializers.requests.post", return_value=mock_response
        ):
            assert serializer.verify_captcha("invalid-token") is False

        with patch(
            "apps.accounts.serializers.requests.post",
            side_effect=Exception("Network error"),
        ):
            assert serializer.verify_captcha("any-token") is False

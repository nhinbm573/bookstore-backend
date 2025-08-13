import pytest
from unittest.mock import patch, MagicMock, Mock
from django.core.cache import cache
from apps.accounts.serializers import LoginSerializer


@pytest.mark.unit
def test_login_serializer_valid_data(account_factory):
    """Test LoginSerializer with valid credentials."""
    password = "TestPass123"
    account = account_factory.create(
        email="user@example.com", password=password, is_active=True
    )

    request = Mock()
    request.META = {"REMOTE_ADDR": "127.0.0.1"}

    data = {"email": account.email, "password": password}
    serializer = LoginSerializer(data=data, context={"request": request})

    assert serializer.is_valid()
    assert serializer.validated_data["user"] == account


@pytest.mark.unit
def test_login_serializer_invalid_credentials(account_factory):
    """Test LoginSerializer with invalid password, non-existent user, and inactive user."""
    account = account_factory.create(
        email="user@example.com", password="CorrectPass", is_active=True
    )
    request = Mock()
    request.META = {"REMOTE_ADDR": "127.0.0.1"}

    data = {"email": account.email, "password": "WrongPass"}
    serializer = LoginSerializer(data=data, context={"request": request})
    assert not serializer.is_valid()
    assert serializer.errors["message"][0] == "Invalid credentials."

    data = {"email": "nonexistent@example.com", "password": "TestPass123"}
    serializer = LoginSerializer(data=data, context={"request": request})
    assert not serializer.is_valid()
    assert serializer.errors["message"][0] == "Invalid credentials."

    inactive_account = account_factory.create(
        email="inactive@example.com", password="TestPass123", is_active=False
    )
    data = {"email": inactive_account.email, "password": "TestPass123"}
    serializer = LoginSerializer(data=data, context={"request": request})
    assert not serializer.is_valid()
    assert serializer.errors["message"][0] == "Invalid credentials."


@pytest.mark.unit
def test_login_serializer_field_validation():
    """Test field requirements and validation."""
    serializer = LoginSerializer(data={})
    assert not serializer.is_valid()
    assert "email" in serializer.errors
    assert "password" in serializer.errors

    request = Mock()
    request.META = {"REMOTE_ADDR": "127.0.0.1"}
    data = {"email": "invalid-email", "password": "TestPass123"}
    serializer = LoginSerializer(data=data, context={"request": request})
    assert not serializer.is_valid()
    assert "email" in serializer.errors

    serializer = LoginSerializer()
    assert serializer.fields["password"].write_only is True

    expected_fields = ["email", "password", "captcha"]
    assert set(serializer.fields.keys()) == set(expected_fields)


@pytest.mark.unit
def test_login_serializer_failed_attempts_tracking(account_factory):
    """Test failed attempts tracking and captcha requirement."""
    account = account_factory.create(
        email="user@example.com", password="CorrectPass", is_active=True
    )
    request = Mock()
    request.META = {"REMOTE_ADDR": "127.0.0.1"}

    cache.clear()
    cache_key = f"failed_attempts:{account.email}:127.0.0.1"

    data = {"email": account.email, "password": "WrongPass"}
    for i in range(3):
        serializer = LoginSerializer(data=data, context={"request": request})
        serializer.is_valid()
        assert cache.get(cache_key) == i + 1
        if i == 2:
            assert (
                "Captcha required for next attempt" in serializer.errors["message"][0]
            )

    data = {"email": account.email, "password": "CorrectPass"}
    serializer = LoginSerializer(data=data, context={"request": request})
    assert not serializer.is_valid()
    assert "Captcha verification required" in serializer.errors["message"][0]


@pytest.mark.unit
def test_login_serializer_captcha_validation(account_factory):
    """Test captcha validation scenarios."""
    password = "CorrectPass123"
    account = account_factory.create(
        email="user@example.com", password=password, is_active=True
    )
    request = Mock()
    request.META = {"REMOTE_ADDR": "127.0.0.1"}

    cache.clear()
    cache_key = f"failed_attempts:{account.email}:127.0.0.1"
    cache.set(cache_key, 3, timeout=1800)

    with patch.object(LoginSerializer, "verify_captcha", return_value=True):
        data = {"email": account.email, "password": password, "captcha": "valid-token"}
        serializer = LoginSerializer(data=data, context={"request": request})
        assert serializer.is_valid()
        assert cache.get(cache_key) is None  # Failed attempts cleared

    cache.set(cache_key, 3, timeout=1800)

    with patch.object(LoginSerializer, "verify_captcha", return_value=False):
        data = {
            "email": account.email,
            "password": password,
            "captcha": "invalid-token",
        }
        serializer = LoginSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "Invalid captcha" in serializer.errors["message"][0]


@pytest.mark.unit
def test_verify_captcha_implementation():
    """Test captcha verification with Google reCAPTCHA."""
    serializer = LoginSerializer()

    with patch("apps.accounts.serializers.settings.RECAPTCHA_SECRET_KEY", ""):
        assert serializer.verify_captcha("any-token") is True

    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}
    with patch(
        "apps.accounts.serializers.settings.RECAPTCHA_SECRET_KEY", "test-secret"
    ):
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
        "apps.accounts.serializers.settings.RECAPTCHA_SECRET_KEY", "test-secret"
    ):
        with patch(
            "apps.accounts.serializers.requests.post", return_value=mock_response
        ):
            assert serializer.verify_captcha("invalid-token") is False

    with patch(
        "apps.accounts.serializers.settings.RECAPTCHA_SECRET_KEY", "test-secret"
    ):
        with patch(
            "apps.accounts.serializers.requests.post",
            side_effect=Exception("Network error"),
        ):
            assert serializer.verify_captcha("any-token") is False


@pytest.mark.unit
@pytest.mark.parametrize(
    "failed_attempts,expected_message",
    [
        (0, "Invalid credentials."),
        (1, "Invalid credentials."),
        (2, "Invalid credentials. Captcha required for next attempt."),
    ],
)
def test_login_serializer_progressive_error_messages(
    account_factory, failed_attempts, expected_message
):
    """Test that error messages change based on failed attempts count."""
    account = account_factory.create(
        email="user@example.com", password="CorrectPass", is_active=True
    )
    request = Mock()
    request.META = {"REMOTE_ADDR": "127.0.0.1"}

    cache.clear()

    if failed_attempts > 0:
        cache_key = f"failed_attempts:{account.email}:127.0.0.1"
        cache.set(cache_key, failed_attempts, timeout=1800)

    data = {"email": account.email, "password": "WrongPass"}
    serializer = LoginSerializer(data=data, context={"request": request})

    assert not serializer.is_valid()
    assert serializer.errors["message"][0] == expected_message

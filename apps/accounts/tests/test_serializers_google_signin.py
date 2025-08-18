import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.conf import settings
from apps.accounts.serializers import GoogleSignInSerializer

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_new_user(mock_verify):
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
        data = {"credential": "valid-google-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert serializer.is_valid()
        assert "user" in serializer.validated_data
        assert "idinfo" in serializer.validated_data

        user = serializer.validated_data["user"]
        assert user.email == "newuser@gmail.com"
        assert user.full_name == "New User"
        assert user.is_active is True
        assert user.is_google_user is True
        assert user.google_id == "123456789"
        assert user.phone is None
        assert user.birthday is None
        assert not user.has_usable_password()


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_existing_google_user(mock_verify, account_factory):
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
        data = {"credential": "valid-google-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.validated_data["user"]
        assert user.id == existing_user.id
        assert user.email == existing_user.email
        assert user.google_id == "123456789"


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_link_existing_email_account(mock_verify, account_factory):
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
        data = {"credential": "valid-google-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.validated_data["user"]
        assert user.id == existing_user.id
        assert user.is_google_user is True
        assert user.google_id == "123456789"


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_conflict_different_google_id(mock_verify, account_factory):
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
        data = {"credential": "valid-google-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert not serializer.is_valid()
        assert "message" in serializer.errors
        assert "different Google account" in serializer.errors["message"][0]


@pytest.mark.unit
def test_google_signin_field_validation():
    """Test field requirements and validation."""
    # Test missing credential
    serializer = GoogleSignInSerializer(data={})
    assert not serializer.is_valid()
    assert "credential" in serializer.errors

    # Test empty credential
    serializer = GoogleSignInSerializer(data={"credential": ""})
    assert not serializer.is_valid()
    assert "credential" in serializer.errors

    # Test serializer fields
    serializer = GoogleSignInSerializer()
    expected_fields = ["credential"]
    assert set(serializer.fields.keys()) == set(expected_fields)


@pytest.mark.unit
@pytest.mark.django_db
def test_google_signin_not_configured():
    """Test error when GOOGLE_CLIENT_ID is not configured."""
    with patch.object(settings, "GOOGLE_CLIENT_ID", ""):
        data = {"credential": "some-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert not serializer.is_valid()
        assert "message" in serializer.errors
        assert "not configured" in serializer.errors["message"][0]


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_invalid_issuer(mock_verify):
    """Test error when token issuer is invalid."""
    mock_verify.return_value = {
        "iss": "invalid-issuer.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        data = {"credential": "invalid-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert not serializer.is_valid()
        assert "message" in serializer.errors
        assert "Invalid token issuer" in serializer.errors["message"][0]


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_invalid_audience(mock_verify):
    """Test error when token audience doesn't match client ID."""
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "different-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        data = {"credential": "invalid-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert not serializer.is_valid()
        assert "message" in serializer.errors
        assert "Invalid token audience" in serializer.errors["message"][0]


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_missing_email(mock_verify):
    """Test error when email is missing from Google token."""
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email_verified": True,
        "name": "User Name",
        # Missing email field
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        data = {"credential": "invalid-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert not serializer.is_valid()
        assert "message" in serializer.errors
        assert "Email not found" in serializer.errors["message"][0]


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_unverified_email(mock_verify):
    """Test error when Google email is not verified."""
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": False,  # Not verified
        "name": "User Name",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        data = {"credential": "invalid-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert not serializer.is_valid()
        assert "message" in serializer.errors
        assert "email not verified" in serializer.errors["message"][0]


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_token_verification_errors(mock_verify):
    """Test handling of token verification errors."""
    # Test ValueError
    mock_verify.side_effect = ValueError("Token expired")

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        data = {"credential": "expired-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert not serializer.is_valid()
        assert "message" in serializer.errors
        assert "Invalid token" in serializer.errors["message"][0]
        assert "Token expired" in serializer.errors["message"][0]

    # Test generic Exception
    mock_verify.side_effect = Exception("Network error")

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        data = {"credential": "invalid-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert not serializer.is_valid()
        assert "message" in serializer.errors
        assert "Failed to verify Google token" in serializer.errors["message"][0]


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_without_name(mock_verify):
    """Test user creation when name is not provided in token."""
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
        # No name field
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        data = {"credential": "valid-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.validated_data["user"]
        assert user.full_name == ""  # Empty string when name not provided


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_both_issuer_formats(mock_verify):
    """Test that both Google issuer formats are accepted."""
    token_info = {
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
        "name": "User Name",
    }

    # Test with "accounts.google.com"
    mock_verify.return_value = {**token_info, "iss": "accounts.google.com"}

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        data = {"credential": "valid-token"}
        serializer = GoogleSignInSerializer(data=data)
        assert serializer.is_valid()

    # Clean up created user
    User.objects.filter(email="user@gmail.com").delete()

    # Test with "https://accounts.google.com"
    mock_verify.return_value = {**token_info, "iss": "https://accounts.google.com"}

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        data = {"credential": "valid-token"}
        serializer = GoogleSignInSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.unit
@pytest.mark.django_db
@patch("apps.accounts.serializers.id_token.verify_oauth2_token")
def test_google_signin_idinfo_in_validated_data(mock_verify):
    """Test that idinfo is included in validated data."""
    token_info = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "123456789",
        "email": "user@gmail.com",
        "email_verified": True,
        "name": "User Name",
        "picture": "https://example.com/photo.jpg",
        "given_name": "User",
        "family_name": "Name",
    }

    mock_verify.return_value = token_info

    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-client-id"):
        data = {"credential": "valid-token"}
        serializer = GoogleSignInSerializer(data=data)

        assert serializer.is_valid()
        assert "idinfo" in serializer.validated_data
        assert serializer.validated_data["idinfo"] == token_info

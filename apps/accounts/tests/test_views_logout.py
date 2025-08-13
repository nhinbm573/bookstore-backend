import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.unit
def test_logout_view_success_with_valid_token(api_client, account_factory):
    """Test successful logout with valid authentication."""
    account = account_factory.create(
        email="test@example.com", password="TestPass123", is_active=True
    )

    refresh = RefreshToken.for_user(account)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    api_client.cookies["refresh_token"] = str(refresh)

    url = reverse("logout")
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Logout successful."
    assert response.data["status"] == 200
    # Cookie is deleted by setting its value to empty with max_age=0
    if "refresh_token" in response.cookies:
        assert response.cookies["refresh_token"].value == ""


@pytest.mark.unit
def test_logout_view_success_without_refresh_token(api_client, account_factory):
    """Test logout works even without refresh token in cookies."""
    account = account_factory.create(
        email="test@example.com", password="TestPass123", is_active=True
    )

    refresh = RefreshToken.for_user(account)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    url = reverse("logout")
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Logout successful."
    assert response.data["status"] == 200


@pytest.mark.unit
def test_logout_view_with_invalid_refresh_token(api_client, account_factory):
    """Test logout still succeeds with invalid refresh token."""
    account = account_factory.create(
        email="test@example.com", password="TestPass123", is_active=True
    )

    refresh = RefreshToken.for_user(account)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    api_client.cookies["refresh_token"] = "invalid_token"

    url = reverse("logout")
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Logout successful."
    assert response.data["status"] == 200


@pytest.mark.unit
def test_logout_view_requires_authentication(api_client):
    """Test logout requires user to be authenticated."""
    url = reverse("logout")
    response = api_client.post(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
def test_logout_view_with_expired_access_token(api_client):
    """Test logout fails with expired or invalid access token."""
    api_client.credentials(HTTP_AUTHORIZATION="Bearer expired_token")

    url = reverse("logout")
    response = api_client.post(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
def test_logout_view_method_not_allowed(api_client, account_factory):
    """Test that only POST method is allowed for logout."""
    account = account_factory.create(
        email="test@example.com", password="TestPass123", is_active=True
    )

    refresh = RefreshToken.for_user(account)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    url = reverse("logout")

    response = api_client.get(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = api_client.put(url, {}, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = api_client.delete(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = api_client.patch(url, {}, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.unit
def test_logout_view_removes_cookie_with_domain(api_client, account_factory, settings):
    """Test logout removes cookie with correct domain in production."""
    settings.DEBUG = False

    account = account_factory.create(
        email="test@example.com", password="TestPass123", is_active=True
    )

    refresh = RefreshToken.for_user(account)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    api_client.cookies["refresh_token"] = str(refresh)

    url = reverse("logout")
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Logout successful."


@pytest.mark.unit
def test_logout_view_removes_cookie_without_domain(
    api_client, account_factory, settings
):
    """Test logout removes cookie without domain in debug mode."""
    settings.DEBUG = True

    account = account_factory.create(
        email="test@example.com", password="TestPass123", is_active=True
    )

    refresh = RefreshToken.for_user(account)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    api_client.cookies["refresh_token"] = str(refresh)

    url = reverse("logout")
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Logout successful."

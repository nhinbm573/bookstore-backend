import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
@pytest.mark.unit
def test_refresh_token_success(api_client, account_factory):
    """Test successful token refresh with valid refresh token"""
    account = account_factory.create(
        email="user@example.com", password="TestPass123", is_active=True
    )
    refresh = RefreshToken.for_user(account)

    api_client.cookies["refresh_token"] = str(refresh)

    url = reverse("refresh-token")
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Token refreshed successfully."
    assert "access" in response.data["data"]
    assert "account" in response.data["data"]
    assert response.data["data"]["account"]["email"] == account.email


@pytest.mark.django_db
@pytest.mark.unit
def test_refresh_token_no_cookie(api_client):
    """Test refresh token fails when no cookie is provided"""
    url = reverse("refresh-token")
    response = api_client.post(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["message"] == "No refresh token provided."


@pytest.mark.django_db
@pytest.mark.unit
def test_refresh_token_invalid_token(api_client):
    """Test refresh token fails with invalid token"""
    api_client.cookies["refresh_token"] = "invalid_token_12345"

    url = reverse("refresh-token")
    response = api_client.post(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["message"] == "Invalid or expired token."

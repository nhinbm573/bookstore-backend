import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.unit
def test_health_endpoint_returns_200(client):
    """Test that the health check endpoint returns 200 OK"""
    url = reverse("health-check")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

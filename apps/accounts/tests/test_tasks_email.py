import pytest
from unittest.mock import patch, MagicMock
from apps.accounts.tasks import send_activation_email


@pytest.mark.unit
def test_send_activation_email_success(account_factory):
    """Test successful sending of activation email."""
    user = account_factory(email="test@example.com")
    activation_link = "http://example.com/activate/abc123"

    with patch("apps.accounts.tasks.EmailMultiAlternatives") as mock_email_class:
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email

        result = send_activation_email(user.id, activation_link)

        assert result == f"Activation email sent successfully to {user.email}"
        mock_email_class.assert_called_once()
        mock_email.attach_alternative.assert_called_once()
        mock_email.send.assert_called_once()


@pytest.mark.unit
@pytest.mark.django_db
def test_send_activation_email_user_not_found():
    """Test sending email when user doesn't exist."""
    non_existent_user_id = 99999
    activation_link = "http://example.com/activate/abc123"

    result = send_activation_email(non_existent_user_id, activation_link)

    assert result == f"User with id {non_existent_user_id} not found"


@pytest.mark.unit
def test_send_activation_email_send_failure(account_factory):
    """Test handling of email send failure."""
    user = account_factory(email="test@example.com")
    activation_link = "http://example.com/activate/abc123"

    with patch("apps.accounts.tasks.EmailMultiAlternatives") as mock_email_class:
        mock_email = MagicMock()
        mock_email.send.side_effect = Exception("SMTP connection failed")
        mock_email_class.return_value = mock_email

        result = send_activation_email(user.id, activation_link)

        assert "Failed to send activation email: SMTP connection failed" in result


@pytest.mark.unit
def test_send_activation_email_template_rendering(account_factory):
    """Test that email templates are rendered with correct context."""
    user = account_factory(email="test@example.com", full_name="Test User")
    activation_link = "http://example.com/activate/abc123"

    with (
        patch("apps.accounts.tasks.render_to_string") as mock_render,
        patch("apps.accounts.tasks.EmailMultiAlternatives"),
    ):

        mock_render.return_value = "Rendered content"

        send_activation_email(user.id, activation_link)

        assert mock_render.call_count == 2

        html_call = mock_render.call_args_list[0]
        assert html_call[0][0] == "accounts/emails/activation_email.html"
        assert html_call[0][1]["user"].id == user.id
        assert html_call[0][1]["activation_link"] == activation_link

        text_call = mock_render.call_args_list[1]
        assert text_call[0][0] == "accounts/emails/activation_email.txt"
        assert text_call[0][1]["user"].id == user.id
        assert text_call[0][1]["activation_link"] == activation_link


@pytest.mark.unit
def test_send_activation_email_correct_email_params(account_factory):
    """Test that email is created with correct parameters."""
    user = account_factory(email="recipient@example.com")
    activation_link = "http://example.com/activate/abc123"

    with (
        patch("apps.accounts.tasks.render_to_string") as mock_render,
        patch("apps.accounts.tasks.EmailMultiAlternatives") as mock_email_class,
        patch("apps.accounts.tasks.settings") as mock_settings,
    ):

        mock_render.side_effect = ["<html>HTML content</html>", "Text content"]
        mock_settings.DEFAULT_FROM_EMAIL = "noreply@bookstore.com"
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email

        send_activation_email(user.id, activation_link)

        mock_email_class.assert_called_once_with(
            subject="Activate Your Bookstore Account",
            body="Text content",
            from_email="noreply@bookstore.com",
            to=[user.email],
        )

        mock_email.attach_alternative.assert_called_once_with(
            "<html>HTML content</html>", "text/html"
        )

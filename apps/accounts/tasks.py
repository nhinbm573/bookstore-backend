from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Account


@shared_task
def send_activation_email(user_id, activation_link):
    try:
        user = Account.objects.get(pk=user_id)

        subject = "Activate Your Bookstore Account"
        html_content = render_to_string(
            "accounts/emails/activation_email.html",
            {
                "user": user,
                "activation_link": activation_link,
            },
        )
        text_content = render_to_string(
            "accounts/emails/activation_email.txt",
            {
                "user": user,
                "activation_link": activation_link,
            },
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        return f"Activation email sent successfully to {user.email}"

    except Account.DoesNotExist:
        return f"User with id {user_id} not found"
    except Exception as e:
        return f"Failed to send activation email: {str(e)}"

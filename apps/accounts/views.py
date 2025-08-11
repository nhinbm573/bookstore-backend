from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.settings.base import FRONTEND_DOMAIN
from .models import Account
from .serializers import SignupSerializer
from .tokens import account_activation_token
from .tasks import send_activation_email


class SignupView(generics.CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        activation_link = f"{FRONTEND_DOMAIN}/activate/{uid}/{token}"

        send_activation_email.delay(user.id, activation_link)

        response_data = {
            "message": "Registration successful. Please check your email to activate your account.",
            "status": 201,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class AccountActivateView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            if user.is_active:
                return Response(
                    {"message": "Account already activated.", "status": 200},
                    status=status.HTTP_200_OK,
                )

            user.is_active = True
            user.save()

            return Response(
                {
                    "message": "Account activated successfully! You can now log in.",
                    "status": 200,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "Activation link is invalid or has expired.",
                    "status": 400,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

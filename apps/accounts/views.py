from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from urllib.parse import urlparse

from config.settings.base import FRONTEND_DOMAIN
from .models import Account
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    GoogleSignInSerializer,
)
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


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            response_data = {
                "message": "Login successful.",
                "status": 200,
                "data": {
                    "access": str(access_token),
                    "account": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "phone": user.phone,
                        "birthday": user.birthday,
                    },
                },
            }

            response = Response(response_data, status=status.HTTP_200_OK)

            parsed_url = urlparse(FRONTEND_DOMAIN)
            cookie_domain = parsed_url.hostname if parsed_url.hostname else None

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                max_age=60 * 60 * 24 * 7,
                httponly=True,
                samesite="Lax",
                secure=not settings.DEBUG,
                domain=cookie_domain if not settings.DEBUG else None,
            )
            return response

        error_message = serializer.errors.get("message", ["Invalid credentials."])[0]
        captcha_error = serializer.errors.get("captcha", None)

        response_data = {
            "message": error_message,
            "status": 400,
        }

        if captcha_error or "captcha" in error_message.lower():
            response_data["captcha_required"] = True

        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"message": "No refresh token provided.", "status": 401},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = RefreshTokenSerializer(data={"refresh": refresh_token})

        if serializer.is_valid():
            access_token = serializer.validated_data["access"]
            refresh = serializer.validated_data["refresh"]

            try:
                user_id = refresh.payload.get("user_id")
                user = Account.objects.get(pk=user_id)

                response_data = {
                    "message": "Token refreshed successfully.",
                    "status": 200,
                    "data": {
                        "access": str(access_token),
                        "account": {
                            "id": user.id,
                            "email": user.email,
                            "full_name": user.full_name,
                            "phone": user.phone,
                            "birthday": user.birthday,
                        },
                    },
                }

                response = Response(response_data, status=status.HTTP_200_OK)

                parsed_url = urlparse(FRONTEND_DOMAIN)
                cookie_domain = parsed_url.hostname if parsed_url.hostname else None

                response.set_cookie(
                    key="refresh_token",
                    value=str(refresh),
                    max_age=60 * 60 * 24 * 7,
                    httponly=True,
                    samesite="Lax",
                    secure=not settings.DEBUG,
                    domain=cookie_domain if not settings.DEBUG else None,
                )

                return response

            except Account.DoesNotExist:
                return Response(
                    {"message": "User not found.", "status": 404},
                    status=status.HTTP_404_NOT_FOUND,
                )

        error_message = serializer.errors.get("message", ["Invalid token."])[0]
        return Response(
            {"message": error_message, "status": 401},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class GoogleSignInView(APIView):
    def post(self, request):
        serializer = GoogleSignInSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            response_data = {
                "message": "Google Sign-In successful.",
                "status": 200,
                "data": {
                    "access": str(access_token),
                    "account": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "phone": user.phone,
                        "birthday": user.birthday,
                        "is_google_user": user.is_google_user,
                    },
                },
            }

            response = Response(response_data, status=status.HTTP_200_OK)

            parsed_url = urlparse(FRONTEND_DOMAIN)
            cookie_domain = parsed_url.hostname if parsed_url.hostname else None

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                max_age=60 * 60 * 24 * 7,
                httponly=True,
                samesite="Lax",
                secure=not settings.DEBUG,
                domain=cookie_domain if not settings.DEBUG else None,
            )

            return response

        error_message = serializer.errors.get("message", ["Google Sign-In failed."])[0]
        return Response(
            {"message": error_message, "status": 400},
            status=status.HTTP_400_BAD_REQUEST,
        )

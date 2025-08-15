from django.urls import path
from .views import (
    SignupView,
    AccountActivateView,
    LoginView,
    LogoutView,
    RefreshTokenView,
    GoogleSignInView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path(
        "activate/<str:uidb64>/<str:token>/",
        AccountActivateView.as_view(),
        name="account-activate",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh-token"),
    path("google/", GoogleSignInView.as_view(), name="google-signin"),
    path(
        "retrieve-password/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "reset-password/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]

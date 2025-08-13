from django.urls import path
from .views import SignupView, AccountActivateView, LoginView, RefreshTokenView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path(
        "activate/<str:uidb64>/<str:token>/",
        AccountActivateView.as_view(),
        name="account-activate",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh-token"),
]

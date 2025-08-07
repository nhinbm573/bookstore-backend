from django.urls import path
from .views import SignupView, AccountActivateView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path(
        "activate/<str:uidb64>/<str:token>/",
        AccountActivateView.as_view(),
        name="account-activate",
    ),
]

from django.urls import path

from .views import (
    LoginAPIView,
    MeAPIView,
    RegisterAPIView,
    ResendVerificationAPIView,
    TokenRefreshAPIView,
    UserMeUpdateAPIView,
    VerifyEmailAPIView,
)


urlpatterns = [
    path("auth/register", RegisterAPIView.as_view(), name="auth-register"),
    path("auth/login", LoginAPIView.as_view(), name="auth-login"),
    path("auth/token/refresh", TokenRefreshAPIView.as_view(), name="token-refresh"),
    path("auth/me", MeAPIView.as_view(), name="auth-me"),
    path("auth/verify-email/", VerifyEmailAPIView.as_view(), name="verify-email"),
    path(
        "auth/resend-verification/",
        ResendVerificationAPIView.as_view(),
        name="resend-verification",
    ),
    path("users/me", UserMeUpdateAPIView.as_view(), name="users-me"),
]

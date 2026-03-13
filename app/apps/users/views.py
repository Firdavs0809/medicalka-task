import uuid
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import EmailVerificationToken, User
from .serializers import RegisterSerializer, UserMeUpdateSerializer, UserSerializer


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        token_obj = EmailVerificationToken.objects.get(user=user)
        verify_url = (
            f"{settings.APP_BASE_URL}/api/auth/verify-email/?token={token_obj.token}"
        )
        send_mail(
            subject="Verify your email",
            message=f"Verify your email by opening: {verify_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )


class LoginAPIView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class TokenRefreshAPIView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class MeAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserMeUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserMeUpdateSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class VerifyEmailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        raw_token = request.query_params.get("token")
        try:
            token_uuid = uuid.UUID(str(raw_token))
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token_obj = EmailVerificationToken.objects.select_related("user").get(
                token=token_uuid
            )
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {"detail": "Token not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if token_obj.is_expired:
            token_obj.delete()
            return Response(
                {"detail": "Token expired."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = token_obj.user
        user.is_verified = True
        user.save(update_fields=["is_verified", "updated_at"])
        token_obj.delete()

        return Response({"detail": "Email verified."}, status=status.HTTP_200_OK)


class ResendVerificationAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user: User = request.user
        if user.is_verified:
            return Response(
                {"detail": "User already verified."}, status=status.HTTP_400_BAD_REQUEST
            )

        new_expires = timezone.now() + timedelta(hours=24)
        token_obj, _ = EmailVerificationToken.objects.update_or_create(
            user=user,
            defaults={"token": uuid.uuid4(), "expires_at": new_expires},
        )
        verify_url = (
            f"{settings.APP_BASE_URL}/api/auth/verify-email/?token={token_obj.token}"
        )
        send_mail(
            subject="Verify your email",
            message=f"Verify your email by opening: {verify_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        return Response(
            {"detail": "Verification email sent."}, status=status.HTTP_200_OK
        )

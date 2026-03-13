import uuid
from datetime import timedelta
from typing import Optional

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from common.models import BaseModel
from common.validators import validate_full_name, validate_username


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: Optional[str] = None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: Optional[str] = None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        return self.create_user(email=email, password=password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=32, unique=True, validators=[validate_username]
    )
    full_name = models.CharField(max_length=100, validators=[validate_full_name])

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "full_name"]

    def __str__(self) -> str:
        return f"{self.email} ({self.username})"


def _default_expires_at():
    return timezone.now() + timedelta(hours=24)


class EmailVerificationToken(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="email_verification_token"
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expires_at = models.DateTimeField(default=_default_expires_at)

    def __str__(self) -> str:
        return f"EmailVerificationToken<{self.user.email}>"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

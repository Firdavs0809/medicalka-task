import re

from django.core.exceptions import ValidationError


USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")
FULL_NAME_RE = re.compile(r"^[A-Za-zА-Яа-яЁёІіЇїЄєҐґ\s\-]{2,100}$")


def validate_username(value: str) -> None:
    if not USERNAME_RE.fullmatch(value or ""):
        raise ValidationError(
            "Username must be 3–32 chars and contain only letters, digits, underscore."
        )


def validate_full_name(value: str) -> None:
    if not FULL_NAME_RE.fullmatch(value or ""):
        raise ValidationError(
            "Full name must be 2–100 chars and contain only letters, spaces, hyphens."
        )

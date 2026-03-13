from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsVerifiedUser(BasePermission):
    message = "Email is not verified."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        return bool(
            user and user.is_authenticated and getattr(user, "is_verified", False)
        )


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and obj.author == request.user
        )

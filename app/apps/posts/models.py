import uuid

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from common.models import BaseModel


class Post(BaseModel):
    author = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=255, validators=[MinLengthValidator(5)])
    content = models.TextField(validators=[MaxLengthValidator(10000)])

    def __str__(self) -> str:
        return f"{self.title} ({self.author.username})"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField(validators=[MaxLengthValidator(2000)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Comment<{self.author.username}> on {self.post_id}"


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="likes"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_user_post_like")
        ]

    def __str__(self) -> str:
        return f"Like<{self.user.username}>:{self.post_id}"

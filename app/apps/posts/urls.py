from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentDeleteAPIView, LikeAPIView, PostCommentsAPIView, PostViewSet


router = DefaultRouter()
router.register("posts", PostViewSet, basename="posts")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "posts/<uuid:post_id>/comments/", PostCommentsAPIView.as_view(), name="comments"
    ),
    path(
        "posts/<uuid:post_id>/comments/<uuid:comment_id>/",
        CommentDeleteAPIView.as_view(),
        name="comment-delete",
    ),
    path("posts/<uuid:post_id>/like/", LikeAPIView.as_view(), name="like"),
]

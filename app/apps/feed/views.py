from django.db.models import Prefetch
from rest_framework import permissions, serializers
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from apps.posts.models import Post
from apps.users.models import User


class FeedPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class FeedPostSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ("id", "title", "content", "created_at", "updated_at", "likes")

    def get_likes(self, obj) -> list:
        return list(obj.likes.values_list("user__username", flat=True))


class FeedUserSerializer(serializers.ModelSerializer):
    posts = FeedPostSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "posts")


class FeedAPIView(ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FeedUserSerializer
    pagination_class = FeedPagination

    def get_queryset(self):
        posts_qs = Post.objects.prefetch_related("likes").order_by("-created_at")
        return (
            User.objects.all()
            .prefetch_related(
                Prefetch("posts", queryset=posts_qs)
            )
            .order_by("-created_at")
        )

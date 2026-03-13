from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAuthorOrReadOnly, IsVerifiedUser

from .filters import PostFilter
from .models import Comment, Like, Post
from .serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostListSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = (
            Post.objects.select_related("author")
            .annotate(likes_count=Count("likes", distinct=True))
            .annotate(comments_count=Count("comments", distinct=True))
        )
        return PostFilter(self.request.query_params, queryset=qs).qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsVerifiedUser()]
        return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostCommentsAPIView(generics.ListCreateAPIView):
    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        return (
            Comment.objects.filter(post_id=post_id)
            .select_related("author")
            .order_by("created_at")
        )

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsVerifiedUser()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        serializer.save(post=post, author=self.request.user)


class CommentDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        if comment.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.author_id == request.user.id:
            return Response(
                {"detail": "You cannot like your own post."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Like.objects.filter(user=request.user, post=post).exists():
            return Response(
                {"detail": "Already liked."}, status=status.HTTP_400_BAD_REQUEST
            )
        Like.objects.create(user=request.user, post=post)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        if not deleted:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

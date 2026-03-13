import pytest
from rest_framework_simplejwt.tokens import AccessToken

from apps.posts.models import Post
from apps.users.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


def auth(api_client, user):
    token = AccessToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")


def test_unverified_user_cannot_create_post_403(api_client):
    user = UserFactory(is_verified=False)
    auth(api_client, user)
    resp = api_client.post(
        "/api/posts/",
        {"title": "Hello world", "content": "Content"},
        format="json",
    )
    assert resp.status_code == 403


def test_verified_user_can_create_post_201(api_client):
    user = UserFactory(is_verified=True)
    auth(api_client, user)
    resp = api_client.post(
        "/api/posts/",
        {"title": "Hello world", "content": "Content"},
        format="json",
    )
    assert resp.status_code == 201
    assert Post.objects.filter(author=user).count() == 1


def test_unverified_user_cannot_create_comment_403(api_client):
    author = UserFactory(is_verified=True)
    post = Post.objects.create(author=author, title="Hello world", content="x")

    user = UserFactory(is_verified=False)
    auth(api_client, user)
    resp = api_client.post(
        f"/api/posts/{post.id}/comments/",
        {"content": "Nice"},
        format="json",
    )
    assert resp.status_code == 403


def test_cannot_like_own_post_400(api_client):
    user = UserFactory(is_verified=False)
    post = Post.objects.create(author=user, title="Hello world", content="x")

    auth(api_client, user)
    resp = api_client.post(f"/api/posts/{post.id}/like/", format="json")
    assert resp.status_code == 400

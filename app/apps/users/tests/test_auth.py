import time

import pytest
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User


pytestmark = pytest.mark.django_db


def test_register_success(api_client):
    payload = {
        "email": "test@example.com",
        "username": "test_user",
        "full_name": "Test User",
        "password": "StrongPass123!",
    }
    resp = api_client.post("/api/auth/register", payload, format="json")
    assert resp.status_code == 201

    user = User.objects.get(email="test@example.com")
    assert user.is_verified is False


def test_register_duplicate_email_400(api_client):
    payload = {
        "email": "dup@example.com",
        "username": "dup_user1",
        "full_name": "Dup User",
        "password": "StrongPass123!",
    }
    resp1 = api_client.post("/api/auth/register", payload, format="json")
    assert resp1.status_code == 201

    payload2 = {
        "email": "dup@example.com",
        "username": "dup_user2",
        "full_name": "Dup User 2",
        "password": "StrongPass123!",
    }
    resp2 = api_client.post("/api/auth/register", payload2, format="json")
    assert resp2.status_code == 400


def test_register_duplicate_username_400(api_client):
    payload = {
        "email": "u1@example.com",
        "username": "same_username",
        "full_name": "User One",
        "password": "StrongPass123!",
    }
    resp1 = api_client.post("/api/auth/register", payload, format="json")
    assert resp1.status_code == 201

    payload2 = {
        "email": "u2@example.com",
        "username": "same_username",
        "full_name": "User Two",
        "password": "StrongPass123!",
    }
    resp2 = api_client.post("/api/auth/register", payload2, format="json")
    assert resp2.status_code == 400


def test_login_success_returns_access(api_client):
    api_client.post(
        "/api/auth/register",
        {
            "email": "login@example.com",
            "username": "login_user",
            "full_name": "Login User",
            "password": "StrongPass123!",
        },
        format="json",
    )

    resp = api_client.post(
        "/api/auth/login",
        {"email": "login@example.com", "password": "StrongPass123!"},
        format="json",
    )
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" in resp.data


def test_login_wrong_password_401(api_client):
    api_client.post(
        "/api/auth/register",
        {
            "email": "wrongpw@example.com",
            "username": "wrongpw_user",
            "full_name": "Wrong PW",
            "password": "StrongPass123!",
        },
        format="json",
    )

    resp = api_client.post(
        "/api/auth/login",
        {"email": "wrongpw@example.com", "password": "BadPass123!"},
        format="json",
    )
    assert resp.status_code == 401


def test_me_with_valid_token_200(api_client):
    api_client.post(
        "/api/auth/register",
        {
            "email": "me@example.com",
            "username": "me_user",
            "full_name": "Me User",
            "password": "StrongPass123!",
        },
        format="json",
    )
    login = api_client.post(
        "/api/auth/login",
        {"email": "me@example.com", "password": "StrongPass123!"},
        format="json",
    )
    token = login.data["access"]

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = api_client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.data["email"] == "me@example.com"


def test_me_no_token_401(api_client):
    resp = api_client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_invalid_token_401(api_client):
    api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.here")
    resp = api_client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_expired_token_401(api_client):
    api_client.post(
        "/api/auth/register",
        {
            "email": "exp@example.com",
            "username": "exp_user",
            "full_name": "Exp User",
            "password": "StrongPass123!",
        },
        format="json",
    )
    user = User.objects.get(email="exp@example.com")

    token = AccessToken.for_user(user)
    token["exp"] = int(time.time()) - 1

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")
    resp = api_client.get("/api/auth/me")
    assert resp.status_code == 401

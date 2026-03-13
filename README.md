## Quick start

1. Copy env file:

```bash
cp .env.example .env
```

2. Run:

```bash
docker compose up --build
```

API will be available at `http://localhost:8000/`.

## Run tests

```bash
docker compose exec app pytest
```

## Swagger / API docs

This project does not include Swagger by default. If you want it, add `drf-spectacular` and wire `/api/schema/` + `/api/docs/`.

## Project structure

The Django project lives in `app/` with split settings under `app/config/settings/` and feature apps under `app/apps/` (`users`, `posts`, `feed`). Shared reusable pieces (like `BaseModel` and validators) live in `app/common/`.

## Curl examples

### Register

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"u1@example.com","username":"u1_user","full_name":"User One","password":"StrongPass123!"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"u1@example.com","password":"StrongPass123!"}'
```

### Create post (verified users only)

```bash
ACCESS="paste_access_token_here"
curl -X POST http://localhost:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS" \
  -d '{"title":"My first post","content":"Hello!"}'
```

### Like post

```bash
POST_ID="paste_post_uuid_here"
curl -X POST "http://localhost:8000/api/posts/$POST_ID/like/" \
  -H "Authorization: Bearer $ACCESS"
```

### Feed

```bash
curl http://localhost:8000/api/feed/
```

## Background jobs (Celery)

This project runs:
- `celery_worker` for async tasks
- `celery_beat` for scheduled tasks
- `redis` as the broker

Unverified user cleanup runs automatically every hour via Celery beat (no admin-token API endpoint).


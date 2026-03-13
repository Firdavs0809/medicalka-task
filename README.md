## Setup

cp .env.example .env
docker compose up --build

API runs at http://localhost:8000/

## Tests

docker compose exec app pytest

## Structure

Django project in app/ with split settings (config/settings/), apps under apps/ (users, posts, feed), shared code in common/.

## Endpoints

### Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"u1@example.com","username":"u1","full_name":"User One","password":"StrongPass123!"}'

### Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"u1@example.com","password":"StrongPass123!"}'

### Create post
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"My first post","content":"Hello!"}'

### Like a post
curl -X POST http://localhost:8000/api/posts/<post_id>/like/ \
  -H "Authorization: Bearer <token>"

### Feed
curl http://localhost:8000/api/feed/

## Background jobs

Celery worker + beat + Redis handle async tasks. Unverified user cleanup runs on a schedule via Celery beat.


## API Docs

http://localhost:8000/api/docs/
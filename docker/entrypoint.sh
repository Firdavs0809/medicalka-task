#!/usr/bin/env sh
set -e

echo "Waiting for postgres..."
until pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" > /dev/null 2>&1; do
  sleep 1
done
echo "Postgres is ready"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"

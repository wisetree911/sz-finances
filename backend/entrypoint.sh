#!/bin/sh
set -e

echo "waiting for Postgres at ${POSTGRES_HOST}:${POSTGRES_PORT}"
until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"; do
  sleep 1
done

alembic upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
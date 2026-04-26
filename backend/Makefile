include ../.env.test

TEST_COMPOSE = docker compose --env-file ../.env.test -p szfin-test
TEST_API_ENV = DATABASE_URL=$(DATABASE_URL) SECRET_KEY=$(SECRET_KEY) ALGORITHM=$(ALGORITHM) ACCESS_TOKEN_EXPIRE_MINUTES=$(ACCESS_TOKEN_EXPIRE_MINUTES) REFRESH_TOKEN_EXPIRE_DAYS=$(REFRESH_TOKEN_EXPIRE_DAYS) REDIS_URL=$(REDIS_URL) REDIS_PRICES_CHANNEL=$(REDIS_PRICES_CHANNEL)

.PHONY: ruff test-unit test-api test-api-up test-api-down test-api-migrate typecheck check

check: ruff typecheck test-unit

test-api-up:
	@$(TEST_COMPOSE) up -d --wait db redis

test-api-migrate:
	@$(TEST_API_ENV) uv run alembic upgrade head

test-api: test-api-migrate
	@$(TEST_API_ENV) uv run pytest tests/api -q

test-api-down:
	@$(TEST_COMPOSE) down -v

test-unit:
	@uv run pytest tests/unit -q

typecheck:
	@uv run mypy

ruff:
	@uv run ruff check .
	@uv run ruff format --check
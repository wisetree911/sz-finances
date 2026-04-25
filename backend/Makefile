.PHONY: test test-unit test-analytics typecheck

test:
	uv run pytest tests/unit -q

test-unit:
	uv run pytest tests/unit -q

test-analytics:
	uv run pytest tests/unit/test_analytics_service.py -q

typecheck:
	uv run mypy

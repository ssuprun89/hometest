.PHONY: run install lint format typecheck test test-unit test-integration coverage check

run:
	uv run uvicorn app.main:app --reload

install:
	uv sync --all-groups

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy app

test:
	uv run pytest tests/ -v

test-unit:
	uv run pytest tests/unit -v

test-integration:
	uv run pytest tests/integration -v

coverage:
	uv run pytest tests/ --cov=app --cov-report=term-missing

check: lint typecheck test

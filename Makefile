.PHONY: install lint format typecheck test check

install:  ## Install dependencies and git hooks
	uv sync
	uv run pre-commit install

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy

test:
	uv run pytest

check: lint typecheck test  ## Everything CI runs
	uv run ruff format --check .

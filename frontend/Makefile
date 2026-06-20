.PHONY: format lint test run

format:
	uv format

lint:
	uv run ruff check .

test:
	uv run pytest

run:
	uv run flask --app main run --debug --port 8000

.PHONY: format lint test run db-migrate db-upgrade

format:
	uv format

lint:
	uv run ruff check .

test:
	uv run pytest

run:
	uv run flask --app main run --debug

db-migrate:
	uv run flask --app main db migrate -m "$(m)"

db-upgrade:
	uv run flask --app main db upgrade

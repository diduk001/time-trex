FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY . .

ENV APP_CONFIG=production

CMD ["uv", "run", "flask", "--app", "main:app", "run", "--host", "0.0.0.0", "--port", "5000"]

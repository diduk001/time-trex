FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY . .

ENV APP_CONFIG=production

EXPOSE 8000

CMD ["uv", "run", "flask", "--app", "main:app", "run", "--host", "0.0.0.0", "--port", "8000"]

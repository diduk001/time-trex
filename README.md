# 🦖 Time T-Rex - кроссплатформенный сервис для учета времени

Веб-приложение для отслеживания времени, потраченного на различные активности. Состоит из двух независимых сервисов:

- **backend** — Flask REST API с JWT-аутентификацией и SQLite базой данных
- **frontend** — серверный веб-интерфейс на Flask с шаблонами Jinja2

## Архитектура

```
браузер → frontend (8000) → backend API (5000) → SQLite
```

Frontend не хранит данные — он только рендерит страницы и проксирует запросы к backend.

## Быстрый старт (Docker Compose)

```bash
cp .env.example .env   # задать секреты (если нет — будут дефолты)
docker compose up -d
```

Приложение будет доступно на `http://localhost:8000`.

### Переменные окружения

| Переменная                   | Описание                              | По умолчанию    |
|------------------------------|---------------------------------------|-----------------|
| `BACKEND_SECRET_KEY`         | Секрет Flask (backend)                | `change-me`     |
| `JWT_SECRET_KEY`             | Секрет для JWT-токенов                | `change-me-too` |
| `FRONTEND_SECRET_KEY`        | Секрет Flask (frontend)               | `change-me`     |
| `JWT_ACCESS_TOKEN_EXPIRES`   | Время жизни токена в секундах         | `86400` (1 д.)  |
| `REQUEST_TIMEOUT`            | Таймаут запросов frontend → backend   | `10`            |

## Локальная разработка

### Backend

```bash
cd backend
uv sync
cp .env.example .env      # отредактировать секреты
make db-upgrade           # применить миграции
make run                  # http://127.0.0.1:5000
```

### Frontend

```bash
cd frontend
uv sync
cp .env.example .env      # указать SECRET_KEY и BACKEND_URL
make run                  # http://127.0.0.1:8000
```

Backend должен быть запущен до старта frontend.

## Тестирование и линтинг

В каждом сервисе:

```bash
make test     # pytest с покрытием (минимум 70%)
make lint     # ruff
make format   # ruff format
```

## API

Все маршруты начинаются с `/api`. Для всех, кроме `auth/register` и `auth/login`, требуется заголовок `Authorization: Bearer <jwt>`.

| Область        | Эндпоинты                                                                                                                    |
|----------------|------------------------------------------------------------------------------------------------------------------------------|
| Аутентификация | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`                                                       |
| Активности     | `GET/POST /api/activities`, `GET/PATCH/DELETE /api/activities/{id}`                                                          |
| Записи         | `POST /api/entries/start`, `POST /api/entries/{id}/stop`, `POST /api/entries`, `GET /api/entries`, `GET/PATCH/DELETE /api/entries/{id}` |
| Статистика     | `GET /api/stats/summary`, `GET /api/stats/timeline`                                                                          |

Подробнее — в [backend/README.md](backend/README.md) и [frontend/README.md](frontend/README.md).

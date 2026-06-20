# 🦖 Time T-Rex backend - бэкенд сервиса учета времени

Flask REST API для сервиса учёта времени Time T-Rex.

## Установка

    uv sync
    cp .env.example .env   # нужно отредактировать секреты

## База данных

    make db-upgrade        # применить миграции
    make db-migrate m="сообщение"   # создать новую миграцию после изменения моделей

## Запуск

    make run               # http://127.0.0.1:5000

## Тестирование и линтинг

    make test              # pytest с покрытием (ошибка, если покрытие ниже 70%)
    make lint              # ruff
    make format            # uv format

## API

Все маршруты начинаются с `/api`. Для любого маршрута, кроме `auth/register` и
`auth/login`, требуется заголовок `Authorization: Bearer <jwt>`.

| Область     | Эндпоинты                                                                                                          |
|-------------|--------------------------------------------------------------------------------------------------------------------|
| Аутентификация | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`                                            |
| Активности  | `GET/POST /api/activities`, `GET/PATCH/DELETE /api/activities/{id}`                                                |
| Записи      | `POST /api/entries/start`, `POST /api/entries/{id}/stop`, `POST /api/entries`, `GET /api/entries`, `GET/PATCH/DELETE /api/entries/{id}` |
| Статистика  | `GET /api/stats/summary`, `GET /api/stats/timeline`                                                                |
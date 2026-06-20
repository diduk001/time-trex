# 🦖 Time T-Rex frontend - фронтенд сервиса учета времени

Серверный веб-интерфейс на Flask для сервиса учёта времени Time T-Rex. Рендерит
шаблоны Jinja2 и общается с backend REST API по HTTP.

## Установка

    uv sync
    cp .env.example .env   # укажите SECRET_KEY и BACKEND_URL

Backend должен быть запущен (по умолчанию `http://127.0.0.1:5000`).

## Запуск

    make run               # http://127.0.0.1:8000

## Тестирование и линтинг

    make test              # pytest с покрытием (ошибка, если покрытие ниже 70%)
    make lint              # ruff
    make format            # uv format

## Примечания

- JWT backend’а хранится в подписанной сессионной куке Flask.
- Всё отображаемое и вводимое время — UTC.
- Графики используют Chart.js (единственный JavaScript в приложении).
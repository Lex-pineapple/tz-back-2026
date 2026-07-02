# Test FastAPI app

Стек: FastAPI + SQLite

Для старта приложения необходимо:

1. Перейти в корневую папку:

```
cd tz-back-2026
```

2. Запустить контейнер:

```
docker-compose up --build
```

Запуск без контейнера:

1. Установить зависимости:

```bash
pip install -r recs.txt
```

2. Запустить приложение:

```bash
uvicorn app.main:app --reload
```

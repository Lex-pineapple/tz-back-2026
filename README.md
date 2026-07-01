# Test FAstAPI app

Стек: FastAPI + SQLite

Для старта приложения необходимо:

Перейти в корневую папку:

```
cd tz-back-2026
```

Запустить контейнер:

```
docker-compose up --build
```

Также можно запустить без контейнера:

```
uvicorn app.main:app --reload
```

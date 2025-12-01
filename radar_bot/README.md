# Radar Bot

Telegram-бот для трейдинга, работающий в связке с Radar Backend.

## Переменные окружения

- `BOT_TOKEN` — токен Telegram-бота от @BotFather
- `BACKEND_URL` — URL backend-сервиса Radar, например:
  `https://radar-backend.onrender.com`

## Запуск локально

```bash
pip install -r requirements.txt
export BOT_TOKEN=xxxx
export BACKEND_URL=http://localhost:8000
python -m app.main
```

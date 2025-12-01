import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")
BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment variables")

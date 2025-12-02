import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from .ai_menu import router as ai_menu_router


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(ai_menu_router)

    print("🚀 Radar backend started")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

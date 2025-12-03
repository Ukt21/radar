import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from radar_bot.app.handlers.ai_menu import ai_menu_router

def setup_routers(dp):
    dp.include_router(ai_menu_router)


def setup_routers(dp: Dispatcher) -> None:
    dp.include_router(main_menu_router)
    dp.include_router(settings_router)

def setup_routers(dp: Dispatcher) -> None:
    dp.include_router(main_menu_router)
    dp.include_router(settings_router)
    # dp.include_router(ai_menu_router)  # временно отключено


async def main():
    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    dp.include_router(ai_menu_router)

    print("🚀 Radar backend started")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

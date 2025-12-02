import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from app.config import BOT_TOKEN
from app.handlers.start import router as start_router
from app.handlers.analyze import router as analyze_router
from app.handlers.liquidity import router as liquidity_router
from app.handlers.btc import router as btc_router

async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # REGISTER ROUTERS
    dp.include_router(start_router)
    dp.include_router(analyze_router)
    dp.include_router(liquidity_router)
    dp.include_router(btc_router)

    print("🚀 Radar Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")

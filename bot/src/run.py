from aiogram import Bot, Dispatcher
from handlers import router as main_router
from config import settings
import asyncio
import logging
from http_client import api_client

bot = Bot(token=settings.bot.token)
dp = Dispatcher()

async def on_startup(dispatcher: Dispatcher):
    print("Бот запускается...")
    await api_client.create_session()

async def on_shutdown(dispatcher: Dispatcher):
    print("Бот останавливается...")
    await api_client.close_session()

async def main():
    logging.basicConfig(level=logging.INFO)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.include_router(main_router)

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("Bot stopped")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
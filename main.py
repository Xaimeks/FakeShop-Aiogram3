import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from os import getenv

from app.handlers import router

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

async def main():

    dp = Dispatcher()
    bot = Bot(token=TOKEN)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
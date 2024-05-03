import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import router
from dotenv import load_dotenv, dotenv_values
import os

async def main():
    load_dotenv()
    c = dotenv_values(".env")
    print('env: ', c)
    print(os.listdir(os.curdir))
    print(os.getcwd())
    bot = Bot(token=c.get('BOT_TOKEN'), parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

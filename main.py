import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv, dotenv_values
from peewee import *

from handlers import router
from models.word import Word


async def main():
    db = SqliteDatabase('word.db')
    db.connect()
    db.create_tables([Word])
    load_dotenv()
    c = dotenv_values(".env")
    bot = Bot(token=c.get('BOT_TOKEN'), parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

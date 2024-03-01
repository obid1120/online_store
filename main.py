import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers.command_handlers import cmd_router
from handlers.category_handlers import category_router
from handlers.product_handler import product_router


async def main():
    bot = Bot(token=BOT_TOKEN)
    db = Dispatcher()
    db.include_routers(cmd_router, category_router, product_router)
    await db.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")

import asyncio

from aiogram import Bot, Dispatcher

from bot.settings import (
    BOT_TOKEN,
    USE_WEBHOOK,
    WEBHOOK_PATH,
    WEBHOOK_SECRET,
    BASE_WEBHOOK_URL
)

from bot.database import db, User, Group
from bot.nsfw_worker import nsfw_worker
from bot.utils import get_time

from bot.handlers import commands, messages, callback_queries, chat_members


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(commands.router)
dp.include_router(messages.router)
dp.include_router(callback_queries.router)
dp.include_router(chat_members.router)



# --- SETUP ---
@dp.startup()
async def startup():
    print(f"{get_time()} - Online")
    with db.allow_sync():
        db.create_tables([User, Group])

    await db.aio_connect()

    for _ in range(4):
        asyncio.create_task(nsfw_worker(bot))

    if USE_WEBHOOK:
        await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


@dp.shutdown()
async def shutdown():
    try:
        await bot.delete_webhook()
    except Exception:
        pass
    
    try:
        await db.aio_close()
        db.close()
    except Exception:
        pass
    
    try:
        await bot.session.close()
    except Exception:
        pass

    print(f"{get_time()} - Offline")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, handle_signals=True)
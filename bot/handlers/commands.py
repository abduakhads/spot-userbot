from aiogram import Bot, Router, F, types
from aiogram.enums import ChatType
from aiogram.filters import Command

from bot.utils import get_time
from bot.database import User
from bot.settings import DEVELOPER_ID


router = Router()



# --- START CMD ---
@router.message(Command('start'), F.chat.type == ChatType.PRIVATE)
async def start_cmd(message: types.Message):
    await message.reply("👋 Welcome!\nTo start monitoring just add me to your super group. (no need to add as admin)\n\nP.s. Currently we only support supergroups.")
    await User.aio_get_or_create(id=message.from_user.id)



# --- ANNOUNCE CMD ---
@router.message(Command('say'), F.from_user.id == int(DEVELOPER_ID), F.chat.type == ChatType.PRIVATE)
async def announce_cmd(message: types.Message, bot: Bot):
    text_parts = message.text.split(maxsplit=1)
    if len(text_parts) < 2:
        await message.reply("Please provide announcement text after the command.")
        return
    
    announcement_text = text_parts[1]
    users = await User.select().aio_execute()

    for user in users:
        try:
            await bot.send_message(user.id, f"📢 Announcement: \n\n{announcement_text}")
        except Exception as e:
            print(f"{get_time()} - Failed to send message to {user.id}: {e}")
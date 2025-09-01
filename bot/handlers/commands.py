from aiogram import Bot, Router, F, types
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject

from bot import keyboards as kb
from bot.utils import get_time
from bot.database import User
from bot.settings import DEVELOPER_ID


router = Router()



# --- START CMD ---
@router.message(Command('start'), F.chat.type == ChatType.PRIVATE)
async def start_cmd(message: types.Message, command: CommandObject, bot: Bot):
    # print(await bot.get_my_default_administrator_rights())
    try:
        if not command.args:
            await message.reply(
                text="👋 Welcome!\nTo start monitoring just add me to your super group.\n\nP.s. Currently we only support supergroups.",
                reply_markup=await kb.get_main_kb()
            )
        else:
            await message.reply(
                text=f"👋 Welcome!\n\nNow You can add me to super group again.\n\nP.s. Currently we only support supergroups.",
                reply_markup=await kb.get_main_kb()
            )
        await User.aio_get_or_create(id=message.from_user.id)
    except Exception as e:
        print(f"{get_time()} - [Error (start_cmd)] {e}")


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
from aiogram import types

from bot.utils import FalseAlertCallback

async def get_false_inkb(message_id: str) -> types.InlineKeyboardMarkup:
    confrmkb = types.InlineKeyboardMarkup(
        inline_keyboard=[[
            types.InlineKeyboardButton(
                text="Report False Alert 📤", 
                callback_data=FalseAlertCallback(message_id=message_id).pack()
            )
        ]]
    )
    return confrmkb
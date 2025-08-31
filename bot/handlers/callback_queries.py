from aiogram import Bot, Router, F, types

from bot.settings import DEVELOPER_ID
from bot.utils import FalseAlertCallback


router = Router()



# --- CALLBACK QUERY HANDLER ---
@router.callback_query(FalseAlertCallback.filter())
async def false_alert_handler(callback: types.CallbackQuery, callback_data: FalseAlertCallback, bot: Bot):
    await bot.send_message(
        DEVELOPER_ID,
        f"📩 False Alert Reported!\n\n",
        reply_to_message_id=callback_data.message_id
    )
    
    await callback.answer("False alert reported!")
    await callback.message.edit_text("Thank you for your feedback and sorry for the inconvenience!")
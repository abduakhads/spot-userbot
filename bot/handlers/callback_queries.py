from aiogram import Bot, Router, F, types

from bot import utils
from bot import keyboards as kb
from bot.settings import DEVELOPER_ID
from bot.database import Group
from bot.handlers import common

router = Router()



# --- FALSE ALERT ---
@router.callback_query(utils.FalseAlertCallback.filter())
async def false_alert_handler(callback: types.CallbackQuery, callback_data: utils.FalseAlertCallback, bot: Bot):
    await bot.send_message(
        DEVELOPER_ID,
        f"📩 False Alert Reported!\n\n",
        reply_to_message_id=callback_data.message_id
    )
    
    await callback.answer("False alert reported!")
    await callback.message.edit_text("Thank you for your feedback and sorry for the inconvenience!")



# --- GROUP SETTINGS ---
@router.callback_query(utils.GroupSettingsCallback.filter())
async def group_settings_handler(callback: types.CallbackQuery, callback_data: utils.GroupSettingsCallback, bot: Bot):
    await common.group_settings(callback, bot, callback_data)

    await callback.answer()



# --- TOGGLE KICK BOT ---
@router.callback_query(utils.ToggleKickBotCallback.filter())
async def toggle_kick_bot_handler(callback: types.CallbackQuery, callback_data: utils.ToggleKickBotCallback, bot: Bot):
    member = await bot.get_chat_member(callback_data.group_id, bot.id)
    answer = ""
    
    if not member.status in ["administrator"]:
        answer = "Please make me an admin in the group first."
    elif not member.can_restrict_members:
        answer = "Give me permission to restrict members."
    else:
        group = await Group.aio_get_or_none(Group.id == callback_data.group_id)

        if not group:
            await callback.answer("Group not found.")
            return

        group.kick_bot = not group.kick_bot
        await group.aio_save()
    
    await common.group_settings(callback, bot, callback_data)
    await callback.answer(answer)



# --- TOGGLE DELETE MESSAGE ---
@router.callback_query(utils.ToggleDeleteMessageCallback.filter())
async def toggle_delete_message_handler(callback: types.CallbackQuery, callback_data: utils.ToggleDeleteMessageCallback, bot: Bot):
    member = await bot.get_chat_member(callback_data.group_id, bot.id)
    answer = ""

    if not member.status in ["administrator"]:
        answer = "Please make me an admin in the group first."
    elif not member.can_delete_messages:
        answer = "Give me permission to delete messages."
    else:

        group = await Group.aio_get_or_none(Group.id == callback_data.group_id)

        if not group:
            await callback.answer("Group not found.")
            return

        group.delete_message = not group.delete_message
        await group.aio_save()
    
    await common.group_settings(callback, bot, callback_data)
    await callback.answer(answer)



# --- DELETE GROUP ---
@router.callback_query(utils.DeleteGroupCallback.filter())
async def delete_group_handler(callback: types.CallbackQuery, callback_data: utils.DeleteGroupCallback, bot: Bot):
    await callback.message.edit_text(
        text="Are you sure you want to delete this group?",
        reply_markup=await kb.get_confirm_inkb(callback_data.group_id, ["list_my_groups", "delete_group"])
    )
    await callback.answer()



# --- CONFIRM ---
@router.callback_query(utils.ConfirmCallback.filter())
async def confirm_delete_group_handler(callback: types.CallbackQuery, callback_data: utils.ConfirmCallback, bot: Bot):
    msg = await getattr(common, callback_data.function)(callback.message, bot, callback.from_user.id, callback_data)
    await callback.answer(msg)



# --- BACK BTN ---
@router.callback_query(utils.BackCallback.filter())
async def back_button_handler(callback: types.CallbackQuery, callback_data: utils.BackCallback, bot: Bot):
    await getattr(common, callback_data.function)(callback.message, bot, callback.from_user.id)

    # if callback_data.function == "list_my_groups":
    #     await common.list_my_groups(callback.message, bot, callback.from_user.id)



# --- CLOSE BTN ---
@router.callback_query(F.data == "close")
async def close_group_settings_handler(callback: types.CallbackQuery, bot: Bot):
    await callback.message.delete()
    await callback.answer()
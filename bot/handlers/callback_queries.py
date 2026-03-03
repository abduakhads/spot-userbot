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
    try:
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    except:
        id = (await callback.message.edit_text("closed")).message_id
        try:
            await bot.delete_message(callback.message.chat.id, id)
        except:
            print("error: line 126 callback_queries.py")
    await callback.answer()


# --- DONATE AMOUNT ---
@router.callback_query(utils.DonateAmountCallback.filter())
async def donate_amount_handler(callback: types.CallbackQuery, callback_data: utils.DonateAmountCallback, bot: Bot):
    await callback.answer()
    await callback.message.delete()
    amount = int(callback_data.amount)

    if amount <= 0:
        await callback.message.answer(
            "For custom donation amounts, please use the /donate command followed by the amount you wish to donate. For example: \n\n`/donate 10` \n\nto donate 10 ⭐.",
            parse_mode="Markdown"
        )
        return

    await common.donate_amount_cmd(callback.message, bot, amount)


# --- PRE CHECKOUT QUERY ---
@router.pre_checkout_query()
async def pre_checkout_query(query: types.PreCheckoutQuery):
    await query.answer(
        ok=True,
    )


# --- SUCCESSFUL PAYMENT ---
@router.message(F.successful_payment)
async def on_successfull_payment(message: types.Message, bot: Bot):
    tid = message.successful_payment.telegram_payment_charge_id
    # msgid = message.successful_payment.invoice_payload.split("_")[-1]
    # await message.delete()
    await bot.send_message(
        DEVELOPER_ID,
        f"💰 New Donation Received!\n\n"\
        f"Amount: {message.successful_payment.total_amount} {message.successful_payment.currency}\nTelegram Charge ID: `{tid}`\n\n"\
        f"from user: \n{message.from_user.full_name}\n"\
        f"{'@'+message.from_user.username if message.from_user.username else 'No username'}\n"\
        f"ID: `{message.from_user.id}`",
        parse_mode="Markdown",
        )
        

    await message.answer(
        text="🫶 Thank you for your donation! Your support helps keep the bot running and improving. ",
        message_effect_id="5159385139981059251",

        # 🔥 - 5104841245755180586🌟
        # 👍 - 5107584321108051014
        # 👎 - 5104858069142078462
        # ❤️ - 5159385139981059251
        # 🎉 - 5046509860389126442
        # 💩 - 5046589136895476101
    )
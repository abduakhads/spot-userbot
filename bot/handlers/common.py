from aiogram import Bot, types

from bot import keyboards as kb
from bot.database import Group
from bot.settings import HELP_TEXT, DEMO_VIDEO



async def list_my_groups(message: types.Message, bot: Bot, user_id: int, callback_data = None):
    groups = await Group.select().where(Group.user_id == user_id).aio_execute()
    
    group_list = [(await bot.get_chat(group.id)) for group in groups]
    if message.from_user.id == bot.id:
        if not groups:
            await message.edit_text("You are not monitoring any groups.", reply_markup=await kb.get_add_group_inkb())
            return
        await message.edit_text(
            text="You are monitoring the following groups:",
            reply_markup=await kb.get_groups_list_inkb(group_list)
        )
        return
    
    if not groups:
        await message.reply("You are not monitoring any groups.", reply_markup=await kb.get_add_group_inkb())
        return

    await message.delete()
    await message.answer(
        text=f"You are monitoring the following groups:", 
        reply_markup=await kb.get_groups_list_inkb(group_list)
    )



async def delete_group(message: types.Message, bot: Bot, user_id: int, callback_data = None):
    group = await Group.aio_get_or_none(Group.id == callback_data.group_id)

    if not group:
        await message.edit_text("Group not found.")
        return

    await bot.leave_chat(group.id)
    await group.aio_delete_instance()
    await list_my_groups(message, bot, user_id)

    return "Group deleted."



async def group_settings(callback: types.CallbackQuery, bot: Bot, callback_data = None):
    group = await Group.aio_get_or_none(Group.id == callback_data.group_id)

    if not group:
        await callback.answer("Group not found.")
        return

    group_info = await bot.get_chat(callback_data.group_id)
    text = f"Settings for super group: {group_info.title}\n"
    text += f"\nKick User Bot: {'🟢 on' if group.kick_bot else '🔴 off'}"
    text += f"\nDelete Messages: {'🟢 on' if group.delete_message else '🔴 off'}"
    
    if callback.message.text != text:
        await callback.message.edit_text(
            text=text,
            reply_markup=await kb.get_group_settings_inkb(group)
        )



async def help_cmd(message: types.Message, bot: Bot):
    await message.reply_video(
        video=DEMO_VIDEO,
        caption=HELP_TEXT,
        parse_mode="MarkdownV2",
        show_caption_above_media=True,
    )



async def donate_amount_cmd(message: types.Message, bot: Bot, amount: int):
    prices = [types.LabeledPrice(label="XTR", amount=amount)]
    await message.answer_invoice(
        title="Donation",
        description=f"🌱 Support the project with {amount} ⭐️",
        prices=prices,

        provider_token="",

        payload=f"donation_{amount}_stars",

        currency="XTR",
        reply_markup=await kb.get_donate_inkb(amount)
    )
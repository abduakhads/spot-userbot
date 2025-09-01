from aiogram import Bot, types

from bot import keyboards as kb
from bot.database import Group



async def list_my_groups(message: types.Message, bot: Bot, user_id: int, callback_data = None):
    groups = await Group.select().where(Group.user_id == user_id).aio_execute()
    
    group_list = [(await bot.get_chat(group.id)) for group in groups]
    if message.from_user.id == bot.id:
        if not groups:
            await message.edit_text("You are not monitoring any groups.")
            return
        await message.edit_text(
            text="You are monitoring the following groups:",
            reply_markup=await kb.get_groups_list_inkb(group_list)
        )
        return
    
    if not groups:
        await message.reply("You are not monitoring any groups.")
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
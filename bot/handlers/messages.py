from aiogram import Bot, Router, F, types
from aiogram.enums import ChatType

from bot import keyboards as kb
from bot.handlers import common
from bot.nsfw_worker import nsfw_queue
from bot.database import Group
from bot.settings import DEVELOPER_ID

router = Router()


# --- MY GROUP BTN HANDLER ---
@router.message(F.text == "My Groups 👥", F.chat.type == ChatType.PRIVATE)
async def my_groups_btn_handler(message: types.Message, bot: Bot):
    await common.list_my_groups(message, bot, message.from_user.id)


# --- HELP BTN HANDLER ---
@router.message(F.text == "💬 Help", F.chat.type == ChatType.PRIVATE)
async def help_btn_handler(message: types.Message, bot: Bot):
    await common.help_cmd(message, bot)


# --- DONATE BTN HANDLER ---
@router.message(F.text == "Donate 🕊️", F.chat.type == ChatType.PRIVATE)
async def donate_btn_handler(message: types.Message, bot: Bot):
    await message.delete()
    await message.answer(
        text="🙏 Big thanks for considering a donation! \nYour support helps keep the bot running." \
        "\n\nPlease choose the amount to donate:",
        reply_markup=await kb.get_donations_inkb()
    )


# --- SUPER GROUP MESSAGE HANDLER ---
@router.message(
        F.chat.type.in_([ChatType.SUPERGROUP]),
        ~F.new_chat_members, ~F.left_chat_member)
async def group_message_handler(message: types.Message, bot: Bot):
    user = await bot.get_chat(message.from_user.id)
    user_photo = user.photo
    if not user_photo:
        # print("No profile photo found.") #TODO: Log this event

        stripped_chat_id = str(message.chat.id).removeprefix("-100")
        chat_link = f"https://t.me/{message.chat.username if message.chat.username else 'c/' + stripped_chat_id}"
        message_link = chat_link + f"/{message.message_id}"

        await bot.send_message(
            chat_id=DEVELOPER_ID,
            text=f"{message_link}\n\nNo profile photo found for user {user.full_name} in {message.chat.full_name} (id: {user.id}). Skipping NSFW check."
        )

        return

    if not (user.personal_chat or user.bio):
        # print("No personal chat found.") #TODO: Log this event

        stripped_chat_id = str(message.chat.id).removeprefix("-100")
        chat_link = f"https://t.me/{message.chat.username if message.chat.username else 'c/' + stripped_chat_id}"
        message_link = chat_link + f"/{message.message_id}"

        await bot.send_message(
            chat_id=DEVELOPER_ID,
            text=f"{message_link}\n\No personal chat found {user.full_name} in {message.chat.full_name} (id: {user.id}). Skipping NSFW check."
        )

        return

    channel = await bot.get_chat(user.personal_chat.id)
    channel_photo = channel.photo

    # if not channel_photo:
    #     print("No channel photo found.") #TODO: Log this event
    #     return

    
    file_info = await bot.get_file(user_photo.big_file_id)
    file_path = file_info.file_path

    downloaded_file = await bot.download_file(file_path)
    image_bytes = downloaded_file.getvalue()
    # print("Putting task in queue...")
    await nsfw_queue.put((message, image_bytes))



# @router.message(lambda message: message.left_chat_member)
# async def delete_left_chat_member_service_message(message: types.Message, bot: Bot):
#     try:
#         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#     except Exception as e:
#         print(f"Failed to delete leave/kick message: {e}")
from aiogram import Bot, Router, F, types
from aiogram.enums import ChatType

from bot.nsfw_worker import nsfw_queue


router = Router()



# --- SUPER GROUP MESSAGE HANDLER ---
@router.message(
        F.chat.type.in_([ChatType.SUPERGROUP]),
        ~F.new_chat_members, ~F.left_chat_member)
async def group_message_handler(message: types.Message, bot: Bot):
    user = await bot.get_chat(message.from_user.id)
    user_photo = user.photo
    if not user_photo:
        print("No profile photo found.") #TODO: Log this event
        return

    if not user.personal_chat:
        print("No personal chat found.") #TODO: Log this event
        return

    channel = await bot.get_chat(user.personal_chat.id)
    channel_photo = channel.photo

    if not channel_photo:
        print("No channel photo found.") #TODO: Log this event
        return

    
    file_info = await bot.get_file(user_photo.big_file_id)
    file_path = file_info.file_path

    downloaded_file = await bot.download_file(file_path)
    image_bytes = downloaded_file.getvalue()
    # print("Putting task in queue...")
    await nsfw_queue.put((message, image_bytes))
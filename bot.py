import os
import asyncio

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.filters.callback_data import CallbackData

from aiogram.enums import ChatType

from database import db, User, Group
from detect import is_nsfw

load_dotenv()

nsfw_queue = asyncio.Queue()

BOT_TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class FalseAlertCallback(CallbackData, prefix="false_alert"):
    message_id: int | str 


# --- NSFW WORKER ---
async def nsfw_worker(bot: Bot):
    """Background worker to process NSFW detection tasks."""
    print("NSFW Worker started...")
    while True:
        task_retrieved = False
        try:
            message, image_bytes = await nsfw_queue.get()
            task_retrieved = True

            result = await asyncio.to_thread(is_nsfw, image_bytes)

            nsfw = result['is_nsfw']
            nsfw_confidence = result['nsfw_confidence']
            top_category = result['top_category']
            top_confidence = result['top_confidence']

            stripped_chat_id = str(message.chat.id).removeprefix("-100")
            message_link = f"https://t.me/{message.chat.username if message.chat.username else 'c/' + stripped_chat_id}/{message.message_id}"

            user_data = (
                f"link {message_link}\n\n"
                f"User: {message.from_user.full_name} (id: {message.from_user.id}) "
                f"[Profile](tg://user?id={message.from_user.id}) username: @{message.from_user.username}"
            )

            if nsfw:
                response = (
                    f"🚨 NSFW Content Detected! 🚨\n\n"
                    f"Top Category: {top_category}\n"
                    f"Confidence: {top_confidence*100:.2f}%\n"
                    f"NSFW Confidence: {nsfw_confidence*100:.2f}%\n\n"
                    f"{user_data}"
                )
            else:
                response = (
                    f"✅ The image seems safe for work!\n\n"
                    f"Top Category: {top_category}\n"
                    f"Confidence: {top_confidence*100:.2f}%\n"
                    f"{user_data}"
                )

            bot_msg = await bot.send_message(os.getenv("DEVELOPER_ID"), response, parse_mode="Markdown")
            group_admin = (await Group.aio_get(Group.id == message.chat.id)).user_id
    
            if nsfw:
                await bot.send_message(
                    group_admin, 
                    f"🚨 Alert 🚨\n\nlink: {message_link}",
                    reply_markup=await get_false_inkb(bot_msg.message_id),
                    )

        except asyncio.CancelledError:
            # Worker is being cancelled during shutdown
            break
        except Group.DoesNotExist:
            pass # TODO: Handle group not found
        except Exception as e:
            print(f"[NSFW Worker Error] {e}")
        finally:
            if task_retrieved:
                nsfw_queue.task_done()


# --- START CMD ---
@dp.message(Command('start'), F.chat.type == ChatType.PRIVATE)
async def start_cmd(message: types.Message):
    await message.reply("👋 Welcome!\nTo start monitoring just add me to your super group\n\nP.s. Currently we only support supergroups.")
    await User.aio_get_or_create(id=message.from_user.id)



# --- GROUP HANDLERS ---
@dp.my_chat_member(
        ChatMemberUpdatedFilter(IS_MEMBER), 
        F.chat.type.in_([ChatType.SUPERGROUP])
    )
async def added_to_group(update: types.ChatMemberUpdated, bot: Bot):
    user_id = update.from_user.id
    group_id = update.chat.id

    user, created = await Group.aio_get_or_create(id=group_id, defaults={'user': user_id})

    if created:
        await bot.send_message(user_id, f"🔍 Starting to monitor {update.chat.title}")
    else:
        await bot.send_message(user_id, f"🧐 I was already added to group {update.chat.title}")


@dp.my_chat_member(
    ChatMemberUpdatedFilter(IS_NOT_MEMBER),
    F.chat.type.in_([ChatType.SUPERGROUP])
)
async def removed_from_group(update: types.ChatMemberUpdated, bot: Bot):
    group_id = update.chat.id

    try:
        group = await Group.aio_get(id=group_id)
        user_id = group.user_id
        await group.aio_delete_instance()
        await bot.send_message(user_id, f"❌ Stopped monitoring {update.chat.title}")
    except Group.DoesNotExist:
        print("Group not found in DB")



# --- MESSAGE HANDLER ---
@dp.message(
        F.chat.type.in_([ChatType.SUPERGROUP]),
        ~F.new_chat_members, ~F.left_chat_member)
async def group_message_handler(message: types.Message):
    user = await bot.get_chat(message.from_user.id)
    user_photo = user.photo

    if not user_photo:
        # print("No profile photo found.") #TODO: Log this event
        return

    channel = await bot.get_chat(user.personal_chat.id)
    channel_photo = channel.photo

    if not channel_photo:
        # print("No channel photo found.") #TODO: Log this event
        return

    
    file_info = await bot.get_file(user_photo.big_file_id)
    file_path = file_info.file_path

    downloaded_file = await bot.download_file(file_path)
    image_bytes = downloaded_file.getvalue()
    # print("Putting task in queue...")
    await nsfw_queue.put((message, image_bytes))



# --- CALLBACK QUERY HANDLER ---
@dp.callback_query(FalseAlertCallback.filter())
async def false_alert_handler(callback: types.CallbackQuery, callback_data: FalseAlertCallback):
    await bot.send_message(
        os.getenv("DEVELOPER_ID"),
        f"📩 False Alert Reported!\n\n",
        reply_to_message_id=callback_data.message_id
    )
    
    await callback.answer("False alert reported!")
    await callback.message.edit_text("Thank you for your feedback and sorry for the inconvenience!")



# --- KEYBOARD ---
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


# --- SETUP ---
@dp.startup()
async def startup():
    print("Online")
    with db.allow_sync():
        db.create_tables([User, Group])

    await db.aio_connect()

    for _ in range(4):
        asyncio.create_task(nsfw_worker(bot))


@dp.shutdown()
async def shutdown():
    await bot.session.close()
    await db.aio_close()
    db.close()
    print("Offline")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, handle_signals=True)


if __name__ == "__main__":
    asyncio.run(main())
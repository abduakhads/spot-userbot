import asyncio

from aiogram import Bot

from bot.settings import DEVELOPER_ID
from bot.utils import get_time
from bot.detect import is_nsfw
from bot.keyboards import get_false_inkb
from bot.database import Group

nsfw_queue = asyncio.Queue()


async def nsfw_worker(bot: Bot):
    """Background worker to process NSFW detection tasks."""
    print(f"{get_time()} - NSFW Worker started...")
    while True:
        task_retrieved = False
        try:
            message, image_bytes = await nsfw_queue.get()
            task_retrieved = True

            group = (await Group.aio_get_or_none(Group.id == message.chat.id))
            
            if not group:
                await bot.leave_chat(message.chat.id)
                continue

            group_admin = group.user_id

            result = await asyncio.to_thread(is_nsfw, image_bytes)

            nsfw = result['is_nsfw']
            nsfw_confidence = result['nsfw_confidence']
            top_category = result['top_category']
            top_confidence = result['top_confidence']

            stripped_chat_id = str(message.chat.id).removeprefix("-100")
            chat_link = f"https://t.me/{message.chat.username if message.chat.username else 'c/' + stripped_chat_id}"
            message_link = chat_link + f"/{message.message_id}"

            # Escape special Markdown characters in user data
            def escape_markdown(text):
                if text is None:
                    return "N/A"
                return str(text).replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)').replace('`', '\\`')
            
            username = f"@{message.from_user.username}" if message.from_user.username else "N/A"
            
            user_data = (
                f"link {message_link}\n\n"
                f"User: {escape_markdown(message.from_user.full_name)} (id: {message.from_user.id}) "
                f"[Profile](tg://user?id={message.from_user.id}) username: {escape_markdown(username)}"
            )

            if nsfw:
                response = (
                    f"🚨 NSFW Content Detected! 🚨\n\n"
                    f"Top Category: {escape_markdown(top_category)}\n"
                    f"Confidence: {top_confidence*100:.2f}%\n"
                    f"NSFW Confidence: {nsfw_confidence*100:.2f}%\n\n"
                    f"{user_data}"
                )
            else:
                response = (
                    f"✅ The image seems safe for work!\n\n"
                    f"Top Category: {escape_markdown(top_category)}\n"
                    f"Confidence: {top_confidence*100:.2f}%\n"
                    f"{user_data}"
                )

            try:
                bot_msg = await bot.send_message(DEVELOPER_ID, response, parse_mode="Markdown")
            except Exception as parse_error:
                # If Markdown parsing fails, send without formatting
                print(f"{get_time()} - Markdown parse error, sending as plain text: {parse_error}")
                bot_msg = await bot.send_message(DEVELOPER_ID, response)

            notification = "🚨 Alert 🚨\n\n"
            notification += "Confidence: " + f"{top_confidence*100:.2f}%\n\n"
            notification += ("link: " + message_link) if not group.delete_message else ("in group: " + chat_link) + "\n"
            notification += "\nuser message was deleted" if group.delete_message else ""
            notification += "\nuser was kicked" if group.kick_bot else ""

            if nsfw:
                if group.delete_message:
                    await bot.delete_message(
                        chat_id=group.id,
                        message_id=message.message_id
                    )
                if group.kick_bot:
                    await bot.ban_chat_member(
                        chat_id=group.id, 
                        user_id=message.from_user.id,
                        revoke_messages=True)
                await bot.send_message(
                    chat_id=group_admin,
                    text=notification,
                    reply_markup=await get_false_inkb(bot_msg.message_id),
                )

        except asyncio.CancelledError:
            # Worker is being cancelled during shutdown
            break
        except Group.DoesNotExist:
            pass # TODO: Handle group not found
        except Exception as e:
            print(f"{get_time()} - [NSFW Worker Error] {e}")
        finally:
            if task_retrieved:
                nsfw_queue.task_done()
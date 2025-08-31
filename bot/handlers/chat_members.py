from aiogram import Bot, Router, F, types
from aiogram.enums import ChatType
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter

from bot.utils import get_time
from bot.database import Group

router = Router()


# --- BOT WAS ADDED TO SUPER GROUP ---
@router.my_chat_member(
        ChatMemberUpdatedFilter(IS_MEMBER), 
        F.chat.type.in_([ChatType.SUPERGROUP])
    )
async def added_to_group(update: types.ChatMemberUpdated, bot: Bot):
    user_id = update.from_user.id
    group_id = update.chat.id

    user, created = await Group.aio_get_or_create(id=group_id, defaults={'user': user_id})

    try:
        if created:
            await bot.send_message(user_id, f"🔍 Starting to monitor {update.chat.title}")
        else:
            await bot.send_message(user_id, f"🧐 I was already added to group {update.chat.title}")
    except:
        pass #TODO


# --- BOT WAS REMOVED FROM SUPER GROUP ---
@router.my_chat_member(
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
        print(f"{get_time()} - [Group Not Found] Group not found in DB")
    except:
        pass #TODO
        
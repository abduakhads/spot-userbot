from aiogram import Bot, Router, F, types
from aiogram.enums import ChatType
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, JOIN_TRANSITION, IS_MEMBER

from bot.utils import get_time
from bot.database import Group, User

router = Router()


# --- BOT WAS ADDED TO SUPER GROUP ---
@router.my_chat_member(
        ChatMemberUpdatedFilter(JOIN_TRANSITION), 
        F.chat.type.in_([ChatType.SUPERGROUP]),
        # F.old_chat_member.status.not_in(["member", "administrator", "creator"])
    )
async def added_to_super_group(update: types.ChatMemberUpdated, bot: Bot):
    user_id = update.from_user.id
    group_id = update.chat.id
    user = await User.aio_get_or_none(id=user_id)
    if not user:
        await update.answer(f"[{update.from_user.full_name}](tg://user?id={update.from_user.id}) Please first start a chat with me!\n\nsend [/start](t.me/{(await bot.get_me()).username}?start=retry)", parse_mode="Markdown")
        await bot.leave_chat(group_id)
        return

    group, created = await Group.aio_get_or_create(id=group_id, defaults={'user': user_id})

    try:
        if created:
            await bot.send_message(user_id, f"🔍 Starting to monitor {update.chat.title}")
        else:
            await bot.send_message(user_id, f"🧐 wasn't I already added to group {update.chat.title}")
    except:
        pass #TODO



# --- BOT PERMISSIONS WERE CHANGED ---
@router.my_chat_member(
    ChatMemberUpdatedFilter(IS_MEMBER),
    F.chat.type.in_([ChatType.SUPERGROUP])
)
async def permission_change(update: types.ChatMemberUpdated, bot: Bot):
    member = await bot.get_chat_member(update.chat.id, bot.id)
    group = await Group.aio_get(Group.id == update.chat.id)
    flag = False

    if update.old_chat_member.status in ["administrator"] and not member.status in ["administrator"]:
        flag = True

    if flag or not member.can_delete_messages:
        group.delete_message = False

    if flag or not member.can_restrict_members:
        group.kick_bot = False

    await group.aio_save()



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
    # except Group.DoesNotExist:
    #     print(f"{get_time()} - [Group Not Found] Group not found in DB")
    except:
        pass #TODO



# --- BOT WAS BLOCKED BY USER ---
@router.my_chat_member(
    ChatMemberUpdatedFilter(IS_NOT_MEMBER),
    F.chat.type.in_([ChatType.PRIVATE])
)
async def blocked_bot(update: types.ChatMemberUpdated, bot: Bot):
    groups = await Group.select().where(Group.user_id == update.from_user.id).aio_execute()
    for group in groups:
        await bot.leave_chat(group.id)
        # await group.aio_delete_instance()

    await User.delete().where(User.id == update.from_user.id).aio_execute()



# --- BOT WAS ADDED TO GROUP ---
@router.my_chat_member(
        ChatMemberUpdatedFilter(JOIN_TRANSITION), 
        F.chat.type.in_([ChatType.GROUP])
    )
async def added_to_group(update: types.ChatMemberUpdated, bot: Bot):
    await update.answer("I only work in super groups. Please add me to a super group.")
    await bot.leave_chat(update.chat.id)
from aiogram import Bot, Router, F, types
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramBadRequest

from bot import keyboards as kb
from bot.handlers import common
from bot.utils import get_time
from bot.database import User
from bot.settings import DEVELOPER_ID


router = Router()



# --- START CMD ---
@router.message(Command('start'), F.chat.type == ChatType.PRIVATE)
async def start_cmd(message: types.Message, command: CommandObject, bot: Bot):
    # print(await bot.get_my_default_administrator_rights())
    try:
        await message.reply(
            text="👋 Welcome!",
            reply_markup=await kb.get_main_kb()
        )
        if not command.args:
            await message.answer(
                text="To start monitoring just add me to your super group.\n\nP.s. Currently we only support supergroups.",
                reply_markup=await kb.get_add_group_inkb()
            )
        elif command.args == "retry":
            await message.answer(
                text=f"Now You can add me to super group again.\n\nP.s. Currently we only support supergroups.",
                reply_markup=await kb.get_add_group_inkb()
            )
        elif command.args == "donate":
            await message.answer(
                text="🙏 Big thanks for considering a donation! \nYour support helps keep the bot running." \
                "\n\nPlease choose the amount to donate:",
                reply_markup=await kb.get_donations_inkb()
            )
        await User.aio_get_or_create(id=message.from_user.id)
    except Exception as e:
        print(f"{get_time()} - [Error (start_cmd)] {e}")


# --- ANNOUNCE CMD ---
@router.message(Command('say'), F.from_user.id == int(DEVELOPER_ID), F.chat.type == ChatType.PRIVATE)
async def announce_cmd(message: types.Message, bot: Bot):
    text_parts = message.text.split(maxsplit=1)
    if len(text_parts) < 2:
        await message.reply("Please provide announcement text after the command.")
        return
    
    announcement_text = text_parts[1]
    users = await User.select().aio_execute()

    for user in users:
        try:
            await bot.send_message(user.id, f"📢 Announcement: \n\n{announcement_text}")
        except Exception as e:
            print(f"{get_time()} - Failed to send message to {user.id}: {e}")


# --- SAY TO CMD ---
@router.message(Command('sayto'), F.from_user.id == int(DEVELOPER_ID), F.chat.type == ChatType.PRIVATE)
async def sayto_cmd(message: types.Message, bot: Bot, command: CommandObject):
    args = command.args
    if args is None or len(args.split(" ")) < 2:
        await message.reply("Please provide the user id and the message to send. For example: \n\n`/sayto <user_id> <message>`", parse_mode="Markdown")
        return
    
    user_id = args.split(" ")[0]
    text = " ".join(args.split(" ")[1:])
    if text is None:
        await message.answer("Please provide the message to send.")
        return

    try:
        await bot.send_message(user_id, text)
        await message.answer("✅ Message sent successfully.")
    except TelegramBadRequest as e:
        err_text = "The message could not be sent.\n\nError: " + str(e.message)
        await message.answer(err_text)
        return


# --- HELP CMD ---
@router.message(Command('help'), F.chat.type == ChatType.PRIVATE)
async def help_cmd(message: types.Message, bot: Bot):
    await common.help_cmd(message, bot)


# --- DONATE CMD ---
@router.message(Command('donate'), F.chat.type == ChatType.PRIVATE)
async def donate_cmd(message: types.Message, command: CommandObject, bot: Bot):
    amount = command.args
    if amount is None or not amount.isdigit() or int(amount) <= 0:
        await message.reply("Please type a valid donation amount after the command. For example: \n\n`/donate 10`\n\nto donate 10 ⭐.", parse_mode="Markdown")
        return
    await common.donate_amount_cmd(message, bot, int(amount))


# --- REFUND CMD ---
@router.message(Command("refund"), F.from_user.id == int(DEVELOPER_ID), F.chat.type == ChatType.PRIVATE)
async def refund_cmd(message: types.Message, bot: Bot, command: CommandObject):
    if command.args == None or len(command.args.split(" ")) != 2:
        await message.reply("Please provide the user id and Telegram payment charge ID to process the refund. For example: \n\n`/refund <user_id> <telegram_payment_charge_id>`", parse_mode="Markdown")
        return
    
    args = command.args.split(" ")
    
    user_id = args[0]
    t_id = args[1]
    if t_id is None:
        await message.answer("Please provide the Telegram payment charge ID to process the refund.")
        return

    try:
        await bot.refund_star_payment(
            user_id=user_id,
            telegram_payment_charge_id=t_id
        )
        await message.answer("✅ Refund processed successfully.")

    except TelegramBadRequest as e:
        err_text = "The refund could not be processed.\n\nError: " + str(e.message)

        if "CHARGE_ALREADY_REFUNDED" in e.message:
            err_text = "This payment has already been refunded."

        await message.answer(err_text)
        return
    

# --- VIDEO MESSAGE HANDLER (FOR TESTING) ---
@router.message(F.video, F.chat.type == ChatType.PRIVATE, F.from_user.id == int(DEVELOPER_ID))
async def video_message_handler(message: types.Message, bot: Bot):
    await message.answer(
        text=f"`{message.video.file_id}`",
        parse_mode="MarkdownV2"
    )
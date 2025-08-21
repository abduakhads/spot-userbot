
import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from detect import is_nsfw

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command('start'))
async def start_command(message: types.Message, bot: Bot):
    user = await bot.get_chat(message.from_user.id)
    channel = await bot.get_chat(user.personal_chat.id)
    photo = channel.photo

    if not photo:
        return
    

    file_info = await bot.get_file(photo.big_file_id)
    file_path = file_info.file_path

    # Download the photo
    downloaded_file = await bot.download_file(file_path)
    image_bytes = downloaded_file.getvalue()

    result = is_nsfw(image_bytes)

    # Prepare response based on NSFW classification
    nsfw = result['is_nsfw']
    nsfw_confidence = result['nsfw_confidence']
    top_category = result['top_category']
    top_confidence = result['top_confidence']
    
    # Send a response to the user
    if nsfw:
        response = f"🚨 NSFW Content Detected! 🚨\n\n" \
                   f"Top Category: {top_category}\n" \
                   f"Confidence: {top_confidence*100:.2f}%\n" \
                   f"NSFW Confidence: {nsfw_confidence*100:.2f}%"
    else:
        response = f"✅ This image seems safe for work!\n\n" \
                   f"Top Category: {top_category}\n" \
                   f"Confidence: {top_confidence*100:.2f}%"
    
    # Send the response
    await message.reply(response, parse_mode="Markdown")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, handle_signals=True),


# Start the bot
@dp.startup()
async def start_bot():
    print("Online")


if __name__ == "__main__":
    asyncio.run(main())

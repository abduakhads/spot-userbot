from aiogram import types

from bot import utils
from bot.database import Group
from bot.settings import BOT_USERNAME

async def get_false_inkb(message_id: str) -> types.InlineKeyboardMarkup:
    confrmkb = types.InlineKeyboardMarkup(
        inline_keyboard=[[
            types.InlineKeyboardButton(
                text="Report False Alert 📤", 
                callback_data=utils.FalseAlertCallback(message_id=message_id).pack()
            )
        ]]
    )
    return confrmkb


async def get_main_kb() -> types.ReplyKeyboardMarkup:
    main_kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="My Groups 👥")],
            [types.KeyboardButton(text="💬 Help"), types.KeyboardButton(text="Donate 🕊️")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return main_kb


async def get_groups_list_inkb(groups: list) -> types.InlineKeyboardMarkup:
    groups_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=group.title, callback_data=utils.GroupSettingsCallback(group_id=group.id).pack())] for group in groups
        ] + [
            [types.InlineKeyboardButton(text="👥 Add", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"), types.InlineKeyboardButton(text="✖️ Close", callback_data="close")]
        ]
    )
    
    return groups_kb


async def get_group_settings_inkb(group: Group) -> types.InlineKeyboardMarkup:
    if not group:
        return None
    
    settings_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=f"{'▶️ Enable' if not group.kick_bot else '⏸️ Disable'} Kick User Bots",
                    callback_data=utils.ToggleKickBotCallback(group_id=group.id).pack()
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=f"{'▶️ Enable' if not group.delete_message else '⏸️ Disable'} Delete Messages",
                    callback_data=utils.ToggleDeleteMessageCallback(group_id=group.id).pack()
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🗑 Delete Group",
                    callback_data=utils.DeleteGroupCallback(group_id=group.id).pack()
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="⬅️ Back",
                    callback_data=utils.BackCallback(function="list_my_groups").pack()
                ),
                types.InlineKeyboardButton(
                    text="✖️ Close",
                    callback_data="close"
                )
            ]
        ]
    )
    return settings_kb



async def get_confirm_inkb(group_id: int | str, function: list) -> types.InlineKeyboardMarkup:
    confirm_inkb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="✅ Confirm",
                    callback_data=utils.ConfirmCallback(group_id=group_id, confirm=True, function=function[1]).pack()
                ),
                types.InlineKeyboardButton(
                    text="❌ Cancel",
                    callback_data=utils.ConfirmCallback(group_id=group_id, confirm=False, function=function[0]).pack()
                )
            ]
        ]
    )
    return confirm_inkb


async def get_add_group_inkb() -> types.InlineKeyboardMarkup:
    add_group_inkb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="➕ Add to Group",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                )
            ]
        ]
    )
    return add_group_inkb


async def get_donations_inkb() -> types.InlineKeyboardMarkup:
    donations_inkb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="⭐️ 1",
                    callback_data=utils.DonateAmountCallback(amount=1).pack()
                ),
                types.InlineKeyboardButton(
                    text="⭐️ 5",
                    callback_data=utils.DonateAmountCallback(amount=5).pack()
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="⭐️ 10",
                    callback_data=utils.DonateAmountCallback(amount=10).pack()
                ),
                types.InlineKeyboardButton(
                    text="⭐️ 20",
                    callback_data=utils.DonateAmountCallback(amount=20).pack()
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="⭐️ 50",
                    callback_data=utils.DonateAmountCallback(amount=50).pack()
                ),
                types.InlineKeyboardButton(
                    text="⭐️ 100",
                    callback_data=utils.DonateAmountCallback(amount=100).pack()
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🖋 Custom Amount",
                    callback_data=utils.DonateAmountCallback(amount=0).pack()
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="✖️ Cancel",
                    callback_data="close"
                )
            ]
        ]
    )
    return donations_inkb


async def get_donate_inkb(amount: int) -> types.InlineKeyboardMarkup:
    donate_inkb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=f"Donate {amount} ⭐️ ",
                    pay=True
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="✖️ Close",
                    callback_data="close"
                )
            ]
        ]
    )
    return donate_inkb
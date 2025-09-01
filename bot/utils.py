import datetime

from aiogram.filters.callback_data import CallbackData


class FalseAlertCallback(CallbackData, prefix="false_alert"):
    message_id: int | str 


class GroupSettingsCallback(CallbackData, prefix="group_settings"):
    group_id: int | str 


class ToggleKickBotCallback(CallbackData, prefix="toggle_kick_bot"):
    group_id: int | str 


class ToggleDeleteMessageCallback(CallbackData, prefix="toggle_delete_message"):
    group_id: int | str


class DeleteGroupCallback(CallbackData, prefix="delete_group"):
    group_id: int | str


class BackCallback(CallbackData, prefix="back"):
    function: str


class ConfirmCallback(CallbackData, prefix="confirmation"):
    group_id: int | str
    confirm: bool
    function: str


def get_time() -> str:
    """Get the current time formatted as a string."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
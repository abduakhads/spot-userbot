import datetime

from aiogram.filters.callback_data import CallbackData


class FalseAlertCallback(CallbackData, prefix="false_alert"):
    message_id: int | str 


def get_time() -> str:
    """Get the current time formatted as a string."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
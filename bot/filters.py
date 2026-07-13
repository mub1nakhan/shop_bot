"""
Custom aiogram filters shared across handlers.
"""

from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from bot.config import get_bot_config


class IsAdmin(BaseFilter):
    """Passes only for Telegram users listed in ADMIN_IDS (.env)."""

    async def __call__(self, event: TelegramObject) -> bool:
        user = getattr(event, "from_user", None)
        if user is None:
            return False
        admin_ids = get_bot_config().admin_ids
        return user.id in admin_ids
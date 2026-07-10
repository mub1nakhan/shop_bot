"""
Ensures every incoming update from a real Telegram user is reflected as a
TelegramUser row in the DB, and makes that row available to handlers via
`data["db_user"]` — so handlers never need to query for it themselves.
"""

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from bot.services.user_service import get_or_create_user


class DbUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        aiogram_user: User | None = data.get("event_from_user")
        if aiogram_user is not None and not aiogram_user.is_bot:
            db_user = await get_or_create_user(
                telegram_id=aiogram_user.id,
                username=aiogram_user.username,
                full_name=aiogram_user.full_name,
                language_code=aiogram_user.language_code,
            )
            data["db_user"] = db_user
        return await handler(event, data)
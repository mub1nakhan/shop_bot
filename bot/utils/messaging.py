"""
Telegram won't let you `edit_text` a message that has no text (e.g. a photo
message with a caption). Since product detail cards are photo messages while
category/product-list screens are plain text, navigating between them needs
a "delete + resend" fallback instead of edit. This helper centralizes that
so handlers can just call one function regardless of the previous message type.
"""

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup


async def safe_edit_or_send(
    callback: CallbackQuery, text: str, reply_markup: InlineKeyboardMarkup | None = None
) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
        return
    except TelegramBadRequest:
        pass

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    await callback.message.answer(text, reply_markup=reply_markup)
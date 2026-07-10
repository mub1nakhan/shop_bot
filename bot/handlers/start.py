

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.keyboards.callback_data import NavigateCallback
from bot.keyboards.inline import categories_keyboard
from bot.services.category_service import get_root_categories
from bot.services.user_service import get_bot_settings
from bot.utils.formatters import format_main_menu_prompt
from bot.utils.messaging import safe_edit_or_send

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    settings = await get_bot_settings()
    categories = await get_root_categories()

    if not categories:
        await message.answer(
            f"{settings.welcome_text}\n\nHozircha kategoriyalar qo'shilmagan. Tez orada to'ldiriladi."
        )
        return

    await message.answer(
        format_main_menu_prompt(settings.welcome_text),
        reply_markup=categories_keyboard(categories),
    )


@router.callback_query(NavigateCallback.filter(F.action == "main_menu"))
async def cb_main_menu(callback: CallbackQuery):
    settings = await get_bot_settings()
    categories = await get_root_categories()

    if not categories:
        await safe_edit_or_send(
            callback, f"{settings.welcome_text}\n\nHozircha kategoriyalar qo'shilmagan.", None
        )
        await callback.answer()
        return

    await safe_edit_or_send(
        callback,
        format_main_menu_prompt(settings.welcome_text),
        categories_keyboard(categories),
    )
    await callback.answer()


@router.callback_query(NavigateCallback.filter(F.action == "categories"))
async def cb_back_to_categories(callback: CallbackQuery):
    # Same rendering as main menu -- kept as a distinct handler for clarity
    # in case "categories" and "main menu" ever diverge (e.g. different copy).
    await cb_main_menu(callback)
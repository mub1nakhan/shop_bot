from aiogram import Router
from aiogram.types import CallbackQuery, Message

router = Router(name="fallback")


@router.callback_query()
async def cb_noop_or_unknown(callback: CallbackQuery):
    # Catches the "noop" page-indicator button and any callback that didn't
    # match a more specific handler above, so users never see a spinning
    # "loading" state on an unhandled tap.
    await callback.answer()


@router.message()
async def unknown_message(message: Message):
    await message.answer(
        "Buyruqni tushunmadim 🤔\nAsosiy menyuga qaytish uchun /start buyrug'ini yuboring."
    )
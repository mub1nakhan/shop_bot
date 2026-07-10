
"""
Short-lived FSM flow: user taps "📞 Buyurtma berish" on a product ->
bot asks for a phone number (share contact button) -> saved as a Lead in DB
and admin can see/process it in Django Admin.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from bot.keyboards.callback_data import OrderCallback
from bot.keyboards.inline import share_phone_keyboard
from bot.services.product_service import get_product
from bot.services.user_service import create_lead, save_phone_number

router = Router(name="order")


class OrderStates(StatesGroup):
    waiting_for_phone = State()


@router.callback_query(OrderCallback.filter())
async def cb_order_start(callback: CallbackQuery, callback_data: OrderCallback, state: FSMContext):
    product = await get_product(callback_data.product_id)
    if product is None:
        await callback.answer("Mahsulot topilmadi.", show_alert=True)
        return

    await state.update_data(product_id=product.pk)
    await state.set_state(OrderStates.waiting_for_phone)

    await callback.message.answer(
        f"📞 <b>{product.name}</b> uchun buyurtma.\n\n"
        "Operatorlarimiz siz bilan bog'lanishi uchun telefon raqamingizni yuboring:",
        reply_markup=share_phone_keyboard(),
    )
    await callback.answer()


@router.message(OrderStates.waiting_for_phone, F.contact)
async def process_shared_contact(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await _finish_order(message, state, phone_number)


@router.message(OrderStates.waiting_for_phone, F.text)
async def process_typed_phone(message: Message, state: FSMContext):
    text = message.text.strip()
    digits = "".join(ch for ch in text if ch.isdigit() or ch == "+")
    if len(digits) < 9:
        await message.answer(
            "Iltimos, to'g'ri telefon raqam kiriting (masalan: +998901234567) "
            "yoki pastdagi tugma orqali yuboring."
        )
        return
    await _finish_order(message, state, digits)


async def _finish_order(message: Message, state: FSMContext, phone_number: str):
    data = await state.get_data()
    product_id = data.get("product_id")

    await save_phone_number(message.from_user.id, phone_number)
    await create_lead(message.from_user.id, product_id, phone_number)
    await state.clear()

    await message.answer(
        "✅ Rahmat! So'rovingiz qabul qilindi. Operatorlarimiz tez orada siz bilan bog'lanishadi.",
        reply_markup=ReplyKeyboardRemove(),
    )
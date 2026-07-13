"""
In-bot admin/owner panel.

Only reachable by Telegram user IDs listed in ADMIN_IDS (.env) -- see
bot/filters.py:IsAdmin, applied to the whole router below. This exists so
the shop owner never needs direct access to Django Admin (where a wrong
click can silently break data, as happened with the category/product
mismatch bug) -- everything here is guided, narrow, and hard to misuse.
"""

from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.filters import IsAdmin
from bot.keyboards.admin_inline import (
    admin_cancel_keyboard,
    admin_categories_keyboard,
    admin_leads_keyboard,
    admin_menu_keyboard,
    admin_new_product_categories_keyboard,
    admin_product_detail_keyboard,
    admin_products_keyboard,
)
from bot.keyboards.callback_data import (
    AdminCategoryCallback,
    AdminEditPriceCallback,
    AdminLeadDoneCallback,
    AdminNavCallback,
    AdminNewProductCatCallback,
    AdminProductCallback,
    AdminProductsPageCallback,
    AdminToggleActiveCallback,
)
from bot.services.admin_services import (
    add_product_image_from_bytes,
    create_product,
    get_leaf_categories,
    get_product_for_admin,
    get_products_in_category,
    get_stats,
    get_unprocessed_leads,
    mark_lead_done,
    toggle_product_active,
    update_product_price,
)
from bot.utils.formatters import (
    format_admin_menu_prompt,
    format_admin_product_detail,
    format_lead_line,
    format_numbered_admin_products,
    format_stats,
)
from bot.utils.messaging import safe_edit_or_send
from bot.utils.pagination import paginate
from django.conf import settings

router = Router(name="admin")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


class AdminAddProduct(StatesGroup):
    waiting_category = State()
    waiting_name = State()
    waiting_price = State()
    waiting_description = State()
    waiting_photos = State()


class AdminEditPrice(StatesGroup):
    waiting_price = State()


def _parse_price(raw: str) -> Decimal | None:
    cleaned = raw.strip().replace(" ", "").replace(",", "")
    try:
        price = Decimal(cleaned)
    except InvalidOperation:
        return None
    return price if price > 0 else None


# ---------------------------------------------------------------- entry ----


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(format_admin_menu_prompt(), reply_markup=admin_menu_keyboard())


# ------------------------------------------------------------- nav menu ----


@router.callback_query(AdminNavCallback.filter())
async def cb_admin_nav(
    callback: CallbackQuery, callback_data: AdminNavCallback, state: FSMContext
):
    action = callback_data.action

    if action == "menu":
        await state.clear()
        await safe_edit_or_send(callback, format_admin_menu_prompt(), admin_menu_keyboard())

    elif action == "products":
        await state.clear()
        categories = await get_leaf_categories()
        if not categories:
            await safe_edit_or_send(
                callback, "Hozircha kategoriyalar yo'q.", admin_menu_keyboard()
            )
        else:
            await safe_edit_or_send(
                callback, "📂 Kategoriyani tanlang:", admin_categories_keyboard(categories)
            )

    elif action == "leads":
        await state.clear()
        leads = await get_unprocessed_leads()
        if not leads:
            await safe_edit_or_send(
                callback, "🛒 Hozircha yangi buyurtmalar yo'q.", admin_menu_keyboard()
            )
        else:
            text = "🛒 <b>Yangi buyurtmalar:</b>\n\n" + "\n\n".join(
                f"#{lead.pk}\n{format_lead_line(lead)}" for lead in leads
            )
            await safe_edit_or_send(callback, text, admin_leads_keyboard(leads))

    elif action == "new_product":
        categories = await get_leaf_categories()
        if not categories:
            await state.clear()
            await safe_edit_or_send(
                callback,
                "Avval kamida bitta kategoriya (sub-kategoriya) yaratilishi kerak "
                "(hozircha bu faqat Django admin orqali qilinadi).",
                admin_menu_keyboard(),
            )
        else:
            await state.set_state(AdminAddProduct.waiting_category)
            await safe_edit_or_send(
                callback,
                "➕ Yangi mahsulot uchun kategoriyani tanlang:",
                admin_new_product_categories_keyboard(categories),
            )

    elif action == "stats":
        await state.clear()
        stats = await get_stats()
        await safe_edit_or_send(callback, format_stats(stats), admin_menu_keyboard())

    await callback.answer()


# ------------------------------------------------------- browse products ----


async def _render_admin_products(callback: CallbackQuery, category_id: int, page_number: int):
    products = await get_products_in_category(category_id)
    if not products:
        await safe_edit_or_send(
            callback, "Bu kategoriyada hali mahsulot yo'q.", admin_menu_keyboard()
        )
        await callback.answer()
        return

    page = paginate(products, page_number, settings.ADMIN_PRODUCTS_PAGE_SIZE)
    text = "📦 Mahsulotni tanlang:\n\n" + format_numbered_admin_products(page.items)
    await safe_edit_or_send(
        callback,
        text,
        admin_products_keyboard(page, category_id),
    )
    await callback.answer()


@router.callback_query(AdminCategoryCallback.filter())
async def cb_admin_category(callback: CallbackQuery, callback_data: AdminCategoryCallback):
    await _render_admin_products(callback, callback_data.category_id, page_number=0)


@router.callback_query(AdminProductsPageCallback.filter())
async def cb_admin_products_page(
    callback: CallbackQuery, callback_data: AdminProductsPageCallback
):
    await _render_admin_products(callback, callback_data.category_id, callback_data.page)


@router.callback_query(AdminProductCallback.filter())
async def cb_admin_product(callback: CallbackQuery, callback_data: AdminProductCallback):
    product = await get_product_for_admin(callback_data.product_id)
    if product is None:
        await callback.answer("Mahsulot topilmadi.", show_alert=True)
        return
    await safe_edit_or_send(
        callback,
        format_admin_product_detail(product),
        admin_product_detail_keyboard(product, callback_data.category_id),
    )
    await callback.answer()


@router.callback_query(AdminToggleActiveCallback.filter())
async def cb_admin_toggle_active(
    callback: CallbackQuery, callback_data: AdminToggleActiveCallback
):
    product = await toggle_product_active(callback_data.product_id)
    if product is None:
        await callback.answer("Mahsulot topilmadi.", show_alert=True)
        return
    product = await get_product_for_admin(product.pk)  # refresh with prefetch
    await safe_edit_or_send(
        callback,
        format_admin_product_detail(product),
        admin_product_detail_keyboard(product, callback_data.category_id),
    )
    await callback.answer("Holat yangilandi ✅")


# ---------------------------------------------------------- edit price ----


@router.callback_query(AdminEditPriceCallback.filter())
async def cb_admin_edit_price_start(
    callback: CallbackQuery, callback_data: AdminEditPriceCallback, state: FSMContext
):
    await state.set_state(AdminEditPrice.waiting_price)
    await state.update_data(
        product_id=callback_data.product_id, category_id=callback_data.category_id
    )
    await callback.message.answer(
        "✏️ Yangi narxni kiriting (faqat raqam, masalan: 150000):",
        reply_markup=admin_cancel_keyboard(),
    )
    await callback.answer()


@router.message(AdminEditPrice.waiting_price, F.text)
async def process_new_price(message: Message, state: FSMContext):
    price = _parse_price(message.text)
    if price is None:
        await message.answer(
            "❗ Noto'g'ri format. Faqat musbat raqam kiriting, masalan: 150000"
        )
        return

    data = await state.get_data()
    await update_product_price(data["product_id"], price)
    product = await get_product_for_admin(data["product_id"])
    await state.clear()

    if product is None:
        await message.answer("Mahsulot topilmadi.")
        return

    await message.answer(
        f"✅ Narx yangilandi: {product.formatted_price}",
        reply_markup=admin_product_detail_keyboard(product, data["category_id"]),
    )


# -------------------------------------------------------------- leads ----


@router.callback_query(AdminLeadDoneCallback.filter())
async def cb_admin_lead_done(callback: CallbackQuery, callback_data: AdminLeadDoneCallback):
    lead = await mark_lead_done(callback_data.lead_id)
    if lead is None:
        await callback.answer("Topilmadi.", show_alert=True)
        return

    leads = await get_unprocessed_leads()
    if not leads:
        await safe_edit_or_send(
            callback, "🛒 Hozircha yangi buyurtmalar yo'q.", admin_menu_keyboard()
        )
    else:
        text = "🛒 <b>Yangi buyurtmalar:</b>\n\n" + "\n\n".join(
            f"#{l.pk}\n{format_lead_line(l)}" for l in leads
        )
        await safe_edit_or_send(callback, text, admin_leads_keyboard(leads))
    await callback.answer("Bajarildi deb belgilandi ✅")


# -------------------------------------------------- add new product (FSM) ----


@router.callback_query(AdminAddProduct.waiting_category, AdminNewProductCatCallback.filter())
async def cb_new_product_category(
    callback: CallbackQuery, callback_data: AdminNewProductCatCallback, state: FSMContext
):
    await state.update_data(category_id=callback_data.category_id)
    await state.set_state(AdminAddProduct.waiting_name)
    await callback.message.answer(
        "📝 Mahsulot nomini kiriting:", reply_markup=admin_cancel_keyboard()
    )
    await callback.answer()


@router.message(AdminAddProduct.waiting_name, F.text)
async def process_new_product_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("Nomi bo'sh bo'lmasligi kerak. Qayta kiriting:")
        return
    await state.update_data(name=name)
    await state.set_state(AdminAddProduct.waiting_price)
    await message.answer("💰 Narxni kiriting (faqat raqam, masalan: 150000):")


@router.message(AdminAddProduct.waiting_price, F.text)
async def process_new_product_price(message: Message, state: FSMContext):
    price = _parse_price(message.text)
    if price is None:
        await message.answer("❗ Noto'g'ri format. Faqat musbat raqam kiriting:")
        return
    await state.update_data(price=str(price))
    await state.set_state(AdminAddProduct.waiting_description)
    await message.answer(
        "📄 Qisqacha tavsif kiriting (yoki o'tkazib yuborish uchun \"-\" yuboring):"
    )


@router.message(AdminAddProduct.waiting_description, F.text)
async def process_new_product_description(message: Message, state: FSMContext):
    description = "" if message.text.strip() == "-" else message.text.strip()
    await state.update_data(description=description, photo_file_ids=[])
    await state.set_state(AdminAddProduct.waiting_photos)
    await message.answer(
        "🖼 Endi mahsulot rasmlarini yuboring (bir nechta bo'lishi mumkin).\n\n"
        "Hammasini yuborib bo'lgach, <b>\"Tayyor\"</b> deb yozing."
    )


@router.message(AdminAddProduct.waiting_photos, F.photo)
async def process_new_product_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    file_ids = data.get("photo_file_ids", [])
    file_ids.append(message.photo[-1].file_id)  # eng katta o'lchamdagi versiyasi
    await state.update_data(photo_file_ids=file_ids)
    await message.answer(
        f"✅ Rasm qabul qilindi ({len(file_ids)} ta).\n"
        "Yana rasm yuboring yoki \"Tayyor\" deb yozing."
    )


@router.message(AdminAddProduct.waiting_photos, F.text.lower() == "tayyor")
async def process_new_product_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    file_ids = data.get("photo_file_ids", [])
    if not file_ids:
        await message.answer("❗ Kamida bitta rasm yuborishingiz kerak.")
        return

    product = await create_product(
        category_id=data["category_id"],
        name=data["name"],
        price=Decimal(data["price"]),
        description=data.get("description", ""),
    )

    from bot.loader import bot as tg_bot  # local import: avoid import cycles at module load

    for i, file_id in enumerate(file_ids):
        file_bytes_io = await tg_bot.download(file_id)
        await add_product_image_from_bytes(
            product_id=product.pk,
            filename=f"{file_id}.jpg",
            content=file_bytes_io.read(),
            is_main=(i == 0),
        )

    await state.clear()
    await message.answer(
        f"✅ Yangi mahsulot qo'shildi: <b>{product.name}</b> ({len(file_ids)} ta rasm bilan)",
        reply_markup=admin_menu_keyboard(),
    )


@router.message(AdminAddProduct.waiting_photos, F.text)
async def process_new_product_photos_other_text(message: Message):
    await message.answer('🖼 Rasm yuboring yoki tugatish uchun "Tayyor" deb yozing.')
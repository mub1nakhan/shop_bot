import traceback

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto

from bot.keyboards.callback_data import (
    CategoryCallback,
    NavigateCallback,
    ProductCallback,
    ProductsPageCallback,
    SubcategoryCallback,
)
from bot.keyboards.inline import product_detail_keyboard, products_keyboard, subcategories_keyboard
from bot.services.category_service import get_category, get_subcategories
from bot.services.product_service import get_product, get_products_by_subcategory
from bot.utils.formatters import format_category_prompt, format_product_caption, format_products_prompt
from bot.utils.messaging import safe_edit_or_send
from bot.utils.pagination import paginate
from django.conf import settings

router = Router(name="catalog")


async def _render_subcategories_or_products(callback: CallbackQuery, category_id: int):
    """Shared logic: a category was selected -> show its subcategories,
    or, if it has none, treat it as a leaf and show its products directly."""
    category = await get_category(category_id)
    if category is None:
        await callback.answer("Kategoriya topilmadi yoki o'chirilgan.", show_alert=True)
        return

    subcategories = await get_subcategories(category_id)

    if subcategories:
        await safe_edit_or_send(
            callback,
            format_category_prompt(category.name),
            subcategories_keyboard(subcategories, category_id),
        )
        await callback.answer()
        return

    # No subcategories -> this category is itself a leaf; show its products.
    await _render_products(callback, subcategory_id=category_id, page_number=0)


@router.callback_query(CategoryCallback.filter())
async def cb_category_selected(callback: CallbackQuery, callback_data: CategoryCallback):
    await _render_subcategories_or_products(callback, callback_data.category_id)


@router.callback_query(NavigateCallback.filter(F.action == "subcategories"))
async def cb_back_to_subcategories(callback: CallbackQuery, callback_data: NavigateCallback):
    category = await get_category(callback_data.category_id)
    if category is None:
        await callback.answer("Kategoriya topilmadi.", show_alert=True)
        return
    subcategories = await get_subcategories(callback_data.category_id)
    await safe_edit_or_send(
        callback,
        format_category_prompt(category.name),
        subcategories_keyboard(subcategories, callback_data.category_id),
    )
    await callback.answer()


async def _render_products(callback: CallbackQuery, subcategory_id: int, page_number: int):
    subcategory = await get_category(subcategory_id)
    if subcategory is None:
        await callback.answer("Bo'lim topilmadi yoki o'chirilgan.", show_alert=True)
        return

    products = await get_products_by_subcategory(subcategory_id)
    if not products:
        await safe_edit_or_send(
            callback,
            f"{format_products_prompt(subcategory.name)}\n\nHozircha bu bo'limda mahsulot yo'q.",
            None,
        )
        await callback.answer()
        return

    page = paginate(products, page_number, settings.PRODUCTS_PAGE_SIZE)
    await safe_edit_or_send(
        callback,
        format_products_prompt(subcategory.name),
        products_keyboard(page, subcategory_id, subcategory.parent_id),
    )
    await callback.answer()


@router.callback_query(SubcategoryCallback.filter())
async def cb_subcategory_selected(callback: CallbackQuery, callback_data: SubcategoryCallback):
    await _render_products(callback, callback_data.subcategory_id, callback_data.page)


@router.callback_query(ProductsPageCallback.filter())
async def cb_products_page(callback: CallbackQuery, callback_data: ProductsPageCallback):
    await _render_products(callback, callback_data.subcategory_id, callback_data.page)


@router.callback_query(ProductCallback.filter())
async def cb_product_selected(callback: CallbackQuery, callback_data: ProductCallback):
    product = await get_product(callback_data.product_id)
    if product is None:
        await callback.answer("Mahsulot topilmadi yoki o'chirilgan.", show_alert=True)
        return

    caption = format_product_caption(
        product.name, product.formatted_price, product.short_description
    )
    keyboard = product_detail_keyboard(product, callback_data.subcategory_id)

    # The product card is a NEW message (can't "edit" a text message into a
    # photo/album message reliably) — delete the old list message first.
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    images = list(product.images.all())
    # Asosiy rasm bo'lsa birinchi o'ringa qo'yamiz, keyin order bo'yicha.
    images.sort(key=lambda img: (not img.is_main, img.order))

    if images:
        media = [
            InputMediaPhoto(
                media=FSInputFile(img.image.path),
                caption=caption if i == 0 else None,
            )
            for i, img in enumerate(images[:10])  # Telegram albomda max 10 ta rasm
        ]
        try:
            await callback.message.answer_media_group(media=media)
        except Exception:
            traceback.print_exc()
            await callback.message.answer(caption)
        await callback.message.answer("👇", reply_markup=keyboard)
    else:
        await callback.message.answer(caption, reply_markup=keyboard)

    await callback.answer()
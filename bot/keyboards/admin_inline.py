"""Inline keyboards for the in-bot owner/admin panel."""

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.callback_data import (
    AdminCategoryCallback,
    AdminEditPriceCallback,
    AdminLeadDoneCallback,
    AdminNavCallback,
    AdminNewProductCatCallback,
    AdminProductCallback,
    AdminToggleActiveCallback,
)
from catalog.models import Category, Product
from users.models import Lead

BACK_TO_ADMIN_MENU = InlineKeyboardButton(
    text="⬅️ Admin menyu", callback_data=AdminNavCallback(action="menu").pack()
)


def admin_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📦 Mahsulotlar", callback_data=AdminNavCallback(action="products"))
    builder.button(text="🛒 Buyurtmalar", callback_data=AdminNavCallback(action="leads"))
    builder.button(text="➕ Yangi mahsulot", callback_data=AdminNavCallback(action="new_product"))
    builder.button(text="📊 Statistika", callback_data=AdminNavCallback(action="stats"))
    builder.adjust(2)
    return builder.as_markup()


def admin_categories_keyboard(categories: list[Category]):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat.name, callback_data=AdminCategoryCallback(category_id=cat.pk))
    builder.adjust(2)
    builder.row(BACK_TO_ADMIN_MENU)
    return builder.as_markup()


def admin_new_product_categories_keyboard(categories: list[Category]):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(
            text=cat.name, callback_data=AdminNewProductCatCallback(category_id=cat.pk)
        )
    builder.adjust(2)
    builder.row(BACK_TO_ADMIN_MENU)
    return builder.as_markup()


def admin_products_keyboard(products: list[Product], category_id: int):
    builder = InlineKeyboardBuilder()
    for p in products:
        status_icon = "🟢" if p.is_active else "🔴"
        builder.button(
            text=f"{status_icon} {p.name} — {p.formatted_price}",
            callback_data=AdminProductCallback(category_id=category_id, product_id=p.pk),
        )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Kategoriyalar",
            callback_data=AdminNavCallback(action="products").pack(),
        ),
        BACK_TO_ADMIN_MENU,
    )
    return builder.as_markup()


def admin_product_detail_keyboard(product: Product, category_id: int):
    builder = InlineKeyboardBuilder()
    toggle_text = "🔴 Nofaol qilish" if product.is_active else "🟢 Faol qilish"
    builder.row(
        InlineKeyboardButton(
            text=toggle_text,
            callback_data=AdminToggleActiveCallback(
                category_id=category_id, product_id=product.pk
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="✏️ Narxni o'zgartirish",
            callback_data=AdminEditPriceCallback(
                category_id=category_id, product_id=product.pk
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Mahsulotlar",
            callback_data=AdminCategoryCallback(category_id=category_id).pack(),
        ),
        BACK_TO_ADMIN_MENU,
    )
    return builder.as_markup()


def admin_leads_keyboard(leads: list[Lead]):
    builder = InlineKeyboardBuilder()
    for lead in leads:
        builder.row(
            InlineKeyboardButton(
                text=f"✅ #{lead.pk} — bajarildi deb belgilash",
                callback_data=AdminLeadDoneCallback(lead_id=lead.pk).pack(),
            )
        )
    builder.row(BACK_TO_ADMIN_MENU)
    return builder.as_markup()


def admin_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Bekor qilish", callback_data=AdminNavCallback(action="menu"))
    return builder.as_markup()
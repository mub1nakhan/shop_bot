"""Inline keyboards for the in-bot owner/admin panel."""

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.callback_data import (
    AdminCategoryCallback,
    AdminEditPriceCallback,
    AdminLeadCallback,
    AdminLeadDoneCallback,
    AdminLeadsPageCallback,
    AdminNavCallback,
    AdminNewProductCatCallback,
    AdminProductCallback,
    AdminProductsPageCallback,
    AdminToggleActiveCallback,
)
from bot.utils.pagination import Page
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


def admin_products_keyboard(page: Page, category_id: int):
    """Numbered grid (1, 2, 3 ...) that lines up with the numbered text list
    built by format_numbered_admin_products — tapping "3" opens the 3rd
    product's admin detail/edit card."""
    builder = InlineKeyboardBuilder()
    for i, p in enumerate(page.items):
        builder.button(
            text=str(i + 1),
            callback_data=AdminProductCallback(category_id=category_id, product_id=p.pk),
        )
    builder.adjust(5)

    if page.total_pages > 1:
        nav_buttons = []
        if page.has_prev:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=AdminProductsPageCallback(
                        category_id=category_id, page=page.page - 1
                    ).pack(),
                )
            )
        nav_buttons.append(
            InlineKeyboardButton(
                text=f"{page.page + 1}/{page.total_pages}", callback_data="noop"
            )
        )
        if page.has_next:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=AdminProductsPageCallback(
                        category_id=category_id, page=page.page + 1
                    ).pack(),
                )
            )
        builder.row(*nav_buttons)

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


def admin_leads_keyboard(page: Page):
    """Numbered grid (1, 2, 3 ...) lining up with format_numbered_leads —
    tapping a number opens that lead's full detail card."""
    builder = InlineKeyboardBuilder()
    for i, lead in enumerate(page.items):
        builder.button(text=str(i + 1), callback_data=AdminLeadCallback(lead_id=lead.pk))
    builder.adjust(5)

    if page.total_pages > 1:
        nav_buttons = []
        if page.has_prev:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=AdminLeadsPageCallback(page=page.page - 1).pack(),
                )
            )
        nav_buttons.append(
            InlineKeyboardButton(
                text=f"{page.page + 1}/{page.total_pages}", callback_data="noop"
            )
        )
        if page.has_next:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=AdminLeadsPageCallback(page=page.page + 1).pack(),
                )
            )
        builder.row(*nav_buttons)

    builder.row(BACK_TO_ADMIN_MENU)
    return builder.as_markup()


def admin_lead_detail_keyboard(lead: Lead):
    builder = InlineKeyboardBuilder()
    if not lead.is_processed:
        builder.row(
            InlineKeyboardButton(
                text="✅ Bajarildi deb belgilash",
                callback_data=AdminLeadDoneCallback(lead_id=lead.pk).pack(),
            )
        )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Buyurtmalar",
            callback_data=AdminNavCallback(action="leads").pack(),
        ),
        BACK_TO_ADMIN_MENU,
    )
    return builder.as_markup()


def admin_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Bekor qilish", callback_data=AdminNavCallback(action="menu"))
    return builder.as_markup()
"""
All inline keyboard builders live here — handlers never construct
InlineKeyboardMarkup manually. This keeps presentation logic in one place
and makes it trivial to restyle buttons project-wide.
"""

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.callback_data import (
    CategoryCallback,
    NavigateCallback,
    OrderCallback,
    ProductCallback,
    ProductsPageCallback,
    SubcategoryCallback,
)
from bot.utils.pagination import Page
from catalog.models import Category, Product

MAIN_MENU_BTN = "🏠 Bosh menyu"
BACK_BTN = "⬅️ Orqaga"


def categories_keyboard(categories: list[Category]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=category.name,
            callback_data=CategoryCallback(category_id=category.pk),
        )
    builder.adjust(2)
    return builder.as_markup()


def subcategories_keyboard(
    subcategories: list[Category], parent_category_id: int
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for sub in subcategories:
        builder.button(
            text=sub.name,
            callback_data=SubcategoryCallback(subcategory_id=sub.pk),
        )
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(
            text=BACK_BTN,
            callback_data=NavigateCallback(action="categories").pack(),
        ),
        InlineKeyboardButton(
            text=MAIN_MENU_BTN,
            callback_data=NavigateCallback(action="main_menu").pack(),
        ),
    )
    return builder.as_markup()


def products_keyboard(
    page: Page, subcategory_id: int, parent_category_id: int | None
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for product in page.items:
        builder.button(
            text=f"{product.name} — {product.formatted_price}",
            callback_data=ProductCallback(
                product_id=product.pk, subcategory_id=subcategory_id
            ),
        )
    builder.adjust(1)

    # Pagination row
    if page.total_pages > 1:
        nav_buttons = []
        if page.has_prev:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="◀️",
                    callback_data=ProductsPageCallback(
                        subcategory_id=subcategory_id, page=page.page - 1
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
                    text="▶️",
                    callback_data=ProductsPageCallback(
                        subcategory_id=subcategory_id, page=page.page + 1
                    ).pack(),
                )
            )
        builder.row(*nav_buttons)

    if parent_category_id is None:
        # This "subcategory" is actually a root category with no children
        # (products attached directly to it) -> back goes to the main menu.
        back_callback = NavigateCallback(action="categories").pack()
    else:
        back_callback = NavigateCallback(
            action="subcategories", category_id=parent_category_id
        ).pack()

    builder.row(
        InlineKeyboardButton(text=BACK_BTN, callback_data=back_callback),
        InlineKeyboardButton(
            text=MAIN_MENU_BTN,
            callback_data=NavigateCallback(action="main_menu").pack(),
        ),
    )
    return builder.as_markup()


def product_detail_keyboard(product: Product, subcategory_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📞 Buyurtma berish",
            callback_data=OrderCallback(product_id=product.pk).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=BACK_BTN,
            callback_data=SubcategoryCallback(subcategory_id=subcategory_id).pack(),
        ),
        InlineKeyboardButton(
            text=MAIN_MENU_BTN,
            callback_data=NavigateCallback(action="main_menu").pack(),
        ),
    )
    return builder.as_markup()


def share_phone_keyboard():
    from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
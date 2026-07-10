"""Text formatting helpers, kept separate from handlers so copy can change
without touching business/navigation logic."""


def format_product_caption(name: str, price_text: str, short_description: str) -> str:
    caption = f"<b>{name}</b>\n💰 <b>{price_text}</b>"
    if short_description:
        caption += f"\n\n{short_description}"
    return caption


def format_category_prompt(category_name: str) -> str:
    return f"📂 <b>{category_name}</b>\n\nBo'limni tanlang:"


def format_products_prompt(subcategory_name: str) -> str:
    return f"🧾 <b>{subcategory_name}</b>\n\nMahsulotni tanlang:"


def format_main_menu_prompt(welcome_text: str) -> str:
    return f"{welcome_text}\n\nKategoriyani tanlang 👇"
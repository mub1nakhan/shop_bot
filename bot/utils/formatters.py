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


def format_numbered_products(products, start_index: int = 0) -> str:
    """Renders a numbered list like:
        1. Nomi — 150 000 UZS
        2. Nomi — 200 000 UZS
    `start_index` lets a page start numbering from where the previous page
    left off; pass 0 to always restart each page at 1 (current behaviour).
    """
    lines = [
        f"{start_index + i + 1}. {p.name} — {p.formatted_price}"
        for i, p in enumerate(products)
    ]
    return "\n".join(lines)


def format_numbered_admin_products(products, start_index: int = 0) -> str:
    """Same as format_numbered_products but with the 🟢/🔴 active-status icon,
    since the admin needs to see at a glance what's live in the bot."""
    lines = []
    for i, p in enumerate(products):
        icon = "🟢" if p.is_active else "🔴"
        lines.append(f"{start_index + i + 1}. {icon} {p.name} — {p.formatted_price}")
    return "\n".join(lines)


def format_main_menu_prompt(welcome_text: str) -> str:
    return f"{welcome_text}\n\nKategoriyani tanlang 👇"



# ---- Admin / owner panel ----


def format_admin_menu_prompt() -> str:
    return "🛠 <b>Admin panel</b>\n\nBo'limni tanlang:"


def format_admin_product_detail(product) -> str:
    status = "🟢 Faol" if product.is_active else "🔴 Nofaol"
    return (
        f"<b>{product.name}</b>\n"
        f"💰 {product.formatted_price}\n"
        f"📂 {product.category.name}\n"
        f"Holati: {status}\n"
        f"Rasmlar soni: {product.images.count()}"
    )


def format_lead_line(lead) -> str:
    user = lead.user
    user_name = user.full_name or user.username or str(user.telegram_id)
    product_name = lead.product.name if lead.product else "—"
    return f"👤 {user_name}\n📦 {product_name}\n📞 {lead.phone_number}"


def format_stats(stats: dict) -> str:
    return (
        "📊 <b>Statistika</b>\n\n"
        f"📦 Mahsulotlar: {stats['products_total']} (faol: {stats['products_active']})\n"
        f"📂 Kategoriyalar: {stats['categories_total']}\n"
        f"🛒 Buyurtmalar: {stats['leads_total']} (kutilmoqda: {stats['leads_unprocessed']})\n"
        f"👥 Foydalanuvchilar: {stats['users_total']}"
    )
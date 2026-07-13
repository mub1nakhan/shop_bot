"""
Typed callback_data factories (aiogram 3 CallbackData).

Using CallbackData factories instead of raw strings gives us:
- automatic serialization/deserialization
- type safety
- easy filtering in handlers via `.filter()`
"""

from aiogram.filters.callback_data import CallbackData


class CategoryCallback(CallbackData, prefix="cat"):
    """User tapped a root category -> show its subcategories (or products)."""
    category_id: int


class SubcategoryCallback(CallbackData, prefix="sub"):
    """User tapped a subcategory -> show its products (page 0)."""
    subcategory_id: int
    page: int = 0


class ProductCallback(CallbackData, prefix="prod"):
    """User tapped a product -> show product detail card."""
    product_id: int
    # remembers where "Back" should return to
    subcategory_id: int


class ProductsPageCallback(CallbackData, prefix="page"):
    """Pagination within a product list."""
    subcategory_id: int
    page: int


class NavigateCallback(CallbackData, prefix="nav"):
    """Generic navigation: back to main menu / back to subcategories list."""
    action: str  # "main_menu" | "categories" | "subcategories"
    category_id: int = 0  # used when action == "subcategories"


class OrderCallback(CallbackData, prefix="order"):
    """User wants to leave a contact request for a specific product."""
    product_id: int








# ---- Admin / owner panel (only reachable by ADMIN_IDS, see bot/filters.py) ----


class AdminNavCallback(CallbackData, prefix="anav"):
    """Admin panel navigation: menu / products / leads / new_product / stats."""
    action: str


class AdminCategoryCallback(CallbackData, prefix="acat"):
    """Admin browsing existing products inside a (leaf) category."""
    category_id: int


class AdminProductCallback(CallbackData, prefix="aprod"):
    """Admin opened a specific product's detail/edit card."""
    category_id: int
    product_id: int


class AdminToggleActiveCallback(CallbackData, prefix="atgl"):
    """Admin toggled a product's is_active flag."""
    category_id: int
    product_id: int


class AdminEditPriceCallback(CallbackData, prefix="apri"):
    """Admin wants to change a product's price."""
    category_id: int
    product_id: int


class AdminNewProductCatCallback(CallbackData, prefix="anpc"):
    """Admin picked a category while creating a brand new product."""
    category_id: int


class AdminLeadDoneCallback(CallbackData, prefix="adon"):
    """Admin marked a Lead (order/request) as processed."""
    lead_id: int
# ---- Admin / owner panel (only reachable by ADMIN_IDS, see bot/filters.py) ----



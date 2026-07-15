"""
Data-access layer for the in-bot admin/owner panel.

Follows the same convention as category_service.py / product_service.py /
user_service.py: handlers never touch the ORM directly, everything goes
through here.
"""

from decimal import Decimal

from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from django.db.models import Count

from catalog.models import Category, Product, ProductImage
from users.models import Lead, TelegramUser


@sync_to_async
def get_leaf_categories() -> list[Category]:
    """Categories that have no sub-categories -- the only ones a Product is
    allowed to be attached to. Restricting product assignment to leaf
    categories prevents the parent/child mix-up (products silently
    disappearing because they got attached to a non-leaf category)."""
    return list(
        Category.objects.annotate(num_children=Count("children"))
        .filter(num_children=0)
        .order_by("name")
    )


@sync_to_async
def get_products_in_category(category_id: int) -> list[Product]:
    return list(
        Product.objects.filter(category_id=category_id).order_by("order", "-created_at")
    )


@sync_to_async
def get_product_for_admin(product_id: int) -> Product | None:
    return (
        Product.objects.filter(pk=product_id)
        .select_related("category")
        .prefetch_related("images")
        .first()
    )


@sync_to_async
def toggle_product_active(product_id: int) -> Product | None:
    product = Product.objects.filter(pk=product_id).first()
    if product is None:
        return None
    product.is_active = not product.is_active
    product.save(update_fields=["is_active"])
    return product


@sync_to_async
def update_product_price(product_id: int, new_price: Decimal) -> Product | None:
    product = Product.objects.filter(pk=product_id).first()
    if product is None:
        return None
    product.price = new_price
    product.save(update_fields=["price"])
    return product


@sync_to_async
def create_product(
    category_id: int, name: str, price: Decimal, description: str
) -> Product:
    return Product.objects.create(
        category_id=category_id,
        name=name,
        price=price,
        short_description=description,
    )


@sync_to_async
def add_product_image_from_bytes(
    product_id: int, filename: str, content: bytes, is_main: bool
) -> ProductImage:
    return ProductImage.objects.create(
        product_id=product_id,
        image=ContentFile(content, name=filename),
        is_main=is_main,
    )


@sync_to_async
def get_unprocessed_leads(limit: int = 200) -> list[Lead]:
    return list(
        Lead.objects.filter(is_processed=False)
        .select_related("user", "product")
        .order_by("created_at")[:limit]
    )


@sync_to_async
def get_lead_for_admin(lead_id: int) -> Lead | None:
    """Full lead detail: client (TelegramUser) + product + product images,
    all prefetched so the admin sees everything without extra queries."""
    return (
        Lead.objects.filter(pk=lead_id)
        .select_related("user", "product", "product__category")
        .prefetch_related("product__images")
        .first()
    )


@sync_to_async
def mark_lead_done(lead_id: int) -> Lead | None:
    lead = Lead.objects.filter(pk=lead_id).first()
    if lead is None:
        return None
    lead.is_processed = True
    lead.save(update_fields=["is_processed"])
    return lead


@sync_to_async
def get_stats() -> dict:
    return {
        "products_total": Product.objects.count(),
        "products_active": Product.objects.filter(is_active=True).count(),
        "categories_total": Category.objects.count(),
        "leads_total": Lead.objects.count(),
        "leads_unprocessed": Lead.objects.filter(is_processed=False).count(),
        "users_total": TelegramUser.objects.count(),
    }
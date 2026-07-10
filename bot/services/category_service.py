"""
Data-access layer for categories.

This is the ONLY layer allowed to touch the Django ORM directly for
category-related data. Handlers/keyboards must go through here — this keeps
the ORM swappable and testable, and keeps handlers thin (SRP).
"""

from asgiref.sync import sync_to_async

from catalog.models import Category


@sync_to_async
def get_root_categories() -> list[Category]:
    return list(Category.active.filter(parent__isnull=True))


@sync_to_async
def get_subcategories(category_id: int) -> list[Category]:
    return list(Category.active.filter(parent_id=category_id))


@sync_to_async
def get_category(category_id: int) -> Category | None:
    return Category.active.filter(pk=category_id).first()


@sync_to_async
def category_has_subcategories(category_id: int) -> bool:
    return Category.active.filter(parent_id=category_id).exists()
"""Small, dependency-free pagination helper used by the product list keyboard."""

from dataclasses import dataclass
from typing import Sequence, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Page:
    items: Sequence
    page: int          # 0-indexed current page
    total_pages: int
    has_prev: bool
    has_next: bool


def paginate(items: Sequence[T], page: int, page_size: int) -> Page:
    total = len(items)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(0, min(page, total_pages - 1))

    start = page * page_size
    end = start + page_size

    return Page(
        items=items[start:end],
        page=page,
        total_pages=total_pages,
        has_prev=page > 0,
        has_next=page < total_pages - 1,
    )
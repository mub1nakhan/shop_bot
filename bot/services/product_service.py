from asgiref.sync import sync_to_async

from catalog.models import Product


@sync_to_async
def get_products_by_subcategory(subcategory_id: int) -> list[Product]:
    return list(
        Product.active.filter(category_id=subcategory_id).prefetch_related("images")
    )


@sync_to_async
def get_product(product_id: int) -> Product | None:
    return (
        Product.active.filter(pk=product_id)
        .select_related("category")
        .prefetch_related("images")
        .first()
    )


@sync_to_async
def get_product_main_image_path(product: Product) -> str | None:
    img = product.main_image
    return img.image.path if img else None
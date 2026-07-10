from django.contrib import admin

from .models import Category, Product, ProductImage


class SubcategoryInline(admin.TabularInline):
    """Lets an admin add subcategories directly from the parent Category page."""

    model = Category
    fk_name = "parent"
    extra = 0
    fields = ("name", "order", "is_active", "image")
    verbose_name = "Sub-kategoriya"
    verbose_name_plural = "Sub-kategoriyalar"
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_root_display", "order", "is_active", "image_preview")
    list_filter = ("is_active", ("parent", admin.EmptyFieldListFilter))
    search_fields = ("name",)
    list_editable = ("order", "is_active")
    readonly_fields = ("image_preview",)
    autocomplete_fields = ("parent",)
    search_help_text = "Kategoriya nomi bo'yicha qidiring"

    fieldsets = (
        (None, {"fields": ("name", "parent", "order", "is_active")}),
        ("Rasm", {"fields": ("image", "image_preview")}),
    )

    def get_inlines(self, request, obj):
        # Only show the subcategory inline for root categories,
        # to avoid encouraging 3rd-level nesting from the admin UI.
        if obj is None or obj.is_root:
            return [SubcategoryInline]
        return []

    @admin.display(description="Turi", boolean=False)
    def is_root_display(self, obj: Category):
        return "🗂 Asosiy kategoriya" if obj.is_root else "↳ Sub-kategoriya"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "image_preview", "is_main", "order")
    readonly_fields = ("image_preview",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "formatted_price",
        "is_active",
        "order",
        "main_image_preview",
    )
    list_filter = ("is_active", "category")
    search_fields = ("name", "short_description")
    list_editable = ("order", "is_active")
    autocomplete_fields = ("category",)
    inlines = [ProductImageInline]
    search_help_text = "Mahsulot nomi yoki tavsifi bo'yicha qidiring"

    fieldsets = (
        (None, {"fields": ("category", "name", "short_description")}),
        ("Narx", {"fields": ("price", "currency")}),
        ("Holat", {"fields": ("is_active", "order")}),
    )

    @admin.display(description="Narx")
    def formatted_price(self, obj: Product):
        return obj.formatted_price

    @admin.display(description="Asosiy rasm")
    def main_image_preview(self, obj: Product):
        img = obj.main_image
        return img.image_preview() if img else "—"
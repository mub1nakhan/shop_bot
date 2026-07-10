from django.db import models
from django.utils.html import format_html


class ActiveManager(models.Manager):
    """Returns only records that should be visible in the bot."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Category(models.Model):
    """
    Self-referencing category tree.

    depth 0 (parent is NULL)      -> top-level Category, shown in Main Menu
    depth 1 (parent is a root)    -> Subcategory, shown after a Category is picked

    The bot flow only walks 2 levels deep (Category -> Subcategory -> Products),
    but the model itself does not restrict nesting, so this can be extended
    later without a schema change.
    """

    name = models.CharField("Nomi", max_length=150)
    parent = models.ForeignKey(
        "self",
        verbose_name="Ota kategoriya",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        help_text="Bo'sh qoldirilsa — asosiy (top-level) kategoriya bo'ladi. "
        "Tanlansa — shu kategoriyaning sub-kategoriyasi bo'ladi.",
    )
    image = models.ImageField(
        "Rasm", upload_to="categories/%Y/%m/", blank=True, null=True
    )
    order = models.PositiveIntegerField("Tartib raqami", default=0)
    is_active = models.BooleanField("Faol (botda ko'rinadi)", default=True)
    created_at = models.DateTimeField("Yaratilgan vaqti", auto_now_add=True)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["order", "name"]

    def __str__(self):
        if self.parent_id:
            return f"{self.parent.name} → {self.name}"
        return self.name

    @property
    def is_root(self) -> bool:
        return self.parent_id is None

    def image_preview(self):
        if self.image:
            return format_html(
                '<img src="{}" style="height:50px;border-radius:4px;" />',
                self.image.url,
            )
        return "—"

    image_preview.short_description = "Ko'rinish"


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        verbose_name="Kategoriya (sub-kategoriya)",
        related_name="products",
        on_delete=models.CASCADE,
    )
    name = models.CharField("Nomi", max_length=200)
    short_description = models.TextField(
        "Qisqacha tavsif", max_length=500, blank=True
    )
    price = models.DecimalField("Narxi", max_digits=12, decimal_places=2)
    currency = models.CharField("Valyuta", max_length=8, default="UZS")
    is_active = models.BooleanField("Faol (botda ko'rinadi)", default=True)
    order = models.PositiveIntegerField("Tartib raqami", default=0)
    created_at = models.DateTimeField("Yaratilgan vaqti", auto_now_add=True)
    updated_at = models.DateTimeField("Yangilangan vaqti", auto_now=True)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.name

    @property
    def main_image(self):
        first_main = next((img for img in self.images.all() if img.is_main), None)
        if first_main:
            return first_main
        images = list(self.images.all())
        return images[0] if images else None

    @property
    def formatted_price(self) -> str:
        # 150000 -> "150 000 UZS"
        return f"{int(self.price):,}".replace(",", " ") + f" {self.currency}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, verbose_name="Mahsulot", related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField("Rasm", upload_to="products/%Y/%m/")
    is_main = models.BooleanField(
        "Asosiy rasm", default=False, help_text="Mahsulot kartasida shu rasm ko'rsatiladi."
    )
    order = models.PositiveIntegerField("Tartib raqami", default=0)

    class Meta:
        verbose_name = "Mahsulot rasmi"
        verbose_name_plural = "Mahsulot rasmlari"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.product.name} — rasm #{self.pk or ''}"

    def image_preview(self):
        if self.image:
            return format_html(
                '<img src="{}" style="height:50px;border-radius:4px;" />',
                self.image.url,
            )
        return "—"

    image_preview.short_description = "Ko'rinish"
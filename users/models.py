from django.db import models


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField("Telegram ID", unique=True, db_index=True)
    username = models.CharField("Username", max_length=150, blank=True, null=True)
    full_name = models.CharField("Ism familiya", max_length=255, blank=True)
    phone_number = models.CharField(
        "Telefon raqami", max_length=32, blank=True, null=True
    )
    language_code = models.CharField(
        "Til kodi", max_length=8, blank=True, null=True
    )
    is_blocked = models.BooleanField(
        "Botni bloklagan", default=False,
        help_text="Foydalanuvchi botni bloklasa, avtomatik True bo'ladi."
    )
    first_seen = models.DateTimeField("Birinchi tashrif", auto_now_add=True)
    last_seen = models.DateTimeField("Oxirgi tashrif", auto_now=True)

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ["-last_seen"]

    def __str__(self):
        return self.full_name or self.username or str(self.telegram_id)


class Lead(models.Model):
    """A customer's 'order / contact me' request captured from the bot."""

    user = models.ForeignKey(
        TelegramUser, verbose_name="Foydalanuvchi", related_name="leads",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "catalog.Product", verbose_name="Mahsulot", related_name="leads",
        on_delete=models.SET_NULL, null=True, blank=True
    )
    phone_number = models.CharField("Telefon raqami", max_length=32)
    is_processed = models.BooleanField("Ko'rib chiqildi", default=False)
    created_at = models.DateTimeField("Yaratilgan vaqti", auto_now_add=True)

    class Meta:
        verbose_name = "Buyurtma / So'rov"
        verbose_name_plural = "Buyurtmalar / So'rovlar"
        ordering = ["-created_at"]

    def __str__(self):
        product_name = self.product.name if self.product else "—"
        return f"{self.user} — {product_name}"


class BotSettings(models.Model):
    """Singleton table for admin-editable bot copy. Always pk=1."""

    welcome_text = models.TextField(
        "Salomlashuv matni",
        default="Assalomu alaykum! Jalyuzi va parda katalogimizga xush kelibsiz. 👇",
    )
    contact_phone = models.CharField("Aloqa telefoni", max_length=32, blank=True)
    contact_address = models.TextField("Manzil", blank=True)

    class Meta:
        verbose_name = "Bot sozlamalari"
        verbose_name_plural = "Bot sozlamalari"

    def __str__(self):
        return "Bot sozlamalari"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # prevent deletion of the singleton

    @classmethod
    def load(cls) -> "BotSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
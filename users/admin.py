from django.contrib import admin

from .models import BotSettings, Lead, TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        "full_name", "username", "telegram_id", "phone_number",
        "is_blocked", "first_seen", "last_seen",
    )
    list_filter = ("is_blocked",)
    search_fields = ("full_name", "username", "telegram_id", "phone_number")
    readonly_fields = ("telegram_id", "first_seen", "last_seen")

    def has_add_permission(self, request):
        # Users are only ever created by the bot itself.
        return False


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "phone_number", "is_processed", "created_at")
    list_filter = ("is_processed", "created_at")
    search_fields = ("phone_number", "user__full_name", "user__username")
    list_editable = ("is_processed",)
    autocomplete_fields = ("user", "product")
    readonly_fields = ("created_at",)


@admin.register(BotSettings)
class BotSettingsAdmin(admin.ModelAdmin):
    list_display = ("__str__", "contact_phone")

    def has_add_permission(self, request):
        # Only allow one instance to exist.
        return not BotSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
from asgiref.sync import sync_to_async

from users.models import BotSettings, Lead, TelegramUser


@sync_to_async
def get_or_create_user(
    telegram_id: int,
    username: str | None,
    full_name: str,
    language_code: str | None,
) -> TelegramUser:
    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "username": username,
            "full_name": full_name,
            "language_code": language_code,
        },
    )
    if not created:
        # Keep profile data fresh (name/username can change on Telegram side).
        user.username = username
        user.full_name = full_name
        user.language_code = language_code
        user.is_blocked = False
        user.save(update_fields=["username", "full_name", "language_code", "is_blocked"])
    return user


@sync_to_async
def mark_user_blocked(telegram_id: int) -> None:
    TelegramUser.objects.filter(telegram_id=telegram_id).update(is_blocked=True)


@sync_to_async
def save_phone_number(telegram_id: int, phone_number: str) -> None:
    TelegramUser.objects.filter(telegram_id=telegram_id).update(phone_number=phone_number)


@sync_to_async
def create_lead(telegram_id: int, product_id: int | None, phone_number: str) -> Lead:
    user = TelegramUser.objects.get(telegram_id=telegram_id)
    return Lead.objects.create(user=user, product_id=product_id, phone_number=phone_number)


@sync_to_async
def get_bot_settings() -> BotSettings:
    return BotSettings.load()
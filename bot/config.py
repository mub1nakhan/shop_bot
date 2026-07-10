from dataclasses import dataclass, field

from django.conf import settings


@dataclass(frozen=True)
class BotConfig:
    token: str
    admin_ids: list[int] = field(default_factory=list)
    products_page_size: int = 5


def get_bot_config() -> BotConfig:
    if not settings.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Please set it in your .env file.")
    return BotConfig(
        token=settings.BOT_TOKEN,
        admin_ids=settings.ADMIN_IDS,
        products_page_size=getattr(settings, "PRODUCTS_PAGE_SIZE", 5),
    )
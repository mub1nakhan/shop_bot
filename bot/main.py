"""
Aiogram bot entrypoint.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django  # noqa: E402

django.setup()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("bot")


async def _on_startup():
    logger.info("Bot ishga tushmoqda...")


async def _on_shutdown():
    logger.info("Bot to'xtatilmoqda...")


async def run_polling():
    from bot.handlers import get_root_router
    from bot.loader import bot, dp
    from bot.middlewares.db_user_middleware import DbUserMiddleware
    from bot.middlewares.throttling import ThrottlingMiddleware

    dp.include_router(get_root_router())

    dp.update.middleware(DbUserMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit_seconds=0.35))

    dp.startup.register(_on_startup)
    dp.shutdown.register(_on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


def main():
    try:
        asyncio.run(run_polling())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    main()
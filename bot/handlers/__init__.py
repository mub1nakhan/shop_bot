from aiogram import Router

from bot.handlers import admin, catalog, fallback, order, start


def get_root_router() -> Router:
    root = Router(name="root")
    root.include_router(start.router)
    root.include_router(admin.router)
    root.include_router(catalog.router)
    root.include_router(order.router)
    root.include_router(fallback.router)
    return root